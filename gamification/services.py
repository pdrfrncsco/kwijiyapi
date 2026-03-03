from __future__ import annotations
from datetime import date, timedelta
from typing import TypedDict
import logging

from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


LEVEL_TITLES = {
    1: "Mulami", 2: "Mukanda", 3: "Muzumbi", 4: "Mwana",
    5: "Mukongo", 6: "Mufumu", 7: "Mwenyo", 8: "Nganga",
    9: "Kalunga", 10: "Hosi", 12: "Kanda", 15: "Soma", 20: "Ngola",
}


def get_level_title(level: int) -> str:
    for lvl in sorted(LEVEL_TITLES.keys(), reverse=True):
        if level >= lvl:
            return LEVEL_TITLES[lvl]
    return "Mulami"


def xp_required_for_level(level: int) -> int:
    """XP necessário para subir do nível `level` para o seguinte."""
    return int(100 * (level ** 1.65))


def total_xp_for_level(level: int) -> int:
    """XP total acumulado para atingir o nível `level`."""
    if level <= 1:
        return 0
    return sum(xp_required_for_level(i) for i in range(1, level))


def xp_to_next_level(current_xp: int, current_level: int) -> int:
    threshold = total_xp_for_level(current_level + 1)
    return max(0, threshold - current_xp)


def calculate_answer_xp(
    difficulty: str,
    time_taken: float,
    timer_seconds: int,
    streak_days: int,
    is_spaced_repetition: bool = False,
    age_multiplier: float = 1.0,
) -> int:
    BASE_XP = {"easy": 10, "medium": 20, "hard": 35}
    base = BASE_XP.get(difficulty, 10)
    time_ratio = min(1.0, time_taken / max(timer_seconds, 1))
    speed_bonus = max(0.0, 1.0 - time_ratio) * 0.5
    streak_bonus = min(streak_days, 7) * 0.05
    review_bonus = 0.25 if is_spaced_repetition else 0.0
    total = base * (1 + speed_bonus + streak_bonus + review_bonus) * age_multiplier
    return max(5, int(total))


@transaction.atomic
def award_xp(user, xp_amount: int, source: str, makuta_amount: int = 0) -> dict:
    from .models import UserXPLog, Badge, UserBadge

    old_level = user.level
    user.total_xp += xp_amount
    user.coins += makuta_amount

    while user.total_xp >= total_xp_for_level(user.level + 1):
        user.level += 1
        user.coins += user.level * 25

    leveled_up = user.level > old_level
    user.save(update_fields=["total_xp", "level", "coins"])
    UserXPLog.objects.create(user=user, xp_gained=xp_amount, source=source)

    badges_earned = []
    existing_ids = set(UserBadge.objects.filter(user=user).values_list("badge_id", flat=True))
    for badge in Badge.objects.all():
        if badge.id not in existing_ids and badge.xp_required and user.total_xp >= badge.xp_required:
            UserBadge.objects.create(user=user, badge=badge)
            badges_earned.append(badge.name)

    return {
        "xp_gained": xp_amount,
        "makuta_gained": makuta_amount,
        "leveled_up": leveled_up,
        "new_level": user.level,
        "level_title": get_level_title(user.level),
        "total_xp": user.total_xp,
        "xp_to_next": xp_to_next_level(user.total_xp, user.level),
        "badges_earned": badges_earned,
    }


def update_streak(user) -> dict:
    today = timezone.now().date()
    # Handle DateTimeField -> date conversion
    last_activity_dt = user.last_activity
    last_activity_date = last_activity_dt.date() if last_activity_dt else None
    
    coins_bonus = 0

    if last_activity_date is None or last_activity_date < today - timedelta(days=1):
        user.streak_days = 1
    elif last_activity_date == today - timedelta(days=1):
        user.streak_days += 1
    # se last_activity == today, já jogou hoje — não alterar

    user.last_activity = timezone.now()

    MILESTONES = {3: 30, 7: 75, 14: 150, 30: 400}
    if user.streak_days in MILESTONES:
        coins_bonus = MILESTONES[user.streak_days]
        user.coins += coins_bonus

    user.save(update_fields=["streak_days", "last_activity", "coins"])
    return {"streak_days": user.streak_days, "milestone_bonus": user.streak_days if user.streak_days in MILESTONES else 0, "coins_bonus": coins_bonus}


def recover_streak_with_coins(user, cost: int = 50) -> dict:
    if user.coins < cost:
        return {"success": False, "reason": "Makuta insuficiente", "coins_required": cost}
    user.coins -= cost
    user.streak_days = 1
    user.last_activity = timezone.now()
    user.save(update_fields=["coins", "streak_days", "last_activity"])
    return {"success": True, "coins_remaining": user.coins, "streak_days": user.streak_days}

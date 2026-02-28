"""
Gamification service layer — XP, Streak, Level.
"""

from django.utils import timezone
from datetime import timedelta
import logging
from .models import UserXPLog, Badge, UserBadge


logger = logging.getLogger(__name__)


def award_xp(user, amount, source='quiz', description=''):
    """Award XP to a user and log it."""
    UserXPLog.objects.create(
        user=user,
        xp_gained=amount,
        source=source,
        description=description,
    )
    user.total_xp += amount
    user.save(update_fields=['total_xp'])


def check_level_up(user):
    """
    Check if user has enough XP to level up.
    Formula: XP required for level N = 100 * N
    Returns True if leveled up.
    """
    leveled_up = False
    while True:
        xp_needed = 100 * user.level
        # Total XP needed to reach current level
        xp_at_current = sum(100 * i for i in range(1, user.level))
        xp_in_current_level = user.total_xp - xp_at_current

        if xp_in_current_level >= xp_needed:
            user.level += 1
            leveled_up = True
            # Award bonus for level up
            UserXPLog.objects.create(
                user=user,
                xp_gained=0,
                source='level_up',
                description=f'Subiu para nível {user.level}!',
            )
            # Check for new badges
            _check_badges(user)
        else:
            break

    if leveled_up:
        user.save(update_fields=['level'])

    return leveled_up


def update_streak(user):
    now = timezone.now().date()
    logger.info(
        "update_streak start user=%s streak_days=%s last_activity=%s",
        user.id,
        user.streak_days,
        user.last_activity,
    )

    if user.last_activity:
        last = user.last_activity.date()
        diff = (now - last).days

        if diff == 0:
            return
        elif diff == 1:
            user.streak_days += 1
        else:
            user.streak_days = 1
    else:
        user.streak_days = 1

    if user.streak_days in (3, 7, 14, 30):
        bonus = user.streak_days * 10
        award_xp(
            user,
            bonus,
            source='streak',
            description=f'Bónus de streak de {user.streak_days} dias!',
        )

    user.last_activity = timezone.now()
    user.save(update_fields=['streak_days', 'last_activity'])
    logger.info(
        "update_streak end user=%s streak_days=%s last_activity=%s",
        user.id,
        user.streak_days,
        user.last_activity,
    )


def _check_badges(user):
    """Award any earned but unawarded badges."""
    earned_badge_ids = UserBadge.objects.filter(user=user).values_list('badge_id', flat=True)
    eligible = Badge.objects.filter(xp_required__lte=user.total_xp).exclude(id__in=earned_badge_ids)

    for badge in eligible:
        UserBadge.objects.create(user=user, badge=badge)

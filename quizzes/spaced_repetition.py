"""
Algoritmo SM-2 adaptado para o Kwijiya.
SM-2 original: Piotr Wozniak (1987).
"""
from __future__ import annotations
from datetime import date, timedelta
from django.db import transaction


def answer_quality(is_correct: bool, time_taken: float, timer: int) -> int:
    """
    Converte resultado de resposta em quality (0-5) para SM-2.
      5 = correcto e rápido (<40% do tempo)
      4 = correcto com hesitação
      3 = correcto lento
      2 = errado (hesitação)
      1 = errado rápido
      0 = em branco / não respondeu
    """
    if not is_correct:
        return 1 if time_taken < timer * 0.5 else 2
    time_ratio = time_taken / max(timer, 1)
    if time_ratio <= 0.40:
        return 5
    elif time_ratio <= 0.65:
        return 4
    else:
        return 3


@transaction.atomic
def update_card(card, quality: int) -> dict:
    """Actualiza um SpacedRepetitionCard com o algoritmo SM-2."""
    if quality >= 3:
        if card.repetitions == 0:
            new_interval = 1
        elif card.repetitions == 1:
            new_interval = 3
        else:
            new_interval = round(card.interval * card.ease_factor)
        card.repetitions += 1
        ef_delta = 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)
        card.ease_factor = max(1.3, min(3.0, card.ease_factor + ef_delta))
    else:
        new_interval = 1
        card.repetitions = 0
        card.ease_factor = max(1.3, card.ease_factor - 0.2)

    card.interval = new_interval
    card.next_review = date.today() + timedelta(days=new_interval)
    card.last_quality = quality
    card.save()

    return {
        "next_review": card.next_review.isoformat(),
        "interval_days": new_interval,
        "ease_factor": round(card.ease_factor, 2),
        "repetitions": card.repetitions,
    }


def get_or_create_card(user, question):
    from .models import SpacedRepetitionCard
    return SpacedRepetitionCard.objects.get_or_create(
        user=user, question=question,
        defaults={"ease_factor": 2.5, "interval": 1, "repetitions": 0, "next_review": date.today(), "last_quality": 0},
    )


def get_due_cards(user, language, limit: int = 5):
    from .models import SpacedRepetitionCard
    return (
        SpacedRepetitionCard.objects
        .filter(user=user, question__language=language, next_review__lte=date.today())
        .select_related("question")
        .order_by("next_review")[:limit]
    )

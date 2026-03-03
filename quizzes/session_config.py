from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class SessionConfig:
    questions_per_session: int
    timer_seconds: int
    xp_multiplier: float
    makuta_per_correct: int
    feedback_style: Literal["encouraging", "neutral", "competitive"]
    show_ranking: bool
    show_streak_pressure: bool
    show_statistics_detail: bool
    max_difficulty: Literal["easy", "medium", "hard"]
    spaced_repetition_ratio: float


CONFIGS = {
    "child": SessionConfig(
        questions_per_session=3, timer_seconds=10, xp_multiplier=1.3,
        makuta_per_correct=15, feedback_style="encouraging",
        show_ranking=False, show_streak_pressure=False, show_statistics_detail=False,
        max_difficulty="medium", spaced_repetition_ratio=0.33,
    ),
    "teen": SessionConfig(
        questions_per_session=7, timer_seconds=7, xp_multiplier=1.1,
        makuta_per_correct=10, feedback_style="neutral",
        show_ranking=True, show_streak_pressure=True, show_statistics_detail=True,
        max_difficulty="hard", spaced_repetition_ratio=0.28,
    ),
    "adult": SessionConfig(
        questions_per_session=12, timer_seconds=5, xp_multiplier=1.0,
        makuta_per_correct=10, feedback_style="competitive",
        show_ranking=True, show_streak_pressure=True, show_statistics_detail=True,
        max_difficulty="hard", spaced_repetition_ratio=0.25,
    ),
}


def get_config(age_group: str) -> SessionConfig:
    return CONFIGS.get(age_group, CONFIGS["adult"])


def question_distribution(config: SessionConfig, level: int) -> dict:
    """Retorna distribuição {easy, medium, hard} para a sessão."""
    n = config.questions_per_session
    if level == 1:
        easy = max(1, int(n * 0.6))
        medium = n - easy
        hard = 0
    elif level == 2:
        easy = max(1, int(n * 0.3))
        hard = 0 if config.max_difficulty == "easy" else max(0, int(n * 0.2))
        medium = n - easy - hard
    else:
        if config.max_difficulty == "medium":
            easy = max(1, int(n * 0.4))
            medium = n - easy
            hard = 0
        else:
            easy = max(1, int(n * 0.2))
            hard = max(1, int(n * 0.3))
            medium = n - easy - hard
    return {"easy": easy, "medium": medium, "hard": hard}

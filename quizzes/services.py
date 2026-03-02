from django.db.models import Q
from django.utils import timezone
from .models import Question

def get_adaptive_questions(user, language, level, count=10):
    """
    Selects questions adaptively:
    1. Due spaced repetition items
    2. New questions (never answered)
    3. Random questions from level to fill count
    """
    from progress.models import SpacedRepetitionItem, UserAnswer

    # 1. Spaced Repetition Due Items (max 4)
    from progress.models import SpacedRepetitionItem, UserAnswer

    # Calculate target counts
    count_srs = 4
    count_new = 4
    count_random = count - count_srs - count_new
    if count_random < 0:
        count_random = 0

    # 1. Get due SRS items (questions that need review)
    # Filter by user, language. Difficulty can be flexible here (review old levels too)
    # But for now strict level to keep context
    due_items_qs = SpacedRepetitionItem.objects.filter(
        user=user,
        question__language=language,
        # Allow reviewing questions from current level OR lower levels
        question__difficulty__lte=level,
        next_review__lte=timezone.now()
    ).select_related('question').order_by('next_review')

    due_items = list(due_items_qs[:count_srs])
    due_question_ids = [item.question.id for item in due_items]

    # 2. Get NEW questions (never answered) for CURRENT level
    # Get all question IDs the user has answered ever
    answered_ids = UserAnswer.objects.filter(user=user).values_list('question_id', flat=True)
    
    new_questions_qs = Question.objects.filter(
        language=language,
        difficulty=level  # Strict level for new material
    ).exclude(
        id__in=list(answered_ids)
    ).order_by('?')

    new_questions = list(new_questions_qs[:count_new])
    new_question_ids = [q.id for q in new_questions]

    # 3. Fill remaining slots
    current_selected = due_items + new_questions
    current_count = len(current_selected)
    needed = count - current_count

    if needed > 0:
        # Fill with random questions from current level (even if already answered)
        # to ensure the user practices at their current difficulty
        exclude_ids = due_question_ids + new_question_ids
        
        extra_questions = list(Question.objects.filter(
            language=language,
            difficulty=level
        ).exclude(
            id__in=exclude_ids
        ).order_by('?')[:needed])
        
        current_selected.extend(extra_questions)
    
    # Normalize result to list of Question objects
    result = []
    for item in current_selected:
        if hasattr(item, 'question'):
            result.append(item.question)
        else:
            result.append(item)

    # Shuffle final result
    import random
    random.shuffle(result)
    
    return result[:count]

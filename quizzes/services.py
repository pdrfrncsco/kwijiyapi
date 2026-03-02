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
    due_items = SpacedRepetitionItem.objects.filter(
        user=user,
        question__language=language,
        question__difficulty=level,
        next_review__lte=timezone.now()
    ).select_related('question').order_by('next_review')[:4]

    due_question_ids = [item.question_id for item in due_items]

    # 2. New Questions (not answered yet) (max 4)
    # Get all question IDs the user has answered
    answered_ids = UserAnswer.objects.filter(user=user).values_list('question_id', flat=True)
    
    # Exclude answered and due questions
    new_questions = list(
        Question.objects.filter(
            language=language,
            difficulty=level
        ).exclude(
            id__in=list(answered_ids) + due_question_ids
        ).order_by('?')[:4]
    )

    # 3. Fill with random questions from the level if needed
    selected = list(due_items) + new_questions
    
    # Extract IDs currently selected
    selected_ids = []
    for item in selected:
        if hasattr(item, 'question'):
            selected_ids.append(item.question.id)
        else:
            selected_ids.append(item.id)
            
    current_count = len(selected)
    
    if current_count < count:
        extra = Question.objects.filter(
            language=language,
            difficulty=level
        ).exclude(
            id__in=selected_ids
        ).order_by('?')[:count - current_count]
        
        selected.extend(list(extra))

    # Normalize result to list of Question objects
    result = []
    for item in selected:
        if hasattr(item, 'question'):
            result.append(item.question)
        else:
            result.append(item)

    # Shuffle final result so due items aren't always first
    import random
    random.shuffle(result)
    
    return result[:count]

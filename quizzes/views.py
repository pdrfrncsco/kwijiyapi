"""
Quiz engine views: start_quiz, submit_answer, session detail.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Question, Option, QuizSession
from .serializers import (
    StartQuizSerializer, SubmitAnswerSerializer,
    QuizSessionSerializer, QuestionSerializer,
)
from languages.models import Language
from gamification.services import award_xp, update_streak, check_level_up
from progress.models import UserAnswer, UserProgress, SpacedRepetitionItem
from .services import get_adaptive_questions


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_quiz(request):
    """
    Start a new quiz session.
    Selects random questions for the given language and level.
    """
    serializer = StartQuizSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    language_code = serializer.validated_data['language_code']
    level = serializer.validated_data['level']
    num_questions = serializer.validated_data['num_questions']

    # Validate language
    try:
        language = Language.objects.get(code=language_code, is_active=True)
    except Language.DoesNotExist:
        return Response(
            {'error': f'Língua "{language_code}" não encontrada.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Get adaptive questions
    questions = get_adaptive_questions(
        user=request.user,
        language=language,
        level=level,
        count=num_questions
    )

    if not questions:
        return Response(
            {'error': 'Sem perguntas disponíveis para este nível.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Create session
    session = QuizSession.objects.create(
        user=request.user,
        language=language,
        level=level,
        total_questions=len(questions),
    )
    session.questions.set(questions)

    return Response({
        'session_id': str(session.id),
        'language': language.name,
        'level': level,
        'total_questions': len(questions),
        'questions': QuestionSerializer(questions, many=True).data,
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_answer(request):
    """
    Submit an answer for a question in an active quiz session.
    Calculates XP based on correctness and time taken.
    """
    serializer = SubmitAnswerSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    session_id = serializer.validated_data['session_id']
    question_id = serializer.validated_data['question_id']
    option_id = serializer.validated_data['option_id']
    time_taken = serializer.validated_data['time_taken']

    # Validate session
    session = get_object_or_404(QuizSession, id=session_id, user=request.user)

    if session.is_completed:
        return Response(
            {'error': 'Esta sessão já foi concluída.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate question belongs to session
    question = get_object_or_404(Question, id=question_id)
    if not session.questions.filter(id=question_id).exists():
        return Response(
            {'error': 'Pergunta não pertence a esta sessão.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Check if already answered
    if UserAnswer.objects.filter(
        user=request.user, question=question, quiz_session=session
    ).exists():
        return Response(
            {'error': 'Pergunta já respondida nesta sessão.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Get the selected option
    option = get_object_or_404(Option, id=option_id, question=question)
    is_correct = option.is_correct

    # Calculate XP: base_xp * speed_bonus
    xp_earned = 0
    makuta_earned = 0

    if is_correct:
        speed_factor = max(0, 1 - (time_taken / question.timer_seconds))
        xp_earned = int(question.xp_value * (0.5 + 0.5 * speed_factor))
        makuta_earned = 10  # 10 Makuta per correct answer

        session.correct_answers += 1
        session.total_xp_earned += xp_earned
        session.total_makuta_earned += makuta_earned

        # Award XP and Makuta to user
        award_xp(request.user, xp_earned, source='quiz')
        request.user.coins += makuta_earned
        request.user.save(update_fields=['coins'])

    # Record the answer
    UserAnswer.objects.create(
        user=request.user,
        question=question,
        selected_option=option,
        is_correct=is_correct,
        time_taken=time_taken,
        quiz_session=session,
    )
    
    # Update Spaced Repetition (SM-2)
    quality = 0
    if is_correct:
        # Calculate quality based on speed
        ratio = time_taken / question.timer_seconds
        if ratio < 0.5:
            quality = 5
        elif ratio < 0.8:
            quality = 4
        else:
            quality = 3
    else:
        quality = 0
        
    srs_item, _ = SpacedRepetitionItem.objects.get_or_create(
        user=request.user,
        question=question
    )
    srs_item.schedule_next(quality)

    # Get correct option for feedback
    correct_option = question.options.filter(is_correct=True).first()

    # Check if all questions are answered
    answered_count = UserAnswer.objects.filter(
        user=request.user, quiz_session=session
    ).count()

    if answered_count >= session.total_questions:
        session.is_completed = True
        session.completed_at = timezone.now()

        # Update streak
        update_streak(request.user)

        # Check level up
        leveled_up = check_level_up(request.user)

        # Bonus for completing session — streak bonus
        if session.accuracy >= 80:
            bonus_makuta = 50
            session.total_makuta_earned += bonus_makuta
            request.user.coins += bonus_makuta
            request.user.save(update_fields=['coins'])

        # Update user progress
        progress, _ = UserProgress.objects.get_or_create(
            user=request.user,
            language=session.language,
        )
        progress.completed_lessons += 1
        total_answers = UserAnswer.objects.filter(
            user=request.user,
            question__language=session.language,
        ).count()
        correct_total = UserAnswer.objects.filter(
            user=request.user,
            question__language=session.language,
            is_correct=True,
        ).count()
        progress.accuracy_rate = round(correct_total / total_answers * 100, 1) if total_answers else 0
        progress.level = session.level
        progress.last_activity = timezone.now()
        progress.save()

    session.save()

    response_data = {
        'is_correct': is_correct,
        'xp_earned': xp_earned,
        'makuta_earned': makuta_earned,
        'correct_answer': correct_option.text if correct_option else None,
        'explanation': question.explanation,
        'cultural_note': question.cultural_note,
        'session_progress': {
            'answered': answered_count,
            'total': session.total_questions,
            'is_completed': session.is_completed,
        },
    }

    if session.is_completed:
        response_data['session_summary'] = {
            'accuracy': session.accuracy,
            'total_xp': session.total_xp_earned,
            'total_makuta': session.total_makuta_earned,
            'correct': session.correct_answers,
            'total': session.total_questions,
        }

    return Response(response_data, status=status.HTTP_200_OK)


class QuizSessionDetailView(generics.RetrieveAPIView):
    """Get details of a completed quiz session."""
    serializer_class = QuizSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return QuizSession.objects.filter(user=self.request.user)

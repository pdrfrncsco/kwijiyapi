from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import UserProgress, UserAnswer
from .serializers import UserProgressSerializer, UserStatsSerializer
from quizzes.models import QuizSession


class UserProgressListView(generics.ListAPIView):
    """List user progress per language."""
    serializer_class = UserProgressSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_stats(request):
    """Aggregate stats for the authenticated user."""
    user = request.user
    total_answers = UserAnswer.objects.filter(user=user).count()
    correct_answers = UserAnswer.objects.filter(user=user, is_correct=True).count()
    total_sessions = QuizSession.objects.filter(user=user, is_completed=True).count()
    languages_studied = UserProgress.objects.filter(user=user).count()

    data = {
        'total_answers': total_answers,
        'correct_answers': correct_answers,
        'overall_accuracy': round(correct_answers / total_answers * 100, 1) if total_answers else 0,
        'total_quiz_sessions': total_sessions,
        'languages_studied': languages_studied,
    }

    serializer = UserStatsSerializer(data)
    return Response(serializer.data)

from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.db.models import Count, Avg
from django.utils import timezone
from datetime import timedelta
from quizzes.models import QuizSession
from users.models import CustomUser

class DashboardAnalyticsView(generics.RetrieveAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        now = timezone.now()
        last_24h = now - timedelta(days=1)
        
        # Basic Metrics
        total_users = CustomUser.objects.count()
        new_users_24h = CustomUser.objects.filter(created_at__gte=last_24h).count()
        
        total_sessions = QuizSession.objects.count()
        completed_sessions = QuizSession.objects.filter(is_completed=True).count()
        
        completion_rate = 0
        if total_sessions > 0:
            completion_rate = (completed_sessions / total_sessions) * 100
            
        # Retention (Users active in last 24h)
        active_users_24h = CustomUser.objects.filter(last_activity__gte=last_24h).count()
        
        return Response({
            'users': {
                'total': total_users,
                'new_24h': new_users_24h,
                'active_24h': active_users_24h,
            },
            'quizzes': {
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'completion_rate': f"{completion_rate:.1f}%",
            }
        })

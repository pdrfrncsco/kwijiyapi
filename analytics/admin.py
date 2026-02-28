from django.contrib import admin
from django.utils import timezone
from datetime import timedelta
from users.models import CustomUser
from quizzes.models import QuizSession
from .models import AnalyticsDashboard


@admin.register(AnalyticsDashboard)
class AnalyticsDashboardAdmin(admin.ModelAdmin):
    change_list_template = 'admin/analytics/dashboard.html'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        now = timezone.now()
        last_24h = now - timedelta(days=1)

        total_users = CustomUser.objects.count()
        new_users_24h = CustomUser.objects.filter(created_at__gte=last_24h).count()

        total_sessions = QuizSession.objects.count()
        completed_sessions = QuizSession.objects.filter(is_completed=True).count()

        completion_rate = 0
        if total_sessions:
            completion_rate = (completed_sessions / total_sessions) * 100

        active_users_24h = CustomUser.objects.filter(
            last_activity__gte=last_24h
        ).count()

        context = {
            'title': 'Analytics Kwijiya',
            'total_users': total_users,
            'new_users_24h': new_users_24h,
            'active_users_24h': active_users_24h,
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'completion_rate': f'{completion_rate:.1f}%',
        }

        return super().changelist_view(request, extra_context=context)

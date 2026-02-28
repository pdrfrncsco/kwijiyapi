"""
Rankings views — dynamic queries on CustomUser, no separate tables.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from users.models import CustomUser
from gamification.models import UserXPLog


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def global_ranking(request):
    """Top users by total XP (all time)."""
    users = CustomUser.objects.filter(
        is_guest=False, is_active=True
    ).order_by('-total_xp')[:50]

    data = [
        {
            'rank': i + 1,
            'user_id': str(u.id),
            'username': u.username or u.email or 'Anónimo',
            'avatar': u.avatar,
            'title': u.title,
            'total_xp': u.total_xp,
            'level': u.level,
            'streak_days': u.streak_days,
        }
        for i, u in enumerate(users)
    ]

    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def weekly_ranking(request):
    """Top users by XP earned this week."""
    one_week_ago = timezone.now() - timedelta(days=7)

    # Aggregate XP per user for the last 7 days
    from django.db.models import Sum

    xp_by_user = (
        UserXPLog.objects
        .filter(created_at__gte=one_week_ago)
        .values('user')
        .annotate(weekly_xp=Sum('xp_gained'))
        .order_by('-weekly_xp')[:50]
    )

    user_ids = [entry['user'] for entry in xp_by_user]
    users = {str(u.id): u for u in CustomUser.objects.filter(id__in=user_ids)}

    data = []
    for i, entry in enumerate(xp_by_user):
        user = users.get(str(entry['user']))
        if user and not user.is_guest:
            data.append({
                'rank': i + 1,
                'user_id': str(user.id),
                'username': user.username or user.email or 'Anónimo',
                'avatar': user.avatar,
                'title': user.title,
                'total_xp': entry['weekly_xp'] or 0,
                'level': user.level,
                'streak_days': user.streak_days,
            })

    return Response(data)

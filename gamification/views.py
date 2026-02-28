from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import UserXPLog, Badge
from .serializers import UserXPLogSerializer, BadgeSerializer


class UserXPLogListView(generics.ListAPIView):
    """List XP gain history for the authenticated user."""
    serializer_class = UserXPLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserXPLog.objects.filter(user=self.request.user)


class BadgeListView(generics.ListAPIView):
    """List all badges with earned status."""
    serializer_class = BadgeSerializer
    permission_classes = [IsAuthenticated]
    queryset = Badge.objects.all()
    pagination_class = None

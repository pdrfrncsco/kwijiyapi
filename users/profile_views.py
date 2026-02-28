"""
Profile views — GET / PATCH for authenticated user.
"""

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import logging
from .models import CustomUser
from .serializers import UserProfileSerializer


logger = logging.getLogger(__name__)


class ProfileView(generics.RetrieveUpdateAPIView):
    """Get or update the authenticated user's profile."""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        user = request.user
        logger.info(
            "ProfileView user=%s total_xp=%s streak_days=%s coins=%s",
            user.id,
            user.total_xp,
            user.streak_days,
            user.coins,
        )
        return response

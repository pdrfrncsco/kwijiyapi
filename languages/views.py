from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Language
from .serializers import LanguageSerializer


class LanguageListView(generics.ListAPIView):
    """List all active languages."""
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Language.objects.filter(is_active=True)

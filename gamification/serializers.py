from rest_framework import serializers
from .models import UserXPLog, Badge, UserBadge


class UserXPLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserXPLog
        fields = ['id', 'xp_gained', 'source', 'description', 'created_at']


class BadgeSerializer(serializers.ModelSerializer):
    is_earned = serializers.SerializerMethodField()

    class Meta:
        model = Badge
        fields = ['id', 'name', 'description', 'icon', 'xp_required', 'is_earned']

    def get_is_earned(self, obj):
        user = self.context.get('request', {})
        if hasattr(user, 'user'):
            user = user.user
        else:
            return False
        return UserBadge.objects.filter(user=user, badge=obj).exists()

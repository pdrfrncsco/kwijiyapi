from rest_framework import serializers
from .models import CustomUser


class RequestOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6, min_length=6)


class UserProfileSerializer(serializers.ModelSerializer):
    title = serializers.ReadOnlyField()
    xp_for_next_level = serializers.ReadOnlyField()
    xp_progress = serializers.ReadOnlyField()
    badges = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'username', 'avatar', 'age_group', 'date_of_birth',
            'total_xp', 'level', 'streak_days', 'coins',
            'title', 'xp_for_next_level', 'xp_progress',
            'is_guest', 'last_activity', 'created_at',
            'badges',
        ]
        read_only_fields = [
            'id', 'email', 'age_group', 'total_xp', 'level', 'streak_days',
            'coins', 'is_guest', 'created_at',
        ]

    def get_badges(self, obj):
        # Import here to avoid circular dependency
        from gamification.models import UserBadge
        user_badges = UserBadge.objects.filter(user=obj).select_related('badge')
        return [
            {
                'name': ub.badge.name,
                'description': ub.badge.description,
                'icon': ub.badge.icon,
                'awarded_at': ub.awarded_at
            }
            for ub in user_badges
        ]

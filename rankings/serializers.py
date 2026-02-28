from rest_framework import serializers


class RankingEntrySerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    user_id = serializers.UUIDField()
    username = serializers.CharField()
    avatar = serializers.CharField()
    title = serializers.CharField()
    total_xp = serializers.IntegerField()
    level = serializers.IntegerField()
    streak_days = serializers.IntegerField()

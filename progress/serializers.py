from rest_framework import serializers
from .models import UserProgress, UserAnswer


class UserProgressSerializer(serializers.ModelSerializer):
    language_name = serializers.CharField(source='language.name', read_only=True)
    language_code = serializers.CharField(source='language.code', read_only=True)

    class Meta:
        model = UserProgress
        fields = [
            'id', 'language', 'language_name', 'language_code',
            'level', 'completed_lessons', 'accuracy_rate', 'last_activity',
        ]


class UserStatsSerializer(serializers.Serializer):
    total_answers = serializers.IntegerField()
    correct_answers = serializers.IntegerField()
    overall_accuracy = serializers.FloatField()
    total_quiz_sessions = serializers.IntegerField()
    languages_studied = serializers.IntegerField()

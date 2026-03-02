from rest_framework import serializers
from .models import Word, Question, Option, QuizSession


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "text"]
        # Note: is_correct is NOT exposed to the client


class PlacementOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ["id", "text", "is_correct"]


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "question_type",
            "difficulty",
            "question_text",
            "timer_seconds",
            "xp_value",
            "options",
        ]


class PlacementQuestionSerializer(serializers.ModelSerializer):
    options = PlacementOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "question_type",
            "difficulty",
            "question_text",
            "timer_seconds",
            "xp_value",
            "options",
        ]


class QuizSessionSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    accuracy = serializers.ReadOnlyField()
    language_name = serializers.CharField(source="language.name", read_only=True)

    class Meta:
        model = QuizSession
        fields = [
            "id",
            "language",
            "language_name",
            "level",
            "total_questions",
            "correct_answers",
            "total_xp_earned",
            "total_makuta_earned",
            "accuracy",
            "is_completed",
            "started_at",
            "completed_at",
            "questions",
        ]


class StartQuizSerializer(serializers.Serializer):
    language_code = serializers.CharField(max_length=10)
    level = serializers.IntegerField(min_value=1, max_value=3, default=1)
    num_questions = serializers.IntegerField(min_value=3, max_value=20, default=10)


class SubmitAnswerSerializer(serializers.Serializer):
    session_id = serializers.UUIDField()
    question_id = serializers.UUIDField()
    option_id = serializers.UUIDField()
    time_taken = serializers.FloatField(min_value=0, max_value=30)  # seconds

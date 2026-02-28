from django.contrib import admin
from .models import UserProgress, UserAnswer


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'language', 'level', 'completed_lessons', 'accuracy_rate']
    list_filter = ['language', 'level']


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'is_correct', 'time_taken', 'answered_at']
    list_filter = ['is_correct']

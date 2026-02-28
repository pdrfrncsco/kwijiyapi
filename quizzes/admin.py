from django.contrib import admin
from .models import Word, Question, Option, QuizSession


class OptionInline(admin.TabularInline):
    model = Option
    extra = 4


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ['word_native', 'word_portuguese', 'language', 'difficulty', 'category']
    list_filter = ['language', 'difficulty', 'category']
    search_fields = ['word_native', 'word_portuguese']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'language', 'difficulty', 'question_type', 'xp_value']
    list_filter = ['language', 'difficulty', 'question_type']
    search_fields = ['question_text']
    inlines = [OptionInline]


@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'language', 'level', 'correct_answers', 'total_questions', 'is_completed']
    list_filter = ['language', 'level', 'is_completed']

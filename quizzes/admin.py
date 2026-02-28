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
    list_display = ['question_text', 'language', 'difficulty', 'question_type', 'xp_value', 'has_correct_option']
    list_filter = ['language', 'difficulty', 'question_type']
    search_fields = ['question_text']
    inlines = [OptionInline]
    
    def has_correct_option(self, obj):
        has_correct = obj.options.filter(is_correct=True).exists()
        return has_correct
    has_correct_option.boolean = True
    has_correct_option.short_description = "Tem Resposta?"

@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'language', 'level', 'score_ratio', 'started_at', 'is_completed']
    list_filter = ['language', 'level', 'is_completed', 'started_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['started_at', 'completed_at']

    def score_ratio(self, obj):
        return f"{obj.correct_answers}/{obj.total_questions}"
    score_ratio.short_description = "Pontuação"

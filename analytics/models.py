from django.db import models
from quizzes.models import QuizSession


class AnalyticsDashboard(QuizSession):
    class Meta:
        proxy = True
        verbose_name = 'Painel de Analytics'
        verbose_name_plural = 'Painel de Analytics'

    def __str__(self):
        return 'Painel de Analytics'


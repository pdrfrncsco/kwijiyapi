import uuid
from django.db import models
from django.conf import settings


class UserProgress(models.Model):
    """User progress per language."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress'
    )
    language = models.ForeignKey(
        'languages.Language', on_delete=models.CASCADE, related_name='user_progress'
    )
    level = models.PositiveIntegerField(default=1)
    completed_lessons = models.PositiveIntegerField(default=0)
    accuracy_rate = models.FloatField(default=0.0)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Progresso do Utilizador'
        verbose_name_plural = 'Progressos dos Utilizadores'
        unique_together = ['user', 'language']

    def __str__(self):
        return f'{self.user} — {self.language.name} L{self.level}'


class UserAnswer(models.Model):
    """Record of each answer submitted by a user."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='answers'
    )
    question = models.ForeignKey(
        'quizzes.Question', on_delete=models.CASCADE, related_name='user_answers'
    )
    selected_option = models.ForeignKey(
        'quizzes.Option', on_delete=models.CASCADE, related_name='selections'
    )
    quiz_session = models.ForeignKey(
        'quizzes.QuizSession', on_delete=models.CASCADE,
        related_name='answers', null=True, blank=True,
    )
    is_correct = models.BooleanField()
    time_taken = models.FloatField(help_text='Seconds')
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Resposta do Utilizador'
        verbose_name_plural = 'Respostas dos Utilizadores'
        ordering = ['-answered_at']

    def __str__(self):
        mark = '✔' if self.is_correct else '✘'
        return f'{mark} {self.user} → Q:{self.question_id}'

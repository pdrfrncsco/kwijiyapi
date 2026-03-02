import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


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


class SpacedRepetitionItem(models.Model):
    """
    Tracks spacing for each user-question pair.
    Uses simplified SM-2 (or Leitner) for scheduling.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='srs_items'
    )
    question = models.ForeignKey(
        'quizzes.Question', on_delete=models.CASCADE, related_name='srs_items'
    )
    
    # SRS parameters
    easiness = models.FloatField(default=2.5)  # SM-2 EF factor
    interval = models.IntegerField(default=1)  # Days until next review
    repetitions = models.IntegerField(default=0)  # Consecutive correct answers
    
    next_review = models.DateTimeField(default=timezone.now)
    last_review = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'question')
        verbose_name = 'Item de Repetição Espaçada'
        verbose_name_plural = 'Itens de Repetição Espaçada'

    def __str__(self):
        return f'{self.user} - {self.question} (Due: {self.next_review.date()})'

    def schedule_next(self, quality: int):
        """
        Update interval based on answer quality (0-5).
        quality: 5=perfect, 0=complete blackout.
        """
        if quality >= 3:
            if self.repetitions == 0:
                self.interval = 1
            elif self.repetitions == 1:
                self.interval = 6
            else:
                self.interval = int(self.interval * self.easiness)
            
            self.repetitions += 1
            
            # Update EF
            self.easiness = self.easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
            if self.easiness < 1.3:
                self.easiness = 1.3
        else:
            self.repetitions = 0
            self.interval = 1
        
        self.next_review = timezone.now() + timezone.timedelta(days=self.interval)
        self.save()

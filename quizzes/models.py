"""
Quiz models: Word, Question, Option, QuizSession.
"""

import uuid
from django.db import models
from django.conf import settings


class Word(models.Model):
    """Vocabulary word in a national language."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    language = models.ForeignKey(
        'languages.Language', on_delete=models.CASCADE, related_name='words'
    )
    word_native = models.CharField(max_length=100)
    word_portuguese = models.CharField(max_length=100)
    pronunciation_audio = models.FileField(
        upload_to='audio/words/', null=True, blank=True
    )
    difficulty = models.PositiveIntegerField(default=1)  # 1, 2, 3
    category = models.CharField(
        max_length=50,
        choices=[
            ('saudacoes', 'Saudações'),
            ('pronomes', 'Pronomes'),
            ('verbos', 'Verbos'),
            ('animais', 'Animais'),
            ('familia', 'Família'),
            ('numeros', 'Números'),
            ('cores', 'Cores'),
            ('cultura', 'Cultura'),
            ('natureza', 'Natureza'),
            ('corpo', 'Corpo Humano'),
            ('alimentos', 'Alimentos'),
        ],
        default='saudacoes',
    )
    explanation = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Palavra'
        verbose_name_plural = 'Palavras'
        ordering = ['language', 'difficulty', 'category']
        unique_together = ['language', 'word_native']

    def __str__(self):
        return f'{self.word_native} → {self.word_portuguese} ({self.language.code})'


QUESTION_TYPES = [
    ('multiple_choice', 'Escolha Múltipla'),
    ('audio', 'Áudio'),
    ('fill_blank', 'Completar Frase'),
    ('translation', 'Tradução Direta'),
]


class Question(models.Model):
    """Quiz question."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    language = models.ForeignKey(
        'languages.Language', on_delete=models.CASCADE, related_name='questions'
    )
    word = models.ForeignKey(
        Word, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions'
    )
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='multiple_choice')
    difficulty = models.PositiveIntegerField(default=1)  # 1, 2, 3
    question_text = models.TextField()
    explanation = models.TextField(blank=True, default='')
    cultural_note = models.TextField(blank=True, default='')
    timer_seconds = models.PositiveIntegerField(default=5)
    xp_value = models.PositiveIntegerField(default=100)
    min_age = models.PositiveIntegerField(default=0)  # Age restriction
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pergunta'
        verbose_name_plural = 'Perguntas'
        ordering = ['language', 'difficulty']

    def __str__(self):
        return f'[{self.language.code}] L{self.difficulty}: {self.question_text[:60]}'


class Option(models.Model):
    """Answer option for a question."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='options'
    )
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Opção'
        verbose_name_plural = 'Opções'

    def __str__(self):
        mark = '✔' if self.is_correct else '✘'
        return f'{mark} {self.text}'


class QuizSession(models.Model):
    """A quiz session (a set of questions answered by a user)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_sessions'
    )
    language = models.ForeignKey(
        'languages.Language', on_delete=models.CASCADE, related_name='sessions'
    )
    level = models.PositiveIntegerField(default=1)
    questions = models.ManyToManyField(Question, blank=True, related_name='sessions')
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    total_xp_earned = models.PositiveIntegerField(default=0)
    total_makuta_earned = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Sessão de Quiz'
        verbose_name_plural = 'Sessões de Quiz'
        ordering = ['-started_at']

    def __str__(self):
        return f'Sessão {self.id} ({self.user}) — {self.language.code} L{self.level}'

    @property
    def accuracy(self):
        if self.total_questions == 0:
            return 0
        return round(self.correct_answers / self.total_questions * 100, 1)

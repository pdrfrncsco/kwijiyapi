import uuid
from django.db import models
from django.conf import settings


class UserXPLog(models.Model):
    """Log of XP gains for a user."""

    SOURCE_CHOICES = [
        ('quiz', 'Quiz'),
        ('streak', 'Streak Bonus'),
        ('challenge', 'Desafio Diário'),
        ('level_up', 'Subida de Nível'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='xp_logs'
    )
    xp_gained = models.PositiveIntegerField()
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    description = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Log de XP'
        verbose_name_plural = 'Logs de XP'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} +{self.xp_gained} XP ({self.source})'


class Badge(models.Model):
    """Achievement badge."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, default='')
    icon = models.CharField(max_length=50, default='🏆')
    xp_required = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Medalha'
        verbose_name_plural = 'Medalhas'
        ordering = ['xp_required']

    def __str__(self):
        return f'{self.icon} {self.name}'


class UserBadge(models.Model):
    """Badge awarded to a user."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='badges'
    )
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='users')
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Medalha do Utilizador'
        verbose_name_plural = 'Medalhas dos Utilizadores'
        unique_together = ['user', 'badge']

    def __str__(self):
        return f'{self.user} — {self.badge.name}'

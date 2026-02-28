import uuid
from django.db import models


class Language(models.Model):
    """National language of Angola."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)  # e.g. Kimbundu
    code = models.CharField(max_length=10, unique=True)   # e.g. kmb
    description = models.TextField(blank=True, default='')
    region = models.CharField(max_length=100, blank=True, default='')
    difficulty_level = models.CharField(
        max_length=20,
        choices=[('easy', 'Fácil'), ('medium', 'Médio'), ('hard', 'Difícil')],
        default='medium',
    )
    num_speakers = models.CharField(max_length=50, blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Língua'
        verbose_name_plural = 'Línguas'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.code})'

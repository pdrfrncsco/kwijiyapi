"""
Rankings models: WeeklyRankingArchive for historical data.
"""

from django.db import models
from django.conf import settings
import uuid

class WeeklyRankingArchive(models.Model):
    """
    Archives the top users of a past week.
    Created by Celery task at the end of each week.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    week_start = models.DateField()
    week_end = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-week_end']
        verbose_name = 'Arquivo de Ranking Semanal'
        verbose_name_plural = 'Arquivos de Ranking Semanal'

    def __str__(self):
        return f'Ranking {self.week_start} - {self.week_end}'


class RankingEntry(models.Model):
    """
    An entry in a weekly archive.
    """
    archive = models.ForeignKey(
        WeeklyRankingArchive, on_delete=models.CASCADE, related_name='entries'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ranking_entries'
    )
    rank = models.PositiveIntegerField()
    xp_earned = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['rank']
        unique_together = ['archive', 'user']


class WeeklyRankingSnapshot(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="weekly_snapshots"
    )
    week_number = models.IntegerField()
    year = models.IntegerField()
    xp_week = models.IntegerField()
    position = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [["user", "week_number", "year"]]
        indexes = [
            models.Index(fields=["year", "week_number", "position"]),
        ]

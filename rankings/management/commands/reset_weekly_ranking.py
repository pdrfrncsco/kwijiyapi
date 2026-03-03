from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
import logging

logger = logging.getLogger("rankings")


class Command(BaseCommand):
    help = "Arquiva snapshot do ranking semanal (correr toda segunda-feira)"

    def handle(self, *args, **options):
        from gamification.models import UserXPLog
        from rankings.models import WeeklyRankingSnapshot

        now = timezone.now()
        week_start = now.date() - timedelta(days=7)
        week_number = now.isocalendar()[1]
        year = now.year

        weekly_xp = (
            UserXPLog.objects
            .filter(created_at__date__gte=week_start)
            .values("user")
            .annotate(xp_week=Sum("xp_gained"))
            .order_by("-xp_week")
        )

        count = 0
        for position, entry in enumerate(weekly_xp[:500], 1):
            WeeklyRankingSnapshot.objects.update_or_create(
                user_id=entry["user"],
                week_number=week_number,
                year=year,
                defaults={
                    "xp_week": entry["xp_week"],
                    "position": position,
                }
            )
            count += 1

        logger.info(f"Weekly ranking archived: week={week_number}, year={year}, entries={count}")
        self.stdout.write(self.style.SUCCESS(f"Semana {week_number}/{year}: {count} entradas arquivadas"))

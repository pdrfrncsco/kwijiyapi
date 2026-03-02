from celery import shared_task
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
import logging

from .models import WeeklyRankingArchive, RankingEntry
from gamification.models import UserXPLog
from users.models import CustomUser

logger = logging.getLogger(__name__)

@shared_task
def reset_weekly_rankings():
    """
    1. Calculate weekly ranking for the ending week.
    2. Archive it.
    3. (Implicitly) The next week starts fresh as queries filter by date.
    """
    logger.info("Starting weekly ranking reset task...")
    
    today = timezone.now().date()
    # Assume this runs on Monday at 00:00, so we archive the previous week (Mon-Sun)
    # Start of previous week
    last_week_start = today - timedelta(days=7)
    # End of previous week
    last_week_end = today - timedelta(days=1)
    
    logger.info(f"Archiving ranking for {last_week_start} to {last_week_end}")

    # Calculate XP gained in that range
    xp_by_user = (
        UserXPLog.objects
        .filter(created_at__date__gte=last_week_start, created_at__date__lte=last_week_end)
        .values('user')
        .annotate(weekly_xp=Sum('xp_gained'))
        .order_by('-weekly_xp')[:100]  # Archive top 100
    )

    if not xp_by_user:
        logger.info("No XP activity found for last week.")
        return

    # Create Archive
    archive = WeeklyRankingArchive.objects.create(
        week_start=last_week_start,
        week_end=last_week_end
    )

    entries = []
    for i, entry in enumerate(xp_by_user):
        user_id = entry['user']
        xp = entry['weekly_xp']
        
        try:
            user = CustomUser.objects.get(id=user_id)
            entries.append(RankingEntry(
                archive=archive,
                user=user,
                rank=i + 1,
                xp_earned=xp
            ))
        except CustomUser.DoesNotExist:
            continue
            
    RankingEntry.objects.bulk_create(entries)
    
    logger.info(f"Successfully archived {len(entries)} ranking entries.")

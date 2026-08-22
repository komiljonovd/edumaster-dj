from celery import shared_task
from django.core.cache import cache
from edumasterapp.repository.dashboard_repository import DashboardRepository

CACHE_KEY = "admin_dashboard_stats"
CACHE_TTL = 60 * 60


@shared_task
def sync_dashboard_to_redis_task() -> str:
    """Берет всю дату из БД и сохраняет в Redis."""

    repo = DashboardRepository()

    stats = repo.get_statistics()

    cache.set(CACHE_KEY, stats, timeout=CACHE_TTL)

    return "Dashboard data saved to Redis successfully!"

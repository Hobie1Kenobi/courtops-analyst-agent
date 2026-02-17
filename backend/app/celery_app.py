from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "courtops_agent",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    timezone="UTC",
    beat_schedule={
        "daily-sla-and-inventory-checks": {
            "task": "app.tasks.daily_checks.run_daily_checks",
            "schedule": 60 * 60 * 24,
        },
        "weekly-patch-and-data-quality-checks": {
            "task": "app.tasks.weekly_checks.run_weekly_checks",
            "schedule": 60 * 60 * 24 * 7,
        },
        "monthly-report-generation": {
            "task": "app.tasks.monthly_reports.run_monthly_reports",
            "schedule": 60 * 60 * 24 * 30,
        },
    },
)


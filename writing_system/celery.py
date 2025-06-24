from __future__ import absolute_import, unicode_literals
import os
import json
from celery import Celery
from celery.schedules import crontab

# Set default Django settings module for Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "writing_system.settings")

app = Celery("writing_system")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")

# --- Static CELERY_BEAT_SCHEDULE ---
app.conf.beat_schedule = {
    "deactivate-expired-discounts": {
        "task": "discounts.tasks.deactivate_expired_discounts",
        "schedule": crontab(minute=0, hour=0),  # Daily midnight
    },
    "update_engagement_stats_every_minute": {
        "task": "blogs.tasks.update_engagement_stats",
        "schedule": crontab(minute="*/1"),  # Every minute
    },
    "check_for_broken_links": {
        "task": "blogs.tasks.check_for_broken_links",
        "schedule": crontab(day_of_month="15"),  # Mid-month
    },
    "expire-stale-requests-every-minute": {
        "task": "tasks.order_request_tasks.expire_stale_requests",
        "schedule": crontab(minute="*"),  # Every minute
    },
    "archive-expired-orders-every-day": {
        "task": "orders.tasks.archive_expired_orders",
        "schedule": crontab(minute=0, hour=2),  # Daily at 2AM
    },
    "generate_monthly_review_summary": {
        "task": "orders.tasks.review_analytics.generate_monthly_review_summary",
        "schedule": crontab(minute=0, hour=4, day_of_month=1),  # Monthly
    },
    'decay-referral-bonuses-monthly': {
        'task': 'loyalty_management.tasks.apply_monthly_referral_bonus_decay',
        'schedule': crontab(day_of_month=1, hour=1, minute=0),
    },
}

# --- Dynamic Schedule via django-celery-beat ---
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule

    # Interval Schedules
    every_5_min, _ = IntervalSchedule.objects.get_or_create(every=5, period=IntervalSchedule.MINUTES)
    every_24_hours, _ = IntervalSchedule.objects.get_or_create(every=1440, period=IntervalSchedule.MINUTES)

    periodic_tasks = [
        {"name": "Sync Blog Clicks", "task": "blog_management.tasks.sync_blog_clicks_to_db", "schedule": every_5_min},
        {"name": "Sync Blog Conversions", "task": "blog_management.tasks.sync_blog_conversions_to_db", "schedule": every_5_min},
        {"name": "Update Freshness Scores", "task": "blog_management.tasks.update_freshness_scores", "schedule": every_24_hours},
        {"name": "Publish Scheduled Blogs", "task": "blog_management.tasks.publish_scheduled_blogs", "schedule": every_5_min},
        {"name": "Cleanup Soft Deleted Blogs", "task": "blog_management.tasks.cleanup_soft_deleted_blogs", "schedule": every_24_hours},
        {"name": "Warn Admins Before Deletion", "task": "blog_management.tasks.warn_admins_before_deletion", "schedule": every_24_hours},
    ]

    for task in periodic_tasks:
        PeriodicTask.objects.update_or_create(
            name=task["name"],
            defaults={"interval": task["schedule"], "task": task["task"], "args": json.dumps([]), "enabled": True}
        )

    # Crontab Schedules
    weekly_schedule, _ = CrontabSchedule.objects.get_or_create(minute=0, hour=8, day_of_week=1)
    sunday_schedule, _ = CrontabSchedule.objects.get_or_create(minute=0, hour=9, day_of_week=0)

    crontab_tasks = [
        {"name": "Send Weekly Newsletter", "task": "blog_management.tasks.send_weekly_newsletter", "schedule": weekly_schedule},
        {"name": "Check for Broken Links", "task": "blog_management.tasks.check_for_broken_links", "schedule": sunday_schedule},
    ]

    for task in crontab_tasks:
        PeriodicTask.objects.update_or_create(
            name=task["name"],
            defaults={"crontab": task["schedule"], "task": task["task"], "args": json.dumps([]), "enabled": True}
        )

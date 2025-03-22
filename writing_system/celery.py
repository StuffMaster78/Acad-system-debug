from celery.schedules import crontab
from celery import Celery
import os
from celery import Celery

# Set default Django settings module for Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "your_project.settings")

app = Celery("your_project")

# Load task modules from all registered Django apps
app.config_from_object("django.conf:settings", namespace="CELERY")

# Autodiscover tasks from installed apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")  # Simple debug task


app = Celery("writing_system")

app.conf.beat_schedule = {
    "deactivate-expired-discounts": {
        "task": "discounts.tasks.deactivate_expired_discounts",
        "schedule": crontab(minute=0, hour=0),  # Runs daily at midnight
    },
}



CELERY_BEAT_SCHEDULE = {
    "update_engagement_stats_every_minute": {
        "task": "blogs.tasks.update_engagement_stats",
        "schedule": crontab(minute="*/1"),  # Runs every 1 minute
    },
}

CELERY_BEAT_SCHEDULE = {
    "check_for_broken_links": {
        "task": "blogs.tasks.check_for_broken_links",
        "schedule": crontab(day_of_month="15"),  # Runs mid-month
    }
}


# Start Celery Beat automatically when Celery starts
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
    import json

    # Set up intervals
    every_5_min, _ = IntervalSchedule.objects.get_or_create(every=5, period=IntervalSchedule.MINUTES)
    every_24_hours, _ = IntervalSchedule.objects.get_or_create(every=1440, period=IntervalSchedule.MINUTES)

    # Define periodic tasks
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

    # Set up crontab tasks (Weekly & Daily Schedules)
    weekly_schedule, _ = CrontabSchedule.objects.get_or_create(minute=0, hour=8, day_of_week=1, day_of_month="*", month_of_year="*")
    sunday_schedule, _ = CrontabSchedule.objects.get_or_create(minute=0, hour=9, day_of_week=0, day_of_month="*", month_of_year="*")

    crontab_tasks = [
        {"name": "Send Weekly Newsletter", "task": "blog_management.tasks.send_weekly_newsletter", "schedule": weekly_schedule},
        {"name": "Check for Broken Links", "task": "blog_management.tasks.check_for_broken_links", "schedule": sunday_schedule},
    ]

    for task in crontab_tasks:
        PeriodicTask.objects.update_or_create(
            name=task["name"],
            defaults={"crontab": task["schedule"], "task": task["task"], "args": json.dumps([]), "enabled": True}
        )
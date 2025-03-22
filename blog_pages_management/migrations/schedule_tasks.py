from django.db import migrations
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
import json

def schedule_celery_tasks(apps, schema_editor):
    """
    Schedules Celery tasks using Celery Beat.
    """

    # Define intervals for frequent tasks
    interval_tasks = [
        {"name": "Sync Blog Clicks to DB", "task": "blog_management.tasks.sync_blog_clicks_to_db", "interval": 5},
        {"name": "Sync Blog Conversions to DB", "task": "blog_management.tasks.sync_blog_conversions_to_db", "interval": 5},
        {"name": "Update Freshness Scores", "task": "blog_management.tasks.update_freshness_scores", "interval": 1440},  # 24 hours
        {"name": "Auto-Publish Scheduled Blogs", "task": "blog_management.tasks.publish_scheduled_blogs", "interval": 5},
        {"name": "Auto-Delete Expired Blogs", "task": "blog_management.tasks.cleanup_soft_deleted_blogs", "interval": 1440},
        {"name": "Warn Admins Before Blog Deletion", "task": "blog_management.tasks.warn_admins_before_deletion", "interval": 1440},
    ]

    for task_data in interval_tasks:
        schedule, _ = IntervalSchedule.objects.get_or_create(every=task_data["interval"], period=IntervalSchedule.MINUTES)
        PeriodicTask.objects.update_or_create(
            name=task_data["name"],
            defaults={"interval": schedule, "task": task_data["task"], "args": json.dumps([]), "enabled": True}
        )

    # Define crontab schedules for less frequent tasks
    crontab_tasks = [
        {"name": "Send Weekly Newsletter", "task": "blog_management.tasks.send_weekly_newsletter", "minute": 0, "hour": 8, "day_of_week": 1},
        {"name": "Check for Broken Links", "task": "blog_management.tasks.check_for_broken_links", "minute": 0, "hour": 9, "day_of_week": 0},
    ]

    for task_data in crontab_tasks:
        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=task_data["minute"],
            hour=task_data["hour"],
            day_of_week=task_data["day_of_week"],
            day_of_month="*",
            month_of_year="*"
        )
        PeriodicTask.objects.update_or_create(
            name=task_data["name"],
            defaults={"crontab": schedule, "task": task_data["task"], "args": json.dumps([]), "enabled": True}
        )

def remove_celery_tasks(apps, schema_editor):
    """
    Removes scheduled Celery tasks when rolling back the migration.
    """
    PeriodicTask.objects.filter(name__in=[
        "Sync Blog Clicks to DB", "Sync Blog Conversions to DB",
        "Update Freshness Scores", "Auto-Publish Scheduled Blogs",
        "Auto-Delete Expired Blogs", "Warn Admins Before Blog Deletion",
        "Send Weekly Newsletter", "Check for Broken Links"
    ]).delete()

class Migration(migrations.Migration):

    dependencies = [
        ("blog_management", "0001_initial"),
        ("django_celery_beat", "0012_auto_20210430_0921"),  # Ensure Celery Beat is migrated
    ]

    operations = [
        migrations.RunPython(schedule_celery_tasks, reverse_code=remove_celery_tasks),
    ]
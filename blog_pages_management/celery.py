from celery.schedules import crontab
from celery import Celery



app = Celery("blog_management")

app.conf.beat_schedule = {
    "auto-delete-soft-deleted-blogs-daily": {
        "task": "blog_management.tasks.auto_delete_soft_deleted_blogs",
        "schedule": crontab(hour=0, minute=0),  # Runs daily at midnight
    },
}
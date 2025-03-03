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

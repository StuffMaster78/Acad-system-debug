from __future__ import annotations

from celery.schedules import crontab
from celery import Celery

from writing_system.celery import app


app.conf.beat_schedule = {
    "process-outbox-every-30-seconds": {
        "task": "writer_payments_management.tasks.outbox_tasks.process_outbox_events",
        "schedule": 30.0,
        "args": (100,),
    },
}
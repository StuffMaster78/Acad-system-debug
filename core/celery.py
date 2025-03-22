# core/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set up the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'writing_system.settings')

celery = Celery('writing_system')

# Load task modules from all registered Django apps
celery.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed apps
celery.autodiscover_tasks()

@celery.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
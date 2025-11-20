from celery.schedules import crontab
from django.conf import settings

CELERY_BEAT_SCHEDULE = {
    'expire-referral-bonuses-daily': {
        'task': 'wallet.tasks.expire_referral_bonuses',
        'schedule': crontab(hour=0, minute=0),  # Runs at midnight daily
    },
}
# notifications_system/checks.py
"""
Django system checks for the notification system.
Run on startup to catch configuration errors early.
"""
from __future__ import annotations

from django.core.checks import Error, Warning, register


@register()
def check_email_provider_configured(app_configs, **kwargs):
    """Warn if no email provider is configured."""
    from django.conf import settings
    errors = []

    provider = getattr(settings, 'DEFAULT_EMAIL_PROVIDER', None)
    if not provider or provider == 'console':
        errors.append(
            Warning(
                'DEFAULT_EMAIL_PROVIDER is not configured. '
                'Emails will be printed to console only.',
                hint=(
                    "Set DEFAULT_EMAIL_PROVIDER to 'sendgrid', 'mailgun', "
                    "or 'ses' in your settings."
                ),
                id='notifications_system.W001',
            )
        )
    return errors


@register()
def check_celery_configured(app_configs, **kwargs):
    """Warn if Celery appears unconfigured."""
    from django.conf import settings
    errors = []

    broker = getattr(settings, 'CELERY_BROKER_URL', None)
    if not broker:
        errors.append(
            Warning(
                'CELERY_BROKER_URL is not set. '
                'Async notification delivery will not work.',
                hint='Set CELERY_BROKER_URL in your settings e.g. redis://localhost:6379/0',
                id='notifications_system.W002',
            )
        )
    return errors


@register()
def check_notifications_enabled(app_configs, **kwargs):
    """Info check — confirm notifications are enabled."""
    from django.conf import settings
    errors = []

    if not getattr(settings, 'ENABLE_NOTIFICATIONS', True):
        errors.append(
            Warning(
                'ENABLE_NOTIFICATIONS is False. '
                'No notifications will be sent.',
                hint='Set ENABLE_NOTIFICATIONS = True in your settings.',
                id='notifications_system.W003',
            )
        )
    return errors
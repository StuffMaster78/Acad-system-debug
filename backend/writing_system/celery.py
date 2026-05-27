# writing_system/celery.py
from __future__ import annotations
import os, json

# --- Try real Celery; otherwise fall back to a safe shim ---------------------
try:
    from celery import Celery  # type: ignore
    from celery.schedules import crontab  # type: ignore
    CELERY_AVAILABLE = True
except Exception:
    CELERY_AVAILABLE = False

    # tiny crontab stub so your schedule dict compiles
    def crontab(*args, **kwargs):  # type: ignore
        return None

    # signal stub
    class _Signal:
        def connect(self, f):  # decorator-style .connect
            return f

    # no-op Celery shim with the handful of APIs you use
    class Celery:  # type: ignore
        def __init__(self, *a, **k):
            class _Conf:
                beat_schedule = {}
            self.conf = _Conf()
            self.on_after_configure = _Signal()

        def config_from_object(self, *a, **k):  # real Celery API
            return None

        def update_config(self, **k):
            # compat if code calls app.conf.update(...)
            for k_, v_ in (k or {}).items():
                setattr(self.conf, k_, v_)
            return None

        def autodiscover_tasks(self, *a, **k):  # real Celery API
            return None

        def task(self, *dargs, **dkwargs):
            # decorator passthrough: @app.task(...) just returns the func
            def _decorator(func):
                return func
            return _decorator

# ---------------------------------------------------------------------------

# Ensure Django settings for Celery loader
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "writing_system.settings")

app = Celery("writing_system")

# Broker/backends: default to in-memory if not provided
broker_url = os.getenv("CELERY_BROKER_URL", "memory://")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "cache+memory://")

# Support both app.conf.update(...) and app.update_config(...)
_config = {
    "broker_url": broker_url,
    "result_backend": result_backend,
    "task_ignore_result": True,
}
try:
    # real Celery has app.conf.update
    app.conf.update(**_config)  # type: ignore[attr-defined]
except Exception:
    # shim exposes update_config
    app.update_config(**_config)  # type: ignore[attr-defined]

# Try to pull Django settings namespace if Celery is present
if CELERY_AVAILABLE:
    try:
        app.config_from_object("django.conf:settings", namespace="CELERY")
    except Exception:
        # non-fatal; you still have explicit broker/backends above
        pass

# Autodiscover tasks from all installed apps
# This will automatically find tasks.py files in each installed app
# By default, it looks for 'tasks' modules in all installed Django apps
if CELERY_AVAILABLE:
    app.autodiscover_tasks()
    # Also explicitly tell it to look in notifications_system
    try:
        app.autodiscover_tasks(['notifications_system'])
    except Exception:
        pass  # If it fails, autodiscover should have already found it

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")

# ---------- Static Beat Schedule (safe even with shim) ----------
# Using crontab() stub returns None when Celery isn't installed; harmless.
app.conf.beat_schedule = {  # type: ignore[attr-defined]
    "send-scheduled-announcements": {
        "task": "announcements.tasks.send_scheduled_announcements",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
    "expire-announcements": {
        "task": "announcements.tasks.expire_announcements",
        "schedule": crontab(minute=0, hour=0),  # Daily at midnight
    },
    "deactivate-expired-discounts": {
        "task": "discounts.tasks.deactivate_expired_discounts",
        "schedule": crontab(minute=0, hour=0),
    },
    "update_engagement_stats_every_minute": {
        "task": "blogs.tasks.update_engagement_stats",
        "schedule": crontab(minute="*/1"),
    },
    "check_for_broken_links": {
        "task": "blogs.tasks.check_for_broken_links",
        "schedule": crontab(day_of_month="15"),
    },
    "expire-stale-requests-every-minute": {
        "task": "tasks.order_request_tasks.expire_stale_requests",
        "schedule": crontab(minute="*"),
    },
    "archive-expired-orders-every-day": {
        "task": "orders.tasks.archive_expired_orders",
        "schedule": crontab(minute=0, hour=2),
    },
    "generate_monthly_review_summary": {
        "task": "orders.tasks.review_analytics.generate_monthly_review_summary",
        "schedule": crontab(minute=0, hour=4, day_of_month=1),
    },
    "decay-referral-bonuses-monthly": {
        "task": "loyalty_management.tasks.apply_monthly_referral_bonus_decay",
        "schedule": crontab(day_of_month=1, hour=1, minute=0),
    },
    "weekly_writer_metrics": {
        "task": "writer_management.tasks.performance.generate_weekly_performance_snapshots",
        "schedule": crontab(hour=3, minute=0, day_of_week="sunday"),
    },
    "run_auto_badge_awards": {
        "task": "writer_management.tasks.badges.run_auto_badge_awards",
        "schedule": crontab(0, 7, day_of_week="monday"),
    },
    "update_writer_levels": {
        "task": "writer_management.tasks.leveling.update_writer_levels",
        "schedule": crontab(hour=0, minute=0, day_of_week="monday"),
    },
    "update_composite_scores": {
        "task": "writer_management.tasks.scoring.update_composite_scores",
        "schedule": crontab(hour=1, minute=0, day_of_week="monday"),
    },
    "expire_old_warnings": {
        "task": "writer_management.tasks.warnings.expire_old_warnings",
        "schedule": crontab(hour=0, minute=0, day_of_week="monday"),
    },
    "preload_currency_conversion_rates": {
        "task": "writer_management.tasks.currency.preload_currency_conversion_rates",
        "schedule": crontab(hour=0, minute=0, day_of_week="sunday"),
    },
    "purge-old-expired-notifications": {
        "task": "notifications_system.tasks.expiry_tasks.purge_expired_notifications_task",
        "schedule": crontab(hour=2, minute=30),
        "args": (90,),
    },
    "archive-expired-broadcasts-every-day": {
        "task": "notifications_system.tasks.broadcast.archive_expired_broadcasts",
        "schedule": crontab(minute=0, hour="*/6"),
    },
    "delete_old_expired_broadcasts": {
        "task": "notifications_system.tasks.broadcast.delete_old_expired_broadcasts",
        "schedule": crontab(minute=30, hour=2),
    },
    "daily-notification-digest": {
        "task": "notifications_system.tasks.send_notification_digests",
        "schedule": crontab(minute=5, hour=8),
        "args": ("daily",),
    },
    "weekly-notification-digest": {
        "task": "notifications_system.tasks.send_notification_digests",
        "schedule": crontab(minute=30, hour=8, day_of_week="monday"),
        "args": ("weekly",),
    },
    "send-digest-rows-nightly": {
        "task": "notifications_system.tasks.send_daily_digests",
        "schedule": crontab(minute=20, hour=2),
    },
    "soft-expire-inapp-30d": {
        "task": "notifications_system.tasks.soft_expire_inapp_old",
        "schedule": crontab(minute=0, hour=3),
        "kwargs": {"older_than_days": 30},
    },
    "purge-expired-inapp-90d": {
        "task": "notifications_system.tasks.purge_expired_inapp",
        "schedule": crontab(minute=15, hour=3, day_of_week="sunday"),
        "kwargs": {"older_than_days": 90, "dry_run": False},
    },
    "send-progress-reminders": {
        "task": "orders.tasks.progress_reminders.send_progress_reminders",
        "schedule": crontab(minute="*/60"),  # Every hour
    },
    "send-writer-engagement-reminders": {
        "task": "orders.tasks.reminder_tasks.send_writer_engagement_reminders",
        "schedule": crontab(minute=0, hour=9),  # Daily at 9 AM
    },
    "send-message-reminders": {
        "task": "orders.tasks.reminder_tasks.send_message_reminders",
        "schedule": crontab(minute="*/60"),  # Every hour
    },
    "send-review-reminders": {
        "task": "orders.tasks.reminder_tasks.send_review_reminders",
        "schedule": crontab(minute=0, hour=10),  # Daily at 10 AM
    },
    "create-review-reminders-for-completed-orders": {
        "task": "orders.tasks.reminder_tasks.create_review_reminders_for_completed_orders",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
    },
    # Support Management Tasks
    "refresh-support-dashboards": {
        "task": "support_management.tasks.refresh_all_support_dashboards",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
    },
    "check-sla-breaches": {
        "task": "support_management.tasks.check_sla_breaches",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
    "send-sla-breach-alerts": {
        "task": "support_management.tasks.send_sla_breach_alerts",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
    },
    "auto-reassign-unresolved-tasks": {
        "task": "support_management.tasks.auto_reassign_unresolved_tasks",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
    },
    "auto-reassign-breached-slas": {
        "task": "support_management.tasks.auto_reassign_breached_slas",
        "schedule": crontab(minute="*/30"),  # Every 30 minutes
    },
    "balance-support-workload": {
        "task": "support_management.tasks.balance_support_workload",
        "schedule": crontab(minute=0),  # Every hour
    },
    "update-support-workload-trackers": {
        "task": "support_management.tasks.update_support_workload_trackers",
        "schedule": crontab(minute="*/10"),  # Every 10 minutes
    },
    "calculate-support-performance-metrics": {
        "task": "support_management.tasks.calculate_support_performance_metrics",
        "schedule": crontab(minute=0, hour=2),  # Daily at 2 AM
    },
    "orders-send-writer-acknowledgement-reminders-every-30-minutes": {
            "task": "orders.tasks.order_monitoring_tasks.send_writer_acknowledgement_reminders",
            "schedule": crontab(minute="*/30"),
    },
        "orders-send-operational-writer-reminders-every-15-minutes": {
            "task": "orders.tasks.order_monitoring_tasks.send_operational_writer_reminders",
            "schedule": crontab(minute="*/15"),
    },
    # Close windows at 23:50 every night.
    # Runs just before midnight so end_date == today is still true.
    # auto_confirm_pending=True so no events are excluded.
    "compensation-close-windows-nightly": {
        "task": "writer_compensation.tasks.check_and_close_windows",
        "schedule": crontab(hour=23, minute=50),
    },
 
    # Open new windows at 00:05 every night.
    # Runs just after midnight so the new window's start_date == today.
    # Five minute gap after close ensures close task finishes first.
    "compensation-open-windows-nightly": {
        "task": "writer_compensation.tasks.check_and_open_windows",
        "schedule": crontab(hour=0, minute=5),
    },
 
    # Alert admin at 09:00 every morning about any pending events
    # sitting in closed windows that need post-close adjustments.
    "compensation-alert-pending-events-daily": {
        "task": "writer_compensation.tasks.alert_pending_events",
        "schedule": crontab(hour=9, minute=0),
    },
        # ── Outbox reliability ─────────────────────────────────────────────────
    # Safety net: requeues any PENDING outbox rows whose Celery task was
    # never queued (e.g. broker was briefly down when enqueue() ran).
    # Without this, those notifications are silently lost forever.
    'notif-requeue-pending': {
        'task': 'notifications_system.tasks.maintenance.requeue_pending_outbox',
        'schedule': crontab(minute='*/5'),
    },

    # ── Expiry ─────────────────────────────────────────────────────────────
    # Marks sent in-app notifications as CANCELLED past their expires_at.
    'notif-expire-stale': {
        'task': 'notifications_system.tasks.maintenance.expire_stale_notifications',
        'schedule': crontab(minute='*/30'),
    },

    # ── Dead letter alerting ───────────────────────────────────────────────
    # Logs WARNING for every permanently-failed outbox entry so Sentry /
    # CloudWatch / Datadog picks them up. Extend to Slack if needed.
    'notif-alert-dead-letters': {
        'task': 'notifications_system.tasks.maintenance.alert_dead_letter_outbox',
        'schedule': crontab(minute='*/15'),
    },

    # ── Webhook event processing ───────────────────────────────────────────
    # Processes any ProviderWebhookEvent rows still PENDING after the
    # original webhook request failed (brief DB unavailability etc.).
    'notif-process-webhook-events': {
        'task': 'notifications_system.tasks.maintenance.process_pending_webhook_events',
        'schedule': crontab(minute='*/5'),
    },
    # ── Digest sending ─────────────────────────────────────────────────────
    # Sends all due unsent digests. Runs every hour.
    'notif-process-due-digests': {
        'task': 'notifications_system.tasks.digest.process_due_digests',
        'schedule': crontab(minute=0, hour='*'),
    },
    # ── Digest ─────────────────────────────────────────────────────────────
    # Deletes sent digest rows older than 30 days to keep the table lean.
    'notif-clear-stale-digests': {
        'task': 'notifications_system.tasks.maintenance.clear_stale_digests',
        'schedule': crontab(hour=3, minute=0),
    },

    # ── Unread count integrity ─────────────────────────────────────────────
    # Recalculates cached unread counts from source of truth.
    # Run daily as a drift correction. Also run manually after migrations.
    'notif-rebuild-unread-counts': {
        'task': 'notifications_system.tasks.maintenance.rebuild_unread_counts',
        'schedule': crontab(hour=4, minute=0),
    },

    # ── Outbox cleanup ─────────────────────────────────────────────────────
    # Deletes processed outbox rows older than 7 days (OUTBOX_RETAIN_DAYS).
    # This recycles dedupe keys so the same event can be re-sent legitimately
    # after the retention window (e.g. a second password reset days later).
    'notif-cleanup-processed-outbox': {
        'task': 'notifications_system.tasks.maintenance.cleanup_processed_outbox',
        'schedule': crontab(hour=3, minute=30),
    },
    "weekly-writer-rewards": {
        "task": (
            "writer_compensation.tasks.reward_tasks."
            "run_weekly_rewards_task"
        ),
        "schedule": crontab(
            minute=0,
            hour=1,
            day_of_week="monday",
        ),
    },
    "monthly-writer-rewards": {
        "task": (
            "writer_compensation.tasks.reward_tasks."
            "run_monthly_rewards_task"
        ),
        "schedule": crontab(
            minute=0,
            hour=2,
            day_of_month=1,
        ),
    },

}

# ---------- Dynamic schedule via django-celery-beat (guarded) ---------------
@app.on_after_configure.connect  # works with real Celery; is a no-op on shim
def setup_periodic_tasks(sender=None, **kwargs):
    if not CELERY_AVAILABLE:
        return  # silently skip when Celery (or beat) isn’t installed
    try:
        from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule  # type: ignore
    except Exception:
        return  # beat not installed; skip dynamically registered tasks

    periodic_tasks = []

    for t in periodic_tasks:
        PeriodicTask.objects.update_or_create(
            name=t["name"],
            defaults={"interval": t["interval"], "task": t["task"], "args": json.dumps([]), "enabled": True},
        )

    crontab_tasks = []
    for t in crontab_tasks:
        PeriodicTask.objects.update_or_create(
            name=t["name"],
            defaults={"crontab": t["crontab"], "task": t["task"], "args": json.dumps([]), "enabled": True},
        )

from celery import shared_task
import requests # type: ignore
import logging
from django.core.cache import cache
from django.conf import settings
from .utils import WebhookPayloadFormatter
from django.core.exceptions import ValidationError
from writer_management.models import WebhookSettings
from writer_management.models import WebhookPlatform
from orders.order_enums import  WebhookEvent
from models.payout import CurrencyConversionRate
from writer_management.services.conversion_service import CurrencyConversionService
from writer_management.models.profile import WriterProfile
from writer_management.services.writer_metrics_snapshot import WriterMetricsService
from writer_management.services.leveling import WriterLevelingService
from writer_management.services.scoring import CompositeScoreService
from writer_management.models.writer_warnings import WriterWarning
from writer_management.models.profile import WriterProfile
from writer_management.services.auto_badge_award_service import (
    AutoBadgeAwardService
)
from django.utils.timezone import now

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def deliver_webhook_payload(
    self, webhook_url, payload,
    platform, user_id, event_type
):
    """
    Task to deliver a webhook payload.
    Retries on failure.
    """
    headers = {
        "Content-Type": "application/json",
        "X-Platform": platform,
        "X-User-ID": str(user_id),
        "X-Event-Type": event_type,
    }

    try:
        formatted = WebhookPayloadFormatter.format(event_type, payload, platform)
        resp = requests.post(
            webhook_url, json=formatted,
            headers=headers, timeout=5
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning(f"Webhook delivery {platform} failed: {exc}")
        raise self.retry(
            exc=exc, countdown=10 * (self.request.retries + 1)
        )
    
@shared_task
def preload_currency_conversion_rates():
    """
    Preload and cache the latest conversion rates per website & currency.
    """
    websites = CurrencyConversionRate.objects.values_list(
        "website_id", flat=True
    ).distinct()

    for website_id in websites:
        entries = (
            CurrencyConversionRate.objects.filter(website_id=website_id)
            .order_by("target_currency", "-effective_date")
            .distinct("target_currency")
        )

        for entry in entries:
            key = CurrencyConversionService._cache_key(
                website_id, entry.target_currency
            )
            cache.set(key, str(entry.rate), timeout=60 * 60)  # 1 hour


@shared_task
def generate_weekly_performance_snapshots():
    """
    Generates weekly performance metrics for all writers.
    """
    for writer in WriterProfile.objects.select_related("website").all():
        try:
            WriterMetricsService.generate_snapshot(writer=writer)
        except Exception as e:
            # Optional: Log or notify
            continue


@shared_task
def update_writer_metrics_and_levels():
    for writer in WriterProfile.objects.all():
        metrics_obj = WriterMetricsService.update_metrics(writer)
        score = CompositeScoreService.compute_score(
            metrics_obj.as_dict()
        )
        metrics_obj.composite_score = score
        metrics_obj.save()

        WriterLevelingService.assign_level(metrics_obj)


@shared_task
def expire_old_warnings():
    WriterWarning.objects.filter(
        is_active=True, expires_at__lte=now()
    ).update(is_active=False)


@shared_task
def run_auto_badge_awards():
    for writer in WriterProfile.objects.filter(user__is_active=True):
        AutoBadgeAwardService.run(writer)
from __future__ import annotations

from typing import Iterable, List

from django.db import transaction

from notifications_system.models.webhook_endpoint import (
    NotificationWebhookEndpoint,
)


class WebhookEndpointService:
    """Helper functions for resolving and updating webhook endpoints."""

    @staticmethod
    def get_active_endpoints(*, user, website, event: str) -> List[NotificationWebhookEndpoint]:
        if not user or not website:
            return []

        qs = NotificationWebhookEndpoint.objects.filter(
            user=user,
            website=website,
            enabled=True,
        )
        endpoints: List[NotificationWebhookEndpoint] = []
        for endpoint in qs:
            if endpoint.should_handle(event):
                endpoints.append(endpoint)
        return endpoints

    @staticmethod
    def record_delivery(
        endpoint: NotificationWebhookEndpoint,
        *,
        success: bool,
    ) -> None:
        if success:
            endpoint.mark_success()
            return
        endpoint.mark_failure()

    @staticmethod
    def disable_endpoint(endpoint: NotificationWebhookEndpoint) -> None:
        endpoint.enabled = False
        endpoint.save(update_fields=["enabled"])

    @staticmethod
    def bulk_disable_for_urls(urls: Iterable[str]) -> None:
        if not urls:
            return
        NotificationWebhookEndpoint.objects.filter(url__in=list(urls)).update(
            enabled=False
        )


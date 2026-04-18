from __future__ import annotations

from django.db.models import QuerySet
from django.utils import timezone

from orders.models.legacy_models.order_adjustment_request import (
    OrderAdjustmentRequest,
    OrderAdjustmentStatus,
)


class OrderAdjustmentRequestSelector:
    """
    Provide read-side helpers and common query patterns for order
    adjustment requests.

    This selector keeps computed reads and reusable filtering logic out
    of models and services.
    """

    ACTIVE_STATUSES = {
        OrderAdjustmentStatus.PENDING_CLIENT_RESPONSE,
        OrderAdjustmentStatus.CLIENT_COUNTERED,
        OrderAdjustmentStatus.ACCEPTED,
        OrderAdjustmentStatus.FUNDING_PENDING,
    }

    TERMINAL_STATUSES = {
        OrderAdjustmentStatus.DECLINED,
        OrderAdjustmentStatus.CANCELLED,
        OrderAdjustmentStatus.FUNDED,
        OrderAdjustmentStatus.EXPIRED,
    }

    @staticmethod
    def get_queryset_for_website(
        *,
        website,
    ) -> QuerySet[OrderAdjustmentRequest]:
        """
        Return a tenant-scoped adjustment request queryset.

        Args:
            website:
                Tenant website.

        Returns:
            QuerySet[OrderAdjustmentRequest]:
                Website-scoped queryset.
        """
        return OrderAdjustmentRequest.objects.filter(website=website)

    @classmethod
    def get_queryset_for_order(
        cls,
        *,
        website,
        order,
    ) -> QuerySet[OrderAdjustmentRequest]:
        """
        Return adjustment requests for a specific order within a tenant.

        Args:
            website:
                Tenant website.
            order:
                Order whose adjustment requests should be returned.

        Returns:
            QuerySet[OrderAdjustmentRequest]:
                Order-scoped adjustment request queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            order=order
        )

    @classmethod
    def get_active_queryset_for_website(
        cls,
        *,
        website,
    ) -> QuerySet[OrderAdjustmentRequest]:
        """
        Return active adjustment requests for a tenant.

        Active requests are not yet fully resolved and may still require
        client action, staff review, or funding.

        Args:
            website:
                Tenant website.

        Returns:
            QuerySet[OrderAdjustmentRequest]:
                Active adjustment request queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            status__in=cls.ACTIVE_STATUSES
        )

    @classmethod
    def get_terminal_queryset_for_website(
        cls,
        *,
        website,
    ) -> QuerySet[OrderAdjustmentRequest]:
        """
        Return terminal adjustment requests for a tenant.

        Terminal requests are fully resolved and should not continue
        through negotiation or funding workflows.

        Args:
            website:
                Tenant website.

        Returns:
            QuerySet[OrderAdjustmentRequest]:
                Terminal adjustment request queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            status__in=cls.TERMINAL_STATUSES
        )

    @classmethod
    def get_pending_client_response_queryset(
        cls,
        *,
        website,
    ) -> QuerySet[OrderAdjustmentRequest]:
        """
        Return requests awaiting direct client response.

        Args:
            website:
                Tenant website.

        Returns:
            QuerySet[OrderAdjustmentRequest]:
                Requests waiting for client acceptance, decline, or
                counter.
        """
        return cls.get_queryset_for_website(website=website).filter(
            status=OrderAdjustmentStatus.PENDING_CLIENT_RESPONSE
        )

    @classmethod
    def get_countered_queryset(
        cls,
        *,
        website,
    ) -> QuerySet[OrderAdjustmentRequest]:
        """
        Return requests that were countered by the client.

        Args:
            website:
                Tenant website.

        Returns:
            QuerySet[OrderAdjustmentRequest]:
                Countered adjustment request queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            status=OrderAdjustmentStatus.CLIENT_COUNTERED
        )

    @classmethod
    def get_accepted_queryset(
        cls,
        *,
        website,
    ) -> QuerySet[OrderAdjustmentRequest]:
        """
        Return accepted requests that have agreed commercial terms.

        Args:
            website:
                Tenant website.

        Returns:
            QuerySet[OrderAdjustmentRequest]:
                Accepted adjustment request queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            status=OrderAdjustmentStatus.ACCEPTED
        )

    @classmethod
    def get_funding_pending_queryset(
        cls,
        *,
        website,
    ) -> QuerySet[OrderAdjustmentRequest]:
        """
        Return requests waiting for settlement after billing handoff.

        Args:
            website:
                Tenant website.

        Returns:
            QuerySet[OrderAdjustmentRequest]:
                Funding-pending adjustment request queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            status=OrderAdjustmentStatus.FUNDING_PENDING
        )

    @classmethod
    def get_funded_queryset(
        cls,
        *,
        website,
    ) -> QuerySet[OrderAdjustmentRequest]:
        """
        Return fully funded adjustment requests.

        Args:
            website:
                Tenant website.

        Returns:
            QuerySet[OrderAdjustmentRequest]:
                Funded adjustment request queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            status=OrderAdjustmentStatus.FUNDED
        )

    @classmethod
    def get_expired_queryset(
        cls,
        *,
        website,
    ) -> QuerySet[OrderAdjustmentRequest]:
        """
        Return explicitly expired adjustment requests.

        Args:
            website:
                Tenant website.

        Returns:
            QuerySet[OrderAdjustmentRequest]:
                Expired adjustment request queryset.
        """
        return cls.get_queryset_for_website(website=website).filter(
            status=OrderAdjustmentStatus.EXPIRED
        )

    @staticmethod
    def is_expired(
        *,
        adjustment_request: OrderAdjustmentRequest,
    ) -> bool:
        """
        Determine whether an adjustment request is expired.

        Args:
            adjustment_request:
                Adjustment request to inspect.

        Returns:
            bool:
                True when the request is explicitly expired or when its
                expiry timestamp has passed.
        """
        if adjustment_request.status == OrderAdjustmentStatus.EXPIRED:
            return True

        if adjustment_request.expires_at is None:
            return False

        return timezone.now() > adjustment_request.expires_at

    @staticmethod
    def is_active(
        *,
        adjustment_request: OrderAdjustmentRequest,
    ) -> bool:
        """
        Determine whether an adjustment request is active.

        Args:
            adjustment_request:
                Adjustment request to inspect.

        Returns:
            bool:
                True when the request is still in a non-terminal state.
        """
        return (
            adjustment_request.status
            in OrderAdjustmentRequestSelector.ACTIVE_STATUSES
        )

    @staticmethod
    def requires_client_response(
        *,
        adjustment_request: OrderAdjustmentRequest,
    ) -> bool:
        """
        Determine whether an adjustment request still requires direct
        client action.

        Args:
            adjustment_request:
                Adjustment request to inspect.

        Returns:
            bool:
                True when the request is waiting for client acceptance,
                decline, or counter.
        """
        return adjustment_request.status in {
            OrderAdjustmentStatus.PENDING_CLIENT_RESPONSE,
            OrderAdjustmentStatus.CLIENT_COUNTERED,
        }

    @staticmethod
    def can_generate_billing_artifact(
        *,
        adjustment_request: OrderAdjustmentRequest,
    ) -> bool:
        """
        Determine whether a billing payment request or invoice can be
        created from the adjustment request.

        Args:
            adjustment_request:
                Adjustment request to inspect.

        Returns:
            bool:
                True when the request has accepted commercial terms and
                has not yet moved into funding.
        """
        return adjustment_request.status == OrderAdjustmentStatus.ACCEPTED

    @staticmethod
    def has_billing_artifact(
        *,
        adjustment_request: OrderAdjustmentRequest,
    ) -> bool:
        """
        Determine whether a billing artifact is already linked.

        Args:
            adjustment_request:
                Adjustment request to inspect.

        Returns:
            bool:
                True when either a billing payment request or invoice
                is linked.
        """
        return (
            adjustment_request.billing_payment_request is not None
            or adjustment_request.invoice is not None
        )
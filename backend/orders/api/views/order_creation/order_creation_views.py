from __future__ import annotations

from typing import Any, cast

from django.db import transaction
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from django.shortcuts import get_object_or_404  # noqa: F401 kept for possible future use

from orders.api.permissions.order_creation_permissions import (
    CanAccessOrderCreation,
)
from orders.api.serializers.order_creation.create_order_serializer import (
    CreateOrderSerializer,
)
from orders.services.order_creation_service import (
    OrderCreationService,
)
from orders.services.order_payment_application_service import (
    OrderPaymentApplicationService,
)
from orders.api.permissions import ClientOrderCreatePermission
from core.utils.request_context import get_request_website
from accounts.services.permission_service import AccountPermissionService
from orders.models.orders.order import Order
from orders.models.orders.enums import OrderPaymentStatus

class CreateOrderView(GenericAPIView):
    """
    Create a new priced order and optionally start checkout.

    Flow:
        1. Validate transport and business rules through serializer.
        2. Create the order aggregate through OrderCreationService.
        3. Optionally start checkout for unpaid orders.
        4. Return order summary and payment context.

    Notes:
        1. This view stays thin and delegates business logic to services.
        2. Pricing truth comes from order_pricing_core via the selected
           PricingSnapshot resolved by the serializer.
    """

    serializer_class = CreateOrderSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanAccessOrderCreation,
    ]

    @transaction.atomic
    def post(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """
        Create a new order from validated payload.

        Args:
            request:
                Incoming DRF request.

        Returns:
            Response:
                Created order summary and optional checkout payload.
        """
        serializer = self.get_serializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        validated_data = cast(dict[str, Any], serializer.validated_data)

        if "website_id" in validated_data:
            raise PermissionDenied(
                "Tenant cannot be overridden."
            )

        pricing_snapshot = validated_data["pricing_snapshot"]
        pricing_snapshots = validated_data.get(
            "pricing_snapshots",
            [pricing_snapshot],
        )

        user = cast(Any, request.user)

        website = get_request_website(request)

        client = self._resolve_client_for_creation(
            request=request,
            acting_user=user,
            website=website,
        )

        order = OrderCreationService.create_order(
            website=website,
            client=client,
            order_payload=serializer.to_order_payload(),
            pricing_result=(
                OrderCreationService.build_pricing_result_from_snapshots(
                    pricing_snapshots=pricing_snapshots,
                )
            ),
            source_pricing_snapshot=pricing_snapshot,
            triggered_by=user,
        )

        checkout_started = False
        payment_intent_payload: dict[str, Any] | None = None

        entered_code = (validated_data.get("entered_code") or "").strip() or None
        has_prior_paid_purchase = self._has_prior_paid_purchase(
            client=client,
            website=website,
        )

        provider = self._get_checkout_provider(request=request)
        if provider and not order.is_fully_paid:
            payment_intent = (
                OrderPaymentApplicationService.start_checkout(
                    order=order,
                    provider=provider,
                    payment_method_code=self._get_payment_method_code(
                        request=request
                    ),
                    triggered_by=user,
                    entered_code=entered_code,
                    has_prior_paid_purchase=has_prior_paid_purchase,
                    metadata={
                        "source": "order_creation_api",
                    },
                )
            )
            checkout_started = True
            payment_intent_payload = self._serialize_payment_intent(
                payment_intent=payment_intent
            )

        return Response(
            {
                "message": "Order created successfully.",
                "order": self._serialize_order(order=order),
                "checkout_started": checkout_started,
                "payment_intent": payment_intent_payload,
            },
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _resolve_client_for_creation(
        *,
        request: Request,
        acting_user: Any,
        website: Any,
    ) -> Any:
        """
        Resolve which client should own the new order.

        Rules:
            1. Default to the authenticated user.
            2. Staff may supply client_id (integer PK) OR client_email.
               Either triggers the on-behalf permission check.
               client_id takes precedence over client_email when both are
               provided.
        """
        request_data = cast(dict[str, Any], request.data)
        client_id = request_data.get("client_id")
        client_email = (request_data.get("client_email") or "").strip().lower() or None

        # No override — act as the authenticated user
        if not client_id and not client_email:
            return acting_user

        # Permission check — both lookup paths require the same permission
        can_create_on_behalf = AccountPermissionService.user_has_permission(
            user=acting_user,
            permission_code="orders.create_on_behalf",
            website=website,
        )
        if not can_create_on_behalf:
            raise PermissionDenied(
                "You are not allowed to create orders for another client."
            )

        user_model = CreateOrderSerializer._get_user_model()

        if client_id:
            # Filter by website immediately to prevent cross-tenant resolution.
            # A missing or null website_id on the user record is treated as a
            # mismatch — legitimate clients should always be website-scoped.
            client = user_model.objects.filter(pk=client_id, website=website).first()
            if client is None:
                raise PermissionDenied(
                    "Client not found on this site."
                )
        else:
            # Lookup by email — scoped to this website for safety
            client = user_model.objects.filter(
                email__iexact=client_email,
                website=website,
            ).first()
            if client is None:
                raise PermissionDenied(
                    f"No client found with email '{client_email}' on this site."
                )

        return client

    @staticmethod
    def _has_prior_paid_purchase(*, client: Any, website: Any) -> bool:
        """
        Return True if the client has at least one fully paid order on this site.
        """
        return Order.objects.filter(
            client=client,
            website=website,
            payment_status=OrderPaymentStatus.FULLY_PAID,
        ).exists()

    @staticmethod
    def _get_checkout_provider(*, request: Request) -> str:
        """
        Extract checkout provider from request payload.

        Args:
            request:
                Incoming DRF request.

        Returns:
            str:
                Selected provider code, or empty string when omitted.
        """
        request_data = cast(dict[str, Any], request.data)
        value = request_data.get("payment_provider", "")
        return str(value).strip()

    @staticmethod
    def _get_payment_method_code(*, request: Request) -> str:
        """
        Extract payment method code from request payload.

        Args:
            request:
                Incoming DRF request.

        Returns:
            str:
                Selected payment method code, or empty string.
        """
        request_data = cast(dict[str, Any], request.data)
        value = request_data.get("payment_method_code", "")
        return str(value).strip()

    @staticmethod
    def _serialize_order(*, order) -> dict[str, Any]:
        """
        Serialize minimal order creation response payload.

        Args:
            order:
                Newly created order.

        Returns:
            dict[str, Any]:
                Serialized order summary.
        """
        return {
            "id": order.pk,
            "public_order_number": order.public_order_number,
            "reference": order.reference,
            "topic": order.topic,
            "status": order.status,
            "payment_status": order.payment_status,
            "total_price": str(order.total_price),
            "amount_paid": str(order.amount_paid),
            "remaining_balance": str(order.remaining_balance),
            "currency": order.currency,
            "service_family": order.service_family,
            "service_code": order.service_code,
            "is_composite": order.is_composite,
            "client_deadline": order.client_deadline,
            "writer_deadline": order.writer_deadline,
            "pricing_snapshot_id": getattr(
                order.pricing_snapshot,
                "pk",
                None,
            ),
        }

    @staticmethod
    def _serialize_payment_intent(
        *,
        payment_intent: Any,
    ) -> dict[str, Any]:
        """
        Serialize returned payment intent payload.

        Args:
            payment_intent:
                Payment intent returned by payments_processor.

        Returns:
            dict[str, Any]:
                Minimal serialized checkout context.
        """
        return {
            "id": getattr(payment_intent, "pk", None),
            "reference": getattr(payment_intent, "reference", ""),
            "status": getattr(payment_intent, "status", ""),
            "amount": str(getattr(payment_intent, "amount", "")),
            "currency": getattr(payment_intent, "currency", ""),
            "provider": getattr(payment_intent, "provider", ""),
            "client_secret": getattr(
                payment_intent,
                "client_secret",
                "",
            ),
            "checkout_url": getattr(
                payment_intent,
                "checkout_url",
                "",
            ),
        }

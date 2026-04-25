from __future__ import annotations

from typing import Any, cast

from django.db import transaction
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.permissions.order_creation_permissions import (
    CanCreateOrder,
    CanCreateOrderWithUnpaidAccess,
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
        CanCreateOrder,
        CanCreateOrderWithUnpaidAccess,
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
        pricing_snapshot = validated_data["pricing_snapshot"]

        user = cast(Any, request.user)
        client = self._resolve_client_for_creation(
            request=request,
            acting_user=user,
        )

        order = OrderCreationService.create_order(
            website=user.website,
            client=client,
            order_payload=serializer.to_order_payload(),
            pricing_result=pricing_snapshot,
            source_pricing_snapshot=pricing_snapshot,
            triggered_by=user,
        )

        checkout_started = False
        payment_intent_payload: dict[str, Any] | None = None

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
    ) -> Any:
        """
        Resolve which client should own the new order.

        Rules:
            1. Default to the authenticated user.
            2. Allow staff to supply client_id for assisted creation.

        Args:
            request:
                Incoming DRF request.
            acting_user:
                Authenticated user performing the action.

        Returns:
            Any:
                Client user instance.
        """
        request_data = cast(dict[str, Any], request.data)
        client_id = request_data.get("client_id")
        if not client_id or not getattr(acting_user, "is_staff", False):
            return acting_user

        user_model = CreateOrderSerializer._get_user_model()
        client = user_model.objects.get(pk=client_id)

        client_website_id = getattr(client, "website_id", None)
        acting_website_id = getattr(acting_user, "website_id", None)
        if (
            client_website_id is not None
            and acting_website_id is not None
            and client_website_id != acting_website_id
        ):
            raise PermissionDenied(
                "Selected client must belong to the same tenant."
            )

        return client

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
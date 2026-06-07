from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from rest_framework import status
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from special_orders.api.permissions import (
    CanPaySpecialOrder,
)
from special_orders.api.serializers import (
    SpecialOrderPaymentApplicationSerializer,
)
from special_orders.selectors import (
    SpecialOrderFundingSelector,
    SpecialOrderSelector,
)
from special_orders.services.new_services.special_order_payment_orchestration_service import (
    SpecialOrderPaymentOrchestrationService,
)
from special_orders.integrations.wallet_bridge import SpecialOrderWalletBridge


class ManualVerifiedSpecialOrderPaymentSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    transaction_reference = serializers.CharField(max_length=255)
    verification_note = serializers.CharField(max_length=1000)
    payment_method = serializers.CharField(
        max_length=80,
        required=False,
        allow_blank=True,
    )

    def validate_transaction_reference(self, value: str) -> str:
        value = value.strip()
        if len(value) < 4:
            raise serializers.ValidationError(
                "Transaction reference must be at least 4 characters."
            )
        return value

    def validate_verification_note(self, value: str) -> str:
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError(
                "Verification note must be at least 10 characters."
            )
        return value


def _can_manually_verify_payment(user: Any) -> bool:
    return bool(
        getattr(user, "is_superuser", False)
        or getattr(user, "role", None) in {"admin", "superadmin"}
    )


class ApplyExternalPaymentView(APIView):
    permission_classes = [IsAuthenticated, CanPaySpecialOrder]

    def post(self, request, special_order_id: int):
        data = cast(dict[str, Any], request.data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        application = (
            SpecialOrderPaymentOrchestrationService.apply_external_payment(
                special_order=special_order,
                amount=Decimal(str(data["amount"])),
                idempotency_key=str(data["idempotency_key"]),
                payment_intent_reference=str(
                    data["payment_intent_reference"]
                ),
                payment_transaction_reference=str(
                    data["payment_transaction_reference"]
                ),
                ledger_entry_reference=str(
                    data.get("ledger_entry_reference", "")
                ),
                applied_by=request.user,
                metadata=data.get("metadata", {}),
            )
        )

        serializer = SpecialOrderPaymentApplicationSerializer(application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ApplyWalletPaymentView(APIView):
    permission_classes = [IsAuthenticated, CanPaySpecialOrder]

    def post(self, request, special_order_id: int):
        data = cast(dict[str, Any], request.data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        milestone = None
        milestone_id = data.get("milestone_id")

        if milestone_id is not None:
            milestone = SpecialOrderFundingSelector.get_milestone(
                website=request.user.website,
                milestone_id=int(milestone_id),
            )

        application = SpecialOrderWalletBridge.pay_from_wallet(
            special_order=special_order,
            amount=data["amount"],
            milestone=milestone,
            paid_by=request.user,
            metadata=cast(dict[str, Any], data.get("metadata", {})),
        )

        response_serializer = SpecialOrderPaymentApplicationSerializer(
            application,
        )
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )


class ApplySplitPaymentView(APIView):
    permission_classes = [IsAuthenticated, CanPaySpecialOrder]

    def post(self, request, special_order_id: int):
        data = cast(dict[str, Any], request.data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        applications = (
            SpecialOrderPaymentOrchestrationService.apply_split_payment(
                special_order=special_order,
                wallet_amount=Decimal(str(data.get("wallet_amount", "0"))),
                external_amount=Decimal(
                    str(data.get("external_amount", "0"))
                ),
                wallet_idempotency_key=str(
                    data["wallet_idempotency_key"]
                ),
                external_idempotency_key=str(
                    data["external_idempotency_key"]
                ),
                wallet_transaction_reference=str(
                    data["wallet_transaction_reference"]
                ),
                payment_intent_reference=str(
                    data["payment_intent_reference"]
                ),
                payment_transaction_reference=str(
                    data["payment_transaction_reference"]
                ),
                wallet_ledger_entry_reference=str(
                    data.get("wallet_ledger_entry_reference", "")
                ),
                external_ledger_entry_reference=str(
                    data.get("external_ledger_entry_reference", "")
                ),
                applied_by=request.user,
                metadata=data.get("metadata", {}),
            )
        )

        serializer = SpecialOrderPaymentApplicationSerializer(
            applications,
            many=True,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ManualVerifiedSpecialOrderPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, special_order_id: int):
        if not _can_manually_verify_payment(request.user):
            return Response(
                {"detail": "Only admin or superadmin can verify payments."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ManualVerifiedSpecialOrderPaymentSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        data = cast(dict[str, Any], serializer.validated_data)

        if (
            request.user.is_superuser
            or getattr(request.user, "role", None) == "superadmin"
        ):
            from special_orders.models import SpecialOrder

            try:
                special_order = SpecialOrder.objects.select_related(
                    "website",
                    "client",
                    "writer",
                ).get(pk=special_order_id)
            except SpecialOrder.DoesNotExist:
                raise NotFound("Special order not found.")
        else:
            special_order = SpecialOrderSelector.get_by_id(
                website=request.user.website,
                special_order_id=special_order_id,
            )

        transaction_reference = str(data["transaction_reference"])
        from special_orders.models.funding import SpecialOrderFundingPlan
        from rest_framework.exceptions import ValidationError as DRFValidationError
        try:
            application = (
                SpecialOrderPaymentOrchestrationService.apply_admin_adjustment(
                    special_order=special_order,
                    amount=cast(Decimal, data["amount"]),
                    idempotency_key=(
                        f"manual-special-payment:"
                        f"{special_order.website_id}:{special_order.pk}:"
                        f"{transaction_reference}"
                    ),
                    ledger_entry_reference=transaction_reference,
                    applied_by=request.user,
                    reason=str(data["verification_note"]),
                    metadata={
                        "source": "manual_staff_verification",
                        "transaction_reference": transaction_reference,
                        "payment_method": str(data.get("payment_method", "")),
                        "verified_by_user_id": request.user.id,
                    },
                )
            )
        except SpecialOrderFundingPlan.DoesNotExist:
            raise DRFValidationError(
                "This special order has no funding plan. A funding plan must be "
                "created (via the quote acceptance flow) before payments can be applied."
            )

        response_serializer = SpecialOrderPaymentApplicationSerializer(
            application,
        )
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

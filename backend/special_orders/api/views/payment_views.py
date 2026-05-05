from __future__ import annotations

from decimal import Decimal
from typing import Any, cast

from rest_framework import status
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
    

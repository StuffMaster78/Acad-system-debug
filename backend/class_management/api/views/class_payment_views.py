from __future__ import annotations

from decimal import Decimal
from typing import cast, Any

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from class_management.api.permissions import ClassPaymentPermission
from class_management.api.serializers import (
    ClassInstallmentPlanSerializer,
    ClassInstallmentSerializer,
    ClassInvoiceLinkSerializer,
    ClassPaymentAllocationSerializer,
    CreateEqualInstallmentPlanSerializer,
    PrepareClassPaymentSerializer,
)
from class_management.models import ClassInstallment
from class_management.selectors import (
    ClassOrderSelector,
    ClassPaymentSelector,
)
from class_management.services.class_installment_service import (
    ClassInstallmentService,
)
from class_management.services.class_payment_service import (
    ClassPaymentService,
)
from class_management.api.views.class_base_views import ClassTenantViewMixin


class ClassPaymentViewSet(ClassTenantViewMixin, viewsets.GenericViewSet):
    """
    API endpoints for class invoices, installments, and payment allocation.
    """

    permission_classes = [IsAuthenticated, ClassPaymentPermission]

    def get_class_order(self):
        class_order = ClassOrderSelector.get_for_website(
            website=self.get_website(),
            class_order_id=self.kwargs["class_order_pk"],
        )
        self.check_object_permissions(self.request, class_order)
        return class_order

    @action(detail=False, methods=["get"])
    def invoices(self, request, *args, **kwargs):
        class_order = self.get_class_order()
        invoice_links = ClassPaymentSelector.invoice_links_for_order(
            class_order=class_order,
        )
        return Response(
            ClassInvoiceLinkSerializer(invoice_links, many=True).data
        )

    @action(detail=False, methods=["get"])
    def allocations(self, request, *args, **kwargs):
        class_order = self.get_class_order()
        allocations = ClassPaymentSelector.allocations_for_order(
            class_order=class_order,
        )
        return Response(
            ClassPaymentAllocationSerializer(allocations, many=True).data
        )

    @action(detail=False, methods=["get"])
    def installments(self, request, *args, **kwargs):
        class_order = self.get_class_order()
        installments = ClassPaymentSelector.installments_for_order(
            class_order=class_order,
        )
        return Response(
            ClassInstallmentSerializer(installments, many=True).data
        )

    @action(detail=False, methods=["post"])
    def create_equal_installments(self, request, *args, **kwargs):
        class_order = self.get_class_order()

        serializer = CreateEqualInstallmentPlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        plan = ClassInstallmentService.create_equal_plan(
            class_order=class_order,
            installment_count=data["installment_count"],
            due_dates=data["due_dates"],
            created_by=request.user,
            deposit_amount=data.get("deposit_amount", Decimal("0.00")),
            allow_work_before_full_payment=data.get(
                "allow_work_before_full_payment",
                True,
            ),
            pause_work_when_overdue=data.get(
                "pause_work_when_overdue",
                True,
            ),
            notes=data.get("notes", ""),
        )

        return Response(
            ClassInstallmentPlanSerializer(plan).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"])
    def prepare_payment(self, request, *args, **kwargs):
        class_order = self.get_class_order()

        serializer = PrepareClassPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = cast(dict, serializer.validated_data)

        installment = None
        installment_id = data.get("installment_id")

        if installment_id:
            installment = ClassInstallment.objects.get(
                pk=installment_id,
                plan__class_order=class_order,
            )

        result = ClassPaymentService.prepare_payment(
            class_order=class_order,
            amount=data["amount"],
            payer=request.user,
            use_wallet=data.get("use_wallet", False),
            installment=installment,
            metadata={
                "source": "class_management_api",
                "requested_by_user_id": request.user.id,
            },
        )

        return Response(
            {
                "class_order_id": result.class_order.pk,
                "amount_due": str(result.amount_due),
                "wallet_amount": str(result.wallet_amount),
                "external_amount": str(result.external_amount),
                "source_type": result.source_type,
                "checkout_url": result.checkout_url,
                "payment_intent_id": result.payment_intent_id,
                "allocation_id": result.allocation_id,
            }
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="installments/(?P<installment_id>[^/.]+)/waive",
    )
    def waive_installment(self, request, installment_id=None, *args, **kwargs):
        class_order = self.get_class_order()

        installment = ClassInstallment.objects.get(
            pk=installment_id,
            plan__class_order=class_order,
        )

        reason = request.data.get("reason", "")

        updated = ClassInstallmentService.waive_installment(
            installment=installment,
            waived_by=request.user,
            reason=reason,
        )

        return Response(ClassInstallmentSerializer(updated).data)

    @action(detail=False, methods=["post"])
    def resume_work(self, request, *args, **kwargs):
        class_order = self.get_class_order()

        updated = ClassInstallmentService.resume_work(
            class_order=class_order,
            resumed_by=request.user,
            reason=request.data.get("reason", ""),
        )

        return Response({"resumed": True, "class_order_id": updated.pk})
from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone


from orders.models.adjustments.order_compensation_adjustment import(
    OrderCompensationAdjustment,
)

from orders.models.orders.order_item import OrderItem
from orders.models.orders.constants import (
    ORDER_ADJUSTMENT_KIND_EXTRA_SERVICE,
    ORDER_ADJUSTMENT_KIND_SCOPE_INCREMENT,
    ORDER_COMPENSATION_ADJUSTMENT_STATUS_PENDING,
    ORDER_ITEM_KIND_EXTRA_SERVICE,
    ORDER_ITEM_KIND_SCOPE_UNIT,
)
from orders.models.orders.order import Order
from orders.models.orders.order_pricing_snapshot import OrderPricingSnapshot
from orders.services.order_pricing_snapshot_service import (
    OrderPricingSnapshotService,
)
from orders.models.orders.constants import (
    ORDER_EXTRA_SERVICE_PROGRESSIVE_DELIVERY,
)
from orders.services.progressive_delivery_service import (
    ProgressiveDeliveryService,
)

class AdjustmentScopeApplicationService:
    """
    Apply funded adjustment outcomes to live order commercial state.
    This is used for both client and writer counters,
    but currently only client counters are fundable
    and thus applicable immediately.
    """

    TIMELINE_EVENT_COUNTER_APPLIED = "adjustment_counter_applied"


    @classmethod
    @transaction.atomic
    def apply_funded_adjustment(
        cls,
        *,
        adjustment_request,
        triggered_by: Optional[Any] = None,
    ) -> Order:
        """
        Dispatch funded adjustment by adjustment kind.
            - For scope increments, apply the countered scope
            and price to the order immediately.   
            - For extra service adjustments, the countered scope and price
            will be applied when the order item is fulfilled,
            similar to non-countered extra service adjustments.

        Args:
            adjustment_request:
                Target funded adjustment request.
            triggered_by:
                Optional actor.

        Returns:
            Order:
                Updated order.
        """
        if adjustment_request.applied_at is not None:
            return adjustment_request.order
        
        if adjustment_request.adjustment_kind == ORDER_ADJUSTMENT_KIND_SCOPE_INCREMENT:
            return cls.apply_funded_scope_increment(
                adjustment_request=adjustment_request,
                triggered_by=triggered_by,
            )
        
        if adjustment_request.adjustment_kind == ORDER_ADJUSTMENT_KIND_EXTRA_SERVICE:
            return cls.apply_funded_extra_service(
                adjustment_request=adjustment_request,
                triggered_by=triggered_by,
            )
        
        raise ValidationError(
            f"Unsupported adjustment kind: {adjustment_request.adjustment_kind}"
        )
    

    @classmethod
    @transaction.atomic
    def apply_funded_scope_increment(
        cls,
        *,
        adjustment_request,
        triggered_by: Optional[Any] = None,
    ) -> Order:
        """
        Apply a funded scope increment immediately to the order.
        Applied funded page, slide, diagram, or design concept increment.

        Args:
            adjustment_request:
                Target funded scope increment adjustment request.
            triggered_by:
                Optional actor.

        Returns:
            Order:
                Updated order.
        """
        order = adjustment_request.order
        final_quantity = (
            adjustment_request.countered_quantity
            or adjustment_request.requested_quantity
        )
        quantity_delta = final_quantity - adjustment_request.requested_quantity 

        if quantity_delta <= 0:
            raise ValidationError(
                "Countered quantity must be greater than requested quantity for scope increments."
            )
        applied_amount = cls._final_amount(adjustment_request)
        writer_amount = cls._final_writer_amount(adjustment_request)
        final_snapshot = cls._final_pricing_snapshot(adjustment_request)

        order.base_quantity = final_quantity
        order.total_price = cls._to_decimal(order.total_price) + cls._to_decimal(applied_amount)

        if hasattr(order, "writer_compensation"):
            order.writer_compensation = cls._to_decimal(
                getattr(order, "writer_compensation", Decimal("0.00"))
            ) + cls._to_decimal(writer_amount)

        if final_snapshot is not None and hasattr(order, "pricing_snapshot"):
            order.pricing_snapshot = final_snapshot


        order.save()

        OrderItem.objects.create(
            website=order.website,
            order=order,
            pricing_snapshot=final_snapshot,
            service_family=getattr(order, "service_family", ""),
            service_code=getattr(order, "service_code", ""),
            unit_type=adjustment_request.unit_type,
            item_kind=ORDER_ITEM_KIND_SCOPE_UNIT,
            topic=f"Scope increment accepted via client counter: {quantity_delta} {adjustment_request.unit_type}",
            quantity=quantity_delta,
            subtotal=applied_amount,
            discount_amount=Decimal("0.00"),
            total_price=applied_amount,
            metadata={
                "adjustment_request_id": adjustment_request.pk,
                "source": "client_counter_funded",
                "unit_type": adjustment_request.unit_type,
            },
            sort_order=999,
        )

        cls._record_snapshot(
            order=order,
            adjustment_request=adjustment_request,
            triggered_by=triggered_by,
        )

        cls._create_compensation_adjustment(
            adjustment_request=adjustment_request,
            quantity_delta=Decimal(str(quantity_delta)),
            amount_delta=writer_amount,
        )

        cls._mark_applied(
            adjustment_request=adjustment_request,
        )

        return order
    


    @classmethod
    @transaction.atomic
    def apply_funded_extra_service(
        cls,
        *,
        adjustment_request,
        triggered_by: Optional[Any] = None,
    ) -> Order:
        """
        Apply a funded extra service adjustment immediately to the order.
        The countered scope and price will be applied when the order item is fulfilled,
        similar to non-countered extra service adjustments.

        Args:
            adjustment_request:
                Target funded extra service adjustment request.
            triggered_by:
                Optional actor.
        Returns:
            Order:
                Updated order.
        """
        order = adjustment_request.order
        applied_amount = cls._final_amount(adjustment_request)
        writer_amount = cls._final_writer_amount(adjustment_request)
        final_snapshot = cls._final_pricing_snapshot(adjustment_request)

        order.total_price = cls._to_decimal(order.total_price) + cls._to_decimal(applied_amount)

        if hasattr(order, "writer_compensation"):
            order.writer_compensation = cls._to_decimal(
                getattr(order, "writer_compensation", Decimal("0.00"))
            ) + cls._to_decimal(writer_amount)

        if final_snapshot is not None and hasattr(order, "pricing_snapshot"):
            order.pricing_snapshot = final_snapshot

        order.save()

        OrderItem.objects.create(
            website=order.website,
            order=order,
            pricing_snapshot=adjustment_request.counter_pricing_snapshot,
            service_family=getattr(order, "service_family", ""),
            service_code=getattr(order, "service_code", ""),
            item_kind=ORDER_ITEM_KIND_EXTRA_SERVICE,
            topic=f"Extra service accepted via client counter: {adjustment_request.extra_service_description}",
            quantity=adjustment_request.countered_quantity or 1,
            subtotal=adjustment_request.counter_total_amount,
            discount_amount=Decimal("0.00"),
            total_price=adjustment_request.counter_total_amount,
            metadata={
                "adjustment_request_id": adjustment_request.pk,
                "source": "client_counter_funded",
                "extra_service_code": adjustment_request.extra_service_code,
                "extra_service_description": adjustment_request.extra_service_description,
            },
            sort_order=999,
        )

        if (
            adjustment_request.extra_service_code
            == ORDER_EXTRA_SERVICE_PROGRESSIVE_DELIVERY
        ):
            ProgressiveDeliveryService.create_plan_from_adjustment(
                adjustment_request=adjustment_request,
                created_by=triggered_by,
            )

        cls._record_snapshot(
            order=order,
            adjustment_request=adjustment_request,
            triggered_by=triggered_by,
        )

        cls._create_compensation_adjustment(
            adjustment_request=adjustment_request,
            quantity_delta=Decimal("1.00"),
            amount_delta=writer_amount,
        )

        cls._mark_applied(
            adjustment_request=adjustment_request,
        )

        return order
    

    @classmethod
    def _record_snapshot(
        cls,
        *,
        order,
        adjustment_request,
        triggered_by,
    ) -> OrderPricingSnapshot:
        """
        Record a new order-owned pricing snapshot after counter application.
        """
        return OrderPricingSnapshotService.record_current_snapshot(
            order=order,
            source_pricing_snapshot=cls._final_pricing_snapshot(
                adjustment_request
            ),
            subtotal_amount=order.total_price,
            discount_amount=Decimal("0.00"),
            total_amount=order.total_price,
            writer_compensation_amount=getattr(
                order,
                "writer_compensation",
                Decimal("0.00"),
            ),
            pricing_payload=cls._final_payload(adjustment_request),
            created_by=triggered_by,
            currency=getattr(order, "currency", "USD"),
            pricing_policy_version="adjustment_applied",
        )
    

    @classmethod
    def _create_compensation_adjustment(
        cls,
        *,
        adjustment_request,
        quantity_delta: Decimal,
        amount_delta: Decimal,
    ) -> Optional[OrderCompensationAdjustment]:
        """
        Create a compensation adjustment for the writer if the
        counter offer includes a writer compensation change.
        """
        if amount_delta == 0:
            return None

        return OrderCompensationAdjustment.objects.create(
            website=adjustment_request.order.website,
            order=adjustment_request.order,
            adjustment_request=adjustment_request,
            writer=cls._resolve_current_writer(adjustment_request.order),
            compensation_type=cls._compensation_type(adjustment_request),
            status=ORDER_COMPENSATION_ADJUSTMENT_STATUS_PENDING,
            unit_type=adjustment_request.unit_type,
            quantity_delta=quantity_delta,
            amount_delta=amount_delta,
            metadata={
                "adjustment_kind": adjustment_request.adjustment_kind,
                "adjustment_id": adjustment_request.pk,
                "adjustment_type": adjustment_request.adjustment_type,
            },
        )
    

    @staticmethod
    def _mark_applied(
        *,
        adjustment_request,
    ) -> None:
        """
        Mark the adjustment request as applied.
        """
        # adjustment_request.status = "counter_funded_final"
        adjustment_request.is_counter_final = bool(
            adjustment_request.countered_quantity
            or adjustment_request.counter_total_amount
        )
        adjustment_request.applied_at = timezone.now()
        adjustment_request.save(
            update_fields=[
                "status",
                "is_counter_final",
                "applied_at",
                "updated_at",
            ]
        )

    @staticmethod
    def _resolve_current_writer(
        order: Order
    ) -> Optional[Any]:
        """
        Resolve the current writer for the order, if applicable.
        This is used to associate compensation adjustments with the correct writer.
        The resolution logic first checks for an active assignment
        and falls back to the preferred writer if no active assignment is found.
        """
        assignments = getattr(order, "assignments", None)
        if assignments is not None:
            current_assignment = assignments.filter(is_active=True).select_related("writer").first()
            if current_assignment is not None:
                return current_assignment.writer

        return getattr(order, "preferred_writer", None)


    @staticmethod
    def _final_amount(adjustment_request) -> Decimal:
        """
        Determine the final total amount to apply to the order after counter.
        """
        if adjustment_request.countered_quantity:
            return Decimal(str(adjustment_request.counter_total_amount))
        return Decimal(str(adjustment_request.requested_total_amount))
        

    @staticmethod
    def _final_writer_amount(adjustment_request) -> Decimal:
        """
        Determine the final writer compensation amount to apply to the order after counter.
        """
        if adjustment_request.countered_quantity:
            return Decimal(
                str(adjustment_request.counter_writer_compensation_amount)
            )
        return Decimal(
            str(adjustment_request.requested_writer_compensation_amount)
        )
    

    @staticmethod
    def _final_payload(adjustment_request) -> dict:
        """
        Determine the final pricing payload to associate with the order snapshot after counter.
        """
        if adjustment_request.countered_quantity:
            return adjustment_request.counter_pricing_payload or {}
        return adjustment_request.requested_pricing_payload or {}
    
    @staticmethod
    def _final_pricing_snapshot(adjustment_request) -> Optional[OrderPricingSnapshot]:
        """
        Determine the final pricing snapshot to associate with the order after counter.
        """
        if adjustment_request.countered_quantity:
            return adjustment_request.counter_pricing_snapshot
        return adjustment_request.requested_pricing_snapshot
    

    @staticmethod
    def _to_decimal(value: Any) -> Decimal:
        """Convert a value to Decimal, handling different input types."""
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))
    
    @staticmethod
    def _compensation_type(adjustment_request) -> str:
        """
        Determine the compensation type for a compensation adjustment based on the adjustment request.
        """
        mapping = {
            "page_increase": "page_delta",
            "slide_increase": "slide_delta",
            "diagram_increase": "diagram_delta",
            "design_concept_increase": "design_concept_delta",
            "extra_service": "extra_service",
            "deadline_decrease": "deadline_decrease",
            "paid_revision": "paid_revision",
        }

        return mapping.get(adjustment_request.adjustment_type, "other")
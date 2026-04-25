
from typing import Any, Optional
from django.db import transaction

from notifications_system.services.notification_service import (
    NotificationService,
)
from orders.models.progresssive_delivery.progressive_delivery import (
    OrderMilestone,
    OrderProgressivePlan,
)
from orders.models.orders.constants import (
    ORDER_EXTRA_SERVICE_PROGRESSIVE_DELIVERY,
)
from orders.models.orders.order_timeline_event import (
    OrderTimelineEvent,
)

class ProgressiveDeliveryService:
    """
    Manage progressive delivery plans and milestones.
    """

    @classmethod
    @transaction.atomic
    def create_plan(
        cls,
        *,
        order,
        milestones: list[dict[str, Any]],
        created_by: Optional[Any] = None,
        is_required: bool = True,
    ):
        """
        Create a progressuve delivery plan for an order.

        Args:
            order:
                Target order.
            milestones:
                Milstone payloads containing title, due_at, percentage.
            created_by:
                Optional actor creating the plan.
            is_required:
                Whether the drafts are mandatory for this order.

        Returns:
            OrderProgressivePlan:
                Created progressive plan.
        
        """
        plan = OrderProgressivePlan.objects.create(
            website=order.website,
            order=order,
            is_required=True,
        )

        for item in milestones:
            OrderMilestone.objects.create(
                website=order.website,
                plan=plan,
                order=order,
                title=item["title"],
                description=item.get("description", ""),
                due_at=item["due_at"],
                percentage=item["percentage"],
            )

        OrderTimelineEvent.objects.create(
            website=order.website,
            order=order,
            actor=created_by,
            event_type="progressive_delivery_plan_created",
            metadata={
                "plan_id": plan.pk,
                "milestone_count": len(milestones),
            },
        )

        cls._create_timeline_event(
            order=order,
            actor=created_by,
            event_type="progressive_plan_created",
            metadata={
                "plan_id": plan.pk,
                "milestone_count": len(milestones),
                "source": "manual_or_order_creation",
            },
        )

        cls._notify_plan_created(
            order=order,
            plan=plan,
            milestone_count=len(milestones),
            triggered_by=created_by,
        )

        return plan
    

    @classmethod
    @transaction.atomic
    def create_plan_from_adjustment(
        cls,
        *,
        adjustment_request,
        created_by: Optional[Any] = None,
    ):
        """
        Create a progressive delivery plan after a paid adjustment.

        This is used when the client adds progressive delivery after
        the order has already been placed and funded.

        Args:
            adjustment_request:
                Funded extra_service adjustment request.
            created_by:
                Optional actor or system user.

        Returns:
            OrderProgressivePlan:
                Created progressive plan
        """
        order = adjustment_request.order

        if adjustment_request.extra_service_code != (
            ORDER_EXTRA_SERVICE_PROGRESSIVE_DELIVERY
        ):
            raise ValueError(
                "Adjustment is not for progressive delivery"
            )
        
        milestones = cls._resolve_milestones_from_adjustment(
            adjustment_request=adjustment_request,
        )

        plan = cls.create_plan(
            order=order,
            milestones=milestones,
            created_by=created_by,
            is_required=True,
        )

        cls._create_timeline_event(
            order=order,
            actor=created_by,
            event_type="progressive_plan_created_from_adjustment",
            metadata={
                "plan_id": plan.pk,
                "adjustment_request_id": adjustment_request.pk,
                "milestone_count": len(milestones),
                "extra_service_code": adjustment_request.extra_service_code,
            },
        )

        return plan
    

    @staticmethod
    def _resolve_milestones_from_adjustment(
        *,
        adjustment_request,
    ) -> list[dict[str, Any]]:
        """
        Resolve milstone payloads from adjustment metadata.

        Expected payload shape, preferably inside request_pricing_payload:

        {
            "progressive_delivery": {
                "milestones": [
                    {
                        "title": "50% Draft",
                        "description": "",
                        "due_at": "...",
                        "percentage": 50,
                    }
                ]
            }
        }

        Fallback supports direct key:
        {"milestones": [...]}
        """
        payload = (
            adjustment_request.counter_pricing_payload
            if getattr(adjustment_request, "countered_quantity", None)
            else adjustment_request.request_pricing_payload
        ) or {}

        progressive_payload = payload.get("progressive_delivery", {})
        milestones = progressive_payload.get("milestones")

        if not milestones:
            milestones = payload.get("milestones", [])

        if not milestones:
            raise ValueError(
                "Progressive delivery adjustment requires milestones"
            )
        
        return milestones
    
    @staticmethod
    def _create_timeline_event(
        *,
        order,
        actor: Optional[Any],
        event_type: str,
        metadata: dict[str, Any],
    ) -> None:
        """
        Create an order timeline event.
        """

        OrderTimelineEvent.objects.create(
            website=order.website,
            order=order,
            actor=actor,
            event_type=event_type,
            metadata=metadata,
        )


    @staticmethod
    def _notify_plan_created(
        *,
        order,
        plan,
        milestone_count: int,
        triggered_by: Optional[Any],
    ) -> None:
        """
        Notify client and writer that progressive delivery is active.
        """
        NotificationService.notify(
            event_key="orders.progressive_delivery.plan_created",
            recipient=order.client,
            website=order.website,
            context={
                "order_id": order.pk,
                "plan_id": plan.pk,
                "milestone_count": milestone_count,
            },
            triggered_by=triggered_by,
        )


    @staticmethod
    def _resolve_current_writer(order):
        """
        Best-effort resolve current writer.
        """
        assignments = getattr(order, "assignments", None)
        if assignments is not None:
            current_assignment = (
                assignments.filter(is_current=True)
                .select_related("writer")
                .first()
            )
            if current_assignment is not None:
                return current_assignment.writer
            
        return getattr(order, "preferred_writer", None)

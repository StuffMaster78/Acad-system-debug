from django.db import transaction
from django.utils import timezone

from orders.models.drafts.draft import OrderDraft
from orders.workflows.draft_workflow import DraftWorkflow
from notifications_system.services.notification_service import (
    NotificationService,
)
from orders.models.orders.order_timeline_event import OrderTimelineEvent
class DraftService:
    """
    Handle draft submissions and reviews.
    """

    @classmethod
    @transaction.atomic
    def submit_draft(
        cls,
        *,
        order,
        draft,
        submitted_by,
        reviewed_by,
        milestone=None,
        approve: bool,
        note: str = "",
    ):
    
        draft = OrderDraft.objects.create(
            website=order.website,
            order=order,
            milestone=milestone,
            submitted_by=submitted_by,
            note=note,
            status="submitted",
        )
    
        NotificationService.notify(
            event_key= "orders.draft.submitted",
            recipient=order.client,
            website=order.website,
            context={
                "order_id": order.pk,
                "draft_id": draft.pk,
                "milestone_id": getattr(milestone, "pk", None)
            },
            triggered_by=submitted_by,
        )

        OrderTimelineEvent.objects.create(
            website=draft.website,
            order=draft.order,
            actor=reviewed_by,
            event_type="draft_reviewed",
            metadata={
                "draft_id": draft.pk,
                "status": draft.status,
                "approved": approve,
            },
        )

        return draft
        

    @classmethod
    @transaction.atomic
    def review_draft(
        cls,
        *,
        draft,
        reviewed_by,
        approve: bool,
    ):
        next_status = "reviewed" if approve else "revision_requested"

        DraftWorkflow.ensure_can_transition(
            current=draft.status,
            next_=next_status,
        )

        draft.status = next_status
        draft.reviewed_at = timezone.now()
        draft.save(update_fields=["status", "reviewed_at"])

        if approve and draft.milestone:
            draft.milestone.is_completed = True
            draft.milestone.save(update_fields=["is_completed"])

        NotificationService.notify(
            event_key=(
                "orders.draft.approved"
                if approve
                else "orders.draft.revision_requested"
            ),
            recipient=draft.submitted_by,
            website=draft.website,
            context={
                "order_id": draft.order.pk,
                "draft_id": draft.pk,
                "status": draft.status,
            },
            triggered_by=reviewed_by,

        )

        OrderTimelineEvent.objects.create(
            website=draft.website,
            order=draft.order,
            actor=reviewed_by,
            event_type="draft_reviewed",
            metadata={
                "draft_id": draft.pk,
                "status": draft.status,
                "approved": approve,
            },

        )

        return draft
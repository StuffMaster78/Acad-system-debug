from __future__ import annotations

from typing import Any, cast

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from special_orders.api.permissions import (
    CanAssignSpecialOrderWriter,
    CanManageSpecialOrderQuote,
    CanUploadSpecialOrderDeliverable,
    CanViewSpecialOrder,
)
from special_orders.api.serializers.lifecycle_serializers import (
    AssignWriterSerializer,
    CancelOrderSerializer,
    HoldOrderSerializer,
    NotesSerializer,
    ReleaseHoldSerializer,
    RequestRevisionSerializer,
    StartRevisionSerializer,
    SubmitWorkSerializer,
)
from special_orders.api.serializers.special_order_serializers import (
    SpecialOrderClientDetailSerializer,
    SpecialOrderDetailSerializer,
    SpecialOrderWriterDetailSerializer,
    serialize_special_order_milestone,
)
from special_orders.models import SpecialOrderWriterPayRule
from special_orders.selectors import SpecialOrderSelector
from special_orders.services.new_services.special_order_assignment_service import (
    SpecialOrderAssignmentService,
)
from special_orders.services.new_services.special_order_cancellation_service import (
    SpecialOrderCancellationService,
)
from special_orders.services.new_services.special_order_completion_service import (
    SpecialOrderCompletionService,
)
from special_orders.services.new_services.special_order_hold_service import (
    SpecialOrderHoldService,
)
from special_orders.services.new_services.special_order_revision_service import (
    SpecialOrderRevisionService,
)
from special_orders.services.new_services.special_order_submission_service import (
    SpecialOrderSubmissionService,
)


def _detail_serializer(special_order, request):
    role = getattr(request.user, "role", "")
    serializer_class = SpecialOrderDetailSerializer
    if role == "writer":
        serializer_class = SpecialOrderWriterDetailSerializer
    elif role == "client":
        serializer_class = SpecialOrderClientDetailSerializer
    return serializer_class(
        special_order,
        context={"request": request},
    )


class AssignWriterView(APIView):
    permission_classes = [IsAuthenticated, CanAssignSpecialOrderWriter]

    def post(self, request, special_order_id: int):
        serializer = AssignWriterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        User = get_user_model()
        writer = User.objects.get(
            id=int(data["writer_id"]),
            website=request.user.website,
        )

        writer_pay_rule = None
        writer_pay_rule_id = data.get("writer_pay_rule_id")
        if writer_pay_rule_id is not None:
            writer_pay_rule = SpecialOrderWriterPayRule.objects.get(
                id=int(writer_pay_rule_id),
                website=request.user.website,
            )

        special_order = SpecialOrderAssignmentService.assign_writer(
            special_order=special_order,
            writer=writer,
            assigned_by=request.user,
            writer_pay_rule=writer_pay_rule,
            reason=str(data.get("reason", "")),
        )

        return Response(_detail_serializer(special_order, request).data)


class StartWorkView(APIView):
    permission_classes = [IsAuthenticated, CanUploadSpecialOrderDeliverable]

    def post(self, request, special_order_id: int):
        serializer = NotesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        special_order = SpecialOrderAssignmentService.start_work(
            special_order=special_order,
            started_by=request.user,
            reason=str(data.get("notes", "")),
        )

        return Response(_detail_serializer(special_order, request).data)


class SubmitWorkView(APIView):
    permission_classes = [IsAuthenticated, CanUploadSpecialOrderDeliverable]

    def post(self, request, special_order_id: int):
        serializer = SubmitWorkSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        special_order = SpecialOrderSubmissionService.submit_work(
            special_order=special_order,
            submitted_by=request.user,
            notes=str(data.get("notes", "")),
            mark_ready_for_delivery=bool(
                data.get("mark_ready_for_delivery", False),
            ),
        )

        return Response(_detail_serializer(special_order, request).data)


class MarkReadyForDeliveryView(APIView):
    permission_classes = [IsAuthenticated, CanManageSpecialOrderQuote]

    def post(self, request, special_order_id: int):
        serializer = NotesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        special_order = SpecialOrderSubmissionService.mark_ready_for_delivery(
            special_order=special_order,
            marked_by=request.user,
            notes=str(data.get("notes", "")),
        )

        return Response(_detail_serializer(special_order, request).data)


class CompleteOrderView(APIView):
    permission_classes = [IsAuthenticated, CanManageSpecialOrderQuote]

    def post(self, request, special_order_id: int):
        serializer = NotesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        special_order = SpecialOrderCompletionService.complete_order(
            special_order=special_order,
            completed_by=request.user,
            notes=str(data.get("notes", "")),
        )

        return Response(_detail_serializer(special_order, request).data)


class ApproveOrderView(APIView):
    permission_classes = [IsAuthenticated, CanViewSpecialOrder]

    def post(self, request, special_order_id: int):
        serializer = NotesSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        special_order = SpecialOrderCompletionService.approve_order(
            special_order=special_order,
            approved_by=request.user,
            notes=str(data.get("notes", "")),
        )

        return Response(_detail_serializer(special_order, request).data)


class HoldOrderView(APIView):
    permission_classes = [IsAuthenticated, CanManageSpecialOrderQuote]

    def post(self, request, special_order_id: int):
        serializer = HoldOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        special_order = SpecialOrderHoldService.put_on_hold(
            special_order=special_order,
            held_by=request.user,
            reason=str(data["reason"]),
        )

        return Response(_detail_serializer(special_order, request).data)


class ReleaseHoldView(APIView):
    permission_classes = [IsAuthenticated, CanManageSpecialOrderQuote]

    def post(self, request, special_order_id: int):
        serializer = ReleaseHoldSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        special_order = SpecialOrderHoldService.release_hold(
            special_order=special_order,
            released_by=request.user,
            restore_status=str(data["restore_status"]),
            reason=str(data.get("reason", "")),
        )

        return Response(_detail_serializer(special_order, request).data)


class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated, CanManageSpecialOrderQuote]

    def post(self, request, special_order_id: int):
        serializer = CancelOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        special_order = SpecialOrderCancellationService.cancel_order(
            special_order=special_order,
            cancelled_by=request.user,
            reason=str(data["reason"]),
        )

        return Response(_detail_serializer(special_order, request).data)


class RequestRevisionView(APIView):
    permission_classes = [IsAuthenticated, CanViewSpecialOrder]

    def post(self, request, special_order_id: int):
        serializer = RequestRevisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        special_order = SpecialOrderRevisionService.request_revision(
            special_order=special_order,
            requested_by=request.user,
            reason=str(data["reason"]),
            metadata=cast(dict[str, Any], data.get("metadata", {})),
        )

        return Response(_detail_serializer(special_order, request).data)


class StartRevisionView(APIView):
    permission_classes = [IsAuthenticated, CanUploadSpecialOrderDeliverable]

    def post(self, request, special_order_id: int):
        serializer = StartRevisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = cast(dict[str, Any], serializer.validated_data)

        special_order = SpecialOrderSelector.get_by_id(
            website=request.user.website,
            special_order_id=special_order_id,
        )
        self.check_object_permissions(request, special_order)

        special_order = SpecialOrderRevisionService.start_revision(
            special_order=special_order,
            started_by=request.user,
            notes=str(data.get("notes", "")),
        )

        return Response(_detail_serializer(special_order, request).data)

# ── Milestone actions ─────────────────────────────────────────────────────────

def _get_order(special_order_id: int, website):
    from special_orders.models import SpecialOrder
    try:
        return SpecialOrder.objects.get(pk=special_order_id, website=website)
    except SpecialOrder.DoesNotExist:
        return None


def _req_website(request):
    w = getattr(request, "website", None)
    if w:
        return w
    try:
        return request.user.account_profiles.order_by("pk").first().website
    except Exception:
        return None


class SpecialOrderMilestoneListView(APIView):
    """GET /special-orders/<id>/milestones/   — list funding milestones with delivery tracking."""
    permission_classes = [IsAuthenticated, CanViewSpecialOrder]

    def get(self, request, special_order_id: int):
        from special_orders.models.funding import SpecialOrderFundingMilestone
        from special_orders.models.delivery import SpecialOrderDeliverable

        website = _req_website(request)
        order = _get_order(special_order_id, website)
        if not order:
            return Response({"detail": "Not found."}, status=404)

        milestones = SpecialOrderFundingMilestone.objects.filter(
            special_order=order
        ).order_by("sequence")

        # Index deliverables by milestone_id stored in metadata
        deliverables = {
            d.metadata.get("milestone_id"): d
            for d in SpecialOrderDeliverable.objects.filter(
                special_order=order
            ).order_by("-created_at")
            if d.metadata.get("milestone_id")
        }

        include_money = getattr(request.user, "role", "") != "writer"
        result = [
            serialize_special_order_milestone(
                order=order,
                milestone=m,
                deliverable=deliverables.get(m.id),
                include_money=include_money,
            )
            for m in milestones
        ]

        return Response(result)


class SpecialOrderMilestoneDeliverView(APIView):
    """
    POST /special-orders/<id>/milestones/<milestone_id>/deliver/
    Writer submits a deliverable for this milestone.
    Body: { notes: str, file_reference?: str }
    """
    permission_classes = [IsAuthenticated, CanViewSpecialOrder]

    def post(self, request, special_order_id: int, milestone_id: int):
        from special_orders.models.funding import SpecialOrderFundingMilestone
        from special_orders.models.delivery import SpecialOrderDeliverable
        from special_orders.constants.delivery import SpecialOrderDeliverableStatus
        from django.utils import timezone

        website = _req_website(request)
        order = _get_order(special_order_id, website)
        if not order:
            return Response({"detail": "Not found."}, status=404)

        try:
            milestone = SpecialOrderFundingMilestone.objects.get(
                pk=milestone_id, special_order=order
            )
        except SpecialOrderFundingMilestone.DoesNotExist:
            return Response({"detail": "Milestone not found."}, status=404)

        notes        = request.data.get("notes", request.data.get("delivery_notes", ""))
        file_ref     = request.data.get("file_reference", request.data.get("delivery_file_url", ""))
        now          = timezone.now()

        deliverable, created = SpecialOrderDeliverable.objects.update_or_create(
            special_order=order,
            metadata__milestone_id=milestone.id,
            defaults={
                "website":        website,
                "title":          f"Delivery for {milestone.label}",
                "description":    notes,
                "status":         SpecialOrderDeliverableStatus.UPLOADED,
                "file_reference": file_ref or None,
                "uploaded_by":    request.user,
                "uploaded_at":    now,
                "metadata":       {"milestone_id": milestone.id},
            },
        )
        if created:
            deliverable.metadata = {"milestone_id": milestone.id}
            deliverable.save(update_fields=["metadata"])

        return Response(
            serialize_special_order_milestone(
                order=order,
                milestone=milestone,
                deliverable=deliverable,
                include_money=getattr(request.user, "role", "") != "writer",
            ),
            status=status.HTTP_201_CREATED,
        )


class SpecialOrderMilestoneApproveView(APIView):
    """
    POST /special-orders/<id>/milestones/<milestone_id>/approve/
    Admin approves the deliverable for this milestone.
    """
    permission_classes = [IsAuthenticated, CanViewSpecialOrder]

    def post(self, request, special_order_id: int, milestone_id: int):
        from special_orders.models.funding import SpecialOrderFundingMilestone
        from special_orders.models.delivery import SpecialOrderDeliverable
        from special_orders.constants.delivery import SpecialOrderDeliverableStatus
        from special_orders.constants.funding import FundingMilestoneStatus
        from django.utils import timezone

        website = _req_website(request)
        order = _get_order(special_order_id, website)
        if not order:
            return Response({"detail": "Not found."}, status=404)

        try:
            milestone = SpecialOrderFundingMilestone.objects.get(
                pk=milestone_id, special_order=order
            )
        except SpecialOrderFundingMilestone.DoesNotExist:
            return Response({"detail": "Milestone not found."}, status=404)

        now = timezone.now()

        # Approve the associated deliverable if it exists
        deliverable = SpecialOrderDeliverable.objects.filter(
            special_order=order
        ).filter(metadata__milestone_id=milestone.id).first()

        if deliverable:
            deliverable.status      = SpecialOrderDeliverableStatus.APPROVED
            deliverable.reviewed_by = request.user
            deliverable.reviewed_at = now
            deliverable.save(update_fields=["status", "reviewed_by", "reviewed_at", "updated_at"])

        # Advance milestone to PAID if currently pending/partially paid
        if milestone.status in (FundingMilestoneStatus.PENDING, FundingMilestoneStatus.PARTIALLY_PAID):
            milestone.status = FundingMilestoneStatus.PAID
            milestone.save(update_fields=["status", "updated_at"])

        return Response(
            serialize_special_order_milestone(
                order=order,
                milestone=milestone,
                deliverable=deliverable,
                include_money=getattr(request.user, "role", "") != "writer",
            )
        )


class SpecialOrderMilestoneRequestRevisionView(APIView):
    """
    POST /special-orders/<id>/milestones/<milestone_id>/request-revision/
    Admin requests a revision for this milestone's deliverable.
    Body: { notes: str }
    """
    permission_classes = [IsAuthenticated, CanViewSpecialOrder]

    def post(self, request, special_order_id: int, milestone_id: int):
        from special_orders.models.funding import SpecialOrderFundingMilestone
        from special_orders.models.delivery import SpecialOrderDeliverable
        from special_orders.constants.delivery import SpecialOrderDeliverableStatus
        from django.utils import timezone

        website = _req_website(request)
        order = _get_order(special_order_id, website)
        if not order:
            return Response({"detail": "Not found."}, status=404)

        try:
            milestone = SpecialOrderFundingMilestone.objects.get(
                pk=milestone_id, special_order=order
            )
        except SpecialOrderFundingMilestone.DoesNotExist:
            return Response({"detail": "Milestone not found."}, status=404)

        notes = request.data.get("notes", "").strip()
        now   = timezone.now()

        deliverable = SpecialOrderDeliverable.objects.filter(
            special_order=order
        ).filter(metadata__milestone_id=milestone.id).first()

        if not deliverable:
            return Response({"detail": "No deliverable found for this milestone."}, status=400)

        deliverable.status       = SpecialOrderDeliverableStatus.REJECTED
        deliverable.review_notes = notes
        deliverable.reviewed_by  = request.user
        deliverable.reviewed_at  = now
        deliverable.save(update_fields=["status", "review_notes", "reviewed_by", "reviewed_at", "updated_at"])

        return Response(
            serialize_special_order_milestone(
                order=order,
                milestone=milestone,
                deliverable=deliverable,
                include_money=getattr(request.user, "role", "") != "writer",
            )
        )

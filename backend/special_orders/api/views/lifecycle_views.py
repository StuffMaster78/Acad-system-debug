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
    SpecialOrderDetailSerializer,
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

        return Response(SpecialOrderDetailSerializer(special_order).data)


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

        return Response(SpecialOrderDetailSerializer(special_order).data)


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

        return Response(SpecialOrderDetailSerializer(special_order).data)


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

        return Response(SpecialOrderDetailSerializer(special_order).data)


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

        return Response(SpecialOrderDetailSerializer(special_order).data)


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

        return Response(SpecialOrderDetailSerializer(special_order).data)


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

        return Response(SpecialOrderDetailSerializer(special_order).data)


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

        return Response(SpecialOrderDetailSerializer(special_order).data)


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

        return Response(SpecialOrderDetailSerializer(special_order).data)


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

        return Response(SpecialOrderDetailSerializer(special_order).data)


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

        return Response(SpecialOrderDetailSerializer(special_order).data)
from __future__ import annotations

from typing import Any, cast

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.permissions.reassignment_permissions import (
    CanCancelReassignment,
    CanRequestReassignment,
    CanReviewReassignment,
)
from orders.api.serializers.reassignments.reassignment_approve_assign_serializer import (  # noqa: E501
    ReassignmentApproveAssignSerializer,
)
from orders.api.serializers.reassignments.reassignment_approve_pool_serializer import (  # noqa: E501
    ReassignmentApprovePoolSerializer,
)
from orders.api.serializers.reassignments.reassignment_cancel_serializer import (
    ReassignmentCancelSerializer,
)
from orders.api.serializers.reassignments.reassignment_reject_serializer import (
    ReassignmentRejectSerializer,
)
from orders.api.serializers.reassignments.reassignment_request_serializer import (  # noqa: E501
    ReassignmentRequestSerializer,
)
from orders.models.orders import Order
from orders.models.orders.order_reassignment_request import (
OrderReassignmentRequest,
)
from orders.services.order_reassignment_service import (
    OrderReassignmentService,
)


class ReassignmentRequestView(GenericAPIView):
    """
    Create a reassignment request for an order.
    """

    serializer_class = ReassignmentRequestSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanRequestReassignment,
    ]

    def post(
        self,
        request: Request,
        order_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        order = self._get_order_for_tenant(
            request=request,
            order_id=order_id,
        )
        self.check_object_permissions(request, order)

        reassignment_request = (
            OrderReassignmentService.request_reassignment(
                order=order,
                requested_by=request.user,
                requester_role=validated_data["requester_role"],
                reason=validated_data["reason"],
                internal_notes=validated_data.get("internal_notes", ""),
                triggered_by=request.user,
            )
        )

        return Response(
            {
                "message": "Reassignment request created.",
                "reassignment_request_id": reassignment_request.pk,
                "order_id": order.pk,
                "status": reassignment_request.status,
            },
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _get_order_for_tenant(
        *,
        request: Request,
        order_id: int,
    ) -> Order:
        user = cast(Any, request.user)
        return get_object_or_404(
            Order.objects.select_related(
                "website",
                "client",
                "preferred_writer",
            ),
            pk=order_id,
            website=user.website,
        )


class ReassignmentRejectView(GenericAPIView):
    """
    Reject a pending reassignment request.
    """

    serializer_class = ReassignmentRejectSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanReviewReassignment,
    ]

    def post(
        self,
        request: Request,
        reassignment_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        reassignment_request = self._get_reassignment_for_tenant(
            request=request,
            reassignment_id=reassignment_id,
        )
        self.check_object_permissions(request, reassignment_request)

        updated_request = OrderReassignmentService.reject_reassignment(
            reassignment_request=reassignment_request,
            reviewed_by=request.user,
            internal_notes=validated_data.get("internal_notes", ""),
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Reassignment request rejected.",
                "reassignment_request_id": updated_request.pk,
                "status": updated_request.status,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_reassignment_for_tenant(
        *,
        request: Request,
        reassignment_id: int,
    ) -> OrderReassignmentRequest:
        user = cast(Any, request.user)
        return get_object_or_404(
            OrderReassignmentRequest.objects.select_related(
                "website",
                "order",
                "requested_by",
                "current_assignment",
            ),
            pk=reassignment_id,
            website=user.website,
        )


class ReassignmentCancelView(GenericAPIView):
    """
    Cancel a pending reassignment request.
    """

    serializer_class = ReassignmentCancelSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanCancelReassignment,
    ]

    def post(
        self,
        request: Request,
        reassignment_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        reassignment_request = self._get_reassignment_for_tenant(
            request=request,
            reassignment_id=reassignment_id,
        )
        self.check_object_permissions(request, reassignment_request)

        updated_request = (
            OrderReassignmentService.cancel_reassignment_request(
                reassignment_request=reassignment_request,
                cancelled_by=request.user,
                triggered_by=request.user,
            )
        )

        return Response(
            {
                "message": "Reassignment request cancelled.",
                "reassignment_request_id": updated_request.pk,
                "status": updated_request.status,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_reassignment_for_tenant(
        *,
        request: Request,
        reassignment_id: int,
    ) -> OrderReassignmentRequest:
        user = cast(Any, request.user)
        return get_object_or_404(
            OrderReassignmentRequest.objects.select_related(
                "website",
                "order",
                "requested_by",
                "current_assignment",
            ),
            pk=reassignment_id,
            website=user.website,
        )


class ReassignmentApproveReturnToPoolView(GenericAPIView):
    """
    Approve reassignment request and return order to pool.
    """

    serializer_class = ReassignmentApprovePoolSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanReviewReassignment,
    ]

    def post(
        self,
        request: Request,
        reassignment_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        reassignment_request = self._get_reassignment_for_tenant(
            request=request,
            reassignment_id=reassignment_id,
        )
        self.check_object_permissions(request, reassignment_request)

        updated_order = OrderReassignmentService.approve_return_to_pool(
            reassignment_request=reassignment_request,
            reviewed_by=request.user,
            internal_notes=validated_data.get("internal_notes", ""),
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Reassignment approved and order returned to pool.",
                "order_id": updated_order.pk,
                "status": updated_order.status,
                "visibility_mode": updated_order.visibility_mode,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_reassignment_for_tenant(
        *,
        request: Request,
        reassignment_id: int,
    ) -> OrderReassignmentRequest:
        user = cast(Any, request.user)
        return get_object_or_404(
            OrderReassignmentRequest.objects.select_related(
                "website",
                "order",
                "requested_by",
                "current_assignment",
            ),
            pk=reassignment_id,
            website=user.website,
        )


class ReassignmentApproveAssignWriterView(GenericAPIView):
    """
    Approve reassignment request and assign a specific writer.
    """

    serializer_class = ReassignmentApproveAssignSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        CanReviewReassignment,
    ]

    def post(
        self,
        request: Request,
        reassignment_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = cast(dict[str, Any], serializer.validated_data)

        reassignment_request = self._get_reassignment_for_tenant(
            request=request,
            reassignment_id=reassignment_id,
        )
        self.check_object_permissions(request, reassignment_request)

        writer = self._get_writer_for_tenant(
            request=request,
            writer_id=validated_data["writer_id"],
        )

        assignment = (
            OrderReassignmentService.approve_assign_specific_writer(
                reassignment_request=reassignment_request,
                reviewed_by=request.user,
                assign_to_writer=writer,
                internal_notes=validated_data.get("internal_notes", ""),
                triggered_by=request.user,
            )
        )

        return Response(
            {
                "message": "Reassignment approved and writer assigned.",
                "assignment_id": assignment.pk,
                "order_id": assignment.order.pk,
                "writer_id": assignment.writer.pk,
                "status": assignment.status,
                "source": assignment.source,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_reassignment_for_tenant(
        *,
        request: Request,
        reassignment_id: int,
    ) -> OrderReassignmentRequest:
        user = cast(Any, request.user)
        return get_object_or_404(
            OrderReassignmentRequest.objects.select_related(
                "website",
                "order",
                "requested_by",
                "current_assignment",
            ),
            pk=reassignment_id,
            website=user.website,
        )

    @staticmethod
    def _get_writer_for_tenant(
        *,
        request: Request,
        writer_id: int,
    ) -> Any:
        user = cast(Any, request.user)
        user_model = type(user)
        return get_object_or_404(
            user_model.objects.filter(website=user.website),
            pk=writer_id,
        )
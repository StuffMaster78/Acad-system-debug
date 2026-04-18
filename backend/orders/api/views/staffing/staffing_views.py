from __future__ import annotations

from typing import Any, cast

from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from orders.api.serializers.staffing.express_interest_serializer import (
    ExpressInterestSerializer,
)
from orders.api.serializers.staffing.route_to_staffing_serializer import (
    RouteToStaffingSerializer,
)
from orders.api.serializers.staffing.take_order_serializer import (
    TakeOrderSerializer,
)
from orders.models import Order
from orders.services.order_staffing_service import OrderStaffingService
from orders.api.serializers.staffing.assign_direct_serializer import (
    AssignDirectSerializer,
)
from orders.api.serializers.staffing.assign_from_interest_serializer import (
    AssignFromInterestSerializer,
)
from orders.api.serializers.staffing.withdraw_interest_serializer import (
    WithdrawInterestSerializer,
)
from orders.models import OrderInterest
from orders.api.serializers.staffing.preferred_writer_accept_serializer import (
    PreferredWriterAcceptSerializer,
)
from orders.api.serializers.staffing.preferred_writer_decline_serializer import (
    PreferredWriterDeclineSerializer,
)
from orders.api.serializers.staffing.release_to_pool_serializer import (
    ReleaseToPoolSerializer,
)


class RouteOrderToStaffingView(GenericAPIView):
    """
    Route an order into staffing flow.

    Intended for staff side usage after payment or internal creation
    makes the order staffing ready.
    """

    serializer_class = RouteToStaffingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(
        self,
        request: Request,
        order_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = self._get_order_for_tenant(
            request=request,
            order_id=order_id,
        )

        updated_order = OrderStaffingService.route_order_to_staffing(
            order=order,
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Order routed to staffing.",
                "order_id": updated_order.pk,
                "status": updated_order.status,
                "visibility_mode": updated_order.visibility_mode,
                "preferred_writer_status": (
                    updated_order.preferred_writer_status
                ),
            },
            status=status.HTTP_200_OK,
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


class ExpressInterestView(GenericAPIView):
    """
    Allow a writer to express interest in a staffing ready pool order.
    """

    serializer_class = ExpressInterestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(
        self,
        request: Request,
        order_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = self._get_order_for_tenant(
            request=request,
            order_id=order_id,
        )

        validated_data = cast(dict[str, Any], serializer.validated_data)

        interest = OrderStaffingService.express_interest(
            order=order,
            writer=request.user,
            message=validated_data.get("message", ""),
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Interest submitted.",
                "interest_id": interest.pk,
                "order_id": order.pk,
                "status": interest.status,
                "interest_type": interest.interest_type,
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


class TakeOrderView(GenericAPIView):
    """
    Allow a writer to self take a staffing ready pool order.
    """

    serializer_class = TakeOrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(
        self,
        request: Request,
        order_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = self._get_order_for_tenant(
            request=request,
            order_id=order_id,
        )

        assignment = OrderStaffingService.take_order(
            order=order,
            writer=request.user,
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Order taken successfully.",
                "assignment_id": assignment.pk,
                "order_id": order.pk,
                "writer_id": assignment.writer.pk,
                "status": assignment.status,
                "source": assignment.source,
            },
            status=status.HTTP_200_OK,
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
    

class WithdrawInterestView(GenericAPIView):
    """
    Allow a writer to withdraw their pending interest.
    """

    serializer_class = WithdrawInterestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(
        self,
        request: Request,
        interest_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        interest = self._get_interest_for_tenant(
            request=request,
            interest_id=interest_id,
        )

        updated_interest = OrderStaffingService.withdraw_interest(
            interest=interest,
            writer=request.user,
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Interest withdrawn.",
                "interest_id": updated_interest.pk,
                "status": updated_interest.status,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_interest_for_tenant(
        *,
        request: Request,
        interest_id: int,
    ) -> OrderInterest:
        user = cast(Any, request.user)
        return get_object_or_404(
            OrderInterest.objects.select_related(
                "website",
                "order",
                "writer",
            ),
            pk=interest_id,
            website=user.website,
        )
    

class AssignFromInterestView(GenericAPIView):
    """
    Allow staff to assign an order from an existing interest.
    """

    serializer_class = AssignFromInterestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(
        self,
        request: Request,
        interest_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        interest = self._get_interest_for_tenant(
            request=request,
            interest_id=interest_id,
        )

        assignment = OrderStaffingService.assign_from_interest(
            interest=interest,
            assigned_by=request.user,
        )

        return Response(
            {
                "message": "Order assigned from interest.",
                "assignment_id": assignment.pk,
                "order_id": assignment.order.pk,
                "writer_id": assignment.writer.pk,
                "status": assignment.status,
                "source": assignment.source,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_interest_for_tenant(
        *,
        request: Request,
        interest_id: int,
    ) -> OrderInterest:
        user = cast(Any, request.user)
        return get_object_or_404(
            OrderInterest.objects.select_related(
                "website",
                "order",
                "writer",
            ),
            pk=interest_id,
            website=user.website,
        )
    

class AssignDirectView(GenericAPIView):
    """
    Allow staff to assign a staffing ready order directly to a writer.
    """

    serializer_class = AssignDirectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(
        self,
        request: Request,
        order_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = self._get_order_for_tenant(
            request=request,
            order_id=order_id,
        )
        validated_data = cast(dict[str, Any], serializer.validated_data)
        writer = self._get_writer_for_tenant(
            request=request,
            writer_id=validated_data["writer_id"],
        )

        assignment = OrderStaffingService.assign_directly(
            order=order,
            writer=writer,
            assigned_by=request.user,
        )

        return Response(
            {
                "message": "Order assigned directly.",
                "assignment_id": assignment.pk,
                "order_id": assignment.order.pk,
                "writer_id": assignment.writer.pk,
                "status": assignment.status,
                "source": assignment.source,
            },
            status=status.HTTP_200_OK,
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
    
class PreferredWriterAcceptView(GenericAPIView):
    """
    Allow the invited preferred writer to accept the invitation.
    """

    serializer_class = PreferredWriterAcceptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(
        self,
        request: Request,
        interest_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        interest = self._get_interest_for_tenant(
            request=request,
            interest_id=interest_id,
        )

        assignment = (
            OrderStaffingService.accept_preferred_writer_invitation(
                interest=interest,
                writer=request.user,
                triggered_by=request.user,
            )
        )

        return Response(
            {
                "message": "Preferred writer invitation accepted.",
                "assignment_id": assignment.pk,
                "order_id": assignment.order.pk,
                "writer_id": assignment.writer.pk,
                "status": assignment.status,
                "source": assignment.source,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_interest_for_tenant(
        *,
        request: Request,
        interest_id: int,
    ) -> OrderInterest:
        user = cast(Any, request.user)
        return get_object_or_404(
            OrderInterest.objects.select_related(
                "website",
                "order",
                "writer",
            ),
            pk=interest_id,
            website=user.website,
        )
    

class PreferredWriterDeclineView(GenericAPIView):
    """
    Allow the invited preferred writer to decline the invitation.
    """

    serializer_class = PreferredWriterDeclineSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(
        self,
        request: Request,
        interest_id: int,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        interest = self._get_interest_for_tenant(
            request=request,
            interest_id=interest_id,
        )

        order = OrderStaffingService.decline_preferred_writer_invitation(
            interest=interest,
            writer=request.user,
            triggered_by=request.user,
        )

        return Response(
            {
                "message": "Preferred writer invitation declined.",
                "order_id": order.pk,
                "status": order.status,
                "visibility_mode": order.visibility_mode,
                "preferred_writer_status": order.preferred_writer_status,
            },
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def _get_interest_for_tenant(
        *,
        request: Request,
        interest_id: int,
    ) -> OrderInterest:
        user = cast(Any, request.user)
        return get_object_or_404(
            OrderInterest.objects.select_related(
                "website",
                "order",
                "writer",
            ),
            pk=interest_id,
            website=user.website,
        )
    

class ReleaseToPoolView(GenericAPIView):
    """
    Allow staff to release an actively assigned order back to the pool.
    """

    serializer_class = ReleaseToPoolSerializer
    permission_classes = [permissions.IsAuthenticated]

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

        updated_order = OrderStaffingService.release_to_pool(
            order=order,
            released_by=request.user,
            reason=validated_data["reason"],
        )

        return Response(
            {
                "message": "Order released to pool.",
                "order_id": updated_order.pk,
                "status": updated_order.status,
                "visibility_mode": updated_order.visibility_mode,
                "preferred_writer_status": (
                    updated_order.preferred_writer_status
                ),
            },
            status=status.HTTP_200_OK,
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
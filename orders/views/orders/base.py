from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from rest_framework import status, decorators, viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from orders.models import Order
from orders.serializers import OrderSerializer
from orders.permissions import IsOrderOwnerOrSupport
from orders.services.order_deletion_service import (
    OrderDeletionService, ALLOWED_STAFF_ROLES
)


class OrderBaseViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    Base viewset for orders. Supports list and retrieve operations.

    Attributes:
        queryset: QuerySet of Order objects.
        serializer_class: Serializer used for order objects.
        permission_classes: List of permission classes.
    """

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsOrderOwnerOrSupport]

    def get_queryset(self):
        """
        Returns the filtered queryset for the current user.

        Returns:
            QuerySet: A queryset filtered based on user role.
        """
        user = self.request.user

        if user.is_superuser:
            return Order.objects.all()

        if user.role == 'client':
            return Order.objects.filter(client=user)

        if user.role == 'writer':
            return Order.objects.filter(writer=user)

        if user.role in ['admin', 'support', 'editor']:
            return Order.objects.all()

        return Order.objects.none()
    


    # ---------- soft delete (clients: only UNPAID; staff: any) ----------

    def destroy(self, request, pk=None):
        """
        Soft delete an order.
        - Clients: only their own UNPAID orders.
        - Staff (admin/support/superadmin): any order.
        Returns 204 if a transition happened, 200 if it was already deleted.
        """
        order = get_object_or_404(self.get_queryset().model,
                                  pk=pk, website_id=self.website.id)
        # use the raw manager to bypass deleted filter when needed
        # but we already got it via model; refetch guarded by tenant:
        order = get_object_or_404(Order, pk=pk, website_id=self.website.id)

        reason = request.data.get("reason", "") if isinstance(
            request.data, dict
        ) else ""

        result = self._svc().soft_delete(user=request.user,
                                         order=order,
                                         reason=reason)
        code = status.HTTP_204_NO_CONTENT if result.was_deleted \
            else status.HTTP_200_OK
        return Response(status=code)

    # ---------- restore (client: own; staff: any) ----------

    @decorators.action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        """
        Restore a soft-deleted order.
        - Clients: only their own.
        - Staff: any.
        Returns 200 on success.
        """
        # need to access even if currently deleted, so bypass filtered qs
        order = get_object_or_404(Order, pk=pk, website_id=self.website.id)
        self._svc().restore(user=request.user, order=order)
        return Response(status=status.HTTP_200_OK)

    # ---------- hard delete (irreversible; staff-only) ----------

    @decorators.action(detail=True, methods=["delete"], url_path="hard")
    def hard_delete(self, request, pk=None):
        """
        Irreversible delete (row removal).
        - Staff only: admin/support/superadmin (or superuser).
        Returns 204 if deleted, 200 if it was already gone.
        """
        if not self._is_staff_role(request.user):
            return Response({"detail": "Forbidden."},
                            status=status.HTTP_403_FORBIDDEN)

        result = self._svc().hard_delete_by_id(user=request.user,
                                               order_id=int(pk))
        code = status.HTTP_204_NO_CONTENT if result.was_deleted \
            else status.HTTP_200_OK
        return Response(status=code)
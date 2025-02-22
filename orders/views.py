from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Order, Dispute
from .serializers import OrderSerializer, OrderCreateSerializer, DisputeSerializer
from notifications_system.models import send_notification
from superadmin_management.models import SuperadminLog
from .permissions import IsSuperadminOnly
from django.contrib.auth import get_user_model

User = get_user_model()

class OrderViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for managing Orders.
    """
    queryset = Order.objects.all().select_related('client', 'writer', 'preferred_writer', 'discount_code', 'website')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return the appropriate serializer based on the action."""
        if self.action in ['create', 'update', 'partial_update']:
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        """
        Return the queryset based on the user's role:
        - Admins and support see all orders.
        - Writers see all orders they can express interest in.
        - Assigned writers only see their orders.
        - Clients see only their orders.
        """
        user = self.request.user
        if user.is_staff:  # Admin or support
            return Order.objects.all()
        elif hasattr(user, 'is_writer') and user.is_writer:
            return Order.objects.filter(writer__isnull=True) | Order.objects.filter(writer=user)
        return Order.objects.filter(client=user)

    def perform_create(self, serializer):
        """Automatically assign the authenticated user as the client when creating an order."""
        serializer.save(client=self.request.user)

    def perform_update(self, serializer):
        """Additional logic during order updates (if required)."""
        serializer.save()

    @action(detail=True, methods=["post"], permission_classes=[IsSuperadminOnly])
    def bring_back_in_progress(self, request, pk=None):
        """Superadmin brings back a completed, canceled, or disputed order to 'In Progress'."""
        order = self.get_object()
        if order.bring_back_in_progress(request.user):
            SuperadminLog.objects.create(
                superadmin=request.user,
                action_type="order_reopened",
                action_details=f"Brought back order #{order.id} to 'In Progress'."
            )
            send_notification(order.client, "Order Reopened", f"Your order #{order.id} is now in progress.")
            return Response({"message": "Order is now in progress."}, status=status.HTTP_200_OK)
        return Response({"error": "Order cannot be reopened."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsSuperadminOnly])
    def reassign_writer(self, request, pk=None):
        """Superadmin reassigns an order to a different writer."""
        order = self.get_object()
        new_writer = User.objects.filter(pk=request.data.get("writer_id")).first()
        if not new_writer:
            return Response({"error": "Writer not found."}, status=status.HTTP_404_NOT_FOUND)

        order.reassign_writer(request.user, new_writer)
        SuperadminLog.objects.create(
            superadmin=request.user,
            action_type="order_reassigned",
            action_details=f"Reassigned order #{order.id} to {new_writer.username}."
        )
        send_notification(order.client, "Order Reassigned", f"Your order #{order.id} has been reassigned to a new writer.")
        send_notification(new_writer, "New Assignment", f"You have been assigned order #{order.id}.")
        return Response({"message": "Order reassigned successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsSuperadminOnly])
    def edit_order(self, request, pk=None):
        """Superadmin edits order details."""
        order = self.get_object()
        order.edit_order_details(request.user, request.data)
        SuperadminLog.objects.create(
            superadmin=request.user,
            action_type="order_edited",
            action_details=f"Edited details of order #{order.id}."
        )
        return Response({"message": "Order details updated."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsSuperadminOnly])
    def update_deadline(self, request, pk=None):
        """Superadmin updates the order deadline."""
        order = self.get_object()
        order.update_deadline(request.user, request.data.get("deadline"))
        SuperadminLog.objects.create(
            superadmin=request.user,
            action_type="deadline_updated",
            action_details=f"Updated deadline of order #{order.id}."
        )
        return Response({"message": "Deadline updated."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[IsSuperadminOnly])
    def cancel_order(self, request, pk=None):
        """Superadmin cancels an order."""
        order = self.get_object()
        if order.cancel_order(request.user):
            SuperadminLog.objects.create(
                superadmin=request.user,
                action_type="order_canceled",
                action_details=f"Canceled order #{order.id}."
            )
            send_notification(order.client, "Order Canceled", f"Your order #{order.id} has been canceled.")
            return Response({"message": "Order canceled."}, status=status.HTTP_200_OK)
        return Response({"error": "Order cannot be canceled."}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=["post"])
    def mark_completed(self, request, pk=None):
        """Allows Admins, Editors, and Support to mark an order as completed."""
        order = get_object_or_404(Order, pk=pk)
        if order.mark_as_completed(request.user):
            return Response({"message": "Order marked as completed!"})
        return Response({"error": "You do not have permission to complete this order."}, status=403)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def express_interest(self, request, pk=None):
        """
        Allows a writer to express interest in an order.
        """
        order = self.get_object()
        user = request.user

        if not hasattr(user, 'is_writer') or not user.is_writer:
            return Response({"error": "Only writers can express interest in orders."}, status=status.HTTP_403_FORBIDDEN)

        if order.writer:
            return Response({"error": "Order already has an assigned writer."}, status=status.HTTP_400_BAD_REQUEST)

        order.expressed_interest.add(user)
        send_notification(order.client, "Writer Interest", f"A writer has expressed interest in your order #{order.id}.")
        return Response({"message": "Interest expressed successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAdminUser])
    def assign_writer(self, request, pk=None):
        """
        Allows an admin to assign a writer to an order.
        """
        order = self.get_object()
        writer_id = request.data.get("writer_id")
        writer = User.objects.filter(pk=writer_id, is_writer=True).first()

        if not writer:
            return Response({"error": "Writer not found or not eligible."}, status=status.HTTP_404_NOT_FOUND)

        if order.writer:
            return Response({"error": "Order already assigned to a writer."}, status=status.HTTP_400_BAD_REQUEST)

        order.writer = writer
        order.save()

        send_notification(writer, "New Order Assigned", f"You have been assigned to Order #{order.id}.")
        send_notification(order.client, "Writer Assigned", f"A writer has been assigned to your order #{order.id}.")
        return Response({"message": "Writer assigned successfully."}, status=status.HTTP_200_OK)
    

class DisputeViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for managing Disputes.
    """
    queryset = Dispute.objects.all().select_related('order', 'raised_by')
    serializer_class = DisputeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter disputes based on user role:
        - Superadmins/Admins see all disputes.
        - Users only see disputes they raised.
        """
        user = self.request.user
        if user.is_staff:
            return Dispute.objects.all()
        return Dispute.objects.filter(raised_by=user)

    def perform_create(self, serializer):
        """
        Automatically set the logged-in user as the dispute raiser.
        """
        serializer.save(raised_by=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsSuperadminOnly])
    def resolve(self, request, pk=None):
        """
        Superadmins resolve a dispute by adding resolution notes and updating the status.
        """
        dispute = get_object_or_404(Dispute, pk=pk)
        resolution_notes = request.data.get("resolution_notes", "")

        if not resolution_notes:
            return Response({"error": "Resolution notes are required."}, status=status.HTTP_400_BAD_REQUEST)

        dispute.status = "resolved"
        dispute.resolution_notes = resolution_notes
        dispute.save()

        SuperadminLog.objects.create(
            superadmin=request.user,
            action_type="dispute_resolved",
            action_details=f"Resolved dispute #{dispute.id} on order #{dispute.order.id}."
        )

        send_notification(
            dispute.raised_by, 
            "Dispute Resolved", 
            f"Your dispute on order #{dispute.order.id} has been resolved."
        )

        return Response({"message": "Dispute resolved successfully."}, status=status.HTTP_200_OK)
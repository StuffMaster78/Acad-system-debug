from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import OrderMessage, DisputeMessage, OrderMessageThread, OrderMessageNotification, ScreenedWord, FlaggedMessage
from .serializers import (
    OrderMessageSerializer, OrderMessageThreadSerializer, 
    OrderMessageNotificationSerializer, ScreenedWordSerializer,
    FlaggedMessageSerializer, AdminReviewSerializer,
    AdminEditFlaggedMessageSerializer, DisputeMessageSerializer
)
from .permissions import IsAdminOrOwner, CanSendOrderMessage


class OrderMessageThreadViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing order message threads.
    """
    queryset = OrderMessageThread.objects.all()
    serializer_class = OrderMessageThreadSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrderMessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for sending and retrieving order messages.
    Only returns messages related to the authenticated user.
    """
    serializer_class = OrderMessageSerializer
    permission_classes = [permissions.IsAuthenticated, CanSendOrderMessage, IsAdminOrOwner]

    def get_queryset(self):
        """
        Returns only messages related to the authenticated user.
        """
        user = self.request.user
        return OrderMessage.objects.filter(
            thread__order__client=user
        ) | OrderMessage.objects.filter(
            thread__order__writer=user
        ) | OrderMessage.objects.filter(
            sender=user
        )


    def perform_create(self, serializer):
        """Attach sender information before saving."""
        serializer.save(sender=self.request.user, sender_role=self.request.user.profile.role)


class OrderMessageNotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing message notifications.
    """
    serializer_class = OrderMessageNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only notifications for the logged-in user."""
        return OrderMessageNotification.objects.filter(recipient=self.request.user)


class ScreenedWordViewSet(viewsets.ModelViewSet):
    """
    API endpoint for admin-controlled banned words.
    """
    queryset = ScreenedWord.objects.all()
    serializer_class = ScreenedWordSerializer
    permission_classes = [permissions.IsAdminUser]


class FlaggedMessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint to retrieve and manage flagged messages.
    Only accessible by admins.
    """
    queryset = FlaggedMessage.objects.all().order_by("-flagged_at")
    serializer_class = FlaggedMessageSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admins can access

    @action(detail=True, methods=["PATCH"])
    def update_category(self, request, pk=None):
        """
        Allows admins to update the category of a flagged message.
        """
        flagged_message = self.get_object()
        category = request.data.get("category")

        if category not in dict(FlaggedMessage.CATEGORY_CHOICES):
            return Response({"error": "Invalid category choice."}, status=status.HTTP_400_BAD_REQUEST)

        flagged_message.category = category
        flagged_message.save()

        return Response({"detail": f"Category updated to {flagged_message.get_category_display()}."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"])
    def statistics(self, request):
        """
        Returns statistics about flagged messages.
        """
        total_flagged = FlaggedMessage.objects.count()
        total_reviewed = FlaggedMessage.objects.filter(reviewed_by__isnull=False).count()
        total_pending = total_flagged - total_reviewed

        return Response({
            "total_flagged": total_flagged,
            "total_reviewed": total_reviewed,
            "total_pending": total_pending
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=["POST"])
    def unblock(self, request, pk=None):
        """
        Admin manually unblocks a flagged message with a comment.
        """
        flagged_message = self.get_object()
        serializer = AdminReviewSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            flagged_message.admin_comment = serializer.validated_data.get("admin_comment", "")
            flagged_message.reviewed_by = request.user
            flagged_message.reviewed_at = flagged_message.reviewed_at or flagged_message.flagged_at
            flagged_message.is_unblocked = True
            flagged_message.save()
            return Response({"detail": "Message has been unblocked successfully."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["PATCH"])
    def edit(self, request, pk=None):
        """
        Allows admins to edit flagged messages.
        """
        flagged_message = self.get_object()
        serializer = AdminEditFlaggedMessageSerializer(flagged_message, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Flagged message updated successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["POST"])
    def reflag(self, request, pk=None):
        """
        Admin manually re-flags a message that was previously unblocked.
        """
        flagged_message = self.get_object()

        if flagged_message.is_unblocked:
            flagged_message.is_unblocked = False
            flagged_message.reviewed_by = None
            flagged_message.reviewed_at = None
            flagged_message.admin_comment = "Message re-flagged by admin."
            flagged_message.save()
            return Response({"detail": "Message has been re-flagged successfully."}, status=status.HTTP_200_OK)

        return Response({"detail": "This message is already flagged."}, status=status.HTTP_400_BAD_REQUEST)
    

class DisputeMessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint to manage dispute messages.
    Admins can resolve and update dispute messages.
    """
    queryset = DisputeMessage.objects.all()
    serializer_class = DisputeMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrOwner]

    def perform_create(self, serializer):
        """Attach sender information before saving."""
        serializer.save(sender=self.request.user, sender_role=self.request.user.profile.role)

    @action(detail=True, methods=["POST"])
    def resolve(self, request, pk=None):
        """
        Admin resolves a dispute message.
        """
        dispute_message = self.get_object()
        resolution_comment = request.data.get("resolution_comment", "")

        if not resolution_comment:
            return Response({"error": "Resolution comment is required."}, status=status.HTTP_400_BAD_REQUEST)

        dispute_message.resolve(admin_user=request.user, resolution_comment=resolution_comment)

        return Response({"detail": "Dispute message resolved successfully."}, status=status.HTTP_200_OK)
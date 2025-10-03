from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import (
    CommunicationMessage, DisputeMessage,
    CommunicationThread, CommunicationNotification,
    ScreenedWord, FlaggedMessage, CommunicationLog,
    WebSocketAuditLog, SystemAlert
)
from .services.communication_guard import CommunicationGuardService
from .services.messages import MessageService
from .services.notification_service import NotificationService
from .services.thread_service import ThreadService

from .serializers import (
    CommunicationMessageSerializer, CommunicationThreadSerializer, 
    CommunicationNotificationSerializer, ScreenedWordSerializer,
    FlaggedMessageSerializer, AdminReviewSerializer,
    AdminEditFlaggedMessageSerializer, DisputeMessageSerializer,
    CommunicationThreadSerializer, CommunicationMessageSerializer,
    CommunicationLogSerializer, WebSocketAuditLogSerializer,
    OrderMessageNotificationSerializer
)
from .permissions import IsAdminOrOwner, CanSendOrderMessage
from rest_framework.throttling import UserRateThrottle
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from communications.throttles import AuditLogThrottle
from rest_framework.permissions import IsAuthenticated
from communications.permissions import IsSuperAdmin
from .throttles import SuperAdminAuditThrottle


class MessageThrottle(UserRateThrottle):
    rate = '10/min'

class CommunicationThreadViewSet(viewsets.ModelViewSet):
    queryset = CommunicationThread.objects.all()
    serializer_class = CommunicationThreadSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [MessageThrottle]

    def perform_create(self, serializer):
        order = serializer.validated_data["order"]
        participants = serializer.validated_data["participants"]
        created_by = self.request.user

        # Check thread creation permission
        if not created_by.profile.role in ["admin", "superadmin"]:
            ThreadService.assert_can_create_thread(order)

        # Actually create the thread
        thread = ThreadService.create_thread(
            order=order,
            created_by=created_by,
            participants=participants
        )
        return Response(
            CommunicationThreadSerializer(thread).data,
            status=status.HTTP_201_CREATED
        )


class CommunicationMessageViewSet(viewsets.ModelViewSet):
    queryset = CommunicationMessage.objects.all()
    serializer_class = CommunicationMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        thread_id = self.kwargs.get("thread_pk")
        thread = CommunicationThread.objects.get(pk=thread_id)
        return MessageService.get_visible_messages(self.request.user, thread)

    def perform_create(self, serializer):
        thread_id = self.kwargs.get("thread_pk")
        thread = CommunicationThread.objects.get(pk=thread_id)
        sender = self.request.user
        recipient = serializer.validated_data["recipient"]
        message = serializer.validated_data["message"]
        reply_to = serializer.validated_data.get("reply_to")
        message_type = serializer.validated_data.get("message_type", "text")
        sender_role = getattr(sender.profile, "role", None)

        # 💥 Guard message creation
        CommunicationGuardService.assert_can_send_message(sender, thread)

        # ✍️ Create via service
        msg = MessageService.create_message(
            thread=thread,
            sender=sender,
            recipient=recipient,
            sender_role=sender_role,
            message=message,
            reply_to=reply_to,
            message_type=message_type
        )
        return Response(
            CommunicationMessageSerializer(msg).data,
            status=status.HTTP_201_CREATED
        )


class OrderMessageNotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing message notifications.
    """
    serializer_class = OrderMessageNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return only notifications for the logged-in user."""
        return CommunicationNotification.objects.filter(recipient=self.request.user)


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


class MessageAttachmentUploadView(APIView):
    
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated]
    

    def post(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        file = request.FILES.get("file")
        thread_id = request.data.get("thread_id")
        recipient_id = request.data.get("recipient_id")

        if not all([file, thread_id, recipient_id]):
            return Response({"error": "Missing fields."},
                            status=status.HTTP_400_BAD_REQUEST)

        thread = CommunicationThread.objects.get(id=thread_id)
        recipient = User.objects.get(id=recipient_id)
        sender = request.user

        msg = MessageService.create_message(
            thread=thread,
            sender=sender,
            recipient=recipient,
            message=f"[Attachment: {file.name}]",
            message_type="attachment",
            attachment_file=file,
            sender_role=getattr(sender.profile, "role", None),
        )

        # Send notification via socket layer too, if needed
        return Response(CommunicationMessageSerializer(msg).data,
                        status=status.HTTP_201_CREATED)
    




class CommunicationLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = CommunicationLog.objects.all().order_by("-timestamp")
    serializer_class = CommunicationLogSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [AuditLogThrottle]

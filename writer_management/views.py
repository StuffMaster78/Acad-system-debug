from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from .models import (
    WriterProfile, WriterLevel, WriterConfig,
    WriterOrderRequest, WriterOrderTake,
    WriterPayoutPreference, WriterPayment,
    WriterEarningsHistory, WriterEarningsReviewRequest,
    WriterReward, WriterRewardCriteria, Probation,
    WriterPenalty, WriterSuspension,
    WriterActionLog, WriterSupportTicket,
    WriterDeadlineExtensionRequest, WriterOrderHoldRequest,
    WriterOrderReopenRequest, WriterActivityLog,
    WriterRatingCooldown, WriterFileDownloadLog,
    WriterIPLog, OrderDispute
)
from orders.models import Order
from .serializers import (
    WebhookSettingsSerializer, WriterProfileSerializer, WriterLevelSerializer,
    WriterConfigSerializer, WriterOrderRequestSerializer,
    WriterOrderTakeSerializer, WriterPayoutPreferenceSerializer,
    WriterPaymentSerializer, WriterEarningsHistorySerializer,
    WriterEarningsReviewRequestSerializer, WriterRewardSerializer,
    WriterRewardCriteriaSerializer, ProbationSerializer,
    WriterPenaltySerializer, WriterSuspensionSerializer,
    WriterActionLogSerializer, WriterSupportTicketSerializer,
    WriterDeadlineExtensionRequestSerializer,
    WriterOrderHoldRequestSerializer,
    WriterOrderReopenRequestSerializer,
    WriterActivityLogSerializer, WriterRatingCooldownSerializer,
    WriterFileDownloadLogSerializer, WriterIPLogSerializer,
    OrderDisputeSerializer
)
from writer_management.models import WebhookSettings
from writer_management.serializers import (
WebhookSettingsSerializer
)
from writer_management.services.webhook_settings_service import (
    WebhookSettingsService
)

from core.utils.notifications import send_notification 
from writer_management.serializers import TipCreateSerializer
from writer_management.models import Tip
from writer_management.serializers import TipListSerializer
from writer_management.services.tip_service import TipService
from rest_framework import generics 

### ---------------- Writer Profile Views ---------------- ###

class WriterProfileViewSet(viewsets.ModelViewSet):
    """
    Manage Writer Profiles.
    """
    queryset = WriterProfile.objects.all()
    serializer_class = WriterProfileSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=['GET'], permission_classes=[permissions.IsAdminUser])
    def earnings(self, request, pk=None):
        """
        Retrieve a writer's earnings history.
        """
        writer = self.get_object()
        earnings = WriterEarningsHistory.objects.filter(writer=writer)
        serializer = WriterEarningsHistorySerializer(earnings, many=True)
        return Response(serializer.data)


### ---------------- Admin Configuration Views ---------------- ###

class WriterConfigViewSet(viewsets.ModelViewSet):
    """
    Manage global Writer Configurations (Enable/Disable Takes).
    """
    queryset = WriterConfig.objects.all()
    serializer_class = WriterConfigSerializer
    permission_classes = [permissions.IsAdminUser]


### ---------------- Order Request & Take Views ---------------- ###

class WriterOrderRequestViewSet(viewsets.ModelViewSet):
    """
    Writers can request an order. Admins must approve.
    """
    queryset = WriterOrderRequest.objects.all()
    serializer_class = WriterOrderRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Validate and save writer order requests.
        """
        writer = self.request.user.writer_profile
        config = WriterConfig.objects.first()
        max_requests = config.max_requests_per_writer
        active_requests = WriterOrderRequest.objects.filter(writer=writer, approved=False).count()

        if active_requests >= max_requests:
            raise ValidationError("Max request limit reached.")

        serializer.save(writer=writer)

    @action(detail=True, methods=['POST'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        """
        Admin approves a writer's order request.
        """
        request_obj = self.get_object()
        request_obj.approved = True
        request_obj.save()
        return Response({"message": "Order request approved."}, status=status.HTTP_200_OK)


class WriterOrderTakeViewSet(viewsets.ModelViewSet):
    """
    Writers can take orders directly if admin allows.
    """
    queryset = WriterOrderTake.objects.all()
    serializer_class = WriterOrderTakeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Validate and allow a writer to take an order.
        """
        writer = self.request.user.writer_profile
        config = WriterConfig.objects.first()
        if not config.takes_enabled:
            raise ValidationError("Taking orders is disabled.")

        max_allowed_orders = writer.writer_level.max_orders if writer.writer_level else 0
        current_taken_orders = WriterOrderTake.objects.filter(writer=writer).count()

        if current_taken_orders >= max_allowed_orders:
            raise ValidationError("You have reached your max take limit.")

        serializer.save(writer=writer)


### ---------------- Payment & Earnings Views ---------------- ###

class WriterPayoutPreferenceViewSet(viewsets.ModelViewSet):
    """
    API View for Admins to manage writer payout preferences.
    """
    queryset = WriterPayoutPreference.objects.all()
    serializer_class = WriterPayoutPreferenceSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admins can manage this

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Admin can approve a writer's payout method"""
        payout_method = get_object_or_404(WriterPayoutPreference, pk=pk)
        payout_method.verified = True
        payout_method.save()

        # Send notification to writer
        send_notification(
            user=payout_method.writer.user,
            title="Payout Method Approved",
            message=f"Your {payout_method.preferred_method} payout method has been approved!"
        )

        return Response({"message": "Payout method approved successfully!"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Admin can reject a writer's payout method"""
        payout_method = get_object_or_404(WriterPayoutPreference, pk=pk)
        payout_method.verified = False
        payout_method.save()

        # Send notification to writer
        send_notification(
            user=payout_method.writer.user,
            title="Payout Method Rejected",
            message=f"Your {payout_method.preferred_method} payout method was rejected. Please update it."
        )

        return Response({"message": "Payout method rejected!"}, status=status.HTTP_200_OK)


class WriterPaymentViewSet(viewsets.ModelViewSet):
    """
    Manage Payments to Writers.
    """
    queryset = WriterPayment.objects.all()
    serializer_class = WriterPaymentSerializer
    permission_classes = [permissions.IsAdminUser]


### ---------------- Writer Penalty & Reward Views ---------------- ###

class WriterPenaltyViewSet(viewsets.ModelViewSet):
    """
    Manage Writer Penalties.
    """
    queryset = WriterPenalty.objects.all()
    serializer_class = WriterPenaltySerializer
    permission_classes = [permissions.IsAdminUser]


class WriterRewardViewSet(viewsets.ModelViewSet):
    """
    Manage Writer Rewards.
    """
    queryset = WriterReward.objects.all()
    serializer_class = WriterRewardSerializer
    permission_classes = [permissions.IsAdminUser]


class ProbationViewSet(viewsets.ModelViewSet):
    """
    Manage Writer Probations.
    """
    queryset = Probation.objects.all()
    serializer_class = ProbationSerializer
    permission_classes = [permissions.IsAdminUser]


### ---------------- Support, Disputes & Requests ---------------- ###

class WriterSupportTicketViewSet(viewsets.ModelViewSet):
    """
    Writers can submit support tickets.
    """
    queryset = WriterSupportTicket.objects.all()
    serializer_class = WriterSupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]


class OrderDisputeViewSet(viewsets.ModelViewSet):
    """
    Writers can dispute an order.
    Admins resolve disputes.
    """
    queryset = OrderDispute.objects.all()
    serializer_class = OrderDisputeSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['POST'])
    def resolve_dispute(self, request, pk=None):
        """
        Admins can resolve disputes.
        """
        dispute = get_object_or_404(OrderDispute, pk=pk)
        dispute.resolved = True
        dispute.resolution_notes = request.data.get('resolution_notes', '')
        dispute.resolved_by = request.user
        dispute.save()
        return Response({"message": "Dispute resolved successfully."})


### ---------------- Writer Activity Logs ---------------- ###

class WriterActivityLogViewSet(viewsets.ModelViewSet):
    """
    Track Writer Activity Logs.
    """
    queryset = WriterActivityLog.objects.all()
    serializer_class = WriterActivityLogSerializer
    permission_classes = [permissions.IsAdminUser]


class WriterIPLogViewSet(viewsets.ModelViewSet):
    """
    Track Writer IP Logs.
    """
    queryset = WriterIPLog.objects.all()
    serializer_class = WriterIPLogSerializer
    permission_classes = [permissions.IsAdminUser]


class WriterRatingCooldownViewSet(viewsets.ModelViewSet):
    """
    Manage Writer Rating Cooldowns.
    """
    queryset = WriterRatingCooldown.objects.all()
    serializer_class = WriterRatingCooldownSerializer
    permission_classes = [permissions.IsAdminUser]


class WriterFileDownloadLogViewSet(viewsets.ModelViewSet):
    """
    Track Writer File Downloads.
    """
    queryset = WriterFileDownloadLog.objects.all()
    serializer_class = WriterFileDownloadLogSerializer
    permission_classes = [permissions.IsAdminUser]


class WriterLevelViewSet(viewsets.ModelViewSet):
    queryset = WriterLevel.objects.all()
    serializer_class = WriterLevelSerializer

class WriterEarningsHistoryViewSet(viewsets.ModelViewSet):
    queryset = WriterEarningsHistory.objects.all()
    serializer_class = WriterEarningsHistorySerializer

class WriterEarningsReviewRequestViewSet(viewsets.ModelViewSet):
    queryset = WriterEarningsReviewRequest.objects.all()
    serializer_class = WriterEarningsReviewRequestSerializer

class WriterRewardCriteriaViewSet(viewsets.ModelViewSet):
    queryset = WriterRewardCriteria.objects.all()
    serializer_class = WriterRewardCriteriaSerializer

class WriterSuspensionViewSet(viewsets.ModelViewSet):
    queryset = WriterSuspension.objects.all()
    serializer_class = WriterSuspensionSerializer


class WriterSuspensionViewSet(viewsets.ModelViewSet):
    queryset = WriterSuspension.objects.all()
    serializer_class = WriterSuspensionSerializer
class WriterActionLogViewSet(viewsets.ModelViewSet):
    queryset = WriterActionLog.objects.all()
    serializer_class = WriterActionLogSerializer


class WriterSupportTicketViewSet(viewsets.ModelViewSet):
    queryset = WriterSupportTicket.objects.all()
    serializer_class = WriterSupportTicketSerializer

class WriterDeadlineExtensionRequestViewSet(viewsets.ModelViewSet):
    queryset = WriterDeadlineExtensionRequest.objects.all()
    serializer_class = WriterDeadlineExtensionRequestSerializer


class WriterOrderHoldRequestViewSet(viewsets.ModelViewSet):
    queryset = WriterOrderHoldRequest.objects.all()
    serializer_class = WriterOrderHoldRequestSerializer

class WriterOrderReopenRequestViewSet(viewsets.ModelViewSet):
    queryset = WriterOrderReopenRequest.objects.all()
    serializer_class = WriterOrderReopenRequestSerializer


class WebhookSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing a writer's WebhookSettings.
    """
    queryset = WebhookSettings.objects.all()
    serializer_class = WebhookSettingsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WebhookSettings.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, website=self.request.user.website)

    @action(detail=True, methods=["post"], url_path="test", url_name="test-webhook")
    def test_webhook(self, request, pk=None):
        """
        Sends a test payload to the writer's webhook URL.
        """
        webhook_setting = self.get_object()
        try:
            WebhookSettingsService.send_test_payload(webhook_setting)
            return Response({"detail": "Test webhook sent successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class TipCreateView(generics.CreateAPIView):
    serializer_class = TipCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Tip.objects.filter(client=self.request.user)
    

class TipListView(generics.ListAPIView):
    serializer_class = TipListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        website = self.request.website  # For multitenancy filter

        if user.role == "client":
            return Tip.objects.filter(client=user, website=website).select_related("writer", "order")
        elif user.role == "writer":
            return Tip.objects.filter(writer=user, website=website).select_related("client", "order")
        else:
            return Tip.objects.none()
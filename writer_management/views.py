from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from .models import (
    WriterProfile, WriterLevel, WriterConfig, WriterOrderRequest, WriterOrderTake,
    WriterPayoutPreference, WriterPayment, PaymentHistory, WriterEarningsHistory,
    WriterEarningsReviewRequest, WriterReward, WriterRewardCriteria, Probation,
    WriterPenalty, WriterSuspension, WriterActionLog, WriterSupportTicket,
    WriterDeadlineExtensionRequest, WriterOrderHoldRequest, WriterOrderReopenRequest,
    WriterActivityLog, WriterRatingCooldown, WriterFileDownloadLog, WriterIPLog, OrderDispute
)
from orders.models import Order
from .serializers import (
    WriterProfileSerializer, WriterLevelSerializer, WriterConfigSerializer,
    WriterOrderRequestSerializer, WriterOrderTakeSerializer, WriterPayoutPreferenceSerializer,
    WriterPaymentSerializer, PaymentHistorySerializer, WriterEarningsHistorySerializer,
    WriterEarningsReviewRequestSerializer, WriterRewardSerializer, WriterRewardCriteriaSerializer,
    ProbationSerializer, WriterPenaltySerializer, WriterSuspensionSerializer, WriterActionLogSerializer,
    WriterSupportTicketSerializer, WriterDeadlineExtensionRequestSerializer,
    WriterOrderHoldRequestSerializer, WriterOrderReopenRequestSerializer,
    WriterActivityLogSerializer, WriterRatingCooldownSerializer, WriterFileDownloadLogSerializer, WriterIPLogSerializer,
    OrderDisputeSerializer
)


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
    Manage Writer Payout Preferences.
    """
    queryset = WriterPayoutPreference.objects.all()
    serializer_class = WriterPayoutPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]


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
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend # type: ignore
from django.db.models import Q
from writer_management.models.levels import (
    WriterLevel, WriterLevelHistory
)
from writer_management.models.configs import WriterConfig
from writer_management.models.messages import (
    WriterMessageThread, WriterMessage
)
from writer_management.models.status import WriterStatus
from writer_management.models.webhook_settings import (
    WebhookSettings, WebhookPlatform
)
from writer_management.models.requests import (
    WriterOrderRequest, WriterOrderTake, WriterDeadlineExtensionRequest,
    WriterOrderHoldRequest, WriterOrderReopenRequest,
    WriterEarningsReviewRequest
)
from writer_management.models.payout import (
    WriterPayoutPreference, WriterPayment,
    WriterEarningsHistory
)

from writer_management.models.rewards import ( 
    WriterReward, WriterRewardCriteria
)
# from writer_management.models.discipline import (
#     WriterStrike, WriterSuspension, WriterBlacklist, Probation
# )
from writer_management.models.performance_snapshot import (
    WriterPerformanceSnapshot
)

from writer_management.models.discipline import (
    WriterSuspension,   WriterBlacklist,
    WriterBlacklistHistory, WriterDisciplineConfig,
    WriterPenalty, Probation, WriterStrike, WriterStrikeHistory,
    WriterSuspensionHistory
)
from writer_management.models.logs import (
    WriterActivityLog
)

from writer_management.models.logs import (
    WriterActionLog, WriterIPLog, WriterFileDownloadLog
)

from writer_management.models.ratings import (
    WriterRating, WriterRatingCooldown
)
from writer_management.models.requests import (
    WriterOrderRequest, WriterOrderTake, WriterDeadlineExtensionRequest,
    WriterOrderHoldRequest, WriterOrderReopenRequest
)

from writer_management.models.tickets import (
    WriterSupportTicket
)

from orders.models import Order
from writer_management.models.order_dispute import OrderDispute
from .serializers import (
    WebhookSettingsSerializer, WriterProfileSerializer, WriterLevelSerializer,
    WriterConfigSerializer, WriterLevelConfigSerializer, WriterOrderRequestSerializer,
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
    OrderDisputeSerializer, CurrencyConversionRateSerializer,
    WriterPaymentSerializer, WriterPerformanceSnapshotSerializer,
    WriterPerformanceSummarySerializer, WriterLevelHistorySerializer,
    WriterBadgeSerializer,
)

from writer_management.serializers import (
WebhookSettingsSerializer
)
from writer_management.services.webhook_settings_service import (
    WebhookSettingsService
)
from writer_management.models.payout import CurrencyConversionRate
from writer_management.services.payment_service import WriterPaymentService
from decimal import Decimal
from core.utils.notifications import send_notification 
from writer_management.serializers import TipCreateSerializer
from writer_management.models.tipping import Tip
from writer_management.serializers import TipListSerializer
from writer_management.services.tip_service import TipService
from rest_framework import generics 
from rest_framework.views import APIView
from writer_management.models.profile import WriterProfile
from writer_management.serializers import WriterStatusSerializer
from writer_management.services.status_service import WriterStatusService
from writer_management.models.performance_snapshot import WriterPerformanceSnapshot
from writer_management.serializers import (
    WriterPerformanceSnapshotSerializer, WriterWarningSelfViewSerializer
)
from rest_framework.permissions import IsAdminUser
from writer_management.serializers import WriterLevelSerializer
from writer_management.models.writer_warnings import WriterWarning
from writer_management.serializers import WriterWarningSerializer
from writer_management.services.writer_warning_service import (
    WriterWarningService
)
from django.db.models import Q

from rest_framework import viewsets, filters
from rest_framework.permissions import IsAdminUser
from writer_management.models.badges import WriterBadge
from writer_management.serializers import WriterBadgeSerializer
from writer_management.models.profile import WriterProfile
from writer_management.serializers import (
    WriterBadgeTimelineSerializer
)
from rest_framework.response import Response
from collections import defaultdict

from notifications_system.services.dispatch import send

### ---------------- Writer Profile Views ---------------- ###

class IsWriter(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "writer"
class WriterProfileViewSet(viewsets.ModelViewSet):
    """
    Manage Writer Profiles.
    """
    queryset = WriterProfile.objects.all()
    serializer_class = WriterProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_permissions(self):
        """
        Allow writers to update their own profile (specifically pen_name).
        """
        if self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]
    
    def get_queryset(self):
        """
        Writers can only access their own profile.
        """
        if self.request.user.role == 'writer':
            return WriterProfile.objects.filter(user=self.request.user)
        return WriterProfile.objects.all()
    
    def update(self, request, *args, **kwargs):
        """
        Allow writers to update their pen_name.
        """
        instance = self.get_object()
        
        # Writers can only update their own profile
        if request.user.role == 'writer' and instance.user != request.user:
            return Response(
                {"error": "You can only update your own profile."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # For writers, only allow updating pen_name
        if request.user.role == 'writer':
            pen_name = request.data.get('pen_name')
            if pen_name is not None:
                instance.pen_name = pen_name
                instance.save(update_fields=['pen_name'])
                serializer = self.get_serializer(instance)
                return Response(serializer.data)
            return Response(
                {"error": "Only pen_name can be updated."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Admins can update everything
        return super().update(request, *args, **kwargs)

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


class WriterLevelConfigViewSet(viewsets.ModelViewSet):
    """
    Manage Writer Level Configurations (criteria-based levels).
    """
    queryset = WriterLevelConfig.objects.all()
    serializer_class = WriterLevelConfigSerializer
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


class WriterPaymentViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]

    def list(self, request):
        payments = WriterPayment.objects.select_related("writer", "website").order_by("-payment_date")
        serializer = WriterPaymentSerializer(payments, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            payment = WriterPayment.objects.get(pk=pk)
        except WriterPayment.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)
        serializer = WriterPaymentSerializer(payment)
        return Response(serializer.data)

    def create(self, request):
        data = request.data.copy()
        serializer = WriterPaymentSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        writer = serializer.validated_data["writer"]
        website = serializer.validated_data["website"]
        amount = serializer.validated_data["amount"]
        bonuses = serializer.validated_data.get("bonuses", Decimal("0.00"))
        fines = serializer.validated_data.get("fines", Decimal("0.00"))
        tips = serializer.validated_data.get("tips", Decimal("0.00"))
        currency = request.data.get("currency", "USD")
        convert = request.data.get("convert_to_local", False)

        payment = WriterPaymentService.create_payment(
            writer=writer,
            website=website,
            amount_usd=amount,
            bonuses=bonuses,
            fines=fines,
            tips=tips,
            currency=currency,
            convert_to_local=convert,
            description=serializer.validated_data.get("description", ""),
            actor=request.user
        )

        return Response(WriterPaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


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
        


class CurrencyConversionRateViewSet(viewsets.ModelViewSet):
    """
    Admin-only view for managing USD → Local currency conversion rates.
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = CurrencyConversionRateSerializer
    queryset = CurrencyConversionRate.objects.all().order_by(
        "-effective_date", "target_currency"
    )

    def get_queryset(self):
        """
        Optionally filter by website.
        """
        queryset = super().get_queryset()
        website_id = self.request.query_params.get("website_id")
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        return queryset
    


class CurrencyConversionRateViewSet(viewsets.ModelViewSet):
    """
    Admin-only view for managing USD → Local currency conversion rates.
    """
    permission_classes = [permissions.IsAdminUser]
    serializer_class = CurrencyConversionRateSerializer
    queryset = CurrencyConversionRate.objects.all().order_by(
        "-effective_date", "target_currency"
    )

    def get_queryset(self):
        """
        Optionally filter by website.
        """
        queryset = super().get_queryset()
        website_id = self.request.query_params.get("website_id")
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        return queryset
    

class WriterStatusViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = WriterStatus.objects.all()
        return qs.order_by("-active_strikes", "-updated_at")

    def list(self, request):
        queryset = self.get_queryset()
        serializer = WriterStatusSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        GET /api/writer-status/{writer_id}/
        Admins can query any writer's status.
        Writers can only see their own.
        """
        try:
            writer = WriterProfile.objects.get(pk=pk)
        except WriterProfile.DoesNotExist:
            return Response(
                {"detail": "Writer not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.user != writer.user and not request.user.is_staff:
            return Response(
                {"detail": "Permission denied."},
                status=status.HTTP_403_FORBIDDEN
            )

        WriterStatusService.update(writer)
        serializer = WriterStatusSerializer(writer.status)
        return Response(serializer.data)

    def update(self, request, pk=None):
        """
        PUT /api/writer-status/{writer_id}/
        Forces a refresh of the status. Admin-only.
        """
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can refresh writer status."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            writer = WriterProfile.objects.get(pk=pk)
        except WriterProfile.DoesNotExist:
            return Response(
                {"detail": "Writer not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        WriterStatusService.update(writer)
        serializer = WriterStatusSerializer(writer.status)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        """
        GET /api/writer-status/me/
        Self status for the current authenticated writer.
        """
        try:
            writer = WriterProfile.objects.get(user=request.user)
        except WriterProfile.DoesNotExist:
            return Response(
                {"detail": "No writer profile found."},
                status=status.HTTP_404_NOT_FOUND
            )

        WriterStatusService.update(writer)
        serializer = WriterStatusSerializer(writer.status)
        return Response(serializer.data)


    def list(self, request):
        """
        GET /api/writer-status/
        Admins can list writer statuses with filters.
        """
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can access list."},
                status=status.HTTP_403_FORBIDDEN
            )

        qs = WriterStatus.objects.select_related("writer", "writer__user")

        # Optional query params
        is_suspended = request.query_params.get("suspended")
        is_blacklisted = request.query_params.get("blacklisted")
        min_strikes = request.query_params.get("min_strikes")
        on_probation = request.query_params.get("probation")
        auto_susp = request.query_params.get("auto_flagged")

        if is_suspended in ["true", "1"]:
            qs = qs.filter(is_suspended=True)

        if is_blacklisted in ["true", "1"]:
            qs = qs.filter(is_blacklisted=True)

        if min_strikes:
            qs = qs.filter(active_strikes__gte=int(min_strikes))

        if on_probation in ["true", "1"]:
            qs = qs.filter(is_on_probation=True)

        if auto_susp in ["true", "1"]:
            qs = qs.filter(should_be_suspended=True)

        serializer = WriterStatusSerializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["patch"], url_path="toggle-flag")
    def toggle_flag(self, request, pk=None):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can toggle flags."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            status_obj = WriterStatus.objects.get(pk=pk)
        except WriterStatus.DoesNotExist:
            return Response(
                {"detail": "Writer status not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        flag = request.data.get("flag")
        if flag not in ["should_be_suspended", "should_be_probated"]:
            return Response(
                {"detail": "Invalid flag provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Toggle the flag
        current = getattr(status_obj, flag)
        setattr(status_obj, flag, not current)
        status_obj.save(update_fields=[flag])

        return Response(
            {"detail": f"{flag} set to {not current}"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=["post"], url_path="bulk-notify")
    def bulk_notify(self, request):
        if not request.user.is_staff:
            return Response(
                {"detail": "Only admins can send notifications."},
                status=status.HTTP_403_FORBIDDEN
            )

        reason = request.data.get("reason")
        flag = request.data.get("flag")

        if flag not in ["should_be_suspended", "should_be_probated"]:
            return Response(
                {"detail": "Invalid flag type."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not reason:
            return Response(
                {"detail": "Notification reason is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        qs = WriterStatus.objects.filter(**{flag: True}).select_related("writer__user")

        notified = 0
        for status_obj in qs:
            writer_user = status_obj.writer.user
            send(
                user=writer_user,
                title="Account Warning",
                message=reason,
                category="writer_status_flag",
                metadata={"flag": flag},
                immediate=True
            )

            notified += 1

        return Response(
            {"detail": f"Notified {notified} writers."},
            status=status.HTTP_200_OK
        )
    

class WriterDashboardStatusView(APIView):
    def get(self, request):
        try:
            writer = WriterProfile.objects.get(user=request.user)
        except WriterProfile.DoesNotExist:
            return Response({"detail": "Writer not found."}, status=404)

        status = WriterStatusService.get(writer)

        return Response({
            "status": "restricted" if not status["is_active"] else "ok",
            "flags": {
                "suspended": status["is_suspended"],
                "blacklisted": status["is_blacklisted"],
                "on_probation": status["is_on_probation"],
                "strikes": status["active_strikes"],
            }
        })
    

class WriterPerformanceSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet to list or retrieve writer performance snapshots.
    """

    queryset = WriterPerformanceSnapshot.objects.all()
    serializer_class = WriterPerformanceSnapshotSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = [
        "writer", "website", "period_start", "period_end", "is_cached"
    ]
    ordering_fields = [
        "generated_at", "average_rating", "total_orders", "completion_rate"
    ]
    ordering = ["-generated_at"]

class WriterPerformanceDashboardView(generics.RetrieveAPIView):
    serializer_class = WriterPerformanceSummarySerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return (
            WriterPerformanceSnapshot.objects
            .filter(writer__user=self.request.user)
            .order_by("-generated_at")
            .first()
        )
    
class WriterLevelViewSet(viewsets.ModelViewSet):
    queryset = WriterLevel.objects.select_related("writer__user")
    serializer_class = WriterLevelSerializer

    def get_permissions(self):
        if self.action in ["me", "history"]:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_queryset(self):
        qs = super().get_queryset()
        writer_id = self.request.query_params.get("writer_id")
        if writer_id:
            qs = qs.filter(writer_id=writer_id)
        return qs

    @action(detail=False, methods=["get"])
    def me(self, request):
        writer = request.user.writer_profile
        level = WriterLevel.objects.filter(writer=writer).first()
        if not level:
            return Response(
                {"detail": "No level assigned yet."},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(WriterLevelSerializer(level).data)

    @action(detail=False, methods=["get"])
    def history(self, request):
        writer = request.user.writer_profile
        history = WriterLevelHistory.objects.filter(writer=writer)
        return Response(
            WriterLevelHistorySerializer(history, many=True).data
        )
    

class WriterWarningViewSet(viewsets.ModelViewSet):
    queryset = WriterWarning.objects.all().select_related(
        'writer__user', 'issued_by'
    )
    serializer_class = WriterWarningSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['writer', 'is_active']

    def perform_create(self, serializer):
        writer = serializer.validated_data['writer']
        reason = serializer.validated_data['reason']
        expires_at = serializer.validated_data.get('expires_at')

        warning = WriterWarningService.issue_warning(
            writer=writer,
            reason=reason,
            issued_by=self.request.user,
            expires_days=(expires_at - warning.issued_at).days
            if expires_at else 30
        )

        return warning

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(
            {'detail': 'Warning marked as inactive.'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["get"])
    def active(self, request):
        queryset = self.queryset.filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    @action(detail=False, methods=['get'], url_path='mine',
            permission_classes=[IsAuthenticated])
    def my_warnings(self, request):
        profile = request.user.writer_profile
        warnings = WriterWarning.objects.filter(
            writer=profile, is_active=True
        ).order_by('-issued_at')
        serializer = self.get_serializer(warnings, many=True)
        return Response(serializer.data)

class WriterWarningSelfViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WriterWarningSelfViewSerializer
    permission_classes = [permissions.IsAuthenticated, IsWriter]

    def get_queryset(self):
        return WriterWarning.objects.filter(
            writer__user=self.request.user,
            is_active=True
        ).order_by('-created_at')


class WriterBadgeAdminViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = WriterBadge.objects.select_related("writer", "badge")
    serializer_class = WriterBadgeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "badge__name", "writer__user__username",
        "notes", "badge__type"
    ]
    ordering_fields = ["issued_at", "badge__name"]


class WriterBadgeTimelineViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        writer = WriterProfile.objects.get(user=request.user)
        badges = WriterBadge.objects.filter(
            writer=writer
        ).order_by("-issued_at")

        grouped = defaultdict(list)
        for badge in badges:
            date_str = badge.issued_at.strftime("%B %Y")
            grouped[date_str].append(
                WriterBadgeTimelineSerializer(badge).data
            )

        return Response(grouped)
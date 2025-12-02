from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend # type: ignore
from django.db.models import Q
from writer_management.models.levels import (
    WriterLevel, WriterLevelHistory
)
from writer_management.models.configs import WriterConfig, WriterLevelConfig
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
from activity.utils.logger_safe import safe_log_activity
from notifications_system.services.dispatch import send
from notifications_system.enums import NotificationType
from django.contrib.auth import get_user_model

User = get_user_model()
from writer_management.serializers import (
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
    WriterPerformanceSnapshotSerializer, WriterPerformanceSummarySerializer,
    WriterLevelHistorySerializer, WriterBadgeSerializer,
    TipCreateSerializer, TipListSerializer, WriterStatusSerializer,
    WriterWarningSelfViewSerializer, WriterStrikeSerializer,
    WriterStrikeHistorySerializer, WriterDisciplineConfigSerializer,
    WriterWarningSerializer, WriterBadgeTimelineSerializer,
    WriterPenNameChangeRequestSerializer, WriterResourceSerializer,
    WriterResourceCategorySerializer, WriterResourceViewSerializer
)
from writer_management.services.webhook_settings_service import (
    WebhookSettingsService
)
from writer_management.models.payout import CurrencyConversionRate
from writer_management.services.payment_service import WriterPaymentService
from decimal import Decimal
from core.utils.notifications import send_notification 
from writer_management.models.tipping import Tip
from writer_management.services.tip_service import TipService
from rest_framework import generics, viewsets, filters
from rest_framework.views import APIView
from writer_management.models.profile import WriterProfile
from writer_management.services.status_service import WriterStatusService
from writer_management.models.performance_snapshot import WriterPerformanceSnapshot
from rest_framework.permissions import IsAdminUser
from writer_management.models.writer_warnings import WriterWarning
from writer_management.services.writer_warning_service import (
    WriterWarningService,
)
from writer_management.services.discipline_notification_service import (
    DisciplineNotificationService,
)
from django.db.models import Q
from writer_management.models.badges import WriterBadge
try:
    from writer_management.models.pen_name_requests import WriterPenNameChangeRequest
except ImportError:
    WriterPenNameChangeRequest = None
try:
    from writer_management.models.resources import (
        WriterResource, WriterResourceCategory, WriterResourceView
    )
except ImportError:
    WriterResource = None
    WriterResourceCategory = None
    WriterResourceView = None
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
    queryset = WriterProfile.objects.all().select_related(
        'user', 'website', 'writer_level'
    )
    serializer_class = WriterProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_permissions(self):
        """
        Allow writers to update their own profile (specifically pen_name) and view their own profile.
        """
        if self.action in ['update', 'partial_update', 'my_profile']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]
    
    def get_queryset(self):
        """
        Writers can only access their own profile.
        """
        if self.request.user.role == 'writer':
            return WriterProfile.objects.filter(user=self.request.user).select_related(
                'user', 'website', 'writer_level'
            )
        return WriterProfile.objects.all().select_related(
            'user', 'website', 'writer_level'
        )
    
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

    @action(detail=False, methods=['GET'], permission_classes=[permissions.IsAuthenticated])
    def my_profile(self, request):
        """
        Get the current writer's own profile with hierarchy details.
        """
        from websites.models import Website
        
        # Check if user has writer role
        user_role = getattr(request.user, 'role', None)
        if user_role != 'writer':
            return Response(
                {"detail": "This endpoint is only available for writers."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get writer profile - try to get by website if provided, otherwise get first one
        website_id = request.query_params.get('website') or request.headers.get('X-Website')
        
        try:
            if website_id:
                # Try to get profile for specific website
                try:
                    website = Website.objects.get(id=website_id)
                    profile = WriterProfile.objects.get(user=request.user, website=website)
                except (Website.DoesNotExist, WriterProfile.DoesNotExist):
                    # Fallback to any profile for this user
                    profile = WriterProfile.objects.filter(user=request.user).first()
                    if not profile:
                        raise WriterProfile.DoesNotExist
            else:
                # Get first available profile for this user
                profile = WriterProfile.objects.filter(user=request.user).first()
                if not profile:
                    raise WriterProfile.DoesNotExist
        except WriterProfile.DoesNotExist:
            # Safety net: auto‑create a minimal WriterProfile for real writers
            # if one does not exist, similar to how many production systems
            # ensure role/profile consistency.
            from django.conf import settings as dj
            try:
                # Allow tests to disable auto‑creation explicitly
                if getattr(dj, 'DISABLE_AUTO_CREATE_WRITER_PROFILE', False):
                    raise WriterProfile.DoesNotExist
            except Exception:
                pass

            # Try to use the user's website; if missing, fall back to any active site
            website = getattr(request.user, 'website', None)
            if website is None:
                website = Website.objects.filter(is_active=True).first()

            if website is None:
                # Still no website – bail out with a clear error
                return Response(
                    {"detail": "Writer profile not found and no website available to create one."},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Use the custom manager to handle wallet/registration_id defaults
            profile = WriterProfile.objects.create(user=request.user, website=website)
        
        serializer = self.get_serializer(profile)
        data = serializer.data
        
        # Add hierarchy details
        if profile.writer_level:
            from writer_management.services.level_progression import WriterLevelProgressionService
            from writer_management.models.levels import WriterLevel
            
            level = profile.writer_level
            level_data = {
                'id': level.id,
                'name': level.name,
                'description': level.description or '',
                'earning_mode': level.earning_mode,
                'base_pay_per_page': float(level.base_pay_per_page),
                'base_pay_per_slide': float(level.base_pay_per_slide),
                'earnings_percentage_of_cost': float(level.earnings_percentage_of_cost) if level.earnings_percentage_of_cost else None,
                'earnings_percentage_of_total': float(level.earnings_percentage_of_total) if level.earnings_percentage_of_total else None,
                'urgency_percentage_increase': float(level.urgency_percentage_increase),
                'urgency_additional_per_page': float(level.urgency_additional_per_page),
                'urgent_order_deadline_hours': level.urgent_order_deadline_hours,
                'technical_order_adjustment_per_page': float(level.technical_order_adjustment_per_page),
                'technical_order_adjustment_per_slide': float(level.technical_order_adjustment_per_slide),
                'deadline_percentage': float(level.deadline_percentage),
                'tips_percentage': float(level.tips_percentage),
                'max_orders': level.max_orders,
                'bonus_per_order_completed': float(level.bonus_per_order_completed),
                'bonus_per_rating_above_threshold': float(level.bonus_per_rating_above_threshold),
                'rating_threshold_for_bonus': float(level.rating_threshold_for_bonus),
            }
            data['writer_level_details'] = level_data
            
            # Get next level requirements
            next_level_info = WriterLevelProgressionService.get_next_level_requirements(profile)
            if next_level_info:
                data['next_level_info'] = next_level_info
        
        return Response(data)
    
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
    queryset = WriterOrderRequest.objects.all().select_related(
        'writer__user', 'order', 'website'
    ).order_by('-requested_at')
    serializer_class = WriterOrderRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Validate and save writer order requests.
        Prevents duplicates and handles race conditions.
        """
        from django.db import transaction
        from orders.order_enums import OrderStatus
        
        writer = self.request.user.writer_profile
        order = serializer.validated_data.get('order')
        
        if not order:
            raise ValidationError("Order is required.")
        
        # Use select_for_update to prevent race conditions
        with transaction.atomic():
            # Lock the order to prevent concurrent modifications
            order = Order.objects.select_for_update().get(id=order.id)
            
            # Check if order is already requested by this writer
            existing_request = WriterOrderRequest.objects.filter(
                writer=writer,
                order=order
            ).first()
            
            if existing_request:
                if existing_request.approved:
                    raise ValidationError("You have already requested and been approved for this order.")
                else:
                    raise ValidationError("You have already requested this order. Please wait for admin review.")
            
            # Check if order is already assigned to this writer
            if order.assigned_writer == writer.user:
                raise ValidationError("This order is already assigned to you.")
            
            # Check if order is already assigned to another writer
            if order.assigned_writer is not None:
                raise ValidationError("This order is already assigned to another writer.")
            
            # Validate order status - must be available or pending
            if order.status not in [OrderStatus.AVAILABLE.value, OrderStatus.PENDING.value, OrderStatus.PENDING_PREFERRED.value]:
                raise ValidationError(
                    f"This order is not available for requests. Current status: {order.status.replace('_', ' ').title()}"
                )
            
        # Get max requests from writer's level, fallback to WriterConfig if no level
        if writer.writer_level:
            max_requests = writer.writer_level.max_requests_per_writer
        else:
            # Fallback to WriterConfig for writers without a level
            config = WriterConfig.objects.filter(website=writer.website).first()
            max_requests = config.max_requests_per_writer if config else 5
        
            # Count active requests (excluding this one if it exists)
            active_requests = WriterOrderRequest.objects.filter(
                writer=writer,
                approved=False
            ).count()

        if active_requests >= max_requests:
                raise ValidationError(
                    f"You have reached your maximum request limit ({max_requests}). "
                    "Please wait for existing requests to be reviewed or submit work to free up capacity."
                )

            request_instance = serializer.save(writer=writer)
            
            # Log activity
            try:
                safe_log_activity(
                    user=writer.user,
                    website=writer.website,
                    action_type="ORDER",
                    description=f"You requested order #{order.id}",
                    metadata={
                        "order_id": order.id,
                        "request_id": request_instance.id,
                        "reason": request_instance.reason[:200] if request_instance.reason else None,
                    },
                    triggered_by=writer.user,
                )
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Failed to log activity for order request: {e}")
            
            # Notify admins about the new request
            try:
                admin_users = User.objects.filter(
                    role__in=['admin', 'superadmin'],
                    is_active=True
                ).exclude(id=writer.user.id)
                
                # If website-specific, filter by website
                if writer.website:
                    admin_users = admin_users.filter(website=writer.website)
                
                for admin in admin_users[:50]:  # Limit to prevent spam
                    send(
                        user=admin,
                        event="writer.order_request.created",
                        payload={
                            "order_id": order.id,
                            "order_topic": order.topic or "No topic",
                            "writer_id": writer.id,
                            "writer_username": writer.user.username,
                            "request_id": request_instance.id,
                            "reason_preview": request_instance.reason[:100] if request_instance.reason else None,
                        },
                        website=writer.website,
                        channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET],
                        category="order_requests",
                    )
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Failed to notify admins about order request: {e}")
            
            return request_instance

    @action(detail=True, methods=['POST'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        """
        Admin approves a writer's order request.
        Assigns the order to the writer and updates order status.
        """
        from django.db import transaction
        from orders.order_enums import OrderStatus
        from django.utils import timezone
        
        request_obj = self.get_object()
        
        # Check if already approved
        if request_obj.approved:
            return Response(
                {"message": "This request has already been approved."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order = request_obj.order
        writer = request_obj.writer
        
        with transaction.atomic():
            # Lock the order
            order = Order.objects.select_for_update().get(id=order.id)
            
            # Validate order is still available
            if order.assigned_writer is not None:
                return Response(
                    {"error": "This order has already been assigned to another writer."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if order.status not in [OrderStatus.AVAILABLE.value, OrderStatus.PENDING.value, OrderStatus.PENDING_PREFERRED.value]:
                return Response(
                    {"error": f"Order is not available for assignment. Current status: {order.status}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Approve the request
        request_obj.approved = True
            request_obj.reviewed_by = request.user
        request_obj.save()
            
            # Assign the order to the writer
            order.assigned_writer = writer.user
            order.status = OrderStatus.IN_PROGRESS.value
            if hasattr(order, 'assigned_at'):
                order.assigned_at = timezone.now()
            order.save()
            
            # Log activity
            try:
                safe_log_activity(
                    user=writer.user,
                    website=writer.website,
                    action_type="ORDER",
                    description=f"Admin approved your request for order #{order.id}",
                    metadata={
                        "order_id": order.id,
                        "request_id": request_obj.id,
                        "approved_by": request.user.username,
                    },
                    triggered_by=request.user,
                )
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Failed to log activity for order approval: {e}")
            
            # Notify the writer
            try:
                send(
                    user=writer.user,
                    event="writer.order_request.approved",
                    payload={
                        "order_id": order.id,
                        "order_topic": order.topic or "No topic",
                        "request_id": request_obj.id,
                        "approved_by": request.user.username,
                    },
                    website=writer.website,
                    channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET],
                    category="order_requests",
                )
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Failed to notify writer about approval: {e}")
        
        return Response({
            "message": "Order request approved and assigned successfully.",
            "order_id": order.id,
            "assigned_to": writer.user.username
        }, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['POST'], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        """
        Admin rejects a writer's order request with optional feedback.
        """
        request_obj = self.get_object()
        
        # Check if already approved
        if request_obj.approved:
            return Response(
                {"error": "Cannot reject an already approved request."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        feedback = request.data.get('feedback', '')
        writer = request_obj.writer
        order = request_obj.order
        
        # Mark as reviewed (we'll use a custom field or just track via reviewed_by)
        # For now, we'll delete the request or mark it as rejected
        # Since we don't have a rejected field, we'll delete it and log the rejection
        
        # Log activity before deletion
        try:
            safe_log_activity(
                user=writer.user,
                website=writer.website,
                action_type="ORDER",
                description=f"Admin rejected your request for order #{order.id}",
                metadata={
                    "order_id": order.id,
                    "request_id": request_obj.id,
                    "rejected_by": request.user.username,
                    "feedback": feedback[:200] if feedback else None,
                },
                triggered_by=request.user,
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to log activity for order rejection: {e}")
        
        # Notify the writer
        try:
            send(
                user=writer.user,
                event="writer.order_request.rejected",
                payload={
                    "order_id": order.id,
                    "order_topic": order.topic or "No topic",
                    "request_id": request_obj.id,
                    "rejected_by": request.user.username,
                    "feedback": feedback[:500] if feedback else None,
                },
                website=writer.website,
                channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET],
                category="order_requests",
            )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Failed to notify writer about rejection: {e}")
        
        # Delete the request (or you could add a 'rejected' field to the model)
        request_obj.delete()
        
        return Response({
            "message": "Order request rejected.",
            "feedback": feedback if feedback else None
        }, status=status.HTTP_200_OK)


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
        Automatically assigns the order to the writer when taken.
        Prevents duplicates and handles race conditions.
        """
        from django.db import transaction
        from orders.order_enums import OrderStatus
        from orders.models import Order
        
        writer = self.request.user.writer_profile
        order = serializer.validated_data.get('order')
        
        if not order:
            raise ValidationError("Order is required.")
        
        # Use select_for_update to prevent race conditions
        with transaction.atomic():
            # Lock the order to prevent concurrent modifications
            order = Order.objects.select_for_update().get(id=order.id)
            
            # Check if order is already taken by this writer
            existing_take = WriterOrderTake.objects.filter(
                writer=writer,
                order=order
            ).first()
            
            if existing_take:
                raise ValidationError("You have already taken this order.")
            
            # Check if order is already assigned to this writer
            if order.assigned_writer == writer.user:
                raise ValidationError("This order is already assigned to you.")
            
            # Check if order is already assigned to another writer
        if order.assigned_writer is not None:
                raise ValidationError("This order is already assigned to another writer.")
            
            # Validate order status - must be available
            if order.status != OrderStatus.AVAILABLE.value:
                raise ValidationError(
                    f"This order is not available. Current status: {order.status.replace('_', ' ').title()}"
                )
            
            # Check if takes are enabled
            config = WriterConfig.objects.filter(website=writer.website).first()
            if not config or not config.takes_enabled:
                raise ValidationError(
                    "Taking orders directly is currently disabled. Please submit a request instead."
                )

            # Get max allowed orders from writer's level
            max_allowed_orders = writer.writer_level.max_orders if writer.writer_level else 0
            
            if max_allowed_orders <= 0:
                raise ValidationError(
                    "You do not have permission to take orders. Please contact an administrator."
                )
            
            # Count active assignments (in_progress, on_hold, revision_requested, under_editing)
            active_assignments = Order.objects.filter(
                assigned_writer=writer.user,
                status__in=[
                    OrderStatus.IN_PROGRESS.value,
                    OrderStatus.ON_HOLD.value,
                    OrderStatus.REVISION_REQUESTED.value,
                    OrderStatus.UNDER_EDITING.value,
                ]
            ).count()

            if active_assignments >= max_allowed_orders:
                raise ValidationError(
                    f"You have reached your maximum order limit ({max_allowed_orders}). "
                    "Please submit existing work or request a hold before taking another order."
                )
            
            # Create the take record
            take_instance = serializer.save(writer=writer)
            
            # Assign the order to the writer
            order.assigned_writer = writer.user
            order.status = OrderStatus.IN_PROGRESS.value
            if hasattr(order, 'assigned_at'):
                from django.utils import timezone
                order.assigned_at = timezone.now()
            order.save()
            
            # Log activity
            try:
                safe_log_activity(
                    user=writer.user,
                    website=writer.website,
                    action_type="ORDER",
                    description=f"You took order #{order.id}",
                    metadata={
                        "order_id": order.id,
                        "take_id": take_instance.id,
                    },
                    triggered_by=writer.user,
                )
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Failed to log activity for order take: {e}")
            
            # Notify admins about the order take
            try:
                admin_users = User.objects.filter(
                    role__in=['admin', 'superadmin'],
                    is_active=True
                ).exclude(id=writer.user.id)
                
                # If website-specific, filter by website
                if writer.website:
                    admin_users = admin_users.filter(website=writer.website)
                
                for admin in admin_users[:50]:  # Limit to prevent spam
                    send(
                        user=admin,
                        event="writer.order_taken",
                        payload={
                            "order_id": order.id,
                            "order_topic": order.topic or "No topic",
                            "writer_id": writer.id,
                            "writer_username": writer.user.username,
                            "take_id": take_instance.id,
                        },
                        website=writer.website,
                        channels=[NotificationType.IN_APP, NotificationType.WEBSOCKET],
                        category="order_takes",
                    )
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Failed to notify admins about order take: {e}")
            
            return take_instance


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
        payments = WriterPayment.objects.select_related(
            "writer__user", "website", "processed_by"
        ).order_by("-payment_date")
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
    
    @action(detail=True, methods=['get'], url_path='receipt')
    def download_receipt(self, request, pk=None):
        """Download PDF receipt for a writer payment."""
        try:
            payment = WriterPayment.objects.select_related(
                'writer__user', 'website', 'processed_by'
            ).get(pk=pk)
        except WriterPayment.DoesNotExist:
            return Response(
                {"detail": "Payment not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permissions - writers can only download their own receipts
        if request.user.role == 'writer':
            if payment.writer.user != request.user:
                return Response(
                    {"detail": "You can only download your own payment receipts."},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        try:
            from order_payments_management.services.receipt_service import ReceiptService
            from django.utils import timezone
            
            # Prepare transaction data for receipt
            transaction_data = {
                'reference_id': f"WP-{payment.id}",
                'transaction_id': str(payment.id),
                'amount': float(payment.amount),
                'currency': 'USD',
                'payment_date': payment.payment_date.isoformat() if payment.payment_date else timezone.now().isoformat(),
                'payment_type': 'writer_payment',
                'description': payment.description or f"Writer Payment #{payment.id}",
                'writer': {
                    'id': payment.writer.id,
                    'username': payment.writer.user.username,
                    'email': payment.writer.user.email,
                },
                'breakdown': {
                    'base_amount': float(payment.amount),
                    'bonuses': float(payment.bonuses or 0),
                    'fines': float(payment.fines or 0),
                    'tips': float(payment.tips or 0),
                },
            }
            
            if payment.converted_amount:
                transaction_data['converted_amount'] = float(payment.converted_amount)
                transaction_data['conversion_rate'] = float(payment.conversion_rate or 1)
            
            website_name = payment.website.name if payment.website else "Writing System"
            
            # Generate PDF receipt
            pdf_buffer = ReceiptService.generate_receipt_pdf(transaction_data, website_name)
            filename = f"writer_payment_receipt_{payment.id}_{timezone.now().strftime('%Y%m%d')}.pdf"
            return ReceiptService.create_pdf_response(pdf_buffer, filename)
            
        except ImportError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"PDF generation failed: {str(e)}")
            return Response(
                {"error": "PDF generation is not available. Please install reportlab: pip install reportlab"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error generating receipt: {str(e)}")
            return Response(
                {"error": f"Failed to generate receipt: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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

    def perform_create(self, serializer):
        probation = serializer.save()
        if probation.is_active:
            DisciplineNotificationService.notify_probation_started(probation)
        WriterStatusService.update(probation.writer)
        return probation

    def perform_update(self, serializer):
        previous_active = serializer.instance.is_active
        probation = serializer.save()
        WriterStatusService.update(probation.writer)
        if previous_active and not probation.is_active:
            DisciplineNotificationService.notify_probation_completed(probation)
        elif not previous_active and probation.is_active:
            DisciplineNotificationService.notify_probation_started(probation)
        return probation

    def perform_destroy(self, instance):
        writer = instance.writer
        was_active = instance.is_active
        if was_active:
            DisciplineNotificationService.notify_probation_completed(instance)
        super().perform_destroy(instance)
        WriterStatusService.update(writer)


### ---------------- Support, Disputes & Requests ---------------- ###

class WriterSupportTicketViewSet(viewsets.ModelViewSet):
    """
    Writers can submit support tickets.
    """
    queryset = WriterSupportTicket.objects.all().select_related(
        'writer__user', 'website', 'assigned_to'
    )
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
    queryset = WriterEarningsHistory.objects.all().select_related(
        'writer__user', 'website'
    )
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
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        suspension = serializer.save()
        WriterStatusService.update(suspension.writer)
        if suspension.is_active:
            DisciplineNotificationService.notify_suspension_started(suspension)
        return suspension

    def perform_update(self, serializer):
        previous_active = serializer.instance.is_active
        suspension = serializer.save()
        WriterStatusService.update(suspension.writer)
        if previous_active and not suspension.is_active:
            DisciplineNotificationService.notify_suspension_lifted(suspension)
        elif not previous_active and suspension.is_active:
            DisciplineNotificationService.notify_suspension_started(suspension)
        return suspension

    def perform_destroy(self, instance):
        writer = instance.writer
        was_active = instance.is_active
        if was_active:
            DisciplineNotificationService.notify_suspension_lifted(instance)
        super().perform_destroy(instance)
        WriterStatusService.update(writer)
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
    """
    Manage WriterLevel definitions (templates/configurations).
    Admin-only endpoint for managing level configurations.
    """
    queryset = WriterLevel.objects.select_related("website").prefetch_related("writers")
    serializer_class = WriterLevelSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['website', 'is_active', 'earning_mode']
    search_fields = ['name', 'description']
    ordering_fields = ['display_order', 'name', 'created_at']
    ordering = ['display_order', 'name']
    
    def get_queryset(self):
        qs = super().get_queryset()
        # Filter by website if not superadmin
        if self.request.user.role != 'superadmin':
            website = getattr(self.request.user, 'website', None)
            if website:
                qs = qs.filter(website=website)
        return qs
    
    @action(detail=True, methods=['post'])
    def calculate_sample_earnings(self, request, pk=None):
        """
        Calculate sample earnings for a level with example order.
        Helps admins understand earnings before saving.
        """
        from writer_management.services.earnings_calculator import WriterEarningsCalculator
        from decimal import Decimal
        
        level = self.get_object()
        pages = int(request.data.get('pages', 10))
        slides = int(request.data.get('slides', 0))
        order_total = request.data.get('order_total')
        order_cost = request.data.get('order_cost')
        is_urgent = request.data.get('is_urgent', False)
        is_technical = request.data.get('is_technical', False)
        
        order_total_decimal = Decimal(str(order_total)) if order_total else None
        order_cost_decimal = Decimal(str(order_cost)) if order_cost else None
        
        breakdown = WriterEarningsCalculator.calculate_estimated_earnings(
            level,
            pages=pages,
            slides=slides,
            order_total=order_total_decimal,
            order_cost=order_cost_decimal,
            is_urgent=is_urgent,
            is_technical=is_technical
        )
        
        return Response({
            'earnings': breakdown,
            'level_name': level.name,
            'earning_mode': level.earning_mode,
        })
    
    @action(detail=True, methods=['get'])
    def progression_stats(self, request, pk=None):
        """
        Get statistics on how many writers are eligible for this level.
        """
        from writer_management.services.level_progression import WriterLevelProgressionService
        
        level = self.get_object()
        from writer_management.models.profile import WriterProfile
        
        # Get all writers for this website
        writers = WriterProfile.objects.filter(website=level.website)
        
        eligible_count = 0
        ineligible_count = 0
        sample_failures = []
        
        for writer in writers[:100]:  # Limit to first 100 for performance
            is_eligible, failed = WriterLevelProgressionService.check_level_eligibility(writer, level)
            if is_eligible:
                eligible_count += 1
            else:
                ineligible_count += 1
                if len(sample_failures) < 5:  # Store first 5 failure examples
                    sample_failures.append({
                        'writer_id': writer.id,
                        'writer_username': writer.user.username,
                        'failed_requirements': failed[:3],  # First 3 failures
                    })
        
        return Response({
            'level': {
                'id': level.id,
                'name': level.name,
            },
            'statistics': {
                'eligible_writers': eligible_count,
                'ineligible_writers': ineligible_count,
                'total_checked': eligible_count + ineligible_count,
            },
            'sample_failures': sample_failures,
        })
    

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

        expires_days = (
            (expires_at - now()).days
            if expires_at
            else None
        )

        warning = WriterWarningService.issue_warning(
            writer=writer,
            reason=reason,
            issued_by=self.request.user,
            expires_days=expires_days
        )

        return warning

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=['is_active'])
        DisciplineNotificationService.notify_warning_resolved(
            instance,
            reason="revoked by admin",
        )
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


class WriterStrikeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing writer strikes.
    Admins can issue, view, and manage strikes.
    """
    queryset = WriterStrike.objects.all().select_related(
        'writer__user', 'issued_by', 'website'
    ).order_by('-issued_at')
    serializer_class = WriterStrikeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['writer', 'website', 'issued_by']
    ordering_fields = ['issued_at']
    ordering = ['-issued_at']

    def perform_create(self, serializer):
        """Create a strike and update writer status."""
        strike = serializer.save()
        
        # Update writer status to reflect new strike
        WriterStatusService.update(strike.writer)
        
        # Evaluate if strike should trigger suspension/blacklist
        from writer_management.services.discipline import DisciplineService
        DisciplineService.evaluate_strikes(strike.writer)
        
        DisciplineNotificationService.notify_strike_issued(strike)

        return strike

    @action(detail=False, methods=['get'], url_path='by-writer/(?P<writer_id>[^/.]+)')
    def by_writer(self, request, writer_id=None):
        """Get all strikes for a specific writer."""
        strikes = self.queryset.filter(writer_id=writer_id)
        serializer = self.get_serializer(strikes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke a strike (soft delete by creating history entry)."""
        strike = self.get_object()
        
        # Create history entry
        WriterStrikeHistory.objects.create(
            strike=strike,
            changed_by=request.user,
            change_type="Deleted",
            notes="Strike revoked by admin"
        )
        
        DisciplineNotificationService.notify_strike_revoked(strike)

        # Delete the strike
        strike.delete()
        
        # Update writer status
        WriterStatusService.update(strike.writer)
        
        return Response(
            {'detail': 'Strike revoked successfully.'},
            status=status.HTTP_200_OK
        )


class WriterDisciplineConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing writer discipline configuration.
    Admins can configure strike thresholds, suspension rules, etc.
    """
    queryset = WriterDisciplineConfig.objects.all().select_related('website')
    serializer_class = WriterDisciplineConfigSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['website']
    lookup_field = 'website'

    def get_object(self):
        """Get config by website ID."""
        website_id = self.kwargs.get('website')
        if website_id:
            obj = get_object_or_404(self.queryset, website_id=website_id)
            self.check_object_permissions(self.request, obj)
            return obj
        return super().get_object()

    def create(self, request, *args, **kwargs):
        """Create or update discipline config for a website."""
        website_id = request.data.get('website')
        if not website_id:
            return Response(
                {'detail': 'Website ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if config already exists for this website
        existing_config = self.queryset.filter(website_id=website_id).first()
        if existing_config:
            # Update existing config
            serializer = self.get_serializer(existing_config, data=request.data, partial=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Create new config
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Update discipline config by website ID."""
        website_id = kwargs.get('website')
        if not website_id:
            return Response(
                {'detail': 'Website ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        instance = get_object_or_404(self.queryset, website_id=website_id)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def partial_update(self, request, *args, **kwargs):
        """Partial update discipline config by website ID."""
        return self.update(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='by-website/(?P<website_id>[^/.]+)')
    def by_website(self, request, website_id=None):
        """Get discipline config for a specific website."""
        config = self.queryset.filter(website_id=website_id).first()
        if not config:
            # Return default config structure
            return Response({
                'website': int(website_id),
                'max_strikes': 3,
                'auto_suspend_days': 7,
                'auto_blacklist_strikes': 5
            })
        serializer = self.get_serializer(config)
        return Response(serializer.data)


### ---------------- Writer Pen Name & Resources Views ---------------- ###

class WriterPenNameChangeRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing pen name change requests.
    Writers can create requests, admins/superadmins can approve/reject.
    """
    queryset = WriterPenNameChangeRequest.objects.all().select_related(
        'writer__user', 'website', 'reviewed_by'
    ) if WriterPenNameChangeRequest else WriterPenNameChangeRequest.objects.none()
    serializer_class = WriterPenNameChangeRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['status', 'website', 'writer']
    ordering_fields = ['requested_at', 'reviewed_at']
    ordering = ['-requested_at']
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Writers can only see their own requests
        if user.role == 'writer':
            try:
                writer_profile = WriterProfile.objects.get(user=user)
                queryset = queryset.filter(writer=writer_profile)
            except WriterProfile.DoesNotExist:
                queryset = queryset.none()
        
        # Admins/superadmins see all requests
        elif user.role in ['admin', 'superadmin']:
            # Can filter by website if provided
            website_id = self.request.query_params.get('website_id')
            if website_id:
                queryset = queryset.filter(website_id=website_id)
        else:
            queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """Create a pen name change request."""
        user = self.request.user
        if user.role != 'writer':
            raise ValidationError("Only writers can request pen name changes")
        
        try:
            writer_profile = WriterProfile.objects.get(user=user)
        except WriterProfile.DoesNotExist:
            raise ValidationError("Writer profile not found")
        
        # Set current pen name from profile
        current_pen_name = writer_profile.pen_name or ''
        
        serializer.save(
            writer=writer_profile,
            website=writer_profile.website,
            current_pen_name=current_pen_name,
            status='pending'
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        """Approve a pen name change request (admin/superadmin only)."""
        if request.user.role not in ['admin', 'superadmin']:
            return Response(
                {'error': 'Only admins can approve requests'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        request_obj = self.get_object()
        notes = request.data.get('admin_notes', '')
        
        try:
            request_obj.approve(request.user, notes)
            return Response(
                {'message': 'Pen name change approved successfully'},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        """Reject a pen name change request (admin/superadmin only)."""
        if request.user.role not in ['admin', 'superadmin']:
            return Response(
                {'error': 'Only admins can reject requests'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        request_obj = self.get_object()
        notes = request.data.get('admin_notes', '')
        
        try:
            request_obj.reject(request.user, notes)
            return Response(
                {'message': 'Pen name change rejected'},
                status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class WriterResourceCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing writer resource categories.
    Admin/superadmin only.
    """
    queryset = WriterResourceCategory.objects.all().select_related('website') if WriterResourceCategory else WriterResourceCategory.objects.none()
    serializer_class = WriterResourceCategorySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['website', 'is_active']
    ordering_fields = ['display_order', 'name']
    ordering = ['display_order', 'name']
    
    def perform_create(self, serializer):
        """Create a resource category."""
        serializer.save()


class WriterResourceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing writer resources.
    Writers can view, admins can create/update/delete.
    """
    queryset = WriterResource.objects.all().select_related(
        'category', 'website', 'created_by', 'updated_by'
    ) if WriterResource else WriterResource.objects.none()
    serializer_class = WriterResourceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ['website', 'category', 'resource_type', 'is_active', 'is_featured']
    ordering_fields = ['display_order', 'created_at', 'view_count']
    ordering = ['display_order', '-created_at']
    search_fields = ['title', 'description']
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Writers can only see active resources
        if user.role == 'writer':
            queryset = queryset.filter(is_active=True)
            # Filter by website if writer has a profile
            try:
                writer_profile = WriterProfile.objects.get(user=user)
                queryset = queryset.filter(website=writer_profile.website)
            except WriterProfile.DoesNotExist:
                queryset = queryset.none()
        
        # Admins/superadmins see all resources
        elif user.role in ['admin', 'superadmin']:
            website_id = self.request.query_params.get('website_id')
            if website_id:
                queryset = queryset.filter(website_id=website_id)
        else:
            queryset = queryset.none()
        
        return queryset
    
    def perform_create(self, serializer):
        """Create a resource (admin/superadmin only)."""
        if self.request.user.role not in ['admin', 'superadmin']:
            raise ValidationError("Only admins can create resources")
        
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Update a resource (admin/superadmin only)."""
        if self.request.user.role not in ['admin', 'superadmin']:
            raise ValidationError("Only admins can update resources")
        
        serializer.save(updated_by=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def view(self, request, pk=None):
        """Track a resource view (writers only)."""
        if request.user.role != 'writer':
            return Response(
                {'error': 'Only writers can track views'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        resource = self.get_object()
        
        try:
            writer_profile = WriterProfile.objects.get(user=request.user)
            
            # Create or get view record
            view_record, created = WriterResourceView.objects.get_or_create(
                resource=resource,
                writer=writer_profile
            )
            
            # Increment view count if new view
            if created:
                resource.increment_view()
            
            return Response(
                {'message': 'View tracked successfully'},
                status=status.HTTP_200_OK
            )
        except WriterProfile.DoesNotExist:
            return Response(
                {'error': 'Writer profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def download(self, request, pk=None):
        """Track a resource download (writers only)."""
        if request.user.role != 'writer':
            return Response(
                {'error': 'Only writers can download resources'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        resource = self.get_object()
        
        if resource.resource_type != 'document' or not resource.file:
            return Response(
                {'error': 'Resource is not a downloadable document'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Increment download count
        resource.increment_download()
        
        # Return file URL
        return Response(
            {
                'message': 'Download tracked',
                'file_url': resource.file.url
            },
            status=status.HTTP_200_OK
        )
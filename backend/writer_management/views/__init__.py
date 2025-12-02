from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError

from writer_management.models.profile import WriterProfile
from writer_management.models.configs import WriterConfig, WriterLevelConfig
from writer_management.models.requests import (
    WriterOrderRequest, WriterOrderTake, WriterDeadlineExtensionRequest,
)
from writer_management.models.discipline import WriterSuspension
from writer_management.models.tickets import WriterSupportTicket
from writer_management.serializers import (
    WriterProfileSerializer, WriterConfigSerializer,
    WriterOrderRequestSerializer, WriterOrderTakeSerializer,
    WriterSuspensionSerializer, WriterSupportTicketSerializer,
    WriterDeadlineExtensionRequestSerializer, WriterLevelConfigSerializer,
    WriterLevelSerializer,
)

# Note: WriterPerformanceSnapshotViewSet and WriterPerformanceDashboardView
# are defined in writer_management/views.py (not in this __init__.py file)
# They are imported directly in urls.py to avoid circular imports


class WriterProfileViewSet(viewsets.ModelViewSet):
    queryset = WriterProfile.objects.all()
    serializer_class = WriterProfileSerializer
    permission_classes = [permissions.IsAdminUser]


class WriterConfigViewSet(viewsets.ModelViewSet):
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


class WriterOrderRequestViewSet(viewsets.ModelViewSet):
    queryset = WriterOrderRequest.objects.all()
    serializer_class = WriterOrderRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        writer = self.request.user.writer_profile
        # Get max requests from writer's level, fallback to WriterConfig if no level
        if writer.writer_level:
            max_requests = writer.writer_level.max_requests_per_writer
        else:
            # Fallback to WriterConfig for writers without a level
            config = WriterConfig.objects.filter(website=writer.website).first()
            max_requests = config.max_requests_per_writer if config else 5
        
        active_requests = WriterOrderRequest.objects.filter(writer=writer, approved=False).count()
        if active_requests >= max_requests:
            raise ValidationError(f"Max request limit reached ({max_requests}).")
        serializer.save(writer=writer)

    @action(detail=True, methods=['POST'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        """
        Legacy simple approval (does not assign the order).
        Kept for backward compatibility; prefer using `assign` action.
        """
        request_obj = self.get_object()
        if request_obj.approved:
            return Response({"message": "This request has already been approved."}, status=status.HTTP_400_BAD_REQUEST)
        request_obj.approved = True
        request_obj.reviewed_by = request.user
        request_obj.save(update_fields=["approved", "reviewed_by"])
        return Response({"message": "Order request approved."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], permission_classes=[permissions.IsAdminUser], url_path='assign')
    def assign_from_request(self, request, pk=None):
        """
        Approve a writer's order request and assign the order to that writer.

        This is used by the admin/superadmin/support "Assign from Request" button.
        """
        from django.db import transaction
        from django.core.exceptions import ValidationError as DjangoValidationError, PermissionDenied
        from orders.services.assignment import OrderAssignmentService

        request_obj = self.get_object()
        order = request_obj.order
        writer_profile = request_obj.writer

        if not writer_profile or not getattr(writer_profile, "user", None):
            return Response(
                {"error": "Writer profile is missing or invalid for this request."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        writer_user = writer_profile.user
        reason = request.data.get("reason") or request_obj.reason or "Assigned from writer request"

        try:
            with transaction.atomic():
                # Use the shared assignment service so notifications, logs, etc. stay consistent
                service = OrderAssignmentService(order)
                # Attach the acting admin/support user so access checks and logs work
                service.actor = request.user  # type: ignore[attr-defined]

                updated_order = service.assign_writer(writer_user.id, reason=reason)

                # Mark the request as approved and reviewed
                request_obj.approved = True
                request_obj.reviewed_by = request.user
                request_obj.save(update_fields=["approved", "reviewed_by"])

            return Response(
                {
                    "message": "Writer assigned successfully from request.",
                    "order_id": updated_order.id,
                },
                status=status.HTTP_200_OK,
            )
        except (DjangoValidationError, PermissionDenied) as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to assign writer from request: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class WriterOrderTakeViewSet(viewsets.ModelViewSet):
    queryset = WriterOrderTake.objects.all()
    serializer_class = WriterOrderTakeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        writer = self.request.user.writer_profile
        config = WriterConfig.objects.first()
        if config and not config.takes_enabled:
            raise ValidationError("Taking orders is disabled.")
        max_allowed_orders = writer.writer_level.max_orders if writer.writer_level else 0
        current_taken_orders = WriterOrderTake.objects.filter(writer=writer).count()
        if current_taken_orders >= max_allowed_orders:
            raise ValidationError("You have reached your max take limit.")
        serializer.save(writer=writer)


class WriterSupportTicketViewSet(viewsets.ModelViewSet):
    queryset = WriterSupportTicket.objects.all()
    serializer_class = WriterSupportTicketSerializer
    permission_classes = [permissions.IsAuthenticated]


class WriterSuspensionViewSet(viewsets.ModelViewSet):
    queryset = WriterSuspension.objects.all()
    serializer_class = WriterSuspensionSerializer
    permission_classes = [permissions.IsAdminUser]


class WriterDeadlineExtensionRequestViewSet(viewsets.ModelViewSet):
    queryset = WriterDeadlineExtensionRequest.objects.all()
    serializer_class = WriterDeadlineExtensionRequestSerializer
    permission_classes = [permissions.IsAuthenticated]


# Import performance views from the performance module
from writer_management.views.performance import (
    WriterPerformanceSnapshotViewSet,
    WriterPerformanceDashboardView,
)

# Import WriterLevelViewSet from level_management module
from writer_management.views.level_management import WriterLevelViewSet

# Import discipline ViewSets from main views.py file
# Using importlib to avoid circular imports since views.py and views/ both exist
try:
    import sys
    import os
    import importlib.util
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    main_views_path = os.path.join(parent_dir, 'views.py')
    if os.path.exists(main_views_path):
        spec = importlib.util.spec_from_file_location("writer_management.views_main", main_views_path)
        if spec and spec.loader:
            views_main = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(views_main)
            WriterStrikeViewSet = getattr(views_main, 'WriterStrikeViewSet', None)
            WriterDisciplineConfigViewSet = getattr(views_main, 'WriterDisciplineConfigViewSet', None)
        else:
            WriterStrikeViewSet = None
            WriterDisciplineConfigViewSet = None
    else:
        WriterStrikeViewSet = None
        WriterDisciplineConfigViewSet = None
except Exception:
    # If import fails, set to None - urls.py will handle the error
    WriterStrikeViewSet = None
    WriterDisciplineConfigViewSet = None

# Import pen name and resource viewsets from main views.py
try:
    import sys
    import os
    import importlib.util
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    main_views_path = os.path.join(parent_dir, 'views.py')
    if os.path.exists(main_views_path):
        spec = importlib.util.spec_from_file_location("writer_management.views_main", main_views_path)
        if spec and spec.loader:
            views_main = importlib.util.module_from_spec(spec)
            views_main.__package__ = 'writer_management'
            views_main.__name__ = 'writer_management.views'
            spec.loader.exec_module(views_main)
            WriterPenNameChangeRequestViewSet = getattr(views_main, 'WriterPenNameChangeRequestViewSet', None)
            WriterResourceViewSet = getattr(views_main, 'WriterResourceViewSet', None)
            WriterResourceCategoryViewSet = getattr(views_main, 'WriterResourceCategoryViewSet', None)
        else:
            WriterPenNameChangeRequestViewSet = None
            WriterResourceViewSet = None
            WriterResourceCategoryViewSet = None
    else:
        WriterPenNameChangeRequestViewSet = None
        WriterResourceViewSet = None
        WriterResourceCategoryViewSet = None
except Exception:
    # If import fails, set to None - urls.py will handle the error
    WriterPenNameChangeRequestViewSet = None
    WriterResourceViewSet = None
    WriterResourceCategoryViewSet = None

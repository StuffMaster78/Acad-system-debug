from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

from fines.models import Fine, FineAppeal, FineStatus
from fines.serializers import FineSerializer, FineAppealSerializer
from fines.services.fine_services import FineService
from fines.services.fine_appeal_service import FineAppealService
from authentication.permissions import IsAdminOrSuperAdmin


class FineViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing fines. Supports CRUD and custom actions like
    waive and void, with user-context and permissions handled.
    """
    queryset = Fine.objects.select_related('order', 'order__assigned_writer', 'issued_by', 'waived_by')
    serializer_class = FineSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter fines based on user role."""
        user = self.request.user
        
        if user.role in ['admin', 'superadmin', 'support']:
            # Admins see all fines
            return self.queryset.all()
        elif user.role == 'writer':
            # Writers see only their own fines
            return self.queryset.filter(order__assigned_writer=user)
        else:
            return self.queryset.none()

    def perform_create(self, serializer):
        """Automatically set the fine issuer as the current user."""
        serializer.save(issued_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="waive")
    def waive(self, request, pk=None):
        """
        Admin action to waive a fine (restores compensation).
        """
        fine = get_object_or_404(self.get_queryset(), pk=pk)
        
        if request.user.role not in ['admin', 'superadmin']:
            raise PermissionDenied("Only admins or superadmins can waive fines.")
        
        reason = request.data.get("reason", "")
        waived = FineService.waive_fine(fine, request.user, reason)
        return Response(self.get_serializer(waived).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="void")
    def void(self, request, pk=None):
        """
        Admin action to void/revoke a fine (restores compensation).
        """
        fine = get_object_or_404(self.get_queryset(), pk=pk)
        
        if request.user.role not in ['admin', 'superadmin']:
            raise PermissionDenied("Only admins or superadmins can void fines.")
        
        reason = request.data.get("reason", "Fine revoked by admin")
        voided = FineService.void_fine(fine, request.user, reason)
        return Response(self.get_serializer(voided).data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["post"], url_path="issue")
    def issue_fine(self, request):
        """
        Admin action to issue a fine using fine type config.
        
        Request Body:
        {
            "order_id": 123,
            "fine_type_code": "quality_issue",
            "reason": "Poor quality work, multiple issues",
            "custom_amount": 25.00  // Optional override
        }
        """
        if request.user.role not in ['admin', 'superadmin']:
            raise PermissionDenied("Only admins or superadmins can issue fines.")
        
        order_id = request.data.get('order_id')
        fine_type_code = request.data.get('fine_type_code')
        reason = request.data.get('reason', '')
        custom_amount = request.data.get('custom_amount')
        
        if not order_id:
            return Response(
                {"detail": "order_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not fine_type_code:
            return Response(
                {"detail": "fine_type_code is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not reason:
            return Response(
                {"detail": "reason is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from orders.models import Order
            order = Order.objects.get(id=order_id)
            
            from fines.services.fine_type_service import FineTypeService
            fine = FineTypeService.issue_fine(
                order=order,
                fine_type_code=fine_type_code,
                reason=reason,
                issued_by=request.user,
                custom_amount=custom_amount
            )
            
            return Response(
                self.get_serializer(fine).data,
                status=status.HTTP_201_CREATED
            )
        except Order.DoesNotExist:
            return Response(
                {"detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=["get"], url_path="available-types")
    def available_types(self, request):
        """Get available fine types for current website."""
        from fines.services.fine_management_service import FineManagementService
        from websites.utils import get_current_website
        
        website = get_current_website(request)
        fine_types = FineManagementService.get_available_fine_types(website)
        
        from fines.serializers.fine_type_config_serializers import FineTypeConfigSerializer
        serializer = FineTypeConfigSerializer(fine_types, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"], url_path="dispute")
    def dispute(self, request, pk=None):
        """
        Writer action to dispute a fine.
        """
        fine = get_object_or_404(self.get_queryset(), pk=pk)
        
        if request.user.role != 'writer':
            raise PermissionDenied("Only writers can dispute fines.")
        
        reason = request.data.get("reason", "")
        if not reason:
            return Response(
                {"detail": "Reason is required for disputing a fine."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            appeal = FineAppealService.submit_appeal(fine, request.user, reason)
            return Response(
                FineAppealSerializer(appeal).data,
                status=status.HTTP_201_CREATED
            )
        except (ValueError, PermissionDenied) as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class FineAppealViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling fine appeals/disputes. Supports creation and admin
    review workflows with smart permissioning and audit trails.
    """
    queryset = FineAppeal.objects.select_related(
        'fine', 'fine__order', 'appealed_by', 'reviewed_by', 'escalated_to'
    )
    serializer_class = FineAppealSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter appeals based on user role."""
        user = self.request.user
        
        if user.role in ['admin', 'superadmin', 'support']:
            # Admins see all appeals
            return self.queryset.all()
        elif user.role == 'writer':
            # Writers see only their own appeals
            return self.queryset.filter(appealed_by=user)
        else:
            return self.queryset.none()

    def perform_create(self, serializer):
        """Set the current user as the appellant."""
        serializer.save(appealed_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="review")
    def review(self, request, pk=None):
        """
        Admin action to review a submitted appeal/dispute.
        """
        appeal = get_object_or_404(self.get_queryset(), pk=pk)
        
        if request.user.role not in ['admin', 'superadmin', 'support']:
            raise PermissionDenied("Only admins, superadmins, or support can review disputes.")
        
        accept = request.data.get("accept")
        if accept is None:
            return Response(
                {"detail": "Field 'accept' (true/false) is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        review_notes = request.data.get("review_notes", "")
        
        try:
            reviewed = FineAppealService.review_appeal(
                appeal, request.user, accept, review_notes
            )
            return Response(self.get_serializer(reviewed).data)
        except (ValueError, PermissionDenied) as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=["post"], url_path="escalate")
    def escalate(self, request, pk=None):
        """
        Escalate a dispute to admin/superadmin for resolution.
        """
        appeal = get_object_or_404(self.get_queryset(), pk=pk)
        
        if request.user.role not in ['admin', 'superadmin', 'support']:
            raise PermissionDenied("Only admins, superadmins, or support can escalate disputes.")
        
        escalated_to_id = request.data.get("escalated_to_id")
        if escalated_to_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            escalated_to = get_object_or_404(User, id=escalated_to_id)
        else:
            escalated_to = request.user
        
        escalation_reason = request.data.get("escalation_reason", "")
        
        try:
            escalated = FineAppealService.escalate_dispute(
                appeal, escalated_to, escalation_reason
            )
            return Response(self.get_serializer(escalated).data)
        except (ValueError, PermissionDenied) as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
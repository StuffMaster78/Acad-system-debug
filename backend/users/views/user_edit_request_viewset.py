"""
ViewSet for User Edit Requests.
Handles user edit requests and admin approval workflow.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError as DRFValidationError
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from users.models.user_edit_requests import UserEditRequest
from users.services.user_edit_service import UserEditService
from users.serializers.user_edit_requests import (
    UserEditRequestSerializer,
    CreateUserEditRequestSerializer
)
from admin_management.permissions import IsAdmin
import logging

logger = logging.getLogger(__name__)


class UserEditRequestViewSet(viewsets.ViewSet):
    """
    ViewSet for managing user edit requests.
    """
    permission_classes = [IsAuthenticated]
    
    # ==================== User Endpoints ====================
    
    @action(detail=False, methods=['post'], url_path='request')
    def create_edit_request(self, request):
        """
        Create a new edit request.
        
        Request body:
        {
            "field_changes": {
                "email": "newemail@example.com",
                "username": "newusername"
            },
            "request_type": "email_change",
            "reason": "I want to update my email address"
        }
        """
        serializer = CreateUserEditRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        service = UserEditService(request.user)
        try:
            result = service.create_edit_request(
                field_changes=serializer.validated_data['field_changes'],
                request_type=serializer.validated_data.get('request_type', 'profile_update'),
                reason=serializer.validated_data.get('reason', '')
            )
            
            response_data = {
                'message': 'Edit request created successfully.',
                'auto_approved': result.get('auto_approved', {}),
            }
            
            if result.get('edit_request'):
                response_data['edit_request'] = UserEditRequestSerializer(result['edit_request']).data
                response_data['pending_approval'] = result.get('pending_approval', {})
                response_data['message'] = 'Edit request created. Some changes require admin approval.'
            else:
                response_data['message'] = 'All changes were applied immediately.'
            
            return Response(response_data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            raise DRFValidationError(str(e))
    
    @action(detail=False, methods=['get'], url_path='my-requests')
    def get_my_requests(self, request):
        """
        Get current user's edit requests.
        
        Query params:
        - status: Filter by status (pending, approved, rejected, cancelled)
        """
        status_filter = request.query_params.get('status')
        
        service = UserEditService(request.user)
        requests = service.get_user_edit_requests(
            user=request.user,
            status=status_filter
        )
        
        serializer = UserEditRequestSerializer(requests, many=True)
        return Response({
            'requests': serializer.data,
            'count': requests.count()
        })
    
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_request(self, request, pk=None):
        """
        Cancel own edit request (only if pending).
        """
        edit_request = get_object_or_404(
            UserEditRequest,
            id=pk,
            user=request.user
        )
        
        if edit_request.status != 'pending':
            return Response(
                {'error': 'Only pending requests can be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        edit_request.cancel()
        return Response({
            'message': 'Edit request cancelled successfully.'
        })
    
    # ==================== Admin Endpoints ====================
    
    @action(detail=False, methods=['get'], url_path='admin/pending')
    def get_pending_requests(self, request):
        """
        Get all pending edit requests (admin only).
        
        Query params:
        - website_id: Filter by website
        - request_type: Filter by request type
        """
        if request.user.role not in ['admin', 'superadmin']:
            raise PermissionDenied("Only admins can view pending requests.")
        
        website_id = request.query_params.get('website_id')
        request_type = request.query_params.get('request_type')
        
        website = None
        if website_id:
            from websites.models import Website
            website = Website.objects.filter(id=website_id).first()
        
        requests = UserEditService.get_pending_requests(website=website)
        
        if request_type:
            requests = requests.filter(request_type=request_type)
        
        serializer = UserEditRequestSerializer(requests, many=True)
        return Response({
            'requests': serializer.data,
            'count': requests.count()
        })
    
    @action(detail=False, methods=['get'], url_path='admin/all')
    def get_all_requests(self, request):
        """
        Get all edit requests (admin only).
        
        Query params:
        - status: Filter by status
        - website_id: Filter by website
        - user_id: Filter by user
        """
        if request.user.role not in ['admin', 'superadmin']:
            raise PermissionDenied("Only admins can view all requests.")
        
        status_filter = request.query_params.get('status')
        website_id = request.query_params.get('website_id')
        user_id = request.query_params.get('user_id')
        
        queryset = UserEditRequest.objects.all().select_related(
            'user', 'website', 'reviewed_by'
        )
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        queryset = queryset.order_by('-created_at')
        
        serializer = UserEditRequestSerializer(queryset, many=True)
        return Response({
            'requests': serializer.data,
            'count': queryset.count()
        })
    
    @action(detail=True, methods=['post'], url_path='admin/approve')
    def approve_request(self, request, pk=None):
        """
        Approve an edit request (admin only).
        
        Request body (optional):
        {
            "notes": "Approved after verification"
        }
        """
        if request.user.role not in ['admin', 'superadmin']:
            raise PermissionDenied("Only admins can approve requests.")
        
        edit_request = get_object_or_404(UserEditRequest, id=pk)
        
        if edit_request.status != 'pending':
            return Response(
                {'error': f'Request is already {edit_request.status}.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notes = request.data.get('notes', '')
        
        try:
            UserEditService.approve_request(edit_request, request.user, notes)
            return Response({
                'message': 'Edit request approved and changes applied.',
                'edit_request': UserEditRequestSerializer(edit_request).data
            })
        except Exception as e:
            logger.error(f"Error approving edit request {pk}: {e}", exc_info=True)
            return Response(
                {'error': f'Error approving request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='admin/reject')
    def reject_request(self, request, pk=None):
        """
        Reject an edit request (admin only).
        
        Request body:
        {
            "reason": "Reason for rejection"
        }
        """
        if request.user.role not in ['admin', 'superadmin']:
            raise PermissionDenied("Only admins can reject requests.")
        
        edit_request = get_object_or_404(UserEditRequest, id=pk)
        
        if edit_request.status != 'pending':
            return Response(
                {'error': f'Request is already {edit_request.status}.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reason = request.data.get('reason', '')
        if not reason:
            return Response(
                {'error': 'Rejection reason is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            UserEditService.reject_request(edit_request, request.user, reason)
            return Response({
                'message': 'Edit request rejected.',
                'edit_request': UserEditRequestSerializer(edit_request).data
            })
        except Exception as e:
            logger.error(f"Error rejecting edit request {pk}: {e}", exc_info=True)
            return Response(
                {'error': f'Error rejecting request: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], url_path='detail')
    def get_request_detail(self, request, pk=None):
        """
        Get a specific edit request.
        Users can only view their own requests.
        Admins can view any request.
        """
        edit_request = get_object_or_404(UserEditRequest, id=pk)
        
        # Check permissions
        if request.user.role not in ['admin', 'superadmin']:
            if edit_request.user != request.user:
                raise PermissionDenied("You can only view your own edit requests.")
        
        serializer = UserEditRequestSerializer(edit_request)
        return Response(serializer.data)


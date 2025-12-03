"""
Profile Change ViewSet
Handles profile change requests for writers (requires admin approval).
"""
import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError

from users.models.profile_changes import ProfileChangeRequest, WriterAvatarUpload
from users.services.profile_change_service import ProfileChangeService, WriterAvatarService
from users.serializers.profile_changes import (
    ProfileChangeRequestSerializer, WriterAvatarUploadSerializer
)

logger = logging.getLogger(__name__)


class ProfileChangeRequestViewSet(viewsets.ViewSet):
    """
    ViewSet for profile change requests.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='request')
    def request_profile_change(self, request):
        """
        Request a profile change (writers only, requires admin approval).
        """
        if request.user.role != 'writer':
            return Response(
                {'error': 'Only writers can request profile changes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        change_type = request.data.get('change_type')
        requested_value = request.data.get('requested_value')
        current_value = request.data.get('current_value')
        
        if not change_type or not requested_value:
            return Response(
                {'error': 'change_type and requested_value are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = ProfileChangeService(request.user)
        try:
            change_request = service.request_profile_change(
                change_type=change_type,
                requested_value=requested_value,
                current_value=current_value
            )
            serializer = ProfileChangeRequestSerializer(change_request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='my-requests')
    def get_my_requests(self, request):
        """Get user's profile change requests."""
        from users.models.profile_changes import ProfileChangeRequest
        from websites.utils import get_current_website
        website = get_current_website(request)
        
        requests = ProfileChangeRequest.objects.filter(
            user=request.user,
            website=website
        ).order_by('-created_at')
        
        serializer = ProfileChangeRequestSerializer(requests, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='approve')
    def approve_change(self, request, pk=None):
        """
        Admin approves/rejects profile change request.
        """
        if request.user.role not in ['admin', 'superadmin']:
            return Response(
                {'error': 'Only admins can approve profile changes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        rejection_reason = request.data.get('rejection_reason')
        
        try:
            change_request = ProfileChangeRequest.objects.get(id=pk)
        except ProfileChangeRequest.DoesNotExist:
            return Response(
                {'error': 'Profile change request not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        service = ProfileChangeService(change_request.user)
        try:
            approved = service.approve_change(request.user, pk, rejection_reason)
            if approved:
                return Response({'message': 'Profile change approved and applied.'})
            else:
                return Response({'message': 'Profile change rejected.'})
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='admin/pending')
    def get_pending_requests(self, request):
        """
        Get all pending profile change requests (admin only).
        """
        if request.user.role not in ['admin', 'superadmin']:
            return Response(
                {'error': 'Only admins can view pending requests'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from websites.utils import get_current_website
        website = get_current_website(request)
        
        requests = ProfileChangeRequest.objects.filter(
            website=website,
            status='pending'
        ).order_by('-created_at')
        
        serializer = ProfileChangeRequestSerializer(requests, many=True)
        return Response(serializer.data)


class WriterAvatarViewSet(viewsets.ViewSet):
    """
    ViewSet for writer avatar uploads (requires admin approval).
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='upload')
    def upload_avatar(self, request):
        """
        Upload avatar for approval (writers only).
        """
        if request.user.role != 'writer':
            return Response(
                {'error': 'Only writers can upload avatars'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        avatar_file = request.FILES.get('avatar')
        if not avatar_file:
            return Response(
                {'error': 'Avatar file is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = WriterAvatarService(request.user)
        try:
            upload = service.upload_avatar(avatar_file)
            serializer = WriterAvatarUploadSerializer(upload)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='approve')
    def approve_avatar(self, request, pk=None):
        """
        Admin approves/rejects avatar upload.
        """
        if request.user.role not in ['admin', 'superadmin']:
            return Response(
                {'error': 'Only admins can approve avatars'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        rejection_reason = request.data.get('rejection_reason')
        
        try:
            upload = WriterAvatarUpload.objects.get(id=pk)
        except WriterAvatarUpload.DoesNotExist:
            return Response(
                {'error': 'Avatar upload not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        service = WriterAvatarService(upload.user)
        try:
            approved = service.approve_avatar(request.user, pk, rejection_reason)
            if approved:
                return Response({'message': 'Avatar approved and applied.'})
            else:
                return Response({'message': 'Avatar rejected.'})
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='admin/pending')
    def get_pending_uploads(self, request):
        """
        Get all pending avatar uploads (admin only).
        """
        if request.user.role not in ['admin', 'superadmin']:
            return Response(
                {'error': 'Only admins can view pending uploads'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from websites.utils import get_current_website
        website = get_current_website(request)
        
        uploads = WriterAvatarUpload.objects.filter(
            website=website,
            status='pending'
        ).order_by('-created_at')
        
        serializer = WriterAvatarUploadSerializer(uploads, many=True)
        return Response(serializer.data)


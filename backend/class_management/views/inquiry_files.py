"""
ViewSets for express class inquiry file management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from class_management.models import ExpressClass, ExpressClassInquiryFile
from class_management.serializers.inquiry_files import ExpressClassInquiryFileSerializer
import logging

logger = logging.getLogger(__name__)


class ExpressClassInquiryFileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing express class inquiry files.
    """
    queryset = ExpressClassInquiryFile.objects.select_related(
        'express_class', 'uploaded_by', 'website'
    ).order_by('-uploaded_at')
    serializer_class = ExpressClassInquiryFileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = self.queryset
        
        # Admins can see all files
        if user.is_staff or getattr(user, 'role', None) in ['admin', 'superadmin', 'support']:
            return queryset
        
        # Clients see files for their classes
        if getattr(user, 'role', None) == 'client':
            return queryset.filter(express_class__client=user)
        
        # Writers see files for assigned classes
        if getattr(user, 'role', None) == 'writer':
            return queryset.filter(express_class__assigned_writer=user)
        
        return queryset.none()
    
    def perform_create(self, serializer):
        """Set uploaded_by and validate class access."""
        user = self.request.user
        express_class_id = self.request.data.get('express_class')
        
        if express_class_id:
            try:
                express_class = ExpressClass.objects.get(id=express_class_id)
                
                # Check permissions
                if not (user.is_staff or 
                        getattr(user, 'role', None) in ['admin', 'superadmin', 'support'] or
                        express_class.client == user):
                    raise PermissionError("You don't have permission to upload files for this class")
                
                serializer.save(
                    uploaded_by=user,
                    website=express_class.website
                )
            except ExpressClass.DoesNotExist:
                raise ValueError("Express class not found")
        else:
            serializer.save(uploaded_by=user)
    
    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_file(self, request, pk=None):
        """Delete an inquiry file."""
        file_obj = self.get_object()
        user = request.user
        
        # Check permissions
        if not (user.is_staff or 
                getattr(user, 'role', None) in ['admin', 'superadmin', 'support'] or
                file_obj.uploaded_by == user):
            return Response(
                {'error': 'You do not have permission to delete this file'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        file_obj.delete()
        return Response({'status': 'File deleted successfully'})

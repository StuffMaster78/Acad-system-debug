"""
ViewSets for inquiry file management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from special_orders.models import SpecialOrder, SpecialOrderInquiryFile
from special_orders.serializers import SpecialOrderInquiryFileSerializer
import logging

logger = logging.getLogger(__name__)


class SpecialOrderInquiryFileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing special order inquiry files.
    """
    queryset = SpecialOrderInquiryFile.objects.select_related(
        'special_order', 'uploaded_by', 'website'
    ).order_by('-uploaded_at')
    serializer_class = SpecialOrderInquiryFileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = self.queryset
        
        # Admins can see all files
        if user.is_staff or getattr(user, 'role', None) in ['admin', 'superadmin', 'support']:
            return queryset
        
        # Clients see files for their orders
        if getattr(user, 'role', None) == 'client':
            return queryset.filter(special_order__client=user)
        
        # Writers see files for assigned orders
        if getattr(user, 'role', None) == 'writer':
            return queryset.filter(special_order__writer=user)
        
        return queryset.none()
    
    def perform_create(self, serializer):
        """Set uploaded_by and validate order access."""
        user = self.request.user
        special_order_id = self.request.data.get('special_order')
        
        if special_order_id:
            try:
                special_order = SpecialOrder.objects.get(id=special_order_id)
                
                # Check permissions
                if not (user.is_staff or 
                        getattr(user, 'role', None) in ['admin', 'superadmin', 'support'] or
                        special_order.client == user):
                    raise PermissionError("You don't have permission to upload files for this order")
                
                serializer.save(
                    uploaded_by=user,
                    website=special_order.website
                )
            except SpecialOrder.DoesNotExist:
                raise ValueError("Special order not found")
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

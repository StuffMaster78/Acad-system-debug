"""
Views for handling draft requests from clients.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from orders.models import Order, DraftRequest, DraftFile
from orders.serializers.draft_requests import (
    DraftRequestSerializer, DraftRequestCreateSerializer, DraftFileSerializer
)


class DraftRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing draft requests.
    Clients can request drafts if they've paid for Progressive Delivery.
    """
    queryset = DraftRequest.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DraftRequestCreateSerializer
        return DraftRequestSerializer
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = DraftRequest.objects.select_related(
            'order', 'requested_by', 'website'
        ).prefetch_related('files')
        
        if user.role == 'client':
            # Clients can only see their own requests
            queryset = queryset.filter(requested_by=user)
        elif user.role == 'writer':
            # Writers can see requests for their assigned orders
            queryset = queryset.filter(order__assigned_writer=user)
        elif user.role in ['admin', 'superadmin', 'support']:
            # Admins can see all requests
            pass
        else:
            # Other roles see nothing
            queryset = queryset.none()
        
        # Filter by order if provided
        order_id = self.request.query_params.get('order_id')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    def perform_create(self, serializer):
        """Create a draft request (can be created by client or admin)."""
        order = serializer.validated_data['order']
        user = self.request.user
        
        # Admins can create draft requests for any order
        # Clients can only create for their own orders (validated in serializer)
        serializer.save(
            website=order.website,
            requested_by=user,
            status='pending'
        )
    
    @action(detail=True, methods=['post'], url_path='upload-draft')
    def upload_draft(self, request, pk=None):
        """
        Writer uploads a draft file in response to a draft request.
        """
        draft_request = self.get_object()
        
        # Check if user is the assigned writer or admin
        if request.user.role not in ['admin', 'superadmin', 'support']:
            if draft_request.order.assigned_writer != request.user:
                return Response(
                    {"error": "Only the assigned writer can upload drafts"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Check if request is still pending or in progress
        if draft_request.status not in ['pending', 'in_progress']:
            return Response(
                {"error": f"Cannot upload draft for {draft_request.status} request"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get file from request
        file = request.FILES.get('file')
        if not file:
            return Response(
                {"error": "File is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size (max 50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        if file.size > max_size:
            return Response(
                {"error": "File size exceeds 50MB limit"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create draft file
        draft_file = DraftFile.objects.create(
            website=draft_request.website,
            draft_request=draft_request,
            order=draft_request.order,
            uploaded_by=request.user,
            file=file,
            file_name=file.name,
            description=request.data.get('description', '')
        )
        
        # Update draft request status
        if draft_request.status == 'pending':
            draft_request.status = 'in_progress'
            draft_request.save()
        
        serializer = DraftFileSerializer(draft_file, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], url_path='mark-fulfilled')
    def mark_fulfilled(self, request, pk=None):
        """
        Mark draft request as fulfilled (typically done automatically when file is uploaded).
        """
        draft_request = self.get_object()
        
        # Check permissions
        if request.user.role not in ['admin', 'superadmin', 'support']:
            if draft_request.order.assigned_writer != request.user:
                return Response(
                    {"error": "Only the assigned writer or admin can mark as fulfilled"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        if draft_request.status == 'fulfilled':
            return Response(
                {"error": "Request is already fulfilled"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        draft_request.fulfill(request.user)
        
        serializer = self.get_serializer(draft_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_request(self, request, pk=None):
        """
        Cancel a draft request (client or admin can cancel).
        """
        draft_request = self.get_object()
        
        # Check permissions
        if request.user.role not in ['admin', 'superadmin', 'support']:
            if draft_request.requested_by != request.user:
                return Response(
                    {"error": "Only the requester or admin can cancel"},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        if draft_request.status in ['fulfilled', 'cancelled']:
            return Response(
                {"error": f"Cannot cancel {draft_request.status} request"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        from django.utils import timezone
        draft_request.status = 'cancelled'
        draft_request.cancelled_at = timezone.now()
        draft_request.save()
        
        serializer = self.get_serializer(draft_request)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='check-eligibility')
    def check_eligibility(self, request):
        """
        Check if client can request drafts for a specific order.
        """
        order_id = request.query_params.get('order_id')
        if not order_id:
            return Response(
                {"error": "order_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if order belongs to user
        if order.client != request.user and request.user.role not in ['admin', 'superadmin', 'support']:
            return Response(
                {"error": "You can only check eligibility for your own orders"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create temporary draft request to check eligibility
        draft_request = DraftRequest(
            website=order.website,
            order=order,
            requested_by=request.user
        )
        can_request, reason = draft_request.can_request()
        
        # Check if there's already a pending request (admins can create multiple)
        has_pending = False
        if request.user.role not in ['admin', 'superadmin', 'support']:
            has_pending = DraftRequest.objects.filter(
                order=order,
                requested_by=request.user,
                status__in=['pending', 'in_progress']
            ).exists()
        
        return Response({
            'can_request': can_request and not has_pending,
            'reason': reason if not can_request else None,
            'has_pending_request': has_pending,
            'order_id': order.id,
            'order_status': order.status,
            'is_paid': order.is_paid,
        })


class DraftFileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing draft files.
    """
    queryset = DraftFile.objects.all()
    serializer_class = DraftFileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset based on user role."""
        user = self.request.user
        queryset = DraftFile.objects.select_related(
            'draft_request', 'order', 'uploaded_by', 'website'
        )
        
        if user.role == 'client':
            # Clients can see files for their draft requests
            queryset = queryset.filter(draft_request__requested_by=user)
        elif user.role == 'writer':
            # Writers can see files they uploaded
            queryset = queryset.filter(uploaded_by=user)
        elif user.role in ['admin', 'superadmin', 'support']:
            # Admins can see all files
            pass
        else:
            queryset = queryset.none()
        
        # Filter by draft_request if provided
        draft_request_id = self.request.query_params.get('draft_request_id')
        if draft_request_id:
            queryset = queryset.filter(draft_request_id=draft_request_id)
        
        # Filter by order if provided
        order_id = self.request.query_params.get('order_id')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        
        return queryset
    
    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        """
        Download a draft file.
        """
        draft_file = self.get_object()
        
        # Check permissions
        if request.user.role not in ['admin', 'superadmin', 'support']:
            if request.user.role == 'client':
                if draft_file.draft_request.requested_by != request.user:
                    return Response(
                        {"error": "You can only download drafts you requested"},
                        status=status.HTTP_403_FORBIDDEN
                    )
            elif request.user.role == 'writer':
                if draft_file.uploaded_by != request.user and draft_file.order.assigned_writer != request.user:
                    return Response(
                        {"error": "You can only download drafts you uploaded or for your assigned orders"},
                        status=status.HTTP_403_FORBIDDEN
                    )
        
        if not draft_file.is_visible_to_client and request.user.role == 'client':
            return Response(
                {"error": "This draft is not visible to clients"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        from django.http import FileResponse
        response = FileResponse(
            draft_file.file.open(),
            content_type='application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{draft_file.file_name}"'
        return response


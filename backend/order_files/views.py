from rest_framework import viewsets, permissions, serializers, status  # Make sure serializers is imported here
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import (
    OrderFile, FileDeletionRequest, ExternalFileLink, ExtraServiceFile,
    OrderFilesConfig, OrderFileCategory, FileDownloadLog, StyleReferenceFile,
)
from .serializers import (
    OrderFileSerializer, FileDeletionRequestSerializer, ExternalFileLinkSerializer,
    ExtraServiceFileSerializer, OrderFilesConfigSerializer, OrderFileCategorySerializer,
    FileDownloadLogSerializer, StyleReferenceFileSerializer,
)
from .permissions import (
    CanDownloadFile, IsAdminOrSupport, IsEditorOrSupport, CanUploadFile
)

class OrderFileViewSet(viewsets.ModelViewSet):
    queryset = OrderFile.objects.all()
    serializer_class = OrderFileSerializer
    permission_classes = [permissions.IsAuthenticated, CanUploadFile, CanDownloadFile]

    def retrieve(self, request, pk=None):
        """View details of a specific file."""
        file = get_object_or_404(OrderFile, pk=pk)
        if file.check_download_access(request.user):
            return Response(OrderFileSerializer(file).data)
        return Response({"error": "Download not allowed"}, status=403)

    def get_queryset(self):
        """Filter files by current website if applicable and user permissions."""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Try to filter by website from request if available
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        
        # Filter by order if specified
        order_id = self.request.query_params.get('order')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        
        # Admins, editors, and support can see all files
        if user.is_staff or user.groups.filter(name__in=["Support", "Editor"]).exists():
            return queryset
        
        # Writers can see files for orders they're assigned to or have requested
        if hasattr(user, 'role') and user.role == 'writer':
            from writer_management.models.requests import WriterOrderRequest
            try:
                writer_profile = user.writer_profile
                # Get orders the writer is assigned to or has requested
                requested_orders = WriterOrderRequest.objects.filter(
                    writer=writer_profile
                ).values_list('order_id', flat=True)
                
                queryset = queryset.filter(
                    Q(order__assigned_writer=user) |
                    Q(order_id__in=requested_orders)
                )
            except Exception:
                # Fallback to assigned orders only
                queryset = queryset.filter(order__assigned_writer=user)
        
        # Clients can see files for their orders
        if hasattr(user, 'role') and user.role == 'client':
            queryset = queryset.filter(order__client=user)
        
        return queryset
    
    def perform_create(self, serializer):
        """Ensures file upload is done by authorized users only."""
        # Get website from order or request context
        order = serializer.validated_data.get('order')
        website = order.website if order else None
        
        config = OrderFilesConfig.get_config(website=website)
        
        file_obj = self.request.FILES["file"]
        
        # Enforce file size limit
        max_size_mb = config.max_upload_size if config else 100
        if file_obj.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(
                f"File too large. Max size is {max_size_mb}MB."
            )
        
        # Validate file extension if config has restrictions
        if config.allowed_extensions:
            file_ext = file_obj.name.split('.')[-1].lower() if '.' in file_obj.name else ''
            if file_ext and file_ext not in [ext.lower().lstrip('.') for ext in config.allowed_extensions]:
                raise serializers.ValidationError(
                    f"File extension '{file_ext}' not allowed. "
                    f"Allowed extensions: {', '.join(config.allowed_extensions)}"
                )
        
        # Set website from order if not already set
        if not website and order:
            website = order.website
        
        serializer.save(uploaded_by=self.request.user, website=website)

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        """Download a file if user has access."""
        from .models import FileDownloadLog
        
        file = get_object_or_404(OrderFile, pk=pk)
        
        if not file.check_download_access(request.user):
            return Response({"error": "Download not allowed"}, status=403)
        
        if not file.file:
            raise Http404("File not found")
        
        try:
            # Log the download
            FileDownloadLog.objects.create(
                website=file.website,
                file=file,
                downloaded_by=request.user
            )
            
            # If writer downloaded, mark in acknowledgment
            if getattr(request.user, "role", None) == 'writer' and getattr(file.order, "assigned_writer", None) == request.user:
                from orders.models import WriterAssignmentAcknowledgment
                acknowledgment = WriterAssignmentAcknowledgment.objects.filter(
                    order=file.order,
                    writer=request.user
                ).first()
                if acknowledgment:
                    acknowledgment.mark_file_downloaded()
            
            response = FileResponse(file.file.open(), content_type='application/octet-stream')
            file_name = file.file.name.split('/')[-1] if '/' in file.file.name else file.file.name
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
        except Exception as e:
            return Response({"error": f"Failed to download file: {str(e)}"}, status=500)
    
    def perform_destroy(self, instance):
        """Only admin/superadmin/support can delete files when order is in progress.
        Clients and writers must request deletion."""
        from rest_framework.exceptions import PermissionDenied
        
        user = self.request.user
        user_role = getattr(user, 'role', None)
        order = instance.order
        
        # Check if order is in progress
        order_in_progress = order.status in ['in_progress', 'revision', 'paid', 'assigned']
        
        # Only admins/superadmin/support can delete when order is in progress
        if order_in_progress:
            if not (user_role in ['admin', 'superadmin', 'support'] or user.is_staff):
                raise PermissionDenied(
                    "Only administrators and support staff can delete files when an order is in progress. "
                    "Please request deletion instead."
                )
        
        # If order is not in progress, check if user has permission
        # Admins/support can always delete
        if not (user_role in ['admin', 'superadmin', 'support'] or user.is_staff):
            # Writers can delete their own uploads if order is not in progress
            if user_role == 'writer' and instance.uploaded_by == user and not order_in_progress:
                pass  # Allow deletion
            # Clients can delete files they uploaded if order is not in progress
            elif user_role == 'client' and instance.uploaded_by == user and not order_in_progress:
                pass  # Allow deletion
            else:
                raise PermissionDenied(
                    "You do not have permission to delete this file. Please request deletion instead."
                )
        
        # Delete the file
        instance.file.delete(save=False)
        instance.delete()
    
    @action(detail=True, methods=["post"])
    def request_deletion(self, request, pk=None):
        """Allows clients and writers to request file deletion."""
        from rest_framework.exceptions import PermissionDenied
        
        file = get_object_or_404(OrderFile, pk=pk)
        user = request.user
        user_role = getattr(user, 'role', None)
        
        # Only clients and writers can request deletion
        if user_role not in ['client', 'writer']:
            raise PermissionDenied("Only clients and writers can request file deletion.")
        
        # Check if user has access to this file's order
        if user_role == 'client' and file.order.client != user:
            raise PermissionDenied("You can only request deletion for files in your orders.")
        
        if user_role == 'writer' and file.order.assigned_writer != user:
            raise PermissionDenied("You can only request deletion for files in orders assigned to you.")
        
        # Check if deletion request already exists
        existing_request = FileDeletionRequest.objects.filter(
            file=file,
            status='pending'
        ).first()
        
        if existing_request:
            return Response({
                "message": "A deletion request for this file is already pending.",
                "request_id": existing_request.id
            }, status=status.HTTP_200_OK)
        
        # Create deletion request
        reason = request.data.get('reason', '')
        deletion_request = FileDeletionRequest.objects.create(
            website=file.website,
            file=file,
            requested_by=user,
            status='pending'
        )
        
        # Store reason if provided (we may need to add a reason field to the model)
        # For now, we'll use the description field if it exists
        
        return Response({
            "message": "Deletion request submitted successfully. An admin will review it.",
            "request_id": deletion_request.id
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=["get"])
    def access_history(self, request, pk=None):
        """Get file access/download history. Only accessible to admin/superadmin/support."""
        from rest_framework.exceptions import PermissionDenied
        
        file = get_object_or_404(OrderFile, pk=pk)
        user = request.user
        user_role = getattr(user, 'role', None)
        
        # Only admins/superadmin/support can view access history
        if not (user_role in ['admin', 'superadmin', 'support'] or user.is_staff):
            raise PermissionDenied("Only administrators and support staff can view file access history.")
        
        # Get download logs for this file
        download_logs = FileDownloadLog.objects.filter(
            file=file
        ).select_related('downloaded_by').order_by('-downloaded_at')
        
        # Serialize the logs
        from .serializers import FileDownloadLogSerializer
        serializer = FileDownloadLogSerializer(download_logs, many=True)
        
        return Response({
            "file_id": file.id,
            "file_name": file.file.name.split('/')[-1] if file.file else "Unknown",
            "order_id": file.order.id,
            "total_downloads": download_logs.count(),
            "downloads": serializer.data
        })
    
    @action(detail=True, methods=["post"])
    def toggle_download(self, request, pk=None):
        """Allows Admins & Support to enable/disable file downloads."""
        file = get_object_or_404(OrderFile, pk=pk)
        
        if request.user.role in ['admin', 'superadmin'] or request.user.is_staff:
            file.is_downloadable = not file.is_downloadable
            file.save()
            return Response({"message": "File download status updated!"})
        
        return Response({"error": "Unauthorized"}, status=403)
    
class FileDeletionRequestViewSet(viewsets.ModelViewSet):
    queryset = FileDeletionRequest.objects.all()
    serializer_class = FileDeletionRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupport]

    def perform_create(self, serializer):
        """Enables clients & writers to request deletion of files."""
        serializer.save(requested_by=self.request.user)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Allows Admin or Support to approve deletion requests."""
        from django.utils import timezone
        
        deletion_request = get_object_or_404(FileDeletionRequest, pk=pk)
        user = request.user
        user_role = getattr(user, 'role', None)
        
        if not (user_role in ['admin', 'superadmin', 'support'] or user.is_staff):
            return Response({"error": "Unauthorized"}, status=403)
        
        # Approve and delete the file
        deletion_request.status = "approved"
        deletion_request.reviewed_by = user
        deletion_request.reviewed_at = timezone.now()
        deletion_request.admin_comment = request.data.get('admin_comment', '')
        deletion_request.save()
        
        # Delete the file
        if deletion_request.file.file:
            deletion_request.file.file.delete(save=False)
        deletion_request.file.delete()
        
        return Response({"message": "Deletion request approved and file deleted!"})
    
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Allows Admin or Support to reject deletion requests."""
        from django.utils import timezone
        
        deletion_request = get_object_or_404(FileDeletionRequest, pk=pk)
        user = request.user
        user_role = getattr(user, 'role', None)
        
        if not (user_role in ['admin', 'superadmin', 'support'] or user.is_staff):
            return Response({"error": "Unauthorized"}, status=403)
        
        deletion_request.status = "rejected"
        deletion_request.reviewed_by = user
        deletion_request.reviewed_at = timezone.now()
        deletion_request.admin_comment = request.data.get('admin_comment', 'Deletion request rejected')
        deletion_request.save()
        
        return Response({"message": "Deletion request rejected!"})

class ExternalFileLinkViewSet(viewsets.ModelViewSet):
    queryset = ExternalFileLink.objects.all()
    serializer_class = ExternalFileLinkSerializer
    permission_classes = [permissions.IsAuthenticated]  # All authenticated users can create links

    def perform_create(self, serializer):
        """Allows all authenticated users to submit external file links."""
        serializer.save(uploaded_by=self.request.user)
    
    def get_queryset(self):
        """Filter links by order if provided."""
        queryset = super().get_queryset()
        order_id = self.request.query_params.get('order')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        return queryset

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Allows Admin or Support to approve external file links."""
        link = get_object_or_404(ExternalFileLink, pk=pk)
        # Check if user is admin or superadmin
        if request.user.role in ['admin', 'superadmin'] or request.user.is_staff:
            link.status = "approved"
            link.reviewed_by = request.user
            link.save()
            return Response({"message": "External link approved!"})
        
        return Response({"error": "Unauthorized"}, status=403)
    
    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        """Allows Admin or Support to reject external file links."""
        link = get_object_or_404(ExternalFileLink, pk=pk)
        # Check if user is admin or superadmin
        if request.user.role in ['admin', 'superadmin'] or request.user.is_staff:
            link.status = "rejected"
            link.reviewed_by = request.user
            link.save()
            return Response({"message": "External link rejected!"})
        
        return Response({"error": "Unauthorized"}, status=403)

class ExtraServiceFileViewSet(viewsets.ModelViewSet):
    queryset = ExtraServiceFile.objects.all()
    serializer_class = ExtraServiceFileSerializer
    permission_classes = [permissions.IsAuthenticated, CanUploadFile]

    def get_queryset(self):
        """Filter extra service files based on user permissions."""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admins, editors, and support can see all
        if user.is_staff or user.groups.filter(name__in=["Support", "Editor"]).exists():
            return queryset
        
        # Filter by order if specified
        order_id = self.request.query_params.get('order')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        
        # Writers can see extra service files for orders they're assigned to or have requested
        if hasattr(user, 'role') and user.role == 'writer':
            from writer_management.models.requests import WriterOrderRequest
            try:
                writer_profile = user.writer_profile
                # Get orders the writer is assigned to or has requested
                requested_orders = WriterOrderRequest.objects.filter(
                    writer=writer_profile
                ).values_list('order_id', flat=True)
                
                queryset = queryset.filter(
                    Q(order__assigned_writer=user) |
                    Q(order_id__in=requested_orders)
                )
            except Exception:
                # Fallback to assigned orders only
                queryset = queryset.filter(order__assigned_writer=user)
        
        # Clients can see extra service files for their orders
        if hasattr(user, 'role') and user.role == 'client':
            queryset = queryset.filter(order__client=user)
        
        return queryset

    def perform_create(self, serializer):
        """Allows writers to upload Extra Service files (e.g., Plagiarism Reports)."""
        serializer.save(uploaded_by=self.request.user)

    @action(detail=True, methods=["post"])
    def toggle_download(self, request, pk=None):
        """Allows Admins & Support to enable/disable download for extra service files."""
        file = get_object_or_404(ExtraServiceFile, pk=pk)
        
        if request.user.is_staff or request.user.groups.filter(name__in=["Support", "Editor"]).exists():
            file.is_downloadable = not file.is_downloadable
            file.save()
            return Response({"message": "Extra service file download status updated!"})
        
        return Response({"error": "Unauthorized"}, status=403)

class OrderFilesConfigViewSet(viewsets.ModelViewSet):
    queryset = OrderFilesConfig.objects.all()
    serializer_class = OrderFilesConfigSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        """Allow Admins to create or update order files config."""
        serializer.save()

class OrderFileCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing file categories.

    - Admins/superadmins can create/update/delete categories.
    - All authenticated users can list categories (for upload dropdowns).
    """
    queryset = OrderFileCategory.objects.all()
    serializer_class = OrderFileCategorySerializer

    def get_permissions(self):
        # Safe methods (GET, HEAD, OPTIONS) → any authenticated user
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return [permissions.IsAuthenticated()]
        # Mutating methods → admin / superadmin / staff only
        if getattr(self.request.user, 'role', None) in ['admin', 'superadmin'] or self.request.user.is_staff:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

    def get_queryset(self):
        """
        Return categories for a website:
        - Universal categories (website=None) - available to all websites
        - Website-specific categories (website=website_id) - only for that website
        """
        queryset = super().get_queryset()
        website_id = self.request.query_params.get('website_id')
        
        if website_id:
            # Return universal categories (website=None) + website-specific categories
            from django.db.models import Q
            queryset = queryset.filter(
                Q(website__isnull=True) | Q(website_id=website_id)
            ).distinct()
        else:
            # If no website_id provided, return all categories (for admin management)
            pass
        
        return queryset.order_by('website', 'name')  # Universal first, then by name


class FileDownloadLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing file download logs.
    Only accessible to admin, superadmin, and support staff.
    """
    serializer_class = FileDownloadLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['file__order', 'downloaded_by', 'file']
    search_fields = ['file__order__id', 'downloaded_by__username', 'downloaded_by__email']
    ordering_fields = ['downloaded_at']
    ordering = ['-downloaded_at']
    
    def get_queryset(self):
        """Only staff can view download logs."""
        user = self.request.user
        
        if not (user.is_staff or getattr(user, "role", None) in ['admin', 'superadmin', 'support']):
            return FileDownloadLog.objects.none()
        
        queryset = FileDownloadLog.objects.select_related(
            'file', 'file__order', 'downloaded_by', 'website'
        )
        
        # Filter by order if specified
        order_id = self.request.query_params.get('order_id')
        if order_id:
            queryset = queryset.filter(file__order_id=order_id)
        
        # Filter by writer if specified
        writer_id = self.request.query_params.get('writer_id')
        if writer_id:
            queryset = queryset.filter(downloaded_by_id=writer_id)
        
        return queryset
    
    @action(detail=False, methods=['get'], url_path='by-order/(?P<order_id>[^/.]+)')
    def by_order(self, request, order_id=None):
        """Get all download logs for a specific order."""
        logs = self.get_queryset().filter(file__order_id=order_id)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='by-writer/(?P<writer_id>[^/.]+)')
    def by_writer(self, request, writer_id=None):
        """Get all download logs for a specific writer."""
        logs = self.get_queryset().filter(downloaded_by_id=writer_id)
        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """Get download statistics."""
        from django.db.models import Count
        from django.utils import timezone
        from datetime import timedelta
        
        queryset = self.get_queryset()
        
        # Total downloads
        total_downloads = queryset.count()
        
        # Downloads in last 24 hours
        last_24h = queryset.filter(
            downloaded_at__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        # Downloads in last 7 days
        last_7d = queryset.filter(
            downloaded_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Downloads by user role
        downloads_by_role = queryset.values(
            'downloaded_by__role'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Most downloaded files
        most_downloaded = queryset.values(
            'file__id',
            'file__order__id'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return Response({
            'total_downloads': total_downloads,
            'last_24_hours': last_24h,
            'last_7_days': last_7d,
            'downloads_by_role': list(downloads_by_role),
            'most_downloaded_files': list(most_downloaded),
        })


class StyleReferenceFileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing style reference files uploaded by clients.
    
    - Clients can upload style reference files for their orders
    - Writers assigned to the order can view and download these files
    - Admins and support can manage all style reference files
    """
    queryset = StyleReferenceFile.objects.all()
    serializer_class = StyleReferenceFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['order', 'reference_type', 'uploaded_by']
    search_fields = ['file_name', 'description', 'order__topic']
    ordering_fields = ['uploaded_at', 'file_name']
    ordering = ['-uploaded_at']
    
    def get_serializer_context(self):
        """Add request to serializer context."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        """Filter style references based on user permissions."""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admins, editors, and support can see all
        if user.is_staff or user.groups.filter(name__in=["Support", "Editor"]).exists():
            return queryset
        
        # Filter by order if specified
        order_id = self.request.query_params.get('order')
        if order_id:
            queryset = queryset.filter(order_id=order_id)
        
        # Clients can see their own uploads
        if hasattr(user, 'role') and user.role == 'client':
            queryset = queryset.filter(uploaded_by=user)
        
        # Writers can see style references for orders they're assigned to
        if hasattr(user, 'role') and user.role == 'writer':
            queryset = queryset.filter(
                order__assigned_writer=user,
                is_visible_to_writer=True
            )
        
        return queryset
    
    def perform_create(self, serializer):
        """Ensure only clients can upload style references for their orders."""
        order = serializer.validated_data.get('order')
        user = self.request.user
        
        # Validate that user is the client or admin
        if order and order.client != user:
            if not (user.is_staff or user.role in ['admin', 'superadmin']):
                raise serializers.ValidationError(
                    "Only the client who placed the order can upload style reference files."
                )
        
        # Auto-set file_name and file_size
        file_obj = self.request.FILES.get('file')
        if file_obj:
            serializer.validated_data['file_name'] = file_obj.name
            serializer.validated_data['file_size'] = file_obj.size
        
        serializer.save(uploaded_by=user)
    
    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        """Download a style reference file if user has access."""
        style_ref = get_object_or_404(StyleReferenceFile, pk=pk)
        
        if not style_ref.can_access(request.user):
            return Response(
                {"error": "You do not have permission to download this file."},
                status=403
            )
        
        if not style_ref.file:
            raise Http404("File not found")
        
        try:
            response = FileResponse(
                style_ref.file.open(),
                content_type='application/octet-stream'
            )
            file_name = style_ref.file_name or style_ref.file.name.split('/')[-1]
            response['Content-Disposition'] = f'attachment; filename="{file_name}"'
            return response
        except Exception as e:
            return Response(
                {"error": f"Failed to download file: {str(e)}"},
                status=500
            )
    
    @action(detail=True, methods=["post"])
    def toggle_visibility(self, request, pk=None):
        """Allow clients to toggle visibility of style reference to writer."""
        style_ref = get_object_or_404(StyleReferenceFile, pk=pk)
        user = request.user
        
        # Only the client who uploaded or admin can toggle visibility
        if style_ref.uploaded_by == user or user.is_staff or user.role in ['admin', 'superadmin']:
            style_ref.is_visible_to_writer = not style_ref.is_visible_to_writer
            style_ref.save()
            return Response({
                "message": "Visibility updated!",
                "is_visible_to_writer": style_ref.is_visible_to_writer
            })
        
        return Response({"error": "Unauthorized"}, status=403)
from rest_framework import viewsets, permissions, serializers, status  # Make sure serializers is imported here
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import (
    OrderFile, FileDeletionRequest, ExternalFileLink, ExtraServiceFile,
    OrderFilesConfig, OrderFileCategory, FileDownloadLog,
)
from .serializers import (
    OrderFileSerializer, FileDeletionRequestSerializer, ExternalFileLinkSerializer,
    ExtraServiceFileSerializer, OrderFilesConfigSerializer, OrderFileCategorySerializer,
    FileDownloadLogSerializer,
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
        """Filter files by current website if applicable."""
        queryset = super().get_queryset()
        # Try to filter by website from request if available
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
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
        deletion_request = get_object_or_404(FileDeletionRequest, pk=pk)
        if request.user.is_staff or request.user.groups.filter(name="Support").exists():
            deletion_request.status = "approved"
            deletion_request.save()
            return Response({"message": "Deletion request approved!"})
        
        return Response({"error": "Unauthorized"}, status=403)

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
        """Filter categories by website if available."""
        queryset = super().get_queryset()
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        return queryset


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
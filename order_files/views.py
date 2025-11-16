from rest_framework import viewsets, permissions, serializers, status  # Make sure serializers is imported here
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from .models import (
    OrderFile, FileDeletionRequest, ExternalFileLink, ExtraServiceFile, OrderFilesConfig, OrderFileCategory
)
from .serializers import (
    OrderFileSerializer, FileDeletionRequestSerializer, ExternalFileLinkSerializer, ExtraServiceFileSerializer, OrderFilesConfigSerializer, OrderFileCategorySerializer
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
        file = get_object_or_404(OrderFile, pk=pk)
        
        if not file.check_download_access(request.user):
            return Response({"error": "Download not allowed"}, status=403)
        
        if not file.file:
            raise Http404("File not found")
        
        try:
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

class OrderFileCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for listing file categories (read-only for all authenticated users)."""
    queryset = OrderFileCategory.objects.all()
    serializer_class = OrderFileCategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter categories by website if available."""
        queryset = super().get_queryset()
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        return queryset
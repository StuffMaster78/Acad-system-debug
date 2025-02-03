from rest_framework import viewsets, permissions, serializers  # Make sure serializers is imported here
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import (
    OrderFile, FileDeletionRequest, ExternalFileLink, ExtraServiceFile, OrderFilesConfig
)
from .serializers import (
    OrderFileSerializer, FileDeletionRequestSerializer, ExternalFileLinkSerializer, ExtraServiceFileSerializer, OrderFilesConfigSerializer
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

    def perform_create(self, serializer):
        """Ensures file upload is done by authorized users only."""
        config = OrderFilesConfig.get_config()
        
        # Enforce file size limit
        max_size_mb = config.max_upload_size if config else 100
        if self.request.FILES["file"].size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(f"File too large. Max size is {max_size_mb}MB.")
        
        serializer.save(uploaded_by=self.request.user)

    @action(detail=True, methods=["post"])
    def toggle_download(self, request, pk=None):
        """Allows Admins & Support to enable/disable file downloads."""
        file = get_object_or_404(OrderFile, pk=pk)
        
        if request.user.is_staff or request.user.groups.filter(name__in=["Support", "Editor"]).exists():
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
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupport]

    def perform_create(self, serializer):
        """Allows clients and writers to submit external file links."""
        serializer.save(uploaded_by=self.request.user)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Allows Admin or Support to approve external file links."""
        link = get_object_or_404(ExternalFileLink, pk=pk)
        if request.user.is_staff or request.user.groups.filter(name="Support").exists():
            link.status = "approved"
            link.reviewed_by = request.user
            link.save()
            return Response({"message": "External link approved!"})
        
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
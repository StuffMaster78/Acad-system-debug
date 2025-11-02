"""
Views for service page PDF sample sections and downloads.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse, Http404
import os

from ..models.pdf_samples import (
    ServicePagePDFSampleSection, ServicePagePDFSample, ServicePagePDFSampleDownload
)
from ..serializers.pdf_serializers import (
    ServicePagePDFSampleSectionSerializer, ServicePagePDFSampleSerializer
)


class ServicePagePDFSampleSectionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing service page PDF sample sections."""
    queryset = ServicePagePDFSampleSection.objects.all()
    serializer_class = ServicePagePDFSampleSectionSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['service_page', 'is_active']
    
    def get_queryset(self):
        """Filter by service page if page_id is provided."""
        queryset = super().get_queryset()
        page_id = self.request.query_params.get('page_id')
        if page_id:
            queryset = queryset.filter(service_page_id=page_id)
        return queryset.select_related('service_page').prefetch_related('pdf_samples')


class ServicePagePDFSampleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing service page PDF samples."""
    queryset = ServicePagePDFSample.objects.all()
    serializer_class = ServicePagePDFSampleSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['section', 'is_active', 'is_featured']
    
    def get_queryset(self):
        """Optimize queryset."""
        return super().get_queryset().select_related('section', 'section__service_page', 'uploaded_by')
    
    def perform_create(self, serializer):
        """Set uploaded_by to current user."""
        serializer.save(uploaded_by=self.request.user)
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def download(self, request, pk=None):
        """Download a PDF sample."""
        try:
            pdf_sample = self.get_object()
        except ServicePagePDFSample.DoesNotExist:
            raise Http404("PDF sample not found")
        
        if not pdf_sample.is_active:
            return Response(
                {"error": "This PDF is not available for download."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if pdf_sample.section.requires_auth and not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required to download this PDF."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        if not pdf_sample.pdf_file or not os.path.exists(pdf_sample.pdf_file.path):
            return Response(
                {"error": "PDF file not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Track download
        ServicePagePDFSampleDownload.objects.create(
            pdf_sample=pdf_sample,
            user=request.user if request.user.is_authenticated else None,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            session_id=request.session.session_key or ''
        )
        
        pdf_sample.increment_download()
        
        try:
            import re
            file_handle = open(pdf_sample.pdf_file.path, 'rb')
            response = FileResponse(
                file_handle,
                content_type='application/pdf'
            )
            # Clean filename for download
            safe_filename = re.sub(r'[^\w\s-]', '', pdf_sample.title).strip()
            safe_filename = re.sub(r'[-\s]+', '-', safe_filename)
            response['Content-Disposition'] = f'attachment; filename="{safe_filename}.pdf"'
            return response
        except (OSError, IOError):
            return Response(
                {"error": "PDF file could not be accessed."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def popular(self, request):
        """Get most downloaded PDF samples."""
        limit = int(request.query_params.get('limit', 10))
        pdfs = self.get_queryset().order_by('-download_count')[:limit]
        serializer = self.get_serializer(pdfs, many=True)
        return Response(serializer.data)


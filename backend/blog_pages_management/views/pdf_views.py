"""
Views for PDF sample sections and downloads.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse, Http404
from django.utils import timezone
import os

from ..models.pdf_samples import (
    PDFSampleSection, PDFSample, PDFSampleDownload
)
from ..serializers.pdf_serializers import (
    PDFSampleSectionSerializer, PDFSampleSerializer, PDFSampleDownloadSerializer
)


class PDFSampleSectionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing PDF sample sections."""
    queryset = PDFSampleSection.objects.all()
    serializer_class = PDFSampleSectionSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['blog', 'is_active']
    
    def get_queryset(self):
        """Filter by blog if blog_id is provided."""
        queryset = super().get_queryset()
        blog_id = self.request.query_params.get('blog_id')
        if blog_id:
            queryset = queryset.filter(blog_id=blog_id)
        return queryset.select_related('blog').prefetch_related('pdf_samples')


class PDFSampleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing PDF samples."""
    queryset = PDFSample.objects.all()
    serializer_class = PDFSampleSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['section', 'is_active', 'is_featured']
    
    def get_queryset(self):
        """Optimize queryset."""
        return super().get_queryset().select_related('section', 'section__blog', 'uploaded_by')
    
    def perform_create(self, serializer):
        """Set uploaded_by to current user."""
        serializer.save(uploaded_by=self.request.user)
    
    @action(detail=True, methods=['get'], permission_classes=[AllowAny])
    def download(self, request, pk=None):
        """
        Download a PDF sample.
        Tracks the download and increments the counter.
        """
        try:
            pdf_sample = self.get_object()
        except PDFSample.DoesNotExist:
            raise Http404("PDF sample not found")
        
        # Check if PDF is active
        if not pdf_sample.is_active:
            return Response(
                {"error": "This PDF is not available for download."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check authentication requirement
        if pdf_sample.section.requires_auth and not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required to download this PDF."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if file exists
        if not pdf_sample.pdf_file or not os.path.exists(pdf_sample.pdf_file.path):
            return Response(
                {"error": "PDF file not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Track download
        PDFSampleDownload.objects.create(
            pdf_sample=pdf_sample,
            user=request.user if request.user.is_authenticated else None,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            session_id=request.session.session_key or ''
        )
        
        # Increment download counter
        pdf_sample.increment_download()
        
        # Return file response
        try:
            file_handle = open(pdf_sample.pdf_file.path, 'rb')
            response = FileResponse(
                file_handle,
                content_type='application/pdf'
            )
            # Clean filename for download
            import re
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


class PDFSampleDownloadViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing PDF download analytics."""
    queryset = PDFSampleDownload.objects.all()
    serializer_class = PDFSampleDownloadSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['pdf_sample', 'user', 'pdf_sample__section__blog']
    
    def get_queryset(self):
        """Optimize queryset."""
        return super().get_queryset().select_related(
            'pdf_sample', 'pdf_sample__section', 'pdf_sample__section__blog', 'user'
        )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get download statistics."""
        pdf_id = request.query_params.get('pdf_id')
        blog_id = request.query_params.get('blog_id')
        
        queryset = self.get_queryset()
        
        if pdf_id:
            queryset = queryset.filter(pdf_sample_id=pdf_id)
        elif blog_id:
            queryset = queryset.filter(pdf_sample__section__blog_id=blog_id)
        
        total_downloads = queryset.count()
        unique_users = queryset.filter(user__isnull=False).values('user').distinct().count()
        unique_ips = queryset.filter(ip_address__isnull=False).values('ip_address').distinct().count()
        
        return Response({
            'total_downloads': total_downloads,
            'unique_users': unique_users,
            'unique_ips': unique_ips,
        })


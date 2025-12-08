"""
Views for SEO Pages.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from .models import SeoPage
from .serializers import SeoPageSerializer, PublicSeoPageSerializer
from websites.models import Website


class SeoPageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SEO Pages (admin/internal use).
    """
    queryset = SeoPage.objects.filter(is_deleted=False)
    serializer_class = SeoPageSerializer
    
    def get_queryset(self):
        qs = super().get_queryset()
        website_id = self.request.query_params.get('website_id')
        if website_id:
            qs = qs.filter(website_id=website_id)
        return qs
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
    
    @action(detail=True, methods=['get'], url_path='preview')
    def preview(self, request, pk=None):
        """
        Preview an SEO page as it will appear publicly.
        Accessible to authenticated users (admins, content creators).
        Works for both published and draft pages.
        """
        page = self.get_object()
        
        # Check permissions - user must have access to this page's website
        user = request.user
        if user.role not in ['superadmin', 'admin']:
            user_website = getattr(user, 'website', None)
            if user_website and page.website != user_website:
                return Response(
                    {'error': 'You do not have permission to preview this page'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Use public serializer to show how it will appear
        serializer = PublicSeoPageSerializer(page, context={'request': request})
        
        return Response({
            'preview': True,
            'is_internal_preview': True,
            'is_published': page.is_published,
            'page': serializer.data
        }, status=status.HTTP_200_OK)


class PublicSeoPageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public read-only ViewSet for SEO Pages.
    Exposes published pages via slug.
    """
    permission_classes = [AllowAny]
    serializer_class = PublicSeoPageSerializer
    lookup_field = 'slug'
    
    def get_queryset(self):
        return SeoPage.objects.filter(
            is_published=True,
            is_deleted=False
        )
    
    @action(detail=False, methods=['get'], url_path='by-slug/(?P<slug>[^/.]+)')
    def by_slug(self, request, slug=None):
        """
        Get a published SEO page by slug.
        
        Query params:
        - website_id (optional): Filter by website
        """
        website_id = request.query_params.get('website_id')
        
        queryset = self.get_queryset()
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        
        page = get_object_or_404(queryset, slug=slug)
        serializer = self.get_serializer(page)
        return Response(serializer.data)


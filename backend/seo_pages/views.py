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


class SeoPageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SEO Pages (admin/internal use).
    """
    serializer_class = SeoPageSerializer

    def get_queryset(self):
        qs = SeoPage.objects.filter(is_deleted=False)
        user = self.request.user

        if not user.is_authenticated:
            return qs.none()

        # Superadmin sees all tenants; optional website_id narrows further.
        if getattr(user, 'role', None) == 'superadmin' or getattr(user, 'is_superuser', False):
            website_id = self.request.query_params.get('website_id')
            if website_id:
                qs = qs.filter(website_id=website_id)
            return qs

        # All other staff are scoped to the website resolved from the host,
        # falling back to the website assigned to their user account.
        website = (
            getattr(self.request, 'website', None)
            or getattr(user, 'website', None)
        )
        if website:
            return qs.filter(website=website)

        return qs.none()

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

    Scoped to the website resolved from the request host by
    PortalTenantResolverMiddleware — a slug on site A never leaks to site B.
    """
    permission_classes = [AllowAny]
    serializer_class = PublicSeoPageSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        qs = SeoPage.objects.filter(is_published=True, is_deleted=False)
        # Always scope to the host-resolved website so slugs are tenant-isolated.
        # If no website resolves (unknown host, dev localhost) return nothing —
        # public SEO content must never leak across tenant boundaries.
        website = getattr(self.request, 'website', None)
        if website is None:
            return qs.none()
        return qs.filter(website=website)

    @action(detail=False, methods=['get'], url_path='by-slug/(?P<slug>[^/.]+)')
    def by_slug(self, request, slug=None):
        """GET a published SEO page by slug, scoped to the current domain."""
        page = get_object_or_404(self.get_queryset(), slug=slug)
        return Response(self.get_serializer(page).data)


"""
ViewSets for Tenant Features
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from websites.models.tenant_features import TenantBranding, TenantFeatureToggle
from websites.serializers.tenant_features import (
    TenantBrandingSerializer, TenantBrandingUpdateSerializer,
    TenantFeatureToggleSerializer, TenantFeatureToggleUpdateSerializer
)
from admin_management.permissions import IsAdmin
from superadmin_management.permissions import IsSuperadmin


class TenantBrandingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tenant branding.
    """
    queryset = TenantBranding.objects.select_related('website').all()
    permission_classes = [permissions.IsAuthenticated, IsAdmin]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['update', 'partial_update']:
            return TenantBrandingUpdateSerializer
        return TenantBrandingSerializer
    
    def get_queryset(self):
        """Filter branding based on website."""
        user = self.request.user
        qs = super().get_queryset()
        
        # Filter by website
        if hasattr(user, 'website') and user.website:
            qs = qs.filter(website=user.website)
        
        # Superadmins can see all
        if user.role == 'superadmin':
            website_id = self.request.query_params.get('website')
            if website_id:
                qs = qs.filter(website_id=website_id)
        
        return qs
    
    def perform_create(self, serializer):
        """Create branding with website from user."""
        user = self.request.user
        website = user.website if hasattr(user, 'website') and user.website else None
        
        if not website:
            return Response(
                {'error': 'User must be associated with a website.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if branding already exists
        if TenantBranding.objects.filter(website=website).exists():
            return Response(
                {'error': 'Branding already exists for this website. Use update instead.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save(website=website)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current branding for user's website."""
        user = request.user
        website = user.website if hasattr(user, 'website') and user.website else None
        
        if not website:
            return Response(
                {'error': 'User must be associated with a website.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        branding, created = TenantBranding.objects.get_or_create(
            website=website,
            defaults={}
        )
        
        return Response(TenantBrandingSerializer(branding).data)


class TenantFeatureToggleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tenant feature toggles.
    """
    queryset = TenantFeatureToggle.objects.select_related('website').all()
    permission_classes = [permissions.IsAuthenticated, IsSuperadmin]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['update', 'partial_update']:
            return TenantFeatureToggleUpdateSerializer
        return TenantFeatureToggleSerializer
    
    def get_queryset(self):
        """Filter toggles based on website."""
        user = self.request.user
        qs = super().get_queryset()
        
        # Filter by website
        if hasattr(user, 'website') and user.website:
            qs = qs.filter(website=user.website)
        
        # Superadmins can see all
        if user.role == 'superadmin':
            website_id = self.request.query_params.get('website')
            if website_id:
                qs = qs.filter(website_id=website_id)
        
        return qs
    
    def perform_create(self, serializer):
        """Create feature toggle with website from user."""
        user = self.request.user
        website = user.website if hasattr(user, 'website') and user.website else None
        
        if not website:
            return Response(
                {'error': 'User must be associated with a website.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if toggle already exists
        if TenantFeatureToggle.objects.filter(website=website).exists():
            return Response(
                {'error': 'Feature toggle already exists for this website. Use update instead.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save(website=website)
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current feature toggles for user's website."""
        user = request.user
        website = user.website if hasattr(user, 'website') and user.website else None
        
        if not website:
            return Response(
                {'error': 'User must be associated with a website.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        toggle, created = TenantFeatureToggle.objects.get_or_create(
            website=website,
            defaults={}
        )
        
        return Response(TenantFeatureToggleSerializer(toggle).data)
    
    @action(detail=True, methods=['get'])
    def check_feature(self, request, pk=None):
        """Check if a specific feature is enabled."""
        toggle = self.get_object()
        feature_name = request.query_params.get('feature')
        
        if not feature_name:
            return Response(
                {'error': 'feature parameter required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_enabled = toggle.is_feature_enabled(feature_name)
        
        return Response({
            'feature': feature_name,
            'enabled': is_enabled
        })


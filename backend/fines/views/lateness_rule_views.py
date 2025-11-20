"""
Views for managing LatenessFineRule configurations.
"""

from django.db import models
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404

from fines.models.late_fine_policy import LatenessFineRule
from fines.serializers.lateness_rule_serializers import LatenessFineRuleSerializer
from authentication.permissions import IsAdminOrSuperAdmin
from websites.utils import get_current_website
from fines.models.fine_type_config import FineTypeConfig
from fines.serializers.fine_type_config_serializers import FineTypeConfigSerializer


class LatenessFineRuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing lateness fine rule configurations.
    Admin-only endpoint.
    """
    queryset = LatenessFineRule.objects.select_related('website', 'created_by')
    serializer_class = LatenessFineRuleSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]
    
    def get_queryset(self):
        """Filter by website if specified."""
        queryset = super().get_queryset()
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        return queryset
    
    def perform_create(self, serializer):
        """Set created_by and website."""
        website = get_current_website(self.request)
        if not website:
            from websites.models import Website
            website = Website.objects.filter(is_active=True).first()
        
        serializer.save(
            created_by=self.request.user,
            website=website
        )
    
    @action(detail=False, methods=['get'])
    def active_rule(self, request):
        """Get active lateness fine rule for current website."""
        website = get_current_website(request)
        if not website:
            return Response(
                {"detail": "Website context required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        rule = LatenessFineRule.objects.filter(
            website=website,
            active=True
        ).order_by('-start_date').first()
        
        if rule:
            serializer = self.get_serializer(rule)
            return Response(serializer.data)
        else:
            return Response({
                "message": "No active rule found. Using default calculation.",
                "defaults": {
                    "first_hour_percentage": "5.00",
                    "second_hour_percentage": "10.00",
                    "third_hour_percentage": "15.00",
                    "subsequent_hours_percentage": "5.00",
                    "daily_rate_percentage": "20.00",
                    "calculation_mode": "cumulative",
                    "base_amount": "writer_compensation"
                }
            })


class FineTypeConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing fine type configurations.
    Admin-only endpoint for creating/managing fine types.
    """
    queryset = FineTypeConfig.objects.select_related('website', 'created_by')
    serializer_class = FineTypeConfigSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSuperAdmin]
    
    def get_queryset(self):
        """Filter by website if specified."""
        queryset = super().get_queryset()
        website_id = self.request.query_params.get('website_id')
        code = self.request.query_params.get('code')
        
        if website_id:
            queryset = queryset.filter(website_id=website_id) | queryset.filter(website__isnull=True)
        if code:
            queryset = queryset.filter(code=code)
        
        return queryset.distinct()
    
    def perform_create(self, serializer):
        """Set created_by and website."""
        website = get_current_website(self.request)
        website_id = self.request.data.get('website_id')
        if website_id and not website:
            from websites.models import Website
            website = Website.objects.filter(id=website_id).first()
        
        serializer.save(
            created_by=self.request.user,
            website=website
        )
    
    @action(detail=False, methods=['get'])
    def available_types(self, request):
        """Get all available fine types for current website."""
        website = get_current_website(request)
        
        queryset = FineTypeConfig.objects.filter(active=True)
        if website:
            # Get website-specific and global types
            queryset = queryset.filter(
                models.Q(website=website) | models.Q(website__isnull=True)
            )
        else:
            # Only global types
            queryset = queryset.filter(website__isnull=True)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


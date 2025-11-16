"""
Configuration management for admin/superadmin.
Allows managing all system configurations (pricing, writer configs, discounts, etc.)
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction

from admin_management.permissions import IsAdmin, IsSuperAdmin
from admin_management.models import AdminActivityLog


class PricingConfigManagementViewSet(viewsets.ModelViewSet):
    """Manage pricing configurations."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        from pricing_configs.models import PricingConfiguration
        queryset = PricingConfiguration.objects.all()
        
        # Filter by website if not superadmin
        if self.request.user.role != 'superadmin':
            website = getattr(self.request.user, 'website', None)
            if website:
                queryset = queryset.filter(website=website)
        
        return queryset
    
    def get_serializer_class(self):
        try:
            from pricing_configs.serializers import PricingConfigurationSerializer
            return PricingConfigurationSerializer
        except ImportError:
            from rest_framework import serializers
            from pricing_configs.models import PricingConfiguration
            
            class PricingConfigurationSerializer(serializers.ModelSerializer):
                class Meta:
                    model = PricingConfiguration
                    fields = '__all__'
            
            return PricingConfigurationSerializer
    
    def perform_create(self, serializer):
        """Create pricing configuration."""
        from rest_framework import serializers as drf_serializers
        website = getattr(self.request.user, 'website', None)
        if not website and self.request.user.role != 'superadmin':
            raise drf_serializers.ValidationError("Website is required.")
        
        if website:
            serializer.save(website=website)
        else:
            serializer.save()
        
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Created pricing configuration",
            details=f"Created pricing config for {serializer.instance.website}"
        )
    
    def perform_update(self, serializer):
        """Update pricing configuration."""
        serializer.save()
        
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Updated pricing configuration",
            details=f"Updated pricing config for {serializer.instance.website}"
        )


class WriterConfigManagementViewSet(viewsets.ModelViewSet):
    """Manage writer configurations."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        from writer_management.models.configs import WriterConfig
        queryset = WriterConfig.objects.all()
        
        # Filter by website if not superadmin
        if self.request.user.role != 'superadmin':
            website = getattr(self.request.user, 'website', None)
            if website:
                queryset = queryset.filter(website=website)
        
        return queryset
    
    def get_serializer_class(self):
        try:
            from writer_management.serializers import WriterConfigSerializer
            return WriterConfigSerializer
        except ImportError:
            from rest_framework import serializers
            from writer_management.models.configs import WriterConfig
            
            class WriterConfigSerializer(serializers.ModelSerializer):
                class Meta:
                    model = WriterConfig
                    fields = '__all__'
            
            return WriterConfigSerializer
    
    def perform_create(self, serializer):
        """Create writer configuration."""
        from rest_framework import serializers as drf_serializers
        website = getattr(self.request.user, 'website', None)
        if not website and self.request.user.role != 'superadmin':
            raise drf_serializers.ValidationError("Website is required.")
        
        if website:
            serializer.save(website=website)
        else:
            serializer.save()
        
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Created writer configuration",
            details=f"Created writer config for {serializer.instance.website}"
        )
    
    def perform_update(self, serializer):
        """Update writer configuration."""
        serializer.save()
        
        AdminActivityLog.objects.create(
            admin=self.request.user,
            action="Updated writer configuration",
            details=f"Updated writer config for {serializer.instance.website}"
        )


class DiscountConfigManagementViewSet(viewsets.ModelViewSet):
    """Manage discount configurations."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        from discounts.models.discount_configs import DiscountConfig
        queryset = DiscountConfig.objects.all()
        
        # Filter by website if not superadmin
        if self.request.user.role != 'superadmin':
            website = getattr(self.request.user, 'website', None)
            if website:
                queryset = queryset.filter(website=website)
        
        return queryset
    
    def get_serializer_class(self):
        try:
            from discounts.serializers import DiscountConfigSerializer
            return DiscountConfigSerializer
        except ImportError:
            from rest_framework import serializers
            from discounts.models.discount_configs import DiscountConfig
            
            class DiscountConfigSerializer(serializers.ModelSerializer):
                class Meta:
                    model = DiscountConfig
                    fields = '__all__'
            
            return DiscountConfigSerializer


class NotificationConfigManagementViewSet(viewsets.ModelViewSet):
    """Manage notification preference profiles."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    def get_queryset(self):
        from notifications_system.models.notification_preferences import NotificationPreferenceProfile
        return NotificationPreferenceProfile.objects.all()
    
    def get_serializer_class(self):
        # Create a simple serializer for notification profiles
        from rest_framework import serializers
        from notifications_system.models.notification_preferences import NotificationPreferenceProfile
        
        class NotificationProfileSerializer(serializers.ModelSerializer):
            class Meta:
                model = NotificationPreferenceProfile
                fields = '__all__'
        
        return NotificationProfileSerializer


class SystemConfigManagementViewSet(viewsets.ViewSet):
    """Manage various system configurations."""
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @action(detail=False, methods=['get'])
    def list_all_configs(self, request):
        """List all available configuration types."""
        website = getattr(request.user, 'website', None)
        
        configs = {
            'pricing_configs': [],
            'writer_configs': [],
            'discount_configs': [],
            'notification_profiles': [],
        }
        
        # Get pricing configs
        from pricing_configs.models import PricingConfiguration
        pricing_qs = PricingConfiguration.objects.all()
        if website and request.user.role != 'superadmin':
            pricing_qs = pricing_qs.filter(website=website)
        configs['pricing_configs'] = [
            {'id': c.id, 'website': c.website.name, 'base_price': str(c.base_price_per_page)}
            for c in pricing_qs[:10]
        ]
        
        # Get writer configs
        from writer_management.models.configs import WriterConfig
        writer_qs = WriterConfig.objects.all()
        if website and request.user.role != 'superadmin':
            writer_qs = writer_qs.filter(website=website)
        configs['writer_configs'] = [
            {'id': c.id, 'website': c.website.name, 'takes_enabled': c.takes_enabled}
            for c in writer_qs[:10]
        ]
        
        # Get discount configs
        from discounts.models.discount_configs import DiscountConfig
        discount_qs = DiscountConfig.objects.all()
        if website and request.user.role != 'superadmin':
            discount_qs = discount_qs.filter(website=website)
        configs['discount_configs'] = [
            {'id': c.id, 'website': getattr(c, 'website', {}).name if hasattr(c, 'website') else 'N/A'}
            for c in discount_qs[:10]
        ]
        
        # Get notification profiles
        from notifications_system.models.notification_preferences import NotificationPreferenceProfile
        configs['notification_profiles'] = [
            {'id': p.id, 'name': p.name, 'is_default': p.is_default}
            for p in NotificationPreferenceProfile.objects.all()[:10]
        ]
        
        return Response(configs)


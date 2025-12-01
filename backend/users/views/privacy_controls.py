"""
Privacy Controls ViewSet - User privacy settings and data access management.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from users.models import PrivacySettings, DataAccessLog
from websites.utils import get_current_website
from authentication.utils.ip import get_client_ip


class PrivacyControlsViewSet(viewsets.ViewSet):
    """
    ViewSet for privacy controls and settings.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='settings')
    def get_settings(self, request):
        """
        Get current privacy settings.
        
        Response:
        {
            "profile_visibility": {
                "to_writers": "limited",
                "to_admins": "public",
                "to_support": "public"
            },
            "data_sharing": {
                "analytics": true,
                "marketing": false,
                "third_party": false
            },
            "notifications": {
                "on_login": true,
                "on_login_method": "email",
                "on_suspicious_activity": true
            },
            "privacy_score": 75
        }
        """
        user = request.user
        settings, _ = PrivacySettings.get_or_create_for_user(user)
        
        return Response({
            "profile_visibility": {
                "to_writers": settings.profile_visibility_to_writers,
                "to_admins": settings.profile_visibility_to_admins,
                "to_support": settings.profile_visibility_to_support,
            },
            "data_sharing": {
                "analytics": settings.allow_analytics,
                "marketing": settings.allow_marketing,
                "third_party": settings.allow_third_party_sharing,
            },
            "notifications": {
                "on_login": settings.notify_on_login,
                "on_login_method": settings.notify_on_login_method,
                "on_suspicious_activity": settings.notify_on_suspicious_activity,
            },
            "privacy_score": settings.calculate_privacy_score()
        })
    
    @action(detail=False, methods=['post'], url_path='update-visibility')
    def update_visibility(self, request):
        """
        Update profile visibility settings.
        
        Request body:
        {
            "to_writers": "limited",
            "to_admins": "public",
            "to_support": "public"
        }
        """
        user = request.user
        settings, _ = PrivacySettings.get_or_create_for_user(user)
        
        if 'to_writers' in request.data:
            settings.profile_visibility_to_writers = request.data['to_writers']
        if 'to_admins' in request.data:
            settings.profile_visibility_to_admins = request.data['to_admins']
        if 'to_support' in request.data:
            settings.profile_visibility_to_support = request.data['to_support']
        
        settings.save()
        
        # Log privacy settings change
        from authentication.models.security_events import SecurityEvent
        website = get_current_website(request)
        if website:
            SecurityEvent.log_event(
                user=user,
                website=website,
                event_type='privacy_settings_changed',
                severity='low',
                ip_address=get_client_ip(request),
                metadata={'visibility_changes': request.data}
            )
        
        return Response({
            "message": "Privacy settings updated",
            "privacy_score": settings.calculate_privacy_score()
        })
    
    @action(detail=False, methods=['post'], url_path='update-data-sharing')
    def update_data_sharing(self, request):
        """
        Update data sharing preferences.
        
        Request body:
        {
            "analytics": true,
            "marketing": false,
            "third_party": false
        }
        """
        user = request.user
        settings, _ = PrivacySettings.get_or_create_for_user(user)
        
        if 'analytics' in request.data:
            settings.allow_analytics = request.data['analytics']
        if 'marketing' in request.data:
            settings.allow_marketing = request.data['marketing']
        if 'third_party' in request.data:
            settings.allow_third_party_sharing = request.data['third_party']
        
        settings.save()
        
        return Response({
            "message": "Data sharing preferences updated",
            "privacy_score": settings.calculate_privacy_score()
        })
    
    @action(detail=False, methods=['get'], url_path='access-log')
    def get_access_log(self, request):
        """
        Get data access log (who accessed user's data).
        
        Query params:
        - limit: Number of entries to return (default: 50)
        - days: Number of days to look back (default: 30)
        """
        user = request.user
        limit = int(request.query_params.get('limit', 50))
        days = int(request.query_params.get('days', 30))
        
        cutoff = timezone.now() - timezone.timedelta(days=days)
        
        logs = DataAccessLog.objects.filter(
            user=user,
            accessed_at__gte=cutoff
        ).select_related('accessed_by')[:limit]
        
        return Response({
            "count": len(logs),
            "logs": [
                {
                    "id": log.id,
                    "accessed_by": {
                        "id": log.accessed_by.id if log.accessed_by else None,
                        "email": log.accessed_by.email if log.accessed_by else "System",
                        "role": log.accessed_by.role if log.accessed_by else None,
                    },
                    "access_type": log.access_type,
                    "accessed_at": log.accessed_at.isoformat(),
                    "ip_address": log.ip_address,
                    "location": log.metadata.get('location'),
                }
                for log in logs
            ]
        })
    
    @action(detail=False, methods=['get'], url_path='export-data')
    def export_data(self, request):
        """
        Export all user data (GDPR compliance).
        
        Response: Comprehensive JSON export of all user data.
        """
        user = request.user
        website = get_current_website(request)
        
        # Collect all user data
        from users.serializers import UserSerializer
        from orders.serializers import OrderSerializer
        from order_payments_management.serializers import OrderPaymentSerializer
        
        export_data = {
            "exported_at": timezone.now().isoformat(),
            "user": UserSerializer(user).data,
            "orders": OrderSerializer(user.orders.all(), many=True).data if hasattr(user, 'orders') else [],
            "payments": [],
            "messages": [],
            "sessions": [],
            "privacy_settings": {},
        }
        
        # Get payments if available
        if hasattr(user, 'payments'):
            export_data["payments"] = OrderPaymentSerializer(user.payments.all(), many=True).data
        
        # Get privacy settings
        try:
            privacy_settings = PrivacySettings.objects.get(user=user)
            export_data["privacy_settings"] = {
                "profile_visibility": {
                    "to_writers": privacy_settings.profile_visibility_to_writers,
                    "to_admins": privacy_settings.profile_visibility_to_admins,
                    "to_support": privacy_settings.profile_visibility_to_support,
                },
                "data_sharing": {
                    "analytics": privacy_settings.allow_analytics,
                    "marketing": privacy_settings.allow_marketing,
                    "third_party": privacy_settings.allow_third_party_sharing,
                }
            }
        except PrivacySettings.DoesNotExist:
            pass
        
        # Log data export
        if website:
            DataAccessLog.objects.create(
                user=user,
                accessed_by=user,  # User accessing their own data
                access_type='data_export',
                ip_address=get_client_ip(request),
                user_agent=request.headers.get('User-Agent', ''),
                metadata={'export_type': 'full'}
            )
        
        return Response(export_data)


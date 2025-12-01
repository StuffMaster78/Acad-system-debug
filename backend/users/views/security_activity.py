"""
Security Activity ViewSet - User security event feed and monitoring.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from authentication.models.security_events import SecurityEvent
from websites.utils import get_current_website


class SecurityActivityViewSet(viewsets.ViewSet):
    """
    ViewSet for security activity feed and monitoring.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='feed')
    def activity_feed(self, request):
        """
        Get security activity feed.
        
        Query params:
        - limit: Number of events to return (default: 50)
        - days: Number of days to look back (default: 30)
        - event_type: Filter by event type
        - suspicious_only: Only show suspicious events (default: false)
        """
        user = request.user
        website = get_current_website(request)
        
        limit = int(request.query_params.get('limit', 50))
        days = int(request.query_params.get('days', 30))
        event_type = request.query_params.get('event_type')
        suspicious_only = request.query_params.get('suspicious_only', 'false').lower() == 'true'
        
        cutoff = timezone.now() - timedelta(days=days)
        
        queryset = SecurityEvent.objects.filter(
            user=user,
            website=website,
            created_at__gte=cutoff
        )
        
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        if suspicious_only:
            queryset = queryset.filter(is_suspicious=True)
        
        events = queryset.order_by('-created_at')[:limit]
        
        # Calculate summary
        all_recent_events = SecurityEvent.objects.filter(
            user=user,
            website=website,
            created_at__gte=cutoff
        )
        
        summary = {
            "total_logins": all_recent_events.filter(event_type='login').count(),
            "failed_attempts": all_recent_events.filter(event_type='login_failed').count(),
            "password_changes": all_recent_events.filter(event_type='password_change').count(),
            "suspicious_activities": all_recent_events.filter(is_suspicious=True).count(),
            "device_changes": all_recent_events.filter(event_type__in=['device_trusted', 'device_revoked']).count(),
        }
        
        return Response({
            "summary": summary,
            "events": [
                {
                    "id": event.id,
                    "event_type": event.event_type,
                    "severity": event.severity,
                    "is_suspicious": event.is_suspicious,
                    "created_at": event.created_at.isoformat(),
                    "location": event.location,
                    "device": event.device,
                    "ip_address": event.ip_address,
                    "metadata": event.metadata,
                }
                for event in events
            ],
            "count": len(events)
        })
    
    @action(detail=False, methods=['get'], url_path='summary')
    def activity_summary(self, request):
        """
        Get security activity summary statistics.
        
        Response:
        {
            "last_30_days": {
                "total_logins": 45,
                "failed_attempts": 2,
                "password_changes": 1,
                "suspicious_activities": 0,
                "device_changes": 3
            },
            "last_login": "2025-12-01T10:00:00Z",
            "last_suspicious_activity": null,
            "security_score": 95
        }
        """
        user = request.user
        website = get_current_website(request)
        
        cutoff_30 = timezone.now() - timedelta(days=30)
        cutoff_7 = timezone.now() - timedelta(days=7)
        
        events_30 = SecurityEvent.objects.filter(
            user=user,
            website=website,
            created_at__gte=cutoff_30
        )
        
        events_7 = SecurityEvent.objects.filter(
            user=user,
            website=website,
            created_at__gte=cutoff_7
        )
        
        # Get last login
        last_login = events_30.filter(event_type='login').first()
        
        # Get last suspicious activity
        last_suspicious = events_30.filter(is_suspicious=True).first()
        
        # Calculate security score (0-100)
        security_score = self._calculate_security_score(user, events_30, events_7)
        
        return Response({
            "last_30_days": {
                "total_logins": events_30.filter(event_type='login').count(),
                "failed_attempts": events_30.filter(event_type='login_failed').count(),
                "password_changes": events_30.filter(event_type='password_change').count(),
                "suspicious_activities": events_30.filter(is_suspicious=True).count(),
                "device_changes": events_30.filter(event_type__in=['device_trusted', 'device_revoked']).count(),
            },
            "last_7_days": {
                "total_logins": events_7.filter(event_type='login').count(),
                "failed_attempts": events_7.filter(event_type='login_failed').count(),
                "suspicious_activities": events_7.filter(is_suspicious=True).count(),
            },
            "last_login": last_login.created_at.isoformat() if last_login else None,
            "last_suspicious_activity": last_suspicious.created_at.isoformat() if last_suspicious else None,
            "security_score": security_score
        })
    
    def _calculate_security_score(self, user, events_30, events_7):
        """
        Calculate security score (0-100).
        Higher score = better security.
        """
        score = 100
        
        # Deduct for failed attempts
        failed_attempts = events_30.filter(event_type='login_failed').count()
        score -= min(failed_attempts * 2, 20)  # Max 20 points deduction
        
        # Deduct for suspicious activities
        suspicious = events_30.filter(is_suspicious=True).count()
        score -= min(suspicious * 10, 30)  # Max 30 points deduction
        
        # Deduct if no 2FA
        if not getattr(user, 'is_2fa_enabled', False) and not getattr(user, 'is_mfa_enabled', False):
            score -= 15
        
        # Deduct if weak password (would need password strength check)
        # For now, assume good if password was changed recently
        recent_password_change = events_30.filter(event_type='password_change').exists()
        if not recent_password_change:
            score -= 5
        
        return max(score, 0)  # Don't go below 0


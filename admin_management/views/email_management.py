"""
Admin views for managing mass emails, digests, and broadcast messages.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Count, Sum
from django.contrib.auth import get_user_model

from authentication.permissions import IsSuperadminOrAdmin
from mass_emails.models import EmailCampaign, EmailRecipient, EmailTemplate
from notifications_system.models.digest_notifications import NotificationDigest
from notifications_system.models.broadcast_notification import BroadcastNotification
from notifications_system.services.digest_service import DigestService
from notifications_system.services.broadcast_services import BroadcastNotificationService
from websites.models import Website

User = get_user_model()


class MassEmailManagementViewSet(viewsets.ModelViewSet):
    """
    Admin interface for managing mass email campaigns.
    """
    queryset = EmailCampaign.objects.all()
    permission_classes = [IsAuthenticated, IsSuperadminOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        queryset = EmailCampaign.objects.select_related('website', 'created_by').prefetch_related('recipients')
        
        # Filter by website if not superadmin
        if user.role != 'superadmin':
            website = getattr(user, 'website', None)
            if website:
                queryset = queryset.filter(website=website)
        
        # Filtering
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        email_type = self.request.query_params.get('email_type')
        if email_type:
            queryset = queryset.filter(email_type=email_type)
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        from mass_emails.serializers import (
            EmailCampaignListSerializer,
            EmailCampaignDetailSerializer,
            EmailCampaignCreateSerializer
        )
        from admin_management.serializers.email_serializers import MassEmailListSerializer
        
        if self.action == 'list':
            return MassEmailListSerializer
        elif self.action == 'retrieve':
            return EmailCampaignDetailSerializer
        return EmailCampaignCreateSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_now(self, request, pk=None):
        """Send campaign immediately."""
        campaign = self.get_object()
        if campaign.status not in ['draft', 'scheduled']:
            return Response(
                {"detail": "Only draft or scheduled campaigns can be sent."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from mass_emails.tasks import send_email_campaign
            campaign.status = 'sending'
            campaign.scheduled_time = timezone.now()
            campaign.save()
            send_email_campaign.delay(campaign.id)
            return Response({"detail": "Campaign sending started."})
        except Exception as e:
            return Response(
                {"detail": f"Failed to start campaign: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        """Schedule campaign for future sending."""
        campaign = self.get_object()
        scheduled_time = request.data.get('scheduled_time')
        if not scheduled_time:
            return Response(
                {"detail": "scheduled_time is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        campaign.scheduled_time = scheduled_time
        campaign.status = 'scheduled'
        campaign.save()
        return Response({"detail": "Campaign scheduled."})
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Get campaign analytics."""
        campaign = self.get_object()
        recipients = campaign.recipients.all()
        
        total = recipients.count()
        sent = recipients.filter(status='sent').count()
        opened = recipients.filter(status='opened').count()
        bounced = recipients.filter(status='bounced').count()
        failed = recipients.filter(status='failed').count()
        
        return Response({
            'total_recipients': total,
            'sent': sent,
            'opened': opened,
            'bounced': bounced,
            'failed': failed,
            'open_rate': (opened / sent * 100) if sent > 0 else 0,
        })


class EmailDigestManagementViewSet(viewsets.ModelViewSet):
    """
    Admin interface for managing email digests.
    """
    queryset = NotificationDigest.objects.all()
    permission_classes = [IsAuthenticated, IsSuperadminOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        queryset = NotificationDigest.objects.select_related('user', 'website')
        
        if user.role != 'superadmin':
            website = getattr(user, 'website', None)
            if website:
                queryset = queryset.filter(website=website)
        
        # Filtering
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        
        is_sent = self.request.query_params.get('is_sent')
        if is_sent is not None:
            queryset = queryset.filter(is_sent=is_sent.lower() == 'true')
        
        event_key = self.request.query_params.get('event_key')
        if event_key:
            queryset = queryset.filter(event_key=event_key)
        
        return queryset.order_by('-scheduled_for')
    
    def get_serializer_class(self):
        from admin_management.serializers.email_serializers import (
            EmailDigestSerializer,
            EmailDigestCreateSerializer
        )
        if self.action in ['create', 'update', 'partial_update']:
            return EmailDigestCreateSerializer
        return EmailDigestSerializer
    
    @action(detail=False, methods=['get'])
    def configs(self, request):
        """Get available digest configurations."""
        from notifications_system.registry import get_digest_config, list_all_event_keys
        
        # Get all event keys and filter for those with digest configs
        all_events = list_all_event_keys()
        digestable_events = [
            event_key for event_key in all_events
            if get_digest_config(event_key) is not None
        ]
        
        return Response({
            'available_events': digestable_events
        })
    
    @action(detail=True, methods=['post'])
    def send_now(self, request, pk=None):
        """Send digest immediately."""
        digest = self.get_object()
        if getattr(digest, 'is_sent', False):
            return Response(
                {"detail": "Digest already sent."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            DigestService.send_user_digest(digest.user_id, [digest])
            return Response({"detail": "Digest sent."})
        except Exception as e:
            return Response(
                {"detail": f"Failed to send digest: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def send_due(self, request):
        """Send all due digests."""
        try:
            DigestService.send_due_digests()
            return Response({"detail": "Due digests sent."})
        except Exception as e:
            return Response(
                {"detail": f"Failed to send digests: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BroadcastMessageManagementViewSet(viewsets.ModelViewSet):
    """
    Admin interface for managing broadcast messages.
    """
    queryset = BroadcastNotification.objects.all()
    permission_classes = [IsAuthenticated, IsSuperadminOrAdmin]
    
    def get_queryset(self):
        user = self.request.user
        queryset = BroadcastNotification.objects.select_related('website', 'created_by')
        
        if user.role != 'superadmin':
            website = getattr(user, 'website', None)
            if website:
                queryset = queryset.filter(website=website)
        
        # Filtering
        website_id = self.request.query_params.get('website_id')
        if website_id:
            queryset = queryset.filter(website_id=website_id)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        from admin_management.serializers.email_serializers import (
            BroadcastMessageSerializer,
            BroadcastMessageCreateSerializer
        )
        if self.action in ['create', 'update', 'partial_update']:
            return BroadcastMessageCreateSerializer
        return BroadcastMessageSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def send_now(self, request, pk=None):
        """Send broadcast immediately."""
        broadcast = self.get_object()
        
        try:
            BroadcastNotificationService.send_broadcast(
                event=broadcast.event_type,
                title=broadcast.title,
                message=broadcast.message,
                website=broadcast.website,
                channels=broadcast.channels or ['in_app', 'email'],
                is_test=False,
            )
            broadcast.sent_at = timezone.now()
            broadcast.is_active = True
            broadcast.save()
            return Response({"detail": "Broadcast sent."})
        except Exception as e:
            return Response(
                {"detail": f"Failed to send broadcast: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def preview(self, request, pk=None):
        """Preview broadcast to a test user."""
        broadcast = self.get_object()
        test_user = request.user
        
        try:
            BroadcastNotificationService.preview_to_user(
                event=broadcast.event_type,
                title=broadcast.title,
                message=broadcast.message,
                user=test_user,
                website=broadcast.website,
                channels=broadcast.channels or ['in_app', 'email'],
            )
            return Response({"detail": f"Preview sent to {test_user.email}."})
        except Exception as e:
            return Response(
                {"detail": f"Failed to send preview: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get broadcast statistics."""
        broadcast = self.get_object()
        from notifications_system.models.broadcast_notification import BroadcastAcknowledgement
        
        total_recipients = User.objects.filter(is_active=True).count()
        acknowledged = BroadcastAcknowledgement.objects.filter(broadcast=broadcast).count()
        
        return Response({
            'total_recipients': total_recipients,
            'acknowledged': acknowledged,
            'acknowledgement_rate': (acknowledged / total_recipients * 100) if total_recipients > 0 else 0,
        })


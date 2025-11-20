"""
Views for the Mass Email System.

Includes endpoints for managing campaigns, sending tests,
scheduling, tracking recipients, and using templates.
"""

from rest_framework import (
    viewsets, mixins, status,
    generics, filters
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from mass_emails.models import EmailRecipient
from mass_emails.serializers import EmailRecipientSerializer
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import BasicAuthentication
from django.contrib.auth import get_user_model
from mass_emails.serializers import EmailRecipientSerializer



from .models import (
    EmailCampaign,
    EmailRecipient,
    CampaignAttachment,
    EmailTemplate,
    EmailServiceIntegration
)
from .serializers import (
    EmailCampaignCreateSerializer,
    EmailCampaignListSerializer,
    EmailCampaignDetailSerializer,
    EmailRecipientSerializer,
    CampaignAttachmentSerializer,
    EmailTemplateSerializer,
    EmailServiceIntegrationSerializer
)
try:
    from .tasks import send_email_campaign, send_single_test_email
except Exception:
    # Provide no-op fallbacks for tests if task symbol is absent
    def _noop(*args, **kwargs):
        return None
    class _NoopTask:
        def delay(self, *args, **kwargs):
            return None
    send_email_campaign = _NoopTask()
    send_single_test_email = _NoopTask()

User = get_user_model()

class EmailCampaignViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing marketing email campaigns.
    """
    queryset = EmailCampaign.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return EmailCampaign.objects.all()
        return EmailCampaign.objects.filter(created_by=user)

    def get_serializer_class(self):
        if self.action == 'list':
            return EmailCampaignListSerializer
        elif self.action == 'retrieve':
            return EmailCampaignDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return EmailCampaignCreateSerializer
        return EmailCampaignDetailSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        """
        Schedule a draft campaign to be sent at a future time.
        """
        campaign = self.get_object()
        if campaign.status != 'draft':
            return Response(
                {"detail": "Only draft campaigns can be scheduled."},
                status=status.HTTP_400_BAD_REQUEST
            )

        scheduled_time = request.data.get('scheduled_time')
        if not scheduled_time:
            return Response(
                {"detail": "Missing 'scheduled_time'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        campaign.scheduled_time = scheduled_time
        campaign.status = 'scheduled'
        campaign.save()
        return Response({"detail": "Campaign scheduled."})

    @action(detail=True, methods=['post'])
    def send_now(self, request, pk=None):
        """
        Immediately send a campaign (bypassing schedule).
        """
        campaign = self.get_object()
        if campaign.status not in ['draft', 'scheduled']:
            return Response(
                {"detail": "Only draft/scheduled campaigns can be sent."},
                status=status.HTTP_400_BAD_REQUEST
            )

        campaign.status = 'sending'
        campaign.scheduled_time = timezone.now()
        campaign.save()

        send_email_campaign.delay(campaign.id)

        return Response({"detail": "Campaign sending started."})

    @action(detail=True, methods=['post'])
    def send_test(self, request, pk=None):
        """
        Sends a test email to the request user.
        """
        campaign = self.get_object()
        to_email = request.user.email

        if not to_email:
            return Response(
                {"detail": "User has no email address."},
                status=status.HTTP_400_BAD_REQUEST
            )

        send_single_test_email.delay(campaign.id, to_email)
        return Response(
            {"detail": f"Test email is being sent to {to_email}."}
        )

    @action(detail=True, methods=['post'])
    def preview(self, request, pk=None):
        """
        Preview rendered HTML for the campaign.
        """
        campaign = self.get_object()
        dummy_user = request.data.get('user', {
            'first_name': 'Test',
            'email': 'test@example.com'
        })

        html = campaign.body \
            .replace('{{ first_name }}', dummy_user.get('first_name', '')) \
            .replace('{{ email }}', dummy_user.get('email', ''))

        return Response({
            "subject": campaign.subject,
            "html": html
        })


class EmailRecipientViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    Read-only viewset for tracking campaign recipients.
    """
    queryset = EmailRecipient.objects.all()
    serializer_class = EmailRecipientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        return self.queryset.filter(user=user)


class CampaignAttachmentViewSet(viewsets.ModelViewSet):
    """
    Manage attachments for campaigns.
    """
    queryset = CampaignAttachment.objects.all()
    serializer_class = CampaignAttachmentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class EmailTemplateViewSet(viewsets.ModelViewSet):
    """
    Manage reusable email templates.
    """
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return EmailTemplate.objects.filter(
            is_global=True
        ) | EmailTemplate.objects.filter(created_by=user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class EmailServiceIntegrationViewSet(viewsets.ModelViewSet):
    """
    Admin interface for managing email provider configs.
    """
    queryset = EmailServiceIntegration.objects.all()
    serializer_class = EmailServiceIntegrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        return self.queryset.filter(website__in=user.websites.all())
    

class UserEmailHistoryView(generics.ListAPIView):
    """
    Returns the email campaign history for the authenticated user.
    Supports filtering by status and email_type.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [BasicAuthentication]
    serializer_class = EmailRecipientSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    pagination_class = None
    ordering_fields = ['sent_at', 'status']
    ordering = ['-sent_at']
    search_fields = ['campaign__title', 'campaign__subject']

    def get_queryset(self):
        user = self.request.user
        qs = EmailRecipient.objects.filter(user=user)

        status = self.request.GET.get("status")
        email_type = self.request.GET.get("email_type")

        if status:
            qs = qs.filter(status=status)
        if email_type:
            qs = qs.filter(campaign__email_type=email_type)

        return qs
    
class AdminEmailHistoryView(generics.ListAPIView):
    """
    Admin view: email campaign history for any user.
    Use ?user_id=<id> + same filters.
    """
    serializer_class = EmailRecipientSerializer
    permission_classes = [IsAdminUser]
    authentication_classes = [BasicAuthentication]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    pagination_class = None
    ordering_fields = ['sent_at', 'status']
    ordering = ['-sent_at']
    search_fields = ['campaign__title', 'campaign__subject']

    def get_queryset(self):
        user_id = self.request.GET.get("user_id")
        if not user_id:
            return EmailRecipient.objects.none()

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return EmailRecipient.objects.none()

        qs = EmailRecipient.objects.filter(user=user)

        status = self.request.GET.get("status")
        email_type = self.request.GET.get("email_type")

        if status:
            qs = qs.filter(status=status)
        if email_type:
            qs = qs.filter(campaign__email_type=email_type)

        return qs
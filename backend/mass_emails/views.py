"""
Views for the Mass Email System.

Includes endpoints for managing campaigns, sending tests,
scheduling, tracking recipients, and using templates.
"""

from rest_framework import viewsets, mixins, status, generics, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model

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
from .permissions import CanManageMassEmails, IsMassEmailAdmin
from .selectors import MassEmailCampaignSelector, MassEmailRecipientSelector
from .services import MassEmailCampaignService

try:
    from .tasks import send_email_campaign, send_single_test_email
except Exception:
    # Provide no-op fallbacks for tests if task symbol is absent

    class _NoopTask:
        def delay(self, *args, **kwargs):
            return None

    send_email_campaign = _NoopTask()
    send_single_test_email = _NoopTask()

User = get_user_model()


class EmailHistoryPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 200


class EmailCampaignViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing marketing email campaigns.
    """
    queryset = EmailCampaign.objects.all()
    permission_classes = [CanManageMassEmails]

    def get_queryset(self):
        return MassEmailCampaignSelector.visible_to(self.request.user)

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

        if isinstance(scheduled_time, str):
            scheduled_time = parse_datetime(scheduled_time)
        if scheduled_time is None:
            return Response(
                {"detail": "Invalid 'scheduled_time'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if scheduled_time <= timezone.now():
            return Response(
                {"detail": "Scheduled time must be in the future."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        campaign.scheduled_time = scheduled_time
        campaign.status = 'scheduled'
        campaign.save(
            update_fields=["scheduled_time", "status", "updated_at"],
        )
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

        MassEmailCampaignService.mark_sending(campaign)

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
        dummy_user = request.data.get('user') or {
            'first_name': 'Test',
            'email': 'test@example.com'
        }

        class PreviewUser:
            first_name = dummy_user.get("first_name", "")
            last_name = dummy_user.get("last_name", "")
            username = dummy_user.get("username", "")
            email = dummy_user.get("email", "test@example.com")

        html = MassEmailCampaignService.render_body(
            campaign=campaign,
            user=PreviewUser(),
            email=PreviewUser.email,
        )

        return Response({
            "subject": campaign.subject,
            "html": html
        })

    @action(detail=True, methods=['post'], url_path="sync-recipients")
    def sync_recipients(self, request, pk=None):
        campaign = self.get_object()
        created = MassEmailCampaignService.sync_recipients(campaign)
        return Response(
            {
                "detail": "Recipients synchronized.",
                "created": created,
                "total": campaign.recipients.count(),
            }
        )


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
    permission_classes = [CanManageMassEmails]

    def get_queryset(self):
        user = self.request.user
        campaign_queryset = MassEmailCampaignSelector.visible_to(user)
        return self.queryset.filter(campaign__in=campaign_queryset)


class CampaignAttachmentViewSet(viewsets.ModelViewSet):
    """
    Manage attachments for campaigns.
    """
    queryset = CampaignAttachment.objects.all()
    serializer_class = CampaignAttachmentSerializer
    permission_classes = [CanManageMassEmails]

    def get_queryset(self):
        campaign_queryset = MassEmailCampaignSelector.visible_to(
            self.request.user,
        )
        return self.queryset.select_related(
            "campaign",
            "attachment",
            "attachment__managed_file",
        ).filter(campaign__in=campaign_queryset)

    def perform_create(self, serializer):
        serializer.save()


class EmailTemplateViewSet(viewsets.ModelViewSet):
    """
    Manage reusable email templates.
    """
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [CanManageMassEmails]

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
    permission_classes = [IsMassEmailAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or getattr(user, "role", None) == "superadmin":
            return self.queryset
        website_id = getattr(user, "website_id", None)
        if website_id:
            return self.queryset.filter(website_id=website_id)
        return self.queryset.none()


class UserEmailHistoryView(generics.ListAPIView):
    """
    Returns the email campaign history for the authenticated user.
    Supports filtering by status and email_type.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EmailRecipientSerializer
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    pagination_class = EmailHistoryPagination
    ordering_fields = ['sent_at', 'status']
    ordering = ['-sent_at']
    search_fields = ['campaign__title', 'campaign__subject']

    def get_queryset(self):
        user = self.request.user
        qs = MassEmailRecipientSelector.history_for_user(user)

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
    permission_classes = [IsMassEmailAdmin]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    pagination_class = EmailHistoryPagination
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

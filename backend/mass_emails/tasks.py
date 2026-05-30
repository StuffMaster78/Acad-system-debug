"""
Celery tasks for sending email campaigns.
"""
import logging

from celery import shared_task
from django.utils import timezone

from .models import EmailCampaign, EmailRecipient, UnsubscribeLog
from .services import get_provider_client
from .services.campaign_service import MassEmailCampaignService

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_email_campaign(self, campaign_id):
    """
    Entry point task: sends all emails in a campaign.
    """
    try:
        campaign = EmailCampaign.objects.get(id=campaign_id)
        if campaign.status not in ['draft', 'scheduled', 'sending']:
            logger.warning(f"Invalid campaign status: {campaign.status}")
            return

        MassEmailCampaignService.mark_sending(campaign)

        MassEmailCampaignService.sync_recipients(campaign)
        for recipient in campaign.recipients.all():
            send_single_email.delay(recipient.id)

        MassEmailCampaignService.mark_sent(campaign)

    except Exception as e:
        logger.exception(f"Campaign failed: {e}")
        if "campaign" in locals():
            MassEmailCampaignService.mark_failed(campaign, e)


@shared_task(bind=True, max_retries=3)
def send_single_email(self, recipient_id):
    """
    Task to send a single email via configured provider.
    """
    try:
        recipient = EmailRecipient.objects.select_related(
            'campaign'
        ).get(id=recipient_id)
        campaign = recipient.campaign

        # Unsubscribe gate — never send to addresses that have opted out.
        if UnsubscribeLog.objects.filter(email=recipient.email).exists():
            recipient.status = 'unsubscribed'
            recipient.save(update_fields=['status'])
            logger.info(
                "Skipped unsubscribed recipient %s for campaign %s",
                recipient.email,
                campaign.id,
            )
            return

        # Also skip if the notifications_system suppression list has the address.
        try:
            from notifications_system.models import EmailSuppression
            if EmailSuppression.objects.filter(email=recipient.email).exists():
                recipient.status = 'unsubscribed'
                recipient.save(update_fields=['status'])
                return
        except Exception:
            pass

        provider = get_provider_client(campaign)

        subject = campaign.subject
        from_email = (
            f"{campaign.resolved_sender_name} "
            f"<{campaign.resolved_sender_email}>"
        )
        to = [recipient.email]
        html_content = MassEmailCampaignService.render_body(
            campaign=campaign,
            user=recipient.user,
            email=recipient.email,
        )

        provider.send_email(
            subject=subject,
            body_html=html_content,
            from_email=from_email,
            to=to
        )

        recipient.status = 'sent'
        recipient.sent_at = timezone.now()
        recipient.save()

    except Exception as e:
        logger.error(f"Failed to send to {recipient.email}: {e}")
        recipient.status = 'failed'
        recipient.error_message = str(e)
        recipient.save()


@shared_task(bind=True, max_retries=3)
def send_single_test_email(self, campaign_id, to_email):
    """
    Send a campaign preview to one address without creating a recipient row.
    """
    campaign = EmailCampaign.objects.select_related("website").get(
        id=campaign_id,
    )
    provider = get_provider_client(campaign)
    provider.send_email(
        subject=f"[Test] {campaign.subject}",
        body_html=MassEmailCampaignService.render_body(
            campaign=campaign,
            email=to_email,
        ),
        from_email=(
            f"{campaign.resolved_sender_name} "
            f"<{campaign.resolved_sender_email}>"
        ),
        to=[to_email],
    )

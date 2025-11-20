"""
Celery tasks for sending email campaigns.
"""
import logging
from celery import shared_task
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import EmailCampaign, EmailRecipient
from .services import get_provider_client
# from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()



def _resolve_recipients(campaign):
    """
    Resolve users based on target_roles and website.
    Returns a list of (email, user) tuples.
    """
    target_roles = campaign.target_roles or []
    website = campaign.website

    users = User.objects.filter(
        role__in=target_roles,
        website=website,
        is_active=True,
        email__isnull=False
    ).exclude(email='')

    recipients = []
    for user in users:
        recipients.append((user.email, user))

    return recipients


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

        campaign.status = 'sending'
        campaign.save()

        recipients = _resolve_recipients(campaign)

        for email, user in recipients:
            EmailRecipient.objects.get_or_create(
                campaign=campaign,
                email=email,
                defaults={'user': user}
            )

        for recipient in campaign.recipients.all():
            send_single_email.delay(recipient.id)

        campaign.status = 'sent'
        campaign.sent_time = timezone.now()
        campaign.save()

    except Exception as e:
        logger.exception(f"Campaign failed: {e}")
        campaign.status = 'failed'
        campaign.failure_report = str(e)
        campaign.save()


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

        provider = get_provider_client(campaign)

        subject = campaign.subject
        from_email = f"{campaign.sender_name} <{campaign.sender_email}>"
        to = [recipient.email]
        html_content = campaign.body

        # Optional: Add unsubscribe footer or tracking pixel here

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
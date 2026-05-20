from __future__ import annotations

from django.template import Template, Context
from django.utils import timezone

from mass_emails.models import EmailCampaign, EmailRecipient
from mass_emails.selectors import MassEmailRecipientSelector


class MassEmailCampaignService:
    @staticmethod
    def render_body(
        *,
        campaign: EmailCampaign,
        user=None,
        email: str = "",
    ) -> str:
        context = {
            "first_name": getattr(user, "first_name", "") or "",
            "last_name": getattr(user, "last_name", "") or "",
            "username": getattr(user, "username", "") or "",
            "email": email or getattr(user, "email", "") or "",
            "website": campaign.website,
            "campaign": campaign,
        }
        return Template(campaign.body).render(Context(context))

    @staticmethod
    def sync_recipients(campaign: EmailCampaign) -> int:
        count = 0
        users = MassEmailRecipientSelector.recipients_for_campaign(campaign)
        for user in users:
            _recipient, created = EmailRecipient.objects.get_or_create(
                campaign=campaign,
                email=user.email,
                defaults={"user": user},
            )
            if created:
                count += 1
        return count

    @staticmethod
    def mark_sending(campaign: EmailCampaign) -> EmailCampaign:
        campaign.status = "sending"
        campaign.scheduled_time = campaign.scheduled_time or timezone.now()
        campaign.save(
            update_fields=["status", "scheduled_time", "updated_at"],
        )
        return campaign

    @staticmethod
    def mark_sent(campaign: EmailCampaign) -> EmailCampaign:
        campaign.status = "sent"
        campaign.sent_time = timezone.now()
        campaign.save(update_fields=["status", "sent_time", "updated_at"])
        return campaign

    @staticmethod
    def mark_failed(
        campaign: EmailCampaign,
        error: Exception,
    ) -> EmailCampaign:
        campaign.status = "failed"
        campaign.failure_report = str(error)
        campaign.save(
            update_fields=["status", "failure_report", "updated_at"],
        )
        return campaign

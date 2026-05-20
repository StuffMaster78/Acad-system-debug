from django.contrib.auth import get_user_model
from django.db.models import Q

from mass_emails.models import EmailCampaign, EmailRecipient, UnsubscribeLog


User = get_user_model()


TARGETABLE_ROLES = {"client", "writer"}


class MassEmailCampaignSelector:
    @staticmethod
    def visible_to(user):
        queryset = EmailCampaign.objects.select_related(
            "website",
            "created_by",
        )
        if (
            getattr(user, "is_superuser", False)
            or getattr(user, "role", None) == "superadmin"
        ):
            return queryset

        website_id = getattr(user, "website_id", None)
        if website_id:
            return queryset.filter(website_id=website_id)

        return queryset.filter(created_by=user)


class MassEmailRecipientSelector:
    @staticmethod
    def recipients_for_campaign(campaign):
        target_roles = [
            role
            for role in (campaign.target_roles or [])
            if role in TARGETABLE_ROLES
        ]
        if not target_roles:
            return User.objects.none()

        unsubscribed_emails = UnsubscribeLog.objects.values("email")
        return (
            User.objects.filter(
                role__in=target_roles,
                website=campaign.website,
                is_active=True,
            )
            .exclude(Q(email__isnull=True) | Q(email=""))
            .exclude(email__in=unsubscribed_emails)
            .order_by("id")
        )

    @staticmethod
    def history_for_user(user):
        return EmailRecipient.objects.select_related(
            "campaign",
            "campaign__website",
        ).filter(user=user)

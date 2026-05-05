from __future__ import annotations

from django.core.exceptions import ValidationError


class CampaignValidator:
    """
    Validate campaign configuration.
    """

    @staticmethod
    def validate_date_window(*, starts_at, ends_at) -> None:
        """
        Ensure campaign start date is before end date.
        """
        if starts_at and ends_at and starts_at >= ends_at:
            raise ValidationError(
                "Campaign starts_at must be earlier than ends_at."
            )

    @staticmethod
    def validate_same_website(*, campaign, website) -> None:
        """
        Ensure campaign belongs to the given website.
        """
        if campaign and campaign.website_id != website.id:
            raise ValidationError(
                "Campaign does not belong to this website."
            )
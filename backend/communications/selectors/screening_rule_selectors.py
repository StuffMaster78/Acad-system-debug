from __future__ import annotations

from django.db.models import Q
from django.db.models import QuerySet

from communications.models import CommunicationScreeningRule


class CommunicationScreeningRuleSelector:
    """
    Read helpers for communication screening rules.
    """

    @staticmethod
    def for_website(*, website) -> QuerySet[CommunicationScreeningRule]:
        """
        Return website specific and platform wide screening rules.
        """
        return (
            CommunicationScreeningRule.objects
            .filter(Q(website=website) | Q(is_platform_rule=True))
            .order_by("-is_platform_rule", "name", "id")
        )

    @staticmethod
    def active_for_website(*, website) -> QuerySet[CommunicationScreeningRule]:
        """
        Return active website specific and platform wide screening rules.
        """
        return (
            CommunicationScreeningRule.objects
            .filter(
                Q(website=website) | Q(is_platform_rule=True),
                is_active=True,
            )
            .order_by("-is_platform_rule", "name", "id")
        )

    @staticmethod
    def get_by_name(
        *,
        website,
        name: str,
    ) -> CommunicationScreeningRule | None:
        """
        Return a screening rule by name.
        """
        return (
            CommunicationScreeningRule.objects
            .filter(
                Q(website=website) | Q(is_platform_rule=True),
                name__iexact=name,
            )
            .first()
        )
from __future__ import annotations

from rest_framework.viewsets import ModelViewSet

from communications.api.permissions import CanManageScreeningRules
from communications.api.permissions import IsAuthenticatedForCommunications
from communications.api.serializers import CommunicationScreeningRuleCreateSerializer
from communications.api.serializers import CommunicationScreeningRuleSerializer
from communications.models.screening_rule import CommunicationScreeningRule
from communications.selectors.screening_rule_selectors import (
    CommunicationScreeningRuleSelector,
)
from communications.api.throttles import (
    CommunicationScreeningRuleWriteThrottle,
)



class CommunicationScreeningRuleViewSet(ModelViewSet):
    """
    API endpoints for screening rules.
    """

    permission_classes = [
        IsAuthenticatedForCommunications,
        CanManageScreeningRules,
    ]
    
    
    def get_throttles(self):  # type: ignore[override]
        """
        Apply write throttle only to screening rule mutations.
        """
        if self.action in {
            "create",
            "update",
            "partial_update",
            "destroy",
        }:
            return [CommunicationScreeningRuleWriteThrottle()]

        return super().get_throttles()

    def get_queryset(self):  # type: ignore[override]
        """
        Return website specific and platform rules.
        """
        website = getattr(self.request, "website", None)

        return CommunicationScreeningRuleSelector.for_website(
            website=website,
        ).order_by("-is_platform_rule", "name", "id")

    def get_serializer_class(self):  # type: ignore[override]
        """
        Return serializer class.
        """
        if self.action == "create":
            return CommunicationScreeningRuleCreateSerializer

        return CommunicationScreeningRuleSerializer
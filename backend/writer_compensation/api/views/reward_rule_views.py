from __future__ import annotations

from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from typing import cast

from writer_compensation.permissions.reward_permissions import (
    IsRewardViewer,
)
from writer_compensation.api.serializers.reward_rule_serializer import (
    RewardRuleSerializer,
)
from writer_compensation.selectors.reward_api_selectors import (
    RewardAPISelectors,
)
from writer_compensation.models.reward_rule import (
    RewardRule,
)

from rest_framework.request import Request
from django.db.models import QuerySet

class RewardRuleListView(
    ListAPIView,
):
    """
    List active reward rules.
    """

    serializer_class = (
        RewardRuleSerializer
    )

    permission_classes = [
        IsRewardViewer,
    ]

    def get_queryset(  # type: ignore[override]
            self) -> QuerySet[RewardRule]:
        request = cast(Request, self.request)
        website_id = (
            request.query_params.get(
                "website_id",
            )
        )

        if not website_id:
            return RewardRule.objects.none()

        return (
            RewardAPISelectors.active_rules(
                website_id=website_id,
            )
        )


class RewardRuleDetailView(
    RetrieveAPIView,
):
    """
    Retrieve reward rule details.
    """

    serializer_class = (
        RewardRuleSerializer
    )

    permission_classes = [
        IsRewardViewer,
    ]

    queryset = (
        RewardRule.objects.all()
    )
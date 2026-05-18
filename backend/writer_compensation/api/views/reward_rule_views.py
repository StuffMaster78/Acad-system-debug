from __future__ import annotations

from rest_framework.generics import ListAPIView
from rest_framework.generics import RetrieveAPIView
from typing import cast
from rest_framework import status

from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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


class RewardRuleCreateView(
    CreateAPIView,
):
    """
    Create reward rule.
    """

    serializer_class = (
        RewardRuleSerializer
    )

    permission_classes = [
        IsAuthenticated,
    ]

    queryset = (
        RewardRule.objects.all()
    )

    def create(
        self,
        request,
        *args,
        **kwargs,
    ):
        """
        Create reward rule.
        """

        serializer = self.get_serializer(
            data=request.data,
        )

        serializer.is_valid(
            raise_exception=True,
        )

        reward_rule = serializer.save()

        return Response(
            RewardRuleSerializer(
                reward_rule,
            ).data,
            status=status.HTTP_201_CREATED,
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

    lookup_field = "pk"
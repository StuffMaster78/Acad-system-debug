from __future__ import annotations

import django_filters

from writer_compensation.models.writer_reward import (
    WriterReward,
)


class WriterRewardFilter(
    django_filters.FilterSet,
):
    """
    Reward API filtering.
    """

    issued_after = django_filters.DateFilter(
        field_name="issued_at",
        lookup_expr="gte",
    )

    issued_before = django_filters.DateFilter(
        field_name="issued_at",
        lookup_expr="lte",
    )

    class Meta:
        model = WriterReward

        fields = [
            "status",
            "reward_rule",
            "website",
            "writer",
        ]
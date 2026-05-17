from __future__ import annotations

import django_filters

from reputation_system.models.writer_reputation_snapshot import (
    WriterReputationSnapshot,
)


class LeaderboardFilter(
    django_filters.FilterSet,
):
    """
    Leaderboard filtering.
    """

    minimum_rating = django_filters.NumberFilter(
        field_name="rating",
        lookup_expr="gte",
    )

    minimum_trust_score = (
        django_filters.NumberFilter(
            field_name="trust_score",
            lookup_expr="gte",
        )
    )

    class Meta:
        model = WriterReputationSnapshot

        fields = [
            "rating",
            "trust_score",
        ]
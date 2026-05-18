from __future__ import annotations

from rest_framework.throttling import (
    UserRateThrottle,
)


class RewardLeaderboardThrottle(
    UserRateThrottle,
):
    """
    Leaderboard endpoint throttle.
    """

    rate = "30/min"


class RewardAnalyticsThrottle(
    UserRateThrottle,
):
    """
    Analytics endpoint throttle.
    """

    rate = "20/min"
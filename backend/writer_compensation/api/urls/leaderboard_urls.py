from __future__ import annotations

from django.urls import path

from writer_compensation.api.views.reward_leaderboard_views import (
    RewardLeaderboardView,
)

app_name = "leaderboard_api"

urlpatterns = [
    path(
        "",
        RewardLeaderboardView.as_view(),
        name="global-leaderboard",
    ),
]

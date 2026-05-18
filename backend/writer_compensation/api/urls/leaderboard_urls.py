from __future__ import annotations

from django.urls import path

from writer_compensation.api.views.reward_leaderboard_views import (
    GlobalLeaderboardAPIView,
    WriterLeaderboardPositionAPIView,
)

app_name = "leaderboard_api"

urlpatterns = [
    path(
        "global/",
        GlobalLeaderboardAPIView.as_view(),
        name="global-leaderboard",
    ),
    path(
        "writers/<uuid:writer_id>/position/",
        WriterLeaderboardPositionAPIView.as_view(),
        name="writer-position",
    ),
]
from __future__ import annotations

from django.urls import path

from writer_compensation.api.views.reward_analytics_views import (
    RewardAnalyticsOverviewAPIView,
)

app_name = "reward_analytics_api"

urlpatterns = [
    path(
        "overview/",
        RewardAnalyticsOverviewAPIView.as_view(),
        name="reward-analytics-overview",
    ),
]
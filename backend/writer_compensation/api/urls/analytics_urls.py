from __future__ import annotations

from django.urls import path

from writer_compensation.api.views.reward_analytics_views import (
    RewardAnalyticsOverviewView,
)

app_name = "reward_analytics_api"

urlpatterns = [
    path(
        "overview/",
        RewardAnalyticsOverviewView.as_view(),
        name="reward-analytics-overview",
    ),
]

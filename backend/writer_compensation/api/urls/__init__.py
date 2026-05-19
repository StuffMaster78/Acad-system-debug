from __future__ import annotations

from django.urls import include
from django.urls import path

urlpatterns = [
    path("financial-events/", include("writer_compensation.api.urls.financial_event_urls")),
    path("settlements/", include("writer_compensation.api.urls.settlement_urls")),
    path("exposure/", include("writer_compensation.api.urls.exposure_urls")),
    path("wallets/", include("writer_compensation.api.urls.wallet_urls")),
    path("reconciliation/", include("writer_compensation.api.urls.reconciliation_urls")),
    path("advances/", include("writer_compensation.api.urls.advance_urls")),
    path("admin/", include("writer_compensation.api.urls.admin_urls")),
    path("writer/", include("writer_compensation.api.urls.writer_urls")),
    path("support/", include("writer_compensation.api.urls.support_urls")),
    path("rewards/", include("writer_compensation.api.urls.reward_urls")),
    path("leaderboard/", include("writer_compensation.api.urls.leaderboard_urls")),
    path("analytics/", include("writer_compensation.api.urls.analytics_urls")),
    path("achievements/", include("writer_compensation.api.urls.achievement_urls")),
]

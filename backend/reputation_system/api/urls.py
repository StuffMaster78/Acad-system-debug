from django.urls import path

from reputation_system.api.views import (
    LeaderboardView,
    WebsiteReputationView,
    WriterRankView,
    WriterReputationView,
)

app_name = "reputation_system"

urlpatterns = [
    path("leaderboard/", LeaderboardView.as_view(), name="leaderboard"),
    path("writers/<uuid:writer_id>/", WriterReputationView.as_view(), name="writer-reputation"),
    path("writers/<uuid:writer_id>/rank/", WriterRankView.as_view(), name="writer-rank"),
    path("websites/<uuid:website_id>/", WebsiteReputationView.as_view(), name="website-reputation"),
]

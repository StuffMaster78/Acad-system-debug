from django.urls import path

from writer_compensation.api.views.achievement_progress_views import (
    WriterAchievementProgressView,
)
from writer_compensation.api.views.reward_analytics_views import (
    RewardAnalyticsOverviewView,
)
from writer_compensation.api.views.reward_event_views import (
    RewardEventOutboxView,
)
from writer_compensation.api.views.reward_fraud_views import (
    RewardFraudCheckView,
)
from writer_compensation.api.views.reward_leaderboard_views import (
    RewardLeaderboardView,
)
from writer_compensation.api.views.reward_metrics_views import RewardMetricsView
from writer_compensation.api.views.reward_projection_views import (
    RewardProjectionAPIView,
)
from writer_compensation.api.views.reward_rule_views import RewardRuleListView
from writer_compensation.api.views.reward_snapshot_views import (
    WriterReputationSnapshotView,
)
from writer_compensation.api.views.trust_score_views import TrustScoreDetailView
from writer_compensation.api.views.writer_reward_views import (
    WriterRewardListView,
)

app_name = "writer_compensation"

urlpatterns = [
    path("rules/", RewardRuleListView.as_view(), name="reward-rules"),
    path("writers/<int:writer_id>/rewards/", WriterRewardListView.as_view(), name="writer-rewards"),
    path("leaderboard/", RewardLeaderboardView.as_view(), name="reward-leaderboard"),
    path("writers/<int:writer_id>/trust-score/", TrustScoreDetailView.as_view(), name="trust-score"),
    path("writers/<int:writer_id>/projections/", RewardProjectionAPIView.as_view(), name="reward-projections"),
    path("metrics/", RewardMetricsView.as_view(), name="reward-metrics"),
    path("events/", RewardEventOutboxView.as_view(), name="reward-events"),
    path("analytics/", RewardAnalyticsOverviewView.as_view(), name="reward-analytics"),
    path("fraud/<int:writer_id>/", RewardFraudCheckView.as_view(), name="reward-fraud-check"),
    path("snapshot/<int:writer_id>/", WriterReputationSnapshotView.as_view(), name="writer-reputation-snapshot"),
    path("achievements/<int:writer_id>/", WriterAchievementProgressView.as_view(), name="writer-achievement-progress"),
]

# writer_compensation/api/urls.py

from django.urls import path

from writer_compensation.api.views.reward_analytics_views import (
    RewardAnalyticsView,
)
from writer_compensation.api.views.reward_leaderboard_views import (
    RewardLeaderboardView,
)
from writer_compensation.api.views.reward_orchestration_views import (
    RunMonthlyRewardsView,
)
from writer_compensation.api.views.reward_orchestration_views import (
    RunWeeklyRewardsView,
)
from writer_compensation.api.views.reward_rule_views import (
    RewardRuleCreateView,
)
from writer_compensation.api.views.reward_rule_views import (
    RewardRuleDetailView,
)
from writer_compensation.api.views.reward_rule_views import (
    RewardRuleListView,
)
from writer_compensation.api.views.writer_achievement_views import (
    WriterAchievementListView,
)
from writer_compensation.api.views.writer_reward_views import (
    WriterRewardDetailView,
)
from writer_compensation.api.views.writer_reward_views import (
    WriterRewardListView,
)

urlpatterns = [
    path(
        "rewards/",
        WriterRewardListView.as_view(),
        name="reward-list",
    ),
    path(
        "rewards/<int:pk>/",
        WriterRewardDetailView.as_view(),
        name="reward-detail",
    ),
    path(
        "reward-rules/",
        RewardRuleListView.as_view(),
        name="reward-rule-list",
    ),
    path(
        "reward-rules/create/",
        RewardRuleCreateView.as_view(),
        name="reward-rule-create",
    ),
    path(
        "reward-rules/<int:pk>/",
        RewardRuleDetailView.as_view(),
        name="reward-rule-detail",
    ),
    path(
        "leaderboard/",
        RewardLeaderboardView.as_view(),
        name="reward-leaderboard",
    ),
    path(
        "analytics/",
        RewardAnalyticsView.as_view(),
        name="reward-analytics",
    ),
    path(
        "run-weekly/",
        RunWeeklyRewardsView.as_view(),
        name="run-weekly-rewards",
    ),
    path(
        "run-monthly/",
        RunMonthlyRewardsView.as_view(),
        name="run-monthly-rewards",
    ),
    path(
        (
            "writers/"
            "<int:writer_id>/"
            "achievements/"
        ),
        WriterAchievementListView.as_view(),
        name="writer-achievements",
    ),
]
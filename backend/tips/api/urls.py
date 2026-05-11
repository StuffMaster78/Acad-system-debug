from django.urls import path

from tips.api.views.tip_views import (
    CreateTipView,
    SentTipsView,
    ReceivedTipsView,
    TipDetailView,
)

from tips.api.views.tip_attribution_views import (
    TipAttributionAPIView,
)

from tips.api.views.tip_policy_views import (
    TipPolicyAPIView,
    TipPolicyUpdateAPIView,
)

from tips.api.views.tip_metrics_views import (
    PlatformTipMetricsAPIView,
    UserTipMetricsAPIView,
)

from tips.api.views.tip_settlement_views import (
    TipSettleAPIView,
)

urlpatterns = [
    # ------------------------------------------------------------ #
    # TIP CORE
    # ------------------------------------------------------------ #

    path(
        "create/",
        CreateTipView.as_view(),
        name="tip-create",
    ),

    path(
        "sent/",
        SentTipsView.as_view(),
        name="tips-sent",
    ),

    path(
        "received/",
        ReceivedTipsView.as_view(),
        name="tips-received",
    ),

    path(
        "<int:pk>/",
        TipDetailView.as_view(),
        name="tip-detail",
    ),

    # ------------------------------------------------------------ #
    # ATTRIBUTION
    # ------------------------------------------------------------ #

    path(
        "attribution/",
        TipAttributionAPIView.as_view(),
        name="tip-attribution",
    ),

    # ------------------------------------------------------------ #
    # POLICY
    # ------------------------------------------------------------ #

    path(
        "policy/",
        TipPolicyAPIView.as_view(),
        name="tip-policy",
    ),

    path(
        "policy/update/",
        TipPolicyUpdateAPIView.as_view(),
        name="tip-policy-update",
    ),

    # ------------------------------------------------------------ #
    # METRICS
    # ------------------------------------------------------------ #

    path(
        "metrics/platform/",
        PlatformTipMetricsAPIView.as_view(),
        name="platform-tip-metrics",
    ),

    path(
        "metrics/user/",
        UserTipMetricsAPIView.as_view(),
        name="user-tip-metrics",
    ),

    # ------------------------------------------------------------ #
    # SETTLEMENT
    # ------------------------------------------------------------ #

    path(
        "settle/",
        TipSettleAPIView.as_view(),
        name="tip-settle",
    ),
]
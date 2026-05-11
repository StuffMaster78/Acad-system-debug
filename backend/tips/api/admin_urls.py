# tips/api/admin_urls.py

from django.urls import path

from tips.api.views.admin_tip_views import (
    AdminTipListAPIView,
    AdminTipDetailAPIView,
    AdminRetryTipAPIView,
    AdminCancelTipAPIView,
    AdminFailTipAPIView,
)

from tips.api.views.admin_tip_policy_views import (
    AdminTipPolicyListCreateAPIView,
    AdminTipPolicyDetailAPIView,
    AdminActivateTipPolicyAPIView,
)

from tips.api.views.admin_tip_metrics_views import (
    AdminPlatformAnalyticsAPIView,
    AdminTopTippersAPIView,
    AdminTopWritersAPIView,
    AdminTipTimeseriesAPIView,
)

from tips.api.views.admin_tip_outbox_views import (
    AdminOutboxEventListAPIView,
    AdminRequeueOutboxAPIView,
)

from tips.api.views.admin_tip_snapshot_views import (
    AdminPolicySnapshotListAPIView,
    AdminSettlementSnapshotListAPIView,
)

from tips.api.views.admin_tip_idempotency_views import (
    AdminTipIdempotencyListAPIView,
)

from tips.api.views.admin_tip_audit_views import (
    AdminTipAuditAPIView,
)

from tips.api.views.admin_tip_export_views import (
    AdminTipExportCSVAPIView,
    AdminSettlementExportAPIView,
)

urlpatterns = [

    # ============================================================
    # TIPS
    # ============================================================

    path(
        "tips/",
        AdminTipListAPIView.as_view(),
        name="admin-tip-list",
    ),

    path(
        "tips/<int:pk>/",
        AdminTipDetailAPIView.as_view(),
        name="admin-tip-detail",
    ),

    path(
        "tips/<int:pk>/retry/",
        AdminRetryTipAPIView.as_view(),
        name="admin-tip-retry",
    ),

    path(
        "tips/<int:pk>/cancel/",
        AdminCancelTipAPIView.as_view(),
        name="admin-tip-cancel",
    ),

    path(
        "tips/<int:pk>/fail/",
        AdminFailTipAPIView.as_view(),
        name="admin-tip-fail",
    ),

    # ============================================================
    # POLICIES
    # ============================================================

    path(
        "policies/",
        AdminTipPolicyListCreateAPIView.as_view(),
        name="admin-tip-policy-list-create",
    ),

    path(
        "policies/<int:pk>/",
        AdminTipPolicyDetailAPIView.as_view(),
        name="admin-tip-policy-detail",
    ),

    path(
        "policies/<int:pk>/activate/",
        AdminActivateTipPolicyAPIView.as_view(),
        name="admin-tip-policy-activate",
    ),

    # ============================================================
    # ANALYTICS
    # ============================================================

    path(
        "analytics/platform/",
        AdminPlatformAnalyticsAPIView.as_view(),
        name="admin-platform-analytics",
    ),

    path(
        "analytics/top-tippers/",
        AdminTopTippersAPIView.as_view(),
        name="admin-top-tippers",
    ),

    path(
        "analytics/top-writers/",
        AdminTopWritersAPIView.as_view(),
        name="admin-top-writers",
    ),

    path(
        "analytics/timeseries/",
        AdminTipTimeseriesAPIView.as_view(),
        name="admin-tip-timeseries",
    ),

    # ============================================================
    # OUTBOX EVENTS
    # ============================================================

    path(
        "outbox/",
        AdminOutboxEventListAPIView.as_view(),
        name="admin-outbox-events",
    ),

    path(
        "outbox/<int:pk>/requeue/",
        AdminRequeueOutboxAPIView.as_view(),
        name="admin-outbox-requeue",
    ),

    # ============================================================
    # SNAPSHOTS
    # ============================================================

    path(
        "policy-snapshots/",
        AdminPolicySnapshotListAPIView.as_view(),
        name="admin-policy-snapshots",
    ),

    path(
        "settlement-snapshots/",
        AdminSettlementSnapshotListAPIView.as_view(),
        name="admin-settlement-snapshots",
    ),

    # ============================================================
    # IDEMPOTENCY
    # ============================================================

    path(
        "idempotency/",
        AdminTipIdempotencyListAPIView.as_view(),
        name="admin-tip-idempotency",
    ),

    # ============================================================
    # AUDIT
    # ============================================================

    path(
        "audit/",
        AdminTipAuditAPIView.as_view(),
        name="admin-tip-audit",
    ),

    # ============================================================
    # EXPORTS
    # ============================================================

    path(
        "exports/csv/",
        AdminTipExportCSVAPIView.as_view(),
        name="admin-tip-export-csv",
    ),

    path(
        "exports/settlements/",
        AdminSettlementExportAPIView.as_view(),
        name="admin-settlement-export",
    ),
]
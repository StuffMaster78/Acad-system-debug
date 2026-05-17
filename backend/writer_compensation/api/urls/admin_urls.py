from __future__ import annotations

from django.urls import path

from writer_compensation.api.views.admin_views import (
    AdminBatchBulkConfirmView,
    AdminBatchBulkMarkPaidView,
    AdminBatchDetailView,
    AdminCycleChangeApproveView,
    AdminCycleChangeListView,
    AdminCycleChangeRejectView,
    AdminPayoutItemHoldView,
    AdminPayoutItemMarkPaidView,
    AdminPayoutRecordConfirmView,
    AdminPayoutRecordReleaseView,
    AdminWindowAdjustView,
    AdminWindowCloseView,
    AdminWindowDetailView,
    AdminWindowListCreateView,
    AdminWindowMarkDoneView,
    AdminWindowStartProcessingView,
    AdminWindowSummaryView,
    AdminWriterWindowEventsView,
)
from writer_compensation.api.views.earnings_bonus_views import (
    AdminWindowEarningsBreakdownView,
    AdminWriterEarningsView,
    AdminWriterEarningsBreakdownView,
    AdminWriterFullEarningsView,
    AdminWriterBonusHistoryView,
    AdminApplyMilestoneBonusView,
    AdminApplyPerformanceBonusView,
    AdminApplyRetentionBonusView,
)


urlpatterns = [
    # Windows
    path(
        "windows/",
        AdminWindowListCreateView.as_view(),
        name="admin-window-list-create",
    ),
    path(
        "windows/<int:window_id>/",
        AdminWindowDetailView.as_view(),
        name="admin-window-detail",
    ),
    path(
        "windows/<int:window_id>/close/",
        AdminWindowCloseView.as_view(),
        name="admin-window-close",
    ),
    path(
        "windows/<int:window_id>/start-processing/",
        AdminWindowStartProcessingView.as_view(),
        name="admin-window-start-processing",
    ),
    path(
        "windows/<int:window_id>/mark-done/",
        AdminWindowMarkDoneView.as_view(),
        name="admin-window-mark-done",
    ),
    path(
        "windows/<int:window_id>/adjust/",
        AdminWindowAdjustView.as_view(),
        name="admin-window-adjust",
    ),
    path(
        "windows/<int:window_id>/summary/",
        AdminWindowSummaryView.as_view(),
        name="admin-window-summary",
    ),

    # Writer event drilldown
    path(
        "windows/<int:window_id>/writers/<int:writer_id>/events/",
        AdminWriterWindowEventsView.as_view(),
        name="admin-writer-window-events",
    ),

    # Batches
    path(
        "batches/<int:batch_id>/",
        AdminBatchDetailView.as_view(),
        name="admin-batch-detail",
    ),
    path(
        "batches/<int:batch_id>/bulk-confirm/",
        AdminBatchBulkConfirmView.as_view(),
        name="admin-batch-bulk-confirm",
    ),
    path(
        "batches/<int:batch_id>/bulk-mark-paid/",
        AdminBatchBulkMarkPaidView.as_view(),
        name="admin-batch-bulk-mark-paid",
    ),

    # Payout items
    path(
        "payout-items/<int:item_id>/confirm/",
        AdminPayoutRecordConfirmView.as_view(),
        name="admin-payout-item-confirm",
    ),
    path(
        "payout-items/<int:item_id>/mark-paid/",
        AdminPayoutItemMarkPaidView.as_view(),
        name="admin-payout-item-mark-paid",
    ),
    path(
        "payout-items/<int:item_id>/hold/",
        AdminPayoutItemHoldView.as_view(),
        name="admin-payout-item-hold",
    ),
    path(
        "payout-items/<int:item_id>/release/",
        AdminPayoutRecordReleaseView.as_view(),
        name="admin-payout-item-release",
    ),

    # Cycle changes
    path(
        "cycle-changes/",
        AdminCycleChangeListView.as_view(),
        name="admin-cycle-change-list",
    ),
    path(
        "cycle-changes/<int:request_id>/approve/",
        AdminCycleChangeApproveView.as_view(),
        name="admin-cycle-change-approve",
    ),
    path(
        "cycle-changes/<int:request_id>/reject/",
        AdminCycleChangeRejectView.as_view(),
        name="admin-cycle-change-reject",
    ),
    # Earnings
    path(
        "windows/<int:window_id>/earnings/",
        AdminWindowEarningsBreakdownView.as_view(),
        name="admin-window-earnings"
    ),
    path(
        "writers/<int:writer_id>/earnings/",
        AdminWriterEarningsView.as_view(),
        name="admin-writer-earnings"
    ),
    path(
        "writers/<int:writer_id>/earnings/breakdown/",
         AdminWriterEarningsBreakdownView.as_view(),
         name="admin-writer-earnings-breakdown"
    ),
    path(
        "writers/<int:writer_id>/earnings/full/",
         AdminWriterFullEarningsView.as_view(),
         name="admin-writer-earnings-full"
    ),

    # Bonuses
    path(
        "writers/<int:writer_id>/bonuses/",
        AdminWriterBonusHistoryView.as_view(),
        name="admin-writer-bonus-history"
    ),
    path(
        "writers/<int:writer_id>/bonuses/milestone/",
        AdminApplyMilestoneBonusView.as_view(),
        name="admin-apply-milestone-bonus"
    ),
    path(
        "writers/<int:writer_id>/bonuses/performance/",
        AdminApplyPerformanceBonusView.as_view(),
        name="admin-apply-performance-bonus"
    ),
    path(
        "writers/<int:writer_id>/bonuses/retention/",
        AdminApplyRetentionBonusView.as_view(),
        name="admin-apply-retention-bonus"
    ),
]
from __future__ import annotations

from django.urls import path

from writer_compensation.api.views.exposure_views import (
    ExposureLedgerDetailView,
    ExposureLedgerListView,
)
from writer_compensation.api.views.financial_event_views import (
    FinancialEventDetailView,
    FinancialEventListView,
)
from writer_compensation.api.views.reconciliation_actions_views import (
    RunReconciliationView,
)
from writer_compensation.api.views.settlement_actions_views import (
    RunSettlementView,
)
from writer_compensation.api.views.settlement_views import (
    SettlementDetailView,
    SettlementListView,
)
from writer_compensation.api.views.wallet_actions_views import (
    WalletCreditView,
    WalletDebitView,
)
from writer_compensation.api.views.wallet_views import (
    WalletDetailView,
    WalletListView,
)
from writer_compensation.api.views.admin_views import (
    # Admin — window lifecycle
    AdminWindowListCreateView,
    AdminWindowDetailView,
    AdminWindowCloseView,
    AdminWindowStartProcessingView,
    AdminWindowMarkDoneView,
    AdminWindowAdjustView,
    AdminWindowSummaryView,
    # Admin — event detail
    AdminWriterWindowEventsView,
    # Admin — batch and payout items
    AdminBatchDetailView,
    AdminBatchBulkConfirmView,
    AdminBatchBulkMarkPaidView,
    AdminPayoutRecordConfirmView,
    AdminPayoutItemMarkPaidView,
    AdminPayoutItemHoldView,
    AdminPayoutRecordReleaseView,
    # Admin — cycle changes
    AdminCycleChangeListView,
    AdminCycleChangeApproveView,
    AdminCycleChangeRejectView,
    # Writer
)
from writer_compensation.api.views.writer_payout_views import (
    # Writer
    WriterCurrentWindowView,
    WriterEventListView,
    WriterPayoutHistoryView,
    WriterLifetimeSummaryView,
    WriterPayoutPreferenceView,
    WriterCycleChangeRequestView,
)

from writer_compensation.api.views.support_views import (
    SupportWriterEventsView,
    SupportWriterPayoutsView,
    SupportHeldRecordsView,
)
urlpatterns = [
    # =====================================================
    # FINANCIAL EVENTS
    # =====================================================
    path(
        "financial-events/",
        FinancialEventListView.as_view(),
        name="financial-event-list",
    ),

    path(
        "financial-events/<int:pk>/",
        FinancialEventDetailView.as_view(),
        name="financial-event-detail",
    ),

    # =====================================================
    # SETTLEMENTS
    # =====================================================
    path(
        "settlements/",
        SettlementListView.as_view(),
        name="settlement-list",
    ),

    path(
        "settlements/<int:pk>/",
        SettlementDetailView.as_view(),
        name="settlement-detail",
    ),

    path(
        "settlements/run/",
        RunSettlementView.as_view(),
        name="run-settlement",
    ),

    # =====================================================
    # EXPOSURE LEDGER
    # =====================================================
    path(
        "exposure/",
        ExposureLedgerListView.as_view(),
        name="exposure-list",
    ),

    path(
        "exposure/<int:pk>/",
        ExposureLedgerDetailView.as_view(),
        name="exposure-detail",
    ),

    # =====================================================
    # WALLETS
    # =====================================================
    path(
        "wallets/",
        WalletListView.as_view(),
        name="wallet-list",
    ),

    path(
        "wallets/<int:pk>/",
        WalletDetailView.as_view(),
        name="wallet-detail",
    ),

    path(
        "wallets/credit/",
        WalletCreditView.as_view(),
        name="wallet-credit",
    ),

    path(
        "wallets/debit/",
        WalletDebitView.as_view(),
        name="wallet-debit",
    ),

    # =====================================================
    # RECONCILIATION
    # =====================================================
    path(
        "reconciliation/run/",
        RunReconciliationView.as_view(),
        name="run-reconciliation",
    ),

    # New Path

       # -----------------------------------------------------------------------
    # Admin — Windows
    # -----------------------------------------------------------------------
    path(
        "admin/windows/",
        AdminWindowListCreateView.as_view(),
        name="admin-window-list-create",
    ),
    path(
        "admin/windows/<int:window_id>/",
        AdminWindowDetailView.as_view(),
        name="admin-window-detail",
    ),
    path(
        "admin/windows/<int:window_id>/close/",
        AdminWindowCloseView.as_view(),
        name="admin-window-close",
    ),
    path(
        "admin/windows/<int:window_id>/start-processing/",
        AdminWindowStartProcessingView.as_view(),
        name="admin-window-start-processing",
    ),
    path(
        "admin/windows/<int:window_id>/mark-done/",
        AdminWindowMarkDoneView.as_view(),
        name="admin-window-mark-done",
    ),
    path(
        "admin/windows/<int:window_id>/adjust/",
        AdminWindowAdjustView.as_view(),
        name="admin-window-adjust",
    ),
    path(
        "admin/windows/<int:window_id>/summary/",
        AdminWindowSummaryView.as_view(),
        name="admin-window-summary",
    ),
 
    # -----------------------------------------------------------------------
    # Admin — Per-writer event detail inside a window
    # -----------------------------------------------------------------------
    path(
        "admin/windows/<int:window_id>/writers/<int:writer_id>/events/",
        AdminWriterWindowEventsView.as_view(),
        name="admin-writer-window-events",
    ),
 
    # -----------------------------------------------------------------------
    # Admin — Batches
    # -----------------------------------------------------------------------
    path(
        "admin/batches/<int:batch_id>/",
        AdminBatchDetailView.as_view(),
        name="admin-batch-detail",
    ),
    path(
        "admin/batches/<int:batch_id>/bulk-confirm/",
        AdminBatchBulkConfirmView.as_view(),
        name="admin-batch-bulk-confirm",
    ),
    path(
        "admin/batches/<int:batch_id>/bulk-mark-paid/",
        AdminBatchBulkMarkPaidView.as_view(),
        name="admin-batch-bulk-mark-paid",
    ),
 
    # -----------------------------------------------------------------------
    # Admin — Individual payout items
    # -----------------------------------------------------------------------
    path(
        "admin/payout-items/<int:item_id>/confirm/",
        AdminPayoutRecordConfirmView.as_view(),
        name="admin-payout-item-confirm",
    ),
    path(
        "admin/payout-items/<int:item_id>/mark-paid/",
        AdminPayoutItemMarkPaidView.as_view(),
        name="admin-payout-item-mark-paid",
    ),
    path(
        "admin/payout-items/<int:item_id>/hold/",
        AdminPayoutItemHoldView.as_view(),
        name="admin-payout-item-hold",
    ),
    path(
        "admin/payout-items/<int:item_id>/release/",
        AdminPayoutRecordReleaseView.as_view(),
        name="admin-payout-item-release",
    ),
 
    # -----------------------------------------------------------------------
    # Admin — Cycle change requests
    # -----------------------------------------------------------------------
    path(
        "admin/cycle-changes/",
        AdminCycleChangeListView.as_view(),
        name="admin-cycle-change-list",
    ),
    path(
        "admin/cycle-changes/<int:request_id>/approve/",
        AdminCycleChangeApproveView.as_view(),
        name="admin-cycle-change-approve",
    ),
    path(
        "admin/cycle-changes/<int:request_id>/reject/",
        AdminCycleChangeRejectView.as_view(),
        name="admin-cycle-change-reject",
    ),
 
    # -----------------------------------------------------------------------
    # Writer — own data only
    # -----------------------------------------------------------------------
    path(
        "writer/compensation/current-window/",
        WriterCurrentWindowView.as_view(),
        name="writer-current-window",
    ),
    path(
        "writer/compensation/events/",
        WriterEventListView.as_view(),
        name="writer-event-list",
    ),
    path(
        "writer/compensation/payouts/",
        WriterPayoutHistoryView.as_view(),
        name="writer-payout-history",
    ),
    path(
        "writer/compensation/summary/",
        WriterLifetimeSummaryView.as_view(),
        name="writer-lifetime-summary",
    ),
    path(
        "writer/compensation/preference/",
        WriterPayoutPreferenceView.as_view(),
        name="writer-payout-preference",
    ),
    path(
        "writer/compensation/cycle-change/",
        WriterCycleChangeRequestView.as_view(),
        name="writer-cycle-change-request",
    ),
 
    # -----------------------------------------------------------------------
    # Support — read-only + flag/escalate
    # -----------------------------------------------------------------------
    path(
        "support/writers/<int:writer_id>/events/",
        SupportWriterEventsView.as_view(),
        name="support-writer-events",
    ),
    path(
        "support/writers/<int:writer_id>/payouts/",
        SupportWriterPayoutsView.as_view(),
        name="support-writer-payouts",
    ),
    path(
        "support/held-items/",
        SupportHeldRecordsView.as_view(),
        name="support-held-items",
    ),
]
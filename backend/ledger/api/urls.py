from django.urls import path

from ledger.api.views.profit_views import PlatformProfitSummaryView
from ledger.api.views import (
    JournalEntryDetailView,
    JournalEntryListView,
    LedgerAccountDetailView,
    LedgerAccountListView,
    ReconciliationRecordDetailView,
    ReconciliationRecordListView,
    ReconciliationResolveView,
)

app_name = "ledger"

urlpatterns = [
    path(
        "accounts/",
        LedgerAccountListView.as_view(),
        name="ledger-account-list",
    ),
    path(
        "accounts/<uuid:id>/",
        LedgerAccountDetailView.as_view(),
        name="ledger-account-detail",
    ),
    path(
        "journal-entries/",
        JournalEntryListView.as_view(),
        name="journal-entry-list",
    ),
    path(
        "journal-entries/<uuid:id>/",
        JournalEntryDetailView.as_view(),
        name="journal-entry-detail",
    ),
    path(
        "reconciliations/",
        ReconciliationRecordListView.as_view(),
        name="reconciliation-record-list",
    ),
    path(
        "reconciliations/<uuid:id>/",
        ReconciliationRecordDetailView.as_view(),
        name="reconciliation-record-detail",
    ),
    path(
        "reconciliations/<uuid:id>/resolve/",
        ReconciliationResolveView.as_view(),
        name="reconciliation-record-resolve",
    ),
    path(
        "profit-summary/",
        PlatformProfitSummaryView.as_view(),
        name="profit-summary",
    ),
]
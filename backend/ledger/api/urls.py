from django.urls import path

from ledger.api.views import (
    JournalEntryDetailView,
    JournalEntryListView,
    LedgerAccountDetailView,
    LedgerAccountListView,
    ReconciliationRecordDetailView,
    ReconciliationRecordListView,
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
]
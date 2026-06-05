from django.urls import path

from wallets.api.views import (
    AdminEnsureWalletView,
    AdminWalletCaptureHoldView,
    AdminWalletCreateHoldView,
    AdminWalletDebitView,
    AdminWalletDetailView,
    AdminWalletEntryListView,
    AdminWalletFundView,
    AdminWalletHoldListView,
    AdminWalletListView,
    AdminWalletReconcileView,
    AdminWalletReleaseHoldView,
    AdminWalletRepairView,
    AdminWriterPayoutRequestApproveView,
    AdminWriterPayoutRequestListView,
    AdminWriterPayoutRequestProcessView,
    AdminWriterPayoutRequestRejectView,
    MyWalletEntryListView,
    MyWalletHoldListView,
    MyWalletView,
    MyWriterPayoutRequestListCreateView,
)

app_name = "wallets"

urlpatterns = [
    path("me/", MyWalletView.as_view(), name="my-wallet"),
    path("me/entries/", MyWalletEntryListView.as_view(), name="my-wallet-entries"),
    path("me/holds/", MyWalletHoldListView.as_view(), name="my-wallet-holds"),
    path(
        "me/payout-requests/",
        MyWriterPayoutRequestListCreateView.as_view(),
        name="my-writer-payout-requests",
    ),

    path("admin/wallets/", AdminWalletListView.as_view(), name="admin-wallet-list"),
    path(
        "admin/wallets/ensure/",
        AdminEnsureWalletView.as_view(),
        name="admin-wallet-ensure",
    ),
    path(
        "admin/payout-requests/",
        AdminWriterPayoutRequestListView.as_view(),
        name="admin-writer-payout-requests",
    ),
    path(
        "admin/payout-requests/<int:hold_id>/approve/",
        AdminWriterPayoutRequestApproveView.as_view(),
        name="admin-writer-payout-request-approve",
    ),
    path(
        "admin/payout-requests/<int:hold_id>/reject/",
        AdminWriterPayoutRequestRejectView.as_view(),
        name="admin-writer-payout-request-reject",
    ),
    path(
        "admin/payout-requests/<int:hold_id>/process/",
        AdminWriterPayoutRequestProcessView.as_view(),
        name="admin-writer-payout-request-process",
    ),
    path(
        "admin/wallets/<int:pk>/",
        AdminWalletDetailView.as_view(),
        name="admin-wallet-detail",
    ),
    path(
        "admin/wallets/<int:wallet_id>/entries/",
        AdminWalletEntryListView.as_view(),
        name="admin-wallet-entries",
    ),
    path(
        "admin/wallets/<int:wallet_id>/holds/",
        AdminWalletHoldListView.as_view(),
        name="admin-wallet-holds",
    ),
    path(
        "admin/wallets/<int:wallet_id>/fund/",
        AdminWalletFundView.as_view(),
        name="admin-wallet-fund",
    ),
    path(
        "admin/wallets/<int:wallet_id>/debit/",
        AdminWalletDebitView.as_view(),
        name="admin-wallet-debit",
    ),
    path(
        "admin/wallets/<int:wallet_id>/holds/create/",
        AdminWalletCreateHoldView.as_view(),
        name="admin-wallet-create-hold",
    ),
    path(
        "admin/holds/<int:hold_id>/release/",
        AdminWalletReleaseHoldView.as_view(),
        name="admin-wallet-release-hold",
    ),
    path(
        "admin/holds/<int:hold_id>/capture/",
        AdminWalletCaptureHoldView.as_view(),
        name="admin-wallet-capture-hold",
    ),
    path(
        "admin/wallets/<int:wallet_id>/reconcile/",
        AdminWalletReconcileView.as_view(),
        name="admin-wallet-reconcile",
    ),
    path(
        "admin/wallets/<int:wallet_id>/repair/",
        AdminWalletRepairView.as_view(),
        name="admin-wallet-repair",
    ),
]

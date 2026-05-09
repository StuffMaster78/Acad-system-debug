from __future__ import annotations

from django.urls import path

from writer_payments_management.api.views.exposure_views import (
    ExposureLedgerDetailView,
    ExposureLedgerListView,
)
from writer_payments_management.api.views.financial_event_views import (
    FinancialEventDetailView,
    FinancialEventListView,
)
from writer_payments_management.api.views.reconciliation_actions_views import (
    RunReconciliationView,
)
from writer_payments_management.api.views.settlement_actions_views import (
    RunSettlementView,
)
from writer_payments_management.api.views.settlement_views import (
    SettlementDetailView,
    SettlementListView,
)
from writer_payments_management.api.views.wallet_actions_views import (
    WalletCreditView,
    WalletDebitView,
)
from writer_payments_management.api.views.wallet_views import (
    WalletDetailView,
    WalletListView,
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
]
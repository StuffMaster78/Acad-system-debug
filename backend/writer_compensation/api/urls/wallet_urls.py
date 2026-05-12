from __future__ import annotations

from django.urls import path

from writer_compensation.api.views.wallet_actions_views import (
    WalletCreditView,
    WalletDebitView,
)
from writer_compensation.api.views.wallet_views import (
    WalletDetailView,
    WalletListView,
)

urlpatterns = [
    path(
        "",
        WalletListView.as_view(),
        name="wallet-list",
    ),
    path(
        "<int:pk>/",
        WalletDetailView.as_view(),
        name="wallet-detail",
    ),
    path(
        "credit/",
        WalletCreditView.as_view(),
        name="wallet-credit",
    ),
    path(
        "debit/",
        WalletDebitView.as_view(),
        name="wallet-debit",
    ),
]
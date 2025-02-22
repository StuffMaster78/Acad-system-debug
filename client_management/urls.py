from django.urls import path
from . import views
from client_management.views import (
    BlacklistEmailListView,
    BlacklistEmailAddView,
    BlacklistEmailRemoveView
)

urlpatterns = [
    # Client Profiles
    path("clients/", views.ClientProfileListView.as_view(), name="client-list"),
    path("clients/<int:pk>/", views.ClientProfileDetailView.as_view(), name="client-detail"),
    path("clients/<int:pk>/edit/", views.ClientProfileUpdateView.as_view(), name="client-edit"),

    # Client Wallet
    path("clients/<int:client_id>/wallet/", views.ClientWalletView.as_view(), name="client-wallet"),

    # Admin Actions on Clients
    path("clients/<int:client_id>/actions/", views.ClientActionView.as_view(), name="client-actions"),

    # Profile Update Requests
    path("profile-update-requests/", views.ProfileUpdateRequestCreateView.as_view(), name="create-profile-update-request"),
    path("profile-update-requests/admin/", views.ProfileUpdateRequestListView.as_view(), name="list-profile-update-requests"),

    # Loyalty Management
    path("loyalty/tiers/", views.LoyaltyTierListView.as_view(), name="loyalty-tier-list"),
    path("loyalty/tiers/<int:pk>/", views.LoyaltyTierDetailView.as_view(), name="loyalty-tier-detail"),
    path("loyalty/transactions/<int:client_id>/", views.LoyaltyTransactionListView.as_view(), name="loyalty-transaction-list"),


    path("blacklist/", BlacklistEmailListView.as_view(), name="blacklist-list"),
    path("blacklist/add/", BlacklistEmailAddView.as_view(), name="blacklist-add"),
    path("blacklist/remove/", BlacklistEmailRemoveView.as_view(), name="blacklist-remove"),
]
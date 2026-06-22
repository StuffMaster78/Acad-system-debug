from django.urls import path, include
from rest_framework.routers import DefaultRouter
from client_management.views import (
    ClientProfileListView,
    ClientProfileDetailView,
    ClientProfileUpdateView,
    ClientWalletView,
    LoyaltyTierListView,
    LoyaltyTierDetailView,
    LoyaltyTransactionListView,
    ClientActionView,
    ProfileUpdateRequestCreateView,
    ProfileUpdateRequestListView,
    BlacklistEmailListView,
    BlacklistEmailAddView,
    BlacklistEmailRemoveView,
)
from client_management.views_dashboard import ClientDashboardViewSet
from client_management.views.badge_views import ClientBadgeViewSet, ClientBadgeAnalyticsViewSet

router = DefaultRouter()
router.register(r'dashboard', ClientDashboardViewSet, basename='client-dashboard')
router.register(r'badges', ClientBadgeViewSet, basename='client-badges')
router.register(r'badge-analytics', ClientBadgeAnalyticsViewSet, basename='client-badge-analytics')

urlpatterns = [
    path("clients/", ClientProfileListView.as_view(), name="client-list"),
    path("clients/<int:pk>/", ClientProfileDetailView.as_view(), name="client-detail"),
    path("clients/<int:pk>/edit/", ClientProfileUpdateView.as_view(), name="client-edit"),
    path("clients/<int:client_id>/wallet/", ClientWalletView.as_view(), name="client-wallet"),
    path("clients/<int:client_id>/actions/", ClientActionView.as_view(), name="client-actions"),
    path("profile-update-requests/", ProfileUpdateRequestCreateView.as_view(), name="create-profile-update-request"),
    path("profile-update-requests/admin/", ProfileUpdateRequestListView.as_view(), name="list-profile-update-requests"),
    path("loyalty/tiers/", LoyaltyTierListView.as_view(), name="loyalty-tier-list"),
    path("loyalty/tiers/<int:pk>/", LoyaltyTierDetailView.as_view(), name="loyalty-tier-detail"),
    path("loyalty/transactions/<int:client_id>/", LoyaltyTransactionListView.as_view(), name="loyalty-transaction-list"),
    path("", include(router.urls)),
    path("blacklist/", BlacklistEmailListView.as_view(), name="blacklist-list"),
    path("blacklist/add/", BlacklistEmailAddView.as_view(), name="blacklist-add"),
    path("blacklist/remove/", BlacklistEmailRemoveView.as_view(), name="blacklist-remove"),
]

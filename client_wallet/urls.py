from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientWalletViewSet, LoyaltyTransactionViewSet, ReferralBonusViewSet, ReferralStatsViewSet

# Initialize the router
router = DefaultRouter()

# Register the viewsets with the router
router.register(r'client-wallet', ClientWalletViewSet, basename='client-wallet')
router.register(r'loyalty-transactions', LoyaltyTransactionViewSet, basename='loyalty-transactions')
router.register(r'referral-bonuses', ReferralBonusViewSet, basename='referral-bonuses')
router.register(r'referral-stats', ReferralStatsViewSet, basename='referral-stats')

# Define the URL patterns
urlpatterns = [
    path('api/', include(router.urls)),  # Include all the API viewsets
]
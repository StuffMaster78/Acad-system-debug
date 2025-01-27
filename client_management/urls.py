from django.urls import path
from .views import ClientProfileDetailView, LoyaltyTransactionListView, LoyaltyPointView, LoyaltyPointHistoryView, RedeemLoyaltyPointsView

urlpatterns = [
    # Endpoint to fetch the client's profile
    path('profile/', ClientProfileDetailView.as_view(), name='client-profile'),
    
    # Endpoint to fetch loyalty transactions for a client
    path('loyalty-transactions/', LoyaltyTransactionListView.as_view(), name='loyalty-transactions'),


    path('loyalty-points/', LoyaltyPointView.as_view(), name='loyalty-points'),
    path('loyalty-point-history/', LoyaltyPointHistoryView.as_view(), name='loyalty-point-history'),
    path('redeem-loyalty-points/', RedeemLoyaltyPointsView.as_view(), name='redeem-loyalty-points'),
]
from django.urls import path
from .views import ClientProfileDetailView, LoyaltyTransactionListView

urlpatterns = [
    # Endpoint to fetch the client's profile
    path('profile/', ClientProfileDetailView.as_view(), name='client-profile'),
    
    # Endpoint to fetch loyalty transactions for a client
    path('loyalty-transactions/', LoyaltyTransactionListView.as_view(), name='loyalty-transactions'),
]
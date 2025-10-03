from django.urls import path
from .views import WalletViewSet, WithdrawalRequestViewSet
# from refunds.webhooks.stripe import stripe_webhook

urlpatterns = [
    path('wallets/', WalletViewSet.as_view({'get': 'list'}), name='wallet-detail'),
    path('wallets/top-up/', WalletViewSet.as_view({'post': 'top_up'}), name='wallet-top-up'),
    path('wallets/withdraw/', WalletViewSet.as_view({'post': 'withdraw'}), name='wallet-withdraw'),
    # path("webhooks/stripe/", stripe_webhook, name="stripe-webhook"),
    path('withdrawal-requests/', WithdrawalRequestViewSet.as_view({'get': 'list'}), name='withdrawal-requests'),
    path('withdrawal-requests/<int:pk>/approve/', WithdrawalRequestViewSet.as_view({'post': 'approve_request'}), name='approve-withdrawal'),
    path('withdrawal-requests/<int:pk>/reject/', WithdrawalRequestViewSet.as_view({'post': 'reject_request'}), name='reject-withdrawal'),
]

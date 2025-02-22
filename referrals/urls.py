from django.urls import path
from .views import ReferralViewSet, ReferralBonusConfigViewSet

urlpatterns = [
    # Referral management
    path('referrals/', ReferralViewSet.as_view({'get': 'list', 'post': 'create'}), name='referrals-list'),
    path('referrals/generate-code/', ReferralViewSet.as_view({'post': 'generate_code'}), name='generate-referral-code'),
    path('referrals/credit-bonus/', ReferralViewSet.as_view({'post': 'credit_bonus'}), name='credit-referral-bonus'),

    # Referral bonus configurations
    path('referral-configs/', ReferralBonusConfigViewSet.as_view({'get': 'list', 'post': 'create'}), name='referral-config-list'),
    path('referral-configs/<int:pk>/', ReferralBonusConfigViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}), name='referral-config-detail'),
]
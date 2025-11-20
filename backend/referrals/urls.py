from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReferralViewSet, ReferralBonusConfigViewSet, ReferralCodeViewSet,
    ReferralStatsViewSet, ReferralBonusDecayViewSet, ReferralReportsAPI,
    AwardReferralBonusAPI, ReferralAdminViewSet
)

# Router for ViewSets
router = DefaultRouter()
router.register(r'referrals', ReferralViewSet, basename='referral')
router.register(r'referral-bonus-configs', ReferralBonusConfigViewSet, basename='referral-config')
router.register(r'referral-admin', ReferralAdminViewSet, basename='referral-admin')
router.register(r'referral-codes', ReferralCodeViewSet, basename='referral-code')
router.register(r'referral-stats', ReferralStatsViewSet, basename='referral-stats')
router.register(r'referral-bonus-decays', ReferralBonusDecayViewSet, basename='referral-decay')

# Custom API Views
urlpatterns = [
    path('', include(router.urls)),
    path('referral-reports/', ReferralReportsAPI.as_view(), name='referral-reports'),
    path('award-referral-bonus/<int:referral_id>/', AwardReferralBonusAPI.as_view(), name='award-referral-bonus'),
]
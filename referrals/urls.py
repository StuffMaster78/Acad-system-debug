from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReferralViewSet, ReferralBonusConfigViewSet, ReferralCodeViewSet,
    ReferralStatsViewSet, ReferralBonusDecayViewSet, ReferralReportsAPI, AwardReferralBonusAPI
)

# Router for ViewSets
router = DefaultRouter()
router.register(r'referrals', ReferralViewSet)
router.register(r'referral-bonus-configs', ReferralBonusConfigViewSet)
router.register(r'referral-codes', ReferralCodeViewSet)
router.register(r'referral-stats', ReferralStatsViewSet)
router.register(r'referral-bonus-decays', ReferralBonusDecayViewSet)

# Custom API Views
urlpatterns = [
    path('api/', include(router.urls)),
    path('api/referral-reports/', ReferralReportsAPI.as_view(), name='referral-reports'),
    path('api/award-referral-bonus/<int:referral_id>/', AwardReferralBonusAPI.as_view(), name='award-referral-bonus'),
]
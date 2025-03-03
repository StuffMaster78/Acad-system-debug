from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReferralViewSet, ReferralBonusConfigViewSet, ReferralAdminViewSet

# Router setup
router = DefaultRouter()
router.register(r'referrals', ReferralViewSet, basename='referrals')
router.register(r'referral-configs', ReferralBonusConfigViewSet, basename='referral-configs')
router.register(r'admin/referrals', ReferralAdminViewSet, basename='admin-referrals')  # Register Admin ViewSet

urlpatterns = [
    path('', include(router.urls)),  # Includes all registered ViewSets
]

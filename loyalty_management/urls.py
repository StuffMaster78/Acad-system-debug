from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoyaltyTierViewSet, LoyaltyTransactionViewSet, MilestoneViewSet, ClientBadgeViewSet

router = DefaultRouter()
router.register(r'loyalty-tiers', LoyaltyTierViewSet)
router.register(r'loyalty-transactions', LoyaltyTransactionViewSet)
router.register(r'milestones', MilestoneViewSet)
router.register(r'client-badges', ClientBadgeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
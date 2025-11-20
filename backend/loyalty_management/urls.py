from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LoyaltyTierViewSet, LoyaltyTransactionViewSet,
    MilestoneViewSet, ClientBadgeViewSet,
    LoyaltyPointsConversionConfigViewSet,
    AdminForceConversionView, LoyaltySummaryView,
    LoyaltyConvertView, LoyaltyTransactionListView,
    AdminLoyaltyAwardView, AdminLoyaltyForceConvertView,
    AdminLoyaltyConversionConfigView, AdminLoyaltyTransferView,
    AdminLoyaltyDeductView,
    RedemptionCategoryViewSet, RedemptionItemViewSet, RedemptionRequestViewSet,
    LoyaltyAnalyticsViewSet, DashboardWidgetViewSet,
)

router = DefaultRouter()
router.register(r'loyalty-tiers', LoyaltyTierViewSet)
router.register(r'loyalty-transactions', LoyaltyTransactionViewSet)
router.register(r'milestones', MilestoneViewSet)
router.register(r'client-badges', ClientBadgeViewSet)
router.register(r'loyalty-points-conversion-config', LoyaltyPointsConversionConfigViewSet)
# Redemption system
router.register(r'redemption-categories', RedemptionCategoryViewSet)
router.register(r'redemption-items', RedemptionItemViewSet)
router.register(r'redemption-requests', RedemptionRequestViewSet)
# Analytics dashboard
router.register(r'analytics', LoyaltyAnalyticsViewSet, basename='loyalty-analytics')
router.register(r'dashboard-widgets', DashboardWidgetViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("admin/force-convert/<int:client_id>/", AdminForceConversionView.as_view(), name="admin-force-convert"),
    path('loyalty/summary/', LoyaltySummaryView.as_view(), name='loyalty-summary'),
    path('loyalty/convert/', LoyaltyConvertView.as_view(), name='loyalty-convert'),
    path('loyalty/transactions/', LoyaltyTransactionListView.as_view(), name='loyalty-transactions'),
    path('admin/award-loyalty/', AdminLoyaltyAwardView.as_view(), name='admin-award-loyalty'),
    path('admin/force-convert/<int:client_id>/', AdminLoyaltyForceConvertView.as_view(), name='admin-loyalty-force-convert'),
    path('admin/loyalty-conversion-config/', AdminLoyaltyConversionConfigView.as_view(), name='admin-loyalty-conversion-config'),
    path('admin/transfer-loyalty/', AdminLoyaltyTransferView.as_view(), name='admin-loyalty-transfer'),
    path('admin/deduct-loyalty/', AdminLoyaltyDeductView.as_view(), name='admin-loyalty-deduct'),
]
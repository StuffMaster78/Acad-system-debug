from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WriterBadgeTimelineViewSet, WriterProfileViewSet, WriterLevelViewSet,
    WriterConfigViewSet, WriterOrderRequestViewSet, 
    WriterOrderTakeViewSet, WriterPayoutPreferenceViewSet,
    WriterPaymentViewSet, WriterEarningsHistoryViewSet,
    WriterEarningsReviewRequestViewSet, WriterRewardViewSet,
    WriterRewardCriteriaViewSet, ProbationViewSet,
    WriterPenaltyViewSet, WriterSuspensionViewSet,
    WriterActionLogViewSet, WriterSupportTicketViewSet,
    WriterDeadlineExtensionRequestViewSet,
    WriterOrderHoldRequestViewSet, WriterOrderReopenRequestViewSet,
    WriterActivityLogViewSet, WriterRatingCooldownViewSet,
    WriterFileDownloadLogViewSet, WriterIPLogViewSet,
    WriterStatusViewSet, WebhookSettingsViewSet,
    TipCreateView, TipListView, CurrencyConversionRateViewSet,
    WriterDashboardStatusView, WriterPerformanceSnapshotViewSet,
    WriterPerformanceDashboardView, WriterPaymentViewSet,
    WriterWarningViewSet, WriterWarningSelfViewSet,
    WriterBadgeAdminViewSet
)

from writer_management.views import WebhookSettingsViewSet
from writer_management.views import TipCreateView
from writer_management.views import WriterActionLogViewSet
from writer_management.views import WriterPaymentViewSet
from writer_management.views import WriterEarningsHistoryViewSet
from writer_management.views import WriterEarningsReviewRequestViewSet
from writer_management.views import WriterPayoutPreferenceViewSet
from writer_management.views import WriterRewardViewSet
from writer_management.views import WriterRewardCriteriaViewSet
from writer_management.views import WriterProfileViewSet
from writer_management.views import WriterLevelViewSet
from writer_management.views import WriterConfigViewSet
from writer_management.views import WriterOrderRequestViewSet
from writer_management.views import WriterOrderTakeViewSet
from writer_management.views import (
    WriterSupportTicketViewSet, WriterDeadlineExtensionRequestViewSet,
    WriterOrderHoldRequestViewSet, WriterOrderReopenRequestViewSet,
    WriterActivityLogViewSet, WriterIPLogViewSet,
    WriterRatingCooldownViewSet, WriterFileDownloadLogViewSet,
    WriterActionLogViewSet, WriterPenaltyViewSet,
    WriterSuspensionViewSet, ProbationViewSet
)
from writer_management.views import TipListView
from writer_management.views import CurrencyConversionRateViewSet

# DRF Router
router = DefaultRouter()

### ---------------- Writer Profile & Config Routes ---------------- ###
router.register(r'profiles', WriterProfileViewSet, basename='writer-profile')
router.register(r'levels', WriterLevelViewSet, basename='writer-level')
router.register(r'config', WriterConfigViewSet, basename='writer-config')

### ---------------- Order Requests & Takes ---------------- ###
router.register(r'order-requests', WriterOrderRequestViewSet, basename='writer-order-request')
router.register(r'order-takes', WriterOrderTakeViewSet, basename='writer-order-take')

### ---------------- Payment & Earnings Routes ---------------- ###
router.register(r'payout-preferences', WriterPayoutPreferenceViewSet, basename='writer-payout-preference')
router.register(r'payments', WriterPaymentViewSet, basename='writer-payment')
# router.register(r'payment-history', PaymentHistoryViewSet, basename='writer-payment-history')
router.register(r'earnings-history', WriterEarningsHistoryViewSet, basename='writer-earnings-history')
router.register(r'earnings-reviews', WriterEarningsReviewRequestViewSet, basename='writer-earnings-review')

### ---------------- Writer Rewards, Probation, and Penalties ---------------- ###
router.register(r'rewards', WriterRewardViewSet, basename='writer-reward')
router.register(r'reward-criteria', WriterRewardCriteriaViewSet, basename='writer-reward-criteria')
router.register(r'probations', ProbationViewSet, basename='writer-probation')
router.register(r'penalties', WriterPenaltyViewSet, basename='writer-penalty')
router.register(r'suspensions', WriterSuspensionViewSet, basename='writer-suspension')

### ---------------- Support Tickets & Requests ---------------- ###
router.register(r'support-tickets', WriterSupportTicketViewSet, basename='writer-support-ticket')
router.register(r'deadline-extension-requests', WriterDeadlineExtensionRequestViewSet, basename='writer-deadline-extension-request')
router.register(r'hold-requests', WriterOrderHoldRequestViewSet, basename='writer-order-hold-request')
router.register(r'reopen-requests', WriterOrderReopenRequestViewSet, basename='writer-order-reopen-request')

### ---------------- Writer Activity & Logs ---------------- ###
router.register(r'activity-logs', WriterActivityLogViewSet, basename='writer-activity-log')
router.register(r'ip-logs', WriterIPLogViewSet, basename='writer-ip-log')
router.register(r'rating-cooldowns', WriterRatingCooldownViewSet, basename='writer-rating-cooldown')
router.register(r'file-download-logs', WriterFileDownloadLogViewSet, basename='writer-file-download-log')

### ---------------- Writer Action Logs ---------------- ###
router.register(r'action-logs', WriterActionLogViewSet, basename='writer-action-log')
# Note: Ensure all viewsets are properly implemented in views.py

### ---------------- Webhook Settings Routes ---------------- ###
router.register("webhooks", WebhookSettingsViewSet, basename="webhook-settings")

## ---------------- Tipping Routes ---------------- ###
# Note: Ensure TipCreateView and TipListView are implemented in views.py
# These views should handle the creation and listing of tips sent by clients to writers.    

## ---------------- Conversion Rate Routes ---------------- ###
router.register(r"conversion-rates", CurrencyConversionRateViewSet, basename="conversion-rate")

## ---------------- Writer Payment Routes ---------------- ###
router.register(r"writers-payments", WriterPaymentViewSet, basename="writers-payment")

## ---------------- Writer Status Routes ---------------- ###
router.register(r"writer-status", WriterStatusViewSet, basename="writer-status")

### ---------------- Dashboard Status View ---------------- ###
router.register(
    r"performance-snapshots",
    WriterPerformanceSnapshotViewSet,
    basename="writer-performance-snapshot"
)

## ---------------- Issue Warning ---------------- ###
router.register(r"writer-warnings", WriterWarningViewSet, basename="writer-warning")
router.register(r'me/writer-warnings', WriterWarningSelfViewSet, basename='my-warnings')


## ---------------- Badge System Routes ---------------- ###
router.register(
    r"admin/badges", WriterBadgeAdminViewSet, basename="admin-writer-badges"
)
router.register(
    r"my-badges", WriterBadgeTimelineViewSet, basename="my-badge-timeline"
)

# Include all registered routes
urlpatterns = [
    path('', include(router.urls)),
    path("tip/", TipCreateView.as_view(), name="tip-create"),
    path("tips/", TipListView.as_view(), name="tip-list"),
    path(
        "writer/dashboard-status/",
        WriterDashboardStatusView.as_view(),
        name="writer-dashboard-status",
    ),
    path("dashboard/metrics/", WriterPerformanceDashboardView.as_view()),
]
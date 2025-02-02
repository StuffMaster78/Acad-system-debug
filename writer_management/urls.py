from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    WriterProfileViewSet, WriterLevelViewSet, WriterConfigViewSet, WriterOrderRequestViewSet, WriterOrderTakeViewSet,
    WriterPayoutPreferenceViewSet, WriterPaymentViewSet, PaymentHistoryViewSet, WriterEarningsHistoryViewSet,
    WriterEarningsReviewRequestViewSet, WriterRewardViewSet, WriterRewardCriteriaViewSet, ProbationViewSet,
    WriterPenaltyViewSet, WriterSuspensionViewSet, WriterActionLogViewSet, WriterSupportTicketViewSet,
    WriterDeadlineExtensionRequestViewSet, WriterOrderHoldRequestViewSet, WriterOrderReopenRequestViewSet,
    WriterActivityLogViewSet, WriterRatingCooldownViewSet, WriterFileDownloadLogViewSet, WriterIPLogViewSet
)

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
router.register(r'payment-history', PaymentHistoryViewSet, basename='writer-payment-history')
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

# Include all registered routes
urlpatterns = [
    path('', include(router.urls)),
]
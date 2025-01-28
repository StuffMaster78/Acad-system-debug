from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SupportProfileViewSet,
    SupportActionLogViewSet,
    SupportActivityLogViewSet,
    DisputeResolutionLogViewSet,
    TicketAssignmentViewSet,
    SupportAvailabilityViewSet,
    SupportPerformanceViewSet,
    SupportNotificationViewSet,
    EscalationLogViewSet,
)

router = DefaultRouter()
router.register("profiles", SupportProfileViewSet, basename="support-profile")
router.register("action-logs", SupportActionLogViewSet, basename="support-action-log")
router.register("activity-logs", SupportActivityLogViewSet, basename="support-activity-log")
router.register("dispute-resolution-logs", DisputeResolutionLogViewSet, basename="dispute-resolution-log")
router.register("ticket-assignments", TicketAssignmentViewSet, basename="ticket-assignment")
router.register("availability", SupportAvailabilityViewSet, basename="support-availability")
router.register("performance", SupportPerformanceViewSet, basename="support-performance")
router.register("notifications", SupportNotificationViewSet, basename="support-notification")
router.register("escalations", EscalationLogViewSet, basename="escalation-log")

urlpatterns = [
    path("", include(router.urls)),
]
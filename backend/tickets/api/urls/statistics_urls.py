from __future__ import annotations

from rest_framework.routers import DefaultRouter

from tickets.api.views import TicketLogViewSet, TicketStatisticsViewSet

router = DefaultRouter()
router.register(r"logs", TicketLogViewSet, basename="ticket-log")
router.register(
    r"statistics",
    TicketStatisticsViewSet,
    basename="ticketstatistics",
)

urlpatterns = router.urls

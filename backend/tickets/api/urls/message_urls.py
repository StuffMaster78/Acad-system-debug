from __future__ import annotations

from rest_framework.routers import DefaultRouter

from tickets.api.views import TicketMessageViewSet

router = DefaultRouter()
router.register(r"messages", TicketMessageViewSet, basename="ticket-message")

urlpatterns = router.urls

from __future__ import annotations

from rest_framework.routers import DefaultRouter

from tickets.api.views import TicketSLAViewSet

router = DefaultRouter()
router.register(r"sla", TicketSLAViewSet, basename="ticket-sla")

urlpatterns = router.urls

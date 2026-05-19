from __future__ import annotations

from rest_framework.routers import DefaultRouter

from tickets.api.views import TicketFileViewSet

router = DefaultRouter()
router.register(r"attachments", TicketFileViewSet, basename="ticket-attachment")

urlpatterns = router.urls

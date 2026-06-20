from __future__ import annotations

from rest_framework.routers import DefaultRouter

from orders.views.writers.writer_requests import WriterRequestViewSet

router = DefaultRouter()
router.register(r"writer-requests", WriterRequestViewSet, basename="writer-request")

urlpatterns = router.urls

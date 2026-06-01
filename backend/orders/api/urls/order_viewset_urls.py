from __future__ import annotations

from rest_framework.routers import DefaultRouter

from orders.views.orders.base import OrderBaseViewSet

router = DefaultRouter()
router.register(r"orders", OrderBaseViewSet, basename="order")

urlpatterns = router.urls

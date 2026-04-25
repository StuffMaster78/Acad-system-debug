from django.urls import path

from orders.api.views.progressive_delivery.progressive_delivery_views import (
    CreateProgressivePlanView,
)

urlpatterns = [
    path(
        "orders/<int:order_id>/progressive-plan/",
        CreateProgressivePlanView.as_view(),
    ),
]
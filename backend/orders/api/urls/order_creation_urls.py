from __future__ import annotations

from django.urls import path

from orders.api.views.order_creation.client_lookup_view import ClientLookupView
from orders.api.views.order_creation.order_creation_views import (
    CreateOrderView,
)

urlpatterns = [
    path(
        "orders/create/",
        CreateOrderView.as_view(),
        name="create-order",
    ),
    path(
        "client-lookup/",
        ClientLookupView.as_view(),
        name="client-lookup",
    ),
]
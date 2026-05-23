from __future__ import annotations

from django.urls import include, path


app_name = "special_orders"

urlpatterns = [
    path("", include("special_orders.api.urls.urls")),
]

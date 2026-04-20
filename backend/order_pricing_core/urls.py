"""
Root URL configuration for the order_pricing_core app.
"""

from __future__ import annotations

from django.urls import include
from django.urls import path

urlpatterns = [
    path("", include("order_pricing_core.api.urls")),
]
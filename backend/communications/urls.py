from __future__ import annotations

from django.urls import include
from django.urls import path

app_name = "communications"

urlpatterns = [
    path("", include("communications.api.urls")),
]
from __future__ import annotations

from django.urls import path, include


urlpatterns = [
    path("", include("writer_compensation.api.urls")),
]
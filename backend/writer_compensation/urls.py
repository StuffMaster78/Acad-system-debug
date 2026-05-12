from __future__ import annotations

from django.urls import path, include


urlpatterns = [
    path("api/", include("writer_compensation.api.urls")),
]
from __future__ import annotations

from django.urls import include
from django.urls import path

urlpatterns = [
    path("", include("activity.api.urls")),
]
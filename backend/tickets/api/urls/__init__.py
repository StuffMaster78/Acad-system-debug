from __future__ import annotations

from django.urls import include, path

urlpatterns = [
    path("", include("tickets.api.urls.ticket_urls")),
    path("", include("tickets.api.urls.message_urls")),
    path("", include("tickets.api.urls.file_urls")),
    path("", include("tickets.api.urls.sla_urls")),
    path("", include("tickets.api.urls.statistics_urls")),
]

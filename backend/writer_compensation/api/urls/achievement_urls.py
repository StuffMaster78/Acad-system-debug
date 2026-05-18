from __future__ import annotations

from django.urls import path

from writer_compensation.api.views.writer_achievement_views import (
    WriterAchievementListAPIView,
)

app_name = "achievement_api"

urlpatterns = [
    path(
        "writers/<uuid:writer_id>/",
        WriterAchievementListAPIView.as_view(),
        name="writer-achievements",
    ),
]
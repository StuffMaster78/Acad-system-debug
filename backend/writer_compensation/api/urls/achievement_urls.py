from __future__ import annotations

from django.urls import path

from writer_compensation.api.views.writer_achievement_views import (
    WriterAchievementListView,
)

app_name = "achievement_api"

urlpatterns = [
    path(
        "writers/<uuid:writer_id>/",
        WriterAchievementListView.as_view(),
        name="writer-achievements",
    ),
]

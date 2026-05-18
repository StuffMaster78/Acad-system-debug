from __future__ import annotations

from django.urls import path

from writer_management.api.views.writer_achievement_views import (
    WriterAchievementListView,
)


urlpatterns = [
    path(
        "<int:writer_id>/",
        WriterAchievementListView.as_view(),
        name="writer-achievement-list",
    ),
]
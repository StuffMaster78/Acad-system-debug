from __future__ import annotations

from django.contrib import admin

from writer_management.models.writer_achievement import (
    WriterAchievement,
)


@admin.register(WriterAchievement)
class WriterAchievementAdmin(
    admin.ModelAdmin,
):
    """
    Admin configuration for achievements.
    """

    list_display = (
        "title",
        "writer",
        "achievement_type",
        "unlocked_at",
    )

    list_filter = (
        "achievement_type",
    )

    search_fields = (
        "title",
        "writer__registration_id",
    )

    ordering = (
        "-unlocked_at",
    )
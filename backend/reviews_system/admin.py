from django.contrib import admin

from reviews_system.models.review import Review
from reviews_system.models.moderation_log import (
    ReviewModerationLog,
)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin interface for managing reviews.
    """

    list_display = (
        "id",
        "reviewer_id",
        "target_type",
        "target_id",
        "rating",
        "moderation_state",
        "visibility",
        "created_at",
    )

    list_filter = (
        "target_type",
        "moderation_state",
        "visibility",
        "is_verified",
    )

    search_fields = (
        "id",
        "reviewer_id",
        "target_id",
        "title",
        "comment",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "moderated_at",
    )

    ordering = ("-created_at",)


@admin.register(ReviewModerationLog)
class ReviewModerationLogAdmin(admin.ModelAdmin):
    """
    Admin interface for moderation audit trail.
    """

    list_display = (
        "id",
        "review_id",
        "previous_state",
        "new_state",
        "previous_visibility",
        "new_visibility",
        "moderator_id",
        "created_at",
    )

    list_filter = (
        "previous_state",
        "new_state",
        "previous_visibility",
        "new_visibility",
    )

    search_fields = (
        "review_id",
        "reason",
        "moderator_id",
    )

    readonly_fields = (
        "id",
        "created_at",
    )

    ordering = ("-created_at",)
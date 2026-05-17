from django.contrib import admin

from writer_compensation.models.writer_reward import (
    WriterReward,
)


@admin.register(WriterReward)
class WriterRewardAdmin(admin.ModelAdmin):
    list_display = (
        "reward_title",
        "writer",
        "website",
        "reward_amount",
        "status",
        "issued_at",
    )

    list_filter = (
        "status",
        "website",
        "reward_rule",
    )

    search_fields = (
        "reward_title",
        "writer__registration_id",
        "writer__pen_name",
    )

    readonly_fields = (
        "issued_at",
        "revoked_at",
        "metadata",
    )
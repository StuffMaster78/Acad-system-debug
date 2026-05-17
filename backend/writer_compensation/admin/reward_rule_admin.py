from django.contrib import admin

from writer_compensation.models.reward_rule import RewardRule


@admin.register(RewardRule)
class RewardRuleAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "website",
        "rule_type",
        "reward_type",
        "reward_amount",
        "is_active",
    )

    list_filter = (
        "rule_type",
        "reward_type",
        "is_active",
        "website",
    )

    search_fields = (
        "name",
        "slug",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )
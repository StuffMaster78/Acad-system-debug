from __future__ import annotations

from rest_framework import serializers

from writer_management.models.badges import Badge


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = [
            "id", "name", "icon", "type", "description",
            "auto_award", "rule_code", "rule_description",
            "website", "is_active", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

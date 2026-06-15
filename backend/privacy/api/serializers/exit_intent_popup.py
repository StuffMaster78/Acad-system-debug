from rest_framework import serializers

from privacy.models import ExitIntentPopupConfig


class ExitIntentPopupConfigSerializer(serializers.ModelSerializer):
    website_name = serializers.CharField(source="website.name", read_only=True)

    class Meta:
        model = ExitIntentPopupConfig
        fields = [
            "id",
            "website",
            "website_name",
            "is_enabled",
            "trigger",
            "title",
            "body",
            "primary_cta_label",
            "primary_cta_url",
            "secondary_cta_label",
            "image_url",
            "show_on_paths",
            "suppress_on_paths",
            "delay_seconds",
            "scroll_depth_percent",
            "cooldown_hours",
            "max_shows_per_session",
            "requires_marketing_consent",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "website", "website_name", "created_at", "updated_at"]

    def validate_show_on_paths(self, value):
        return self._validate_paths(value)

    def validate_suppress_on_paths(self, value):
        return self._validate_paths(value)

    @staticmethod
    def _validate_paths(value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Use a list of path prefixes.")
        cleaned = []
        for item in value:
            path = str(item or "").strip()
            if not path:
                continue
            cleaned.append(path if path.startswith("/") else f"/{path}")
        return cleaned


class PublicExitIntentPopupConfigSerializer(ExitIntentPopupConfigSerializer):
    class Meta(ExitIntentPopupConfigSerializer.Meta):
        fields = [
            "is_enabled",
            "trigger",
            "title",
            "body",
            "primary_cta_label",
            "primary_cta_url",
            "secondary_cta_label",
            "image_url",
            "show_on_paths",
            "suppress_on_paths",
            "delay_seconds",
            "scroll_depth_percent",
            "cooldown_hours",
            "max_shows_per_session",
            "requires_marketing_consent",
            "updated_at",
        ]

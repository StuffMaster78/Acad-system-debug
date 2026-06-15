from __future__ import annotations

from rest_framework import serializers

from privacy.models import CookieConsentRecord


class CookieConsentRecordSerializer(serializers.ModelSerializer):
    website_name = serializers.CharField(source="website.name", read_only=True)

    class Meta:
        model = CookieConsentRecord
        fields = [
            "id",
            "website",
            "website_name",
            "anonymous_id",
            "consent_version",
            "policy_version",
            "necessary",
            "preferences",
            "analytics",
            "marketing",
            "source",
            "source_host",
            "created_at",
            "updated_at",
            "revoked_at",
        ]
        read_only_fields = [
            "id",
            "website",
            "website_name",
            "source_host",
            "created_at",
            "updated_at",
            "revoked_at",
        ]


class CookieConsentWriteSerializer(serializers.Serializer):
    anonymous_id = serializers.UUIDField(required=False)
    consent_version = serializers.CharField(required=False, max_length=40)
    policy_version = serializers.CharField(required=False, max_length=40)
    preferences = serializers.BooleanField(default=False)
    analytics = serializers.BooleanField(default=False)
    marketing = serializers.BooleanField(default=False)
    source = serializers.ChoiceField(
        choices=CookieConsentRecord.SOURCE_CHOICES,
        default=CookieConsentRecord.SOURCE_BANNER,
    )

    def validate(self, attrs):
        attrs["necessary"] = True
        return attrs

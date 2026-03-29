from rest_framework import serializers


class AccountSummaryRoleSerializer(serializers.Serializer):
    """Serializer for role data embedded in account summary."""

    id = serializers.IntegerField()
    key = serializers.CharField()
    name = serializers.CharField()
    is_system_role = serializers.BooleanField()


class AccountSummarySerializer(serializers.Serializer):
    """Serializer for account summary payloads."""

    account_profile_id = serializers.IntegerField()
    website_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    status = serializers.CharField()
    onboarding_status = serializers.CharField()
    is_primary = serializers.BooleanField()
    activated_at = serializers.DateTimeField(allow_null=True)
    suspended_at = serializers.DateTimeField(allow_null=True)
    suspension_reason = serializers.CharField(allow_blank=True)
    roles = AccountSummaryRoleSerializer(many=True)
    metadata = serializers.JSONField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
"""
Login Alert Preferences Serializers

LoginAlertPreference model was never migrated (no DB table). These are plain
Serializer stubs so the __init__.py export list stays intact without
referencing the nonexistent model.
"""
from rest_framework import serializers


class LoginAlertPreferenceSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    notify_new_login = serializers.BooleanField(default=True)
    notify_new_device = serializers.BooleanField(default=True)
    notify_new_location = serializers.BooleanField(default=True)
    email_enabled = serializers.BooleanField(default=True)
    push_enabled = serializers.BooleanField(default=False)
    in_app_enabled = serializers.BooleanField(default=True)


class LoginAlertPreferenceUpdateSerializer(serializers.Serializer):
    notify_new_login = serializers.BooleanField(required=False)
    notify_new_device = serializers.BooleanField(required=False)
    notify_new_location = serializers.BooleanField(required=False)
    email_enabled = serializers.BooleanField(required=False)
    push_enabled = serializers.BooleanField(required=False)
    in_app_enabled = serializers.BooleanField(required=False)

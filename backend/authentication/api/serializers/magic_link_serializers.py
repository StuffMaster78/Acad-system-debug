from rest_framework import serializers


class MagicLinkRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class MagicLinkRequestResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()


class MagicLinkConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()


class MagicLinkConfirmResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    session_id = serializers.IntegerField()
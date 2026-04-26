from __future__ import annotations

from rest_framework import serializers


class AdminFileReplaceSerializer(serializers.Serializer):
    """
    Replace an existing file (versioning).
    """

    file = serializers.FileField()
    notes = serializers.CharField(required=False, allow_blank=True)


class ExternalLinkSubmitSerializer(serializers.Serializer):
    """
    Submit external file link.
    """

    url = serializers.URLField()
    purpose = serializers.CharField(max_length=64)
    title = serializers.CharField(required=False, allow_blank=True)


class CMSUploadSerializer(serializers.Serializer):
    """
    CMS-specific upload.
    """

    file = serializers.FileField()
    purpose = serializers.CharField(max_length=64)
    visibility = serializers.CharField(max_length=64)
    is_primary = serializers.BooleanField(default=False)
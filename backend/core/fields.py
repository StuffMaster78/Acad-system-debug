"""
Custom file fields with different storage backends.
"""
from django.db import models
from django.conf import settings
from core.storage_backends import PublicMediaStorage


class PublicFileField(models.FileField):
    """
    FileField that uses public storage backend.
    Use for files that should be publicly accessible (e.g., blog images).
    """
    def __init__(self, *args, **kwargs):
        # Only use public storage if S3 is enabled
        if getattr(settings, 'USE_S3', False):
            kwargs['storage'] = PublicMediaStorage()
        super().__init__(*args, **kwargs)


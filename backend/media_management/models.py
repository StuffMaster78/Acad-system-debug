from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from websites.models import Website


class MediaAsset(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = "image", _("Image")
        VIDEO = "video", _("Video")
        DOCUMENT = "document", _("Document")
        AUDIO = "audio", _("Audio")
        OTHER = "other", _("Other")

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="media_assets",
    )
    type = models.CharField(
        max_length=20,
        choices=MediaType.choices,
        default=MediaType.IMAGE,
    )

    # Either a file we host, or an external embed (YouTube/Vimeo/etc.)
    # FileField automatically uses DEFAULT_FILE_STORAGE from settings (cloud or local)
    file = models.FileField(
        upload_to="media_assets/",
        null=True,
        blank=True,
        help_text="Uploaded media file (image, video, document, etc.)",
    )
    embed_provider = models.CharField(
        max_length=50,
        blank=True,
        help_text="Provider name for embedded media, e.g. youtube, vimeo",
    )
    embed_id = models.CharField(
        max_length=255,
        blank=True,
        help_text="Provider-specific ID or URL for embedded media",
    )

    title = models.CharField(max_length=255, blank=True)
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="Alt text / accessibility description (for images and thumbnails).",
    )
    caption = models.TextField(blank=True)
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Optional list of tags/keywords for searching.",
    )

    mime_type = models.CharField(max_length=100, blank=True)
    size_bytes = models.BigIntegerField(null=True, blank=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_media_assets",
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Soft-delete flag; inactive assets are hidden from pickers.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["website", "type"]),
            models.Index(fields=["website", "is_active", "created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self) -> str:
        base = self.title or (self.file.name if self.file else self.embed_id)
        return f"{self.website.name}: {base}"


class MediaUsage(models.Model):
    """
    Generic model to track where media files are used across the system.
    Supports both MediaAsset and BlogMediaFile (and future media types).
    """
    # Reference to media - can be MediaAsset or BlogMediaFile
    # Using GenericForeignKey for flexibility
    media_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text="Content type of the media (MediaAsset, BlogMediaFile, etc.)"
    )
    media_object_id = models.PositiveIntegerField(
        help_text="ID of the media object"
    )
    media_object = GenericForeignKey('media_content_type', 'media_object_id')
    
    # What content is using this media
    entity_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='media_usages',
        help_text="Content type using the media (BlogPost, ServicePage, CTABlock, etc.)"
    )
    entity_object_id = models.PositiveIntegerField(
        help_text="ID of the content using the media"
    )
    entity_object = GenericForeignKey('entity_content_type', 'entity_object_id')
    
    # Context of usage
    context = models.CharField(
        max_length=100,
        help_text="How the media is used (e.g., 'featured_image', 'inline', 'cta', 'og_image')"
    )
    
    # Metadata
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='media_usages',
        help_text="Website this usage belongs to"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['media_content_type', 'media_object_id']),
            models.Index(fields=['entity_content_type', 'entity_object_id']),
            models.Index(fields=['website', 'context']),
        ]
        unique_together = [
            ['media_content_type', 'media_object_id', 'entity_content_type', 'entity_object_id', 'context']
        ]
        verbose_name = "Media Usage"
        verbose_name_plural = "Media Usages"
    
    def __str__(self) -> str:
        return f"{self.media_object} used in {self.entity_content_type.model} #{self.entity_object_id} ({self.context})"
    
    @classmethod
    def track_usage(cls, media_object, entity_object, context: str, website=None):
        """
        Track usage of a media file by a content entity.
        
        Args:
            media_object: MediaAsset, BlogMediaFile, or any media model instance
            entity_object: BlogPost, ServicePage, CTABlock, or any content model instance
            context: Usage context (e.g., 'featured_image', 'inline', 'cta')
            website: Website instance (auto-detected if not provided)
        """
        from django.contrib.contenttypes.models import ContentType
        
        media_ct = ContentType.objects.get_for_model(media_object)
        entity_ct = ContentType.objects.get_for_model(entity_object)
        
        if not website:
            # Try to get website from entity or media
            if hasattr(entity_object, 'website'):
                website = entity_object.website
            elif hasattr(media_object, 'website'):
                website = media_object.website
            else:
                raise ValueError("Website is required and could not be auto-detected")
        
        usage, created = cls.objects.get_or_create(
            media_content_type=media_ct,
            media_object_id=media_object.id,
            entity_content_type=entity_ct,
            entity_object_id=entity_object.id,
            context=context,
            defaults={'website': website}
        )
        
        return usage
    
    @classmethod
    def get_usages_for_media(cls, media_object):
        """Get all usages of a media file."""
        from django.contrib.contenttypes.models import ContentType
        
        media_ct = ContentType.objects.get_for_model(media_object)
        return cls.objects.filter(
            media_content_type=media_ct,
            media_object_id=media_object.id
        ).select_related('entity_content_type', 'website')
    
    @classmethod
    def remove_usage(cls, media_object, entity_object, context: str = None):
        """Remove usage tracking for a media file."""
        from django.contrib.contenttypes.models import ContentType
        
        media_ct = ContentType.objects.get_for_model(media_object)
        entity_ct = ContentType.objects.get_for_model(entity_object)
        
        filters = {
            'media_content_type': media_ct,
            'media_object_id': media_object.id,
            'entity_content_type': entity_ct,
            'entity_object_id': entity_object.id,
        }
        
        if context:
            filters['context'] = context
        
        cls.objects.filter(**filters).delete()



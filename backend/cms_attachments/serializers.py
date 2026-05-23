"""
Attachment API Serializers
============================
"""

from rest_framework import serializers

from cms_attachments.models import Attachment, AttachmentCategory


class AttachmentCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AttachmentCategory
        fields = ["id", "name", "slug"]


class AttachmentListSerializer(serializers.ModelSerializer):
    """Compact attachment for listings."""

    category = AttachmentCategorySerializer(read_only=True)
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = [
            "id", "title", "slug", "description",
            "attachment_type", "category",
            "academic_level", "subject_area", "formatting_style",
            "gate_type", "is_featured", "average_rating",
            "download_count", "file_format", "file_size_bytes",
            "download_url",
        ]

    def get_download_url(self, obj) -> str | None:
        if obj.gate_type == "free" and obj.managed_file:
            return obj.managed_file.public_url
        # Gated files: return the landing page URL instead
        return f"/resources/{obj.slug}/"


class AttachmentDetailSerializer(serializers.ModelSerializer):
    """Full attachment for detail/landing page."""

    category = AttachmentCategorySerializer(read_only=True)
    author_name = serializers.SerializerMethodField()
    related_service_title = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = [
            "id", "title", "slug", "description",
            "attachment_type", "category",
            "academic_level", "subject_area", "formatting_style",
            "word_count", "page_count",
            "gate_type", "price",
            "meta_title", "meta_description", "schema_type",
            "author_name", "author_credentials",
            "related_service_title",
            "is_verified", "is_featured",
            "average_rating", "rating_count",
            "download_count",
            "version", "file_format", "file_size_bytes",
        ]

    def get_author_name(self, obj) -> str | None:
        return obj.author.name if obj.author else None

    def get_related_service_title(self, obj) -> str | None:
        return obj.related_service.title if obj.related_service else None


class AttachmentSchemaOrgSerializer(serializers.Serializer):
    """Schema.org DigitalDocument / LearningResource JSON-LD."""

    def to_representation(self, attachment: Attachment) -> dict:
        schema = {
            "@context": "https://schema.org",
            "@type": attachment.schema_type or "DigitalDocument",
            "name": attachment.title,
            "description": attachment.description,
            "fileFormat": attachment.file_format,
        }

        if attachment.gate_type == "free":
            schema["isAccessibleForFree"] = True
        else:
            schema["isAccessibleForFree"] = False

        if attachment.author:
            schema["author"] = {
                "@type": "Person",
                "name": attachment.author.name,
            }

        if attachment.published_at:
            schema["dateCreated"] = attachment.published_at.isoformat()

        if attachment.average_rating > 0:
            schema["aggregateRating"] = {
                "@type": "AggregateRating",
                "ratingValue": str(attachment.average_rating),
                "ratingCount": attachment.rating_count,
            }

        return schema
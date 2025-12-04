from rest_framework import serializers

from .models import MediaAsset, MediaUsage


class MediaAssetSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = MediaAsset
        fields = [
            "id",
            "website",
            "type",
            "file",
            "embed_provider",
            "embed_id",
            "title",
            "alt_text",
            "caption",
            "tags",
            "mime_type",
            "size_bytes",
            "width",
            "height",
            "uploaded_by",
            "is_active",
            "created_at",
            "updated_at",
            "url",
        ]
        read_only_fields = [
            "uploaded_by",
            "mime_type",
            "size_bytes",
            "width",
            "height",
            "created_at",
            "updated_at",
            "url",
        ]

    def get_url(self, obj):
        if obj.file:
            return obj.file.url
        if obj.embed_provider and obj.embed_id:
            return obj.embed_id
        return None

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data.setdefault("uploaded_by", request.user)

        file = validated_data.get("file")
        if file:
            validated_data["mime_type"] = getattr(file, "content_type", "") or ""
            validated_data["size_bytes"] = file.size

        return super().create(validated_data)


class MediaUsageSerializer(serializers.ModelSerializer):
    """Serializer for media usage tracking."""
    media_object_repr = serializers.SerializerMethodField()
    entity_object_repr = serializers.SerializerMethodField()
    
    class Meta:
        model = MediaUsage
        fields = [
            'id', 'media_content_type', 'media_object_id', 'media_object_repr',
            'entity_content_type', 'entity_object_id', 'entity_object_repr',
            'context', 'website', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_media_object_repr(self, obj):
        """Get string representation of media object."""
        try:
            return str(obj.media_object)
        except Exception:
            return f"{obj.media_content_type.model} #{obj.media_object_id}"
    
    def get_entity_object_repr(self, obj):
        """Get string representation of entity using the media."""
        try:
            return str(obj.entity_object)
        except Exception:
            return f"{obj.entity_content_type.model} #{obj.entity_object_id}"



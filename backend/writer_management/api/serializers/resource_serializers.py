"""
writer_management/api/serializers/resource_serializer.py

Serializers for WriterResource, WriterResourceCategory, WriterResourceView.

SERIALIZERS
-----------
WriterResourceCategorySerializer
    Compact category for list displays and filter options.

WriterResourceSerializer
    Full resource for writer-facing list and detail views.
    Includes category name inline. No nested objects.

WriterResourceAdminSerializer
    Admin view. Adds internal fields: view_count, download_count,
    created_by, updated_by, is_active, is_featured, display_order.
    Used in admin API only.

WriterResourceViewSerializer
    Read-only record of a writer's view history.

CreateWriterResourceSerializer
    Admin: create a new resource.
    Validates that file OR external_url is provided for non-article types.
    Article type requires content field.

UpdateWriterResourceSerializer
    Admin: partial update. Same validation as create.
"""

from rest_framework import serializers

from writer_management.models.resources import (
    WriterResourceCategory,
    WriterResource,
    WriterResourceView,
)


class WriterResourceCategorySerializer(serializers.ModelSerializer):
    """
    Compact category for filter dropdowns and resource list headers.
    """

    class Meta:
        model = WriterResourceCategory
        fields = [
            "id",
            "name",
            "description",
            "display_order",
            "is_active",
        ]
        read_only_fields = fields


class WriterResourceSerializer(serializers.ModelSerializer):
    """
    Resource detail for writer-facing views.

    Includes category name inline to avoid a second request.
    Omits internal admin fields (view_count, created_by, etc.).
    """

    category_name = serializers.SerializerMethodField()
    resource_type_display = serializers.CharField(
        source="get_resource_type_display",
        read_only=True,
    )
    has_file = serializers.SerializerMethodField()
    has_external_url = serializers.SerializerMethodField()

    class Meta:
        model = WriterResource
        fields = [
            "id",
            "title",
            "description",
            "resource_type",
            "resource_type_display",
            "category",
            "category_name",
            "file",
            "external_url",
            "video_url",
            "content",
            "is_featured",
            "display_order",
            "has_file",
            "has_external_url",
            "created_at",
        ]
        read_only_fields = fields

    def get_category_name(self, obj) -> str | None:
        category = obj.category
        return category.name if category is not None else None

    def get_has_file(self, obj) -> bool:
        return bool(obj.file)

    def get_has_external_url(self, obj) -> bool:
        return bool(obj.external_url)


class WriterResourceAdminSerializer(serializers.ModelSerializer):
    """
    Resource detail for admin views.

    Adds internal tracking fields not shown to writers.
    """

    category_name = serializers.SerializerMethodField()
    resource_type_display = serializers.CharField(
        source="get_resource_type_display",
        read_only=True,
    )
    created_by_name = serializers.SerializerMethodField()
    updated_by_name = serializers.SerializerMethodField()

    class Meta:
        model = WriterResource
        fields = [
            "id",
            "title",
            "description",
            "resource_type",
            "resource_type_display",
            "category",
            "category_name",
            "file",
            "external_url",
            "video_url",
            "content",
            "is_featured",
            "is_active",
            "display_order",
            "view_count",
            "download_count",
            "created_by",
            "created_by_name",
            "updated_by",
            "updated_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "resource_type_display",
            "category_name",
            "created_by_name",
            "updated_by_name",
            "view_count",
            "download_count",
            "created_at",
            "updated_at",
        ]

    def get_category_name(self, obj) -> str | None:
        category = obj.category
        return category.name if category is not None else None

    def get_created_by_name(self, obj) -> str | None:
        user = obj.created_by
        if user is None:
            return None
        return user.get_full_name() or user.email

    def get_updated_by_name(self, obj) -> str | None:
        user = obj.updated_by
        if user is None:
            return None
        return user.get_full_name() or user.email


class WriterResourceViewSerializer(serializers.ModelSerializer):
    """
    Read-only record of a writer's resource view history.

    Used in admin analytics and writer's "recently viewed" endpoint.
    """

    resource_title = serializers.SerializerMethodField()
    resource_type = serializers.SerializerMethodField()

    class Meta:
        model = WriterResourceView
        fields = [
            "id",
            "resource",
            "resource_title",
            "resource_type",
            "view_count",
            "viewed_at",
        ]
        read_only_fields = fields

    def get_resource_title(self, obj) -> str:
        return obj.resource.title

    def get_resource_type(self, obj) -> str:
        return obj.resource.resource_type


class CreateWriterResourceSerializer(serializers.Serializer):
    """
    Admin input for creating a new resource.

    VALIDATION RULES
    ----------------
    document type : file required
    link type     : external_url required
    video type    : video_url required
    article type  : content required
    tool type     : external_url or file required

    All types: title required.
    """

    title = serializers.CharField(max_length=255)
    description = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    resource_type = serializers.ChoiceField(
        choices=WriterResource.ResourceType.choices
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=WriterResourceCategory.objects.all(),
        required=False,
        allow_null=True,
    )
    file_url = serializers.URLField(required=False, allow_null=True)
    external_url = serializers.URLField(
        required=False, allow_blank=True, default=""
    )
    video_url = serializers.URLField(
        required=False, allow_blank=True, default=""
    )
    content = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    is_featured = serializers.BooleanField(default=False)
    is_active = serializers.BooleanField(default=True)
    display_order = serializers.IntegerField(default=0, min_value=0)

def validate(self, attrs: dict) -> dict:
    resource_type = attrs.get("resource_type")

    if resource_type == WriterResource.ResourceType.DOCUMENT:
        if not attrs.get("file"):
            raise serializers.ValidationError(
                {"file": "A file is required for document resources."}
            )

    elif resource_type == WriterResource.ResourceType.LINK:
        if not attrs.get("external_url"):
            raise serializers.ValidationError(
                {"external_url": "An external URL is required for link resources."}
            )

    elif resource_type == WriterResource.ResourceType.VIDEO:
        if not attrs.get("video_url"):
            raise serializers.ValidationError(
                {"video_url": "A video URL is required for video resources."}
            )

    elif resource_type == WriterResource.ResourceType.ARTICLE:
        if not attrs.get("content", "").strip():
            raise serializers.ValidationError(
                {"content": "Content is required for article resources."}
            )

    elif resource_type == WriterResource.ResourceType.TOOL:
        if not attrs.get("external_url") and not attrs.get("file"):
            raise serializers.ValidationError(
                {"external_url": "A URL or file is required for tool resources."}
            )

    return attrs


class UpdateWriterResourceSerializer(serializers.Serializer):
    """
    Admin input for partial update of an existing resource.

    All fields optional — only provided fields are updated.
    When resource_type changes, re-validates the content requirements
    against the new type combined with any existing data.
    """

    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(
        required=False, allow_blank=True
    )
    resource_type = serializers.ChoiceField(
        choices=WriterResource.ResourceType.choices,
        required=False,
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=WriterResourceCategory.objects.all(),
        required=False,
        allow_null=True,
    )
    file = serializers.FileField(required=False, allow_null=True)
    external_url = serializers.URLField(
        required=False, allow_blank=True
    )
    video_url = serializers.URLField(
        required=False, allow_blank=True
    )
    content = serializers.CharField(
        required=False, allow_blank=True
    )
    is_featured = serializers.BooleanField(required=False)
    is_active = serializers.BooleanField(required=False)
    display_order = serializers.IntegerField(
        required=False, min_value=0
    )


class WriterResourceCategoryCreateSerializer(serializers.Serializer):
    """Admin input for creating a resource category."""

    name = serializers.CharField(max_length=100)
    description = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    display_order = serializers.IntegerField(default=0, min_value=0)
    is_active = serializers.BooleanField(default=True)

    def validate_name(self, value: str) -> str:
        return value.strip()
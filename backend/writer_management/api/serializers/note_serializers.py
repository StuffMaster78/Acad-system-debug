from rest_framework import serializers
from writer_management.models.writer_note import WriterNote


class WriterNoteSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = WriterNote
        fields = [
            "id",
            "writer",
            "note",
            "is_pinned",
            "is_sensitive",
            "related_order_id",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id", "writer", "created_by",
            "created_by_name", "created_at", "updated_at",
        ]

    def get_created_by_name(self, obj) -> str:
        user = obj.created_by
        if user is None:
            return "System"
        return user.get_full_name() or user.email


class CreateWriterNoteSerializer(serializers.Serializer):
    note = serializers.CharField(min_length=5)
    is_pinned = serializers.BooleanField(default=False)
    is_sensitive = serializers.BooleanField(default=False)
    related_order_id = serializers.IntegerField(required=False)


class UpdateWriterNoteSerializer(serializers.Serializer):
    note = serializers.CharField(min_length=5, required=False)
    is_pinned = serializers.BooleanField(required=False)
    is_sensitive = serializers.BooleanField(required=False)
from rest_framework import serializers

from .models import QAChecklistItem, QAChecklistResult, QAChecklistTemplate


class QAItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = QAChecklistItem
        fields = ["id", "category", "text", "is_required", "display_order"]


class QATemplateSerializer(serializers.ModelSerializer):
    items = QAItemSerializer(many=True, read_only=True)

    class Meta:
        model = QAChecklistTemplate
        fields = ["id", "name", "description", "is_default", "items"]


class QAResultSerializer(serializers.ModelSerializer):
    template_name = serializers.CharField(source="template.name", read_only=True)
    reviewer_name = serializers.SerializerMethodField()
    pass_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = QAChecklistResult
        fields = [
            "id", "order", "template", "template_name",
            "reviewer", "reviewer_name",
            "checked_items", "verdict", "notes", "pass_rate",
            "completed_at", "created_at",
        ]
        read_only_fields = ["id", "reviewer", "created_at", "completed_at"]

    def get_reviewer_name(self, obj) -> str:
        return obj.reviewer.get_full_name() or obj.reviewer.username

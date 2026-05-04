from __future__ import annotations

from rest_framework import serializers

from class_management.models import ClassTimelineEvent


class ClassTimelineEventSerializer(serializers.ModelSerializer):
    triggered_by_name = serializers.CharField(
        source="triggered_by.get_full_name",
        read_only=True,
    )

    class Meta:
        model = ClassTimelineEvent
        fields = "__all__"
from rest_framework import serializers


class CreateProgressivePlanSerializer(serializers.Serializer):
    milestones = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=False,
    )
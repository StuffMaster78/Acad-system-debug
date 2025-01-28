from rest_framework import serializers
from .models import (
    EditorProfile,
    EditorTaskAssignment,
    EditorPerformance,
    EditorNotification,
)

class EditorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditorProfile
        fields = "__all__"


class EditorTaskAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditorTaskAssignment
        fields = "__all__"


class EditorPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditorPerformance
        fields = "__all__"


class EditorNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EditorNotification
        fields = "__all__"
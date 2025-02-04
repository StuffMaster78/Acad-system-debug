from rest_framework import serializers
from .models import ActivityLog

class ActivityLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Shows the username instead of user ID
    timestamp = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")  # Format timestamp

    class Meta:
        model = ActivityLog
        fields = ["id", "user", "action_type", "description", "timestamp", "metadata"]
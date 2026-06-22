from rest_framework import serializers

from .models import SavedView


class SavedViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedView
        fields = ["id", "view_type", "name", "filters", "is_default", "created_at"]
        read_only_fields = ["id", "created_at"]

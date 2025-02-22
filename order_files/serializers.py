from rest_framework import serializers
from .models import (
    OrderFile, FileDeletionRequest, ExternalFileLink, ExtraServiceFile, OrderFilesConfig
)

class OrderFileSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()

    class Meta:
        model = OrderFile
        fields = "__all__"

class FileDeletionRequestSerializer(serializers.ModelSerializer):
    requested_by = serializers.StringRelatedField()

    class Meta:
        model = FileDeletionRequest
        fields = "__all__"

class ExternalFileLinkSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()

    class Meta:
        model = ExternalFileLink
        fields = "__all__"

class ExtraServiceFileSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField()

    class Meta:
        model = ExtraServiceFile
        fields = "__all__"

class OrderFilesConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderFilesConfig
        fields = "__all__"
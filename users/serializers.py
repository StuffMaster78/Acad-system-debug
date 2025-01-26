from rest_framework import serializers
from .models import User


class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'avatar', 'phone_number', 'role']


class WriterProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'bio', 'writer_level', 'rating',
            'completed_orders', 'verification_documents', 'role'
        ]


class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number', 'role']


class EditorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'bio', 'edited_orders', 'role']
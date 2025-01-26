from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'profile_picture',
            'bio', 'phone', 'verification_documents', 'rating', 'company_name',
        ]
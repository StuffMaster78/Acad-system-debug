from rest_framework import serializers
from .models import Website

class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = [
            'id', 'name', 'domain', 'is_active', 'logo', 'theme_color', 
            'contact_email', 'contact_phone', 'meta_title', 'meta_description',
            'allow_registration', 'allow_guest_checkout'
        ]
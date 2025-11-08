"""
Comprehensive user serializers for admin management.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for list views."""
    full_name = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    website = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'is_active', 'is_suspended', 'is_blacklisted',
            'is_on_probation', 'date_joined', 'last_login', 'website',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_website(self, obj):
        """Get website information"""
        if obj.website:
            return {
                'id': obj.website.id,
                'name': obj.website.name,
                'domain': obj.website.domain,
            }
        return None


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer with all fields."""
    full_name = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    website_name = serializers.CharField(source='website.name', read_only=True)
    
    # Profile information
    writer_profile = serializers.SerializerMethodField()
    client_profile = serializers.SerializerMethodField()
    editor_profile = serializers.SerializerMethodField()
    support_profile = serializers.SerializerMethodField()
    admin_profile = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'phone_number',
            'is_active', 'is_staff', 'is_superuser',
            'is_suspended', 'suspension_reason', 'suspension_start_date', 'suspension_end_date',
            'is_blacklisted', 'blacklisted_at',
            'is_on_probation', 'probation_reason', 'probation_start_date', 'probation_end_date',
            'date_joined', 'last_login', 'website', 'website_name',
            'writer_profile', 'client_profile', 'editor_profile', 'support_profile', 'admin_profile',
        ]
        read_only_fields = [
            'id', 'date_joined', 'last_login', 'is_superuser',
            'writer_profile', 'client_profile', 'editor_profile', 'support_profile', 'admin_profile',
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username
    
    def get_role_display(self, obj):
        """Get human-readable role name."""
        role = obj.role or ''
        role_map = {
            'client': 'Client',
            'writer': 'Writer',
            'editor': 'Editor',
            'support': 'Support',
            'admin': 'Admin',
            'superadmin': 'Superadmin',
        }
        return role_map.get(role, role.title())
    
    def get_writer_profile(self, obj):
        if hasattr(obj, 'writer_profile'):
            return {
                'id': obj.writer_profile.id,
                'level': getattr(obj.writer_profile, 'level', None),
                'specialization': getattr(obj.writer_profile, 'specialization', None),
            }
        return None
    
    def get_client_profile(self, obj):
        if hasattr(obj, 'client_profile'):
            return {
                'id': obj.client_profile.id,
                'registration_id': getattr(obj.client_profile, 'registration_id', None),
            }
        return None
    
    def get_editor_profile(self, obj):
        if hasattr(obj, 'editor_profile'):
            return {'id': obj.editor_profile.id}
        return None
    
    def get_support_profile(self, obj):
        if hasattr(obj, 'support_profile'):
            return {'id': obj.support_profile.id}
        return None
    
    def get_admin_profile(self, obj):
        if hasattr(obj, 'admin_profile'):
            return {
                'id': obj.admin_profile.id,
                'is_superadmin': obj.admin_profile.is_superadmin,
            }
        return None


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    role = serializers.ChoiceField(choices=['client', 'writer', 'editor', 'support', 'admin'], required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name',
            'role', 'phone_number', 'website',
        ]
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'password': {'required': True},
            'role': {'required': True},
        }
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information."""
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone_number', 'is_active', 'website',
        ]
        read_only_fields = ['id']
    
    def validate_email(self, value):
        # Allow updating to same email
        user = self.instance
        if User.objects.filter(email=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_username(self, value):
        # Allow updating to same username
        user = self.instance
        if User.objects.filter(username=value).exclude(id=user.id).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value


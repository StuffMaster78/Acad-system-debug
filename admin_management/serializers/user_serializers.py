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
    phone_number = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'phone_number', 'is_active', 'is_suspended', 'is_blacklisted',
            'is_on_probation', 'date_joined', 'last_login', 'website',
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'phone_number']
    
    def get_website(self, obj):
        """Get website information"""
        try:
            # Access website directly - select_related ensures it's loaded
            website = getattr(obj, 'website', None)
            if website:
                return {
                    'id': website.id,
                    'name': website.name,
                    'domain': website.domain,
                }
        except Exception:
            pass
        return None
    
    def get_full_name(self, obj):
        try:
            return obj.get_full_name() or obj.username or ''
        except Exception:
            return obj.username or ''
    
    def get_phone_number(self, obj):
        """Get phone number from user profile."""
        try:
            profile = getattr(obj, 'user_main_profile', None)
            if profile and hasattr(profile, 'phone_number'):
                return str(profile.phone_number) if profile.phone_number else None
        except Exception:
            pass
        return None
    
    def get_role_display(self, obj):
        """Get human-readable role name."""
        try:
            role = getattr(obj, 'role', None) or ''
            role_map = {
                'client': 'Client',
                'writer': 'Writer',
                'editor': 'Editor',
                'support': 'Support',
                'admin': 'Admin',
                'superadmin': 'Superadmin',
            }
            return role_map.get(role, role.title() if role else 'N/A')
        except Exception:
            return 'N/A'
    
    def to_representation(self, instance):
        """Override to ensure all fields are properly serialized."""
        data = super().to_representation(instance)
        # Ensure role is always present and accurate
        if 'role' not in data or data['role'] is None:
            data['role'] = getattr(instance, 'role', None) or ''
        # Ensure role_display is always present
        if 'role_display' not in data or not data['role_display']:
            data['role_display'] = self.get_role_display(instance)
        # Ensure phone_number is present
        if 'phone_number' not in data:
            data['phone_number'] = self.get_phone_number(instance)
        # Ensure website is properly formatted (select_related should have loaded it)
        if 'website' not in data or data['website'] is None:
            data['website'] = self.get_website(instance)
        # Ensure status fields are booleans
        if 'is_active' not in data:
            data['is_active'] = getattr(instance, 'is_active', True)
        if 'is_suspended' not in data:
            data['is_suspended'] = getattr(instance, 'is_suspended', False)
        if 'is_blacklisted' not in data:
            data['is_blacklisted'] = getattr(instance, 'is_blacklisted', False)
        if 'is_on_probation' not in data:
            data['is_on_probation'] = getattr(instance, 'is_on_probation', False)
        # Ensure dates are properly formatted
        if 'date_joined' not in data or data['date_joined'] is None:
            date_joined = getattr(instance, 'date_joined', None)
            if date_joined:
                data['date_joined'] = date_joined.isoformat() if hasattr(date_joined, 'isoformat') else str(date_joined)
        if 'last_login' not in data or data['last_login'] is None:
            last_login = getattr(instance, 'last_login', None)
            if last_login:
                data['last_login'] = last_login.isoformat() if hasattr(last_login, 'isoformat') else str(last_login)
        return data


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer with all fields."""
    full_name = serializers.SerializerMethodField()
    role_display = serializers.SerializerMethodField()
    website_name = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    
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
            'is_blacklisted',
            'is_on_probation', 'probation_reason', 'probation_start_date', 'probation_end_date',
            'date_joined', 'last_login', 'website', 'website_name',
            'writer_profile', 'client_profile', 'editor_profile', 'support_profile', 'admin_profile',
        ]
        read_only_fields = [
            'id', 'date_joined', 'last_login', 'is_superuser',
            'writer_profile', 'client_profile', 'editor_profile', 'support_profile', 'admin_profile',
            'phone_number',
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
    
    def get_website_name(self, obj):
        """Get website name safely."""
        if obj.website:
            return obj.website.name
        return None
    
    def get_phone_number(self, obj):
        """Get phone number from user profile."""
        try:
            profile = getattr(obj, 'user_main_profile', None)
            if profile and hasattr(profile, 'phone_number'):
                return str(profile.phone_number) if profile.phone_number else None
        except Exception:
            pass
        return None
    
    def get_writer_profile(self, obj):
        try:
            if hasattr(obj, 'writer_profile') and obj.writer_profile:
                return {
                    'id': obj.writer_profile.id,
                    'level': getattr(obj.writer_profile, 'level', None),
                    'specialization': getattr(obj.writer_profile, 'specialization', None),
                }
        except Exception:
            pass
        return None
    
    def get_client_profile(self, obj):
        try:
            if hasattr(obj, 'client_profile') and obj.client_profile:
                return {
                    'id': obj.client_profile.id,
                    'registration_id': getattr(obj.client_profile, 'registration_id', None),
                }
        except Exception:
            pass
        return None
    
    def get_editor_profile(self, obj):
        try:
            if hasattr(obj, 'editor_profile') and obj.editor_profile:
                return {'id': obj.editor_profile.id}
        except Exception:
            pass
        return None
    
    def get_support_profile(self, obj):
        try:
            if hasattr(obj, 'support_profile') and obj.support_profile:
                return {'id': obj.support_profile.id}
        except Exception:
            pass
        return None
    
    def get_admin_profile(self, obj):
        try:
            if hasattr(obj, 'admin_profile') and obj.admin_profile:
                return {
                    'id': obj.admin_profile.id,
                    'is_superadmin': getattr(obj.admin_profile, 'is_superadmin', False),
                }
        except Exception:
            pass
        return None


class CreateUserSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    role = serializers.ChoiceField(choices=['client', 'writer', 'editor', 'support', 'admin'], required=True)
    phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
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
        phone_number = validated_data.pop('phone_number', None)
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create or update user profile with phone number
        if phone_number:
            from users.models import UserProfile
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={'phone_number': phone_number}
            )
            if not profile.phone_number:
                profile.phone_number = phone_number
                profile.save()
        
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information."""
    phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
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
    
    def update(self, instance, validated_data):
        phone_number = validated_data.pop('phone_number', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update phone number in profile
        if phone_number is not None:
            from users.models import UserProfile
            profile, _ = UserProfile.objects.get_or_create(
                user=instance,
                defaults={'phone_number': phone_number}
            )
            profile.phone_number = phone_number if phone_number else None
            profile.save()
        
        return instance


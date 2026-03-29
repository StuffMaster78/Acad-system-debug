from rest_framework import serializers
from django.utils.timezone import now  

from orders.models.orders import Order

from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from orders.registry.decorator import get_all_registered_actions
from django.utils import timezone
from orders.services.revisions import OrderRevisionService


User = get_user_model()

class OrderListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for order list views.
    Excludes large fields like order_instructions and style_reference_files.
    Optimized for fast list rendering in admin dashboard.
    """
    client_username = serializers.CharField(source='client.username', read_only=True, allow_null=True)
    writer_username = serializers.CharField(source='assigned_writer.username', read_only=True, allow_null=True)
    paper_type_name = serializers.CharField(source='paper_type.name', read_only=True, allow_null=True)
    academic_level_name = serializers.CharField(source='academic_level.name', read_only=True, allow_null=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'topic', 'paper_type', 'paper_type_name', 'academic_level', 'academic_level_name',
            'formatting_style', 'type_of_work', 'english_type', 'number_of_pages', 
            'number_of_slides', 'number_of_refereces', 'spacing', 'client_deadline', 'writer_deadline', 
            'client', 'client_username', 'assigned_writer', 'writer_username', 
            'preferred_writer', 'total_price', 'writer_compensation', 
            'subject', 'subject_name', 'discount_code_used', 'is_paid', 
            'status', 'flags', 'created_at', 'updated_at', 
            'is_special_order', 'is_follow_up', 'is_urgent', 'website'
        ]
        read_only_fields = [
            'id', 'client_username', 'writer_username', 'total_price', 
            'writer_compensation', 'is_paid', 'created_at', 'updated_at', 
            'flags', 'writer_deadline'
        ]


class OrderSerializer(serializers.ModelSerializer):
    client_username = serializers.CharField(source='client.username', read_only=True)
    writer_username = serializers.CharField(source='assigned_writer.username', read_only=True)
    is_unattributed = serializers.SerializerMethodField(read_only=True)
    # Fake client ID for writers viewing unattributed orders
    fake_client_id = serializers.SerializerMethodField(read_only=True)
    # Expose external contact fields and unpaid override to admins only (gate in to_representation)
    external_contact_name = serializers.CharField(read_only=True)
    external_contact_email = serializers.EmailField(read_only=True)
    external_contact_phone = serializers.CharField(read_only=True)
    allow_unpaid_access = serializers.BooleanField(read_only=True)
    # Client information (role-based visibility in to_representation)
    client_email = serializers.SerializerMethodField(read_only=True)
    client_registration_id = serializers.SerializerMethodField(read_only=True)
    # Subject specialty information
    subject_is_technical = serializers.SerializerMethodField(read_only=True)
    # Writer deadline percentage config
    writer_deadline_percentage = serializers.SerializerMethodField(read_only=True)
    # Revision eligibility info for clients
    revision_eligibility = serializers.SerializerMethodField(read_only=True)
    # Style reference files uploaded by client
    style_reference_files = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'topic', 'order_instructions', 'paper_type', 'academic_level', 
            'formatting_style', 'type_of_work', 'english_type', 'number_of_pages', 
            'number_of_slides', 'number_of_refereces', 'spacing', 'client_deadline', 'writer_deadline', 
            'client', 'client_username', 'client_email', 'client_registration_id', 'assigned_writer', 'writer_username', 
            'preferred_writer', 'total_price', 'writer_compensation', 
            'extra_services', 'subject', 'subject_is_technical', 'discount_code_used', 'is_paid', 
            'status', 'flags', 'created_at', 'updated_at', 
            'created_by_admin', 'is_special_order', 'is_follow_up',
            'previous_order', 'requires_editing', 'editing_skip_reason', 'is_urgent',
            'is_unattributed', 'fake_client_id', 'external_contact_name', 'external_contact_email', 'external_contact_phone',
            'allow_unpaid_access', 'writer_deadline_percentage', 'revision_eligibility', 'style_reference_files'
        ]
        read_only_fields = [
            'id', 'client_username', 'writer_username', 'total_price', 
            'writer_compensation', 'is_paid', 'created_at', 'updated_at', 
            'flags', 'writer_deadline', 'editing_skip_reason'
        ]

    def validate_academic_level(self, value):
        """
        Make sure the academic level belongs to the current website.
        """
        request = self.context['request']
        if value.website != request.website:
            raise serializers.ValidationError("Invalid academic level for this website.")
        return value

    def get_is_unattributed(self, obj):
        return obj.client_id is None and (
            bool(getattr(obj, 'external_contact_name', None)) or
            bool(getattr(obj, 'external_contact_email', None))
        )
    
    def get_fake_client_id(self, obj):
        """
        Returns a fake client ID for writers viewing unattributed orders.
        This ensures writers see a client ID even when the order is unattributed.
        """
        is_unattributed = obj.client_id is None and (
            bool(getattr(obj, 'external_contact_name', None)) or
            bool(getattr(obj, 'external_contact_email', None))
        )
        
        if is_unattributed:
            # Generate a consistent fake ID based on order ID
            # This ensures the same fake ID is shown for the same order
            return f"EXT-{obj.id:06d}"
        return None
    
    def get_client_email(self, obj):
        """Get client email (admin/superadmin only, filtered in to_representation)"""
        if obj.client:
            return obj.client.email
        return None
    
    def get_client_registration_id(self, obj):
        """Get client registration ID"""
        if obj.client and hasattr(obj.client, 'client_profile'):
            return obj.client.client_profile.registration_id
        return None
    
    def get_subject_is_technical(self, obj):
        """Get whether subject is technical"""
        if obj.subject:
            return getattr(obj.subject, 'is_technical', False)
        return None
    
    def get_writer_deadline_percentage(self, obj):
        """Get writer deadline percentage config"""
        if obj.writer_deadline_percentage:
            config = obj.writer_deadline_percentage
            label = getattr(config, 'label', None)
            return {
                'id': config.id,
                'writer_deadline_percentage': config.writer_deadline_percentage,
                'label': label or f"{config.writer_deadline_percentage}%"
            }
        return None

    def get_revision_eligibility(self, obj):
        """
        Expose whether the order is still within the free revision window.
        Used by client dashboards to show 'Unlimited Revisions' vs
        'Past free revision period'.
        """
        # Only meaningful for completed orders
        status = (obj.status or '').lower()
        # Use submitted_at (writer finished) as primary completion timestamp,
        # falling back to updated_at if needed.
        completed_ts = getattr(obj, "submitted_at", None) or getattr(obj, "updated_at", None)
        if status != 'completed' or not completed_ts:
            return {
                "is_within_free_window": False,
                "free_revision_until": None,
                "days_left": 0,
            }

        try:
            service = OrderRevisionService(order=obj, user=obj.client)
            deadline = service.get_revision_deadline()
        except Exception:
            return {
                "is_within_free_window": False,
                "free_revision_until": None,
                "days_left": 0,
            }

        free_until = completed_ts + deadline
        now_ts = timezone.now()
        if now_ts >= free_until:
            return {
                "is_within_free_window": False,
                "free_revision_until": free_until.isoformat(),
                "days_left": 0,
            }

        delta = free_until - now_ts
        days_left = max(0, delta.days)
        return {
            "is_within_free_window": True,
            "free_revision_until": free_until.isoformat(),
            "days_left": days_left,
        }
    
    def get_style_reference_files(self, obj):
        """Get style reference files for this order."""
        try:
            from order_files.models import StyleReferenceFile
            from order_files.serializers import StyleReferenceFileSerializer
            
            # Get style reference files visible to the current user
            user = self.context.get('request').user if self.context.get('request') else None
            style_refs = StyleReferenceFile.objects.filter(order=obj)
            
            # Filter based on user permissions
            if user:
                # Filter to only show files the user can access
                style_refs = [ref for ref in style_refs if ref.can_access(user)]
            else:
                # If no user, return empty list
                style_refs = []
            
            # Serialize the files
            serializer = StyleReferenceFileSerializer(
                style_refs,
                many=True,
                context=self.context
            )
            return serializer.data
        except Exception:
            # If there's any error (e.g., model not migrated yet), return empty list
            return []

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Hide external contact details from non-admin roles
        request = self.context.get('request')
        role = getattr(getattr(request, 'user', None), 'role', None)
        user = getattr(request, 'user', None)
        
        is_unattributed = instance.client_id is None and (
            bool(getattr(instance, 'external_contact_name', None)) or
            bool(getattr(instance, 'external_contact_email', None))
        )
        
        # Role-based field visibility
        if role not in ['admin', 'superadmin', 'support']:
            data.pop('external_contact_name', None)
            data.pop('external_contact_email', None)
            data.pop('external_contact_phone', None)
            # Hide client email and registration_id from non-admin roles
            data.pop('client_email', None)
            # Keep client_registration_id visible to writers (they need client ID)
            if role != 'writer':
                data.pop('client_registration_id', None)
            # keep allow_unpaid_access visible only if owner/admin
            if role not in ['admin', 'superadmin'] and user != instance.client:
                data.pop('allow_unpaid_access', None)
        
        # For writers viewing unattributed orders, show fake client ID instead of null
        if role == 'writer' and is_unattributed and not data.get('client'):
            # Keep fake_client_id visible to writers
            # Optionally, set client_username to the fake ID for display
            if data.get('fake_client_id'):
                data['client_username'] = data['fake_client_id']
                # Also set client_registration_id to fake_client_id for consistency
                data['client_registration_id'] = data['fake_client_id']
        elif role not in ['admin', 'superadmin', 'support']:
            # Hide fake_client_id from non-admin roles (except writers who need it)
            if role != 'writer':
                data.pop('fake_client_id', None)
        
        return data
    
    def perform_create(self, serializer):
        is_follow_up = self.request.data.get('is_follow_up', False)
        previous_order_id = self.request.data.get('previous_order')

        if is_follow_up and not previous_order_id:
            raise serializers.ValidationError("Follow-up orders must reference a previous order.")

        previous_order = None
        if previous_order_id:
            previous_order = Order.objects.get(id=previous_order_id)
            if previous_order.client != self.request.user:
                raise PermissionDenied("You can only follow up on your own orders.")

        serializer.save(client=self.request.user, previous_order=previous_order)


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'topic', 'order_instructions', 'paper_type', 'academic_level', 
            'formatting_style', 'type_of_work', 'english_type', 'number_of_pages', 
            'number_of_slides', 'number_of_refereces', 'spacing', 'client_deadline', 'extra_services', 
            'discount_code_used', 'client', 'preferred_writer'
        ]

    def validate_deadline(self, value):
        """Ensure the deadline is in the future."""
        if value <= now():
            raise serializers.ValidationError("The deadline must be in the future.")
        return value

    def validate_preferred_writer(self, value):
        """Ensure the preferred writer is available."""
        if value and not value.is_active:
            raise serializers.ValidationError("The preferred writer is not available.")
        return value
    

class OrderActionSerializer(serializers.Serializer):
    action = serializers.CharField(required=True)
    order_id = serializers.IntegerField(required=True)
    params = serializers.DictField(required=False, default=dict)
    
    # You can also add custom validation logic here if needed
    def validate_action(self, value):
        """
        Ensure the action is valid.
        """
        if not get_all_registered_actions(value):
            raise serializers.ValidationError(f"Action '{value}' is not registered.")
        return value

    def validate_order_id(self, value):
        """
        Ensure the order exists.
        """
        if not Order.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"Order with id {value} does not exist.")
        return value

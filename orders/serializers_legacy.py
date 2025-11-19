from rest_framework import serializers
from django.utils.timezone import now  
from .models import (
    Order, Dispute,
    DisputeWriterResponse,
    WriterRequest,
    OrderRequest,
    OrderTransitionLog,
    OrderPricingSnapshot,
    WriterReassignmentLog
)
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from orders.registry.decorator import get_all_registered_actions
from django.utils import timezone
from orders.models import WebhookDeliveryLog

User = get_user_model()

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
            'allow_unpaid_access', 'writer_deadline_percentage'
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

class DisputeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Dispute model.
    """
    order_id = serializers.PrimaryKeyRelatedField(
        source='order', 
        queryset=Order.objects.all(),  
        help_text='The ID of the order associated with this dispute.'
    )
    order_topic = serializers.CharField(
        source='order.topic',
        read_only=True,
        help_text='The topic of the disputed order.'
    )
    raised_by_username = serializers.CharField(
        source='raised_by.username',  
        read_only=True,
        help_text='The username of the user who raised this dispute.'
    )

    class Meta:
        model = Dispute
        fields = [
            'id',
            'order_id',
            'order_topic',
            'raised_by_username',
            'status',
            'website',
            'reason',
            'resolution_notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'order_topic', 'raised_by_username', 'created_at', 'updated_at']

    def validate_order_id(self, value):
        """Ensure the order is not already disputed."""
        if Dispute.objects.filter(order=value).exists():
            raise serializers.ValidationError("A dispute already exists for this order.")
        return value

class AssignOrderSerializer(serializers.Serializer):
    """
    Serializer for assigning an order to a writer.
    Validates the existence of the order and writer,
    and ensures the order is not already assigned.
    """
    writer_id = serializers.IntegerField()
    order_id = serializers.IntegerField()

    def validate(self, data):
        order_id = data['order_id']
        writer_id = data['writer_id']

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise serializers.ValidationError(f"Order {order_id} does not exist.")

        try:
            writer = User.objects.get(id=writer_id, role='writer', is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError(f"Writer {writer_id} does not exist or is inactive.")

        if order.assigned_writer:
            raise serializers.ValidationError(f"Order {order_id} is already assigned.")

        data['order'] = order
        data['writer'] = writer
        return data

class ReassignmentRequestSerializer(serializers.Serializer):
    """
    Serializer for creating a reassignment request.
    Includes validation for the preferred writer, if specified.
    """
    reason = serializers.CharField()
    requested_by = serializers.ChoiceField(choices=["client", "writer"])
    preferred_writer_id = serializers.IntegerField(
        required=False,
        allow_null=True
    )

    def validate_preferred_writer_id(self, value):
        """
        Validates the preferred_writer_id:
        - Must exist in the system
        - Must be an active writer
        """
        if value is None:
            return value

        try:
            user = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Preferred writer not found.")

        if user.role != "writer":
            raise serializers.ValidationError("Preferred user is not a writer.")

        if not user.is_active:
            raise serializers.ValidationError("Preferred writer account is inactive.")

        return value

class ResolveReassignmentSerializer(serializers.Serializer):
    """
    Serializer for resolving a reassignment request.
    Supports marking requests as reassigned, rejected, or cancelled,
    with optional fine and metadata.
    """
    request_id = serializers.IntegerField(required=False)
    order_id = serializers.IntegerField(required=False)
    status = serializers.ChoiceField(choices=['reassigned', 'rejected', 'cancelled'])
    fine = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, default=0.00
    )
    assigned_writer = serializers.IntegerField(
        required=False, allow_null=True
    )
    metadata = serializers.JSONField(required=False, default=dict)

    def validate(self, data):
        if not data.get('request_id') and not data.get('order_id'):
            raise serializers.ValidationError(
                "Either request_id or order_id must be provided."
            )

        writer_id = data.get('assigned_writer')
        if writer_id:
            try:
                User.objects.get(id=writer_id, role='writer', is_active=True)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    f"Writer with ID {writer_id} does not exist or is inactive."
                )

        return data
    

class PreferredWriterResponseSerializer(serializers.Serializer):
    response = serializers.ChoiceField(choices=["accepted", "declined"])
    reason = serializers.CharField(required=False, allow_blank=True)

    def validate(self, data):
        if data["response"] == "declined" and not data.get("reason"):
            raise serializers.ValidationError({
                "reason": "Declining requires a reason."
            })
        return data


class DisputeWriterResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for a writer to submit a response to a dispute.
    """
    response_text = serializers.CharField(required=True, allow_blank=False, max_length=2000)
    response_file = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = DisputeWriterResponse
        fields = ['response_text', 'response_file']

    def validate_response_text(self, value):
        """
        Custom validation for the writer's response text.
        """
        if len(value) < 10:
            raise serializers.ValidationError("The response text must be at least 10 characters long.")
        return value

    def create(self, validated_data):
        """
        Handle creating the DisputeWriterResponse and updating the dispute status.
        """
        dispute = self.context['dispute']  # Assuming the dispute is passed in the context
        writer = self.context['request'].user  # Writer responding to the dispute

        # Create the dispute writer response
        dispute_writer_response = DisputeWriterResponse.objects.create(
            dispute=dispute,
            responded_by=writer,
            **validated_data
        )

        # Mark the dispute as responded
        dispute.writer_responded = True
        dispute.save()

        return dispute_writer_response


class WriterRequestSerializer(serializers.ModelSerializer):
    request_type = serializers.ChoiceField(
        choices=WriterRequest.RequestType.choices
    )
    requested_by_writer = serializers.PrimaryKeyRelatedField(read_only=True)
    new_deadline = serializers.DateTimeField(required=False, allow_null=True)
    additional_pages = serializers.IntegerField(required=False, allow_null=True)
    additional_slides = serializers.IntegerField(required=False, allow_null=True)
    request_reason = serializers.CharField(max_length=1000)
    status_display = serializers.CharField(source="get_status_display")
    payment_pending = serializers.SerializerMethodField()

    class Meta:
        model = WriterRequest
        fields = [
            'id', 'website', 'order', 'request_type', 'requested_by_writer',
            'new_deadline', 'additional_pages', 'additional_slides',
            'request_reason', 'status', 'client_approval', 'estimated-cost',
            'final-cost', 'admin_approval', 'is_paid', 'requires_payment',
            'payment_pending', 'status_display', 'created_at', 'updated_at'
        ]
        read_only_fields = ['status', 'client_approval', 'admin_approval', 'is_paid']

    def validate(self, attrs):
        req_type = attrs.get('request_type')
        if req_type == 'deadline_extension' and not attrs.get('new_deadline'):
            raise serializers.ValidationError(
                "New deadline must be provided for deadline extension requests."
            )
        if req_type == 'page_increase' and not attrs.get('additional_pages'):
            raise serializers.ValidationError(
                "Page increase must be provided for page increase requests."
            )
        if req_type == 'slide_increase' and not attrs.get('additional_slides'):
            raise serializers.ValidationError(
                "Slide increase must be provided for slide increase requests."
            )
        return attrs

    def create(self, validated_data):
        validated_data['requested_by_writer'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Only allow system-side fields to be updated if explicitly permitted
        for field in [
            'status', 'client_approval',
            'admin_approval', 'is_paid'
        ]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance
    
    def get_payment_pending(self, obj):
        return obj.requires_payment and not obj.is_paid


class OrderRequestSerializer(serializers.ModelSerializer):
    writer_name = serializers.CharField(
        source="writer.get_full_name", read_only=True
    )
    status = serializers.CharField(
        source="status_display",
        read_only=True
    )

    class Meta:
        model = OrderRequest
        fields = [
            "id",
            "order",
            "writer",
            "writer_name",
            "message",
            "status",
            "accepted",
            "rejected",
            "created_at",
        ]
        read_only_fields = [
            "accepted",
            "rejected",
            "created_at",
            "status",
        ]

class OrderTransitionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderTransitionLog
        fields = [
            "id", "order", "old_status", "new_status", "action",
            "is_automatic", "user", "timestamp", "meta"
        ]

class OrderDetailSerializer(serializers.ModelSerializer):
    transitions = OrderTransitionLogSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [..., 'transitions']


class OrderMinimalSerializer(serializers.ModelSerializer):
    """ 
    A minimal serializer for Order, used in webhooks and events.
    This serializer includes only essential fields to reduce payload size.
    """
    class Meta:
        model = Order
        fields = ['id', 'title', 'status', 'writer_id']


class DeadlineExtensionSerializer(serializers.Serializer):
    new_deadline = serializers.DateTimeField()

    def validate_new_deadline(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Deadline must be in the future.")
        return value
    

class WebhookDeliveryLogSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = WebhookDeliveryLog
        fields = [
            "id", "user_email", "event", "url", "success", "status_code",
            "retry_count", "test_mode", "created_at", "request_payload",
            "response_body", "error_message"
        ]


class WriterRequestActionSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["approve", "reject"])
    request_id = serializers.IntegerField()

    def validate(self, attrs):
        action = attrs.get("action")
        request_id = attrs.get("request_id")

        if not WriterRequest.objects.filter(id=request_id).exists():
            raise serializers.ValidationError("Writer request does not exist.")

        if action == "approve":
            # Additional validation for approval can be added here
            pass

        return attrs
    

class OrderPricingSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPricingSnapshot
        fields = ["id", "order", "pricing_data", "calculated_at"]
        read_only_fields = ["id", "calculated_at"]


class WriterRequestPreviewSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    request_type = serializers.ChoiceField(choices=WriterRequest.RequestType.choices)
    additional_pages = serializers.IntegerField(required=False, min_value=0)
    additional_slides = serializers.IntegerField(required=False, min_value=0)

    def validate(self, data):
        request_type = data['request_type']
        if request_type == WriterRequest.RequestType.PAGES and not data.get("additional_pages"):
            raise serializers.ValidationError("additional_pages is required.")
        if request_type == WriterRequest.RequestType.SLIDES and not data.get("additional_slides"):
            raise serializers.ValidationError("additional_slides is required.")
        return data
    

class WriterReassignmentLogSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source="order.id", read_only=True)
    order_title = serializers.CharField(
        source="order.title", read_only=True
    )
    previous_writer_username = serializers.CharField(
        source="previous_writer.username", read_only=True
    )
    new_writer_username = serializers.CharField(
        source="new_writer.username", read_only=True
    )
    reassigned_by_username = serializers.CharField(
        source="reassigned_by.username", read_only=True
    )
    

    class Meta:
        model = WriterReassignmentLog
        fields = [
            "id",
            "order_id",
            "order_title",
            "previous_writer_username",
            "new_writer_username",
            "reassigned_by_username",
            "reason",
            "created_at",
        ]
    
    class OrderDeleteSerializer(serializers.Serializer):
        reason = serializers.CharField(
            max_length=255, required=False, allow_blank=True
        )

        class Meta:
            fields = ['reason']
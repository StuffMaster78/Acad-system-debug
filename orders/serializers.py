from rest_framework import serializers
from django.utils.timezone import now  
from .models import (
    Order, Dispute,
    DisputeWriterResponse,
    WriterRequest
)
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model


User = get_user_model()

class OrderSerializer(serializers.ModelSerializer):
    client_username = serializers.CharField(source='client.username', read_only=True)
    writer_username = serializers.CharField(source='writer.username', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'topic', 'instructions', 'paper_type', 'academic_level', 
            'formatting_style', 'type_of_work', 'english_type', 'pages', 
            'slides', 'resources', 'spacing', 'deadline', 'writer_deadline', 
            'client', 'client_username', 'writer', 'writer_username', 
            'preferred_writer', 'total_cost', 'writer_compensation', 
            'extra_services', 'subject', 'discount_code', 'is_paid', 
            'status', 'flag', 'created_at', 'updated_at', 
            'created_by_admin', 'is_special_order', 'is_follow_up',
            'previous_order'
        ]
        read_only_fields = [
            'id', 'client_username', 'writer_username', 'total_cost', 
            'writer_compensation', 'is_paid', 'created_at', 'updated_at', 
            'flag', 'writer_deadline'
        ]

    def validate_academic_level(self, value):
        """
        Make sure the academic level belongs to the current website.
        """
        request = self.context['request']
        if value.website != request.website:
            raise serializers.ValidationError("Invalid academic level for this website.")
        return value
    
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
            'topic', 'instructions', 'paper_type', 'academic_level', 
            'formatting_style', 'type_of_work', 'english_type', 'pages', 
            'slides', 'resources', 'spacing', 'deadline', 'extra_services', 
            'discount_code', 'client', 'preferred_writer'
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
    
    # You can also add custom validation logic here if needed
    def validate_action(self, value):
        """
        Ensure the action is valid.
        """
        valid_actions = [
            'put_on_hold', 'resume_order', 'assign_writer', 'complete_order',
            'dispute_order', 'approve_order', 'cancel_order', 'archive_order',
            'late_order', 'revision_order', 'transition_to_pending'
        ]
        if value not in valid_actions:
            raise serializers.ValidationError(f"Invalid action '{value}'.")
        return value

    def validate_order_id(self, value):
        """
        Ensure the order exists.
        """
        try:
            # Check if the order exists in the database
            from orders.models import Order
            order = Order.objects.get(id=value)
        except Order.DoesNotExist:
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
    """
    Serializer to handle writer requests such as deadline extensions or page increases.
    """
    request_type = serializers.ChoiceField(choices=WriterRequest.ORDER_REQUEST_TYPE)
    requested_by_writer = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="writer"),  # Adjusted filter for role "writer"
        required=False
    )
    new_deadline = serializers.DateTimeField(required=False, allow_null=True)
    additional_pages = serializers.IntegerField(required=False, allow_null=True)
    additional_slides = serializers.IntegerField(required=False, allow_null=True)
    request_reason = serializers.CharField(max_length=1000)
    status = serializers.ChoiceField(choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')], default='pending')
    client_approval = serializers.BooleanField(default=False)
    admin_approval = serializers.BooleanField(default=False)
    is_paid = serializers.BooleanField(default=False)

    class Meta:
        model = WriterRequest
        fields = [
            'website', 'order', 'request_type', 'requested_by_writer',
            'new_deadline', 'additional_pages', 'additional_slides',
            'request_reason', 'status', 'client_approval', 'admin_approval', 'is_paid'
        ]
    
    def validate(self, attrs):
        """
        Custom validation to ensure correct fields based on request type.
        """
        if attrs['request_type'] == 'deadline_extension' and not attrs.get('new_deadline'):
            raise serializers.ValidationError("New deadline must be provided for deadline extension requests.")
        
        if attrs['request_type'] == 'page_increase' and not attrs.get('additional_pages'):
            raise serializers.ValidationError("Page increase must be provided for page increase requests.")
        
        if attrs['request_type'] == 'slide_increase' and not attrs.get('additional_slides'):
            raise serializers.ValidationError("Slide increase must be provided for slide increase requests.")
        
        return attrs

    def create(self, validated_data):
        """
        Override the create method to add custom logic if needed.
        """
        # Create the WriterRequest instance
        writer_request = WriterRequest.objects.create(**validated_data)
        
        # You could also add custom behavior here if needed
        
        return writer_request

    def update(self, instance, validated_data):
        """
        Handle the update of the WriterRequest.
        """
        # Update the fields of the instance with the validated data
        instance.status = validated_data.get('status', instance.status)
        instance.client_approval = validated_data.get('client_approval', instance.client_approval)
        instance.admin_approval = validated_data.get('admin_approval', instance.admin_approval)
        instance.is_paid = validated_data.get('is_paid', instance.is_paid)
        
        instance.save()
        return instance
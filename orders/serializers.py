from rest_framework import serializers
from django.utils.timezone import now  
from .models import Order, Dispute

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
            'created_by_admin', 'is_special_order'
        ]
        read_only_fields = [
            'id', 'client_username', 'writer_username', 'total_cost', 
            'writer_compensation', 'is_paid', 'created_at', 'updated_at', 
            'flag', 'writer_deadline'
        ]

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
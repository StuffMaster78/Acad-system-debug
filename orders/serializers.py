from rest_framework import serializers
from django.utils.timezone import now  # Importing now
from .models import Order, Dispute
from orders.models import PaymentTransaction
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id', 'topic', 'instructions', 'paper_type', 'academic_level', 
            'formatting_style', 'type_of_work', 'english_type', 'pages', 
            'slides', 'resources', 'spacing', 'deadline', 'writer_deadline', 
            'client', 'writer', 'preferred_writer', 'total_cost', 
            'writer_compensation', 'extra_services', 'subject', 'discount_code', 
            'is_paid', 'status', 'flag', 'created_at', 'updated_at', 
            'created_by_admin', 'is_special_order'
        ]
        read_only_fields = [
            'id', 'total_cost', 'writer_compensation', 'is_paid', 
            'created_at', 'updated_at', 'flag', 'writer_deadline'
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
        """
        Ensure the deadline is in the future.
        """
        if value <= now():
            raise serializers.ValidationError("The deadline must be in the future.")
        return value
    

class DisputeSerializer(serializers.ModelSerializer):
    """
    Serializer for the Dispute model.
    """
    order_id = serializers.PrimaryKeyRelatedField(
        source='order',  # Refers to the `order` ForeignKey in the model
        queryset=Order.objects.all(),  # Set a valid queryset
        help_text='The ID of the order associated with this dispute.'
    )
    raised_by_username = serializers.CharField(
        source='raised_by.username',  # Access `username` from the related `User` object
        read_only=True,
        help_text='The username of the user who raised this dispute.'
    )

    class Meta:
        model = Dispute
        fields = [
            'id',
            'order_id',
            'raised_by_username',
            'status',
            'reason',
            'resolution_notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'raised_by_username', 'created_at', 'updated_at']

    def validate_order_id(self, value):
        """
        Custom validation for the order_id field.
        """
        # Add any additional order validation logic here
        if not value:  # For example, ensure an order exists
            raise serializers.ValidationError("The order ID is invalid.")
        return value
    


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ["id", "order", "transaction_id", "amount", "status", "payment_method", "date_processed"]
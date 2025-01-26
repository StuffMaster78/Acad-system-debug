from rest_framework import serializers
from .models import Discount

class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        fields = [
            'id', 'code', 'description', 'discount_type', 'value', 'max_uses', 'used_count',
            'start_date', 'end_date', 'min_order_value', 'is_active', 'website'
        ]
        read_only_fields = ['id', 'used_count']
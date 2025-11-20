from rest_framework import serializers
from .models import (
    SpecialOrder,
    InstallmentPayment,
    PredefinedSpecialOrderConfig,
    PredefinedSpecialOrderDuration,
    WriterBonus
)
from .models import EstimatedSpecialOrderSettings

class PredefinedSpecialOrderConfigSerializer(serializers.ModelSerializer):
    """
    Serializer for predefined special order configurations.
    """

    class Meta:
        model = PredefinedSpecialOrderConfig
        fields = '__all__'


class PredefinedSpecialOrderDurationSerializer(serializers.ModelSerializer):
    """
    Serializer for duration pricing of predefined special orders.
    """

    class Meta:
        model = PredefinedSpecialOrderDuration
        fields = '__all__'


class InstallmentPaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for payments made in installments.
    """
    special_order_id = serializers.PrimaryKeyRelatedField(
        queryset=SpecialOrder.objects.all(),
        source='special_order',
        write_only=True
    )

    class Meta:
        model = InstallmentPayment
        fields = [
            'id', 'special_order_id', 'website', 'due_date',
            'amount_due', 'is_paid'
        ]


class SpecialOrderSerializer(serializers.ModelSerializer):
    """
    Serializer for special orders.
    """
    client_username = serializers.ReadOnlyField(source='client.username')
    writer_username = serializers.ReadOnlyField(source='writer.username')
    predefined_type = PredefinedSpecialOrderConfigSerializer(read_only=True)
    predefined_type_id = serializers.PrimaryKeyRelatedField(
        queryset=PredefinedSpecialOrderConfig.objects.all(),
        source='predefined_type',
        write_only=True,
        required=False
    )
    total_cost = serializers.ReadOnlyField()
    writer = serializers.PrimaryKeyRelatedField(read_only=True)
    client = serializers.HiddenField(default=serializers.CurrentUserDefault())
    installments = InstallmentPaymentSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = SpecialOrder
        fields = [
            'id', 'client', 'client_username', 'writer', 'writer_username',
            'order_type', 'predefined_type', 'predefined_type_id',
            'inquiry_details', 'admin_notes', 'total_cost',
            'deposit_required', 'is_approved', 'status', 'duration_days',
            'website', 'created_at', 'updated_at', 'installments'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        """
        Perform basic structural validation.
        """
        order_type = data.get('order_type')
        pre_type = data.get('predefined_type')

        if order_type == 'predefined' and not pre_type:
            raise serializers.ValidationError(
                "Predefined type is required for this order type."
            )

        duration_days = data.get('duration_days')
        if duration_days is not None and duration_days < 1:
            raise serializers.ValidationError(
                "Duration must be at least 1 day."
            )

        return data


class WriterBonusSerializer(serializers.ModelSerializer):
    """
    Serializer for bonuses granted to writers.
    """
    writer_username = serializers.ReadOnlyField(source='writer.username')
    special_order_id = serializers.PrimaryKeyRelatedField(
        queryset=SpecialOrder.objects.all(),
        source='special_order',
        write_only=True
    )

    class Meta:
        model = WriterBonus
        fields = [
            'id', 'writer', 'writer_username', 'special_order_id',
            'website', 'amount', 'category', 'is_paid', 'granted_at'
        ]
        read_only_fields = ['granted_at']



class EstimatedSpecialOrderSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for the EstimatedSpecialOrderSettings model.
    Used to serialize the settings related to deposit percentages for
    estimated special orders based on the website.
    """

    class Meta:
        model = EstimatedSpecialOrderSettings
        fields = ['id', 'website', 'default_deposit_percentage']

    def validate_default_deposit_percentage(self, value):
        """
        Custom validation to ensure the deposit percentage is between 0 and 100.
        """
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Deposit percentage must be between 0 and 100."
            )
        return value

    def create(self, validated_data):
        """
        Create a new EstimatedSpecialOrderSettings instance.
        If an existing setting exists for the website, it will be updated.
        """
        website = validated_data.get('website')
        defaults = {'default_deposit_percentage': validated_data.get('default_deposit_percentage')}
        
        settings, created = EstimatedSpecialOrderSettings.objects.update_or_create(
            website=website,
            defaults=defaults
        )
        return settings

    def update(self, instance, validated_data):
        """
        Update the EstimatedSpecialOrderSettings instance with the validated data.
        """
        instance.default_deposit_percentage = validated_data.get(
            'default_deposit_percentage', instance.default_deposit_percentage
        )
        instance.save()
        return instance
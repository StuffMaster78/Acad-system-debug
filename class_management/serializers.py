from rest_framework import serializers
from class_management.models import ClassPurchase, ClassInstallment, ClassBundleConfig
from websites.models import Website

# Serializer for ClassInstallment
class ClassInstallmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassInstallment
        fields = ('id', 'purchase', 'amount', 'due_date', 'paid', 'paid_at', 'wallet_txn')

    def validate(self, data):
        """
        You can add validation logic here, for example:
        - Check if the installment amount is greater than 0
        """
        if data['amount'] <= 0:
            raise serializers.ValidationError("Installment amount must be greater than 0.")
        return data

# Serializer for ClassPurchase
class ClassPurchaseSerializer(serializers.ModelSerializer):
    installments = ClassInstallmentSerializer(many=True, read_only=True)
    class_bundle = serializers.StringRelatedField()  # Assuming you want the related class bundle info as a string

    class Meta:
        model = ClassPurchase
        fields = ('id', 'client', 'program', 'duration', 'bundle_size', 'price_locked', 'status', 'paid_at', 'installments', 'class_bundle')

    def create(self, validated_data):
        """
        Create a ClassPurchase instance. You can also override to handle logic such as creating
        installments here if they should be part of the purchase.
        """
        purchase = ClassPurchase.objects.create(**validated_data)
        
        # Assuming you want to create installments after a purchase
        # If required, handle installment creation here.
        return purchase

    def update(self, instance, validated_data):
        """
        Override this method if you want to handle specific update logic for the purchase.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

# Serializer for ClassBundleConfig (Pricing Config)
class ClassBundleConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassBundleConfig
        fields = ('id', 'website', 'program', 'duration_range', 'bundle_size', 'price')

    def validate_price(self, value):
        """
        Ensure the price is a valid value, for example, must be greater than zero.
        """
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value
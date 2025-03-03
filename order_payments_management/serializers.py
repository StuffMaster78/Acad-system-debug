from django.db import models
from rest_framework import serializers
from django.utils import timezone
from .models import (
    OrderPayment, Refund, PaymentNotification, PaymentLog,
    PaymentDispute, DiscountUsage, SplitPayment, AdminLog,
    PaymentReminderSettings
)
from discounts.models import Discount

class OrderPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderPayment
        fields = "__all__"
        depth = 1
        
class TransactionSerializer(serializers.Serializer):
    """
    Unified serializer for handling all transactions:
    - Payments (`OrderPayment`)
    - Refunds (`Refund`)
    - Split Payments (`SplitPayment`)
    """

    transaction_id = serializers.CharField()
    transaction_type = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    status = serializers.CharField()
    payment_method = serializers.CharField(required=False, allow_null=True)
    client = serializers.StringRelatedField()
    order = serializers.SerializerMethodField()
    date_processed = serializers.DateTimeField()

    def get_order(self, instance):
        """Returns the order ID or Special Order ID associated with the transaction."""
        if hasattr(instance, "order") and instance.order:
            return instance.order.id
        if hasattr(instance, "special_order") and instance.special_order:
            return instance.special_order.id
        return None


    def to_representation(self, instance):
        """
        Custom representation to differentiate payments, refunds, and split payments.
        """
        data = super().to_representation(instance)

        if isinstance(instance, OrderPayment):
            data["transaction_type"] = "payment"
            data["status"] = instance.status
            data["amount"] = instance.discounted_amount
            data["transaction_id"] = instance.transaction_id
            data["payment_method"] = instance.payment_method
            data["date_processed"] = instance.date_processed

        elif isinstance(instance, Refund):
            data["transaction_type"] = "refund"
            data["status"] = instance.status
            data["amount"] = instance.amount
            data["transaction_id"] = f"refund-{instance.payment.transaction_id}"
            data["payment_method"] = "wallet" if instance.refund_method == "wallet" else "external"
            data["date_processed"] = instance.processed_at

        elif isinstance(instance, SplitPayment):
            data["transaction_type"] = "split_payment"
            data["status"] = "completed"
            data["amount"] = instance.amount
            data["transaction_id"] = f"split-{instance.payment.transaction_id}"
            data["payment_method"] = instance.method
            data["date_processed"] = instance.created_at

        return data


class PaymentNotificationSerializer(serializers.ModelSerializer):
    """Serializer for handling payment notifications."""
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = PaymentNotification
        fields = ["id", "user", "payment", "message", "created_at", "is_read"]
        read_only_fields = ["id", "user", "payment", "created_at"]

    def update(self, instance, validated_data):
        """Marks the notification as read if requested."""
        instance.is_read = validated_data.get("is_read", instance.is_read)
        instance.save()
        return instance



class PaymentLogSerializer(serializers.ModelSerializer):
    """Serializer for handling system and admin payment logs."""
    class Meta:
        model = PaymentLog
        fields = ["id", "payment", "event", "timestamp", "details"]
        read_only_fields = ["id", "payment", "timestamp"]


class PaymentDisputeSerializer(serializers.ModelSerializer):
    """Serializer for handling client payment disputes."""
    client = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = PaymentDispute
        fields = ["id", "payment", "client", "reason", "status", "created_at", "resolved_at"]
        read_only_fields = ["id", "client", "status", "created_at", "resolved_at"]

    def validate(self, data):
        """Ensures only completed payments can be disputed."""
        payment = data["payment"]
        if payment.status != "completed":
            raise serializers.ValidationError("You can only dispute completed payments.")
        return data

    def update(self, instance, validated_data):
        """Updates the dispute status (resolved or rejected)."""
        instance.status = validated_data.get("status", instance.status)
        if instance.status == "resolved":
            instance.resolved_at = timezone.now()
        instance.save()
        return instance


class DiscountUsageSerializer(serializers.ModelSerializer):
    """
    Serializer for tracking discount usage.
    Stores details about when and where a discount was applied.
    """
    user = serializers.StringRelatedField(read_only=True)
    discount = serializers.StringRelatedField(read_only=True)
    order = serializers.StringRelatedField(read_only=True)
    special_order = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DiscountUsage
        fields = ["id", "discount", "user", "order", "special_order", "applied_at"]
        read_only_fields = ["id", "discount", "user", "order", "special_order", "applied_at"]

class SplitPaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for handling split payments.
    Allows clients to pay using multiple methods (e.g., part wallet, part card).
    """
    payment = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SplitPayment
        fields = ["id", "payment", "method", "amount", "created_at"]
        read_only_fields = ["id", "payment", "created_at"]

    def validate(self, data):
        """Ensures the split payment does not exceed total amount due."""
        total_split = SplitPayment.objects.filter(payment=data["payment"]).aggregate(
            total=models.Sum("amount")
        )["total"] or 0

        if total_split + data["amount"] > data["payment"].discounted_amount:
            raise serializers.ValidationError("Total split payments cannot exceed the discounted amount.")

        return data


    def create(self, validated_data):
        """Processes split payments and checks completion."""
        split_payment = SplitPayment.objects.create(**validated_data)

        # Check if the total amount has been fully covered
        total_paid = SplitPayment.objects.filter(payment=split_payment.payment).aggregate(
            total=models.Sum("amount")
        )["total"]

        if total_paid >= split_payment.payment.discounted_amount:
            split_payment.payment.mark_completed()

        return split_payment


class AdminLogSerializer(serializers.ModelSerializer):
    """
    Serializer for logging admin actions related to payments, refunds, and disputes.
    Helps track manual interventions for accountability.
    """
    admin = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = AdminLog
        fields = ["id", "admin", "action", "timestamp", "details"]
        read_only_fields = ["id", "admin", "timestamp"]


class PaymentReminderSettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for admins to update payment reminder settings.
    """
    admin = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = PaymentReminderSettings
        fields = [
            "first_reminder_hours", "final_reminder_hours",
            "first_reminder_message", "final_reminder_message",
            "admin", "last_updated"
        ]
        read_only_fields = ["admin", "last_updated"]

    def update(self, instance, validated_data):
        """
        Updates the reminder settings and logs the admin who made the change.
        """
        request = self.context.get("request")
        admin_user = request.user if request and request.user.is_staff else None
        instance.admin = admin_user
        return super().update(instance, validated_data)
    
class RefundSerializer(serializers.ModelSerializer):
    payment_id = serializers.CharField(source="payment.transaction_id", read_only=True)
    client_username = serializers.CharField(source="client.username", read_only=True)
    processed_by_username = serializers.CharField(source="processed_by.username", read_only=True)

    class Meta:
        model = Refund
        fields = [
            "id",
            "payment_id",
            "client_username",
            "amount",
            "reason",
            "status",
            "processed_by_username",
            "processed_at",
            "created_at",
        ]
        read_only_fields = ["id", "processed_at", "created_at", "processed_by_username", "payment_id", "client_username"]
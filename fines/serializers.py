from rest_framework import serializers
from django.contrib.auth import get_user_model
from fines.models import Fine, FineAppeal, FineStatus
from orders.models import Order  # Assuming you have an Order model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user-related fields in fine objects."""

    class Meta:
        model = User
        fields = ["id", "username", "email"]


class FineSerializer(serializers.ModelSerializer):
    """
    Serializer for Fine model with support for read/write operations.

    Includes validation for fine amounts and ensures status integrity.
    """

    issued_by = UserSerializer(read_only=True)
    waived_by = UserSerializer(read_only=True)
    order_id = serializers.IntegerField(write_only=True)
    order = serializers.IntegerField(source="order.id", read_only=True)

    class Meta:
        model = Fine
        fields = [
            "id",
            "order_id",
            "order",
            "fine_type",
            "amount",
            "reason",
            "status",
            "imposed_at",
            "waived_by",
            "waived_at",
            "waiver_reason",
        ]
        read_only_fields = [
            "status",
            "imposed_at",
            "waived_by",
            "waived_at",
            "waiver_reason",
        ]

    def validate_amount(self, value):
        """Ensure the fine amount is positive."""
        if value <= 0:
            raise serializers.ValidationError(
                "Fine amount must be greater than zero."
            )
        return value

    def create(self, validated_data):
        """
        Create and return a new Fine instance.

        Adds current user as `issued_by` and sets status to 'issued'.
        """
        request = self.context.get("request")
        if request:
            validated_data["issued_by"] = request.user
        validated_data["status"] = FineStatus.ISSUED
        return Fine.objects.create(**validated_data)


class FineAppealSerializer(serializers.ModelSerializer):
    """
    Serializer for FineAppeal model with support for read/write ops.

    Validates appeal ownership and ensures only one appeal per fine.
    """

    appealed_by = UserSerializer(read_only=True)
    reviewed_by = UserSerializer(read_only=True)
    fine_id = serializers.IntegerField(write_only=True)
    fine = serializers.IntegerField(source="fine.id", read_only=True)

    class Meta:
        model = FineAppeal
        fields = [
            "id",
            "fine_id",
            "fine",
            "reason",
            "appealed_by",
            "created_at",
            "reviewed_by",
            "reviewed_at",
            "accepted",
        ]
        read_only_fields = [
            "created_at",
            "reviewed_by",
            "reviewed_at",
            "accepted",
        ]

    def validate_fine_id(self, fine_id):
        """Ensure the fine exists and has not already been appealed."""
        if not Fine.objects.filter(id=fine_id).exists():
            raise serializers.ValidationError("Fine does not exist.")
        if FineAppeal.objects.filter(fine_id=fine_id).exists():
            raise serializers.ValidationError("This fine is already appealed.")
        return fine_id

    def create(self, validated_data):
        """
        Create and return a new FineAppeal instance.

        Adds current user as `appealed_by`.
        """
        request = self.context.get("request")
        if request:
            validated_data["appealed_by"] = request.user
        return FineAppeal.objects.create(**validated_data)
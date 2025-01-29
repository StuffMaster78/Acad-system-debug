from rest_framework import serializers
from .models import ClientProfile, SuspiciousLogin, ClientActivityLog, TemporaryPassword, ProfileUpdateRequest
from loyalty_management.models import LoyaltyTransaction, Milestone
from wallet.models import Wallet
from django.apps import apps
from decimal import Decimal

class MilestoneSerializer(serializers.ModelSerializer):
    """
    Serializer for the Milestone model.
    """
    class Meta:
        model = Milestone
        fields = [
            "id",
            "name",
            "description",
            "reward_points",
            "target_value",
            "target_type",
        ]


class LoyaltyTransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for the LoyaltyTransaction model.
    """
    client_username = serializers.CharField(source="client.user.username", read_only=True)

    class Meta:
        model = LoyaltyTransaction
        fields = [
            "id",
            "client",
            "client_username",
            "points",
            "transaction_type",
            "timestamp",
            "reason",
        ]
        read_only_fields = ["timestamp"]


class ClientProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the ClientProfile model.
    """
    client_username = serializers.CharField(source="user.username", read_only=True)
    preferred_writers = serializers.StringRelatedField(many=True)
    loyalty_points = serializers.IntegerField(source="loyalty_points", read_only=True)
    loyalty_tier = serializers.CharField(source="loyalty_tier.name", read_only=True)
    wallet_balance = serializers.DecimalField(
        max_digits=10, decimal_places=2, source="wallet_balance", read_only=True, min_value=Decimal("0.00")
    )
    milestones = MilestoneSerializer(source="get_milestones", many=True, read_only=True)
    loyalty_transactions = serializers.SerializerMethodField()

    class Meta:
        model = ClientProfile
        fields = [
            "id",
            "user",
            "client_username",
            "timezone",
            "country",
            "preferred_writers",
            "loyalty_points",
            "loyalty_tier",
            "wallet_balance",
            "milestones",
            "loyalty_transactions",
            "total_spent",
            "is_active",
            "is_suspended",
            "badges",
        ]
        read_only_fields = ["user", "loyalty_points", "loyalty_tier", "wallet_balance"]

    def get_loyalty_transactions(self, obj):
        """
        Retrieve loyalty transactions for the client.
        """
        transactions = LoyaltyTransaction.objects.filter(client=obj)
        return LoyaltyTransactionSerializer(transactions, many=True).data

    def get_badges(self, obj):
        """
        Retrieve all the basdges awarded to the client from loyalty_management.
        """
        ClientBadge = apps.get_model('loyalty_management', 'ClientBadge')
        badges = ClientBadge.objects.filter(client=self)
        return [
            {"badge_name": badge.badge_name, "awarded_at": badge.awarded_at.strftime('%Y-%m-%d')}
            for badge in badges
        ]

class SuspiciousLoginSerializer(serializers.ModelSerializer):
    """
    Serializer for the SuspiciousLogin model.
    """
    client_username = serializers.CharField(source="client.user.username", read_only=True)

    class Meta:
        model = SuspiciousLogin
        fields = [
            "id",
            "client",
            "client_username",
            "ip_address",
            "detected_country",
            "timestamp",
        ]
        read_only_fields = ["timestamp"]

class ClientActivityLogSerializer(serializers.ModelSerializer):
    """
    Serializer for the ClientActivityLog model.
    """
    client_username = serializers.CharField(source="client.user.username", read_only=True)

    class Meta:
        model = ClientActivityLog
        fields = [
            "id",
            "client",
            "client_username",
            "action",
            "timestamp",
        ]
        read_only_fields = ["timestamp"]


class TemporaryPasswordSerializer(serializers.ModelSerializer):
    """
    Serializer for the TemporaryPassword model.
    """
    client_username = serializers.CharField(source="client.user.username", read_only=True)

    class Meta:
        model = TemporaryPassword
        fields = [
            "id",
            "client",
            "client_username",
            "code",
            "expires_at",
        ]
        read_only_fields = ["expires_at"]


class ProfileUpdateRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProfileUpdateRequest model.
    """
    client_username = serializers.CharField(source="client.user.username", read_only=True)

    class Meta:
        model = ProfileUpdateRequest
        fields = [
            "id",
            "client",
            "client_username",
            "requested_changes",
            "status",
            "admin_response",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "admin_response"]


class ClientActionSerializer(serializers.Serializer):
    """
    Serializer for handling client account actions such as suspend, activate, and deactivate.
    """
    action = serializers.ChoiceField(
        choices=["suspend", "activate", "deactivate"],
        required=True,
        help_text="The action to perform on the client account."
    )
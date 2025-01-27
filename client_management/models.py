from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User


class ClientProfile(models.Model):
    """
    Stores client-specific details.
    """
    client = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='client_profile', limit_choices_to={'role': 'client'}
    )
    loyalty_points = models.PositiveIntegerField(default=0, help_text=_("Loyalty points accumulated by the client."))
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text=_("Total amount spent by the client."))
    preferred_writers = models.ManyToManyField(
        User,
        blank=True,
        limit_choices_to={'role': 'writer'},
        help_text=_("Client's preferred writers."),
        related_name="preferred_by_clients"
    )

    def __str__(self):
        return f"Client Profile: {self.client.username}"


class LoyaltyPointConfig(models.Model):
    """
    Stores configuration for loyalty points redemption.
    """
    points_per_dollar = models.PositiveIntegerField(
        default=10,
        help_text="Number of points required to redeem $1."
    )
    minimum_points_redeem = models.PositiveIntegerField(
        default=100,
        help_text="Minimum points required to initiate a redemption."
    )

    def __str__(self):
        return f"{self.points_per_dollar} points = $1, Min: {self.minimum_points_redeem} points"

class LoyaltyTransaction(models.Model):
    """
    Tracks loyalty points earned or deducted.
    """
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name="loyalty_transactions")
    points = models.IntegerField(help_text=_("Points added or deducted."))
    transaction_type = models.CharField(
        max_length=20,
        choices=(("add", "Add"), ("deduct", "Deduct")),
        default="add",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True, null=True, help_text=_("Reason for the loyalty transaction."))

    def __str__(self):
        return f"Loyalty Transaction: {self.points} points ({self.transaction_type}) for {self.client.client.username}"
    

class LoyaltyPoint(models.Model):
    """
    Tracks loyalty points for clients.
    """
    client = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="loyalty_points",
        limit_choices_to={'role': 'client'},
        help_text=_("The client associated with these loyalty points."),
    )
    points = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.0,
        help_text=_("Total loyalty points available for the client."),
    )
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client.username} - {self.points} Points"


class LoyaltyPointHistory(models.Model):
    """
    Logs changes to loyalty points for audit purposes.
    """
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="loyalty_point_history",
        limit_choices_to={'role': 'client'},
        help_text=_("The client associated with this points change."),
    )
    points_change = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_("The amount of points added or deducted."),
    )
    reason = models.CharField(
        max_length=255,
        help_text=_("Reason for the points change."),
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.username} - {self.points_change} Points ({self.reason})"
    

class LoyaltyPointRedemption(models.Model):
    """
    Tracks redemption transactions for loyalty points.
    """
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="redemption_transactions",
        limit_choices_to={"role": "client"},
    )
    points_redeemed = models.PositiveIntegerField(help_text="Number of points redeemed.")
    redeemed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Equivalent dollar amount redeemed.",
    )
    timestamp = models.DateTimeField(auto_now_add=True, help_text="Date and time of redemption.")

    def __str__(self):
        return f"{self.client.username} - {self.points_redeemed} points redeemed"

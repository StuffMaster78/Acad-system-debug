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
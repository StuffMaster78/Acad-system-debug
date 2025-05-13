from decimal import Decimal
from django.db import models
from datetime import timedelta
from django.utils.timezone import now
from core.models.base import WebsiteSpecificBaseModel
from django.conf import settings
from websites.models import Website
# from client_management.models import LoyaltyPoint

User = settings.AUTH_USER_MODEL 
class Wallet(WebsiteSpecificBaseModel):
    """
    Wallet for managing balances of users (clients, writers, etc.), scoped to a specific website.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='user_wallet'
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="wallet",
        help_text="The user associated with this wallet."
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.0,
        help_text="Current wallet balance."
    )
    last_updated = models.DateTimeField(auto_now=True)

    def is_client_wallet(self):
        return self.user.role == "client"

    def is_writer_wallet(self):
        return self.user.role == "writer"

    def __str__(self):
        return f"{self.user.username}'s Wallet ({self.user.role}) - ${self.balance}"
    
    def calculate_loyalty_points(self):
        """
        Calculates loyalty points for the client based on their wallet balance or transactions.
        """
        from client_management.models import LoyaltyPoint  # Local import to avoid circular import issues

        # Example logic: 1 loyalty point for every $10 in wallet balance
        points = int(self.balance // 10)

        # Update or create the LoyaltyPoint entry for the client
        loyalty_point, created = LoyaltyPoint.objects.update_or_create(
            client=self.client,
            defaults={'points': points}
        )
        return loyalty_point


class WalletTransaction(WebsiteSpecificBaseModel):
    """
    Logs all wallet transactions (credits, debits, etc.).
    """
    TRANSACTION_TYPES = (
        ('top-up', 'Top-Up'),
        ('withdrawal', 'Withdrawal'),
        ('refund', 'Refund'),
        ('payment', 'Payment'),
        ('bonus', 'Bonus'),
        ('adjustment', 'Adjustment'),
        ("referral_bonus", "Referral Bonus"),
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='wallet_transactions'
    )
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="transactions",
        help_text="The wallet this transaction belongs to."
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        help_text="Type of transaction."
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Transaction amount."
    )
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional description for the transaction."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.transaction_type == "bonus" and not self.expires_at:
            self.expires_at = now() + timedelta(days=30)  # Default to 30 days
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} of ${self.amount} for {self.wallet.user.username}"


class WithdrawalRequest(WebsiteSpecificBaseModel):
    """
    Tracks withdrawal requests made by writers.
    """
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='withdrawal_request'
    )
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name="withdrawal_requests",
        help_text="The wallet requesting the withdrawal."
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Requested withdrawal amount."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the withdrawal request."
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description for the request."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def approve(self, admin_user):
        """
        Approve the withdrawal request and deduct the amount from the wallet.
        """
        if self.status != 'pending':
            raise ValueError("This withdrawal request has already been processed.")

        if self.wallet.balance < self.amount:
            raise ValueError("Insufficient wallet balance for this withdrawal.")

        self.wallet.balance -= self.amount
        self.wallet.save()

        self.status = 'approved'
        self.processed_at = now()
        self.save()

        WalletTransaction.objects.create(
            wallet=self.wallet,
            transaction_type='withdrawal',
            amount=self.amount,
            description=f"Approved withdrawal request by admin {admin_user.username}",
            website=self.website
        )

    def reject(self, admin_user):
        """
        Reject the withdrawal request.
        """
        if self.status != 'pending':
            raise ValueError("This withdrawal request has already been processed.")

        self.status = 'rejected'
        self.processed_at = now()
        self.save()

    def __str__(self):
        return f"Withdrawal Request - {self.wallet.user.username} - ${self.amount} ({self.status})"
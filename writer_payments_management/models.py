from django.db import models
from django.utils.timezone import now
from decimal import Decimal
from orders.models import Order
from special_orders.models import SpecialOrder
from writer_management.models import WriterProfile
from wallet.models import Wallet, WalletTransaction
from notifications_system import send_notification  # Import notification system
from django.conf import settings
from websites.models import Website


User = settings.AUTH_USER_MODEL 
class WriterPayment(models.Model):
    """
    Handles writer payments, including order payments, 
    special order bonuses, fines, and status management.
    """

    STATUS_CHOICES = [
        ("Pending", "Pending"),  # Default before admin review
        ("Paid", "Paid"),  # Payment successfully processed
        ("Blocked", "Blocked"),  # Payment prevented due to order cancellation
        ("Delayed", "Delayed"),  # Payment held due to revision/dispute
        ("Voided", "Voided")  # Payment removed due to reassignment
    ]
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="payments",
        help_text="Writer receiving the payment."
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="The order related to this payment."
    )
    special_order = models.ForeignKey(
        SpecialOrder,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text="The special order related to this payment."
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Total payment amount."
    )
    bonuses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Bonus amount added."
    )
    fines = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Any fines deducted."
    )
    tips = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Tips received from clients."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending",
        help_text="Payment status based on order conditions."
    )
    processed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    transaction_reference = models.CharField(max_length=255, null=True, blank=True)
    def process_payment(self):
        """
        Calculates the final payment, applies bonuses, fines, updates wallet, 
        and logs the transaction.
        """
        if not self.writer.writer_level:
            raise ValueError("Writer level is not set.")

        # Fetch writer's level-based pay rate
        pages_payment = self.writer.writer_level.base_pay_per_page
        slides_payment = self.writer.writer_level.base_pay_per_slide

        # Calculate base payment if an order exists
        base_payment = (self.order.number_of_pages * pages_payment if self.order else 0.00) + \
                       (self.order.number_of_slides * slides_payment if self.order else 0.00)

        # Apply bonuses from Special Orders
        if self.special_order:
            self.bonuses += self.special_order.bonus_amount

        # Calculate total deductions (penalties)
        total_fines = sum(p.amount_deducted for p in self.writer.penalties.all())
        self.fines += total_fines

        # Calculate final payment
        final_payment = base_payment + self.bonuses + self.tips - self.fines
        self.amount = max(final_payment, 0)  # Ensure non-negative payment

        # Update Wallet
        wallet, created = Wallet.objects.get_or_create(user=self.writer.user)
        wallet.balance += self.amount
        wallet.save()

        # Log the transaction
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type="payment",
            amount=self.amount,
            description="Writer payment processed."
        )

        # Mark as paid
        self.status = "Paid"
        self.processed_at = now()
        self.save()

        # Send notifications
        send_notification(
            user=self.writer.user,
            title="Payment Processed",
            message=f"You payment of ${self.amount} is on it's way.",
            category="payment"
        )

    def update_payment_status(self):
        """
        Updates payment status when an order is cancelled, reassigned, 
        put on revision, or disputed.
        """
        if self.order.status == "Cancelled":
            self.status = "Blocked"
            self.amount = 0  # Remove earnings
        elif self.order.status == "Revision":
            self.status = "Delayed"
        elif self.order.status == "Reassigned":
            self.status = "Voided"
            self.amount = 0  # Reset payment as order moved

            # Create a new payment for the new writer
            new_writer_payment = WriterPayment.objects.create(
                writer=self.order.assigned_writer,
                order=self.order,
                amount=0.00,  # Will be recalculated
                status="Pending"
            )
            new_writer_payment.process_payment()
            
        elif self.order.status == "Disputed":
            self.status = "Delayed"

        self.save()


    def mark_as_paid(self, admin_user):
        """
        Manually sets a payment as 'Paid'.
        Updates the writer's wallet and logs the transaction.
        """
        if self.status in ["Pending", "Delayed"]:
            self.status = "Paid"
            self.processed_at = now()
            self.save()

            # Update Wallet
            wallet, created = Wallet.objects.get_or_create(user=self.writer.user)
            wallet.balance += self.amount
            wallet.save()

            # Log transaction
            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type="payment",
                amount=self.amount,
                description=f"Writer payment manually approved by {admin_user.username}."
            )

            # Notify writer
            send_notification(
                user=self.writer.user,
                title="Payment Approved",
                message=f"Your payment of ${self.amount} has been approved.",
                category="payment"
            )

    class Meta:
        unique_together = ('writer', 'order')

class WriterPayoutRequest(models.Model):
    """
    Handles writer payout requests.
    """

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("Rejected", "Rejected")
    ]
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="payout_requests",
        help_text="Writer requesting the payout."
    )
    amount_requested = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Requested payout amount."
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending",
        help_text="Payout request status."
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def approve_payout(self, admin_user):
        """
        Approves the payout, deducts from the wallet, and clears payments.
        """
        wallet = Wallet.objects.get(user=self.writer.user)

        if wallet.balance < self.amount_requested:
            raise ValueError("Insufficient wallet balance.")

        # Deduct from wallet
        wallet.balance -= self.amount_requested
        wallet.save()

        # Mark all pending payments as paid
        WriterPayment.objects.filter(
            writer=self.writer, status="Pending"
        ).update(status="Paid", processed_at=now())

        # Log transaction
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type="withdrawal",
            amount=self.amount_requested,
            description=f"Approved withdrawal by admin {admin_user.username}."
        )

        # Update status
        self.status = "Approved"
        self.processed_at = now()
        self.save()

        # Send notification
        send_notification(
            user=self.writer.user,
            title="Payout Approved",
            message=f"Your payout request of ${self.amount_requested} has been approved.",
            category="payout"
        )

class SpecialOrderBonus(models.Model):
    """
    Tracks bonuses awarded to writers for completing special orders.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer = models.ForeignKey(
        WriterProfile,
        on_delete=models.CASCADE,
        related_name="special_order_bonuses"
    )
    special_order = models.ForeignKey(
        SpecialOrder,
        on_delete=models.CASCADE,
        related_name="bonuses"
    )
    bonus_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Bonus amount for the special order."
    )
    granted_at = models.DateTimeField(auto_now_add=True)

    def apply_bonus(self):
        """
        Credits the writer's wallet when the bonus is granted.
        Logs the transaction and sends a notification.
        """
        wallet, created = Wallet.objects.get_or_create(
            user=self.writer.user
        )
        wallet.balance += self.bonus_amount
        wallet.save()

        # Log transaction
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type="bonus",
            amount=self.bonus_amount,
            description="Special order bonus applied."
        )

        # Notify writer
        send_notification(
            user=self.writer.user,
            title="Bonus Received",
            message=f"You have received a special order bonus of ${self.bonus_amount}.",
            category="bonus"
        )


class WriterPaymentAdjustment(models.Model):
    """
    Logs manual payment adjustments made by admins.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE
    )
    writer_payment = models.ForeignKey(
        WriterPayment,
        on_delete=models.CASCADE,
        related_name="adjustments",
        help_text="Payment entry being adjusted."
    )
    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payment_adjustments",
        help_text="Admin making the adjustment."
    )
    adjustment_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Amount adjusted (positive or negative)."
    )
    reason = models.TextField(
        help_text="Reason for adjustment."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def apply_adjustment(self):
        """
        Applies an admin adjustment to the writer's payment and updates the wallet.
        """
        self.writer_payment.amount += self.adjustment_amount
        self.writer_payment.save()

        # Update Wallet
        wallet = Wallet.objects.get(
            user=self.writer_payment.writer.user
        )
        wallet.balance += self.adjustment_amount
        wallet.save()

        # Log transaction
        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type="adjustment",
            amount=self.adjustment_amount,
            description=f"Admin adjustment: {self.reason}."
        )
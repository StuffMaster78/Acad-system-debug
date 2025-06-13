from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from decimal import Decimal
from wallet.models import Wallet
from django.core.exceptions import ValidationError
from discounts.models.discount import Discount 
from django.utils.timezone import now
from referrals.models import Referral, ReferralBonusConfig
from websites.models import Website
class OrderPayment(models.Model):
    """
    Manages payments for standard, predefined special,
    and estimated special orders.
    Handles discount application, wallet deductions,
    payment processing, and refunds.
    """
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    PAYMENT_TYPE_CHOICES = [
        ("standard", "Standard Order"),
        ("predefined_special", "Predefined Special Order"),
        ("estimated_special", "Estimated Special Order"),
    ]
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='order_payment'
    )

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    payment_type = models.CharField(
        max_length=20,
        choices=PAYMENT_TYPE_CHOICES
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="payments",
        null=True, blank=True
    )
    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        related_name="payments",
        null=True, blank=True
    )
    transaction_id = models.CharField(max_length=255, unique=True)
    original_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Order amount before discount"
    )
    discount = models.ForeignKey(
        Discount, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="applied_payments"
    )
    discounted_amount = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Final amount after discount"
    )
    payment_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    date_processed = models.DateTimeField(auto_now_add=True)

    refund_reason = models.TextField(blank=True, null=True)
    refunded_at = models.DateTimeField(blank=True, null=True)


    def apply_discount(self, discount_code=None, referral_code=None):
        """
        Apply discount to the payment,
        including potential referral discount.
        """
        if self.discount:
            raise ValidationError("A discount has already been applied.")

        # Apply discount from discount code if provided
        if discount_code:
            discount = self.get_valid_discount(discount_code)
            discount_value = self.calculate_discount_value(discount)
            self.discounted_amount = max(self.original_amount - discount_value, 0)
            self.discount = discount
            discount.increment_usage()

        # Apply referral discount if referral code is provided
        if referral_code:
            referral = Referral.objects.filter(referral_code=referral_code).first()
            if referral and referral.referred_user == self.client:
                # Apply only if it's the referred user's first order
                if self.order and self.order.user.orders.count() == 1:  # Check for first order
                    referral_discount = self.apply_referral_discount(referral)
                    self.discounted_amount = max(self.discounted_amount - referral_discount, 0)
                    referral.first_order_referral_bonus_credited = True
                    referral.save()

        self.save()

    def apply_referral_discount(self, referral):
        """Calculate and apply referral discount."""
        # Assuming referral discount is stored in the Referral model, you can customize this logic
        bonus_config = ReferralBonusConfig.objects.filter(website=referral.website).first()
        if bonus_config:
            if bonus_config.first_order_discount_type == 'percentage':
                discount_value = (bonus_config.first_order_discount_amount / 100) * self.original_amount
            elif bonus_config.first_order_discount_type == 'fixed':
                discount_value = bonus_config.first_order_discount_amount
            else:
                discount_value = 0

            return discount_value
        return 0

    def get_valid_discount(self, discount_code):
        """Fetch and validate discount."""
        try:
            discount = Discount.objects.get(code=discount_code)
            if not discount.is_valid():
                raise ValidationError("This discount code is expired or inactive.")
            if discount.min_order_value and self.original_amount < discount.min_order_value:
                raise ValidationError(f"Minimum order value for this discount is ${discount.min_order_value}.")
            return discount
        except Discount.DoesNotExist:
            raise ValidationError("Invalid discount code.")

    def calculate_discount_value(self, discount):
        """Calculate discount value based on type."""
        return discount.value if discount.discount_type == "fixed" else (discount.value / 100) * self.original_amount


    def verify_payment(self):
        """
        Verifies that the payment was successfully processed before completion.
        This is useful for external payment gateways like Stripe or PayPal.
        """
        if self.status == "completed":
            return True  # Already verified
        
        # # Logic to check payment provider's response
        # payment_verified = external_payment_gateway.verify_transaction(self.transaction_id)

        # Replace with actual external verification logic
        payment_verified = True  # Assume verification succeeds

        if payment_verified:
            self.mark_completed()
        else:
            self.mark_failed()

    def validate_duplicate_payment(self):
        """
        Ensures an order does not have multiple successful payments.
        Prevents double charging.
        """
        existing_payment = OrderPayment.objects.filter(
            order=self.order, status="completed"
        ).exists()

        if existing_payment:
            raise ValidationError("This order has already been paid for.")


    def mark_completed(self):
        """Marks the payment as completed and updates the order status."""
        self.status = "completed"
        self.save()
        self.update_order_status()

    def mark_failed(self):
        """Marks the payment as failed."""
        self.status = "failed"
        self.save()

    def mark_as_paid(self):
        """Mark the order as paid if a completed payment exists."""
        self.status = "paid"
        self.save(update_fields=["status"])

    def mark_as_unpaid(self):
        """Mark the order as unpaid if all payments are refunded."""
        self.status = "unpaid"
        self.save(update_fields=["status"])

    def refund(self, reason=None):
        """Marks the transaction as refunded."""
        if self.status not in ["completed"]:
            raise ValueError("Only completed payments can be refunded.")

        self.status = "refunded"
        self.refund_reason = reason if reason else "No reason provided"
        self.refunded_at = now()
        self.save()

        # Check if all payments for this order are refunded
        if not OrderPayment.objects.filter(order=self.order, status="completed").exists():
            self.order.mark_as_unpaid()


    def update_order_status(self):
        """Updates the status of the associated order after payment completion."""
        if self.payment_type == "standard" and self.order:
            self.order.mark_paid()
        elif (self.payment_type in ["predefined_special", "estimated_special"] and
              self.special_order):
            self.special_order.update_payment_status()

    def send_payment_notification(self):
        """
        Sends an email and in-app notification for payment events.
        """
        from notifications_system.models import Notification

        messages = {
            "completed": f"Your payment of ${self.discounted_amount} has been received!",
            "failed": "Your payment attempt failed. Please try again.",
            "refunded": f"A refund of ${self.discounted_amount} has been processed.",
        }

        if self.status in messages:
            Notification.create_notification(user=self.client, message=messages[self.status])

            send_mail(
                subject="Payment Update",
                message=messages[self.status],
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.client.email],
            )

    def process_wallet_payment(self):
        """Deducts the amount from the client's wallet."""
        wallet = Wallet.objects.select_for_update().get(user=self.client)
        if wallet.balance < self.discounted_amount:
            raise ValueError("Insufficient wallet balance.")

        wallet.balance -= self.discounted_amount
        wallet.save()
        self.mark_completed()

    def clean(self):
        """Enforce business rules for payment status transitions."""

        if self.status == "completed":
            # Prevent multiple completed payments for the same order
            if OrderPayment.objects.filter(order=self.order, status="completed").exclude(id=self.id).exists():
                raise ValidationError("This order has already been paid for.")

            # Prevent marking a refunded payment as completed
            if self.pk and OrderPayment.objects.filter(id=self.pk, status="refunded").exists():
                raise ValidationError("A refunded payment cannot be marked as completed again.")

        if self.status == "refunded":
            # Prevent refunding a payment that isn't completed
            if not OrderPayment.objects.filter(id=self.pk, status="completed").exists():
                raise ValidationError("Only completed payments can be refunded.")

    def save(self, *args, **kwargs):
        self.clean()  # Ensure validation before saving
        super().save(*args, **kwargs)

        # Automatically mark order as paid if a completed payment exists
        if self.status == "completed":
            self.order.mark_as_paid()

        # Automatically mark order as unpaid if all payments are refunded
        elif self.status == "refunded" and not OrderPayment.objects.filter(order=self.order, status="completed").exists():
            self.order.mark_as_unpaid()

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.status} - ${self.discounted_amount}"

class DiscountUsage(models.Model):
    """
    Tracks and updates the usage of discount codes by clients.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='order_discount_usage'
    )
    discount = models.ForeignKey(
        Discount,
        on_delete=models.CASCADE,
        related_name="usage_logs"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="discount_usage"
    )
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    special_order = models.ForeignKey(
        "special_orders.SpecialOrder",
        on_delete=models.CASCADE,
        null=True, blank=True
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} used {self.discount.code} on {self.applied_at}"


class FailedPayment(models.Model):
    """
    Tracks and logs all the instances of failed payments.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='failed_order_payments'
    )
    payment = models.ForeignKey(
        "OrderPayment",
        on_delete=models.CASCADE,
        related_name="failed_payments"
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="failed_payments"
    )
    failure_reason = models.TextField()
    failed_at = models.DateTimeField(default=timezone.now)
    retry_count = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    def retry_payment(self):
        """Retry failed payment (Triggered via Celery Task)."""
        if self.retry_count < 3:  # Limit retries to avoid abuse
            self.retry_count += 1
            self.save()
            # Initiate a new payment attempt here

    @classmethod
    def log_failed_payment(cls, order_id, client_id, payment_method, failure_reason):
        """Log a failed payment attempt"""
        from orders.models import Order  # Avoid circular import
        from django.conf import settings

        User = settings.AUTH_USER_MODEL 

        order = Order.objects.get(id=order_id)
        client = User.objects.get(id=client_id)
        
        failed_payment = cls.objects.create(
            order=order,
            client=client,
            payment_method=payment_method,
            failure_reason=failure_reason,
            retry_count=0
        )
        return failed_payment

    def send_failure_notification(self):
        """
        Send an email to the client and admin when a payment fails.
        """
        subject = f"Payment Failure for Order {self.order.id}"
        message = (
            f"Dear {self.client.username},\n\n"
            f"Your payment for order {self.order.id} has failed due to: {self.failure_reason}.\n\n"
            f"Please try again or contact support."
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [self.client.email, settings.ADMIN_EMAIL]

        send_mail(subject, message, from_email, recipient_list)

    class Meta:
        verbose_name = "Failed Payment"
        verbose_name_plural = "Failed Payments"
        ordering = ["-failed_at"]
    
    def __str__(self):
        return f"Failed Payment for Order {self.order.id} by {self.client.username} on {self.failed_at}"


class PaymentNotification(models.Model):
    """
    Stores notifications related to payment events.
    Helps clients stay informed about payment status updates.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='order_payment_notification'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payment_notifications"
    )
    payment = models.ForeignKey(
        "OrderPayment",
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    @classmethod
    def create_notification(cls, user, payment, message):
        """
        Sends a notification related to a payment event.
        Example: "Your payment of $50 has been received."
        """
        return cls.objects.create(
            user=user,
            payment=payment,
            message=message
        )


class PaymentLog(models.Model):
    """
    Stores logs for all payment-related actions.
    Useful for tracking and auditing payment transactions.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='order_payment_log'
    )
    payment = models.ForeignKey(
        "OrderPayment",
        on_delete=models.CASCADE,
        related_name="logs"
    )
    event = models.CharField(
        max_length=255,
        help_text="Example: 'Payment Completed', 'Refund Issued'"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    @classmethod
    def log_event(cls, payment, event, details=""):
        """
        Creates a log entry for a payment event.
        Example: "Refund Issued - Client refunded $20."
        """
        return cls.objects.create(payment=payment, event=event, details=details)


class PaymentDispute(models.Model):
    """
    Manages disputes for failed or incorrect payments.
    Allows clients to raise disputes, which can be reviewed and resolved by admins.
    """
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("under_review", "Under Review"),
        ("resolved", "Resolved"),
        ("rejected", "Rejected"),
    ]

    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='order_payment_dispute'
    )
    payment = models.ForeignKey(
        "OrderPayment",
        on_delete=models.CASCADE,
        related_name="disputes"
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="disputes"
    )
    reason = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def mark_resolved(self):
        """
        Marks the dispute as resolved and updates the payment status to refunded.
        """
        self.status = "resolved"
        self.resolved_at = timezone.now()
        self.save()
        self.payment.status = "refunded"
        self.payment.save()


class Refund(models.Model):
    """
    Manages refunds for payments. Supports both wallet refunds and external refunds.
    Refund adjustments for writers will be handled in the separate writer payments app.
    """
    REFUND_METHOD_CHOICES = [
        ("wallet", "Wallet Refund"),
        ("external", "External Refund"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processed", "Processed"),
        ("rejected", "Rejected"),
    ]
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='order_payment_refund'
    )
    payment = models.ForeignKey(
        OrderPayment,
        on_delete=models.CASCADE,
        related_name="refunds"
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="refunds"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    refund_method = models.CharField(
        max_length=10,
        choices=REFUND_METHOD_CHOICES,
        default="wallet"
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="processed_refunds",
        help_text="Admin who processed refund"
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    def process_refund(self, admin_user):
        """
        Processes a refund. If the refund method is 'wallet', the amount is credited
        to the client's wallet. If it's 'external', the admin must manually confirm.
        """
        if self.status != "pending":
            raise ValidationError("Only pending refunds can be processed.")

        if self.amount > self.payment.discounted_amount:
            raise ValidationError("Refund amount cannot exceed the paid amount.")
        
        # Prevent multiple refunds on the same payment
        total_refunded = Refund.objects.filter(payment=self.payment, status="processed").aggregate(
            total=models.Sum("amount")
        )["total"] or 0

        if total_refunded + self.amount > self.payment.discounted_amount:
            raise ValidationError("Refund exceeds total paid amount.")

        if self.refund_method == "wallet":
            # Process refund to the wallet
            wallet = Wallet.objects.get(user=self.client)
            wallet.balance += self.amount
            wallet.save()

            self.status = "processed"
            self.processed_by = admin_user
            self.processed_at = timezone.now()
            self.save()

            # Mark payment as refunded
            if total_refunded + self.amount >= self.payment.discounted_amount:
                self.payment.status = "refunded"
                self.payment.save()

        elif self.refund_method == "external":
            # Admin manually refunds externally (e.g., PayPal/Stripe)
            self.status = "processed"
            self.processed_by = admin_user
            self.processed_at = timezone.now()
            self.save()

            # Log external refund for tracking
            AdminLog.log_action(
                admin=admin_user,
                action="External Refund Processed",
                details=(
                    f"Refunded ${self.amount} externally for payment {self.payment.id}. "
                    f"Client: {self.client.username}."
                ),
            )

        # Log refund action for writer payments app to reference
        # Log the refund action
        PaymentLog.log_event(
            self.payment,
            "Refund Processed",
            f"Refund of ${self.amount} ({self.refund_method}) processed by {admin_user.username}."
        )

        self.log_refund_for_writer_app(admin_user)

    def log_refund_for_writer_app(self, admin_user):
        """
        Logs the refund event so the writer payments app can adjust payouts if needed.
        """
        AdminLog.log_action(
            admin=admin_user,
            action="Refund Logged for Writer Payments App",
            details=(
                f"Refund of ${self.amount} for client {self.client.id} "
                f"on order {self.payment.order.id}."
            ),
        )

    def __str__(self):
        return (
            f"Refund of ${self.amount} for {self.client.id} "
            f"({self.get_refund_method_display()})"
        )


class SplitPayment(models.Model):
    """
    Manages split payments where a client pays with multiple payment methods.
    Example: Half from wallet, half via card.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='split_order_payments'
    )
    payment = models.ForeignKey(
        "OrderPayment",
        on_delete=models.CASCADE,
        related_name="split_payments"
    )
    method = models.CharField(max_length=50)  # Card, Wallet, PayPal, etc.
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def process_split_payment(cls, payment, split_data):
        """Processes split payments using bulk create."""
        total_paid = sum(data['amount'] for data in split_data)
        if total_paid != payment.discounted_amount:
            raise ValueError("Total split payments do not match order amount.")

        split_payments = [cls(payment=payment, method=data['method'], amount=data['amount']) for data in split_data]
        cls.objects.bulk_create(split_payments)

        if total_paid == payment.discounted_amount:
            payment.mark_completed()



class AdminLog(models.Model):
    """
    Logs admin actions related to payments, disputes, and refunds.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='admin_log_payments'
    )
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="logs"
    )
    action = models.CharField(max_length=255)  # Example: "Refund Processed"
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField()

    @classmethod
    def log_action(cls, admin, action, details=""):
        """
        Creates a log entry for an admin action.
        """
        return cls.objects.create(admin=admin, action=action, details=details)
    

class PaymentReminderSettings(models.Model):
    """
    Allows admins to customize reminder messages and intervals for unpaid orders.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='order_payment_reminders'
    )
    first_reminder_hours = models.PositiveIntegerField(
        default=12, help_text="Hours before expiration for the first reminder."
    )
    final_reminder_hours = models.PositiveIntegerField(
        default=3, help_text="Hours before expiration for the final reminder."
    )
    first_reminder_message = models.TextField(
        default="Your order payment is still pending. Please complete it to avoid cancellation.",
        help_text="Message for the first reminder email/notification."
    )
    final_reminder_message = models.TextField(
        default="Your order payment will expire soon. Complete payment now to prevent cancellation.",
        help_text="Message for the final reminder email/notification."
    )
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="payment_reminder_settings", help_text="Admin who last updated the settings."
    )
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Payment Reminder Settings"

    class Meta:
        verbose_name = "Payment Reminder Setting"
        verbose_name_plural = "Payment Reminder Settings"

class RequestPayment(models.Model):
    """
    Model to track payment for requests like page increases, slide increases,
    or deadline extensions.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='payment_requests_order'
    )
    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE
    )
    payment_method = models.CharField(max_length=50)  # e.g., 'wallet', 'credit_card'
    additional_cost = models.DecimalField(max_digits=10, decimal_places=2,
                                          default=0.00)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_for = models.CharField(max_length=100)  # Page/Slide Increase, Deadline Extension, etc.

    def __str__(self):
        """
        Return a string representation of the payment record.

        Returns:
            str: A summary of the payment for the request.
        """
        return f"Request Payment for Order {self.order.id} ({self.payment_for})"
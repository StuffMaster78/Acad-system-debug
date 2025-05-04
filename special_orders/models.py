from django.db import models
from django.conf import settings
from websites.models import Website

class PredefinedSpecialOrderConfig(models.Model):
    """
    Configuration for predefined-cost special orders.
    These are the orders with predefined amount such as $250 etc.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='website_settings'
    )
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Name of the predefined order type (e.g., Shadow Health)."
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the predefined order type."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates whether this predefined order type is active."
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="predefined_special_order_configs",
        help_text="Website for which this configuration is valid."
    )
    
    def __str__(self):
        return f"{self.name} - Active: {self.is_active}"


class PredefinedSpecialOrderDuration(models.Model):
    """
    Represents the pricing for different durations of a predefined special order.
    """
    predefined_order = models.ForeignKey(
        PredefinedSpecialOrderConfig,
        on_delete=models.CASCADE,
        related_name="durations",
        help_text="The predefined order this pricing is associated with."
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='pdo_duration'
    )
    duration_days = models.PositiveIntegerField(
        help_text="Number of days for the special order (e.g., 3, 5, 10)."
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price for the special order based on the duration."
    )

    class Meta:
        unique_together = ('predefined_order', 'duration_days')

    def __str__(self):
        return f"{self.predefined_order.name} - {self.duration_days} days - ${self.price}"


class SpecialOrder(models.Model):
    """
    Model for handling special orders with predefined or estimated costs.
    """
    ORDER_TYPE_CHOICES = [
        ('predefined', 'Predefined Cost'),
        ('estimated', 'Estimated Cost'),
    ]
    STATUS_CHOICES = [
        ('inquiry', 'Inquiry Submitted'),
        ('awaiting_approval', 'Awaiting Approval'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="special_orders"
    )
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_special_orders",
        limit_choices_to={'role': 'writer'}
    )
    order_type = models.CharField(
        max_length=20,
        choices=ORDER_TYPE_CHOICES,
        default='estimated'
    )
    predefined_type = models.ForeignKey(
        PredefinedSpecialOrderConfig,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="special_orders"
    )
    inquiry_details = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    total_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    deposit_required = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    is_approved = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='inquiry'
    )
    duration_days = models.PositiveIntegerField(
        help_text="Number of days for the special order (e.g., 2, 3, 10)."
    )
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name="special_orders",
        help_text="Website associated with this special order."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Admin Override Controls
    admin_marked_paid = models.BooleanField(
        default=False,
        help_text="Has the admin manually marked this order as paid?"
    )
    admin_unlocked_files = models.BooleanField(
        default=False,
        help_text="Has the admin manually unlocked file downloads?"
    )
    writer_completed_no_files = models.BooleanField(
        default=False,
        help_text="Did the writer complete the order without uploading files?"
    )
    
    def save(self, *args, **kwargs):
        if self.order_type == 'predefined' and self.predefined_type:
            # Get the price for the selected duration
            duration_price = self.predefined_type.durations.filter(duration_days=self.duration_days).first()
            if duration_price:
                self.total_cost = duration_price.price
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Special Order #{self.id}"
    

class InstallmentPayment(models.Model):
    """
    Tracks installment payments for special orders.
    """
    special_order = models.ForeignKey(
        SpecialOrder,
        on_delete=models.CASCADE,
        related_name="installments"
    )
    due_date = models.DateField(
        help_text="Date when the installment is due."
    )
    amount_due = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Amount for this installment."
    )
    is_paid = models.BooleanField(
        default=False,
        help_text="Indicates whether this installment is paid."
    )

    def __str__(self):
        return f"Installment {self.id} for Order #{self.special_order.id} - Due: {self.due_date} - Paid: {self.is_paid}"


class OrderCompletionLog(models.Model):
    """
    Logs admin and writer actions when completing orders manually.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='pdo_completion_log'
    )
    special_order = models.ForeignKey(
        SpecialOrder,
        on_delete=models.CASCADE,
        related_name="completion_logs"
    )
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="order_completions"
    )
    completion_method = models.CharField(
        max_length=50,
        choices=[
            ('admin_marked_paid', 'Admin Marked as Paid'),
            ('admin_unlocked_files', 'Admin Unlocked File Access'),
            ('writer_completed_no_files', 'Writer Marked Complete (No Files)'),
        ],
        help_text="Completion method used."
    )
    justification = models.TextField(
        blank=True,
        help_text="Reason for order completion."
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.completed_by.username} - {self.completion_method} on Order #{self.special_order.id}"


class WriterBonus(models.Model):
    """
    Bonuses for writers tied to special orders.
    """
    website = models.ForeignKey(
        Website,
        on_delete=models.CASCADE,
        related_name='writer_bonus'
    )
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'writer'}
    )
    special_order = models.ForeignKey(
        SpecialOrder,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="bonuses"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    category = models.CharField(
        max_length=50,
        choices=[
            ('performance', 'Outstanding Performance'),
            ('order_completion', 'Order Completion'),
            ('client_tip', 'Client Tip'),
            ('other', 'Other'),
        ],
        default='client_tip'
    )
    reason = models.TextField(blank=True)
    is_paid = models.BooleanField(default=False)
    granted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bonus of ${self.amount} to {self.writer} (Category: {self.category})"
from django.db import models
from django.conf import settings
from core.models import WebsiteSpecificBaseModel


class PredefinedSpecialOrderConfig(WebsiteSpecificBaseModel):
    """
    Configuration for predefined-cost special orders.
    """
    name = models.CharField(max_length=255, unique=True, help_text="Name of the predefined order type.")
    description = models.TextField(blank=True, help_text="Description of the predefined order type.")
    cost = models.DecimalField(max_digits=10, decimal_places=2, help_text="Fixed cost for this order type.")
    is_active = models.BooleanField(default=True, help_text="Indicates whether this predefined order type is active.")

    def __str__(self):
        return f"{self.name} - ${self.cost}"


class SpecialOrder(WebsiteSpecificBaseModel):
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
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="special_orders")
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_special_orders",
        limit_choices_to={'role': 'writer'}
    )
    order_type = models.CharField(max_length=20, choices=ORDER_TYPE_CHOICES, default='estimated')
    predefined_type = models.ForeignKey(
        PredefinedSpecialOrderConfig,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="special_orders"
    )
    inquiry_details = models.TextField(blank=True)
    admin_notes = models.TextField(blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    deposit_required = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inquiry')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.order_type == 'predefined' and self.predefined_type:
            self.total_cost = self.predefined_type.cost
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Special Order #{self.id}"


class Milestone(WebsiteSpecificBaseModel):
    """
    Milestones for special orders.
    """
    special_order = models.ForeignKey(SpecialOrder, on_delete=models.CASCADE, related_name="milestones")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Milestone '{self.name}' for Special Order #{self.special_order.id}"


class ProgressLog(WebsiteSpecificBaseModel):
    """
    Progress logs recorded by writers for special orders.
    """
    special_order = models.ForeignKey(SpecialOrder, on_delete=models.CASCADE, related_name="progress_logs")
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'writer'}
    )
    description = models.TextField()
    milestone = models.ForeignKey(Milestone, on_delete=models.SET_NULL, null=True, blank=True, related_name="progress_logs")
    attachments = models.FileField(upload_to="progress_logs/", null=True, blank=True)
    progress_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Progress for Order #{self.special_order.id}"


class WriterBonus(WebsiteSpecificBaseModel):
    """
    Bonuses for writers tied to special orders or milestones.
    """
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'writer'}
    )
    special_order = models.ForeignKey(SpecialOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name="bonuses")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(
        max_length=50,
        choices=[
            ('milestone', 'Milestone Completion'),
            ('performance', 'Outstanding Performance'),
            ('other', 'Other'),
        ],
        default='milestone'
    )
    reason = models.TextField(blank=True)
    is_paid = models.BooleanField(default=False)
    granted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bonus of ${self.amount} to {self.writer}"
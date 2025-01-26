from django.db import models
from core.models.base import WebsiteSpecificBaseModel
from discounts.models import Discount
from users.models import User


class Order(WebsiteSpecificBaseModel):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('available', 'Available'),
        ('unpaid', 'Unpaid'),
        ('critical', 'Critical'),
        ('late', 'Late'),
        ('in_progress', 'In Progress'),
        ('revision', 'Revision'),
        ('disputed', 'Disputed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('archived', 'Archived'),
        ('paid', 'Paid'),
    ]

    TYPE_OF_WORK_CHOICES = [
        ('writing', 'Writing'),
        ('editing', 'Editing'),
        ('rewriting', 'Rewriting'),
    ]

    title = models.CharField(max_length=255, help_text="Title of the order")
    topic = models.CharField(max_length=255, help_text="Topic of the work")
    instructions = models.TextField(help_text="Detailed instructions provided by the client")
    academic_level = models.CharField(max_length=50, help_text="Academic level required")
    subject = models.CharField(max_length=100)
    type_of_work = models.CharField(max_length=20, choices=TYPE_OF_WORK_CHOICES, help_text="Type of work required")
    number_of_pages = models.PositiveIntegerField(default=1, help_text="Number of pages required")
    number_of_slides = models.PositiveIntegerField(default=0, help_text="Number of slides required (if applicable)")
    client_deadline = models.DateTimeField(help_text="Deadline specified by the client")
    writer_deadline = models.DateTimeField(null=True, blank=True, help_text="Deadline for the writer (buffered)")
    client = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="client_orders", help_text="Client placing the order"
    )
    assigned_writer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="writer_orders",
        null=True,
        blank=True,
        help_text="Writer assigned to the order",
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total price for the order")
    additional_services = models.JSONField(default=dict, blank=True, help_text="Additional services selected by the client")
    discount_code = models.ForeignKey(
        Discount, on_delete=models.SET_NULL, null=True, blank=True, help_text="Discount code applied to the order"
    )
    tips = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Tips provided by the client")
    payment_status = models.CharField(
        max_length=20,
        choices=[('paid', 'Paid'), ('unpaid', 'Unpaid'), ('partial', 'Partial')],
        default='unpaid',
        help_text="Payment status of the order",
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', help_text="Current status of the order")
    revision_requested = models.BooleanField(default=False, help_text="Indicates if a revision has been requested")
    date_posted = models.DateTimeField(auto_now_add=True, help_text="Date when the order was posted")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="Date when the order was completed")
    is_high_value = models.BooleanField(default=False, help_text="Flag for high-value orders")
    is_urgent = models.BooleanField(default=False, help_text="Flag for urgent orders")

    class Meta:
        ordering = ['-date_posted']

    def __str__(self):
        return f"Order #{self.id} - {self.title} ({self.website.name})"
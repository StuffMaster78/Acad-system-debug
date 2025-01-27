from django.db import models
from django.utils.translation import gettext_lazy as _
from users.models import User
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated


class WriterLevel(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text=_("Name of the writer level."))
    base_pay_per_page = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    tip_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    max_orders = models.PositiveIntegerField(default=10)
    min_orders = models.PositiveIntegerField(default=0)
    min_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.name} (Base Pay: ${self.base_pay_per_page}, Max Orders: {self.max_orders})"


class PaymentHistory(models.Model):
    writer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="payment_history", limit_choices_to={'role': 'writer'}
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, help_text=_("Total payment amount."))
    bonuses = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text=_("Bonuses received."))
    fines = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text=_("Fines deducted."))
    tips = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text=_("Tips received."))
    payment_date = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Payment of ${self.amount} to {self.writer.username} on {self.payment_date}"


class WriterProgress(models.Model):
    writer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="progress_logs", limit_choices_to={'role': 'writer'}
    )
    order = models.ForeignKey(
        'orders.Order', on_delete=models.CASCADE, related_name="progress_logs"
    )
    progress = models.PositiveIntegerField(help_text=_("Progress percentage (0-100)."))
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Progress {self.progress}% for Order {self.order.id} by {self.writer.username}"


class WriterAvailability(models.Model):
    writer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="availability", limit_choices_to={'role': 'writer'}
    )
    start_time = models.DateTimeField(help_text=_("Start of availability period."))
    end_time = models.DateTimeField(help_text=_("End of availability period."))
    is_recurring = models.BooleanField(default=False, help_text=_("If True, this schedule repeats weekly."))

    def __str__(self):
        return f"Availability: {self.writer.username} ({self.start_time} - {self.end_time})"


class WriterPerformance(models.Model):
    writer = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="performance", limit_choices_to={'role': 'writer'}
    )
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, help_text=_("Average rating."))
    on_time_delivery_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, help_text=_("On-time delivery rate in percentage."))
    late_submissions = models.PositiveIntegerField(default=0, help_text=_("Number of late submissions."))
    total_orders = models.PositiveIntegerField(default=0, help_text=_("Total orders completed."))

    def __str__(self):
        return f"Performance for {self.writer.username}"

class WriterOrderAssignment(models.Model):
    writer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="assigned_orders", limit_choices_to={'role': 'writer'}
    )
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name="writer_assignments")
    status = models.CharField(
        max_length=20,
        choices=(
            ('Pending', 'Pending'),
            ('In Progress', 'In Progress'),
            ('Completed', 'Completed'),
            ('Cancelled', 'Cancelled')
        ),
        default='Pending'
    )
    assigned_date = models.DateTimeField(auto_now_add=True)
    completed_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.order.id} assigned to {self.writer.username} ({self.status})"


class WriterReview(models.Model):
    writer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reviews", limit_choices_to={'role': 'writer'}
    )
    client = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'client'})
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name="writer_reviews")
    rating = models.PositiveIntegerField(help_text=_("Rating given by the client (1-5)."))
    feedback = models.TextField(blank=True, null=True, help_text=_("Optional feedback from the client."))
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.writer.username} by {self.client.username} (Rating: {self.rating})"


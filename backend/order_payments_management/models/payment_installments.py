from django.db import models
from django.conf import settings


class PaymentInstallment(models.Model):
    """
    Represents a scheduled or completed installment toward an invoice.

    Attributes:
        invoice: The invoice this installment is part of.
        amount: Scheduled installment amount.
        due_date: When payment is due.
        paid_at: When it was actually paid.
        payment: Linked PaymentRecord if paid.
        status: Current status of the installment.
        notes: Any additional context (e.g., late reason).
        created_at: Timestamp of creation.
    """

    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("paid", "Paid"),
        ("late", "Late"),
        ("cancelled", "Cancelled"),
    ]

    invoice = models.ForeignKey(
        "Invoice", on_delete=models.CASCADE,
        related_name="installments"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    paid_at = models.DateTimeField(null=True, blank=True)
    payment = models.OneToOneField(
        "PaymentRecord", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="installment"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="scheduled"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Installment {self.amount} | {self.status}"

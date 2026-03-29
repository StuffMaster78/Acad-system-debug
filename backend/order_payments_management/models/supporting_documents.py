import uuid
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
from websites.models.websites import Website
from order_payments_management.models.logs import PaymentLog


class PaymentSupportingDocument(models.Model):
    """
    File attachments to support a payment request, such as quotes,
    contracts, approvals, or invoices.

    Attributes:
        invoice: Optional related invoice.
        uploaded_by: User who uploaded the file.
        file: The actual uploaded document.
        document_type: Type of document (e.g., quote, approval).
        description: Additional context or notes.
        uploaded_at: Timestamp of upload.
    """

    DOCUMENT_TYPE_CHOICES = [
        ("quote", "Quote"),
        ("contract", "Contract"),
        ("invoice", "Invoice"),
        ("memo", "Internal Memo"),
        ("receipt", "Previous Receipt"),
        ("other", "Other"),
        ("driving_license", "Driving License"),
        ("passport", "Passport"),
        ("id_card", "ID Card"),
        ("bank_statement", "Bank Statement"),
        ("tax_document", "Tax Document"),
        ("w9_form", "W-9 Form"),
        ("w8_ben_form", "W-8 BEN Form"),
        ("payment_proof", "Payment Proof"),
        ("business_license", "Business License"),
        ("employment_letter", "Employment Letter"),
        ("other_document", "Other Document"),
    ]

    invoice = models.ForeignKey(
        "Invoice", on_delete=models.CASCADE,
        related_name="supporting_documents"
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        help_text="User who uploaded the document",
        related_name="payment_proof_uploaded_documents"
    )
    file = models.FileField(upload_to="payments/supporting_documents/")
    document_type = models.CharField(
        max_length=20, choices=DOCUMENT_TYPE_CHOICES, default="other"
    )
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_type} for Invoice {self.invoice.reference_id}"

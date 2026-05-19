from payments_processor.enums import PaymentIntentPurpose
from payments_processor.enums import PaymentIntentStatus
from payments_processor.models import PaymentIntent as OrderPayment

STATUS_CHOICES = PaymentIntentStatus.choices
PAYMENT_TYPE_CHOICES = PaymentIntentPurpose.choices

__all__ = ["OrderPayment", "PAYMENT_TYPE_CHOICES", "STATUS_CHOICES"]

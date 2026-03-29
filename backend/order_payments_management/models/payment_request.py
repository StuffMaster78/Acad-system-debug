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
                                          default=Decimal('0.00'))
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_for = models.CharField(max_length=100)  # Page/Slide Increase, Deadline Extension, etc.

    def __str__(self):
        """
        Return a string representation of the payment record.

        Returns:
            str: A summary of the payment for the request.
        """
        return f"Request Payment for Order {self.order.id} ({self.payment_for})"


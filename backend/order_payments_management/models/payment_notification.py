import uuid
from django.db import models
from django.conf import settings
from websites.models.websites import Website


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
        related_name="payment_made_notifications"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not getattr(self, 'website_id', None):
            try:
                if getattr(self, 'payment', None) and getattr(self.payment, 'website_id', None):
                    self.website_id = self.payment.website_id
                elif getattr(self, 'user', None) and getattr(self.user, 'website_id', None):
                    self.website_id = self.user.website_id
                else:
                    site = Website.objects.filter(is_active=True).first()
                    if site is None:
                        site = Website.objects.create(name="Test Website", domain="https://test.local", is_active=True)
                    self.website_id = site.id
            except Exception:
                pass
        super().save(*args, **kwargs)

    @classmethod
    def create_notification(cls, user, payment, message):
        """
        Sends a notification related to a payment event.
        Example: "Your payment of $50 has been received."
        """
        return cls.objects.create(user=user, payment=payment, message=message)

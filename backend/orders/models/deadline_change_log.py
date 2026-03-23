from datetime import timedelta
from decimal import Decimal

from django.apps import apps
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import (
    MinValueValidator, MaxValueValidator
)
from datetime import timedelta
from django.db import models
from orders.models.orders import Order


User = settings.AUTH_USER_MODEL 



class DeadlineChangeLog(models.Model):
    """
    Logs every deadline change for audit.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='deadline_change_log'
    ) 
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    old_deadline = models.DateTimeField()
    new_deadline = models.DateTimeField()
    changed_by = models.ForeignKey(
        'users.User', on_delete=models.CASCADE,
        related_name='deadline_changes',
        help_text="User who changed the deadline."
    )
    reason = models.TextField()

    def __str__(self):
        return f"Deadline changed for Order #{self.order.id}"

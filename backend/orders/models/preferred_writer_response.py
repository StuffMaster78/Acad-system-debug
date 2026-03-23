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
from django.utils import timezone
from orders.models.orders import Order
from django.contrib.postgres.fields import ArrayField
from django.utils.timezone import now
from django.utils.text import slugify

User = settings.AUTH_USER_MODEL 

# # Use apps.get_model() to access Website model lazily
# def get_website_model():
#     Website = apps.get_model('websites', 'Website')
#     return Website

# Website = get_website_model()

# from writer_management.models import wr

class PreferredWriterResponse(models.Model):
    """
    Handles the preferred writer's response when declining
    to work on an order.
    """
    website = models.ForeignKey(
        'websites.Website',
        on_delete=models.CASCADE,
        related_name='preferred_writer_decline_response'
    ) 
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    writer = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='preferred_writer_responses',
    )
    response = models.CharField(
        max_length=10,
        choices=[('accepted', 'Accepted'), ('declined', 'Declined')]
    )
    reason = models.TextField(blank=True, null=True)
    responded_at = models.DateTimeField(auto_now_add=True)
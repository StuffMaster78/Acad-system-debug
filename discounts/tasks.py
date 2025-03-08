from core.celery import shared_task
from django.utils.timezone import now
from .models import Discount

@shared_task
def deactivate_expired_discounts():
    """Automatically deactivate discounts that have expired."""
    expired_discounts = Discount.objects.filter(is_active=True, end_date__lt=now())
    expired_discounts.update(is_active=False)
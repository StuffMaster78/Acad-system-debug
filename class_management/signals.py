# class_management/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from class_management.models import ClassPurchase
from communications.models import MessageThread
from tickets.models import SupportTicket

@receiver(post_save, sender=ClassPurchase)
def create_related_entities(sender, instance, created, **kwargs):
    if created:
        MessageThread.objects.create(order=instance, created_by=instance.client)
        SupportTicket.objects.create(
            related_object=instance,
            topic='New class purchase',
            created_by=instance.client
        )
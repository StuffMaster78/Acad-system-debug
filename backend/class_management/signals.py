# class_management/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from class_management.models import ClassPurchase
from communications.models import CommunicationThread
from tickets.models import Ticket as SupportTicket

@receiver(post_save, sender=ClassPurchase)
def create_related_entities(sender, instance, created, **kwargs):
    if created:
        CommunicationThread.objects.create(order=instance, created_by=instance.client)
        SupportTicket.objects.create(
            related_object=instance,
            topic='New class purchase',
            created_by=instance.client
        )
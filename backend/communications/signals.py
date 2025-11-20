from django.db.models.signals import post_save
from django.dispatch import receiver
from communications.models import CommunicationMessage
from communications.tasks import generate_link_preview_task

@receiver(post_save, sender=CommunicationMessage)
def trigger_link_preview(sender, instance, created, **kwargs):
    if created and instance.link_url and not instance.preview_failed_at:
        generate_link_preview_task.delay(instance.id)

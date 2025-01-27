from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import User
from .models import WriterLevel


@receiver(post_save, sender=User)
def assign_default_writer_level(sender, instance, created, **kwargs):
    if created and instance.role == 'writer':
        default_level = WriterLevel.objects.first()  # Assign the first available level as default
        instance.writer_level = default_level
        instance.save()
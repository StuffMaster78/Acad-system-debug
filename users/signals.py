from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User

@receiver(post_save, sender=User)
def assign_default_role(sender, instance, created, **kwargs):
    """
    Assign a default role to newly created users.
    """
    if created and not instance.role:
        instance.role = 'client'
        instance.save()
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User

@receiver(post_save, sender=User)
def set_default_role_behavior(sender, instance, created, **kwargs):
    """
    Handle role-specific defaults when a user is created.
    """
    if created:
        if instance.role == 'client':
            # Set default avatar for clients
            if not instance.avatar:
                instance.avatar = 'avatars/male1.png'
            # Perform additional client setup if necessary

        elif instance.role == 'writer':
            # Set writer-specific defaults
            instance.completed_orders = 0
            instance.rating = 0.0

        elif instance.role == 'editor':
            # Set editor-specific defaults
            instance.edited_orders = 0

        elif instance.role == 'support':
            # Set support-specific defaults
            instance.handled_tickets = 0
            instance.resolved_orders = 0

        # Save the user instance after setting defaults
        instance.save()

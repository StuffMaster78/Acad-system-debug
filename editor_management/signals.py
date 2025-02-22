from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import EditorProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_editor_profile(sender, instance, created, **kwargs):
    """
    Automatically create an EditorProfile when a user with the role 'editor' is created.
    """
    if created and instance.role == "editor":
        EditorProfile.objects.create(user=instance, name=instance.username)
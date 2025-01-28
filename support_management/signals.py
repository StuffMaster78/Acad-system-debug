from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.utils.timezone import now
from .models import SupportProfile, SupportActivityLog
from websites.models import Website
from .utils import send_support_notification
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def create_support_profile(sender, instance, created, **kwargs):
    """
    Automatically create a SupportProfile when a new user with a 'support' role is created.
    """
    if created and instance.role == "support":
        default_website = Website.objects.first()  # Assign the first website as default
        SupportProfile.objects.create(
            user=instance,
            name=instance.username,
            registration_id=f"Support #{instance.id:05d}",
            email=instance.email,
            website=default_website,
        )


@receiver(user_logged_in)
def update_last_logged_in(sender, request, user, **kwargs):
    """
    Update the last_logged_in field for support staff upon login.
    """
    if user.role == "support":
        support_profile = user.support_profile
        support_profile.last_logged_in = now()
        support_profile.save()


@receiver(post_save, sender=SupportProfile)
def log_profile_creation(sender, instance, created, **kwargs):
    """
    Log the creation of a SupportProfile.
    """
    if created:
        SupportActivityLog.objects.create(
            support_staff=instance,
            activity=f"Support profile created for {instance.name}."
        )


@receiver(post_save, sender=SupportActivityLog)
def send_activity_notification(sender, instance, **kwargs):
    """
    Send a notification to support staff when a new activity log is created.
    """
    message = f"New activity logged: {instance.activity[:50]}..."
    send_support_notification(instance.support_staff, message)
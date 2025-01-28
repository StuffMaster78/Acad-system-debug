from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from .models import WriterProfile, WriterActionLog
from core.utils import get_geolocation_from_ip  # Assuming this is now in the `core` app

User = get_user_model()

# Signal to create a WriterProfile when a new writer user is created
@receiver(post_save, sender=User)
def create_writer_profile(sender, instance, created, **kwargs):
    """
    Automatically create a WriterProfile for a user with the 'writer' role.
    """
    if created and instance.role == "writer":
        WriterProfile.objects.create(user=instance)
        print(f"WriterProfile created for user: {instance.username}")


# Signal to track writer login and update geolocation
@receiver(user_logged_in)
def update_writer_geolocation(sender, request, user, **kwargs):
    """
    Fetch and update geolocation data for the writer on login.
    """
    if user.role == "writer":
        try:
            writer_profile = user.writer_profile
            ip_address = get_client_ip(request)  # Fetch client IP address
            geo_data = get_geolocation_from_ip(ip_address)  # Fetch geolocation data

            if "error" not in geo_data:
                writer_profile.country = geo_data.get("country")
                writer_profile.timezone = geo_data.get("timezone")
                writer_profile.ip_address = ip_address
                writer_profile.location_verified = True
                writer_profile.save()
                print(f"Updated geolocation for writer: {user.username}")
        except WriterProfile.DoesNotExist:
            print(f"No WriterProfile found for user: {user.username}")


# Signal to log actions when a writer's profile is updated
@receiver(post_save, sender=WriterProfile)
def log_writer_action(sender, instance, created, **kwargs):
    """
    Log any updates to the WriterProfile as actions.
    """
    if not created:
        action = f"Writer profile updated for {instance.user.username}."
        WriterActionLog.objects.create(
            writer=instance,
            action="profile_update",
            reason=action
        )
        print(action)


# Signal to clean up data when a writer user is deleted
@receiver(pre_delete, sender=User)
def delete_writer_profile(sender, instance, **kwargs):
    """
    Automatically delete associated WriterProfile when a writer user is deleted.
    """
    if instance.role == "writer":
        try:
            writer_profile = instance.writer_profile
            writer_profile.delete()
            print(f"WriterProfile deleted for user: {instance.username}")
        except WriterProfile.DoesNotExist:
            print(f"No WriterProfile found for user: {instance.username}")


# Utility function to get the client's IP address
def get_client_ip(request):
    """
    Get the client's IP address from the request headers.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")
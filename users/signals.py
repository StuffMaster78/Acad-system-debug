from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import User
from client_management.models import ClientProfile
from writer_management.models import WriterProfile
from editor_management.models import EditorProfile
from support_management.models import SupportProfile
from core.utils.location import get_geolocation_from_ip
from django.utils.timezone import now


@receiver(post_save, sender=User)
def create_role_based_profiles(sender, instance, created, **kwargs):
    """
    Automatically create profiles for specific roles when a new user is created.
    """
    if created:
        if instance.role == 'client':
            ClientProfile.objects.create(user=instance)
        elif instance.role == 'writer':
            WriterProfile.objects.create(user=instance)
        elif instance.role == 'editor':
            EditorProfile.objects.create(user=instance)
        elif instance.role == 'support':
            SupportProfile.objects.create(user=instance)


@receiver(user_logged_in)
def update_user_geolocation(sender, request, user, **kwargs):
    """
    Update geolocation information when a user logs in.
    """
    try:
        ip_address = get_client_ip(request)
        geo_data = get_geolocation_from_ip(ip_address)
        if geo_data.get("error"):
            return

        user.last_active = now()
        user.ip_address = ip_address
        user.save()

        # Role-specific geolocation updates
        if user.role == 'client' and hasattr(user, 'client_profile'):
            user.client_profile.country = geo_data.get("country", user.client_profile.country)
            user.client_profile.timezone = geo_data.get("timezone", user.client_profile.timezone)
            user.client_profile.save()
        elif user.role == 'writer' and hasattr(user, 'writer_profile'):
            user.writer_profile.country = geo_data.get("country", user.writer_profile.country)
            user.writer_profile.timezone = geo_data.get("timezone", user.writer_profile.timezone)
            user.writer_profile.save()

    except Exception as e:
        print(f"Error updating geolocation: {e}")


def get_client_ip(request):
    """
    Retrieve the client's IP address from the request headers.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')
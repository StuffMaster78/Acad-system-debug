from django.db.models.signals import (
    post_save, pre_delete, post_delete
)
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.utils.timezone import now
from .models.profile import WriterProfile
from models.logs import WriterActionLog
from core.utils.location import get_geolocation_from_ip
from models.payout import CurrencyConversionRate
from django.core.cache import cache
from writer_management.services.conversion_service import CurrencyConversionService

from writer_management.services.status_service import WriterStatusService
from writer_management.models.discipline import (
    WriterStrike, WriterSuspension, WriterBlacklist, Probation
)

User = get_user_model()


### ---------------- Writer Profile Signals ---------------- ###

@receiver(post_save, sender=User)
def create_writer_profile(sender, instance, created, **kwargs):
    """
    Automatically create a WriterProfile for new users with the 'writer' role.
    """
    if created and instance.role == "writer":
        WriterProfile.objects.create(user=instance)
        print(f"✅ WriterProfile created for {instance.username}")


@receiver(post_save, sender=WriterProfile)
def log_writer_action(sender, instance, created, **kwargs):
    """
    Log writer profile updates as actions.
    """
    if not created:
        action = f"✏️ Writer profile updated for {instance.user.username}."
        WriterActionLog.objects.create(
            writer=instance,
            action="profile_update",
            reason=action
        )
        print(action)


@receiver(pre_delete, sender=User)
def delete_writer_profile(sender, instance, **kwargs):
    """
    Automatically delete associated WriterProfile when a writer user is deleted.
    """
    if instance.role == "writer":
        try:
            writer_profile = instance.writer_profile
            writer_profile.delete()
            print(f"❌ WriterProfile deleted for {instance.username}")
        except WriterProfile.DoesNotExist:
            print(f"⚠️ No WriterProfile found for {instance.username}")


### ---------------- Writer Login Tracking Signals ---------------- ###

@receiver(user_logged_in)
def update_writer_geolocation(sender, request, user, **kwargs):
    """
    Fetch and update geolocation data for the writer upon login.
    """
    if user.role == "writer":
        try:
            writer_profile = user.writer_profile
            ip_address = get_client_ip(request)  # Fetch client IP address
            geo_data = get_geolocation_from_ip(ip_address)  # Fetch geolocation data

            if "error" not in geo_data:
                writer_profile.country = geo_data.get("country", writer_profile.country)
                writer_profile.timezone = geo_data.get("timezone", writer_profile.timezone)
                writer_profile.ip_address = ip_address
                writer_profile.location_verified = True
                writer_profile.last_logged_in = now()
                writer_profile.save()
                print(f"🌍 Updated geolocation for writer: {user.username} (IP: {ip_address})")

        except WriterProfile.DoesNotExist:
            print(f"⚠️ No WriterProfile found for {user.username}")


### ---------------- Order Assignment & Management Signals ---------------- ###

@receiver(post_save, sender=User)
def auto_update_writer_profile(sender, instance, **kwargs):
    """
    Automatically update WriterProfile when a writer's user instance is updated.
    """
    if instance.role == "writer":
        try:
            writer_profile = instance.writer_profile
            writer_profile.last_logged_in = now()
            writer_profile.save()
            print(f"🔄 WriterProfile auto-updated for {instance.username}")
        except WriterProfile.DoesNotExist:
            print(f"⚠️ No WriterProfile found for {instance.username}")


@receiver(post_save, sender=WriterProfile)
def enforce_writer_take_limits(sender, instance, **kwargs):
    """
    Enforce max order takes and requests per writer.
    """
    if instance.number_of_takes > instance.writer_level.max_orders:
        instance.number_of_takes = instance.writer_level.max_orders
        instance.save()
        print(f"⚠️ Order take limit enforced for {instance.user.username}")


### ---------------- Utility Functions ---------------- ###

def get_client_ip(request):
    """
    Retrieve the client's IP address from the request headers.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")

@receiver([post_save, post_delete], sender=WriterStrike)
@receiver([post_save, post_delete], sender=WriterSuspension)
@receiver([post_save, post_delete], sender=WriterBlacklist)
@receiver([post_save, post_delete], sender=Probation)
def invalidate_writer_status_cache(sender, instance, **kwargs):
    """Invalidate the cache for the writer's status
    when any discipline-related model is saved or deleted.
    """
    WriterStatusService.clear_cache(instance.writer)



@receiver(post_save, sender=CurrencyConversionRate)
def clear_cached_conversion_rate(sender, instance, **kwargs):
    key = CurrencyConversionService._cache_key(
        instance.website.id, instance.target_currency
    )
    cache.delete(key)

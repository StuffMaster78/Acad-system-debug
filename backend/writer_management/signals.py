from django.db.models.signals import (
    post_save, pre_delete, post_delete, pre_save
)
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.utils.timezone import now
from .models.profile import WriterProfile
from .models.logs import WriterActionLog
from core.utils.location import get_geolocation_from_ip
from .models.payout import CurrencyConversionRate
from django.core.cache import cache
from writer_management.services.conversion_service import CurrencyConversionService

from writer_management.services.status_service import WriterStatusService
from writer_management.models.discipline import (
    WriterStrike, WriterSuspension, WriterBlacklist, Probation
)
from writer_management.models.writer_warnings import WriterWarning
from writer_management.models.rewards import WriterReward
from writer_management.services.discipline_notification_service import (
    DisciplineNotificationService,
)

User = get_user_model()


### ---------------- Writer Profile Signals ---------------- ###

# @receiver(post_save, sender=User)
# def create_writer_profile(sender, instance, created, **kwargs):
#     """
#     Automatically create a WriterProfile for new users with the 'writer' role.
#     """
#     if created and instance.role == "writer":
#         WriterProfile.objects.create(user=instance)
#         print(f"✅ WriterProfile created for {instance.username}")
# 
# NOTE: This signal is disabled because WriterProfile creation is now handled
# in users/signals.py with proper website and wallet creation


@receiver(post_save, sender=WriterProfile)
def log_writer_action(sender, instance, created, **kwargs):
    """
    Log writer profile updates as actions.
    """
    if not created:
        action = f"✏️ Writer profile updated for {instance.user.username}."
        website = getattr(instance, 'website', None)
        if website is None:
            try:
                from websites.models import Website
                website = Website.objects.filter(is_active=True).first()
                if website is None:
                    website = Website.objects.create(name="Test Website", domain="https://test.local", is_active=True)
            except Exception:
                website = None
        WriterActionLog.objects.create(
            website=website,
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

# @receiver(post_save, sender=User)
# def auto_update_writer_profile(sender, instance, **kwargs):
#     """
#     Automatically update WriterProfile when a writer's user instance is updated.
#     """
#     if instance.role == "writer":
#         try:
#             writer_profile = instance.writer_profile
#             writer_profile.last_logged_in = now()
#             writer_profile.save()
#             print(f"🔄 WriterProfile auto-updated for {instance.username}")
#         except WriterProfile.DoesNotExist:
#             print(f"⚠️ No WriterProfile found for {instance.username}")
# 
# NOTE: This signal is disabled to prevent validation conflicts during user creation


@receiver(post_save, sender=WriterProfile)
def enforce_writer_take_limits(sender, instance, **kwargs):
    """
    Enforce max order takes and requests per writer.
    """
    if instance.writer_level and instance.number_of_takes > instance.writer_level.max_orders:
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


# ---------------- Discipline Notifications ---------------- #

@receiver(pre_save, sender=WriterWarning)
def store_previous_warning_state(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_is_active = None
        return
    try:
        instance._previous_is_active = (
            sender.objects.only("is_active").get(pk=instance.pk).is_active
        )
    except sender.DoesNotExist:
        instance._previous_is_active = None


@receiver(post_save, sender=WriterWarning)
def writer_warning_notifications(sender, instance, created, **kwargs):
    if created:
        DisciplineNotificationService.notify_warning_issued(instance)
        return
    prev_active = getattr(instance, "_previous_is_active", None)
    if prev_active and not instance.is_active:
        DisciplineNotificationService.notify_warning_resolved(
            instance, reason="resolved"
        )


@receiver(post_delete, sender=WriterWarning)
def writer_warning_deleted(sender, instance, **kwargs):
    if instance.writer:
        DisciplineNotificationService.notify_warning_resolved(
            instance, reason="removed"
        )


@receiver(post_save, sender=WriterStrike)
def writer_strike_created(sender, instance, created, **kwargs):
    if created:
        DisciplineNotificationService.notify_strike_issued(instance)


@receiver(post_delete, sender=WriterStrike)
def writer_strike_deleted(sender, instance, **kwargs):
    if instance.writer:
        DisciplineNotificationService.notify_strike_revoked(instance)


@receiver(pre_save, sender=WriterSuspension)
def store_previous_suspension_state(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_is_active = None
        return
    try:
        instance._previous_is_active = (
            sender.objects.only("is_active").get(pk=instance.pk).is_active
        )
    except sender.DoesNotExist:
        instance._previous_is_active = None


@receiver(post_save, sender=WriterSuspension)
def writer_suspension_notifications(sender, instance, created, **kwargs):
    if created:
        DisciplineNotificationService.notify_suspension_started(instance)
        return
    prev_active = getattr(instance, "_previous_is_active", None)
    if prev_active and not instance.is_active:
        DisciplineNotificationService.notify_suspension_lifted(instance)


@receiver(post_save, sender=Probation)
def writer_probation_notifications(sender, instance, created, **kwargs):
    if created:
        DisciplineNotificationService.notify_probation_started(instance)



@receiver(post_save, sender=CurrencyConversionRate)
def clear_cached_conversion_rate(sender, instance, **kwargs):
    key = CurrencyConversionService._cache_key(
        instance.website.id, instance.target_currency
    )
    cache.delete(key)


@receiver([post_save, pre_delete, pre_delete], sender=WriterReward)
def ensure_reward_website(sender, instance, **kwargs):
    try:
        if not getattr(instance, 'website_id', None):
            writer = getattr(instance, 'writer', None)
            if writer and getattr(writer, 'website_id', None):
                instance.website_id = writer.website_id
                try:
                    instance.save(update_fields=['website'])
                except Exception:
                    pass
    except Exception:
        pass

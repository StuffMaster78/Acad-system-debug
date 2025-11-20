from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from orders.models import Dispute
from .models import BlacklistedUser
from .services.admin_services import (
    create_admin_profile_if_needed,
    notify_superadmins_new_admin,
    promote_to_admin_if_needed,
    log_user_suspension_if_changed,
    notify_admins_new_dispute,
    notify_superadmins_blacklist,
    assign_admin_permissions
)

User = get_user_model()


@receiver(post_save, sender=User)
def on_user_created(sender, instance, created, **kwargs):
    if created:
        create_admin_profile_if_needed(instance)
        notify_superadmins_new_admin(instance)

@receiver(pre_save, sender=User)
def on_user_promotion_or_suspend(sender, instance, **kwargs):
    if not instance.pk:
        return

    old_user = User.objects.get(pk=instance.pk)
    if old_user.role != "admin" and instance.role == "admin":
        promote_to_admin_if_needed(instance)

    log_user_suspension_if_changed(instance, old_user)


@receiver(post_save, sender=Dispute)
def on_dispute_created(sender, instance, created, **kwargs):
    if created:
        notify_admins_new_dispute(instance)


@receiver(post_save, sender=BlacklistedUser)
def on_user_blacklisted(sender, instance, created, **kwargs):
    if created:
        notify_superadmins_blacklist(instance)

@receiver(pre_save, sender=BlacklistedUser)
def on_blacklist_update(sender, instance, **kwargs):
    if not instance.pk:
        return

    old_blacklist = BlacklistedUser.objects.get(pk=instance.pk)
    if old_blacklist.email != instance.email:
        raise ValueError("Email cannot be changed for a blacklisted user.") 
    if old_blacklist.website != instance.website:
        raise ValueError("Website cannot be changed for a blacklisted user.")
    if old_blacklist.blacklisted_by != instance.blacklisted_by:
        raise ValueError("Blacklisted by cannot be changed for a blacklisted user.")
@receiver(pre_save, sender=User)
def on_user_update(sender, instance, **kwargs):
    if not instance.pk:
        return

    old_user = User.objects.get(pk=instance.pk)
    if old_user.is_suspended != instance.is_suspended:
        log_user_suspension_if_changed(instance, old_user)
    
    if old_user.role != instance.role:
        if instance.role == "admin":
            promote_to_admin_if_needed(instance)
        elif old_user.role == "admin":
            # If demoting from admin, we might want to handle cleanup
            pass

@receiver(post_save, sender=User)
def on_user_save(sender, instance, created, **kwargs):
    if created:
        create_admin_profile_if_needed(instance)
        notify_superadmins_new_admin(instance)
    else:
        log_user_suspension_if_changed(instance, User.objects.get(pk=instance.pk))
    
    if instance.role == "admin":
        assign_admin_permissions(instance)
        notify_superadmins_new_admin(instance)
@receiver(pre_save, sender=BlacklistedUser)
def on_blacklist_pre_save(sender, instance, **kwargs):
    if not instance.pk:
        return

    old_blacklist = BlacklistedUser.objects.get(pk=instance.pk)
    if old_blacklist.email != instance.email:
        raise ValueError("Email cannot be changed for a blacklisted user.")
    if old_blacklist.website != instance.website:
        raise ValueError("Website cannot be changed for a blacklisted user.")
    if old_blacklist.blacklisted_by != instance.blacklisted_by:
        raise ValueError("Blacklisted by cannot be changed for a blacklisted user.")
    
@receiver(post_save, sender=BlacklistedUser)
def on_blacklist_created(sender, instance, created, **kwargs):
    if created:
        notify_superadmins_blacklist(instance)
    else:
        # Handle updates if needed
        pass
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from notifications_system.models import send_notification  # Import from Notifications App
from django.contrib.auth.models import Group, Permission
from django.apps import apps
from .models import AdminActivityLog, AdminProfile, BlacklistedUser
from admin_management.managers import AdminManager
from orders.models import Dispute

User = get_user_model()

# Ensure the function is imported before usage
def setup_permissions():
    from .managers import assign_admin_permissions
    assign_admin_permissions()



@receiver(post_save, sender=User)
def create_admin_profile(sender, instance, created, **kwargs):
    """
    Automatically creates an AdminProfile when a user is assigned the 'admin' role.
    """
    if created and instance.role == "admin":
        AdminProfile.objects.create(user=instance)

@receiver(pre_save, sender=User)
def handle_admin_promotion(sender, instance, **kwargs):
    """Ensure users promoted to admin get permissions."""
    if instance.pk:
        old_instance = User.objects.get(pk=instance.pk)
        if old_instance.role != "admin" and instance.role == "admin":
            assign_admin_permissions(sender, instance, created=False)

@receiver(post_save, sender=User)
def notify_superadmins_on_new_admin(sender, instance, created, **kwargs):
    """Notifies Superadmins when a new Admin is added."""
    if created and instance.role == "admin":
        superadmins = User.objects.filter(role="superadmin")
        for superadmin in superadmins:
            send_notification(
                recipient=superadmin,
                title="New Admin Added",
                message=f"{instance.username} has been assigned as an Admin.",
                category="user"
            )


@receiver(post_save, sender=User)
def log_admin_suspensions(sender, instance, **kwargs):
    """Logs when an Admin suspends a user."""
    if instance.is_suspended:
        AdminActivityLog.objects.create(
            admin=instance,
            action=f"Suspended {instance.username}."
        )




@receiver(post_save, sender=Dispute)
def notify_admins_on_new_dispute(sender, instance, created, **kwargs):
    """Notifies Admins when a new dispute is created."""
    if created:
        created_by = instance.user.username if instance.user else "System"
        send_notification(
            recipient=User.objects.filter(role="admin"),
            title="New Dispute Opened",
            message=f"A dispute for Order #{instance.order.id} was opened by {created_by}.",
            category="dispute"
        )


@receiver(post_save, sender=User)
def assign_admin_permissions(sender, instance, created, **kwargs):
    """Assign default admin permissions and handle superadmin auto-settings."""
    if instance.role in ["admin", "superadmin"]:
        admin_profile, _ = apps.get_model('admin_management', 'AdminProfile').objects.get_or_create(user=instance)

        if instance.role == "superadmin":
            # Grant all permissions to superadmins
            admin_profile.is_superadmin = True
            admin_profile.can_manage_writers = True
            admin_profile.can_manage_support = True
            admin_profile.can_manage_editors = True
            admin_profile.can_manage_clients = True
            admin_profile.can_suspend_users = True
            admin_profile.can_handle_orders = True
            admin_profile.can_resolve_disputes = True
            admin_profile.can_manage_payouts = True

        admin_profile.save()  # Save only once

        admin_group, _ = Group.objects.get_or_create(name="Admin")

        permissions = [
            "add_user", "change_user", "delete_user",
            "view_order", "change_order", "delete_order",
            "resolve_disputes",
            "approve_payouts", "view_payouts",
            "manage_discounts", "manage_refunds",
            "add_specialorder", "change_specialorder", "delete_specialorder",
        ]

        admin_group.permissions.add(*Permission.objects.filter(codename__in=permissions))
        instance.groups.add(admin_group)


@receiver(pre_save, sender=User)
def log_admin_suspensions(sender, instance, **kwargs):
    """Logs when an Admin suspends a user."""
    if instance.pk:
        old_instance = User.objects.get(pk=instance.pk)
        if not old_instance.is_suspended and instance.is_suspended:  # Log only when suspension is new
            AdminLog.objects.create(
                admin=instance,
                action=f"Suspended {instance.username}."
            )



@receiver(post_save, sender=BlacklistedUser)
def notify_superadmins_on_blacklist(sender, instance, created, **kwargs):
    """Notify Superadmins when a user is blacklisted."""
    if created:
        superadmins = User.objects.filter(role="superadmin")
        for superadmin in superadmins:
            send_notification(
                recipient=superadmin,
                title="User Blacklisted",
                message=f"{instance.email} was blacklisted by {instance.blacklisted_by.username}.",
                category="security"
            )
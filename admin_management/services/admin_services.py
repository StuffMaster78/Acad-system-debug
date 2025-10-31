from django.contrib.auth.models import Group, Permission
from django.apps import apps
from django.db import transaction
from django.contrib.auth import get_user_model
from admin_management.models import AdminProfile, BlacklistedUser
from orders.models import Dispute
from admin_management.models import AdminActivityLog
from notifications_system.services.core import NotificationService

User = get_user_model()

def create_admin_profile_if_needed(user):
    if user.role == "admin":
        AdminProfile.objects.get_or_create(user=user)

def promote_to_admin_if_needed(user):
    admin_profile, _ = AdminProfile.objects.get_or_create(user=user)
    assign_admin_permissions(user, admin_profile)

def assign_admin_permissions(user, admin_profile=None):
    if user.role not in ["admin", "superadmin"]:
        return

    admin_profile = admin_profile or AdminProfile.objects.get_or_create(user=user)[0]

    if user.role == "superadmin":
        admin_profile.is_superadmin = True
        admin_profile.can_manage_writers = True
        admin_profile.can_manage_support = True
        admin_profile.can_manage_editors = True
        admin_profile.can_manage_clients = True
        admin_profile.can_suspend_users = True
        admin_profile.can_handle_orders = True
        admin_profile.can_resolve_disputes = True
        admin_profile.can_manage_payouts = True

    admin_profile.save()

    admin_group, _ = Group.objects.get_or_create(name="Admin")
    perms = [
        "add_user", "change_user", "delete_user",
        "view_order", "change_order", "delete_order",
        "resolve_disputes",
        "approve_payouts", "view_payouts",
        "manage_discounts", "manage_refunds",
        "add_specialorder", "change_specialorder", "delete_specialorder",
    ]
    admin_group.permissions.add(*Permission.objects.filter(codename__in=perms))
    user.groups.add(admin_group)

def notify_superadmins_new_admin(user):
    if user.role == "admin":
        for superadmin in User.objects.filter(role="superadmin"):
            NotificationService.send_notification(
                recipient=superadmin,
                title="New Admin Added",
                message=f"{user.username} has been assigned as an Admin.",
                category="user"
            )

def log_user_suspension_if_needed(user):
    if user.is_suspended:
        AdminActivityLog.objects.create(
            admin=user,
            action=f"User Suspension: {user.username} was suspended."
        )

def log_user_suspension_if_changed(user, previous_state):
    if not previous_state.is_suspended and user.is_suspended:
        AdminActivityLog.objects.create(
            admin=user,
            action=f"User Suspension: {user.username} was suspended."
        )

def notify_superadmins_blacklist(blacklisted_user):
    for superadmin in User.objects.filter(role="superadmin"):
        NotificationService.send_notification(
            recipient=superadmin,
            title="User Blacklisted",
            message=f"{blacklisted_user.email} was blacklisted by {blacklisted_user.blacklisted_by.username}.",
            category="security"
        )

def notify_admins_new_dispute(dispute):
    if not dispute.user or not dispute.order:
        return
    created_by = dispute.user.username
    for admin in User.objects.filter(role="admin"):
        NotificationService.send_notification(
            recipient=admin,
            title="New Dispute Opened",
            message=f"A dispute for Order #{dispute.order.id} was opened by {created_by}.",
            category="dispute"
        )

def assign_admin_permissions_on_user_save(sender, instance, created, **kwargs):
    if instance.role in ["admin", "superadmin"]:
        create_admin_profile_if_needed(instance)
        promote_to_admin_if_needed(instance)
        assign_admin_permissions(instance)
        notify_superadmins_new_admin(instance)

    if created and instance.is_suspended:
        log_user_suspension_if_needed(instance)

    if not created:
        previous_state = User.objects.get(pk=instance.pk)
        log_user_suspension_if_changed(instance, previous_state)
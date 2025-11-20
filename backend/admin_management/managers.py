import random
import string
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, Permission
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
from django.conf import settings
from notifications_system.services.core import NotificationService  # Integration with Notifications App

User = get_user_model()

# Lazy import to prevent circular imports
def get_blacklisted_user_model():
    from admin_management.models import BlacklistedUser
    return BlacklistedUser

def get_admin_log_model():
    from admin_management.models import AdminActivityLog
    return AdminActivityLog

class AdminManager:
    """Handles all Admin operations, including user creation, suspensions, and permission assignments."""

    @staticmethod
    def generate_temp_password():
        """Generates a temporary password for new users."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

    @staticmethod
    def create_user(admin, username, email, role, phone_number=""):
        """Admin creates a user (Writer, Support, Editor, Client)."""
        if role not in ["writer", "support", "editor", "client"]:
            return {"status": "error", "message": "Invalid role"}

        try:
            temp_password = AdminManager.generate_temp_password()
            user = User.objects.create(
                username=username,
                email=email,
                role=role,
                phone_number=phone_number,
                password=make_password(temp_password)
            )

            # Log action
            AdminActivityLog = get_admin_log_model()
            AdminActivityLog.objects.create(
                admin=admin,
                action=f"Created user {username} with role {role}."
            )

            # Send notification
            website = getattr(admin, 'website', None)
            if not website:
                from websites.models import Website
                website = Website.objects.filter(is_active=True).first()
            if website:
                NotificationService.send_notification(
                    user=admin,
                    event="user.created",
                    payload={
                        "username": username,
                        "role": role,
                        "message": f"User {username} ({role}) was created successfully.",
                    },
                    website=website,
                    category="user"
                )

            # Email notification
            send_mail(
                subject="Your Account Details",
                message=f"Hello {username},\nYour new account has been created.\nUsername: {username}\nTemporary Password: {temp_password}\nPlease log in and change your password.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )

            return {"status": "success", "message": f"User {username} created successfully"}

        except Exception as e:
            return {"status": "error", "message": f"An error occurred: {str(e)}"}


    @staticmethod
    def suspend_user(admin, user, reason="No reason provided"):
        """Suspends a user."""
        if user.role == "superadmin":
            return {"error": "Superadmins cannot be suspended."}

        user.is_suspended = True
        user.suspension_reason = reason
        user.suspension_start_date = now()
        user.save()

        # Log action
        AdminLog = get_admin_log_model()
        AdminLog.objects.create(
            admin=admin,
            action=f"Suspended {user.username} for: {reason}"
        )

        # Send notification
        website = getattr(user, 'website', None)
        if not website:
            from websites.models import Website
            website = Website.objects.filter(is_active=True).first()
        if website:
            NotificationService.send_notification(
                user=user,
                event="user.account_suspended",
                payload={
                    "reason": reason,
                    "message": f"Your account has been suspended. Reason: {reason}.",
                },
                website=website,
                category="security"
            )

        return {"message": f"User {user.username} has been suspended."}


    @staticmethod
    def blacklist_user(admin, user, reason="No reason provided"):
        """Blacklists a user and logs the event."""
        if user.role == "admin":
            return {"error": "You cannot blacklist an admin."}

        BlacklistedUser = get_blacklisted_user_model()
        BlacklistedUser.objects.create(email=user.email, blacklisted_by=admin, reason=reason)

        user.is_blacklisted = True
        user.save()

        AdminLog = get_admin_log_model()
        AdminLog.objects.create(
            admin=admin,
            action=f"Blacklisted {user.username}. Reason: {reason}"
        )

        return {"message": f"User {user.username} has been blacklisted."}

    @staticmethod
    def place_user_on_probation(admin, user, reason, duration_in_days=30):
        """Places a user on probation for a set duration."""
        if user.role == "admin":
            return {"error": "Admins cannot be placed on probation."}

        user.is_on_probation = True
        user.probation_reason = reason
        user.probation_start_date = now()
        user.probation_end_date = now() + timedelta(days=duration_in_days)
        user.save()

        # Log the action
        AdminLog = get_admin_log_model()
        AdminLog.objects.create(
            admin=admin,
            action=f"Placed {user.username} on probation for {duration_in_days} days. Reason: {reason}"
        )

        # Send notification
        website = getattr(user, 'website', None)
        if not website:
            from websites.models import Website
            website = Website.objects.filter(is_active=True).first()
        if website:
            NotificationService.send_notification(
                user=user,
                event="user.probation_started",
                payload={
                    "duration_in_days": duration_in_days,
                    "reason": reason,
                    "message": f"You have been placed on probation for {duration_in_days} days. Reason: {reason}.",
                },
                website=website,
                category="account"
            )

        return {"message": f"User {user.username} is now on probation."}

    @staticmethod
    def remove_user_from_probation(admin, user):
        """Removes a user from probation."""
        if not user.is_on_probation:
            return {"error": "User is not on probation."}

        user.is_on_probation = False
        user.probation_reason = None
        user.probation_start_date = None
        user.probation_end_date = None
        user.save()

        # Log the action
        AdminLog = get_admin_log_model()
        AdminLog.objects.create(
            admin=admin,
            action=f"Removed {user.username} from probation."
        )

        # Send notification
        website = getattr(user, 'website', None)
        if not website:
            from websites.models import Website
            website = Website.objects.filter(is_active=True).first()
        if website:
            NotificationService.send_notification(
                user=user,
                event="user.probation_removed",
                payload={
                    "message": "Your probation has been removed. You are now in good standing.",
                },
                website=website,
                category="account"
            )

        return {"message": f"User {user.username} is no longer on probation."}



    @staticmethod
    def assign_permissions(admin_profile):
        """
        Assigns default permissions to admins when they are created.
        Ensures Superadmins are not assigned limited admin permissions.
        """
        try:
            if admin_profile.is_superadmin:
                return {"status": "success", "message": "Superadmins don't need limited permissions"}

            # Define role-based permissions mapping
            role_permissions = {
                "admin": [
                    "add_user", "change_user", "delete_user",
                    "view_order", "change_order", "cancel_order",
                    "resolve_disputes", "manage_discounts", "approve_payouts", "view_payouts",
                    "process_payments", "handle_refunds", "manage_tickets"
                ],
                "support": [
                    "view_order", "resolve_disputes", "manage_tickets"
                ],
                "editor": [
                    "view_order", "change_order", "resolve_disputes"
                ]
                # Add more roles as needed
            }

            # Get the appropriate permissions based on the role
            permissions = role_permissions.get(admin_profile.role, [])

            if not permissions:
                return {"status": "error", "message": "No permissions found for this role"}

            # Fetch or create the group and assign permissions
            admin_group, _ = Group.objects.get_or_create(name="Admin")

            for perm in permissions:
                permission = Permission.objects.filter(codename=perm).first()
                if permission:
                    admin_group.permissions.add(permission)
                else:
                    return {"status": "error", "message": f"Permission '{perm}' not found."}

            admin_profile.user.groups.add(admin_group)

            # Log action
            AdminLog = get_admin_log_model()
            AdminLog.objects.create(
                admin=admin_profile.user,
                action=f"Assigned permissions for role {admin_profile.role}."
            )

            return {"status": "success", "message": f"Permissions assigned for {admin_profile.role} role"}

        except Exception as e:
            return {"status": "error", "message": f"An error occurred: {str(e)}"}
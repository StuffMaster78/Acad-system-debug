import random
import string
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, Permission
from django.core.mail import send_mail
from django.conf import settings
from accounts.models import AccountProfile
from accounts.services.account_activation_service import AccountActivationService
from accounts.services.account_service import AccountService
from notifications_system.services.notification_service import NotificationService  # Integration with Notifications App

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
                from websites.models.websites import Website
                website = Website.objects.filter(is_active=True).first()
            if website:
                NotificationService.notify(
                    event_key="user.created",
                    recipient=user,
                    website=website,
                    context={
                        "user": admin,
                        "event": "user.created",
                        "message": f"User {username} ({role}) was created successfully.",
                    },
                    channels=["email", "in_app"],
                    priority="high",
                    is_broadcast=False,
                    is_critical=True,
                    is_digest=False,
                    is_silent=False,
                    digest_group=None,
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

        website = getattr(user, "website", None) or getattr(admin, "website", None)
        if not website:
            from websites.models.websites import Website

            website = Website.objects.filter(is_active=True).first()
        if not website:
            return {"error": "Cannot suspend a user without a website context."}

        account_profile = AccountService.get_or_create_account_profile(
            website=website,
            user=user,
            actor=admin,
            is_primary=not AccountProfile.objects.filter(user=user).exists(),
            metadata={"source": "admin_management.suspend_user"},
        )
        AccountActivationService.suspend_account(
            account_profile=account_profile,
            reason=reason,
            actor=admin,
            metadata={"source": "admin_management.suspend_user"},
        )

        # Log action
        AdminLog = get_admin_log_model()
        AdminLog.objects.create(
            admin=admin,
            action=f"Suspended {user.username} for: {reason}"
        )

        # Send notification
        if website:
            NotificationService.notify(
                event_key="user.account_suspended",
                recipient=user,
                website=website,
                context={
                    "reason": reason,
                    "message": f"Your account has been suspended. Reason: {reason}.",
                },
                channels=["email", "in_app"],
                priority="high",
                is_broadcast=False,
                is_critical=True,
                is_digest=False,
                is_silent=False,
                digest_group=None,
            )

        return {"message": f"User {user.username} has been suspended."}


    @staticmethod
    def blacklist_user(admin, user, reason="No reason provided"):
        """Blacklists a user and logs the event."""
        if user.role == "admin":
            return {"error": "You cannot blacklist an admin."}

        BlacklistedUser = get_blacklisted_user_model()
        BlacklistedUser.objects.create(email=user.email, blacklisted_by=admin, reason=reason)

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

        if user.role != "writer":
            return {"error": "Probation is currently managed through writer discipline."}

        from writer_management.models import WriterProfile
        from writer_management.services.discipline_service import DisciplineService

        try:
            writer = WriterProfile.objects.get(account_profile__user=user)
        except WriterProfile.DoesNotExist:
            return {"error": "Writer profile not found."}

        DisciplineService.place_on_probation(
            writer=writer,
            reason=reason,
            duration_days=duration_in_days,
            placed_by=admin,
        )

        # Log the action
        AdminLog = get_admin_log_model()
        AdminLog.objects.create(
            admin=admin,
            action=f"Placed {user.username} on probation for {duration_in_days} days. Reason: {reason}"
        )

        # Send notification
        website = getattr(user, 'website', None)
        if not website:
            from websites.models.websites import Website
            website = Website.objects.filter(is_active=True).first()
        if website:
            NotificationService.notify(
                event_key="user.probation_started",
                recipient=user,
                website=website,
                context={
                    "duration_in_days": duration_in_days,
                    "reason": reason,
                    "message": f"You have been placed on probation for {duration_in_days} days. Reason: {reason}.",
                },
                channels=["email", "in_app"],
                priority="high",
                is_broadcast=False,
                is_critical=True,
                is_digest=False,
                is_silent=False,
                digest_group=None,
            )

        return {"message": f"User {user.username} is now on probation."}

    @staticmethod
    def remove_user_from_probation(admin, user):
        """Removes a user from probation."""
        if user.role != "writer":
            return {"error": "User is not on probation."}

        from writer_management.models import WriterProfile
        from writer_management.services.discipline_service import DisciplineService

        try:
            writer = WriterProfile.objects.get(account_profile__user=user)
            DisciplineService.end_probation(
                writer=writer,
                ended_by=admin,
                reason="Probation ended by admin.",
            )
        except (WriterProfile.DoesNotExist, ValueError):
            return {"error": "User is not on probation."}


        # Log the action
        AdminLog = get_admin_log_model()
        AdminLog.objects.create(
            admin=admin,
            action=f"Removed {user.username} from probation."
        )

        # Send notification
        website = getattr(user, 'website', None)
        if not website:
            from websites.models.websites import Website
            website = Website.objects.filter(is_active=True).first()
        if website:
            NotificationService.notify(
                event_key="user.probation_removed",
                recipient=user,
                website=website,
                context={
                    "message": "Your probation has been removed. You are now in good standing.",
                },
                channels=["email", "in_app"],
                priority="high",
                is_broadcast=False,
                is_critical=True,
                is_digest=False,
                is_silent=False,
                digest_group=None,
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

            # Use refined group service for consistent group creation
            from users.services.group_service import UserGroupService
            try:
                UserGroupService.assign_user_to_group(admin_profile.user, admin_profile.user.role)
            except Exception as e:
                # Fallback to old method if service fails
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

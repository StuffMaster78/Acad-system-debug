import random
import string
from datetime import timedelta
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.utils.timezone import now
from django.conf import settings
from .models import SuperadminLog, Probation, Blacklist, User, UserActionLog
from notifications_system.models import Notification
class SuperadminManager:
    """Handles all Superadmin operations."""

    @staticmethod
    def generate_temp_password():
        """Generates a temporary password for new users."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

    @staticmethod
    def create_user(superadmin, username, email, role, phone_number=""):
        """Superadmin creates a new user."""
        if role not in ["admin", "support", "editor", "writer", "client"]:
            return {"error": "Invalid role"}

        temp_password = SuperadminManager.generate_temp_password()
        user = User.objects.create(
            username=username,
            email=email,
            role=role,
            phone_number=phone_number,
            password=make_password(temp_password)
        )

        # Log action
        SuperadminLog.objects.create(
            superadmin=superadmin,
            action_type="user_manage",
            action_details=f"Created user {username} with role {role}."
        )

        # Send Email Notification
        send_mail(
            subject="Your New Account Details",
            message=f"Hello {username},\n\nYour new account has been created.\nUsername: {username}\nTemporary Password: {temp_password}\n\nPlease log in and change your password immediately.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )

        return {"message": f"User {username} created successfully"}

    @staticmethod
    def change_user_role(superadmin, user, new_role):
        """Promotes or demotes a user."""
        if new_role not in ["admin", "support", "editor", "writer", "client"]:
            return {"error": "Invalid role"}

        old_role = user.role
        user.role = new_role
        user.save()

        # Log action
        SuperadminLog.objects.create(
            superadmin=superadmin,
            action_type="promotion",
            action_details=f"Changed role of {user.username} from {old_role} to {new_role}."
        )

        # Notify user
        send_mail(
            subject="Role Update",
            message=f"Hello {user.username},\n\nYour role has been updated from {old_role} to {new_role}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

        return {"message": f"User {user.username} promoted to {new_role}."}

    @staticmethod
    def suspend_user(superadmin, user, reason="No reason provided"):
        """Suspends a user."""
        user.is_suspended = True
        user.suspension_reason = reason
        user.suspension_start_date = now()
        user.save()

        # Log action
        SuperadminLog.objects.create(
            superadmin=superadmin,
            action_type="suspension",
            action_details=f"Suspended {user.username} for: {reason}"
        )

        # Notify user
        send_mail(
            subject="Account Suspended",
            message=f"Hello {user.username},\n\nYour account has been suspended.\nReason: {reason}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

        return {"message": f"User {user.username} has been suspended."}

    @staticmethod
    def reactivate_user(superadmin, user):
        """Reactivates a suspended user."""
        user.is_suspended = False
        user.suspension_reason = None
        user.save()

        # Log action
        SuperadminLog.objects.create(
            superadmin=superadmin,
            action_type="suspension",
            action_details=f"Reactivated {user.username}."
        )

        # Notify user
        send_mail(
            subject="Account Reactivated",
            message=f"Hello {user.username},\n\nYour account has been reactivated.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

        return {"message": f"User {user.username} has been reactivated."}

    @staticmethod
    def place_user_on_probation(superadmin, user, reason, duration_days):
        """Places a user on probation with an expiry date."""
        probation_end_date = now() + timedelta(days=duration_days)

        probation = Probation.objects.create(
            user=user,
            placed_by=superadmin,
            reason=reason,
            start_date=now(),
            end_date=probation_end_date,
            is_active=True
        )

        # Log action
        SuperadminLog.objects.create(
            superadmin=superadmin,
            action_type="probation",
            action_details=f"Placed {user.username} on probation until {probation_end_date}. Reason: {reason}"
        )

        # Notify user
        send_mail(
            subject="Probation Notice",
            message=f"Hello {user.username},\n\nYou have been placed on probation until {probation_end_date}.\nReason: {reason}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

        return {"message": f"User {user.username} placed on probation until {probation_end_date}."}

    @staticmethod
    def blacklist_user(superadmin, user=None, email=None, ip_address=None, reason="No reason provided"):
        """Blacklists a user, email, or IP address."""
        if not user and not email and not ip_address:
            return {"error": "Must provide a user, email, or IP address to blacklist."}

        blacklist_entry = Blacklist.objects.create(
            user=user if user else None,
            email=email,
            ip_address=ip_address,
            reason=reason,
            blacklisted_by=superadmin,
            is_active=True
        )

        # Log action
        SuperadminLog.objects.create(
            superadmin=superadmin,
            action_type="blacklist",
            action_details=f"Blacklisted {user.username if user else email or ip_address}. Reason: {reason}"
        )

        # Notify user if they exist
        if user:
            send_mail(
                subject="Account Blacklisted",
                message=f"Hello {user.username},\n\nYour account has been blacklisted.\nReason: {reason}.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )

        return {"message": f"User {user.username if user else email or ip_address} has been blacklisted."}

    @staticmethod
    def remove_blacklist_entry(superadmin, blacklist_entry):
        """Removes a blacklist entry."""
        blacklist_entry.is_active = False
        blacklist_entry.save()

        # Log action
        SuperadminLog.objects.create(
            superadmin=superadmin,
            action_type="blacklist",
            action_details=f"Removed blacklist entry for {blacklist_entry.user.username if blacklist_entry.user else blacklist_entry.email or blacklist_entry.ip_address}."
        )

        return {"message": f"Blacklist entry removed for {blacklist_entry.user.username if blacklist_entry.user else blacklist_entry.email or blacklist_entry.ip_address}."}
      
    @staticmethod
    def notify_admins(title, message):
        """Sends an in-app notification to all Superadmins."""
        admins = User.objects.filter(superadmin_profile__isnull=False)
        for admin in admins:
            Notification.objects.create(user=admin, title=title, message=message)

    def log_action(admin, user, action, details=""):
        """Logs user actions (suspensions, reactivations, etc.)."""
        UserActionLog.objects.create(admin=admin, target_user=user, action=action, details=details)

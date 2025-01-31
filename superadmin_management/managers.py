import random
import string
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.utils.timezone import now
from django.conf import settings
from .models import SuperadminLog, User

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
            action=f"Created user {username} with role {role}."
        )

        # Send Email Notification
        send_mail(
            subject="Your New Account Details",
            message=f"Hello {username},\n\nYour new account has been created. \nUsername: {username} \nTemporary Password: {temp_password}\n\nPlease log in and change your password immediately.",
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
            action=f"Changed role of {user.username} from {old_role} to {new_role}."
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
            action=f"Suspended {user.username} for: {reason}"
        )

        # Notify user
        send_mail(
            subject="Account Suspended",
            message=f"Hello {user.username},\n\nYour account has been suspended. Reason: {reason}.",
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
            action=f"Reactivated {user.username}."
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
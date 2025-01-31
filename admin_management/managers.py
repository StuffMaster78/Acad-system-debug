import random
import string
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.utils.timezone import now
from django.conf import settings
from .models import AdminLog, User
from notifications_system.models import send_notification  # Integration with Notifications App

class AdminManager:
    """Handles all Admin operations."""

    @staticmethod
    def generate_temp_password():
        """Generates a temporary password for new users."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

    @staticmethod
    def create_user(admin, username, email, role, phone_number=""):
        """Admin creates a user (Writer, Support, Editor, Client)."""
        if role not in ["writer", "support", "editor", "client"]:
            return {"error": "Invalid role"}

        temp_password = AdminManager.generate_temp_password()
        user = User.objects.create(
            username=username,
            email=email,
            role=role,
            phone_number=phone_number,
            password=make_password(temp_password)
        )

        # Log action
        AdminLog.objects.create(
            admin=admin,
            action=f"Created user {username} with role {role}."
        )

        # Send notification
        send_notification(
            recipient=admin,
            title="New User Created",
            message=f"User {username} ({role}) was created successfully.",
            category="user",
            timestamp=now()
        )

        # Email notification
        send_mail(
            subject="Your Account Details",
            message=f"Hello {username},\nYour new account has been created.\nUsername: {username}\nTemporary Password: {temp_password}\nPlease log in and change your password.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )

        return {"message": f"User {username} created successfully"}

    @staticmethod
    def suspend_user(admin, user, reason="No reason provided"):
        """Suspends a user."""
        user.is_suspended = True
        user.suspension_reason = reason
        user.suspension_start_date = now()
        user.save()

        # Log action
        AdminLog.objects.create(
            admin=admin,
            action=f"Suspended {user.username} for: {reason}"
        )

        # Send notification
        send_notification(
            recipient=user,
            title="Account Suspended",
            message=f"Your account has been suspended. Reason: {reason}.",
            category="security",
            timestamp=now()
        )

        return {"message": f"User {user.username} has been suspended."}
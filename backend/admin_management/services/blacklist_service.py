from django.contrib.auth import get_user_model

from admin_management.models import BlacklistedUser
from admin_management.models import AdminActivityLog

User = get_user_model()


class BlacklistService:
    """
    Service class for managing blacklisted users.

    This class provides methods to blacklist users, remove them from the
    blacklist, check if a user is blacklisted, and retrieve blacklisted users.
    """

    @staticmethod
    def blacklist_user(email, website, blacklisted_by, reason=None):
        email = email.strip().lower()
        reason = (reason or "").strip()

        if BlacklistedUser.objects.filter(email=email).exists():
            raise ValueError("This user is already blacklisted.")

        user = User.objects.filter(email=email).first()
        website = website or getattr(user, "website", None)

        record = BlacklistedUser.objects.create(
            email=email,
            website=website,
            user=user,
            blacklisted_by=blacklisted_by,
            reason=reason,
        )

        AdminActivityLog.objects.create(
            admin=blacklisted_by,
            target_user=user,
            action="Blacklisted User",
            website=website,
            details=f"Blacklisted {email}. Reason: {reason or 'N/A'}"
        )

        return {
            "message": f"{email} blacklisted successfully.",
            "blacklist_id": record.id
        }

    @staticmethod
    def remove_blacklist(email):
        email = email.strip().lower()
        deleted_count, _ = BlacklistedUser.objects.filter(
            email=email
        ).delete()

        if not deleted_count:
            return {"message": f"{email} was not blacklisted."}

        return {"message": f"{email} removed from blacklist."}

    @staticmethod
    def is_blacklisted(email):
        return BlacklistedUser.objects.filter(email=email).exists()

    @staticmethod
    def get_blacklisted_users():
        return BlacklistedUser.objects.all().order_by("-created_at")

    @staticmethod
    def get_blacklisted_user_by_email(email):
        """
        Retrieve a blacklisted user by their email.
        Returns None if the user is not found.
        """
        try:
            return BlacklistedUser.objects.get(email=email)
        except BlacklistedUser.DoesNotExist:
            return None

    @staticmethod
    def get_blacklisted_user_by_id(blacklist_id):
        """
        Retrieve a blacklisted user by their ID.
        Returns None if the user is not found.
        """
        try:
            return BlacklistedUser.objects.get(id=blacklist_id)
        except BlacklistedUser.DoesNotExist:
            return None

    @staticmethod
    def get_blacklisted_users_by_website(website):
        """
        Retrieve all blacklisted users for a specific website.
        Returns an empty queryset if no users are found.
        """
        return BlacklistedUser.objects.filter(
            website=website
        ).order_by("-created_at")

    @staticmethod
    def get_blacklisted_users_by_user(user):
        """
        Retrieve all blacklisted users associated with a specific user.
        Returns an empty queryset if no users are found.
        """
        return BlacklistedUser.objects.filter(
            user=user
        ).order_by("-created_at")

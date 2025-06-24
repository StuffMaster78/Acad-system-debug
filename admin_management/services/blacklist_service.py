from django.db import IntegrityError
from admin_management.models import BlacklistedUser
from django.contrib.auth import get_user_model
from activity.models import ActivityLog

User = get_user_model()


class BlacklistService:
    """
    Service class for managing blacklisted users.
    This class provides methods to blacklist users, remove them from the blacklist,
    check if a user is blacklisted, and retrieve blacklisted users.
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

        ActivityLog.objects.create(
            admin=blacklisted_by,
            target_user=user,
            action="Blacklisted User",
            details=f"Blacklisted {email}. Reason: {reason or 'N/A'}"
        )

        return {
            "message": f"{email} blacklisted successfully.",
            "blacklist_id": record.id
        }


    @staticmethod
    def remove_blacklist(email):
        BlacklistedUser.objects.filter(email=email).delete()

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
        return BlacklistedUser.objects.filter(website=website).order_by("-created_at")
    
    @staticmethod
    def get_blacklisted_users_by_user(user):
        """
        Retrieve all blacklisted users associated with a specific user.
        Returns an empty queryset if no users are found.
        """
        return BlacklistedUser.objects.filter(user=user).order_by("-created_at")
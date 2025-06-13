from authentication.models.lockout import AccountLockout
from django.utils import timezone


class AccountLockoutService:
    """
    Service to handle account lockouts per user and website context.
    """

    def __init__(self, user, website):
        """
        Initialize the service.

        Args:
            user (User): The user to lock/unlock.
            website (Website): The website (tenant) context.
        """
        self.user = user
        self.website = website

    def lock_account(self, reason):
        """
        Lock the user's account for this website.

        Args:
            reason (str): Reason for locking the account.

        Returns:
            AccountLockout: The created lockout object.
        """
        return AccountLockout.objects.create(
            user=self.user,
            website=self.website,
            reason=reason,
            active=True
        )

    def unlock_account(self):
        """
        Unlock all active lockouts for this user on this website.

        Returns:
            int: Number of lockouts deactivated.
        """
        return AccountLockout.objects.filter(
            user=self.user,
            website=self.website,
            active=True
        ).update(active=False)

    def is_locked(self):
        """
        Check if the user's account is currently locked.

        Returns:
            bool: True if account is locked, False otherwise.
        """
        return AccountLockout.objects.filter(
            user=self.user,
            website=self.website,
            active=True
        ).exists()

    def get_lockout_reasons(self):
        """
        Get all active lockout reasons for this user.

        Returns:
            QuerySet: List of active lockout records with reasons.
        """
        return AccountLockout.objects.filter(
            user=self.user,
            website=self.website,
            active=True
        )
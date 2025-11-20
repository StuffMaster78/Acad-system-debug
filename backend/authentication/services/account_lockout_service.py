from django.utils.timezone import now
from django.utils import timezone
from authentication.models.lockout import AccountLockout


class AccountLockoutService:
    """
    Service to manage account lockouts for suspicious activity or admin actions.
    """

    def __init__(self, user, website):
        self.user = user
        self.website = website

    def lock_account(self, reason="automatic lockout"):
        """
        Locks a user account with a reason.
        Automatically deactivates any existing lockouts.
        """
        self.unlock_account()  # Ensure no overlapping lockouts

        return AccountLockout.objects.update_or_create(
            user=self.user,
            website=self.website,
            defaults={
                "reason": reason,
                "locked_at": now(),
                "active": True
            }
        )

    def unlock_account(self):
        """
        Unlocks the user account by deactivating all active lockouts.
        """
        return AccountLockout.objects.filter(
            user=self.user,
            website=self.website,
            active=True
        ).update(active=False)

    def is_account_locked(self):
        """
        Returns True if there is an active lockout for the user.
        """
        try:
            lock = AccountLockout.objects.get(user=self.user)
            if not lock.is_locked:
                return False

            if (timezone.now() - lock.locked_at).total_seconds() >= 1800:  # 30 min
                lock.is_locked = False
                lock.save()
                return False

            return True
        except AccountLockout.DoesNotExist:
            return False

    def get_active_lockout(self):
        """
        Returns the active lockout object if it exists, else None.
        """
        return AccountLockout.objects.filter(
            user=self.user,
            website=self.website,
            active=True
        ).first()
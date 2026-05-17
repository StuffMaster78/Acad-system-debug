"""
User state mutation service.

This service is responsible for changing user operational state.

It does NOT decide how state is retrieved. That responsibility belongs
to UserStateResolver.

All methods are tenant-aware via the `website` parameter.
"""

from users_state.resolvers.user_state_resolver import UserStateResolver


class UserStateService:
    """
    Handles mutations to user state.

    This layer is responsible for business actions only:
    suspend, blacklist, probation management.
    """

    # -------------------------
    # SUSPENSION
    # -------------------------
    @staticmethod
    def suspend_user(*, user, reason: str, website=None):
        """
        Suspend a user in a given tenant scope.

        Args:
            user: User instance
            reason: Reason for suspension
            website: Tenant context
        """
        state = UserStateResolver.get(user=user, website=website)

        state.is_suspended = True
        state.suspension_reason = reason
        state.save(update_fields=[
            "is_suspended",
            "suspension_reason",
        ])

    @staticmethod
    def lift_suspension(*, user, website=None):
        """
        Remove suspension from a user.
        """
        state = UserStateResolver.get(user=user, website=website)

        state.is_suspended = False
        state.suspension_reason = None
        state.save(update_fields=[
            "is_suspended",
            "suspension_reason",
        ])

    # -------------------------
    # BLACKLIST
    # -------------------------
    @staticmethod
    def blacklist_user(*, user, reason: str, website=None):
        """
        Blacklist a user in a tenant context.

        Args:
            user: User instance
            reason: Blacklist reason
            website: Tenant context
        """
        state = UserStateResolver.get(user=user, website=website)

        state.is_blacklisted = True
        state.blacklist_reason = reason
        state.save(update_fields=[
            "is_blacklisted",
            "blacklist_reason",
        ])

    @staticmethod
    def lift_blacklist(*, user, website=None):
        """
        Remove blacklist status from a user.
        """
        state = UserStateResolver.get(user=user, website=website)

        state.is_blacklisted = False
        state.blacklist_reason = None
        state.save(update_fields=[
            "is_blacklisted",
            "blacklist_reason",
        ])

    # -------------------------
    # PROBATION
    # -------------------------
    @staticmethod
    def put_on_probation(*, user, reason: str, website=None):
        """
        Put a user on probation.

        Args:
            user: User instance
            reason: Probation reason
            website: Tenant context
        """
        state = UserStateResolver.get(user=user, website=website)

        state.is_on_probation = True
        state.probation_reason = reason
        state.save(update_fields=[
            "is_on_probation",
            "probation_reason",
        ])

    @staticmethod
    def end_probation(*, user, website=None):
        """
        End probation for a user.
        """
        state = UserStateResolver.get(user=user, website=website)

        state.is_on_probation = False
        state.probation_reason = None
        state.save(update_fields=[
            "is_on_probation",
            "probation_reason",
        ])
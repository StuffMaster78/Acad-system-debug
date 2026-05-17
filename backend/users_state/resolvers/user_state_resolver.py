from users_state.models import UserState


class UserStateResolver:
    """
    Single entry point for resolving user state in a tenant-aware system.
    """

    @staticmethod
    def get(*, user, website=None):
        """
        Returns the correct state object.

        Resolution order:
        1. (user, website)
        2. (user, None) global fallback
        3. create (user, website)
        """

        state = UserState.objects.filter(
            user=user,
            website=website,
        ).first()

        if state:
            return state

        # fallback to global state
        state = UserState.objects.filter(
            user=user,
            website=None,
        ).first()

        if state:
            return state

        # create new scoped state
        return UserState.objects.create(
            user=user,
            website=website,
        )
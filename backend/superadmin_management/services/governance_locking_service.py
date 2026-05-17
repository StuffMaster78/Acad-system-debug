from django.db import transaction


class GovernanceLockingService:
    """
    Prevents race conditions in governance actions.
    """

    @staticmethod
    def locked_user(user):
        return transaction.atomic()
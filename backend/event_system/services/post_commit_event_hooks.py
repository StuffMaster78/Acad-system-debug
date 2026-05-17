from django.db import transaction


def on_commit_publish(callback):
    """
    Guarantees event publishing only after DB commit.
    """

    transaction.on_commit(callback)
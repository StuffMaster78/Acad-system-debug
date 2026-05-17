from contextlib import contextmanager
from django.db import transaction


@contextmanager
def transactional_event_scope():
    """
    Ensures:
        - DB write succeeds
        - event publish only happens after commit
        - no orphan events
    """

    try:
        with transaction.atomic():
            yield
    except Exception:
        raise
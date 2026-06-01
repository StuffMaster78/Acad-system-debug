"""
editor_management/utils.py

Registration ID generation for EditorProfile.
"""

import random
import string
from datetime import date


REGISTRATION_ID_PREFIX = "ED"
REGISTRATION_ID_RANDOM_LENGTH = 6
REGISTRATION_ID_CHARS = string.ascii_uppercase + string.digits
REGISTRATION_ID_MAX_RETRIES = 10


def generate_editor_registration_id() -> str:
    """
    Generate a unique editor registration ID.
    Format: ED-{YYYYMMDD}-{RANDOM6}
    Example: ED-20250113-A7X2QP

    Called as default= on EditorProfile.registration_id.
    Retries up to 10 times on collision (extremely unlikely).
    """
    from editor_management.models import EditorProfile

    for _ in range(REGISTRATION_ID_MAX_RETRIES):
        date_part = date.today().strftime("%Y%m%d")
        random_part = "".join(
            random.choices(REGISTRATION_ID_CHARS, k=REGISTRATION_ID_RANDOM_LENGTH)
        )
        registration_id = f"{REGISTRATION_ID_PREFIX}-{date_part}-{random_part}"

        if not EditorProfile.objects.filter(
            registration_id=registration_id
        ).exists():
            return registration_id

    raise RuntimeError(
        "Failed to generate unique editor registration_id after "
        f"{REGISTRATION_ID_MAX_RETRIES} attempts."
    )
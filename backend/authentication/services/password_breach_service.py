import hashlib
import logging
import requests

from typing import Dict
from django.core.exceptions import ValidationError

logger = logging.getLogger(__name__)


class PasswordBreachService:
    """
    Stateless service for checking passwords against HIBP.
    """

    HIBP_API_URL = "https://api.pwnedpasswords.com/range/"
    TIMEOUT = 5

    @classmethod
    def check_password(cls, password: str) -> Dict:
        """
        Check if password exists in breach database.

        Returns:
            dict with is_breached and breach_count
        """
        sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]

        try:
            response = requests.get(
                f"{cls.HIBP_API_URL}{prefix}",
                timeout=cls.TIMEOUT,
                headers={"User-Agent": "AuthSystem"},
            )

            if response.status_code != 200:
                raise RuntimeError("HIBP API failure")

            for line in response.text.splitlines():
                hash_suffix, count = line.split(":")
                if hash_suffix == suffix:
                    return {
                        "is_breached": True,
                        "breach_count": int(count),
                    }

            return {
                "is_breached": False,
                "breach_count": 0,
            }

        except requests.RequestException as e:
            logger.error(f"HIBP request failed: {e}")
            raise RuntimeError("Password breach check unavailable")

    @classmethod
    def validate_password(cls, password: str) -> None:
        """
        Enforce password is not breached.
        """
        result = cls.check_password(password)

        if result["is_breached"]:
            raise ValidationError(
                f"Password found in {result['breach_count']} breaches. "
                "Choose a stronger password."
            )
from __future__ import annotations

import logging

from django.conf import settings

from .loader import ENV


logger = logging.getLogger("config")


def log_boot_config() -> None:
    """
    Log safe, high-level settings information at boot.
    """
    logger.info("ENV=%s", ENV)
    logger.info("DEBUG=%s", settings.DEBUG)
    logger.info("ALLOWED_HOSTS=%s", settings.ALLOWED_HOSTS)

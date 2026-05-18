import logging
from .settings import settings, ENV


logger = logging.getLogger("config")


def log_boot_config():
    logger.info("ENV=%s", ENV)
    logger.info("DEBUG=%s", settings.DEBUG)
    logger.info("ALLOWED_HOSTS=%s", settings.ALLOWED_HOSTS)
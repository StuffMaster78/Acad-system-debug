from audit_logging.ingestion.processors.db_processor import DBProcessor
from audit_logging.ingestion.processors.celery_processor import CeleryProcessor


def get_default_processors():
    """
    Central ingestion pipeline registry.
    """

    return [
        DBProcessor(),
        CeleryProcessor(),
    ]
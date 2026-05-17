# superadmin_management/services/governance_dead_letter_service.py

import logging

logger = logging.getLogger(__name__)


class GovernanceDeadLetterService:
    """
    Stores failed governance operations for later replay.
    """

    @staticmethod
    def store(event_type: str, payload: dict, error: str):
        logger.error(
            "DEAD LETTER event=%s error=%s payload=%s",
            event_type,
            error,
            payload,
        )

    @staticmethod
    def replay(event):
        logger.info("Replaying event=%s", event)
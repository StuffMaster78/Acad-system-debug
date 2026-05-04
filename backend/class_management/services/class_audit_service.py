from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("class_management.audit")


class ClassAuditService:
    """
    Structured audit logging for sensitive class operations.
    """

    @staticmethod
    def log(
        *,
        event: str,
        class_order_id: int | None = None,
        actor_id: int | None = None,
        website_id: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        logger.info(
            "class_management_event",
            extra={
                "event": event,
                "class_order_id": class_order_id,
                "actor_id": actor_id,
                "website_id": website_id,
                "metadata": metadata or {},
            },
        )
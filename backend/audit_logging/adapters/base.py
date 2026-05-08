from abc import ABC, abstractmethod
from typing import Any

from audit_logging.factories.audit_event_factory import AuditEventFactory


class BaseAuditAdapter(ABC):
    """
    Base contract for all domain audit adapters.

    RULES:
    - translate domain → audit input
    - never persist directly
    - always go through AuditEventFactory
    """

    # -------------------------
    # REQUIRED CONTEXT
    # -------------------------

    def __init__(self, *, actor_id: int | None = None, website=None):
        self.actor_id = actor_id
        self.website = website

    # -------------------------
    # CORE ENTRY
    # -------------------------

    def emit(
        self,
        *,
        action: str,
        metadata: dict | None = None,
        object_type: str | None = None,
        object_id: str | None = None,
        is_sensitive: bool = False,
    ):
        return AuditEventFactory.create(
            actor_id=self.actor_id,
            website=self.website,
            action=action,
            metadata=metadata,
            object_type=object_type,
            object_id=object_id,
            is_sensitive=is_sensitive,
        )

    # -------------------------
    # DOMAIN HOOK
    # -------------------------

    @abstractmethod
    def get_domain(self) -> str:
        """
        Example: 'order', 'billing', 'communication'
        """
        raise NotImplementedError
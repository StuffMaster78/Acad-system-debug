"""
Typing helpers for the files_management app.

These aliases keep service signatures readable while avoiding overly
tight coupling to one concrete user model or domain model.
"""

from __future__ import annotations

from typing import Any, Protocol

from django.db.models import Model


class WebsiteScopedModel(Protocol):
    """
    Protocol for models that expose a website attribute.

    The platform is multi tenant, so services often need to accept
    objects that are tenant scoped without caring about the concrete
    model class.
    """

    website: Any


class ActorLike(Protocol):
    """
    Minimal actor protocol used by file services.

    The authenticated user model can be richer than this. File services
    only need a stable subset for ownership and audit style decisions.
    """

    id: Any
    is_authenticated: bool
    is_staff: bool
    is_superuser: bool
    website: Any


DomainObject = Model
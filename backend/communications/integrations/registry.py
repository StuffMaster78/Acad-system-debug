from __future__ import annotations

from typing import Type

from communications.integrations.base import CommunicationDomainAdapter


class CommunicationAdapterRegistry:
    """
    Registry mapping Django models to communication adapters.
    """

    _registry: dict[type, CommunicationDomainAdapter] = {}

    @classmethod
    def register(
        cls,
        *,
        model: type,
        adapter: CommunicationDomainAdapter,
    ) -> None:
        """
        Register adapter for a model.
        """
        cls._registry[model] = adapter

    @classmethod
    def get_adapter(cls, *, target) -> CommunicationDomainAdapter:
        """
        Resolve adapter for a target instance.
        """
        model: Type = target.__class__

        adapter = cls._registry.get(model)

        if adapter is None:
            raise ValueError(
                f"No communication adapter registered for {model}",
            )

        return adapter
from __future__ import annotations

from typing import Type

from payments_processor.providers.base import BasePaymentProvider
from payments_processor.providers.exceptions import PaymentProviderConfigurationError


_PROVIDER_REGISTRY: dict[str, Type[BasePaymentProvider]] = {}


def register_provider(provider_class: Type[BasePaymentProvider]) -> None:
    provider_name = getattr(provider_class, "provider_name", None)

    if not provider_name:
        raise PaymentProviderConfigurationError(
            "Provider class must define provider_name."
        )

    _PROVIDER_REGISTRY[provider_name] = provider_class


def get_provider(provider_name: str) -> BasePaymentProvider:
    provider_class = _PROVIDER_REGISTRY.get(provider_name)

    if provider_class is None:
        raise PaymentProviderConfigurationError(
            f"Unknown payment provider: {provider_name}"
        )

    return provider_class()


def get_registered_provider_names() -> list[str]:
    return sorted(_PROVIDER_REGISTRY.keys())
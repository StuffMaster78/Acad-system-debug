from __future__ import annotations

from typing import TYPE_CHECKING, Type

from payments_processor.providers.base import BasePaymentProvider
from payments_processor.providers.exceptions import PaymentProviderConfigurationError

if TYPE_CHECKING:
    from websites.models.websites import Website


_PROVIDER_REGISTRY: dict[str, Type[BasePaymentProvider]] = {}


def register_provider(provider_class: Type[BasePaymentProvider]) -> None:
    provider_name = getattr(provider_class, "provider_name", None)

    if not provider_name:
        raise PaymentProviderConfigurationError(
            "Provider class must define provider_name."
        )

    _PROVIDER_REGISTRY[provider_name] = provider_class


def get_provider(provider_name: str) -> BasePaymentProvider:
    """Return a provider instance using platform-default credentials."""
    provider_class = _PROVIDER_REGISTRY.get(provider_name)

    if provider_class is None:
        raise PaymentProviderConfigurationError(
            f"Unknown payment provider: {provider_name}"
        )

    return provider_class()


def get_provider_for_website(website: "Website") -> BasePaymentProvider:
    """
    Return a provider instance configured with per-site credentials.

    Reads the website's PaymentGatewayConfig to discover which env vars
    hold the site-specific secret key and webhook secret, then
    instantiates the provider with those resolved values.

    Falls back to platform defaults when:
    - The website has no gateway config
    - The gateway config is inactive
    - The named env vars are unset
    """
    config = getattr(website, "payment_gateway_config", None)
    if config is None:
        from payments_processor.models.gateway_config import PaymentGatewayConfig
        try:
            config = PaymentGatewayConfig.objects.get(website=website)
        except PaymentGatewayConfig.DoesNotExist:
            config = None

    if config is not None and config.is_active:
        provider_name = config.gateway or "stripe"
        secret_key = config.effective_secret_key or None
        webhook_secret = config.effective_webhook_secret or None
    else:
        provider_name = "stripe"
        secret_key = None
        webhook_secret = None

    provider_class = _PROVIDER_REGISTRY.get(provider_name)
    if provider_class is None:
        raise PaymentProviderConfigurationError(
            f"Unknown payment provider: {provider_name}"
        )

    return provider_class(secret_key=secret_key, webhook_secret=webhook_secret)


def get_registered_provider_names() -> list[str]:
    return sorted(_PROVIDER_REGISTRY.keys())

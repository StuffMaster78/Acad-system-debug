import logging
from .base import PROVIDER_REGISTRY
from .smtp import SMTPProvider  # Force registration of default

def get_provider_client(campaign):
    """
    Returns the appropriate email provider client for the campaign.
    Falls back to SMTP if not configured.
    """
    integration = getattr(campaign.website, 'email_service', None)

    if not integration or not integration.is_active:
        return SMTPProvider()

    provider_name = integration.provider_name.lower()
    provider_class = PROVIDER_REGISTRY.get(provider_name)

    if not provider_class:
        raise ValueError(f"Unsupported provider: {provider_name}")

    try:
        return provider_class(api_key=integration.api_key)
    except TypeError:
        return provider_class()  # For SMTP, no args
    except Exception as e:
        logging.error(f"Provider init failed: {e}")
        raise
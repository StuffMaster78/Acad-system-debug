# notifications_system/services/providers/base.py
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class ProviderResponse:
    provider: str
    message_id: str

class TemporaryProviderError(Exception):
    def __init__(self, code="temporary", msg="temporary failure"):
        super().__init__(msg)
        self.code = code

class BaseProvider:
    channel: str = "unknown"

    def send(self, rendered: dict, delivery) -> ProviderResponse:
        raise NotImplementedError


# --- Example In-App provider (no external call) ---
class InAppProvider(BaseProvider):
    channel = "in_app"

    def send(self, rendered: dict, delivery) -> ProviderResponse:
        # Persisted as Delivery row; your app will read it as an in-app message.
        # If you have an InAppMessage model, create it here.
        return ProviderResponse(provider="in_app", message_id=str(delivery.id))


# --- Example Email provider using Django's email backend ---
from django.core.mail import EmailMultiAlternatives

class EmailProvider(BaseProvider):
    channel = "email"

    def send(self, rendered: dict, delivery) -> ProviderResponse:
        subject = rendered.get("subject") or delivery.event_key
        text = rendered.get("text") or ""
        html = rendered.get("html") or None
        to_email = getattr(delivery.user, "email", None)
        if not to_email:
            raise TemporaryProviderError(code="no_recipient", msg="No email")
        msg = EmailMultiAlternatives(subject, text, to=[to_email])
        if html:
            msg.attach_alternative(html, "text/html")
        msg_id = msg.send()  # returns # of successfully delivered messages
        return ProviderResponse(provider="django_email", message_id=str(msg_id))


# registry
PROVIDERS = {
    "in_app": InAppProvider(),
    "email": EmailProvider(),
    # "sms": TwilioProvider(), etc...
}

def choose_provider(channel: str) -> BaseProvider:
    return PROVIDERS[channel]
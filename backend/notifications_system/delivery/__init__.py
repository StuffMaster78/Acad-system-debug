from .email import EmailBackend
from .sms import SMSBackend
from .push import PushBackend
from .in_app import InAppBackend
from .webhook import WebhookBackend

CHANNEL_BACKENDS = {
    "email": EmailBackend,
    "sms": SMSBackend,
    "push": PushBackend,
    "in_app": InAppBackend,
    "webhook": WebhookBackend,
    # Add other backends like "telegram": TelegramBackend, etc.
    # as they are implemented.
}
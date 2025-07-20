from .email import EmailBackend
from .sms import SMSBackend
from .push import PushBackend
from .websocket import WebSocketBackend
from .in_app import InAppBackend

CHANNEL_BACKENDS = {
    "email": EmailBackend,
    "sms": SMSBackend,
    "push": PushBackend,
    "ws": WebSocketBackend,
    "in_app": InAppBackend,
}
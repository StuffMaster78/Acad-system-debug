from django.conf import settings

def channel_enabled(channel: str) -> bool:
    disabled = set(getattr(settings, "DISABLED_CHANNELS", []))
    return channel not in disabled

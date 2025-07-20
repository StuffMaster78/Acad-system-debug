FORCED_CHANNELS = {}

def register_forced_channel(event_key, channels: list):
    """
    Registers a channel or list of channels that should always be used for a specific event.
    If the event already has forced channels, they will be replaced.
    """
    FORCED_CHANNELS[event_key] = channels

def get_forced_channels(event_key: str) -> list:
    """
    Returns a list of channels that are forced for a specific event.
    If no channels are forced, returns an empty list.
    """
    return FORCED_CHANNELS.get(event_key, [])
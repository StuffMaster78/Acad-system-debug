from collections import defaultdict
from typing import Dict, List

NOTIFICATION_TEMPLATES = defaultdict(dict)
FORCED_CHANNELS = defaultdict(set)

def register_notification_template(event_key: str, channel: str, template_name: str):
    """
    Registers a notification template for a specific event and channel.
    """
    NOTIFICATION_TEMPLATES[event_key][channel] = template_name

def register_forced_channel(event_key: str, channel: str):
    """
    Registers a channel that should always be used for a specific event.
    """
    FORCED_CHANNELS[event_key].add(channel)

def get_notification_template(event_key: str, channel: str) -> str:
    """
    Returns the template name for a given event and channel.
    If no specific template is registered, returns a default template.
    """
    return NOTIFICATION_TEMPLATES.get(event_key, {}).get(channel, 'default_template.html')

def get_forced_channels(event_key: str) -> set:
    """
    Returns a set of channels that are forced for a specific event.
    If no channels are forced, returns an empty set.
    """
    return FORCED_CHANNELS.get(event_key, set())



# Define the role-based notification bindings
# This dictionary maps user roles to the events they should receive notifications for and the channels used.
# The keys are user roles, and the values are dictionaries where keys are event names and values are lists of channels.
# This allows for flexible and extensible notification management based on user roles.
# Example: ROLE_NOTIFICATION_BINDINGS['client']['order.created'] = ['email', 'in_app']
# This means that clients will receive notifications for 'order.created' events via both email and in-app notifications.








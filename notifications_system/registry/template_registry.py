from collections import defaultdict
from typing import Dict, List

NOTIFICATION_TEMPLATES = defaultdict(dict)

def register_notification_template(
        event_key: str, channel: str, template_name: str
) -> None:
    """
    Registers a notification template
    for a specific event and channel.
    """
    NOTIFICATION_TEMPLATES[event_key][channel] = template_name



def get_notification_template(
        event_key: str, channel: str
) -> str:
    """
    Returns the template name for
    a given event and channel.
    If no specific template is registered,
    returns a default template.
    """
    return NOTIFICATION_TEMPLATES.get(event_key, {}).get(
        channel, 'default_template.html'
    )

_event_template_registry = defaultdict(list)

def register_template(event_name, template_cls):
    _event_template_registry[event_name].append(template_cls)

def get_templates_for_event(event_name):
    return _event_template_registry.get(event_name, [])

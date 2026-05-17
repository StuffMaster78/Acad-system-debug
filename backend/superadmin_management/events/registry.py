# superadmin_management/events/registry.py

from superadmin_management.events.event_bus import EventBus
from superadmin_management.events.governance_events import (
    UserCreatedEvent,
    UserSuspendedEvent,
    UserBlacklistedEvent,
)

from superadmin_management.event_handlers.user_handlers import (
    handle_user_created,
)
from superadmin_management.event_handlers.blacklist_handlers import (
    handle_user_blacklisted,
)
from superadmin_management.event_handlers.suspension_handlers import (
    handle_user_suspended,
)


def register_handlers():
    EventBus.subscribe(UserCreatedEvent, handle_user_created)
    EventBus.subscribe(UserSuspendedEvent, handle_user_suspended)
    EventBus.subscribe(UserBlacklistedEvent, handle_user_blacklisted)
import logging
import importlib
from typing import Callable, Dict, Optional, Set
from django.apps import apps
from django.conf import settings

logger = logging.getLogger(__name__)

ROLE_RESOLVERS: Dict[str, Callable] = {}
ROLE_CHANNELS: Dict[str, Dict[str, Set[str]]] = {}

DEFAULT_ROLE_CHANNELS: Dict[str, Dict[str, Set[str]]] = getattr(
    settings,
    "NOTIFICATION_ROLE_DEFAULTS",
    {},
)


def get_user_model():
    """Lazily fetch the User model."""
    return apps.get_model(settings.AUTH_USER_MODEL)


def register_role(
    role: str,
    resolver: Callable,
    channels: Optional[Dict[str, Set[str]]] = None,
):
    """Register a role's resolver and channels.

    Args:
        role (str): Role name (e.g., "client", "admin").
        resolver (Callable): Function to resolve user from context.
        channels (Optional[Dict[str, Set[str]]]): Event-channel mapping.

    Notes:
        - Warns if role is already registered.
        - Merges channels with defaults from settings.
    """
    if role in ROLE_RESOLVERS:
        logger.warning(
            "[notifications] Role '%s' already registered. Overwriting.",
            role,
        )

    ROLE_RESOLVERS[role] = resolver

    merged_channels = dict(DEFAULT_ROLE_CHANNELS.get(role, {}))
    if channels:
        for event_key, chans in channels.items():
            merged_channels[event_key] = set(chans)

    ROLE_CHANNELS[role] = merged_channels or {"*": set()}


def resolve_role_user(role: str, context: Dict):
    """Resolve a user for the given role.

    Args:
        role (str): Role name.
        context (Dict): Context dict with objects (e.g., 'order').

    Returns:
        Optional[User]: User instance or None.
    """
    resolver = ROLE_RESOLVERS.get(role)
    if not resolver:
        logger.warning(
            "[notifications] No resolver found for role '%s'", role
        )
        return None
    return resolver(context)


def get_channels_for_role(event_key: str, role: str) -> Set[str]:
    """Get notification channels for a given role and event.

    Args:
        event_key (str): Event identifier.
        role (str): Role name.

    Returns:
        Set[str]: Set of channel names.
    """
    role_channels = ROLE_CHANNELS.get(role, {})
    return role_channels.get(event_key, role_channels.get("*", set()))


def autodiscover_roles():
    """Auto-import `notifications_roles` from each installed app.

    Notes:
        - Skips if the app has no `notifications_roles` module.
        - Logs errors if import fails.
    """
    for app_config in apps.get_app_configs():
        try:
            importlib.import_module(
                f"{app_config.name}.notifications_roles"
            )
            logger.debug(
                "[notifications] Loaded roles from %s",
                app_config.name,
            )
        except ModuleNotFoundError as e:
            if "notifications_roles" not in str(e):
                raise
        except Exception as e:
            logger.error(
                "[notifications] Failed to load roles from %s: %s",
                app_config.name,
                e,
            )


def list_registered_roles() -> Dict[str, Dict]:
    """List all registered roles and their configuration.

    Returns:
        Dict[str, Dict]: Mapping of role to resolver and channels.
    """
    return {
        role: {
            "resolver": resolver.__name__,
            "channels": {
                k: sorted(v) for k, v in ROLE_CHANNELS[role].items()
            },
        }
        for role, resolver in ROLE_RESOLVERS.items()
    }
def clear_role_registry():
    """Clear the role registry."""
    ROLE_RESOLVERS.clear()
    ROLE_CHANNELS.clear()
    logger.info("[notifications] Cleared role registry.")

# def resolve_role_user(
#         role: str, context: Dict
# ) -> Optional["UserType"]:
#     """Resolve a user for the given role using the provided context.

#     Args:
#         role (str): Logical role name (e.g., "client", "writer").
#         context (Dict): Dictionary containing objects like 'order'.

#     Returns:
#         Optional[User]: The user instance tied to the role, or None.
#     """
#     order = context.get("order")

#     if role == "client":
#         return getattr(order, "client", None)

#     if role == "writer":
#         return getattr(order, "writer", None)

#     if role == "support":
#         # You can plug in support-assigning logic here
#         return get_active_support_user(order)
    
#     if role == "admin":
#         return UserType.objects.filter(is_staff=True).first()
    
#     if role == "super_admin":
#         return UserType.objects.filter(is_superuser=True).first()

#     if role == "editor":
#         return UserType.objects.filter(is_editor=True).first()

#     return None

# def get_active_support_user(order):
#     """Placeholder function to get an active support user for an order."""
#     # Implement your logic to fetch the active support user
#     return None  # Replace with actual logic to retrieve the support user
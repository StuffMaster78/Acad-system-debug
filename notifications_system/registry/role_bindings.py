from typing import Optional, Dict, TYPE_CHECKING, Callable, Set
from django.apps import apps
from collections import defaultdict

if TYPE_CHECKING:
    from users.models import User as UserType


# --- Lazy User model getter ---
def get_user_model():
    """Lazily fetch the User model to avoid AppRegistryNotReady errors."""
    return apps.get_model('users', 'User')


# --- Registries ---
ROLE_RESOLVERS: Dict[str, Callable[[Dict], Optional["UserType"]]] = {}
ROLE_CHANNELS: Dict[str, Dict[str, Set[str]]] = defaultdict(dict)
# Structure: ROLE_CHANNELS[role][event_key] = {"email", "webhook", ...}


# --- Registration helpers ---
def register_role_resolver(role: str):
    """Decorator to register a function that resolves a user for a given role."""
    def decorator(func: Callable[[Dict], Optional["UserType"]]):
        ROLE_RESOLVERS[role] = func
        return func
    return decorator


def register_role_channels(role: str, event_key: str, channels: Set[str]):
    """Register notification channels for a given role and event."""
    ROLE_CHANNELS[role][event_key] = channels


# --- Core functions ---
def resolve_role_user(role: str, context: Dict) -> Optional["UserType"]:
    """Resolves a user for a given role using the provided context."""
    resolver = ROLE_RESOLVERS.get(role)
    return resolver(context) if resolver else None


def get_channels_for_role(event_key: str, role: str) -> Set[str]:
    """
    Returns notification channels for a given role and event key.
    Falls back to a default ('*') event if no specific match.
    """
    role_channels = ROLE_CHANNELS.get(role, {})
    return role_channels.get(event_key) or role_channels.get("*", set())


# --- Example resolvers ---
@register_role_resolver("client")
def _resolve_client(context: Dict):
    return getattr(context.get("order"), "client", None)


@register_role_resolver("writer")
def _resolve_writer(context: Dict):
    return getattr(context.get("order"), "writer", None)


@register_role_resolver("support")
def _resolve_support(context: Dict):
    return get_active_support_user(context.get("order"))


@register_role_resolver("admin")
def _resolve_admin(context: Dict):
    return get_user_model().objects.filter(is_staff=True).first()


@register_role_resolver("super_admin")
def _resolve_super_admin(context: Dict):
    return get_user_model().objects.filter(is_superuser=True).first()


@register_role_resolver("editor")
def _resolve_editor(context: Dict):
    return get_user_model().objects.filter(is_editor=True).first()


# --- Example channels ---
register_role_channels("client", "*", {"email", "in_app"})  # default for all events
register_role_channels("writer", "order_created", {"email", "in_app"})
register_role_channels("writer", "order_assigned", {"email", "in_app", "webhook", "websocket"})
register_role_channels("support", "*", {"email", "in_app", "websocket"})
register_role_channels("admin", "*", {"email", "in_app", "webhook", "websocket"})
register_role_channels("super_admin", "*", {"email", "in_app", "webhook", "websocket", "sms"})
register_role_channels("editor", "*", {"email", "in_app", "webhook", "websocket", "sms", "telegram"})


# --- Example support assignment logic ---
def get_active_support_user(order) -> Optional["UserType"]:
    """Example dynamic support assignment."""
    return get_user_model().objects.filter(is_staff=True).order_by("?").first()
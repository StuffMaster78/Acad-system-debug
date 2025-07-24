from typing import Optional, Dict, TYPE_CHECKING
from django.contrib.auth import get_user_model

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser as UserType
else:
    UserType = get_user_model()

User = get_user_model()


def resolve_role_user(
        role: str, context: Dict
) -> Optional["UserType"]:
    """
    Resolves a user for a given role using the provided context.

    Args:
        role (str): Logical role name (e.g., "client", "writer").
        context (Dict): Dictionary containing objects like 'order'.

    Returns:
        Optional[User]: The user instance tied to the role, or None.
    """
    order = context.get("order")

    if role == "client":
        return getattr(order, "client", None)

    if role == "writer":
        return getattr(order, "writer", None)

    if role == "support":
        # You can plug in support-assigning logic here
        return get_active_support_user(order)
    
    if role == "admin":
        return User.objects.filter(is_staff=True).first()
    
    if role == "super_admin":
        return User.objects.filter(is_superuser=True).first()
    
    if role == "editor":
        return User.objects.filter(is_editor=True).first()

    return None


def get_active_support_user(
        order
) -> Optional["UserType"]:
    """
    Dummy function to simulate dynamic resolution.
    Replace with logic for rotating or assigned support agents.
    """
    # Example: assign based on order category, load, region, etc.
    return User.objects.filter(is_staff=True).order_by("?").first()
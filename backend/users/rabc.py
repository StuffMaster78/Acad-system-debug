class Role:
    ADMIN = "admin"
    SUPERADMIN = "superadmin"
    WRITER = "writer"
    CLIENT = "client"
    EDITOR = "editor"
    SUPPORT = "support"

    ALL = [ADMIN, SUPERADMIN, WRITER, CLIENT, EDITOR, SUPPORT]


def has_role(user, *roles):
    if not user.is_authenticated:
        return False
    return getattr(user.profile, "role", None) in roles


def require_role(user, *roles):
    if not has_role(user, *roles):
        raise PermissionError(
            f"Access denied. Required role(s): {roles}. "
            f"User has: {getattr(user.profile, 'role', None)}"
        )
    
def is_superadmin(user):
    """
    Check if the user has superadmin role.
    """
    return has_role(user, Role.SUPERADMIN)

def is_admin(user):
    """
    Check if the user has admin role.
    """
    return has_role(user, Role.ADMIN)

def is_writer(user):
    """
    Check if the user has writer role.
    """
    return has_role(user, Role.WRITER)

def is_client(user):
    """
    Check if the user has client role.
    """
    return has_role(user, Role.CLIENT)

def is_editor(user):
    """
    Check if the user has editor role.
    """
    return has_role(user, Role.EDITOR)

def is_support(user):
    """
    Check if the user has support role.
    """
    return has_role(user, Role.SUPPORT)
def require_superadmin(user):
    """
    Require the user to have superadmin role.
    """
    require_role(user, Role.SUPERADMIN)

def require_admin(user):
    """
    Require the user to have admin role.
    """
    require_role(user, Role.ADMIN)

def require_writer(user):
    """
    Require the user to have writer role.
    """
    require_role(user, Role.WRITER)

def require_client(user):
    """
    Require the user to have client role.
    """
    require_role(user, Role.CLIENT)

def require_editor(user):
    """
    Require the user to have editor role.
    """
    require_role(user, Role.EDITOR)

def require_support(user):
    """
    Require the user to have support role.
    """
    require_role(user, Role.SUPPORT)
def require_any_role(user, *roles):
    """
    Require the user to have any of the specified roles.
    """
    if not has_role(user, *roles):
        raise PermissionError(
            f"Access denied. Required role(s): {roles}. "
            f"User has: {getattr(user.profile, 'role', None)}"
        )
    
def require_all_roles(user, *roles):
    """
    Require the user to have all of the specified roles.
    """
    for role in roles:
        if not has_role(user, role):
            raise PermissionError(
                f"Access denied. Required role(s): {roles}. "
                f"User has: {getattr(user.profile, 'role', None)}"
            )
        
def require_no_role(user):
    """
    Require the user to have no role.
    """
    if user.is_authenticated and getattr(user.profile, "role", None) is not None:
        raise PermissionError(
            f"Access denied. User has a role: {getattr(user.profile, 'role', None)}"
        )
    
def require_role_or_no_role(user, *roles):
    """
    Require the user to have any of the specified roles or no role at all.
    """
    if not has_role(user, *roles) and getattr(user.profile, "role", None) is not None:
        raise PermissionError(
            f"Access denied. Required role(s): {roles}. "
            f"User has: {getattr(user.profile, 'role', None)}"
        )   
    
def require_role_or_any_role(user, *roles):
    """
    Require the user to have any of the specified roles or any role at all.
    """
    if not has_role(user, *roles) and getattr(user.profile, "role", None) is None:
        raise PermissionError(
            f"Access denied. Required role(s): {roles}. "
            f"User has: {getattr(user.profile, 'role', None)}"
        )
    

def require_role_or_all_roles(user, *roles):
    """
    Require the user to have any of the specified roles or all roles at once.
    """
    if not has_role(user, *roles) and getattr(user.profile, "role", None) not in roles:
        raise PermissionError(
            f"Access denied. Required role(s): {roles}. "
            f"User has: {getattr(user.profile, 'role', None)}"
        )
def require_role_or_no_role_or_any_role(user, *roles):
    """
    Require the user to have any of the specified roles, no role at all, or any role.
    """
    if not has_role(user, *roles) and getattr(user.profile, "role", None) not in roles:
        raise PermissionError(
            f"Access denied. Required role(s): {roles}. "
            f"User has: {getattr(user.profile, 'role', None)}"
        )

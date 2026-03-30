"""
User Group Management Service

Centralized service for creating and managing Django user groups with proper
permissions assignment based on user roles.
"""
from django.contrib.auth.models import Group, Permission
from django.db import transaction
from django.core.exceptions import ValidationError
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class UserGroupService:
    """
    Service for managing user groups and permissions.
    Provides centralized, consistent group creation and management.
    """
    
    # Role-based group definitions
    # Note: Only include permissions that exist in Django's Permission model
    # Format: 'app_label.permission_codename' or just 'permission_codename' (will search all apps)
    ROLE_GROUPS = {
        'admin': {
            'name': 'Admin',
            'description': 'Administrators with full system access',
            'permissions': [
                # User management
                'users.add_user', 'users.change_user', 'users.delete_user', 'users.view_user',
                # Order management
                'orders.add_order', 'orders.change_order', 'orders.delete_order', 'orders.view_order',
                # Special orders
                'special_orders.add_specialorder', 'special_orders.change_specialorder', 
                'special_orders.delete_specialorder', 'special_orders.view_specialorder',
            ]
        },
        'superadmin': {
            'name': 'Super Admin',
            'description': 'Super administrators with unrestricted access',
            'permissions': [
                # Superadmins get all permissions via is_superuser=True
                # But we can add specific ones here if needed
            ]
        },
        'support': {
            'name': 'Support',
            'description': 'Support staff with ticket and order management access',
            'permissions': [
                'orders.view_order', 'orders.change_order',
                'users.view_user',
                'tickets.add_ticket', 'tickets.change_ticket', 'tickets.view_ticket',
            ]
        },
        'editor': {
            'name': 'Editor',
            'description': 'Editors with content and order editing access',
            'permissions': [
                'orders.view_order', 'orders.change_order',
                'users.view_user',
                'blog_pages_management.add_blogpost', 'blog_pages_management.change_blogpost',
                'blog_pages_management.view_blogpost',
            ]
        },
        'writer': {
            'name': 'Writer',
            'description': 'Writers with order submission and viewing access',
            'permissions': [
                'orders.view_order',
                'orders.add_order',
                'users.view_user',  # Limited to own profile
            ]
        },
        'client': {
            'name': 'Client',
            'description': 'Clients with order viewing and creation access',
            'permissions': [
                'orders.view_order',
                'orders.add_order',
                'users.view_user',  # Limited to own profile
            ]
        },
    }
    
    @classmethod
    def get_or_create_group(cls, role: str, update_permissions: bool = True) -> tuple[Group, bool]:
        """
        Get or create a group for a specific role.
        
        Args:
            role: User role (admin, superadmin, support, editor, writer, client)
            update_permissions: Whether to update permissions if group exists
            
        Returns:
            Tuple of (Group instance, created boolean)
            
        Raises:
            ValidationError: If role is invalid
        """
        if role not in cls.ROLE_GROUPS:
            raise ValidationError(f"Invalid role: {role}. Must be one of {list(cls.ROLE_GROUPS.keys())}")
        
        group_config = cls.ROLE_GROUPS[role]
        group_name = group_config['name']
        
        with transaction.atomic():
            group, created = Group.objects.get_or_create(name=group_name)
            
            # Update description if group was just created or if updating
            if created or update_permissions:
                # Note: Django Group model doesn't have description field by default
                # If you add a custom field, update it here
                pass
            
            # Assign permissions
            if created or update_permissions:
                cls._assign_permissions_to_group(group, role)
            
            return group, created
    
    @classmethod
    def _assign_permissions_to_group(cls, group: Group, role: str) -> None:
        """
        Assign permissions to a group based on role.
        
        Args:
            group: Django Group instance
            role: User role
        """
        group_config = cls.ROLE_GROUPS[role]
        permission_codenames = group_config.get('permissions', [])
        
        if not permission_codenames:
            # Superadmin gets all permissions
            if role == 'superadmin':
                # Superadmins typically have is_superuser=True, so they get all permissions
                # But we can still add specific permissions if needed
                logger.info(f"Superadmin group '{group.name}' - using superuser permissions")
                return
            return
        
        # Get permissions - handle both 'app.codename' and 'codename' formats
        permission_objects = []
        for perm_spec in permission_codenames:
            if '.' in perm_spec:
                # Format: 'app_label.codename'
                app_label, codename = perm_spec.split('.', 1)
                perm = Permission.objects.filter(
                    content_type__app_label=app_label,
                    codename=codename
                ).first()
            else:
                # Format: 'codename' - search across all apps
                perm = Permission.objects.filter(codename=perm_spec).first()
            
            if perm:
                permission_objects.append(perm)
            else:
                logger.debug(f"Permission not found: {perm_spec}")
        
        found_count = len(permission_objects)
        total_count = len(permission_codenames)
        
        if found_count < total_count:
            logger.info(
                f"Found {found_count}/{total_count} permissions for role '{role}'. "
                f"Some permissions may not exist in the system."
            )
        
        # Clear existing permissions and assign new ones
        group.permissions.clear()
        if permission_objects:
            group.permissions.add(*permission_objects)
        
        logger.info(
            f"Assigned {len(permission_objects)} permissions to group '{group.name}' for role '{role}'"
        )
    
    @classmethod
    def assign_user_to_group(cls, user, role: Optional[str] = None) -> Group:
        """
        Assign a user to the appropriate group based on their role.
        
        Args:
            user: User instance
            role: User role (if None, uses user.role)
            
        Returns:
            Group instance that was assigned
        """
        if role is None:
            role = getattr(user, 'role', None)
        
        if not role:
            raise ValidationError("Role must be provided or user must have a role attribute")
        
        group, _ = cls.get_or_create_group(role)
        user.groups.add(group)
        
        logger.info(f"Assigned user '{user.username}' to group '{group.name}'")
        return group
    
    @classmethod
    def remove_user_from_role_groups(cls, user) -> None:
        """
        Remove user from all role-based groups.
        
        Args:
            user: User instance
        """
        role_group_names = [config['name'] for config in cls.ROLE_GROUPS.values()]
        user.groups.filter(name__in=role_group_names).delete()
        logger.info(f"Removed user '{user.username}' from role-based groups")
    
    @classmethod
    def update_user_groups(cls, user, new_role: str) -> Group:
        """
        Update user's groups when role changes.
        
        Args:
            user: User instance
            new_role: New role to assign
            
        Returns:
            Group instance that was assigned
        """
        # Remove from old role groups
        cls.remove_user_from_role_groups(user)
        
        # Assign to new role group
        return cls.assign_user_to_group(user, new_role)
    
    @classmethod
    def ensure_all_groups_exist(cls) -> Dict[str, tuple[Group, bool]]:
        """
        Ensure all role-based groups exist with proper permissions.
        Useful for initialization/migration scripts.
        
        Returns:
            Dictionary mapping role to (Group, created) tuple
        """
        results = {}
        for role in cls.ROLE_GROUPS.keys():
            try:
                group, created = cls.get_or_create_group(role, update_permissions=True)
                results[role] = (group, created)
                logger.info(f"Ensured group exists for role '{role}': {group.name} (created: {created})")
            except Exception as e:
                logger.error(f"Failed to create group for role '{role}': {e}")
                results[role] = (None, False)
        
        return results
    
    @classmethod
    def get_group_for_role(cls, role: str) -> Optional[Group]:
        """
        Get the group for a specific role.
        
        Args:
            role: User role
            
        Returns:
            Group instance or None if role is invalid
        """
        if role not in cls.ROLE_GROUPS:
            return None
        
        group_name = cls.ROLE_GROUPS[role]['name']
        try:
            return Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return None
    
    @classmethod
    def get_user_role_group(cls, user) -> Optional[Group]:
        """
        Get the role-based group for a user.
        
        Args:
            user: User instance
            
        Returns:
            Group instance or None
        """
        role = getattr(user, 'role', None)
        if not role:
            return None
        
        return cls.get_group_for_role(role)
    
    @classmethod
    def sync_user_groups(cls, user) -> Group:
        """
        Sync user's groups to match their current role.
        Removes from old groups and adds to correct group.
        
        Args:
            user: User instance
            
        Returns:
            Group instance that was assigned
        """
        role = getattr(user, 'role', None)
        if not role:
            raise ValidationError("User must have a role attribute")
        
        return cls.update_user_groups(user, role)


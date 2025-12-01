# User Groups Creation Refinement

## Overview

A centralized service has been created to refine and standardize user group creation and management across the application. This replaces ad-hoc group creation with a consistent, maintainable approach.

## What Was Changed

### 1. New Service: `UserGroupService`

**Location**: `backend/users/services/group_service.py`

A comprehensive service class that provides:

- **Centralized group definitions**: All role-based groups are defined in one place with their permissions
- **Automatic permission assignment**: Permissions are automatically assigned based on role
- **Consistent group creation**: Uses `get_or_create` with proper transaction handling
- **Role-based group management**: Methods to assign, remove, and sync user groups
- **Error handling**: Graceful fallbacks and logging

### 2. Role-Based Groups

The service defines groups for all user roles:

- **Admin**: Full system access (12 permissions)
- **Super Admin**: Unrestricted access (uses Django's superuser permissions)
- **Support**: Ticket and order management (6 permissions)
- **Editor**: Content and order editing (6 permissions)
- **Writer**: Order submission and viewing (3 permissions)
- **Client**: Order viewing and creation (3 permissions)

### 3. Updated Existing Code

**Files Updated**:
- `backend/admin_management/services/admin_services.py`: Uses `UserGroupService` instead of direct `Group.objects.get_or_create()`
- `backend/admin_management/managers.py`: Uses `UserGroupService` for permission assignment
- `backend/users/signals.py`: Added signals to automatically assign groups on user creation and role changes

### 4. New Management Command

**Command**: `python manage.py ensure_user_groups`

Ensures all role-based groups exist with proper permissions. Useful for:
- Initial setup
- After migrations
- Permission updates

## Key Features

### Automatic Group Assignment

Users are automatically assigned to groups when:
1. A new user is created (via `post_save` signal)
2. A user's role changes (via `pre_save` signal)

### Permission Handling

- Supports both `app_label.codename` and `codename` formats
- Gracefully handles missing permissions (logs warnings, continues)
- Automatically clears and reassigns permissions when updating groups

### Transaction Safety

All group operations are wrapped in database transactions to ensure consistency.

## Usage Examples

### Assign User to Group

```python
from users.services.group_service import UserGroupService

# Automatically uses user.role
UserGroupService.assign_user_to_group(user)

# Or specify role explicitly
UserGroupService.assign_user_to_group(user, role='admin')
```

### Update User Groups on Role Change

```python
UserGroupService.update_user_groups(user, new_role='editor')
```

### Sync User Groups

```python
# Ensures user is in the correct group for their current role
UserGroupService.sync_user_groups(user)
```

### Ensure All Groups Exist

```python
results = UserGroupService.ensure_all_groups_exist()
# Returns dict mapping role to (Group, created) tuple
```

## Benefits

1. **Consistency**: All groups are created the same way across the application
2. **Maintainability**: Permission changes only need to be made in one place
3. **Reliability**: Proper error handling and transaction management
4. **Automation**: Groups are automatically assigned when users are created or roles change
5. **Flexibility**: Easy to add new roles or modify permissions

## Migration Notes

- Existing groups are preserved
- Running `ensure_user_groups` will update permissions for existing groups
- The service includes fallback logic to the old method if needed

## Testing

Run the management command to verify all groups are created correctly:

```bash
docker-compose run --rm web python manage.py ensure_user_groups
```

Expected output:
```
✅ Groups ensured: X created, Y already existed
- admin      → Admin         (12 permissions)
- superadmin → Super Admin   (0 permissions)
- support    → Support       (6 permissions)
- editor     → Editor        (6 permissions)
- writer     → Writer        (3 permissions)
- client     → Client        (3 permissions)
```


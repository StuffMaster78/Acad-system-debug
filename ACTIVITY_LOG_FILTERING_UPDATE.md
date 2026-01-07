# Activity Log Filtering Update

## Problem

Users (writers, clients, support, editors) were seeing too many activity notifications, including actions performed by others. The user wanted to limit activity notifications to only show actions they performed themselves.

## Solution

Updated activity log filtering to only show actions where the user is either:
- The `user` field (action is associated with them)
- The `triggered_by` field (they performed/triggered the action)

This ensures users only see "You did X" type notifications.

## Changes Made

### 1. Updated `ActivityLogViewSet.get_queryset()`

**Before**:
- Support: Could see all activities from writers, editors, clients
- Writers: Could see their own activities + activities on their orders
- Clients: Could see their own activities + activities on their orders
- Editors: Could see their own activities

**After**:
- Support, Writers, Clients, Editors: Only see actions they performed
  - Filter: `user=user OR triggered_by=user`
- Admin/Superadmin: Still see all activities (unchanged)

### 2. Updated `UserActivityFeedViewSet.get_queryset()`

**Before**:
- Support: Could see all client/writer/editor activity
- Writers: Could see their own actions + actions on orders assigned to them
- Clients: Could see their own actions + actions on their orders

**After**:
- Support, Writers, Clients, Editors: Only see actions they performed
  - Filter: `user=user OR triggered_by=user`
- Admin/Superadmin: Still see all activities (unchanged)

## Examples

### What Users Will See Now:

**Writer**:
- ✅ "You uploaded an order"
- ✅ "You sent a message to client #123"
- ✅ "You submitted order #456"
- ❌ "Client uploaded new files" (removed - not their action)
- ❌ "Client sent you a message" (removed - not their action)

**Client**:
- ✅ "You uploaded new files"
- ✅ "You sent a message to writer"
- ✅ "You placed order #789"
- ❌ "Writer uploaded files" (removed - not their action)
- ❌ "Writer sent you a message" (removed - not their action)

**Support/Editor**:
- ✅ "You sent a message to client #123"
- ✅ "You reviewed order #456"
- ❌ "Client uploaded files" (removed - not their action)
- ❌ "Writer submitted order" (removed - not their action)

**Admin/Superadmin**:
- ✅ See all activities (unchanged - full visibility)

## Files Changed

1. `backend/activity/views.py`
   - Updated `ActivityLogViewSet.get_queryset()` 
   - Updated `UserActivityFeedViewSet.get_queryset()`

## Benefits

✅ **Cleaner Activity Feed**: Users only see relevant actions they performed
✅ **Better UX**: "You did X" notifications are more meaningful
✅ **Reduced Noise**: No more seeing actions from other users
✅ **Privacy**: Users don't see activities they didn't perform
✅ **Admin Visibility**: Admins/superadmins still see everything for oversight

## Testing

To verify the changes:

1. **As a Writer**:
   - Send a message → Should see "You sent a message"
   - Upload files → Should see "You uploaded files"
   - Should NOT see client actions

2. **As a Client**:
   - Upload files → Should see "You uploaded files"
   - Send a message → Should see "You sent a message"
   - Should NOT see writer actions

3. **As Support/Editor**:
   - Send a message → Should see "You sent a message"
   - Should NOT see client/writer actions

4. **As Admin/Superadmin**:
   - Should see all activities (unchanged)

## Notes

- The filtering uses `user=user OR triggered_by=user` to catch both:
  - Actions where the user is the subject (`user` field)
  - Actions the user performed (`triggered_by` field)
- Admin/Superadmin maintain full visibility for oversight purposes
- This change applies to both the main activity log endpoint and the user feed endpoint


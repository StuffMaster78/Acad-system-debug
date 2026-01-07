# Messaging System Visibility Fix

## Problem

1. **Message Count Bug**: The system showed 20 unread messages, but when opening messages, only 6-11 messages were visible.
2. **Incorrect Visibility Rules**: The visibility rules didn't match the matchmaking platform requirements.

## Root Cause

The `get_unread_count` method was counting ALL unread messages in a thread, but `get_visible_messages` was filtering messages based on visibility rules. This caused a mismatch:
- **Count**: 20 messages (all unread messages)
- **Visible**: 6-11 messages (filtered by visibility rules)

## Solution

### 1. Fixed Unread Count Calculation

Updated `get_unread_count` in `backend/communications/serializers.py` to only count messages that are visible to the user:

```python
def get_unread_count(self, obj):
    """
    Get the count of unread messages for the current user in this thread.
    Only counts messages that are visible to the user (matches get_visible_messages logic).
    This ensures the count matches the actual visible messages.
    """
    request = self.context.get("request")
    if not request or not request.user:
        return 0
    user = request.user
    
    # Get visible messages using the same logic as get_visible_messages
    from communications.services.messages import MessageService
    visible_messages = MessageService.get_visible_messages(user, obj)
    
    # Count unread messages from visible messages only
    unread_count = visible_messages.exclude(read_by=user).count()
    
    return unread_count
```

### 2. Implemented Proper Visibility Rules

Updated `get_visible_messages` in `backend/communications/services/messages.py` to match the matchmaking platform requirements:

#### Visibility Rules:

1. **Admin/Superadmin**: See ALL messages (all communications)
   - No filtering - can see everything

2. **Support**: See messages where:
   - They are sender/recipient OR
   - Client sends to support (all support users can read)

3. **Editor**: See messages where:
   - They are sender/recipient OR
   - Client sends to editor (all editors can read)

4. **Admin** (regular admin, not superadmin): See messages where:
   - They are sender/recipient OR
   - Client sends to admin (all admins can read)

5. **Client**: See messages where:
   - They are sender/recipient OR
   - Writer sends to them (only that specific client)

6. **Writer**: See messages where:
   - They are sender/recipient OR
   - Client sends to them (only that specific writer)

### 3. Unified Visibility Logic

Updated `CommunicationMessageViewSet.get_queryset()` in `backend/communications/views.py` to use `MessageService.get_visible_messages` for all roles, ensuring consistent filtering across the system.

## Files Changed

1. `backend/communications/services/messages.py`
   - Updated `get_visible_messages()` with proper visibility rules

2. `backend/communications/serializers.py`
   - Updated `get_unread_count()` to count only visible messages

3. `backend/communications/views.py`
   - Updated `CommunicationMessageViewSet.get_queryset()` to use unified visibility logic

## Benefits

✅ **Accurate Counts**: Unread count now matches visible messages
✅ **Proper Visibility**: Messages are filtered according to matchmaking platform rules
✅ **Consistent Logic**: All message queries use the same visibility logic
✅ **Better UX**: Users see accurate message counts and only messages they should see

## Testing

To verify the fix:

1. **Check Message Counts**: 
   - Open a thread with messages
   - Verify the unread count matches the number of visible unread messages

2. **Test Visibility Rules**:
   - As a client, send a message to support → All support users should see it
   - As a client, send a message to editor → All editors should see it
   - As a client, send a message to admin → All admins should see it
   - As a writer, send a message to client → Only that specific client should see it
   - As a client, send a message to writer → Only that specific writer should see it
   - As admin/superadmin → Should see all messages

3. **Verify Count Accuracy**:
   - Count should match the number of visible messages
   - No more discrepancies between count and visible messages

## Notes

- The visibility rules are designed for a matchmaking platform where:
  - Staff (support, editor, admin) can see client communications to their role
  - Clients and writers have private 1-on-1 communications
  - Admins/superadmins have full visibility for oversight


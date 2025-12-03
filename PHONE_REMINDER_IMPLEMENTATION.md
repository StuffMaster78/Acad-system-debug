# Phone Number Reminder Implementation

## Overview

Implemented a reminder system to prompt clients to update their working phone number for order fulfillment coordination and urgent contact purposes.

---

## Features Implemented

### 1. Phone Reminder Service
- **File**: `backend/users/services/phone_reminder_service.py`
- **Features**:
  - Checks if user has phone number (UserProfile or ClientProfile)
  - Determines if reminder is needed (clients only)
  - Provides reminder information with reasons
  - Context-aware reminder (shows in order context)
  - Sends notification reminders

### 2. Serializer Integration
- **Files**: `backend/users/serializers_legacy.py`
- **Updated Serializers**:
  - `UserDetailSerializer`: Added `phone_reminder` field
  - `UserProfileSerializer`: Added `phone_reminder` field
- **Response Format**:
  ```json
  {
    "phone_reminder": {
      "needs_reminder": true,
      "has_phone_number": false,
      "phone_number": null,
      "message": "Please update your phone number...",
      "reasons": [
        "Order fulfillment coordination",
        "Urgent contact when needed",
        "Better communication during order process"
      ]
    }
  }
  ```

### 3. Account Management Endpoint
- **File**: `backend/users/views/account_management.py`
- **Endpoint**: `GET /api/users/account/phone-reminder/`
- **Purpose**: Get phone reminder information for current user

### 4. Order View Integration
- **File**: `backend/orders/views/orders/base.py`
- **Updated Methods**:
  - `list()`: Includes phone reminder in order list response
  - `retrieve()`: Includes phone reminder in single order response
- **Behavior**:
  - Only shows reminder for clients
  - Only shows when user has active orders
  - Context-aware (shows in order fulfillment context)

### 5. Signal-Based Reminders
- **File**: `backend/users/signals/phone_reminder_signals.py`
- **Signal**: `post_save` on Order model
- **Behavior**:
  - Triggers when order status changes to active states
  - Sends notification reminder
  - Only for clients without phone numbers

---

## API Endpoints

### Get Phone Reminder Info
```
GET /api/users/account/phone-reminder/
```

**Response**:
```json
{
  "needs_reminder": true,
  "has_phone_number": false,
  "phone_number": null,
  "message": "Please update your phone number to help us coordinate order fulfillment and contact you urgently when needed.",
  "reasons": [
    "Order fulfillment coordination",
    "Urgent contact when needed",
    "Better communication during order process"
  ]
}
```

### Order List/Retrieve (with reminder)
```
GET /api/orders/orders/
GET /api/orders/orders/{id}/
```

**Response** (for clients without phone numbers):
```json
{
  "results": [...],
  "phone_reminder": {
    "needs_reminder": true,
    "has_phone_number": false,
    "phone_number": null,
    "message": "...",
    "reasons": [...]
  }
}
```

---

## Reminder Logic

### When Reminder is Shown
1. **User Profile**: Always included in user profile serializers
2. **Order Context**: Shown when:
   - User is a client
   - User has no phone number
   - User has active orders (pending, in_progress, submitted, etc.)

### When Reminder is NOT Shown
- User is not a client (writers, admins, etc.)
- User already has a phone number
- No active orders (for order context)

---

## Notification Reminders

### Automatic Notifications
- Sent when order status changes to active states
- Only sent to clients without phone numbers
- Uses notification system for delivery
- Event: `profile.phone_reminder`

### Notification Content
- **Message**: "Please update your phone number to help us coordinate order fulfillment and contact you urgently when needed."
- **Action URL**: `/account/settings`
- **Action Text**: "Update Phone Number"
- **Category**: `profile`
- **Priority**: `medium`

---

## Frontend Integration

### Display Options
1. **Banner/Alert**: Show at top of order pages
2. **Modal**: Show when viewing active orders
3. **Settings Page**: Show in account settings
4. **Notification**: In-app notification

### Example Frontend Usage
```javascript
// Check if reminder is needed
if (userProfile.phone_reminder?.needs_reminder) {
  showPhoneReminderBanner({
    message: userProfile.phone_reminder.message,
    reasons: userProfile.phone_reminder.reasons,
    actionUrl: '/account/settings'
  });
}

// Check in order context
if (orderResponse.phone_reminder?.needs_reminder) {
  showPhoneReminderInOrderContext(orderResponse.phone_reminder);
}
```

---

## Phone Number Storage

### Locations Checked
1. **UserProfile.phone_number** (PhoneNumberField)
2. **ClientProfile.phone_number** (CharField)

### Priority
- Checks UserProfile first
- Falls back to ClientProfile if UserProfile doesn't exist or has no phone

---

## Testing Recommendations

1. **Test Reminder Display**:
   - Create client without phone number
   - View profile → Should see reminder
   - View orders → Should see reminder if active orders exist

2. **Test Notification**:
   - Create order for client without phone
   - Change order to active status
   - Verify notification is sent

3. **Test After Update**:
   - Update phone number
   - Verify reminder disappears
   - Verify no more notifications

4. **Test Edge Cases**:
   - Client with phone in UserProfile
   - Client with phone in ClientProfile
   - Client with phone in both
   - Non-client users (should not see reminder)

---

## Configuration

### Reminder Reasons (Configurable)
Currently hardcoded in service, but can be made configurable:
- Order fulfillment coordination
- Urgent contact when needed
- Better communication during order process

### Active Order Statuses (Configurable)
Currently defined in service:
```python
active_statuses = [
    'pending', 'in_progress', 'submitted', 'reviewed', 
    'rated', 'revision_requested', 'on_revision', 'revised'
]
```

---

## Future Enhancements

1. **Frequency Control**: Limit reminder frequency (e.g., once per day)
2. **Dismissal**: Allow users to dismiss reminder temporarily
3. **Scheduled Reminders**: Send periodic reminders via email
4. **Admin Override**: Allow admins to mark phone as verified
5. **Phone Verification**: Add phone verification step

---

*Implementation completed: December 3, 2025*


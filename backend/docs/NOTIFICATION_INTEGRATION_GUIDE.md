# Notification Integration Guide

## Overview

This guide documents how notifications are integrated throughout the system to provide excellent user experience. Notifications keep users informed about important events, actions, and updates.

## Architecture

### Notification System Components

1. **NotificationService** (`notifications_system/services/core.py`)
   - Core service that handles all notification sending
   - Respects user preferences, DND, mute settings
   - Supports multiple channels (email, in-app, SMS, push, etc.)
   - Handles template rendering and delivery

2. **NotificationHelper** (`notifications_system/services/notification_helper.py`)
   - Convenience wrapper around NotificationService
   - Provides easy-to-use methods for common scenarios
   - Handles user/website resolution automatically
   - Includes error handling

3. **Notification Templates** (`notifications_system/templates/`)
   - Class-based templates for different notification types
   - Provides structured title, message, and link generation
   - Supports HTML and plain text rendering

## Notification Templates

### Payment Templates (`payment_templates.py`)
- `payment.completed` - Payment successfully processed
- `payment.failed` - Payment failed
- `payment.refunded` - Refund processed
- `payment.installment_due` - Installment payment due
- `payment.wallet_loaded` - Wallet loaded with funds
- `payment.invoice_generated` - Invoice generated

### Loyalty Templates (`loyalty_templates.py`)
- `loyalty.points_awarded` - Loyalty points awarded
- `loyalty.tier_upgraded` - Tier upgraded
- `loyalty.redemption.approved` - Redemption approved
- `loyalty.redemption.rejected` - Redemption rejected
- `loyalty.milestone_reached` - Milestone reached
- `loyalty.badge_awarded` - Badge awarded

### Class Management Templates (`class_templates.py`)
- `class.bundle.created` - Class bundle created
- `class.bundle.deposit_paid` - Deposit paid
- `class.installment.due` - Installment due
- `class.bundle.completed` - Bundle completed
- `class.message.received` - Message in class thread
- `class.ticket.created` - Ticket created for class

### Ticket Templates (`ticket_templates.py`)
- `ticket.created` - Support ticket created
- `ticket.assigned` - Ticket assigned to support
- `ticket.replied` - Reply added to ticket
- `ticket.resolved` - Ticket resolved
- `ticket.reopened` - Ticket reopened
- `ticket.escalated` - Ticket escalated

### Order Templates (`order_templates.py`)
- `order.created` - New order created
- `order.assigned` - Order assigned to writer
- `order.completed` - Order completed
- `order.paid` - Order payment received

## Integration Points

### 1. Payment Workflows

#### Payment Completed
**Location**: `order_payments_management/services/payment_service.py`
```python
from notifications_system.services.notification_helper import NotificationHelper

# In confirm_external_payment or after payment success
NotificationHelper.notify_order_paid(
    order=payment.order,
    payment_amount=payment.amount,
    payment_method=payment.payment_method
)
```

#### Payment Failed
**Location**: `order_payments_management/services/payment_service.py`
```python
NotificationHelper.notify_payment_failed(
    order=payment.order,
    amount=payment.amount,
    reason="Payment declined"
)
```

#### Refund Processed
**Location**: Refund processing service
```python
NotificationHelper.notify_refund_processed(
    refund=refund_instance,
    order=order,
    amount=refund.amount,
    reason=refund.reason
)
```

### 2. Order Workflows

#### Order Paid
**Location**: `orders/services/mark_order_as_paid_service.py`
- Integrated in `MarkOrderPaidService.mark_paid()`
- Notifies client and assigned writer

#### Order Completed
**Location**: `orders/services/complete_order_service.py`
- Should notify client when order is completed

### 3. Loyalty & Redemption

#### Points Awarded
**Location**: Loyalty conversion service
```python
NotificationHelper.notify_loyalty_points_awarded(
    client_profile=client_profile,
    points=points_earned,
    reason="Order completed",
    total_points=client_profile.loyalty_points
)
```

#### Tier Upgraded
**Location**: Tier update logic
```python
NotificationHelper.notify_tier_upgraded(
    client_profile=client_profile,
    tier_name="Gold",
    perks="10% discount, priority support"
)
```

#### Redemption Approved/Rejected
**Location**: `loyalty_management/services/redemption_service.py`
- Already integrated in `approve_redemption()` and `reject_redemption()`

### 4. Class Management

#### Class Bundle Created
**Location**: `class_management/services/class_bundle_admin.py`
```python
NotificationHelper.notify_class_bundle_created(
    class_bundle=bundle,
    client_profile=client_profile
)
```

#### Deposit Paid
**Location**: `class_management/services/class_payment_processor.py`
```python
NotificationHelper.notify_class_deposit_paid(
    class_bundle=bundle,
    amount=deposit_amount,
    balance_remaining=balance
)
```

#### Installment Due
**Location**: Installment reminder service (to be created)
```python
NotificationHelper.notify_installment_due(
    installment=installment_instance,
    order_id=order.id  # or special_order_id
)
```

### 5. Support Tickets

#### Ticket Created
**Location**: Ticket creation service
```python
NotificationHelper.notify_ticket_created(
    ticket=ticket_instance,
    creator=request.user
)
```

#### Ticket Reply
**Location**: Ticket message service
```python
NotificationHelper.notify_ticket_reply(
    ticket=ticket_instance,
    message=message_instance,
    replier=request.user
)
```

## Usage Examples

### Basic Notification
```python
from notifications_system.services.notification_helper import NotificationHelper

NotificationHelper.send_notification(
    user=user_instance,
    event="custom.event",
    payload={
        "key": "value",
        "order_id": 123
    },
    website=website_instance
)
```

### Using Helper Methods
```python
# Payment notification
NotificationHelper.notify_order_paid(
    order=order,
    payment_amount=Decimal("100.00"),
    payment_method="Credit Card"
)

# Loyalty notification
NotificationHelper.notify_loyalty_points_awarded(
    client_profile=client_profile,
    points=100,
    reason="Order completed",
    total_points=500
)
```

## Notification Channels

Notifications can be sent via multiple channels:

1. **In-App** - Shows in user's notification center
2. **Email** - Sent via email (respects user preferences)
3. **SMS** - Text message (if enabled)
4. **Push** - Mobile push notification (if enabled)
5. **SSE** - Server-sent events for real-time updates

Channels are determined by:
- User preferences
- Event configuration
- Website settings
- Forced channels (if specified)

## User Preferences

Users can control notification preferences:
- Channel preferences (email, in-app, SMS, etc.)
- Category preferences (orders, payments, loyalty, etc.)
- Quiet hours (DND settings)
- Mute specific events

The notification system respects all user preferences automatically.

## Error Handling

All notification calls are wrapped in try-except blocks to ensure that notification failures don't break core workflows:

```python
try:
    NotificationHelper.notify_order_paid(...)
except Exception as e:
    logger.error(f"Failed to send notification: {e}")
    # Continue with normal flow
```

## Best Practices

1. **Always use NotificationHelper** - Don't call NotificationService directly
2. **Include relevant context** - Provide complete payload with all necessary information
3. **Handle errors gracefully** - Don't let notification failures break workflows
4. **Use appropriate events** - Use existing event keys or register new ones
5. **Test notifications** - Verify notifications work in development
6. **Respect user preferences** - System handles this automatically, but be aware

## Event Registration

New events should be registered in:
- `notifications_system/registry/configs/` - JSON config files
- Django admin - `NotificationEvent` model
- Template registration - Use `@register_template` decorator

## Testing Notifications

1. **Development**: Check notification logs in admin
2. **Email Testing**: Use email backend that prints to console
3. **In-App**: Check notification API endpoints
4. **Preview**: Use template preview endpoint

## Future Enhancements

- [ ] Scheduled notification reminders (installments, deadlines)
- [ ] Notification digests (daily/weekly summaries)
- [ ] Rich notifications (with images, actions)
- [ ] Notification analytics (delivery rates, engagement)
- [ ] A/B testing for notification content


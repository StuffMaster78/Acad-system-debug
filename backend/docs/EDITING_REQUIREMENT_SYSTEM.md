# Order Editing Requirement System

## Overview

This system allows admins to configure when orders should undergo editing, with automatic handling of urgent orders and early submissions.

## Features

### 1. Admin Control
- **Per-Order Override**: Admins can set `requires_editing` on individual orders
  - `true` = Force editing (even if urgent)
  - `false` = Skip editing
  - `null` = Use configuration rules

### 2. Automatic Urgent Order Handling
- Urgent orders (deadline < 24 hours or `is_urgent=True`) **automatically skip editing**
- This cannot be overridden (unless admin explicitly sets `requires_editing=True`)

### 3. Early Submission Support
- Orders submitted before deadline can go to editing if configured
- Configurable threshold (default: 24 hours before deadline)

### 4. Configuration-Based Rules
- Website-level configuration for editing requirements
- Supports special requirements (first orders, high-value orders)

---

## Models

### Order Model Changes

Added fields:
- `requires_editing` (BooleanField, nullable): Admin override flag
- `editing_skip_reason` (CharField): Reason why editing was skipped

### EditingRequirementConfig

Website-level configuration:
- `enable_editing_by_default`: Enable editing by default
- `skip_editing_for_urgent`: Skip editing for urgent orders (default: True)
- `allow_editing_for_early_submissions`: Allow editing for early submissions
- `early_submission_hours_threshold`: Hours before deadline threshold (default: 24)
- `editing_required_for_first_orders`: Require editing for first orders
- `editing_required_for_high_value`: Require editing for high-value orders
- `high_value_threshold`: Order value threshold (default: $300)

---

## Decision Logic

The `EditingDecisionService` determines if an order should undergo editing:

1. **Admin Override** (Highest Priority)
   - If `requires_editing = True` → **Go to editing**
   - If `requires_editing = False` → **Skip editing**

2. **Urgent Order Check**
   - If order is urgent → **Skip editing** (unless admin forced)

3. **Configuration Rules**
   - Check website configuration
   - Early submission eligibility
   - Special requirements (first order, high value)

4. **Default Behavior**
   - Use `enable_editing_by_default` setting

---

## API Endpoints

### Admin Endpoints

#### Set Editing Requirement for Order
**PATCH** `/api/v1/orders/admin/orders/<order_id>/editing/`

**Request Body:**
```json
{
  "requires_editing": true,  // or false, or null to remove override
  "reason": "Optional reason for override"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Editing required for order",
  "order_id": 123,
  "requires_editing": true,
  "editing_skip_reason": null
}
```

#### Configure Editing Requirements (Website-Level)
**GET/POST/PUT** `/api/v1/order-configs/api/editing-requirements/`

**GET** `/api/v1/order-configs/api/editing-requirements/get_config/`

Returns current configuration or defaults.

---

## Workflow

### Order Submission Flow

1. Writer submits order → Status: `SUBMITTED`
2. `MoveOrderToEditingService.execute()` is called
3. `EditingDecisionService.should_undergo_editing()` is checked:
   - **If should edit**: Order → `UNDER_EDITING` status
   - **If skip editing**: Order → `REVIEWED` status (skip editing)

### Admin Actions

#### Force Editing
```python
# Via API
PATCH /api/v1/orders/admin/orders/123/editing/
{
  "requires_editing": true
}

# Via Django Admin
OrderAdmin.force_editing() action
```

#### Skip Editing
```python
# Via API
PATCH /api/v1/orders/admin/orders/123/editing/
{
  "requires_editing": false,
  "reason": "Client requested immediate delivery"
}

# Via Django Admin
OrderAdmin.skip_editing() action
```

#### Remove Override
```python
PATCH /api/v1/orders/admin/orders/123/editing/
{
  "requires_editing": null
}
```

---

## Django Admin

### Order Admin
- Added `requires_editing` and `editing_skip_reason` to list display
- Added filters for `requires_editing` and `is_urgent`
- Added actions: `force_editing`, `skip_editing`
- Added "Editing Settings" fieldset

### EditingRequirementConfig Admin
- Full CRUD interface for editing configurations
- Fieldsets organized by category
- Tracks `created_by` admin user

---

## Urgent Order Detection

An order is considered urgent if:
1. `order.is_urgent = True`
2. `OrderFlags.URGENT_ORDER` flag is set
3. `deadline - now() < 24 hours`

---

## Examples

### Example 1: Urgent Order (Auto-Skip)
```
Order #123:
- deadline: 6 hours from now
- is_urgent: False (but deadline < 24h)
- requires_editing: None

Result: SKIP EDITING
Reason: "Order is urgent - skipping editing"
Status: REVIEWED (skip editing)
```

### Example 2: Admin Forces Editing for Urgent Order
```
Order #124:
- deadline: 3 hours from now
- is_urgent: True
- requires_editing: True (admin override)

Result: GO TO EDITING
Status: UNDER_EDITING
```

### Example 3: Early Submission (Config Allowed)
```
Order #125:
- deadline: 48 hours from now
- submitted: Now (48h early)
- Config: allow_editing_for_early_submissions = True

Result: GO TO EDITING
Reason: "Order submitted early - eligible for editing"
Status: UNDER_EDITING
```

### Example 4: High-Value Order (Special Requirement)
```
Order #126:
- total_price: $500
- Config: editing_required_for_high_value = True
- Config: high_value_threshold = $300

Result: GO TO EDITING
Reason: "Special requirement (first order or high value)"
Status: UNDER_EDITING
```

---

## Configuration Best Practices

1. **Default Behavior**: Set `enable_editing_by_default = True` for quality assurance
2. **Urgent Orders**: Always keep `skip_editing_for_urgent = True` (default)
3. **Early Submissions**: Enable `allow_editing_for_early_submissions` to reward early completion
4. **High-Value Orders**: Require editing for orders above a threshold
5. **First Orders**: Require editing for new clients' first orders

---

## Integration Points

### With Editor Management
- Orders that go to editing are auto-assigned to editors (if possible)
- Editor assignment service is called automatically

### With Audit Logging
- All editing requirement changes are logged
- Includes admin override actions

### With Notification System
- Editors are notified when orders are assigned
- Clients can be notified when editing is complete

---

## Migration Notes

1. Existing orders will have `requires_editing = None` (use config rules)
2. Existing urgent orders will automatically skip editing on next submission
3. Configuration must be created for each website (defaults are used if not configured)

---

## Future Enhancements

1. **Editor Capacity Check**: Don't send to editing if no editors available
2. **Quality-Based Routing**: Route to specific editors based on order type
3. **Client Preferences**: Allow clients to request/decline editing
4. **Editor Availability Hours**: Only send to editing during editor work hours
5. **Priority Queue**: Prioritize high-value or first orders in editor queue


# Order Soft Delete Implementation

## Overview
Implemented comprehensive soft delete functionality for the Order model, allowing orders to be hidden from normal queries while remaining in the database for potential restoration.

## Changes Made

### 1. Order Model (`backend/orders/models.py`)

#### Added Custom Manager
- **`OrderManager`**: Custom manager that automatically filters out soft-deleted orders (`is_deleted=False`)
- **`objects`**: Default manager using `OrderManager` (excludes soft-deleted orders)
- **`all_objects`**: Standard Django manager (includes all orders, including soft-deleted)

#### Added Soft Delete Fields
- `is_deleted` (BooleanField): Flag indicating if order is soft-deleted
- `deleted_at` (DateTimeField): Timestamp when order was soft-deleted
- `deleted_by` (ForeignKey): User who soft-deleted the order
- `delete_reason` (CharField): Reason for soft-deleting (max 255 chars)
- `restored_at` (DateTimeField): Timestamp when order was restored
- `restored_by` (ForeignKey): User who restored the order

#### Added Methods
- `mark_deleted(user, reason="")`: Marks order as soft-deleted with timestamp and user
- `mark_restored(user)`: Restores a soft-deleted order with timestamp and user

#### Added Indexes
- Index on `is_deleted` for efficient filtering
- Composite index on `is_deleted` and `deleted_at` for queries filtering by deletion status and date

### 2. Order Deletion Service (`backend/orders/services/order_deletion_service.py`)

#### Updated Methods
- **`hard_delete_by_id`**: Now uses `Order.all_objects` to access soft-deleted orders for permanent deletion

### 3. Order Views (`backend/orders/views/orders/base.py`)

#### Updated Endpoints
- **`restore`**: Now uses `Order.all_objects` to access soft-deleted orders for restoration

### 4. Order Utils (`backend/orders/utils/order_utils.py`)

#### Updated `get_order_by_id`
- Uses `Order.objects` (excludes soft-deleted) when `check_soft_deleted=True`
- Uses `Order.all_objects` (includes all) when `check_soft_deleted=False`

## Migration

Created migration: `0016_order_delete_reason_order_deleted_at_and_more.py`

This migration adds:
- All soft delete fields to the `Order` model
- Indexes for efficient querying

## Usage

### Soft Delete an Order
```python
from orders.services.order_deletion_service import OrderDeletionService
from websites.models import Website

website = Website.objects.get(id=1)
service = OrderDeletionService(website=website)

result = service.soft_delete(
    user=request.user,
    order=order,
    reason="Order cancelled by client"
)
```

### Restore a Soft-Deleted Order
```python
result = service.restore(
    user=request.user,
    order=order
)
```

### Hard Delete an Order (Permanent)
```python
result = service.hard_delete_by_id(
    user=request.user,
    order_id=order.id
)
```

### Query Orders

#### Default (Excludes Soft-Deleted)
```python
# Automatically excludes soft-deleted orders
active_orders = Order.objects.all()
```

#### Include Soft-Deleted
```python
# Access all orders including soft-deleted
all_orders = Order.all_objects.all()
```

#### Only Soft-Deleted
```python
# Get only soft-deleted orders
deleted_orders = Order.all_objects.filter(is_deleted=True)
```

## Permissions

### Soft Delete
- **Staff** (admin/support/superadmin): Can soft-delete any order
- **Clients**: Can only soft-delete their own unpaid orders

### Restore
- **Staff**: Can restore any soft-deleted order
- **Clients**: Can restore only their own soft-deleted orders

### Hard Delete
- **Staff Only**: Only staff members can permanently delete orders

## API Endpoints

### Soft Delete
```
DELETE /api/v1/orders/{id}/
```
- Soft deletes the order
- Returns 204 if deleted, 200 if already deleted

### Restore
```
POST /api/v1/orders/{id}/restore/
```
- Restores a soft-deleted order
- Returns 200 on success

### Hard Delete
```
DELETE /api/v1/orders/{id}/hard/
```
- Permanently deletes the order (irreversible)
- Staff only
- Returns 204 if deleted, 200 if already gone

## Difference: Cancel vs Soft Delete

### Cancel
- Changes order `status` to `"cancelled"`
- Order remains visible in queries
- Used for business logic (order was cancelled but record kept)

### Soft Delete
- Sets `is_deleted=True`
- Order is hidden from normal queries (`Order.objects`)
- Can be restored later
- Used for data management (order should be hidden but not permanently removed)

## Benefits

1. **Data Recovery**: Soft-deleted orders can be restored if needed
2. **Audit Trail**: Tracks who deleted/restored orders and when
3. **Data Integrity**: Maintains referential integrity (related records remain intact)
4. **Performance**: Indexed fields for efficient querying
5. **Flexibility**: Easy to filter active vs deleted orders

## Next Steps

1. Apply the migration: `make migrate`
2. Update frontend to use soft delete endpoints
3. Add UI for viewing/restoring soft-deleted orders (admin only)
4. Consider adding automatic hard delete after retention period (optional)


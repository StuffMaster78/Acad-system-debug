# Frontend Soft Delete Implementation

## Overview
Added comprehensive frontend components for managing order soft delete functionality, including UI for soft deleting, restoring, and permanently deleting orders.

## Changes Made

### 1. API Client (`frontend/src/api/orders.js`)

Added three new API methods:
- `softDelete(id, reason)`: Soft delete an order with optional reason
- `restore(id)`: Restore a soft-deleted order
- `hardDelete(id)`: Permanently delete an order (staff only)

### 2. Order Detail Component (`frontend/src/views/orders/OrderDetail.vue`)

#### Added UI Elements:
- **Soft Deleted Banner**: Displays at the top when an order is soft-deleted, showing:
  - Deletion timestamp and user
  - Delete reason (if provided)
  - Restore timestamp and user (if restored)
  - Quick restore button for admin/support

- **Action Buttons** (Admin/Support only):
  - **Soft Delete**: Orange button to soft delete an order
  - **Restore**: Green button to restore a soft-deleted order
  - **Permanently Delete**: Red button to hard delete (Admin/Superadmin only)

#### Added Functions:
- `softDeleteOrder()`: Prompts for reason, confirms, then soft deletes the order
- `restoreOrder()`: Confirms and restores a soft-deleted order
- `hardDeleteOrder()`: Shows strong warning, then permanently deletes (redirects to orders list)

#### Features:
- Uses `useInputModal` for entering delete reason
- Uses `useConfirmDialog` for all confirmations
- Shows appropriate success/error toasts
- Automatically reloads order after actions
- Redirects to orders list after hard delete

### 3. Order Management Component (`frontend/src/views/admin/OrderManagement.vue`)

#### Added Filters:
- **Include Deleted**: Checkbox to include soft-deleted orders in results
- **Only Deleted**: Checkbox to show only soft-deleted orders

#### Updated `loadOrders()`:
- Adds `include_deleted` and `only_deleted` params to API call
- Performs frontend filtering as fallback (until backend supports these params)
- Filters out soft-deleted orders by default

#### Visual Indicators:
- Soft-deleted orders have red background tint (`bg-red-50`)
- "🗑️ Deleted" badge next to order ID
- Reduced opacity for deleted orders

## Usage

### Soft Delete an Order
1. Navigate to order detail page
2. Click "Soft Delete" button (admin/support only)
3. Enter optional reason
4. Confirm deletion
5. Order is hidden from normal queries but can be restored

### Restore an Order
1. Navigate to order detail page (or use "Include Deleted" filter in Order Management)
2. Click "Restore Order" button
3. Confirm restoration
4. Order becomes visible again

### Permanently Delete an Order
1. Navigate to soft-deleted order detail page
2. Click "Permanently Delete" button (admin/superadmin only)
3. Read warning and confirm
4. Order is permanently removed (redirects to orders list)

### View Soft-Deleted Orders
1. Go to Order Management page
2. Check "Include Deleted" to see all orders including soft-deleted
3. Check "Only Deleted" to see only soft-deleted orders
4. Soft-deleted orders are highlighted with red background and badge

## Permissions

- **Soft Delete**: Admin, Superadmin, Support (any order); Clients (own unpaid orders only)
- **Restore**: Admin, Superadmin, Support (any order); Clients (own orders only)
- **Hard Delete**: Admin, Superadmin only

## UI/UX Features

1. **Clear Visual Indicators**: 
   - Red banner for soft-deleted orders
   - Badge in order list
   - Background tinting

2. **Confirmation Dialogs**:
   - Input modal for delete reason
   - Destructive confirmation for soft/hard delete
   - Info confirmation for restore

3. **Feedback**:
   - Success toasts after actions
   - Error handling with clear messages
   - Automatic page refresh after restore/soft delete

4. **Safety**:
   - Hard delete requires strong warning
   - Redirects away after permanent deletion
   - Cannot accidentally delete active orders

## Backend Integration Notes

The frontend currently performs client-side filtering for soft-deleted orders. For optimal performance, the backend should be updated to:

1. Support `include_deleted` query parameter in OrderViewSet
2. Support `only_deleted` query parameter
3. Use `Order.all_objects` when these params are set

Example backend update:
```python
def get_queryset(self):
    queryset = Order.objects.all()  # Default excludes deleted
    
    if self.request.query_params.get('include_deleted') == 'true':
        queryset = Order.all_objects.all()
    
    if self.request.query_params.get('only_deleted') == 'true':
        queryset = Order.all_objects.filter(is_deleted=True)
    
    return queryset
```

## Next Steps

1. Update backend OrderViewSet to support `include_deleted` and `only_deleted` query params
2. Add bulk restore/delete actions in Order Management
3. Add soft delete statistics to dashboard
4. Consider adding automatic hard delete after retention period (optional)


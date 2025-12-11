# Pattern for Replacing confirm() with Modals

This document shows the pattern for replacing all `confirm()` calls with proper modals throughout the system.

## Pattern

### 1. Add Imports
```javascript
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
```

### 2. Initialize Composable
```javascript
const confirm = useConfirmDialog()
```

### 3. Add Component to Template
```vue
<ConfirmationDialog
  v-model:show="confirm.show.value"
  :title="confirm.title.value"
  :message="confirm.message.value"
  :details="confirm.details.value"
  :variant="confirm.variant.value"
  :icon="confirm.icon.value"
  :confirm-text="confirm.confirmText.value"
  :cancel-text="confirm.cancelText.value"
  @confirm="confirm.onConfirm"
  @cancel="confirm.onCancel"
/>
```

### 4. Replace confirm() Calls

#### For Simple Confirmations:
```javascript
// OLD:
if (!confirm('Are you sure?')) return

// NEW:
const confirmed = await confirm.showDialog(
  'Are you sure?',
  'Confirm Action',
  {
    variant: 'default',
    icon: '❓',
    confirmText: 'Confirm',
    cancelText: 'Cancel'
  }
)
if (!confirmed) return
```

#### For Destructive Actions:
```javascript
// OLD:
if (!confirm('Delete this item? This cannot be undone.')) return

// NEW:
const confirmed = await confirm.showDestructive(
  'Delete this item? This cannot be undone.',
  'Delete Item',
  {
    confirmText: 'Delete',
    cancelText: 'Cancel'
  }
)
if (!confirmed) return
```

#### For Warnings:
```javascript
// OLD:
if (!confirm('Warning: This action may have consequences.')) return

// NEW:
const confirmed = await confirm.showWarning(
  'Warning: This action may have consequences.',
  'Warning',
  {
    confirmText: 'Proceed',
    cancelText: 'Cancel'
  }
)
if (!confirmed) return
```

## Files Completed

✅ `frontend/src/views/admin/SpecialOrderManagement.vue`
- Override Payment (custom modal with enhanced UI)
- Mark Complete (custom modal with enhanced UI)
- Unlock Files (custom modal with enhanced UI)
- View All Installments (enhanced modal with summary cards)
- Approve Order
- Mark Installment Paid (2 instances)
- Delete Config

✅ `frontend/src/views/orders/OrderDetail.vue`
- Reopen Order
- Request File Deletion (with input modal for reason)
- Reject Link
- Delete Message
- Delete Thread
- Cancel Draft Request
- Take Order

✅ `frontend/src/views/admin/ClassManagement.vue`
- Delete Config

✅ `frontend/src/views/admin/ExpressClassesManagement.vue`
- Mark Express Class as Complete

✅ `frontend/src/views/writers/MyOrders.vue`
- Submit Order

## Files Remaining (43 files)

### High Priority Admin Views:
- `frontend/src/views/admin/ExpressClassesManagement.vue`
- `frontend/src/views/admin/OrderManagement.vue`
- `frontend/src/views/admin/RefundManagement.vue`
- `frontend/src/views/admin/FileManagement.vue`
- `frontend/src/views/admin/ConfigManagement.vue`
- `frontend/src/views/admin/SEOPagesManagement.vue`
- `frontend/src/views/admin/BlogManagement.vue`
- `frontend/src/views/admin/AllWriterPayments.vue`
- `frontend/src/views/admin/CategoryPublishingTargets.vue`
- `frontend/src/views/admin/SeoPagesBlockEditor.vue`
- `frontend/src/views/admin/WriterDisciplineManagement.vue`
- `frontend/src/views/admin/ClientEmailBlacklist.vue`
- `frontend/src/views/admin/TemplateSnippetManager.vue`
- `frontend/src/views/admin/EmailManagement.vue`
- `frontend/src/views/admin/HolidayManagement.vue`
- `frontend/src/views/admin/WebsiteManagement.vue`
- `frontend/src/views/admin/NotificationProfiles.vue`
- `frontend/src/views/admin/InvoiceManagement.vue`
- `frontend/src/views/admin/AdvancePaymentsManagement.vue`
- `frontend/src/views/admin/NotificationGroups.vue`
- `frontend/src/views/admin/ReferralTracking.vue`
- `frontend/src/views/admin/AppealsManagement.vue`
- `frontend/src/views/admin/LoyaltyManagement.vue`
- `frontend/src/views/admin/WriterHierarchy.vue`
- `frontend/src/views/admin/ReviewAggregation.vue`
- `frontend/src/views/admin/SuperadminDashboard.vue`
- `frontend/src/views/admin/DeletionRequests.vue`
- `frontend/src/views/admin/ReviewsManagement.vue`
- `frontend/src/views/admin/SupportTicketsManagement.vue`

### Writer Views:
- `frontend/src/views/writers/OrderQueue.vue`
- `frontend/src/views/writers/MyOrders.vue`
- `frontend/src/views/writers/PaymentRequest.vue`

### Support Views:
- `frontend/src/views/support/Tickets.vue`
- `frontend/src/views/support/TicketQueue.vue`

### Other Views:
- `frontend/src/views/orders/OrderDrafts.vue`
- `frontend/src/views/account/Settings.vue`
- `frontend/src/views/account/SecurityActivity.vue`
- `frontend/src/views/superadmin/TenantManagement.vue`

### Components:
- `frontend/src/components/settings/SessionManagement.vue`
- `frontend/src/components/payments/PaymentCheckout.vue`
- `frontend/src/components/orders/ProgressHistory.vue`
- `frontend/src/components/notifications/NotificationSettings.vue`

## Quick Reference: Variant Types

- `'default'` - Standard confirmation (blue/primary)
- `'danger'` - Destructive actions (red)
- `'warning'` - Warning actions (yellow)

## Quick Reference: Common Icons

- `'✅'` - Success/Approve
- `'❌'` - Reject/Cancel
- `'🗑️'` - Delete
- `'⚠️'` - Warning
- `'💰'` - Payment
- `'🔒'` - Lock/Security
- `'🔓'` - Unlock
- `'🔄'` - Refresh/Reopen
- `'✋'` - Take/Assign
- `'📝'` - Edit/Update


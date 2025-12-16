# Confirmation Dialog Update Guide

This document tracks the systematic replacement of `confirm()` calls with the proper `ConfirmationDialog` component for better UX.

## Pattern to Follow

### 1. Import Required Components
```javascript
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
```

### 2. Initialize in Setup
```javascript
const confirm = useConfirmDialog()
```

### 3. Replace confirm() Calls

**Before:**
```javascript
if (!confirm(`Are you sure you want to delete "${item.name}"?`)) return
```

**After:**
```javascript
const confirmed = await confirm.showDestructive(
  `Are you sure you want to delete "${item.name}"?`,
  'Delete Item',
  {
    details: 'This action cannot be undone.',
    confirmText: 'Delete',
    cancelText: 'Cancel'
  }
)

if (!confirmed) return
```

### 4. Add Component to Template
```vue
<!-- Confirmation Dialog -->
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

## Variants

- `confirm.showDialog()` - Default confirmation
- `confirm.showDestructive()` - For destructive actions (delete, remove, etc.)
- `confirm.showWarning()` - For warning actions

## Status

### ✅ Completed
- ContentTemplatesManagement.vue
- BlogCategoriesManagement.vue

### 🔄 In Progress
- BlogTagsManagement.vue
- AuthorProfilesManagement.vue
- BlogPreviewsManagement.vue
- CategoryPublishingTargetsManagement.vue
- PublishingTargetsManagement.vue
- BlogAutosavesManagement.vue
- BlogRevisionsManagement.vue
- PDFSamplesManagement.vue
- ABTestingManagement.vue
- BlogMediaLibrary.vue
- OrderDraftsManagement.vue
- And 30+ more components...

### 📋 Remaining Files with confirm()
See the grep output for the complete list of files that need updating.


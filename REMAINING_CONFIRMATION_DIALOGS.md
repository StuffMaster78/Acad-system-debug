# Remaining Components with confirm() Calls

This document lists all components that still need to be updated to use the proper `ConfirmationDialog` component.

## Summary

- **Total components with confirm()**: ~70+
- **Components updated**: 9
- **Remaining**: ~61+

## Components Needing Updates

### Recently Created Blog Management Components

1. **PDFSamplesManagement.vue** - 2 confirm calls
   - Delete PDF sample
   - Delete PDF sample section

2. **ABTestingManagement.vue** - 1 confirm call
   - Delete A/B test

3. **BlogMediaLibrary.vue** - 1 confirm call
   - Delete media item

4. **OrderDraftsManagement.vue** - 1 confirm call
   - Delete order draft

### Other Blog Management Components

5. **ContentSnippetsManagement.vue**
6. **ContentBlockTemplatesManagement.vue**
7. **EditHistoryManagement.vue**
8. **SEOMetadataManagement.vue**
9. **BlogEditLocksManagement.vue**
10. **BlogClicksConversionsTracking.vue**
11. **ContentAuditManagement.vue**
12. **ContentFreshnessReminders.vue**
13. **FAQSchemaManagement.vue**
14. **AuthorSchemaManagement.vue**
15. **SocialPlatformsManagement.vue**
16. **BlogSharesTracking.vue**
17. **ContentWorkflowsManagement.vue**
18. **EditorAnalyticsDashboard.vue**
19. **BlogAnalyticsDashboard.vue**
20. **MediaBrowser.vue**

### Service & Order Management

21. **ServicePagesManagement.vue**
22. **OrderPresetsManagement.vue**

### Other Admin Components

23. **BlogManagement.vue**
24. **WebsiteManagement.vue**
25. **UserManagement.vue**
26. **WriterDisciplineManagement.vue**
27. **ClientEmailBlacklist.vue**
28. **FileManagement.vue**
29. **SEOPagesManagement.vue**
30. **ConfigManagement.vue**
31. **NotificationGroups.vue**
32. **SuperadminDashboard.vue**
33. **RefundManagement.vue**
34. **AllWriterPayments.vue**
35. **HolidayManagement.vue**
36. **NotificationProfiles.vue**
37. **EmailManagement.vue**
38. **InvoiceManagement.vue**
39. **AdvancePaymentsManagement.vue**
40. **ReferralTracking.vue**
41. **AppealsManagement.vue**
42. **LoyaltyManagement.vue**
43. **WriterHierarchy.vue**
44. **ReviewAggregation.vue**
45. **ReviewsManagement.vue**
46. **SupportTicketsManagement.vue**
47. **CategoryPublishingTargets.vue** (different from CategoryPublishingTargetsManagement)
48. **SeoPagesBlockEditor.vue**
49. **TemplateSnippetManager.vue**

## Priority Order

### High Priority (Recently Created Components)
1. PDFSamplesManagement.vue
2. ABTestingManagement.vue
3. BlogMediaLibrary.vue
4. OrderDraftsManagement.vue
5. ContentSnippetsManagement.vue
6. ContentBlockTemplatesManagement.vue

### Medium Priority (Other Blog Management)
7. EditHistoryManagement.vue
8. SEOMetadataManagement.vue
9. BlogEditLocksManagement.vue
10. ContentWorkflowsManagement.vue
11. And other blog management components

### Lower Priority (Older Components)
- ServicePagesManagement.vue
- OrderPresetsManagement.vue
- And other admin components

## Update Pattern

For each component:

1. **Add imports:**
```javascript
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
```

2. **Initialize:**
```javascript
const confirm = useConfirmDialog()
```

3. **Replace confirm() calls:**
```javascript
// Before:
if (!confirm(`Are you sure?`)) return

// After (for delete):
const confirmed = await confirm.showDestructive(
  'Are you sure?',
  'Delete Item',
  {
    details: 'This action cannot be undone.',
    confirmText: 'Delete',
    cancelText: 'Cancel'
  }
)
if (!confirmed) return

// After (for restore/replace):
const confirmed = await confirm.showWarning(
  'Are you sure?',
  'Restore Item',
  {
    details: 'This will replace the current content.',
    confirmText: 'Restore',
    cancelText: 'Cancel'
  }
)
if (!confirmed) return
```

4. **Add to template:**
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

## Notes

- Use `showDestructive()` for delete/remove actions
- Use `showWarning()` for restore/replace actions
- Use `showDialog()` for general confirmations
- Always provide meaningful `details` text explaining consequences
- Customize `confirmText` and `cancelText` for clarity


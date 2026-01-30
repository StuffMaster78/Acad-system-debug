# Design System Quick Reference 🎨

Quick reference for the new design system utilities and components.

---

## 🎨 Colors

### Primary Colors
```css
bg-primary-500    /* #6366f1 - Main brand color */
bg-primary-600    /* #4f46e5 - Hover state */
text-primary-600  /* Text color */
border-primary-500 /* Border color */
```

### Semantic Colors
```css
/* Success */
bg-success-600    /* #059669 */
text-success-600
border-success-500

/* Warning */
bg-warning-600    /* #d97706 */
text-warning-600
border-warning-500

/* Error */
bg-error-600      /* #e11d48 */
text-error-600
border-error-500

/* Info */
bg-info-600       /* #0891b2 */
text-info-600
border-info-500
```

### Role Colors
```css
bg-admin-600     /* #7c3aed - Purple */
bg-writer-600    /* #0d9488 - Teal */
bg-client-600    /* #2563eb - Blue */
bg-support-600   /* #ea580c - Orange */
bg-editor-600    /* #db2777 - Pink */
```

---

## 🔘 Buttons

### Usage
```vue
<button class="btn btn-primary">Primary</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn btn-outline">Outline</button>
<button class="btn btn-ghost">Ghost</button>
<button class="btn btn-success">Success</button>
<button class="btn btn-warning">Warning</button>
<button class="btn btn-danger">Danger</button>
```

### Sizes
```vue
<button class="btn btn-sm btn-primary">Small</button>
<button class="btn btn-primary">Default</button>
<button class="btn btn-lg btn-primary">Large</button>
```

### With Icons
```vue
<button class="btn btn-primary">
  <svg class="w-4 h-4">...</svg>
  Button Text
</button>
```

---

## 📦 Cards

### Usage
```vue
<div class="card">
  Basic Card
</div>

<div class="card card-hover">
  Hover Card (lifts on hover)
</div>

<div class="card card-elevated">
  Elevated Card (stronger shadow)
</div>
```

---

## 🏷️ Badges

### Usage
```vue
<span class="badge badge-primary">Primary</span>
<span class="badge badge-success">Success</span>
<span class="badge badge-warning">Warning</span>
<span class="badge badge-error">Error</span>
<span class="badge badge-info">Info</span>
```

---

## 📝 Inputs

### Usage
```vue
<input type="text" class="input" placeholder="Enter text...">
<input type="text" class="input input-error" placeholder="Error state">
<input type="text" class="input input-success" placeholder="Success state">
```

---

## 🔔 Alerts

### Usage
```vue
<div class="alert alert-success">Success message</div>
<div class="alert alert-warning">Warning message</div>
<div class="alert alert-error">Error message</div>
<div class="alert alert-info">Info message</div>
```

---

## 📊 Tables

### Usage
```vue
<div class="table-container">
  <table class="table">
    <thead class="table-header">
      <tr>
        <th class="table-header-cell">Header</th>
      </tr>
    </thead>
    <tbody class="table-body">
      <tr class="table-row">
        <td class="table-cell">Data</td>
      </tr>
    </tbody>
  </table>
</div>
```

---

## ✨ Glassmorphism

### Usage
```vue
<div class="glass">
  Semi-transparent with blur
</div>

<div class="glass-strong">
  More opaque with stronger blur
</div>
```

---

## 🎭 Animations

### Usage
```vue
<div class="animate-fade-in">Fades in</div>
<div class="animate-slide-up">Slides up</div>
<div class="animate-slide-down">Slides down</div>
<div class="animate-scale-in">Scales in</div>
<div class="animate-pulse-slow">Pulses slowly</div>
```

---

## 🪟 Modal Component

### Basic Usage
```vue
<template>
  <Modal
    :visible="showModal"
    @update:visible="showModal = $event"
    title="Modal Title"
    subtitle="Optional subtitle"
    icon="🎉"
    size="md"
  >
    <p>Modal content goes here</p>
    
    <template #footer>
      <div class="flex justify-end gap-3">
        <button class="btn btn-secondary" @click="showModal = false">
          Cancel
        </button>
        <button class="btn btn-primary" @click="handleConfirm">
          Confirm
        </button>
      </div>
    </template>
  </Modal>
</template>

<script setup>
import { ref } from 'vue'
import Modal from '@/components/common/Modal.vue'

const showModal = ref(false)

const handleConfirm = () => {
  // Do something
  showModal.value = false
}
</script>
```

### Sizes
```
xs, sm, md (default), lg, xl, 2xl, 3xl, 4xl, 5xl, full
```

### Props
```typescript
visible: boolean         // Show/hide modal
title: string           // Modal title
subtitle: string        // Optional subtitle
icon: string            // Optional emoji/icon
size: string            // Size variant
showClose: boolean      // Show close button (default: true)
closeOnBackdrop: boolean // Close on backdrop click (default: true)
closeOnEscape: boolean  // Close on Escape key (default: true)
autoFocus: boolean      // Auto-focus first input (default: true)
scrollable: boolean     // Enable body scrolling (default: false)
maxHeight: string       // Max body height (default: '60vh')
```

---

## ❓ ConfirmationDialog Component

### Basic Usage
```vue
<template>
  <ConfirmationDialog
    v-model:show="showDialog"
    title="Delete Item"
    message="Are you sure you want to delete this item?"
    details="This action cannot be undone."
    icon="🗑️"
    variant="danger"
    confirmText="Delete"
    cancelText="Cancel"
    :loading="isDeleting"
    @confirm="handleDelete"
    @cancel="handleCancel"
  />
</template>

<script setup>
import { ref } from 'vue'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const showDialog = ref(false)
const isDeleting = ref(false)

const handleDelete = async () => {
  isDeleting.value = true
  try {
    await deleteItem()
    showDialog.value = false
  } finally {
    isDeleting.value = false
  }
}

const handleCancel = () => {
  showDialog.value = false
}
</script>
```

### Variants
```
default  - Blue/primary colors
danger   - Red colors
warning  - Orange/amber colors
success  - Green/emerald colors
```

### Props
```typescript
show: boolean           // Show/hide dialog (v-model)
title: string          // Dialog title
message: string        // Main message
details: string        // Additional details (optional)
icon: string           // Emoji/icon (auto-default based on variant)
variant: string        // Color variant
confirmText: string    // Confirm button text (default: 'Confirm')
cancelText: string     // Cancel button text (default: 'Cancel')
loading: boolean       // Show loading state (default: false)
```

---

## 🎨 Dark Mode

### Toggle Dark Mode
```javascript
// Add 'dark' class to html element
document.documentElement.classList.add('dark')

// Remove 'dark' class
document.documentElement.classList.remove('dark')

// Toggle
document.documentElement.classList.toggle('dark')
```

### Dark Mode Variants
```vue
<!-- Automatic dark mode variants -->
<div class="bg-white dark:bg-slate-900">
  Content
</div>

<p class="text-gray-900 dark:text-slate-100">
  Text
</p>
```

---

## 📱 Responsive

### Breakpoints
```css
sm:  640px   /* Tablet portrait */
md:  768px   /* Tablet landscape */
lg:  1024px  /* Laptop */
xl:  1280px  /* Desktop */
2xl: 1536px  /* Large desktop */
```

### Usage
```vue
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  <!-- Responsive columns -->
</div>
```

---

## 🎯 Focus States

All interactive elements have automatic focus states:
```css
focus-visible:ring-2 focus-visible:ring-primary-500
```

To customize:
```vue
<button class="focus-visible:ring-2 focus-visible:ring-success-500">
  Button
</button>
```

---

## 🚀 Examples

### Complete Form
```vue
<form @submit.prevent="handleSubmit">
  <div class="space-y-4">
    <div>
      <label class="block text-sm font-medium mb-2">Name</label>
      <input type="text" class="input" v-model="form.name">
    </div>
    
    <div>
      <label class="block text-sm font-medium mb-2">Email</label>
      <input 
        type="email" 
        class="input"
        :class="{ 'input-error': errors.email }"
        v-model="form.email"
      >
      <p v-if="errors.email" class="text-sm text-error-600 mt-1">
        {{ errors.email }}
      </p>
    </div>
    
    <div class="flex justify-end gap-3">
      <button type="button" class="btn btn-secondary">
        Cancel
      </button>
      <button type="submit" class="btn btn-primary">
        Submit
      </button>
    </div>
  </div>
</form>
```

### Stat Card
```vue
<div class="card card-hover">
  <div class="flex items-center justify-between">
    <div>
      <p class="text-sm text-gray-600 dark:text-slate-400">Total Orders</p>
      <p class="text-3xl font-bold text-gray-900 dark:text-slate-100 mt-1">
        1,234
      </p>
    </div>
    <div class="w-12 h-12 rounded-xl bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-2xl">
      📦
    </div>
  </div>
  <div class="mt-4 flex items-center gap-2">
    <span class="badge badge-success">+12%</span>
    <span class="text-sm text-gray-600 dark:text-slate-400">vs last month</span>
  </div>
</div>
```

---

## 💡 Tips

1. **Always use utility classes** from the design system
2. **Avoid inline styles** unless absolutely necessary
3. **Use semantic color names** (success, warning, error) instead of specific colors
4. **Test in both light and dark mode**
5. **Check focus states** for accessibility
6. **Use role-specific colors** for user-related features
7. **Prefer glassmorphism** for overlays and modals
8. **Add loading states** to all async actions

---

## 📚 Resources

- **Full Styles**: `/frontend/src/style.css`
- **Modal Component**: `/frontend/src/components/common/Modal.vue`
- **Dialog Component**: `/frontend/src/components/common/ConfirmationDialog.vue`
- **Plan**: `/frontend/UI_UX_MODERNIZATION_PLAN.md`
- **Progress**: `/frontend/UI_UX_PROGRESS.md`

---

**Last Updated**: January 30, 2026  
**Version**: 1.0.0

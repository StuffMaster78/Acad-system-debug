# Naive UI Integration Guide

Naive UI has been successfully integrated into the project. This guide explains how to use it alongside your existing components.

## 🎯 Integration Strategy

We're using a **gradual migration** approach:
- **New components**: Use Naive UI directly
- **Existing components**: Can be gradually migrated
- **Wrapper components**: Created to match existing APIs for easy migration

## 📦 Available Components

### Direct Naive UI Components
Import directly from `naive-ui`:
```vue
<script setup>
import { NButton, NInput, NModal, NDataTable } from 'naive-ui'
</script>
```

### Wrapper Components (Recommended for Migration)
Located in `src/components/naive/`:
- `NaiveModal.vue` - Drop-in replacement for existing Modal
- `NaiveDataTable.vue` - Enhanced data table
- `NaiveButton.vue` - Button component
- `NaiveInput.vue` - Input with label and error handling

## 🚀 Quick Start Examples

### 1. Using Naive Modal (Drop-in Replacement)

**Before:**
```vue
<Modal
  v-model:visible="showModal"
  title="My Modal"
  size="md"
>
  <p>Content</p>
  <template #footer>
    <button @click="showModal = false">Close</button>
  </template>
</Modal>
```

**After (using wrapper):**
```vue
<NaiveModal
  v-model:visible="showModal"
  title="My Modal"
  size="md"
>
  <p>Content</p>
  <template #footer>
    <NButton @click="showModal = false">Close</NButton>
  </template>
</NaiveModal>

<script setup>
import NaiveModal from '@/components/naive/NaiveModal.vue'
import { NButton } from 'naive-ui'
</script>
```

### 2. Using Naive Input

**Before:**
```vue
<div>
  <label class="block text-sm font-medium mb-2">Name</label>
  <input
    v-model="name"
    class="w-full border rounded-lg px-3 py-2"
    placeholder="Enter name"
  />
</div>
```

**After:**
```vue
<NaiveInput
  v-model="name"
  label="Name"
  placeholder="Enter name"
  clearable
/>

<script setup>
import NaiveInput from '@/components/naive/NaiveInput.vue'
</script>
```

### 3. Using Naive DataTable

**Before:**
```vue
<EnhancedDataTable
  :items="orders"
  :columns="columns"
  :loading="loading"
/>
```

**After:**
```vue
<NaiveDataTable
  :items="orders"
  :columns="columns"
  :loading="loading"
  striped
  bordered
/>

<script setup>
import NaiveDataTable from '@/components/naive/NaiveDataTable.vue'
</script>
```

### 4. Using Naive Button

**Before:**
```vue
<button class="px-4 py-2 bg-primary-600 text-white rounded-lg">
  Click Me
</button>
```

**After:**
```vue
<NButton type="primary" @click="handleClick">
  Click Me
</NButton>

<script setup>
import { NButton } from 'naive-ui'
</script>
```

## 🎨 Styling with Tailwind

Naive UI components work seamlessly with Tailwind:

```vue
<NButton type="primary" class="mt-4 shadow-lg">
  Button with Tailwind
</NButton>

<NCard class="!bg-blue-50 dark:!bg-blue-900/20">
  Card with custom background
</NCard>
```

## 🌓 Theme Support

All Naive UI components automatically sync with your light/dark theme. The theme is configured in `src/plugins/naive-ui.js` and responds to your existing theme system.

## 📋 Migration Checklist

When migrating existing components:

- [ ] Replace `Modal` with `NaiveModal` or `NModal`
- [ ] Replace custom inputs with `NaiveInput` or `NInput`
- [ ] Replace `EnhancedDataTable` with `NaiveDataTable` or `NDataTable`
- [ ] Replace custom buttons with `NButton`
- [ ] Update form validation to use Naive UI's built-in validation
- [ ] Test theme switching (light/dark mode)
- [ ] Verify responsive behavior

## 🔧 Common Patterns

### Form with Validation

```vue
<template>
  <NForm :model="form" :rules="rules" ref="formRef">
    <NFormItem label="Email" path="email">
      <NInput v-model:value="form.email" placeholder="Enter email" />
    </NFormItem>
    <NFormItem label="Password" path="password">
      <NInput
        v-model:value="form.password"
        type="password"
        placeholder="Enter password"
      />
    </NFormItem>
    <NButton type="primary" @click="handleSubmit">Submit</NButton>
  </NForm>
</template>

<script setup>
import { NForm, NFormItem, NInput, NButton } from 'naive-ui'
import { ref } from 'vue'

const formRef = ref(null)
const form = ref({
  email: '',
  password: '',
})

const rules = {
  email: {
    required: true,
    message: 'Email is required',
    trigger: 'blur',
  },
  password: {
    required: true,
    message: 'Password is required',
    trigger: 'blur',
  },
}

const handleSubmit = () => {
  formRef.value?.validate((errors) => {
    if (!errors) {
      // Submit form
    }
  })
}
</script>
```

### Modal with Form

```vue
<template>
  <NModal v-model:show="showModal" title="Create Order" preset="card" style="width: 600px">
    <NForm :model="form" :rules="rules">
      <NFormItem label="Title" path="title">
        <NInput v-model:value="form.title" />
      </NFormItem>
    </NForm>
    <template #footer>
      <NButton @click="showModal = false">Cancel</NButton>
      <NButton type="primary" @click="handleSubmit">Submit</NButton>
    </template>
  </NModal>
</template>
```

### Data Table with Actions

```vue
<template>
  <NDataTable
    :columns="columns"
    :data="tableData"
    :pagination="pagination"
  />
</template>

<script setup>
import { NDataTable, NButton, NPopconfirm } from 'naive-ui'
import { h } from 'vue'

const columns = [
  { title: 'Name', key: 'name' },
  { title: 'Email', key: 'email' },
  {
    title: 'Actions',
    key: 'actions',
    render(row) {
      return h('div', { class: 'flex gap-2' }, [
        h(NButton, { size: 'small', onClick: () => edit(row) }, 'Edit'),
        h(
          NPopconfirm,
          {
            onPositiveClick: () => deleteRow(row),
          },
          {
            trigger: () => h(NButton, { size: 'small', type: 'error' }, 'Delete'),
            default: () => 'Are you sure?',
          }
        ),
      ])
    },
  },
]
</script>
```

## 📚 Documentation

- [Naive UI Official Docs](https://www.naiveui.com/)
- [Component API Reference](https://www.naiveui.com/en-US/os-theme/components/button)
- [Theme Customization](https://www.naiveui.com/en-US/os-theme/docs/customize-theme)

## 🎯 Next Steps

1. **Start using Naive UI in new features**
2. **Gradually migrate high-maintenance components**
3. **Keep simple Tailwind-only components as-is**
4. **Leverage Naive UI's built-in features** (validation, loading states, etc.)

## 💡 Tips

- Use wrapper components (`NaiveModal`, `NaiveInput`, etc.) for easier migration
- Import components individually for better tree-shaking
- Combine Naive UI with Tailwind for custom styling
- Use Naive UI's built-in validation instead of custom validation
- Leverage theme system for consistent colors


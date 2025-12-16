# Naive UI Integration Guide

Naive UI has been integrated into the project to provide production-ready, accessible components that work seamlessly with Tailwind CSS and the existing theme system.

## 🎯 Benefits

- **Production-Ready Components**: Battle-tested components with excellent accessibility
- **TypeScript Support**: Full TypeScript support for better DX
- **Theme Integration**: Automatically syncs with your light/dark theme
- **Tailwind Compatible**: Works alongside Tailwind CSS without conflicts
- **Comprehensive**: 80+ components covering all common UI patterns

## 📦 Available Components

### Forms
- `NInput` - Text input
- `NInputNumber` - Number input
- `NTextarea` - Textarea
- `NSelect` - Select dropdown
- `NCheckbox` - Checkbox
- `NRadio` - Radio button
- `NSwitch` - Toggle switch
- `NDatePicker` - Date picker
- `NTimePicker` - Time picker
- `NForm` - Form container with validation
- `NFormItem` - Form field wrapper

### Data Display
- `NDataTable` - Advanced data table
- `NTable` - Simple table
- `NCard` - Card container
- `NList` - List component
- `NEmpty` - Empty state
- `NStatistic` - Statistics display
- `NDescriptions` - Description list

### Feedback
- `NModal` - Modal dialog
- `NDrawer` - Drawer/sidebar
- `NMessage` - Message notification
- `NNotification` - Notification toast
- `NAlert` - Alert banner
- `NProgress` - Progress bar
- `NLoadingBar` - Loading bar
- `NSpin` - Loading spinner

### Navigation
- `NMenu` - Menu navigation
- `NBreadcrumb` - Breadcrumb navigation
- `NPagination` - Pagination
- `NTabs` - Tabs component
- `NSteps` - Steps indicator

### Layout
- `NLayout` - Layout container
- `NLayoutHeader` - Header
- `NLayoutSider` - Sidebar
- `NLayoutContent` - Main content
- `NLayoutFooter` - Footer
- `NGrid` - Grid system
- `NSpace` - Spacing component
- `NDivider` - Divider line

### And many more...

## 🚀 Usage Examples

### Basic Usage

```vue
<template>
  <div>
    <!-- Button -->
    <NButton type="primary" @click="handleClick">
      Click Me
    </NButton>

    <!-- Input -->
    <NInput
      v-model:value="inputValue"
      placeholder="Enter text..."
      clearable
    />

    <!-- Modal -->
    <NModal v-model:show="showModal" title="My Modal">
      <p>Modal content here</p>
    </NModal>

    <!-- Data Table -->
    <NDataTable
      :columns="columns"
      :data="tableData"
      :pagination="pagination"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { NButton, NInput, NModal, NDataTable } from 'naive-ui'

const inputValue = ref('')
const showModal = ref(false)

const columns = [
  { title: 'Name', key: 'name' },
  { title: 'Age', key: 'age' },
]
const tableData = ref([
  { name: 'John', age: 30 },
  { name: 'Jane', age: 25 },
])
</script>
```

### Replacing Custom Components

#### Replace Custom Modal

**Before:**
```vue
<Modal :visible="show" @close="show = false">
  <h2>Title</h2>
  <p>Content</p>
</Modal>
```

**After:**
```vue
<NModal v-model:show="show" title="Title">
  <p>Content</p>
</NModal>
```

#### Replace Custom DataTable

**Before:**
```vue
<EnhancedDataTable
  :items="data"
  :columns="columns"
/>
```

**After:**
```vue
<NDataTable
  :columns="columns"
  :data="data"
  :pagination="pagination"
/>
```

## 🎨 Styling with Tailwind

Naive UI components work alongside Tailwind. You can:

1. **Use Tailwind classes on Naive components:**
```vue
<NButton class="mt-4 shadow-lg">
  Button
</NButton>
```

2. **Override Naive styles with Tailwind:**
```vue
<NCard class="!bg-blue-50">
  Card content
</NCard>
```

3. **Use both together:**
```vue
<div class="p-6 bg-white rounded-lg">
  <NButton type="primary">Click</NButton>
</div>
```

## 🌓 Theme Support

Naive UI automatically syncs with your theme system. The theme is configured in `src/plugins/naive-ui.js` and responds to light/dark mode changes.

## 📚 Documentation

- [Naive UI Official Docs](https://www.naiveui.com/)
- [Component API Reference](https://www.naiveui.com/en-US/os-theme/components/button)
- [Theme Customization](https://www.naiveui.com/en-US/os-theme/docs/customize-theme)

## 🔄 Migration Strategy

You can gradually migrate to Naive UI:

1. **Start with new components** - Use Naive UI for new features
2. **Replace high-maintenance components** - Migrate complex custom components
3. **Keep simple components** - Simple Tailwind-only components can stay

## 💡 Best Practices

1. **Import only what you need** for better tree-shaking
2. **Use TypeScript** for better type safety
3. **Leverage Naive's built-in features** (validation, loading states, etc.)
4. **Customize theme** in `naive-ui.js` for brand consistency
5. **Combine with Tailwind** for custom styling needs


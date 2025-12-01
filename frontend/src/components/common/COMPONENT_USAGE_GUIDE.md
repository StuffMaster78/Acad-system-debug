# Enhanced Components Usage Guide

This guide explains how to use the enhanced, user-friendly components that fetch data from the database.

---

## 📊 Enhanced DataTable Component

### Location
`components/common/EnhancedDataTable.vue`

### Features
- ✅ Built-in search functionality
- ✅ Column sorting (ascending/descending)
- ✅ Client-side pagination
- ✅ Row actions (view, edit, delete)
- ✅ Filter management
- ✅ Responsive design
- ✅ Loading and empty states
- ✅ Customizable styling

### Basic Usage

```vue
<template>
  <EnhancedDataTable
    :items="orders"
    :columns="columns"
    :loading="loading"
    :searchable="true"
    :search-fields="['topic', 'client.username', 'status']"
    @row-click="handleRowClick"
    @view="handleView"
    @edit="handleEdit"
    @delete="handleDelete"
  />
</template>

<script setup>
import EnhancedDataTable from '@/components/common/EnhancedDataTable.vue'

const columns = [
  {
    key: 'id',
    label: 'Order ID',
    sortable: true,
  },
  {
    key: 'topic',
    label: 'Topic',
    sortable: true,
  },
  {
    key: 'client.username',
    label: 'Client',
    sortable: true,
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    format: (value) => value.replace('_', ' ').toUpperCase(),
  },
  {
    key: 'total_price',
    label: 'Price',
    align: 'right',
    sortable: true,
    format: (value) => `$${parseFloat(value).toFixed(2)}`,
  },
]

const orders = ref([])
const loading = ref(false)
</script>
```

### Advanced Usage with Custom Cells

```vue
<template>
  <EnhancedDataTable
    :items="orders"
    :columns="columns"
    :searchable="true"
    :clickable="true"
  >
    <!-- Custom cell for status -->
    <template #cell-status="{ value, item }">
      <span
        :class="[
          'px-2 py-1 rounded-full text-xs font-medium',
          value === 'completed' ? 'bg-green-100 text-green-800' :
          value === 'in_progress' ? 'bg-blue-100 text-blue-800' :
          'bg-gray-100 text-gray-800'
        ]"
      >
        {{ value }}
      </span>
    </template>

    <!-- Custom row actions -->
    <template #row-actions="{ item }">
      <button @click="viewOrder(item)" class="text-blue-600">View</button>
      <button @click="editOrder(item)" class="text-green-600">Edit</button>
    </template>

    <!-- Header actions -->
    <template #headerActions>
      <button @click="exportData" class="btn btn-primary">Export</button>
      <button @click="refreshData" class="btn btn-secondary">Refresh</button>
    </template>
  </EnhancedDataTable>
</template>
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `items` | Array | `[]` | Data items to display |
| `columns` | Array | `[]` | Column definitions |
| `loading` | Boolean | `false` | Show loading state |
| `searchable` | Boolean | `true` | Enable search |
| `searchFields` | Array | `[]` | Fields to search in |
| `sortable` | Boolean | `true` | Enable column sorting |
| `striped` | Boolean | `true` | Alternate row colors |
| `clickable` | Boolean | `false` | Make rows clickable |
| `pageSize` | Number | `10` | Items per page |
| `pageSizeOptions` | Array | `[10, 25, 50, 100]` | Page size options |
| `showViewAction` | Boolean | `false` | Show view button |
| `showEditAction` | Boolean | `false` | Show edit button |
| `showDeleteAction` | Boolean | `false` | Show delete button |

### Events

- `@row-click` - Emitted when a row is clicked
- `@view` - Emitted when view action is clicked
- `@edit` - Emitted when edit action is clicked
- `@delete` - Emitted when delete action is clicked
- `@sort` - Emitted when column is sorted
- `@search` - Emitted when search query changes
- `@page-change` - Emitted when page changes

---

## 🔽 DatabaseSelect Component

### Location
`components/common/DatabaseSelect.vue`

### Features
- ✅ Automatically fetches options from database
- ✅ Supports multiple data sources
- ✅ Loading states
- ✅ Error handling
- ✅ Custom filtering and sorting
- ✅ Accessible and user-friendly

### Basic Usage

```vue
<template>
  <DatabaseSelect
    v-model="form.paper_type_id"
    source="paper-types"
    label="Paper Type"
    placeholder="Select a paper type..."
    required
  />
</template>

<script setup>
import DatabaseSelect from '@/components/common/DatabaseSelect.vue'

const form = ref({
  paper_type_id: null,
})
</script>
```

### Available Sources

1. **Order Configs** (from database):
   - `paper-types`
   - `academic-levels`
   - `formatting-styles`
   - `subjects`
   - `types-of-work`
   - `english-types`

2. **Users** (from database):
   - `clients`
   - `writers`
   - `editors`
   - `support`
   - `admins`

3. **Custom**:
   - `custom` - Provide options via `customOptions` prop

### Advanced Usage

```vue
<template>
  <!-- With filtering -->
  <DatabaseSelect
    v-model="form.subject_id"
    source="subjects"
    label="Subject"
    :filter-fn="(subject) => subject.is_technical"
    placeholder="Select a technical subject..."
  />

  <!-- With API parameters -->
  <DatabaseSelect
    v-model="form.client_id"
    source="clients"
    label="Client"
    :api-params="{ website_id: currentWebsiteId }"
    placeholder="Select a client..."
  />

  <!-- Custom options -->
  <DatabaseSelect
    v-model="form.status"
    source="custom"
    label="Status"
    :custom-options="statusOptions"
    value-key="value"
    label-key="label"
  />

  <!-- With custom value/label keys -->
  <DatabaseSelect
    v-model="form.writer_id"
    source="writers"
    label="Writer"
    value-key="id"
    label-key="username"
    placeholder="Select a writer..."
  />
</template>

<script setup>
const statusOptions = [
  { value: 'active', label: 'Active' },
  { value: 'inactive', label: 'Inactive' },
  { value: 'pending', label: 'Pending' },
]
</script>
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `modelValue` | String/Number | `null` | Selected value |
| `source` | String | **required** | Data source type |
| `label` | String | `''` | Field label |
| `placeholder` | String | `'Select an option...'` | Placeholder text |
| `required` | Boolean | `false` | Required field |
| `disabled` | Boolean | `false` | Disable select |
| `error` | String | `''` | Error message |
| `helperText` | String | `''` | Helper text |
| `tooltip` | String | `''` | Tooltip text |
| `size` | String | `'md'` | Size: `sm`, `md`, `lg` |
| `customOptions` | Array | `[]` | Custom options (for `custom` source) |
| `apiParams` | Object | `{}` | Additional API parameters |
| `valueKey` | String | `'id'` | Key for option value |
| `labelKey` | String | `'name'` | Key for option label |
| `filterFn` | Function | `null` | Filter function |
| `sortFn` | Function | `null` | Sort function |
| `autoLoad` | Boolean | `true` | Auto-load on mount |

### Events

- `@update:modelValue` - Emitted when value changes
- `@change` - Emitted when selection changes
- `@load` - Emitted when options are loaded
- `@focus` - Emitted when focused
- `@blur` - Emitted when blurred

### Methods (via ref)

```vue
<template>
  <DatabaseSelect
    ref="selectRef"
    source="paper-types"
  />
  <button @click="refreshOptions">Refresh</button>
</template>

<script setup>
const selectRef = ref(null)

const refreshOptions = () => {
  selectRef.value?.refresh()
}
</script>
```

---

## 🪟 Enhanced Modal Component

### Location
`components/common/Modal.vue`

### Features
- ✅ Improved styling and animations
- ✅ Icon support
- ✅ Subtitle support
- ✅ Better footer layout
- ✅ Focus management
- ✅ Keyboard navigation
- ✅ Scrollable content

### Basic Usage

```vue
<template>
  <Modal
    v-model:visible="showModal"
    title="Create Order"
    subtitle="Fill in the details below"
    icon="📝"
    size="lg"
  >
    <form>
      <!-- Form content -->
    </form>

    <template #footer>
      <button @click="showModal = false" class="btn btn-secondary">Cancel</button>
      <button @click="submitForm" class="btn btn-primary">Create</button>
    </template>
  </Modal>
</template>

<script setup>
import Modal from '@/components/common/Modal.vue'

const showModal = ref(false)
</script>
```

### Advanced Usage

```vue
<template>
  <Modal
    v-model:visible="showModal"
    title="Order Details"
    subtitle="View and manage order information"
    icon="📦"
    size="xl"
    :scrollable="true"
    :max-height="'80vh'"
  >
    <!-- Scrollable content -->
    <div class="space-y-4">
      <!-- Long content here -->
    </div>

    <template #header>
      <div class="flex items-center gap-2">
        <span class="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">Active</span>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-between w-full">
        <button @click="deleteOrder" class="btn btn-danger">Delete</button>
        <div class="flex gap-2">
          <button @click="showModal = false" class="btn btn-secondary">Close</button>
          <button @click="saveOrder" class="btn btn-primary">Save</button>
        </div>
      </div>
    </template>
  </Modal>
</template>
```

### Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `visible` | Boolean | `false` | Show/hide modal |
| `title` | String | `''` | Modal title |
| `subtitle` | String | `''` | Modal subtitle |
| `icon` | String | `''` | Icon emoji/text |
| `size` | String | `'md'` | Size: `sm`, `md`, `lg`, `xl`, `2xl`, `full` |
| `showClose` | Boolean | `true` | Show close button |
| `closeOnBackdrop` | Boolean | `true` | Close on backdrop click |
| `closeOnEscape` | Boolean | `true` | Close on Escape key |
| `scrollable` | Boolean | `false` | Make body scrollable |
| `maxHeight` | String | `'60vh'` | Max height for scrollable content |

---

## 🔄 Migration Guide

### Replacing Hardcoded Selects

**Before:**
```vue
<select v-model="form.paper_type_id">
  <option value="">Select paper type</option>
  <option value="1">Essay</option>
  <option value="2">Research Paper</option>
  <option value="3">Dissertation</option>
</select>
```

**After:**
```vue
<DatabaseSelect
  v-model="form.paper_type_id"
  source="paper-types"
  label="Paper Type"
  placeholder="Select a paper type..."
/>
```

### Replacing Basic Tables

**Before:**
```vue
<table>
  <thead>
    <tr>
      <th>ID</th>
      <th>Name</th>
    </tr>
  </thead>
  <tbody>
    <tr v-for="item in items" :key="item.id">
      <td>{{ item.id }}</td>
      <td>{{ item.name }}</td>
    </tr>
  </tbody>
</table>
```

**After:**
```vue
<EnhancedDataTable
  :items="items"
  :columns="[
    { key: 'id', label: 'ID', sortable: true },
    { key: 'name', label: 'Name', sortable: true },
  ]"
  :searchable="true"
  :search-fields="['name']"
/>
```

---

## 📝 Best Practices

1. **Always use DatabaseSelect** for dropdowns that should come from the database
2. **Use EnhancedDataTable** for all data tables
3. **Provide meaningful labels** and placeholders
4. **Handle loading states** properly
5. **Show error messages** when data fails to load
6. **Use custom slots** for complex cell rendering
7. **Enable search** for tables with many rows
8. **Set appropriate page sizes** based on data volume

---

## 🎨 Styling

All components use Tailwind CSS and follow the design system. They automatically adapt to:
- Light/dark mode
- Responsive breakpoints
- Accessibility requirements

---

## 🔗 Related Files

- `components/common/EnhancedDataTable.vue` - Enhanced table component
- `components/common/DatabaseSelect.vue` - Database-driven select component
- `components/common/Modal.vue` - Enhanced modal component
- `api/orderConfigs.js` - API methods for order configs
- `api/users.js` - API methods for users


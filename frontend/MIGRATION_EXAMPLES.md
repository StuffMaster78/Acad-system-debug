# Migration Examples: Replacing Hardcoded Dropdowns and Tables

This document provides practical examples of migrating from hardcoded components to the new enhanced, database-driven components.

---

## 🔽 Replacing Hardcoded Selects with DatabaseSelect

### Example 1: Paper Type Select

**Before (Hardcoded):**
```vue
<template>
  <div>
    <label class="block text-sm font-medium text-gray-700 mb-2">
      Paper Type <span class="text-red-500">*</span>
    </label>
    <select
      v-model="form.paper_type_id"
      required
      class="w-full border rounded-lg px-4 py-3"
    >
      <option value="">Select paper type</option>
      <option value="1">Essay</option>
      <option value="2">Research Paper</option>
      <option value="3">Dissertation</option>
      <option value="4">Thesis</option>
      <option value="5">Case Study</option>
    </select>
  </div>
</template>
```

**After (Database-Driven):**
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
</script>
```

**Benefits:**
- ✅ Always shows current options from database
- ✅ No need to update code when options change
- ✅ Consistent UI across the app
- ✅ Built-in loading and error states

---

### Example 2: Subject Select with Filtering

**Before:**
```vue
<template>
  <select v-model="form.subject_id">
    <option value="">Select subject</option>
    <option v-for="subject in subjects" :key="subject.id" :value="subject.id">
      {{ subject.name }}
    </option>
  </select>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import orderConfigsAPI from '@/api/orderConfigs'

const subjects = ref([])

onMounted(async () => {
  const response = await orderConfigsAPI.getSubjects()
  subjects.value = response.data?.results || response.data || []
})
</script>
```

**After:**
```vue
<template>
  <DatabaseSelect
    v-model="form.subject_id"
    source="subjects"
    label="Subject"
    placeholder="Select a subject..."
    :filter-fn="(subject) => subject.is_technical"
    helper-text="Only technical subjects are shown"
  />
</template>

<script setup>
import DatabaseSelect from '@/components/common/DatabaseSelect.vue'
</script>
```

**Benefits:**
- ✅ Less code (no manual API calls)
- ✅ Built-in filtering
- ✅ Automatic error handling
- ✅ Loading states handled automatically

---

### Example 3: Client Select with API Parameters

**Before:**
```vue
<template>
  <select v-model="form.client_id">
    <option value="">Select client</option>
    <option v-for="client in clients" :key="client.id" :value="client.id">
      {{ client.username }} ({{ client.email }})
    </option>
  </select>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import usersAPI from '@/api/users'

const clients = ref([])

onMounted(async () => {
  const response = await usersAPI.list({ role: 'client', website_id: currentWebsiteId })
  clients.value = response.data?.results || []
})
</script>
```

**After:**
```vue
<template>
  <DatabaseSelect
    v-model="form.client_id"
    source="clients"
    label="Client"
    placeholder="Select a client..."
    :api-params="{ website_id: currentWebsiteId }"
    label-key="username"
    helper-text="Select the client for this order"
  />
</template>

<script setup>
import DatabaseSelect from '@/components/common/DatabaseSelect.vue'
</script>
```

---

### Example 4: Custom Options (Status, Priority, etc.)

**Before:**
```vue
<template>
  <select v-model="form.status">
    <option value="pending">Pending</option>
    <option value="active">Active</option>
    <option value="completed">Completed</option>
    <option value="cancelled">Cancelled</option>
  </select>
</template>
```

**After:**
```vue
<template>
  <DatabaseSelect
    v-model="form.status"
    source="custom"
    label="Status"
    :custom-options="statusOptions"
    value-key="value"
    label-key="label"
  />
</template>

<script setup>
import DatabaseSelect from '@/components/common/DatabaseSelect.vue'

// If these come from database in the future, just change source
const statusOptions = [
  { value: 'pending', label: 'Pending' },
  { value: 'active', label: 'Active' },
  { value: 'completed', label: 'Completed' },
  { value: 'cancelled', label: 'Cancelled' },
]
</script>
```

---

## 📊 Replacing Basic Tables with EnhancedDataTable

### Example 1: Simple Order List

**Before:**
```vue
<template>
  <div class="overflow-x-auto">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Topic</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
        </tr>
      </thead>
      <tbody class="bg-white divide-y divide-gray-200">
        <tr v-for="order in orders" :key="order.id">
          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ order.id }}</td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ order.topic }}</td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ order.client?.username }}</td>
          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ order.status }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
```

**After:**
```vue
<template>
  <EnhancedDataTable
    :items="orders"
    :columns="columns"
    :loading="loading"
    :searchable="true"
    :search-fields="['topic', 'client.username', 'status']"
    :show-view-action="true"
    @view="viewOrder"
  >
    <!-- Custom status cell -->
    <template #cell-status="{ value }">
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
  </EnhancedDataTable>
</template>

<script setup>
import EnhancedDataTable from '@/components/common/EnhancedDataTable.vue'

const columns = [
  { key: 'id', label: 'ID', sortable: true },
  { key: 'topic', label: 'Topic', sortable: true },
  { key: 'client.username', label: 'Client', sortable: true },
  { key: 'status', label: 'Status', sortable: true },
]

const viewOrder = (order) => {
  router.push(`/orders/${order.id}`)
}
</script>
```

---

### Example 2: Table with Actions

**Before:**
```vue
<template>
  <table>
    <thead>
      <tr>
        <th>Name</th>
        <th>Email</th>
        <th>Actions</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="user in users" :key="user.id">
        <td>{{ user.username }}</td>
        <td>{{ user.email }}</td>
        <td>
          <button @click="editUser(user)">Edit</button>
          <button @click="deleteUser(user)">Delete</button>
        </td>
      </tr>
    </tbody>
  </table>
</template>
```

**After:**
```vue
<template>
  <EnhancedDataTable
    :items="users"
    :columns="columns"
    :show-edit-action="true"
    :show-delete-action="true"
    @edit="editUser"
    @delete="deleteUser"
  />
</template>

<script setup>
import EnhancedDataTable from '@/components/common/EnhancedDataTable.vue'

const columns = [
  { key: 'username', label: 'Name', sortable: true },
  { key: 'email', label: 'Email', sortable: true },
]
</script>
```

---

## 🪟 Enhancing Modals

### Example: Basic Modal Enhancement

**Before:**
```vue
<template>
  <div v-if="showModal" class="fixed inset-0 bg-black bg-opacity-50">
    <div class="bg-white rounded-lg p-6 max-w-md">
      <h2>Create Order</h2>
      <p>Fill in the details</p>
      <!-- Content -->
      <button @click="showModal = false">Close</button>
    </div>
  </div>
</template>
```

**After:**
```vue
<template>
  <Modal
    v-model:visible="showModal"
    title="Create Order"
    subtitle="Fill in the details below"
    icon="📝"
    size="lg"
  >
    <!-- Content -->
    <template #footer>
      <button @click="showModal = false" class="btn btn-secondary">Cancel</button>
      <button @click="submitForm" class="btn btn-primary">Create</button>
    </template>
  </Modal>
</template>

<script setup>
import Modal from '@/components/common/Modal.vue'
</script>
```

---

## 🔍 Finding Components to Migrate

### Search Commands

```bash
# Find all select elements
grep -r "<select" frontend/src/views --include="*.vue"

# Find hardcoded option arrays
grep -r "options.*=.*\[" frontend/src/views --include="*.vue"

# Find basic tables
grep -r "<table" frontend/src/views --include="*.vue"

# Find modals without Modal component
grep -r "fixed inset-0.*bg-black" frontend/src/views --include="*.vue"
```

---

## ✅ Migration Checklist

### For Each Component:

1. **Identify hardcoded elements**
   - [ ] Select dropdowns
   - [ ] Option arrays
   - [ ] Basic tables
   - [ ] Custom modals

2. **Plan migration**
   - [ ] Determine data source for selects
   - [ ] Define table columns
   - [ ] Plan modal enhancements

3. **Implement changes**
   - [ ] Replace selects with DatabaseSelect
   - [ ] Replace tables with EnhancedDataTable
   - [ ] Enhance modals with Modal component

4. **Test**
   - [ ] Verify data loads correctly
   - [ ] Test search and sorting
   - [ ] Test on mobile devices
   - [ ] Verify error handling

5. **Document**
   - [ ] Update component documentation
   - [ ] Note any special configurations

---

## 🎯 Priority Order

### High Priority (Do First)
1. Order creation forms
2. Admin configuration pages
3. User management forms
4. Main data tables (orders, users, payments)

### Medium Priority
1. Filter components
2. Settings pages
3. Secondary tables
4. Report views

### Low Priority
1. Internal tools
2. Debug views
3. Legacy components

---

## 📝 Notes

- Always test after migration
- Keep backup of original code
- Update related tests
- Document any special cases
- Consider performance implications

---

**Last Updated**: December 2025


# Frontend Quick Reference Guide

A quick reference for common patterns and code snippets.

## Table of Contents
- [API Calls](#api-calls)
- [Components](#components)
- [State Management](#state-management)
- [Forms](#forms)
- [Error Handling](#error-handling)
- [Permissions](#permissions)
- [Styling](#styling)
- [Common Patterns](#common-patterns)

---

## API Calls

### Basic GET Request
```javascript
import { writerManagementAPI } from '@/api'

const response = await writerManagementAPI.getProfile()
const data = response.data
```

### POST Request with Data
```javascript
await ordersAPI.createOrder({
  topic: 'My Order',
  subject_id: 1,
  // ... other fields
})
```

### PATCH/PUT Request
```javascript
await ordersAPI.updateOrder(orderId, {
  topic: 'Updated Topic'
})
```

### DELETE Request
```javascript
await ordersAPI.deleteOrder(orderId)
```

### With Error Handling
```javascript
import { useToast } from '@/composables/useToast'
const { success, error } = useToast()

try {
  await apiCall()
  success('Operation successful')
} catch (err) {
  error(err.message || 'Operation failed')
}
```

### File Upload
```javascript
const formData = new FormData()
formData.append('file', file)
formData.append('description', 'File description')

await apiClient.post('/upload/', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
})
```

### File Download
```javascript
const response = await api.downloadFile(id)
const blob = response.data
const url = window.URL.createObjectURL(blob)
const link = document.createElement('a')
link.href = url
link.download = 'filename.pdf'
link.click()
window.URL.revokeObjectURL(url)
```

---

## Components

### Basic Component Structure
```vue
<template>
  <div>
    <h1>{{ title }}</h1>
    <button @click="handleClick">Click Me</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  title: String
})

const emit = defineEmits(['click'])

const handleClick = () => {
  emit('click')
}
</script>
```

### Loading State
```vue
<template>
  <div v-if="loading">Loading...</div>
  <div v-else-if="error">{{ error }}</div>
  <div v-else>{{ data }}</div>
</template>

<script setup>
const loading = ref(false)
const error = ref(null)
const data = ref(null)
</script>
```

### Conditional Rendering
```vue
<!-- Use v-if for expensive operations or when element shouldn't exist -->
<div v-if="show">Expensive content</div>

<!-- Use v-show for frequent toggles -->
<div v-show="isVisible">Toggleable content</div>
```

### List Rendering
```vue
<template>
  <div v-for="item in items" :key="item.id">
    {{ item.name }}
  </div>
</template>
```

### Modal Usage
```vue
<template>
  <Modal
    :is-open="showModal"
    @close="showModal = false"
    title="Confirm Action"
  >
    <p>Are you sure?</p>
    <template #footer>
      <button @click="handleConfirm">Confirm</button>
      <button @click="showModal = false">Cancel</button>
    </template>
  </Modal>
</template>
```

---

## State Management

### Using Pinia Store
```javascript
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const user = authStore.user
const isAuthenticated = authStore.isAuthenticated
```

### Reactive State
```javascript
import { ref, reactive, computed } from 'vue'

// Primitive values
const count = ref(0)
count.value++ // Access with .value in script

// Objects
const user = reactive({
  name: 'John',
  email: 'john@example.com'
})
user.name = 'Jane' // Direct access

// Computed
const fullName = computed(() => `${user.firstName} ${user.lastName}`)
```

### Watch
```javascript
import { watch } from 'vue'

watch(count, (newVal, oldVal) => {
  console.log(`Count changed from ${oldVal} to ${newVal}`)
})

// Watch multiple
watch([count, name], ([newCount, newName]) => {
  console.log(newCount, newName)
})
```

---

## Forms

### Basic Form
```vue
<template>
  <form @submit.prevent="handleSubmit">
    <input v-model="form.name" type="text" placeholder="Name" />
    <input v-model="form.email" type="email" placeholder="Email" />
    <button type="submit" :disabled="loading">
      {{ loading ? 'Submitting...' : 'Submit' }}
    </button>
  </form>
</template>

<script setup>
import { ref } from 'vue'
import { useToast } from '@/composables/useToast'

const { success, error } = useToast()
const loading = ref(false)
const form = ref({
  name: '',
  email: ''
})

const handleSubmit = async () => {
  loading.value = true
  try {
    await api.createItem(form.value)
    success('Created successfully')
    form.value = { name: '', email: '' } // Reset
  } catch (err) {
    error('Failed to create')
  } finally {
    loading.value = false
  }
}
</script>
```

### Form Validation
```vue
<script setup>
import { ref } from 'vue'
import * as yup from 'yup'

const schema = yup.object({
  name: yup.string().required('Name is required'),
  email: yup.string().email('Invalid email').required('Email is required')
})

const form = ref({ name: '', email: '' })
const errors = ref({})

const validate = async () => {
  try {
    await schema.validate(form.value, { abortEarly: false })
    errors.value = {}
    return true
  } catch (err) {
    errors.value = {}
    err.inner.forEach(e => {
      errors.value[e.path] = e.message
    })
    return false
  }
}
</script>
```

---

## Error Handling

### Using getErrorMessage
```javascript
import { getErrorMessage } from '@/utils/error'

try {
  await apiCall()
} catch (error) {
  const message = getErrorMessage(error)
  console.error(message)
}
```

### Toast Notifications
```javascript
import { useToast } from '@/composables/useToast'

const { success, error, warning, info } = useToast()

success('Operation successful')
error('Operation failed')
warning('Please check your input')
info('Information message')
```

### Error Display in Template
```vue
<template>
  <div v-if="error" class="text-red-600">
    {{ error }}
  </div>
</template>
```

---

## Permissions

### Check Role
```javascript
import { hasRole } from '@/utils/permissions'

if (hasRole(user.role, ['admin', 'superadmin'])) {
  // Show admin features
}
```

### Check Permission
```javascript
import { hasPermission } from '@/utils/permissions'

if (hasPermission(user.role, 'orders.create')) {
  // Show create button
}
```

### In Template
```vue
<template>
  <button v-if="hasRole(user.role, ['admin'])">
    Admin Only Button
  </button>
</template>

<script setup>
import { hasRole } from '@/utils/permissions'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const user = authStore.user
</script>
```

---

## Styling

### Tailwind Classes
```vue
<!-- Basic -->
<div class="p-4 bg-white rounded-lg shadow">
  Content
</div>

<!-- Dark mode -->
<div class="bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
  Content
</div>

<!-- Responsive -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  Items
</div>
```

### Conditional Classes
```vue
<div :class="[
  'base-class',
  isActive ? 'active-class' : 'inactive-class',
  { 'conditional-class': someCondition }
]">
  Content
</div>
```

### Scoped Styles
```vue
<style scoped>
.my-component {
  color: red;
}
</style>
```

---

## Common Patterns

### Pagination
```javascript
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const fetchData = async () => {
  const response = await api.getItems({
    page: page.value,
    page_size: pageSize.value
  })
  items.value = response.data.results
  total.value = response.data.count
}
```

### Search with Debounce
```javascript
import { ref } from 'vue'
import { debounce } from '@/utils/debounce'

const searchQuery = ref('')

const debouncedSearch = debounce(async (query) => {
  if (query.length > 2) {
    const results = await api.search(query)
    // Handle results
  }
}, 300)

// In template: @input="debouncedSearch($event.target.value)"
```

### Filtering
```javascript
import { computed } from 'vue'

const statusFilter = ref('all')
const items = ref([])

const filteredItems = computed(() => {
  return items.value.filter(item => {
    if (statusFilter.value !== 'all' && item.status !== statusFilter.value) {
      return false
    }
    return true
  })
})
```

### Optimistic Updates
```javascript
const handleLike = async () => {
  // Optimistic update
  likes.value++
  isLiked.value = true
  
  try {
    await api.likePost(postId)
  } catch (error) {
    // Revert on error
    likes.value--
    isLiked.value = false
    error('Failed to like post')
  }
}
```

### Cleanup (Intervals/Timeouts)
```javascript
import { onMounted, onUnmounted } from 'vue'

let interval = null

onMounted(() => {
  interval = setInterval(() => {
    // Do something
  }, 1000)
})

onUnmounted(() => {
  if (interval) {
    clearInterval(interval)
  }
})
```

### Route Navigation
```javascript
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// Navigate
router.push('/orders')
router.push({ name: 'OrderDetail', params: { id: 123 } })

// Get params
const orderId = route.params.id
const query = route.query
```

### Formatting
```javascript
import { formatCurrency, formatDate, formatId } from '@/utils/formatDisplay'

formatCurrency(1000) // "$1,000.00"
formatDate(new Date()) // "Jan 1, 2024"
formatId(12345) // "#12345"
```

---

## Composables Quick Reference

### useToast
```javascript
const { success, error, warning, info } = useToast()
success('Success message')
error('Error message')
```

### useTheme
```javascript
const { theme, isDark, toggleTheme, setTheme } = useTheme()
toggleTheme()
setTheme('dark')
```

### useSessionManagement
```javascript
const { extendSession, sessionStatus } = useSessionManagement()
await extendSession()
```

### useOnlineStatus
```javascript
const { isOnline, updateStatus } = useOnlineStatus()
await updateStatus(true)
```

### useWriterDashboardRealtime
```javascript
const { status, data } = useWriterDashboardRealtime()
// status: 'connecting' | 'connected' | 'error'
// data: real-time dashboard data
```

---

## Common Utilities

### Error Handling
```javascript
import { getErrorMessage, normalizeApiError } from '@/utils/error'
const message = getErrorMessage(error)
```

### Permissions
```javascript
import { hasRole, hasPermission, ROLES } from '@/utils/permissions'
hasRole(user.role, [ROLES.ADMIN])
hasPermission(user.role, 'orders.create')
```

### Formatting
```javascript
import { formatCurrency, formatDate, formatId } from '@/utils/formatDisplay'
```

### Debounce
```javascript
import { debounce } from '@/utils/debounce'
const debouncedFn = debounce(fn, 300)
```

---

## Tips & Tricks

1. **Always use `.value` for refs in script, not in template**
2. **Use `computed` for derived data, not methods**
3. **Use `v-if` for expensive operations, `v-show` for frequent toggles**
4. **Always handle errors in API calls**
5. **Clean up intervals/timeouts in `onUnmounted`**
6. **Use meaningful variable names**
7. **Keep components focused and small**
8. **Use TypeScript-style JSDoc for complex functions**
9. **Test with different screen sizes (responsive design)**
10. **Check accessibility (keyboard navigation, ARIA labels)**

---

**Last Updated**: November 2025


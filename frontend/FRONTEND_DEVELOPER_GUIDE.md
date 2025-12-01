# Frontend Developer Guide

## Table of Contents
1. [Project Overview](#project-overview)
2. [Getting Started](#getting-started)
3. [Project Structure](#project-structure)
4. [Core Concepts](#core-concepts)
5. [API Integration](#api-integration)
6. [Component Development](#component-development)
7. [State Management](#state-management)
8. [Routing](#routing)
9. [Styling](#styling)
10. [Common Utilities](#common-utilities)
11. [Composables](#composables)
12. [Development Workflow](#development-workflow)
13. [Best Practices](#best-practices)

---

## Project Overview

This is a Vue 3 single-page application (SPA) built for a writing/order management system. It supports multiple user roles (writers, clients, admins, editors, support staff) with role-based access control.

### Tech Stack
- **Framework**: Vue 3 (Composition API)
- **Build Tool**: Vite
- **Router**: Vue Router 4
- **State Management**: Pinia
- **HTTP Client**: Axios
- **Styling**: Tailwind CSS 4
- **Charts**: ApexCharts (via vue3-apexcharts)
- **Form Validation**: VeeValidate + Yup
- **Rich Text Editor**: Quill

### Key Features
- Multi-role dashboard (writers, clients, admins, editors, support)
- Real-time updates via Server-Sent Events (SSE)
- Dark/Light theme support
- Session management with auto-refresh
- Order management and tracking
- Payment and financial management
- Notification system
- Activity logging
- Advanced search and filtering
- Export functionality (CSV, Excel, PDF)

---

## Getting Started

### Prerequisites
- Node.js 18+ and npm/pnpm
- Access to the backend API

### Installation

```bash
# Install dependencies
pnpm install
# or
npm install
```

### Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
# or
VITE_API_FULL_URL=http://localhost:8000
```

### Development Server

```bash
# Start dev server
pnpm dev
# or
npm run dev
```

The app will be available at `http://localhost:5173` (or the port Vite assigns).

### Building for Production

```bash
# Build for all roles
pnpm build:all

# Build for specific role
pnpm build:writers
pnpm build:clients
pnpm build:staff
```

---

## Project Structure

```
frontend/
├── src/
│   ├── api/              # API client modules
│   │   ├── client.js     # Axios instance with interceptors
│   │   ├── index.js      # API exports
│   │   └── *.js          # Feature-specific API modules
│   │
│   ├── components/       # Reusable Vue components
│   │   ├── common/       # Shared components (Modal, DataTable, etc.)
│   │   ├── dashboard/    # Dashboard-specific components
│   │   └── [feature]/    # Feature-specific components
│   │
│   ├── composables/      # Vue Composition API composables
│   │   ├── useToast.js   # Toast notifications
│   │   ├── useTheme.js   # Theme management
│   │   └── *.js          # Other composables
│   │
│   ├── layouts/          # Layout components
│   │   └── DashboardLayout.vue
│   │
│   ├── router/           # Vue Router configuration
│   │   └── index.js
│   │
│   ├── stores/           # Pinia stores
│   │   └── auth.js       # Authentication store
│   │
│   ├── services/         # Business logic services
│   │   └── sessionManager.js
│   │
│   ├── utils/            # Utility functions
│   │   ├── error.js      # Error handling
│   │   ├── permissions.js # Role-based permissions
│   │   └── *.js          # Other utilities
│   │
│   ├── views/            # Page components (routes)
│   │   ├── auth/         # Authentication pages
│   │   ├── dashboard/    # Dashboard pages
│   │   ├── writers/      # Writer-specific pages
│   │   ├── admin/        # Admin pages
│   │   └── [feature]/    # Feature pages
│   │
│   ├── style.css         # Global styles
│   ├── App.vue           # Root component
│   └── main.js           # Application entry point
│
├── tailwind.config.js    # Tailwind configuration
├── vite.config.js        # Vite configuration
└── package.json
```

---

## Core Concepts

### Component Architecture

Components follow Vue 3 Composition API patterns:

```vue
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { writerManagementAPI } from '@/api'

const { success, error } = useToast()
const loading = ref(false)
const data = ref(null)

const fetchData = async () => {
  loading.value = true
  try {
    const response = await writerManagementAPI.getProfile()
    data.value = response.data
    success('Data loaded successfully')
  } catch (err) {
    error('Failed to load data')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div>
    <div v-if="loading">Loading...</div>
    <div v-else>{{ data }}</div>
  </div>
</template>
```

### Reactive State

Use `ref()` for primitive values and `reactive()` for objects:

```javascript
import { ref, reactive } from 'vue'

// Primitive values
const count = ref(0)
const name = ref('John')

// Objects
const user = reactive({
  name: 'John',
  email: 'john@example.com'
})

// Access refs in template (auto-unwrapped)
// Access in script: count.value
```

### Computed Properties

Use `computed()` for derived state:

```javascript
import { ref, computed } from 'vue'

const firstName = ref('John')
const lastName = ref('Doe')

const fullName = computed(() => {
  return `${firstName.value} ${lastName.value}`
})
```

---

## API Integration

### API Client Setup

The API client (`src/api/client.js`) is configured with:
- Automatic token injection
- Token refresh on 401 errors
- Proactive token refresh (every 20 minutes)
- Error normalization
- Retry logic for network errors

### Using API Modules

Import and use API modules from `@/api`:

```javascript
import { 
  writerManagementAPI, 
  ordersAPI, 
  authAPI 
} from '@/api'

// GET request
const response = await writerManagementAPI.getProfile()
const profile = response.data

// POST request
await ordersAPI.createOrder({
  topic: 'My Order',
  // ... other fields
})

// With error handling
try {
  const response = await ordersAPI.getOrder(123)
} catch (error) {
  console.error('API Error:', error.message)
  // Error is already normalized by interceptor
}
```

### Creating New API Modules

Create a new file in `src/api/`:

```javascript
import apiClient from './client'

const myFeatureAPI = {
  // GET request
  getItems: (params) => 
    apiClient.get('/my-feature/items/', { params }),
  
  // POST request
  createItem: (data) => 
    apiClient.post('/my-feature/items/', data),
  
  // PUT/PATCH request
  updateItem: (id, data) => 
    apiClient.patch(`/my-feature/items/${id}/`, data),
  
  // DELETE request
  deleteItem: (id) => 
    apiClient.delete(`/my-feature/items/${id}/`),
  
  // Custom action
  customAction: (id, data) => 
    apiClient.post(`/my-feature/items/${id}/custom-action/`, data),
}

export default myFeatureAPI
```

Then export it in `src/api/index.js`:

```javascript
export { default as myFeatureAPI } from './my-feature'
```

### File Uploads

For file uploads, use `FormData`:

```javascript
const formData = new FormData()
formData.append('file', file)
formData.append('description', 'File description')

const response = await apiClient.post('/upload/', formData, {
  headers: {
    'Content-Type': 'multipart/form-data'
  }
})
```

### Downloading Files

For file downloads (PDFs, CSVs, etc.):

```javascript
const response = await writerManagementAPI.downloadReceipt(paymentId)
const blob = response.data
const url = window.URL.createObjectURL(blob)
const link = document.createElement('a')
link.href = url
link.download = 'receipt.pdf'
link.click()
window.URL.revokeObjectURL(url)
```

---

## Component Development

### Component Structure

Follow this structure for components:

```vue
<template>
  <!-- Template content -->
</template>

<script setup>
// 1. Imports
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'

// 2. Props
const props = defineProps({
  title: {
    type: String,
    required: true
  },
  items: {
    type: Array,
    default: () => []
  }
})

// 3. Emits
const emit = defineEmits(['update', 'delete'])

// 4. Composables
const { success, error } = useToast()

// 5. Reactive state
const loading = ref(false)
const selectedItem = ref(null)

// 6. Computed properties
const filteredItems = computed(() => {
  return props.items.filter(item => item.active)
})

// 7. Methods
const handleClick = () => {
  emit('update', selectedItem.value)
}

// 8. Lifecycle hooks
onMounted(() => {
  // Initialization
})
</script>

<style scoped>
/* Component-specific styles */
</style>
```

### Common Components

#### Modal Component

```vue
<template>
  <Modal
    :is-open="showModal"
    @close="showModal = false"
    title="Confirm Action"
  >
    <p>Are you sure you want to proceed?</p>
    <template #footer>
      <button @click="handleConfirm">Confirm</button>
      <button @click="showModal = false">Cancel</button>
    </template>
  </Modal>
</template>

<script setup>
import Modal from '@/components/common/Modal.vue'
</script>
```

#### DataTable Component

```vue
<template>
  <DataTable
    :columns="columns"
    :data="items"
    :loading="loading"
    :pagination="pagination"
    @page-change="handlePageChange"
    @sort="handleSort"
  />
</template>

<script setup>
import DataTable from '@/components/common/DataTable.vue'

const columns = [
  { key: 'id', label: 'ID', sortable: true },
  { key: 'name', label: 'Name', sortable: true },
  { key: 'status', label: 'Status' }
]
</script>
```

#### StatusBadge Component

```vue
<template>
  <StatusBadge :status="order.status" />
</template>

<script setup>
import StatusBadge from '@/components/common/StatusBadge.vue'
</script>
```

---

## State Management

### Pinia Store

The app uses Pinia for state management. Example store:

```javascript
// stores/auth.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(null)
  
  const isAuthenticated = computed(() => !!token.value)
  
  const login = (userData, tokenData) => {
    user.value = userData
    token.value = tokenData
    localStorage.setItem('user', JSON.stringify(userData))
    localStorage.setItem('access_token', tokenData)
  }
  
  const logout = () => {
    user.value = null
    token.value = null
    localStorage.removeItem('user')
    localStorage.removeItem('access_token')
  }
  
  return {
    user,
    token,
    isAuthenticated,
    login,
    logout
  }
})
```

### Using Stores

```vue
<script setup>
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// Access state
const user = authStore.user
const isAuthenticated = authStore.isAuthenticated

// Call actions
authStore.login(userData, token)
</script>
```

---

## Routing

### Route Definition

Routes are defined in `src/router/index.js`:

```javascript
{
  path: '/orders',
  name: 'Orders',
  component: () => import('@/views/orders/OrderList.vue'),
  meta: { 
    requiresAuth: true,
    title: 'Orders',
    roles: ['client', 'admin', 'superadmin']
  }
}
```

### Navigation Guards

Routes are protected by authentication and role-based guards:

```javascript
// In router/index.js
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.meta.roles && !hasRole(to.meta.roles)) {
    next('/dashboard') // Redirect to dashboard if no permission
  } else {
    next()
  }
})
```

### Programmatic Navigation

```javascript
import { useRouter } from 'vue-router'

const router = useRouter()

// Navigate
router.push('/orders')
router.push({ name: 'Orders', params: { id: 123 } })

// Replace (no history entry)
router.replace('/dashboard')

// Go back
router.back()
```

### Route Parameters

```vue
<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
const orderId = route.params.id
const query = route.query
</script>
```

---

## Styling

### Tailwind CSS

The project uses Tailwind CSS 4 with class-based dark mode.

### Basic Usage

```vue
<template>
  <div class="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
      Title
    </h1>
  </div>
</template>
```

### Dark Mode

Dark mode is automatically handled via the `dark:` prefix:

```vue
<div class="bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
  Content
</div>
```

### Custom Colors

Colors are defined in `src/style.css` using CSS variables:

```css
:root {
  --color-primary-50: #f0f9ff;
  --color-primary-500: #3b82f6;
  --color-primary-900: #1e3a8a;
}
```

### Responsive Design

Use Tailwind's responsive prefixes:

```vue
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <!-- Responsive grid -->
</div>
```

---

## Common Utilities

### Error Handling

```javascript
import { getErrorMessage } from '@/utils/error'

try {
  await apiCall()
} catch (error) {
  const message = getErrorMessage(error)
  // message is user-friendly error string
}
```

### Permissions

```javascript
import { hasRole, hasPermission } from '@/utils/permissions'

// Check role
if (hasRole(['admin', 'superadmin'])) {
  // Show admin features
}

// Check permission
if (hasPermission('orders.create')) {
  // Show create button
}
```

### Formatting

```javascript
import { formatCurrency, formatDate, formatId } from '@/utils/formatDisplay'

formatCurrency(1000) // "$1,000.00"
formatDate(new Date()) // "Jan 1, 2024"
formatId(12345) // "#12345"
```

### Debouncing

```javascript
import { debounce } from '@/utils/debounce'

const debouncedSearch = debounce((query) => {
  performSearch(query)
}, 300)

// Use in input handler
input.addEventListener('input', (e) => {
  debouncedSearch(e.target.value)
})
```

---

## Composables

### useToast

Show toast notifications:

```vue
<script setup>
import { useToast } from '@/composables/useToast'

const { success, error, warning, info } = useToast()

const handleSave = async () => {
  try {
    await saveData()
    success('Saved successfully!')
  } catch (err) {
    error('Failed to save')
  }
}
</script>
```

### useTheme

Manage theme (light/dark/system):

```vue
<script setup>
import { useTheme } from '@/composables/useTheme'

const { theme, isDark, toggleTheme, setTheme } = useTheme()

// Toggle between light/dark
toggleTheme()

// Set specific theme
setTheme('dark')
</script>
```

### useSessionManagement

Handle session timeouts and extensions:

```vue
<script setup>
import { useSessionManagement } from '@/composables/useSessionManagement'

const { extendSession, sessionStatus } = useSessionManagement()

// Extend session
await extendSession()
</script>
```

### useOnlineStatus

Track online/offline status:

```vue
<script setup>
import { useOnlineStatus } from '@/composables/useOnlineStatus'

const { isOnline, updateStatus } = useOnlineStatus()

// Update status
await updateStatus(true)
</script>
```

### useWriterDashboardRealtime

Real-time dashboard updates via SSE:

```vue
<script setup>
import { useWriterDashboardRealtime } from '@/composables/useWriterDashboardRealtime'

const { status, data } = useWriterDashboardRealtime()

// data contains real-time dashboard data
// status: 'connecting' | 'connected' | 'error'
</script>
```

---

## Development Workflow

### Adding a New Feature

1. **Create API module** (if needed):
   ```javascript
   // src/api/my-feature.js
   import apiClient from './client'
   export default { /* API methods */ }
   ```

2. **Create view component**:
   ```vue
   // src/views/my-feature/MyFeature.vue
   <template>...</template>
   <script setup>...</script>
   ```

3. **Add route**:
   ```javascript
   // src/router/index.js
   {
     path: '/my-feature',
     component: () => import('@/views/my-feature/MyFeature.vue'),
     meta: { requiresAuth: true }
   }
   ```

4. **Create reusable components** (if needed):
   ```vue
   // src/components/my-feature/MyFeatureCard.vue
   ```

### Code Style

- Use Composition API (`<script setup>`)
- Use TypeScript-style JSDoc comments for complex functions
- Follow Vue 3 style guide
- Use meaningful variable names
- Keep components focused and small

### Testing

```bash
# Lint code
pnpm lint

# Build for production
pnpm build
```

---

## Best Practices

### 1. Error Handling

Always handle errors in API calls:

```javascript
try {
  const response = await apiCall()
  success('Operation successful')
} catch (error) {
  error(getErrorMessage(error))
}
```

### 2. Loading States

Show loading indicators:

```vue
<template>
  <div v-if="loading">Loading...</div>
  <div v-else-if="error">{{ error }}</div>
  <div v-else>{{ data }}</div>
</template>
```

### 3. Optimistic Updates

Update UI immediately, revert on error:

```javascript
const handleLike = async () => {
  // Optimistic update
  likes.value++
  
  try {
    await api.likePost(postId)
  } catch (error) {
    // Revert on error
    likes.value--
    error('Failed to like post')
  }
}
```

### 4. Component Props

Use proper prop definitions:

```javascript
defineProps({
  title: {
    type: String,
    required: true
  },
  items: {
    type: Array,
    default: () => []
  },
  status: {
    type: String,
    validator: (value) => ['active', 'inactive'].includes(value)
  }
})
```

### 5. Computed vs Methods

Use `computed` for derived data, `methods` for actions:

```javascript
// ✅ Good: Computed for derived data
const fullName = computed(() => `${firstName.value} ${lastName.value}`)

// ✅ Good: Method for actions
const handleSubmit = () => {
  // Submit logic
}
```

### 6. Memory Leaks

Clean up intervals/timeouts:

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

### 7. API Calls

Use composables or methods, not in template:

```vue
<!-- ❌ Bad -->
<button @click="apiCall()">Click</button>

<!-- ✅ Good -->
<button @click="handleClick">Click</button>

<script setup>
const handleClick = async () => {
  await apiCall()
}
</script>
```

### 8. Accessibility

- Use semantic HTML
- Add ARIA labels where needed
- Ensure keyboard navigation works
- Test with screen readers

### 9. Performance

- Use `v-show` for frequent toggles, `v-if` for conditional rendering
- Lazy load heavy components
- Debounce search inputs
- Use `computed` instead of methods in templates

### 10. Security

- Never store sensitive data in localStorage (except tokens)
- Validate user input
- Sanitize HTML content
- Use HTTPS in production

---

## Common Patterns

### Pagination

```vue
<script setup>
import { ref } from 'vue'

const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const fetchData = async () => {
  const response = await api.getItems({
    page: page.value,
    page_size: pageSize.value
  })
  data.value = response.data.results
  total.value = response.data.count
}
</script>

<template>
  <Pagination
    :current-page="page"
    :page-size="pageSize"
    :total="total"
    @page-change="page = $event; fetchData()"
  />
</template>
```

### Filtering

```vue
<script setup>
import { ref, computed } from 'vue'

const searchQuery = ref('')
const statusFilter = ref('all')
const items = ref([])

const filteredItems = computed(() => {
  return items.value.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesStatus = statusFilter.value === 'all' || item.status === statusFilter.value
    return matchesSearch && matchesStatus
  })
})
</script>
```

### Form Handling

```vue
<script setup>
import { ref } from 'vue'
import { useToast } from '@/composables/useToast'

const { success, error } = useToast()
const form = ref({
  name: '',
  email: ''
})
const loading = ref(false)

const handleSubmit = async () => {
  loading.value = true
  try {
    await api.createItem(form.value)
    success('Item created successfully')
    // Reset form or navigate
  } catch (err) {
    error('Failed to create item')
  } finally {
    loading.value = false
  }
}
</script>
```

---

## Troubleshooting

### Common Issues

1. **API calls failing with 401**
   - Check if token is in localStorage
   - Verify token refresh is working
   - Check API base URL in `.env`

2. **Dark mode not working**
   - Ensure `initTheme()` is called in `main.js`
   - Check `tailwind.config.js` has `darkMode: 'class'`
   - Verify CSS variables are defined

3. **Routes not working**
   - Check route definition in `router/index.js`
   - Verify authentication guards
   - Check role permissions

4. **Components not updating**
   - Ensure reactive state is used (`ref`, `reactive`)
   - Check if computed properties are used correctly
   - Verify props are defined correctly

---

## Additional Resources

- [Vue 3 Documentation](https://vuejs.org/)
- [Vue Router Documentation](https://router.vuejs.org/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [Axios Documentation](https://axios-http.com/)

---

## Support

For questions or issues:
1. Check this documentation
2. Review existing code patterns
3. Ask the team lead or backend developers
4. Check backend API documentation

---

**Last Updated**: November 2025


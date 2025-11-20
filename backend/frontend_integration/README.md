# Frontend Integration Files

This directory contains API service files, Vue components, and integration examples for the Writing System Backend.

## 📁 Files Included

### API Services

1. **auth-api.js** - Complete Authentication API Service
   - Login/Logout
   - Password change/reset
   - Magic link login
   - 2FA setup/verification
   - Session management
   - Account unlock

2. **admin-orders-api.js** - Order Management Dashboard API
3. **admin-special-orders-api.js** - Special Orders Management Dashboard API
4. **admin-class-bundles-api.js** - Class Bundles Management Dashboard API
5. **admin-tips-api.js** - Tip Management & Earnings Tracking Dashboard API
6. **admin-reviews-api.js** - Review Moderation Dashboard API
7. **admin-disputes-api.js** - Dispute Management Dashboard API
8. **admin-refunds-api.js** - Refund Management Dashboard API

### Vue Components

1. **Login.vue** - Complete login page with:
   - Email/Password login with "Remember Me"
   - Magic link login
   - 2FA verification
   - Error handling
   - Auto-redirect from magic links

2. **PasswordChange.vue** - Password change page with:
   - Current password verification
   - Password strength indicator
   - Password requirements display
   - Real-time validation

3. **PasswordReset.vue** - Password reset flow with:
   - Request reset link
   - Reset confirmation
   - Success state
   - Token handling from email

4. **AccountSettings.vue** - Account settings page with:
   - Profile management
   - Password change link
   - 2FA setup/disable
   - Active sessions management
   - Logout all devices

5. **TipManagement.vue** - Tip Management dashboard with:
   - Dashboard tab (summary, stats, breakdowns)
   - List Tips tab (filtering, pagination)
   - Analytics tab (trends, top performers)
   - Earnings tab (earnings breakdown)

## 🚀 Quick Start

### 1. Copy Files to Your Frontend Project

#### API Services
```bash
# Example for Vue.js project
cp auth-api.js /path/to/frontend/src/api/auth.js
cp admin-orders-api.js /path/to/frontend/src/api/admin/orders.js
cp admin-special-orders-api.js /path/to/frontend/src/api/admin/specialOrders.js
cp admin-class-bundles-api.js /path/to/frontend/src/api/admin/classBundles.js
cp admin-tips-api.js /path/to/frontend/src/api/admin/tips.js
cp admin-reviews-api.js /path/to/frontend/src/api/admin/reviews.js
cp admin-disputes-api.js /path/to/frontend/src/api/admin/disputes.js
cp admin-refunds-api.js /path/to/frontend/src/api/admin/refunds.js
```

#### Vue Components
```bash
# Authentication components
cp Login.vue /path/to/frontend/src/views/auth/Login.vue
cp PasswordChange.vue /path/to/frontend/src/views/auth/PasswordChange.vue
cp PasswordReset.vue /path/to/frontend/src/views/auth/PasswordReset.vue
cp AccountSettings.vue /path/to/frontend/src/views/account/Settings.vue

# Admin components
cp TipManagement.vue /path/to/frontend/src/views/admin/TipManagement.vue
```

### 2. Update Import Paths

Update the `apiClient` import in each file to match your project structure:

```javascript
// Change this:
import apiClient from '../client'

// To match your project structure, e.g.:
import apiClient from '@/api/client'
// or
import apiClient from '../utils/apiClient'
```

### 3. Use in Your Components

#### Authentication Example
```javascript
// In your Vue component
import { authApi } from '@/api/auth'

export default {
  methods: {
    async handleLogin() {
      try {
        const response = await authApi.login(email, password, rememberMe)
        // Store tokens and redirect
      } catch (error) {
        console.error('Login error:', error)
      }
    }
  }
}
```

#### Admin Dashboard Example
```javascript
// In your Vue component
import { adminTipsApi } from '@/api/admin/tips'

export default {
  async mounted() {
    try {
      const response = await adminTipsApi.getDashboard()
      this.dashboardData = response.data
    } catch (error) {
      console.error('Error loading dashboard:', error)
    }
  }
}
```

### 4. Set Up Routes

```javascript
// router/index.js
import Login from '@/views/auth/Login.vue'
import PasswordChange from '@/views/auth/PasswordChange.vue'
import PasswordReset from '@/views/auth/PasswordReset.vue'
import AccountSettings from '@/views/account/Settings.vue'
import TipManagement from '@/views/admin/TipManagement.vue'

const routes = [
  { path: '/login', component: Login },
  { path: '/account/password-change', component: PasswordChange },
  { path: '/forgot-password', component: PasswordReset },
  { path: '/account/settings', component: AccountSettings },
  { path: '/admin/tips', component: TipManagement },
  // ... other routes
]
```

## 📚 Documentation

For complete integration examples and Vue component templates, see:

- **FRONTEND_ADMIN_INTEGRATION.md** - Complete integration guide with Vue component examples

## 🔗 API Endpoints

All endpoints are prefixed with `/api/v1/admin-management/`:

### Order Management
- `GET /orders/dashboard/` - Dashboard statistics
- `GET /orders/analytics/` - Analytics and trends
- `GET /orders/assignment-queue/` - Orders needing assignment
- `GET /orders/overdue/` - Overdue orders
- `GET /orders/stuck/` - Stuck orders
- `POST /orders/bulk-assign/` - Bulk assign orders
- `POST /orders/bulk-action/` - Bulk actions
- `GET /orders/{id}/timeline/` - Order timeline

### Special Orders Management
- `GET /special-orders/dashboard/` - Dashboard statistics
- `GET /special-orders/approval-queue/` - Orders awaiting approval
- `GET /special-orders/estimated-queue/` - Orders needing estimation
- `GET /special-orders/installment-tracking/` - Installment tracking
- `GET /special-orders/analytics/` - Analytics
- `GET /special-orders/configs/` - Get configs
- `POST /special-orders/configs/` - Create/update configs

### Class Bundles Management
- `GET /class-bundles/dashboard/` - Dashboard statistics
- `GET /class-bundles/installment-tracking/` - Installment tracking
- `GET /class-bundles/deposit-pending/` - Pending deposits
- `GET /class-bundles/analytics/` - Analytics
- `GET /class-bundles/configs/` - Get configs
- `POST /class-bundles/configs/` - Create/update configs
- `GET /class-bundles/communication-threads/` - Communication threads
- `GET /class-bundles/support-tickets/` - Support tickets

### Tip Management
- `GET /tips/dashboard/` - Dashboard statistics with earnings breakdown
- `GET /tips/list_tips/` - List all tips with earnings
- `GET /tips/analytics/` - Analytics and trends
- `GET /tips/earnings/` - Detailed earnings breakdown

### Review Moderation
- `GET /reviews/moderation-queue/` - Moderation queue
- `POST /reviews/{id}/approve/` - Approve review
- `POST /reviews/{id}/reject/` - Reject review
- `POST /reviews/{id}/flag/` - Flag review
- `POST /reviews/{id}/shadow/` - Shadow hide review
- `GET /reviews/analytics/` - Analytics
- `GET /reviews/spam-detection/` - Spam detection

### Dispute Management
- `GET /disputes/dashboard/` - Dashboard statistics
- `GET /disputes/analytics/` - Analytics
- `GET /disputes/pending/` - Pending disputes
- `POST /disputes/bulk-resolve/` - Bulk resolve

### Refund Management
- `GET /refunds/dashboard/` - Dashboard statistics
- `GET /refunds/analytics/` - Analytics
- `GET /refunds/pending/` - Pending refunds
- `GET /refunds/history/` - Refund history

## 🔐 Authentication

All endpoints require authentication with a JWT token:

```javascript
// Add to your API client interceptor
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

## 📝 Example Usage

### Order Dashboard

```javascript
import { adminOrdersApi } from '@/api/admin/orders'

// Get dashboard stats
const dashboard = await adminOrdersApi.getDashboard()
console.log(dashboard.data.summary.total_orders)

// Get assignment queue
const queue = await adminOrdersApi.getAssignmentQueue({ limit: 20 })
console.log(queue.data.orders)

// Bulk assign orders
const result = await adminOrdersApi.bulkAssign({
  order_ids: [1, 2, 3],
  writer_id: 5,
  reason: 'Bulk assignment'
})
console.log(result.data.results)
```

### Special Orders Dashboard

```javascript
import { adminSpecialOrdersApi } from '@/api/admin/specialOrders'

// Get dashboard
const dashboard = await adminSpecialOrdersApi.getDashboard()

// Get approval queue
const approvalQueue = await adminSpecialOrdersApi.getApprovalQueue()

// Get installment tracking
const installments = await adminSpecialOrdersApi.getInstallmentTracking({
  status: 'overdue'
})
```

### Class Bundles Dashboard

```javascript
import { adminClassBundlesApi } from '@/api/admin/classBundles'

// Get dashboard
const dashboard = await adminClassBundlesApi.getDashboard()

// Get deposit pending
const depositPending = await adminClassBundlesApi.getDepositPending()

// Get installment tracking
const installments = await adminClassBundlesApi.getInstallmentTracking({
  status: 'overdue'
})

// Get communication threads
const threads = await adminClassBundlesApi.getCommunicationThreads({
  bundle_id: 123
})

// Get support tickets
const tickets = await adminClassBundlesApi.getSupportTickets({
  status: 'open'
})
```

### Tip Management Dashboard

```javascript
import { adminTipsApi } from '@/api/admin/tips'

// Get dashboard with earnings breakdown
const dashboard = await adminTipsApi.getDashboard({ days: 30 })

// List all tips with earnings
const tips = await adminTipsApi.listTips({
  tip_type: 'order',
  payment_status: 'completed',
  limit: 50
})

// Get analytics
const analytics = await adminTipsApi.getAnalytics({ days: 90 })

// Get detailed earnings breakdown
const earnings = await adminTipsApi.getEarnings({
  date_from: '2024-01-01',
  date_to: '2024-12-31'
})
```

## 🛠️ TypeScript Support

If using TypeScript, you can add type definitions:

```typescript
// types/admin.ts
export interface OrderDashboard {
  summary: {
    total_orders: number
    pending_orders: number
    // ... other fields
  }
}

// In API service
import type { OrderDashboard } from '@/types/admin'

export const adminOrdersApi = {
  getDashboard: async (): Promise<OrderDashboard> => {
    const response = await apiClient.get('/admin-management/orders/dashboard/')
    return response.data
  }
}
```

## 🐛 Error Handling

All API calls should include proper error handling:

```javascript
try {
  const response = await adminOrdersApi.getDashboard()
  // Success
} catch (error) {
  if (error.response) {
    // Server responded with error
    console.error('Error:', error.response.data)
  } else if (error.request) {
    // Request made but no response
    console.error('No response:', error.request)
  } else {
    // Error setting up request
    console.error('Error:', error.message)
  }
}
```

## 📖 Full Documentation

See **FRONTEND_ADMIN_INTEGRATION.md** for:
- Complete Vue component examples
- Component templates
- Styling examples
- Best practices
- TypeScript examples


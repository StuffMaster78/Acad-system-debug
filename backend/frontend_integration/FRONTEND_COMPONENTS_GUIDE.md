# Frontend Components Guide

Complete guide for using the authentication and admin components.

## 📦 Components Overview

### Authentication Components

#### 1. Login.vue
Complete login page with multiple authentication methods.

**Features**:
- ✅ Email/Password login with "Remember Me"
- ✅ Magic link passwordless login
- ✅ 2FA verification
- ✅ Auto-redirect from magic link emails
- ✅ Error handling
- ✅ Loading states

**Usage**:
```vue
<template>
  <Login />
</template>

<script>
import Login from '@/views/auth/Login.vue'
export default {
  components: { Login }
}
</script>
```

**Routes**:
- `/login` - Main login page
- `/login?token=<magic-token>` - Auto-verify magic link

---

#### 2. PasswordChange.vue
Password change page for authenticated users.

**Features**:
- ✅ Current password verification
- ✅ Real-time password strength indicator
- ✅ Password requirements checklist
- ✅ Password match validation
- ✅ Security tips

**Usage**:
```vue
<template>
  <PasswordChange />
</template>

<script>
import PasswordChange from '@/views/auth/PasswordChange.vue'
export default {
  components: { PasswordChange }
}
</script>
```

**Routes**:
- `/account/password-change` - Password change page

**Requirements**:
- User must be authenticated
- Requires current password

---

#### 3. PasswordReset.vue
Password reset flow for forgotten passwords.

**Features**:
- ✅ Request reset link
- ✅ Reset confirmation with token
- ✅ Password strength indicator
- ✅ Success state
- ✅ Token handling from email links

**Usage**:
```vue
<template>
  <PasswordReset />
</template>

<script>
import PasswordReset from '@/views/auth/PasswordReset.vue'
export default {
  components: { PasswordReset }
}
</script>
```

**Routes**:
- `/forgot-password` - Request reset link
- `/forgot-password?token=<reset-token>` - Reset password with token

**Flow**:
1. User enters email
2. System sends reset link (always shows success for security)
3. User clicks link in email
4. User enters new password
5. Password is reset and user can login

---

#### 4. AccountSettings.vue
Account settings page with profile and security management.

**Features**:
- ✅ Profile information management
- ✅ Password change link
- ✅ 2FA setup/disable
- ✅ Active sessions display
- ✅ Logout all devices
- ✅ Session revocation

**Usage**:
```vue
<template>
  <AccountSettings />
</template>

<script>
import AccountSettings from '@/views/account/Settings.vue'
export default {
  components: { AccountSettings }
}
</script>
```

**Routes**:
- `/account/settings` - Account settings page

**Tabs**:
- **Profile**: Update username, full name
- **Security**: Password, 2FA, sessions

---

### Admin Components

#### 5. TipManagement.vue
Complete Tip Management dashboard for admins.

**Features**:
- ✅ Dashboard tab with summary statistics
- ✅ List Tips tab with filtering and pagination
- ✅ Analytics tab with trends and top performers
- ✅ Earnings tab with detailed breakdowns
- ✅ Real-time data loading
- ✅ Error handling

**Usage**:
```vue
<template>
  <TipManagement />
</template>

<script>
import TipManagement from '@/views/admin/TipManagement.vue'
export default {
  components: { TipManagement }
}
</script>
```

**Routes**:
- `/admin/tips` - Tip Management dashboard

**Tabs**:
- **Dashboard**: Overview statistics, recent summary, payment status, breakdowns
- **List Tips**: Filterable list with pagination
- **Analytics**: Trends, top performers, breakdowns
- **Earnings**: Detailed earnings analysis

---

## 🔧 Setup Instructions

### 1. Install Dependencies

```bash
npm install axios vue-router pinia
```

### 2. Create API Client

Create `src/api/client.js`:

```javascript
import axios from 'axios'

const apiClient = axios.create({
  baseURL: process.env.VUE_APP_API_URL || 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        const response = await axios.post(
          `${process.env.VUE_APP_API_URL}/auth/refresh-token/`,
          { refresh_token: refreshToken }
        )

        const { access_token, refresh_token } = response.data
        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', refresh_token)

        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return apiClient(originalRequest)
      } catch (refreshError) {
        // Refresh failed, redirect to login
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient
```

### 3. Create Auth Store (Pinia)

Create `src/stores/auth.js`:

```javascript
import { defineStore } from 'pinia'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: null,
    refreshToken: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    userRole: (state) => state.user?.role
  },

  actions: {
    async setTokens({ accessToken, refreshToken }) {
      this.accessToken = accessToken
      this.refreshToken = refreshToken
      localStorage.setItem('access_token', accessToken)
      localStorage.setItem('refresh_token', refreshToken)
    },

    async setUser(user) {
      this.user = user
      localStorage.setItem('user', JSON.stringify(user))
    },

    async logout() {
      try {
        await authApi.logout()
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.user = null
        this.accessToken = null
        this.refreshToken = null
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
      }
    },

    loadFromStorage() {
      const accessToken = localStorage.getItem('access_token')
      const refreshToken = localStorage.getItem('refresh_token')
      const user = localStorage.getItem('user')

      if (accessToken && refreshToken && user) {
        this.accessToken = accessToken
        this.refreshToken = refreshToken
        this.user = JSON.parse(user)
      }
    }
  }
})
```

### 4. Set Up Router

```javascript
// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/forgot-password',
    name: 'PasswordReset',
    component: () => import('@/views/auth/PasswordReset.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/account/password-change',
    name: 'PasswordChange',
    component: () => import('@/views/auth/PasswordChange.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/account/settings',
    name: 'AccountSettings',
    component: () => import('@/views/account/Settings.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin/tips',
    name: 'TipManagement',
    component: () => import('@/views/admin/TipManagement.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  authStore.loadFromStorage()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.meta.requiresAdmin && authStore.userRole !== 'admin' && authStore.userRole !== 'superadmin') {
    next({ name: 'Dashboard' })
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
```

---

## 🎨 Styling

All components include scoped styles. You can customize them by:

1. **Override CSS variables** (if using CSS variables)
2. **Modify component styles** directly
3. **Use global styles** for consistent theming

### Theme Colors

```css
:root {
  --primary-color: #667eea;
  --secondary-color: #764ba2;
  --success-color: #28a745;
  --danger-color: #dc3545;
  --warning-color: #ffc107;
  --text-color: #333;
  --text-muted: #666;
  --border-color: #e0e0e0;
  --bg-color: #f5f5f5;
}
```

---

## ✅ Testing Checklist

### Authentication Flow
- [ ] Login with email/password
- [ ] Login with "Remember Me" checked
- [ ] Magic link request
- [ ] Magic link verification
- [ ] 2FA setup and verification
- [ ] Password change
- [ ] Password reset flow
- [ ] Logout
- [ ] Session management

### Tip Management
- [ ] Dashboard loads correctly
- [ ] List tips with filters
- [ ] Pagination works
- [ ] Analytics tab loads
- [ ] Earnings tab loads
- [ ] All tabs switch correctly

---

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure backend CORS settings allow your frontend origin
   - Check `CORS_ALLOWED_ORIGINS` in Django settings

2. **Token Expiration**
   - Token refresh interceptor should handle this automatically
   - Check token expiration times in Django settings

3. **Magic Link Not Working**
   - Verify email service is configured
   - Check magic link expiration (default: 15 minutes)
   - Ensure token is passed correctly in URL

4. **2FA Setup Issues**
   - Verify QR code generation
   - Check backup codes are saved
   - Ensure TOTP secret is stored securely

---

## 📚 Additional Resources

- **API Documentation**: `TIP_MANAGEMENT_API_DOCUMENTATION.md`
- **Auth Guide**: `STREAMLINED_AUTH_GUIDE.md`
- **Auth Review**: `AUTH_SYSTEM_REVIEW_AND_IMPROVEMENTS.md`
- **Swagger UI**: `http://localhost:8000/api/v1/docs/swagger/`

---

**Last Updated**: 2024-12-19  
**Status**: ✅ Ready for Integration


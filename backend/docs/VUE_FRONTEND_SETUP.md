# Vue.js Frontend Setup Guide

## Backend API Ready

Your Django backend is fully API-ready with:
- ✅ JWT Authentication
- ✅ Comprehensive REST API
- ✅ Swagger Documentation: `http://localhost:8000/api/v1/docs/swagger/`
- ✅ Public API Root: `http://localhost:8000/api/v1/`

## Vue.js Project Setup

### 1. Initialize Vue Project

```bash
# Using Vue CLI
npm create vue@latest writing-system-frontend

# Or using Vite directly
npm create vite@latest writing-system-frontend -- --template vue

cd writing-system-frontend
npm install
```

### 2. Install Required Dependencies

```bash
# Core dependencies
npm install axios vue-router pinia

# UI components (choose one)
npm install @headlessui/vue @heroicons/vue  # Headless UI
# OR
npm install vuetify  # Material Design
# OR
npm install element-plus  # Element UI
# OR
npm install @vueuse/core  # Composables

# Authentication
npm install @vueuse/auth

# Form handling
npm install vee-validate yup

# HTTP client
npm install axios

# Development tools
npm install -D @types/node
```

### 3. Project Structure

```
writing-system-frontend/
├── src/
│   ├── api/
│   │   ├── client.js          # Axios instance with interceptors
│   │   ├── auth.js            # Authentication endpoints
│   │   ├── orders.js          # Order endpoints
│   │   ├── users.js           # User endpoints
│   │   └── ...
│   ├── stores/
│   │   ├── auth.js            # Auth store (Pinia)
│   │   ├── user.js            # User store
│   │   └── ...
│   ├── views/
│   │   ├── Dashboard.vue
│   │   ├── Login.vue
│   │   ├── Orders/
│   │   ├── Users/
│   │   └── ...
│   ├── components/
│   │   ├── layout/
│   │   ├── common/
│   │   └── ...
│   ├── router/
│   │   └── index.js           # Vue Router config
│   ├── utils/
│   │   ├── auth.js            # Auth utilities
│   │   └── ...
│   ├── App.vue
│   └── main.js
├── .env
├── .env.local
└── package.json
```

### 4. Environment Configuration

Create `.env.local`:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_VERSION=v1
VITE_API_FULL_URL=http://localhost:8000/api/v1
```

### 5. API Client Setup

**src/api/client.js**:
```javascript
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_FULL_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - add auth token
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

// Response interceptor - handle token refresh
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        const response = await axios.post(
          `${import.meta.env.VITE_API_FULL_URL}/auth/refresh-token/`,
          { refresh: refreshToken }
        )
        
        const { access_token } = response.data
        localStorage.setItem('access_token', access_token)
        
        originalRequest.headers.Authorization = `Bearer ${access_token}`
        return apiClient(originalRequest)
      } catch (refreshError) {
        // Refresh failed - logout
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

### 6. Authentication Store (Pinia)

**src/stores/auth.js**:
```javascript
import { defineStore } from 'pinia'
import apiClient from '@/api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
    isAuthenticated: !!localStorage.getItem('access_token'),
  }),

  actions: {
    async login(email, password) {
      try {
        const response = await apiClient.post('/auth/login/', {
          email,
          password,
        })

        const { access_token, refresh_token, user } = response.data
        
        this.accessToken = access_token
        this.refreshToken = refresh_token
        this.user = user
        this.isAuthenticated = true

        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', refresh_token)

        return { success: true }
      } catch (error) {
        return {
          success: false,
          error: error.response?.data?.message || 'Login failed',
        }
      }
    },

    async logout() {
      try {
        await apiClient.post('/auth/logout/')
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.accessToken = null
        this.refreshToken = null
        this.user = null
        this.isAuthenticated = false
        
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      }
    },

    async fetchUser() {
      try {
        const response = await apiClient.get('/users/profile/')
        this.user = response.data
        return response.data
      } catch (error) {
        console.error('Fetch user error:', error)
        throw error
      }
    },
  },
})
```

### 7. Router Setup with Guards

**src/router/index.js**:
```javascript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/',
      name: 'Dashboard',
      component: () => import('@/views/Dashboard.vue'),
      meta: { requiresAuth: true },
    },
    // Add more routes...
  ],
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login' })
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
```

### 8. Dashboard Layout Example

**src/views/Dashboard.vue**:
```vue
<template>
  <div class="dashboard">
    <nav class="sidebar">
      <!-- Navigation menu -->
    </nav>
    
    <main class="content">
      <header class="header">
        <h1>Dashboard</h1>
        <div class="user-info">
          <span>{{ authStore.user?.email }}</span>
          <button @click="handleLogout">Logout</button>
        </div>
      </header>
      
      <div class="dashboard-content">
        <!-- Dashboard widgets and content -->
      </div>
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>
```

## Quick Start Checklist

- [ ] Initialize Vue project
- [ ] Install dependencies
- [ ] Set up API client
- [ ] Configure authentication store
- [ ] Set up router with guards
- [ ] Create login page
- [ ] Create dashboard layout
- [ ] Integrate with backend API
- [ ] Test authentication flow

## API Integration Points

### Authentication
- `POST /api/v1/auth/login/` - Login
- `POST /api/v1/auth/logout/` - Logout
- `POST /api/v1/auth/refresh-token/` - Refresh token

### Key Endpoints
- `GET /api/v1/users/profile/` - Get user profile
- `GET /api/v1/orders/` - List orders
- `GET /api/v1/docs/swagger/` - API documentation

## Next Steps

1. Set up Vue project structure
2. Implement authentication flow
3. Build dashboard layout
4. Integrate with backend APIs
5. Add role-based access control
6. Implement real-time updates (if needed)


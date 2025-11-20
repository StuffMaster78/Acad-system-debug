# Frontend Setup Instructions

Complete step-by-step guide to set up the frontend application with all authentication and admin components.

## Prerequisites

- Node.js 18+ and npm/yarn
- Vue.js 3 project (or create new one)
- Backend API running on `http://localhost:8000`

---

## Step 1: Initialize Vue Project (if starting fresh)

```bash
# Using Vite (recommended)
npm create vite@latest writing-system-frontend -- --template vue
cd writing-system-frontend
npm install

# Or using Vue CLI
npm install -g @vue/cli
vue create writing-system-frontend
cd writing-system-frontend
```

---

## Step 2: Install Dependencies

```bash
# Core dependencies
npm install vue-router@^4.2.5 pinia@^2.1.7 axios@^1.6.2

# Optional: UI library (choose one)
npm install @headlessui/vue @heroicons/vue  # Headless UI
# OR
npm install vuetify  # Material Design
# OR
npm install element-plus  # Element UI
```

---

## Step 3: Copy Files to Your Project

### API Services

```bash
# Copy API client
cp frontend_integration/api-client.js src/api/client.js

# Copy auth API
cp frontend_integration/auth-api.js src/api/auth.js

# Copy admin APIs
cp frontend_integration/admin-tips-api.js src/api/admin/tips.js
cp frontend_integration/admin-orders-api.js src/api/admin/orders.js
# ... copy other admin API files as needed
```

### Stores

```bash
# Copy auth store
cp frontend_integration/auth-store.js src/stores/auth.js
```

### Router

```bash
# Copy router config
cp frontend_integration/router-config.js src/router/index.js
```

### Components

```bash
# Create directories
mkdir -p src/views/auth
mkdir -p src/views/account
mkdir -p src/views/admin

# Copy components
cp frontend_integration/Login.vue src/views/auth/Login.vue
cp frontend_integration/PasswordChange.vue src/views/auth/PasswordChange.vue
cp frontend_integration/PasswordReset.vue src/views/auth/PasswordReset.vue
cp frontend_integration/AccountSettings.vue src/views/account/Settings.vue
cp frontend_integration/TipManagement.vue src/views/admin/TipManagement.vue
```

### Main Entry Point

```bash
# Copy main.js
cp frontend_integration/main.js src/main.js
```

---

## Step 4: Update Import Paths

### Update API Client Import

In all API service files (`src/api/*.js`), ensure the import path is correct:

```javascript
// Should be:
import apiClient from '@/api/client'

// Or if using relative paths:
import apiClient from '../client'
```

### Update Store Import

In components using the auth store:

```javascript
import { useAuthStore } from '@/stores/auth'
```

### Update Router Import

In `src/router/index.js`, update component import paths to match your structure.

---

## Step 5: Configure Environment Variables

```bash
# Copy .env.example
cp frontend_integration/.env.example .env

# Edit .env with your settings
VUE_APP_API_URL=http://localhost:8000/api/v1
VUE_APP_NAME=Writing System
VUE_APP_ENV=development
```

---

## Step 6: Update package.json

```bash
# Copy package.json.example or merge dependencies
# Ensure you have all required dependencies
```

---

## Step 7: Create Missing Components

### Dashboard Component

Create `src/views/Dashboard.vue`:

```vue
<template>
  <div class="dashboard">
    <h1>Dashboard</h1>
    <p>Welcome, {{ authStore.userFullName || authStore.userEmail }}!</p>
    <button @click="handleLogout">Logout</button>
  </div>
</template>

<script>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

export default {
  name: 'Dashboard',
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()

    const handleLogout = async () => {
      await authStore.logout()
    }

    return {
      authStore,
      handleLogout
    }
  }
}
</script>
```

### App.vue

Update `src/App.vue`:

```vue
<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
</style>
```

---

## Step 8: Configure Vite (if using Vite)

Create or update `vite.config.js`:

```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

---

## Step 9: Test the Setup

### 1. Start Development Server

```bash
npm run dev
```

### 2. Test Authentication Flow

1. Navigate to `http://localhost:3000/login`
2. Try logging in with test credentials
3. Verify redirect to dashboard
4. Test "Remember Me" functionality
5. Test logout

### 3. Test Password Management

1. Navigate to `/account/settings`
2. Click "Change Password"
3. Test password change flow
4. Test password reset flow

### 4. Test Admin Features

1. Login as admin
2. Navigate to `/admin/tips`
3. Verify Tip Management dashboard loads
4. Test all tabs (Dashboard, List, Analytics, Earnings)

---

## Step 10: Add Error Handling (Optional)

Create `src/utils/errorHandler.js`:

```javascript
export const handleApiError = (error) => {
  if (error.response) {
    const { status, data } = error.response
    
    switch (status) {
      case 400:
        return data.error || data.detail || 'Bad request'
      case 401:
        return 'Authentication required'
      case 403:
        return 'Permission denied'
      case 404:
        return 'Resource not found'
      case 429:
        return 'Too many requests'
      case 500:
        return 'Server error'
      default:
        return data.error || data.detail || `Error: ${status}`
    }
  } else if (error.request) {
    return 'Network error'
  } else {
    return error.message || 'An error occurred'
  }
}
```

---

## Step 11: Add Loading States (Optional)

Create `src/components/LoadingSpinner.vue`:

```vue
<template>
  <div class="loading-spinner">
    <div class="spinner"></div>
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script>
export default {
  name: 'LoadingSpinner',
  props: {
    message: {
      type: String,
      default: 'Loading...'
    }
  }
}
</script>

<style scoped>
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
```

---

## Troubleshooting

### Issue: CORS Errors

**Solution**: Ensure backend CORS settings allow your frontend origin:

```python
# In Django settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",  # Vite default port
]
```

### Issue: Token Not Persisting

**Solution**: Check localStorage is available and not blocked:

```javascript
// Test in browser console
localStorage.setItem('test', 'value')
console.log(localStorage.getItem('test'))
```

### Issue: Routes Not Working

**Solution**: Ensure router is properly configured in `main.js`:

```javascript
import router from './router'
app.use(router)
```

### Issue: API Calls Failing

**Solution**: 
1. Check API base URL in `.env`
2. Verify backend is running
3. Check network tab in browser dev tools
4. Verify CORS settings

---

## Next Steps

1. ✅ Add more admin components (Orders, Special Orders, etc.)
2. ✅ Add client-facing components
3. ✅ Add notifications/toast system
4. ✅ Add form validation library (vee-validate)
5. ✅ Add UI component library
6. ✅ Add error tracking (Sentry)
7. ✅ Add analytics (Google Analytics)

---

## File Structure

After setup, your project should look like:

```
writing-system-frontend/
├── src/
│   ├── api/
│   │   ├── client.js
│   │   ├── auth.js
│   │   └── admin/
│   │       ├── tips.js
│   │       └── ...
│   ├── stores/
│   │   └── auth.js
│   ├── router/
│   │   └── index.js
│   ├── views/
│   │   ├── auth/
│   │   │   ├── Login.vue
│   │   │   ├── PasswordChange.vue
│   │   │   └── PasswordReset.vue
│   │   ├── account/
│   │   │   └── Settings.vue
│   │   ├── admin/
│   │   │   └── TipManagement.vue
│   │   └── Dashboard.vue
│   ├── components/
│   ├── utils/
│   ├── App.vue
│   └── main.js
├── .env
├── package.json
├── vite.config.js
└── ...
```

---

**Last Updated**: 2024-12-19  
**Status**: ✅ Ready for Development


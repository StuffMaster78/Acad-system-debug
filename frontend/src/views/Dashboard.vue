<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <h1>Dashboard</h1>
      <div class="user-info">
        <span>Welcome, {{ authStore.userFullName || authStore.userEmail }}!</span>
        <button @click="handleLogout" class="btn btn-secondary">Logout</button>
      </div>
    </div>

    <div class="dashboard-content">
      <div class="welcome-card">
        <h2>Welcome to Writing System</h2>
        <p>You are logged in as: <strong>{{ authStore.userRole }}</strong></p>
        
        <div v-if="authStore.isAdmin" class="admin-links">
          <h3>Admin Features</h3>
          <router-link to="/admin/tips" class="admin-link">
            Tip Management
          </router-link>
          <router-link to="/admin/orders" class="admin-link">
            Order Management
          </router-link>
        </div>

        <div class="account-links">
          <router-link to="/account/settings" class="account-link">
            Account Settings
          </router-link>
          <router-link to="/account/password-change" class="account-link">
            Change Password
          </router-link>
        </div>
      </div>
    </div>
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

<style scoped>
.dashboard {
  min-height: 100vh;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
}

.dashboard-header h1 {
  margin: 0;
  font-size: 32px;
  color: #333;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.dashboard-content {
  margin-top: 30px;
}

.welcome-card {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.welcome-card h2 {
  margin: 0 0 15px 0;
  color: #333;
}

.welcome-card p {
  color: #666;
  margin-bottom: 30px;
}

.admin-links,
.account-links {
  margin-top: 30px;
  padding-top: 30px;
  border-top: 1px solid #e0e0e0;
}

.admin-links h3,
.account-links h3 {
  margin-bottom: 15px;
  color: #333;
}

.admin-link,
.account-link {
  display: inline-block;
  padding: 12px 24px;
  margin: 5px 10px 5px 0;
  background: #667eea;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  transition: background 0.3s;
}

.admin-link:hover,
.account-link:hover {
  background: #5568d3;
}
</style>


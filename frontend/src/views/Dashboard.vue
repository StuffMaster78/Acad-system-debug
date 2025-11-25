<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>Dashboard</h1>
      <div class="user-info">
        <span>Welcome, {{ authStore.userFullName || authStore.userEmail }}!</span>
        <button @click="handleLogout" class="btn btn-secondary">Logout</button>
      </div>
    </div>

    <!-- Role-specific dashboard redirects -->
    <div class="dashboard-content">
      <div v-if="authStore.isSuperAdmin" class="welcome-card">
        <router-link to="/superadmin/dashboard" class="dashboard-card card-blue" style="text-decoration: none; display: block;">
          <div class="card-icon">👑</div>
          <div class="card-label">Superadmin Dashboard</div>
          <div class="card-value">View Full Dashboard →</div>
        </router-link>
      </div>
      
      <div v-else-if="authStore.isAdmin" class="welcome-card">
        <router-link to="/admin/dashboard" class="dashboard-card card-blue" style="text-decoration: none; display: block;">
          <div class="card-icon">👨‍💼</div>
          <div class="card-label">Admin Dashboard</div>
          <div class="card-value">View Full Dashboard →</div>
        </router-link>
      </div>
      
      <div v-else-if="authStore.userRole === 'client'" class="welcome-card">
        <router-link to="/client/dashboard" class="dashboard-card card-green" style="text-decoration: none; display: block;">
          <div class="card-icon">👤</div>
          <div class="card-label">Client Dashboard</div>
          <div class="card-value">View Full Dashboard →</div>
        </router-link>
      </div>
      
      <div v-else-if="authStore.userRole === 'writer'" class="welcome-card">
        <router-link to="/writer/dashboard" class="dashboard-card card-purple" style="text-decoration: none; display: block;">
          <div class="card-icon">✍️</div>
          <div class="card-label">Writer Dashboard</div>
          <div class="card-value">View Full Dashboard →</div>
        </router-link>
      </div>
      
      <div v-else-if="authStore.userRole === 'editor'" class="welcome-card">
        <router-link to="/editor/dashboard" class="dashboard-card card-orange" style="text-decoration: none; display: block;">
          <div class="card-icon">📝</div>
          <div class="card-label">Editor Dashboard</div>
          <div class="card-value">View Full Dashboard →</div>
        </router-link>
      </div>
      
      <div v-else-if="authStore.userRole === 'support'" class="welcome-card">
        <router-link to="/support/dashboard" class="dashboard-card card-teal" style="text-decoration: none; display: block;">
          <div class="card-icon">🎧</div>
          <div class="card-label">Support Dashboard</div>
          <div class="card-value">View Full Dashboard →</div>
        </router-link>
      </div>
      
      <div v-else class="welcome-card">
        <h2>Welcome to Writing System</h2>
        <p>You are logged in as: <strong>{{ authStore.userRole }}</strong></p>
        
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
/* Uses shared dashboard-container from dashboard.css */

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
  flex-wrap: wrap;
  gap: 15px;
}

.dashboard-header h1 {
  margin: 0;
  font-size: clamp(24px, 5vw, 32px);
  color: #333;
  line-height: 1.2;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.user-info span {
  font-size: clamp(14px, 3vw, 16px);
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
  font-size: clamp(20px, 4vw, 24px);
  line-height: 1.3;
}

.welcome-card p {
  color: #666;
  margin-bottom: 30px;
  font-size: clamp(14px, 3vw, 16px);
  line-height: 1.5;
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
  font-size: clamp(18px, 3.5vw, 20px);
}

.admin-link,
.account-link {
  display: inline-block;
  padding: 12px 24px;
  margin: 5px 10px 5px 0;
  background: #667eea;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-size: 15px;
  min-height: 44px; /* Touch-friendly */
  line-height: 1.5;
  touch-action: manipulation;
}

.admin-link:hover,
.account-link:hover,
.admin-link:active,
.account-link:active {
  background: #5568d3;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .dashboard {
    padding: 16px;
  }

  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    margin-bottom: 20px;
    padding-bottom: 15px;
  }

  .dashboard-header h1 {
    width: 100%;
  }

  .user-info {
    width: 100%;
    justify-content: space-between;
  }

  .welcome-card {
    padding: 24px 20px;
    border-radius: 16px;
  }

  .admin-links,
  .account-links {
    margin-top: 24px;
    padding-top: 24px;
  }

  .admin-link,
  .account-link {
    display: block;
    width: 100%;
    margin: 8px 0;
    text-align: center;
    padding: 14px 20px;
  }
}

@media (max-width: 480px) {
  .dashboard {
    padding: 12px;
  }

  .dashboard-header {
    margin-bottom: 16px;
    padding-bottom: 12px;
  }

  .dashboard-content {
    margin-top: 20px;
  }

  .welcome-card {
    padding: 20px 16px;
  }

  .admin-links,
  .account-links {
    margin-top: 20px;
    padding-top: 20px;
  }

  .admin-link,
  .account-link {
    padding: 12px 16px;
    font-size: 14px;
  }
}

/* Tablet optimizations */
@media (min-width: 769px) and (max-width: 1024px) {
  .dashboard {
    padding: 24px;
  }

  .welcome-card {
    padding: 32px;
  }
}

/* Large screen optimizations */
@media (min-width: 1400px) {
  .dashboard {
    max-width: 1400px;
  }

  .welcome-card {
    padding: 48px;
  }
}
</style>


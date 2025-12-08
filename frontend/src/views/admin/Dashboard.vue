<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
        <p class="mt-2 text-gray-600">Overview of platform statistics and management</p>
      </div>
      <button 
        @click="refreshDashboard" 
        :disabled="loading" 
        class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 shadow-sm hover:shadow-md"
      >
        <svg 
          class="w-5 h-5" 
          :class="{ 'animate-spin': loading }"
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        <span v-if="loading">Loading...</span>
        <span v-else>Refresh</span>
      </button>
    </div>

    <div v-if="loading" class="dashboard-loading">Loading dashboard data...</div>
    <div v-else-if="error" class="dashboard-error">{{ error }}</div>
    <div v-else>
      <!-- Primary Summary Cards -->
      <div class="stats-grid">
        <div class="dashboard-card card-blue">
          <div class="card-header">
            <div class="card-icon">👥</div>
            <div class="card-label">Total Users</div>
          </div>
          <div class="card-value">{{ formatNumber(dashboardData.total_users || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">All roles</span>
          </div>
        </div>
        
        <div class="dashboard-card card-green">
          <div class="card-header">
            <div class="card-icon">📦</div>
            <div class="card-label">Total Orders</div>
          </div>
          <div class="card-value">{{ formatNumber(dashboardData.total_orders || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">All time</span>
          </div>
        </div>
        
        <div class="dashboard-card card-purple">
          <div class="card-header">
            <div class="card-icon">💰</div>
            <div class="card-label">Total Revenue</div>
          </div>
          <div class="card-value money-value">${{ formatCurrency(dashboardData.total_revenue || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">All time</span>
          </div>
        </div>
        
        <div class="dashboard-card card-orange">
          <div class="card-header">
            <div class="card-icon">✅</div>
            <div class="card-label">Completed</div>
          </div>
          <div class="card-value">{{ formatNumber(dashboardData.completed_orders || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge" v-if="dashboardData.total_orders">
              {{ Math.round((dashboardData.completed_orders / dashboardData.total_orders) * 100) }}% completion rate
            </span>
          </div>
        </div>
        
        <div class="dashboard-card card-red">
          <div class="card-header">
            <div class="card-icon">⏳</div>
            <div class="card-label">Pending Orders</div>
          </div>
          <div class="card-value">{{ formatNumber(dashboardData.pending_orders || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">Requires attention</span>
          </div>
        </div>
        
        <div class="dashboard-card card-indigo">
          <div class="card-header">
            <div class="card-icon">🎫</div>
            <div class="card-label">Open Tickets</div>
          </div>
          <div class="card-value">{{ formatNumber(dashboardData.open_tickets || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">Active support</span>
          </div>
        </div>
      </div>

      <!-- User Statistics Section -->
      <div class="dashboard-section">
        <h2>User Breakdown</h2>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-label">👨‍💼 Writers</div>
            <div class="stat-value">{{ formatNumber(dashboardData.total_writers || 0) }}</div>
            <div class="stat-description">Active writers</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">👤 Clients</div>
            <div class="stat-value">{{ formatNumber(dashboardData.total_clients || 0) }}</div>
            <div class="stat-description">Registered clients</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">✏️ Editors</div>
            <div class="stat-value">{{ formatNumber(dashboardData.total_editors || 0) }}</div>
            <div class="stat-description">Active editors</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">🎧 Support</div>
            <div class="stat-value">{{ formatNumber(dashboardData.total_support || 0) }}</div>
            <div class="stat-description">Support staff</div>
          </div>
        </div>
      </div>

      <!-- Quick Actions Section -->
      <div class="dashboard-section">
        <h2>Configuration & Management</h2>
        <div class="quick-actions-grid">
          <button type="button" class="quick-action-card quick-action-card--button" @click="goToNotificationProfiles">
            <div class="quick-action-icon">🔔</div>
            <div class="quick-action-title">Notification Profiles</div>
            <div class="quick-action-description">Manage notification preferences and profiles</div>
          </button>
          <router-link to="/admin/tips" class="quick-action-card">
            <div class="quick-action-icon">💰</div>
            <div class="quick-action-title">Tip Management</div>
            <div class="quick-action-description">View and manage tips</div>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'AdminDashboard',
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      loading: false,
      error: null,
      dashboardData: {}
    }
  },
  mounted() {
    this.loadDashboard()
  },
  methods: {
    async loadDashboard() {
      this.loading = true
      this.error = null
      try {
        const response = await axios.get('/api/v1/admin-management/dashboard/', {
          headers: {
            'Authorization': `Bearer ${this.authStore.accessToken}`
          }
        })
        this.dashboardData = response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to load dashboard'
        console.error('Dashboard error:', err)
      } finally {
        this.loading = false
      }
    },
    refreshDashboard() {
      this.loadDashboard()
    },
    formatCurrency(value) {
      const num = parseFloat(value || 0)
      return num.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })
    },
    formatNumber(value) {
      return parseInt(value || 0).toLocaleString()
    },
    goToNotificationProfiles() {
      this.$router.push('/admin/notification-profiles')
    }
  }
}
</script>

<style scoped>
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.dashboard-header h1 {
  font-size: clamp(24px, 4vw, 32px);
  font-weight: 700;
  color: var(--gray-900);
  margin: 0;
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.quick-action-card {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 24px;
  text-decoration: none;
  color: inherit;
  transition: all 0.2s;
  cursor: pointer;
  display: block;
}

.quick-action-card--button {
  width: 100%;
  text-align: left;
  border: 2px solid #e5e7eb;
}

.quick-action-card--button:focus-visible {
  outline: 3px solid #3b82f6;
  outline-offset: 2px;
}

.quick-action-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
  transform: translateY(-2px);
}

.quick-action-icon {
  font-size: 32px;
  margin-bottom: 12px;
}

.quick-action-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--gray-900);
  margin-bottom: 8px;
}

.quick-action-description {
  font-size: 14px;
  color: var(--gray-600);
  line-height: 1.5;
}

.dashboard-section {
  margin-top: 40px;
}

.dashboard-section h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--gray-900);
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .quick-actions-grid {
    grid-template-columns: 1fr;
  }
}
</style>


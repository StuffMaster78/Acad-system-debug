<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>Superadmin Dashboard</h1>
      <button @click="refreshDashboard" :disabled="loading" class="btn btn-primary">
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
            <div class="card-icon">💰</div>
            <div class="card-label">Total Revenue</div>
          </div>
          <div class="card-value money-value">${{ formatCurrency(dashboardData.total_revenue || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">All time</span>
          </div>
        </div>
        
        <div class="dashboard-card card-purple">
          <div class="card-header">
            <div class="card-icon">📦</div>
            <div class="card-label">Total Orders</div>
          </div>
          <div class="card-value">{{ formatNumber(dashboardData.total_orders || 0) }}</div>
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
              {{ Math.round((dashboardData.completed_orders / dashboardData.total_orders) * 100) }}% completion
            </span>
          </div>
        </div>
        
        <div class="dashboard-card card-red">
          <div class="card-header">
            <div class="card-icon">⏳</div>
            <div class="card-label">Pending Payouts</div>
          </div>
          <div class="card-value money-value">${{ formatCurrency(dashboardData.pending_payouts || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">Awaiting payment</span>
          </div>
        </div>
        
        <div class="dashboard-card card-indigo">
          <div class="card-header">
            <div class="card-icon">💸</div>
            <div class="card-label">Total Refunds</div>
          </div>
          <div class="card-value money-value">${{ formatCurrency(dashboardData.total_refunds || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">All time</span>
          </div>
        </div>
      </div>

      <!-- User Statistics -->
      <div class="dashboard-section">
        <h2>User Breakdown</h2>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-label">👑 Admins</div>
            <div class="stat-value">{{ formatNumber(dashboardData.total_admins || 0) }}</div>
            <div class="stat-description">Administrators</div>
          </div>
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
          <div class="stat-item">
            <div class="stat-label">🚫 Suspended</div>
            <div class="stat-value">{{ formatNumber(dashboardData.suspended_users || 0) }}</div>
            <div class="stat-description">Suspended accounts</div>
          </div>
        </div>
      </div>

      <!-- Order Statistics -->
      <div class="dashboard-section">
        <h2>Order Status Breakdown</h2>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-label">🔄 In Progress</div>
            <div class="stat-value">{{ formatNumber(dashboardData.in_progress || 0) }}</div>
            <div class="stat-description">Active orders</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">⚖️ Disputed</div>
            <div class="stat-value">{{ formatNumber(dashboardData.disputed || 0) }}</div>
            <div class="stat-description">Requires resolution</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">❌ Canceled</div>
            <div class="stat-value">{{ formatNumber(dashboardData.canceled || 0) }}</div>
            <div class="stat-description">Canceled orders</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">⚠️ Total Disputes</div>
            <div class="stat-value">{{ formatNumber(dashboardData.total_disputes || 0) }}</div>
            <div class="stat-description">All disputes</div>
          </div>
        </div>
      </div>

      <!-- Financial Statistics -->
      <div class="dashboard-section" v-if="dashboardData.financial_stats">
        <h2>Financial Statistics</h2>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-label">Completed Payments</div>
            <div class="stat-value money-value">${{ formatCurrency(dashboardData.financial_stats.completed_payments || 0) }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">Failed Payments</div>
            <div class="stat-value">{{ formatNumber(dashboardData.financial_stats.failed_payments || 0) }}</div>
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
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'SuperadminDashboard',
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
        const response = await axios.get('/api/v1/superadmin-management/dashboard/', {
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


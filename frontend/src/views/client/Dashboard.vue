<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>Client Dashboard</h1>
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
            <div class="card-icon">📦</div>
            <div class="card-label">Total Orders</div>
          </div>
          <div class="card-value">{{ formatNumber(dashboardData.total_orders || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">All time</span>
          </div>
        </div>
        
        <div class="dashboard-card card-green">
          <div class="card-header">
            <div class="card-icon">💰</div>
            <div class="card-label">Total Spent</div>
          </div>
          <div class="card-value money-value">${{ formatCurrency(dashboardData.all_time_spend || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">All time</span>
          </div>
        </div>
        
        <div class="dashboard-card card-purple">
          <div class="card-header">
            <div class="card-icon">📊</div>
            <div class="card-label">This Month</div>
          </div>
          <div class="card-value">{{ formatNumber(dashboardData.month_orders || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">Orders this month</span>
          </div>
        </div>
        
        <div class="dashboard-card card-orange">
          <div class="card-header">
            <div class="card-icon">💵</div>
            <div class="card-label">Month Spending</div>
          </div>
          <div class="card-value money-value">${{ formatCurrency(dashboardData.month_spend || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">Current month</span>
          </div>
        </div>
        
        <div class="dashboard-card card-indigo">
          <div class="card-header">
            <div class="card-icon">📈</div>
            <div class="card-label">Avg Order Value</div>
          </div>
          <div class="card-value money-value">${{ formatCurrency(dashboardData.avg_order_value || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">Per order</span>
          </div>
        </div>
        
        <div class="dashboard-card card-teal">
          <div class="card-header">
            <div class="card-icon">✅</div>
            <div class="card-label">Completed</div>
          </div>
          <div class="card-value">{{ formatNumber(dashboardData.status_breakdown?.completed || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge" v-if="dashboardData.total_orders">
              {{ Math.round((dashboardData.status_breakdown?.completed / dashboardData.total_orders) * 100) }}% completion
            </span>
          </div>
        </div>
      </div>

      <!-- Order Status Breakdown -->
      <div class="dashboard-section">
        <h2>Order Status Breakdown</h2>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-label">⏳ Pending</div>
            <div class="stat-value">{{ formatNumber(dashboardData.status_breakdown?.pending || 0) }}</div>
            <div class="stat-description">Awaiting assignment</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">🔄 In Progress</div>
            <div class="stat-value">{{ formatNumber(dashboardData.status_breakdown?.in_progress || 0) }}</div>
            <div class="stat-description">Being worked on</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">✏️ On Revision</div>
            <div class="stat-value">{{ formatNumber(dashboardData.status_breakdown?.on_revision || 0) }}</div>
            <div class="stat-description">Under revision</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">✅ Completed</div>
            <div class="stat-value">{{ formatNumber(dashboardData.status_breakdown?.completed || 0) }}</div>
            <div class="stat-description">Finished orders</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'ClientDashboard',
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
        const response = await axios.get('/api/v1/client-management/dashboard/stats/', {
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

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
}
</style>


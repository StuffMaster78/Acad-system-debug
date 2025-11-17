<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>Writer Dashboard</h1>
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
        <div class="dashboard-card card-green">
          <div class="card-header">
            <div class="card-icon">💰</div>
            <div class="card-label">Total Earnings</div>
          </div>
          <div class="card-value money-value">${{ formatCurrency(earningsData.total_earnings || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">Last 30 days</span>
          </div>
        </div>
        
        <div class="dashboard-card card-blue">
          <div class="card-header">
            <div class="card-icon">📦</div>
            <div class="card-label">Active Orders</div>
          </div>
          <div class="card-value">{{ formatNumber(performanceData.total_orders || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">Currently assigned</span>
          </div>
        </div>
        
        <div class="dashboard-card card-purple">
          <div class="card-header">
            <div class="card-icon">✅</div>
            <div class="card-label">Completed</div>
          </div>
          <div class="card-value">{{ formatNumber(performanceData.completed_orders || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">All time</span>
          </div>
        </div>
        
        <div class="dashboard-card card-orange">
          <div class="card-header">
            <div class="card-icon">⭐</div>
            <div class="card-label">Avg Rating</div>
          </div>
          <div class="card-value">{{ formatNumber(performanceData.avg_rating || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">Out of 5.0</span>
          </div>
        </div>
        
        <div class="dashboard-card card-indigo">
          <div class="card-header">
            <div class="card-icon">📊</div>
            <div class="card-label">Completion Rate</div>
          </div>
          <div class="card-value">{{ formatNumber(performanceData.completion_rate || 0) }}%</div>
          <div class="card-footer">
            <span class="card-badge">Success rate</span>
          </div>
        </div>
        
        <div class="dashboard-card card-teal">
          <div class="card-header">
            <div class="card-icon">⏰</div>
            <div class="card-label">On-Time Rate</div>
          </div>
          <div class="card-value">{{ formatNumber(performanceData.on_time_rate || 0) }}%</div>
          <div class="card-footer">
            <span class="card-badge">Timely delivery</span>
          </div>
        </div>
      </div>

      <!-- Earnings Breakdown -->
      <div class="dashboard-section">
        <h2>Earnings Breakdown</h2>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-label">📅 This Week</div>
            <div class="stat-value money-value">${{ formatCurrency(earningsData.week_earnings || 0) }}</div>
            <div class="stat-description">Last 7 days</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">📆 This Month</div>
            <div class="stat-value money-value">${{ formatCurrency(earningsData.month_earnings || 0) }}</div>
            <div class="stat-description">Current month</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">📊 This Year</div>
            <div class="stat-value money-value">${{ formatCurrency(earningsData.year_earnings || 0) }}</div>
            <div class="stat-description">Year to date</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">📈 Avg per Order</div>
            <div class="stat-value money-value">${{ formatCurrency(earningsData.avg_earnings_per_order || 0) }}</div>
            <div class="stat-description">Average earnings</div>
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
  name: 'WriterDashboard',
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      loading: false,
      error: null,
      earningsData: {},
      performanceData: {}
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
        const [earningsRes, performanceRes] = await Promise.all([
          axios.get('/api/v1/writer-management/dashboard/earnings/', {
            headers: { 'Authorization': `Bearer ${this.authStore.accessToken}` }
          }),
          axios.get('/api/v1/writer-management/dashboard/performance/', {
            headers: { 'Authorization': `Bearer ${this.authStore.accessToken}` }
          })
        ])
        this.earningsData = earningsRes.data
        this.performanceData = performanceRes.data
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
      return parseFloat(value || 0).toFixed(1)
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


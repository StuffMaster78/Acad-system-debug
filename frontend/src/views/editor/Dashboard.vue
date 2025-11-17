<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>Editor Dashboard</h1>
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
            <div class="card-icon">📝</div>
            <div class="card-label">Total Reviews</div>
          </div>
          <div class="card-value">{{ formatNumber(dashboardData.performance?.total_orders_reviewed || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">All time</span>
          </div>
        </div>
        
        <div class="dashboard-card card-green">
          <div class="card-header">
            <div class="card-icon">⏱️</div>
            <div class="card-label">Avg Review Time</div>
          </div>
          <div class="card-value">{{ formatNumber(dashboardData.performance?.average_review_time_hours || 0) }}h</div>
          <div class="card-footer">
            <span class="card-badge">Per review</span>
          </div>
        </div>
        
        <div class="dashboard-card card-purple">
          <div class="card-header">
            <div class="card-icon">⭐</div>
            <div class="card-label">Quality Score</div>
          </div>
          <div class="card-value">{{ formatNumber(dashboardData.performance?.average_quality_score || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">Out of 5.0</span>
          </div>
        </div>
        
        <div class="dashboard-card card-orange">
          <div class="card-header">
            <div class="card-icon">✅</div>
            <div class="card-label">Approvals</div>
          </div>
          <div class="card-value">{{ formatNumber(dashboardData.performance?.approvals_count || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">Approved orders</span>
          </div>
        </div>
        
        <div class="dashboard-card card-red">
          <div class="card-header">
            <div class="card-icon">🔄</div>
            <div class="card-label">Revisions</div>
          </div>
          <div class="card-value">{{ formatNumber(dashboardData.performance?.revisions_requested_count || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">Requested</span>
          </div>
        </div>
        
        <div class="dashboard-card card-indigo">
          <div class="card-header">
            <div class="card-icon">⏰</div>
            <div class="card-label">Late Reviews</div>
          </div>
          <div class="card-value">{{ formatNumber(dashboardData.performance?.late_reviews || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">Past deadline</span>
          </div>
        </div>
      </div>

      <!-- Task Statistics -->
      <div class="dashboard-section" v-if="dashboardData.stats">
        <h2>Task Statistics</h2>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-label">🔄 Active Tasks</div>
            <div class="stat-value">{{ formatNumber(dashboardData.stats.active_tasks || 0) }}</div>
            <div class="stat-description">Currently assigned</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">✅ Completed Tasks</div>
            <div class="stat-value">{{ formatNumber(dashboardData.stats.completed_tasks || 0) }}</div>
            <div class="stat-description">Finished reviews</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">⏳ Pending Tasks</div>
            <div class="stat-value">{{ formatNumber(dashboardData.stats.pending_tasks || 0) }}</div>
            <div class="stat-description">Awaiting review</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">📊 Total Tasks</div>
            <div class="stat-value">{{ formatNumber(dashboardData.stats.total_tasks || 0) }}</div>
            <div class="stat-description">All tasks</div>
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
  name: 'EditorDashboard',
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
        const response = await axios.get('/api/v1/editor-management/profiles/dashboard_stats/', {
          headers: {
            'Authorization': `Bearer ${this.authStore.accessToken}`
          },
          params: {
            days: 30
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


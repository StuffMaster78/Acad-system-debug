<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>Support Dashboard</h1>
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
            <div class="card-icon">🎫</div>
            <div class="card-label">Open Tickets</div>
          </div>
          <div class="card-value">{{ formatNumber(ticketsData.total_open || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">Total open</span>
          </div>
        </div>
        
        <div class="dashboard-card card-green">
          <div class="card-header">
            <div class="card-icon">✅</div>
            <div class="card-label">Assigned to Me</div>
          </div>
          <div class="card-value">{{ formatNumber(ticketsData.total_assigned_to_me || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">My tickets</span>
          </div>
        </div>
        
        <div class="dashboard-card card-purple">
          <div class="card-header">
            <div class="card-icon">📋</div>
            <div class="card-label">Recent Tickets</div>
          </div>
          <div class="card-value">{{ formatNumber(ticketsData.count || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">Last 20 tickets</span>
          </div>
        </div>
        
        <div class="dashboard-card card-orange">
          <div class="card-header">
            <div class="card-icon">🔴</div>
            <div class="card-label">High Priority</div>
          </div>
          <div class="card-value">{{ formatNumber(queueData.high_priority?.length || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">Urgent</span>
          </div>
        </div>
        
        <div class="dashboard-card card-red">
          <div class="card-header">
            <div class="card-icon">⏰</div>
            <div class="card-label">Overdue</div>
          </div>
          <div class="card-value">{{ formatNumber(queueData.overdue?.length || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">Past deadline</span>
          </div>
        </div>
        
        <div class="dashboard-card card-indigo">
          <div class="card-header">
            <div class="card-icon">📬</div>
            <div class="card-label">Unassigned</div>
          </div>
          <div class="card-value">{{ formatNumber(queueData.unassigned?.length || 0) }}</div>
          <div class="card-footer">
            <span class="card-badge">Needs assignment</span>
          </div>
        </div>
      </div>

      <!-- Queue Breakdown -->
      <div class="dashboard-section">
        <h2>Ticket Queue Breakdown</h2>
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-label">📬 Unassigned</div>
            <div class="stat-value">{{ formatNumber(queueData.unassigned?.length || 0) }}</div>
            <div class="stat-description">Needs assignment</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">✅ My Assigned</div>
            <div class="stat-value">{{ formatNumber(queueData.my_assigned?.length || 0) }}</div>
            <div class="stat-description">Assigned to me</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">🔴 High Priority</div>
            <div class="stat-value">{{ formatNumber(queueData.high_priority?.length || 0) }}</div>
            <div class="stat-description">Urgent tickets</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">⏰ Overdue</div>
            <div class="stat-value">{{ formatNumber(queueData.overdue?.length || 0) }}</div>
            <div class="stat-description">Past deadline</div>
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
  name: 'SupportDashboard',
  setup() {
    const authStore = useAuthStore()
    return { authStore }
  },
  data() {
    return {
      loading: false,
      error: null,
      ticketsData: {},
      queueData: {}
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
        const [ticketsRes, queueRes] = await Promise.all([
          axios.get('/api/v1/support-management/dashboard/tickets/', {
            headers: { 'Authorization': `Bearer ${this.authStore.accessToken}` },
            params: { limit: 20 }
          }),
          axios.get('/api/v1/support-management/dashboard/queue/', {
            headers: { 'Authorization': `Bearer ${this.authStore.accessToken}` }
          })
        ])
        this.ticketsData = ticketsRes.data
        this.queueData = queueRes.data
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


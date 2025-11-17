<template>
  <div class="tip-management">
    <!-- Header -->
    <div class="header">
      <h1>Tip Management</h1>
      <div class="header-actions">
        <button @click="refreshDashboard" :disabled="loading" class="btn btn-primary">
          <span v-if="loading">Loading...</span>
          <span v-else>Refresh</span>
        </button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="['tab', { active: activeTab === tab.id }]"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Dashboard Tab -->
    <div v-if="activeTab === 'dashboard'" class="tab-content">
      <div v-if="loading" class="loading">Loading dashboard...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else class="dashboard-container">
        <!-- Summary Cards -->
        <div class="stats-grid">
          <div class="dashboard-card card-blue">
            <div class="card-icon">💰</div>
            <div class="card-label">Total Tips</div>
            <div class="card-value">{{ formatNumber(dashboardData.summary?.total_tips || 0) }}</div>
          </div>
          <div class="dashboard-card card-green">
            <div class="card-icon">💵</div>
            <div class="card-label">Total Tip Amount</div>
            <div class="card-value money-value">${{ formatCurrency(dashboardData.summary?.total_tip_amount || 0) }}</div>
          </div>
          <div class="dashboard-card card-purple">
            <div class="card-icon">✍️</div>
            <div class="card-label">Writer Earnings</div>
            <div class="card-value money-value">${{ formatCurrency(dashboardData.summary?.total_writer_earnings || 0) }}</div>
          </div>
          <div class="dashboard-card card-orange">
            <div class="card-icon">🏢</div>
            <div class="card-label">Platform Profit</div>
            <div class="card-value money-value">${{ formatCurrency(dashboardData.summary?.total_platform_profit || 0) }}</div>
          </div>
        </div>

        <!-- Recent Summary -->
        <div class="dashboard-section">
          <h2>Recent Summary (Last {{ dashboardData.recent_summary?.days || 30 }} Days)</h2>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-label">Total Tips</div>
              <div class="stat-value">{{ formatNumber(dashboardData.recent_summary?.total_tips || 0) }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">Total Amount</div>
              <div class="stat-value money-value">${{ formatCurrency(dashboardData.recent_summary?.total_tip_amount || 0) }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">Writer Earnings</div>
              <div class="stat-value money-value">${{ formatCurrency(dashboardData.recent_summary?.total_writer_earnings || 0) }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">Platform Profit</div>
              <div class="stat-value money-value">${{ formatCurrency(dashboardData.recent_summary?.total_platform_profit || 0) }}</div>
            </div>
          </div>
        </div>

        <!-- Payment Status -->
        <div class="dashboard-section">
          <h2>Payment Status</h2>
          <div class="payment-status">
            <div class="status-item">
              <span class="status-badge completed">Completed</span>
              <span>{{ dashboardData.payment_status?.completed || 0 }}</span>
            </div>
            <div class="status-item">
              <span class="status-badge pending">Pending</span>
              <span>{{ dashboardData.payment_status?.pending || 0 }}</span>
            </div>
            <div class="status-item">
              <span class="status-badge processing">Processing</span>
              <span>{{ dashboardData.payment_status?.processing || 0 }}</span>
            </div>
            <div class="status-item">
              <span class="status-badge failed">Failed</span>
              <span>{{ dashboardData.payment_status?.failed || 0 }}</span>
            </div>
          </div>
        </div>

        <!-- Type Breakdown -->
        <div class="dashboard-section">
          <h2>Breakdown by Type</h2>
          <div class="breakdown">
            <div
              v-for="item in dashboardData.type_breakdown"
              :key="item.tip_type"
              class="breakdown-item"
            >
              <h4>{{ item.tip_type }}</h4>
              <p>Count: {{ item.count }}</p>
              <p>Total: ${{ formatCurrency(item.total_amount) }}</p>
              <p>Writer Earnings: ${{ formatCurrency(item.writer_earnings) }}</p>
              <p>Platform Profit: ${{ formatCurrency(item.platform_profit) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- List Tips Tab -->
    <div v-if="activeTab === 'list'" class="tab-content">
      <div class="filters">
        <select v-model="filters.tip_type" @change="loadTips">
          <option value="">All Types</option>
          <option value="direct">Direct</option>
          <option value="order">Order</option>
          <option value="class">Class</option>
        </select>
        <select v-model="filters.payment_status" @change="loadTips">
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="processing">Processing</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
        </select>
        <input
          v-model="filters.date_from"
          type="date"
          placeholder="From Date"
          @change="loadTips"
        />
        <input
          v-model="filters.date_to"
          type="date"
          placeholder="To Date"
          @change="loadTips"
        />
        <button @click="clearFilters" class="btn btn-secondary">Clear Filters</button>
      </div>

      <div v-if="loading" class="loading">Loading tips...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else>
        <div class="tips-summary">
          <p>Total: {{ formatNumber(tipsData.count || 0) }} tips</p>
          <p>Total Amount: ${{ formatCurrency(tipsData.summary?.total_tip_amount || 0) }}</p>
        </div>
        <table class="tips-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Client</th>
              <th>Writer</th>
              <th>Type</th>
              <th>Amount</th>
              <th>Writer Earning</th>
              <th>Platform Profit</th>
              <th>Status</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="tip in tipsData.results" :key="tip.id">
              <td>{{ tip.id }}</td>
              <td>{{ tip.client?.username || tip.client?.email }}</td>
              <td>{{ tip.writer?.username || tip.writer?.email }}</td>
              <td>{{ tip.tip_type }}</td>
              <td>${{ formatCurrency(tip.tip_amount) }}</td>
              <td>${{ formatCurrency(tip.writer_earning) }}</td>
              <td>${{ formatCurrency(tip.platform_profit) }}</td>
              <td>
                <span :class="['status-badge', tip.payment_status]">
                  {{ tip.payment_status }}
                </span>
              </td>
              <td>{{ formatDate(tip.sent_at) }}</td>
            </tr>
          </tbody>
        </table>
        <div class="pagination">
          <button
            @click="previousPage"
            :disabled="pagination.offset === 0"
            class="btn btn-secondary"
          >
            Previous
          </button>
          <span>Page {{ currentPage }} of {{ totalPages }}</span>
          <button
            @click="nextPage"
            :disabled="pagination.offset + pagination.limit >= tipsData.count"
            class="btn btn-secondary"
          >
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Analytics Tab -->
    <div v-if="activeTab === 'analytics'" class="tab-content">
      <div class="analytics-controls">
        <label>
          Days:
          <input
            v-model.number="analyticsDays"
            type="number"
            min="1"
            max="365"
            @change="loadAnalytics"
          />
        </label>
        <button @click="loadAnalytics" class="btn btn-primary">Update</button>
      </div>
      <div v-if="loading" class="loading">Loading analytics...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else class="analytics">
        <div class="section">
          <h2>Monthly Trends</h2>
          <div class="trends">
            <div
              v-for="trend in analyticsData.trends?.monthly"
              :key="trend.month"
              class="trend-item"
            >
              <h4>{{ formatDate(trend.month) }}</h4>
              <p>Count: {{ trend.count }}</p>
              <p>Total: ${{ formatCurrency(trend.total_amount) }}</p>
            </div>
          </div>
        </div>
        <div class="section">
          <h2>Top Writers</h2>
          <div class="top-performers">
            <div
              v-for="writer in analyticsData.top_performers?.writers"
              :key="writer.writer__id"
              class="performer-item"
            >
              <h4>{{ writer.writer__username }}</h4>
              <p>Tips: {{ writer.tip_count }}</p>
              <p>Total Received: ${{ formatCurrency(writer.total_received) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Earnings Tab -->
    <div v-if="activeTab === 'earnings'" class="tab-content">
      <div class="earnings-controls">
        <label>
          From Date:
          <input
            v-model="earningsFilters.date_from"
            type="date"
            @change="loadEarnings"
          />
        </label>
        <label>
          To Date:
          <input
            v-model="earningsFilters.date_to"
            type="date"
            @change="loadEarnings"
          />
        </label>
        <button @click="loadEarnings" class="btn btn-primary">Update</button>
      </div>
      <div v-if="loading" class="loading">Loading earnings...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else class="earnings">
        <div class="section">
          <h2>Overall Earnings</h2>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-label">Total Tips</div>
              <div class="stat-value">{{ formatNumber(earningsData.overall?.total_tips || 0) }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">Total Amount</div>
              <div class="stat-value money-value">${{ formatCurrency(earningsData.overall?.total_tip_amount || 0) }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">Writer Earnings</div>
              <div class="stat-value money-value">${{ formatCurrency(earningsData.overall?.total_writer_earnings || 0) }}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">Platform Profit</div>
              <div class="stat-value money-value">${{ formatCurrency(earningsData.overall?.total_platform_profit || 0) }}</div>
            </div>
          </div>
        </div>
        <div class="section">
          <h2>Earnings by Level</h2>
          <div class="breakdown">
            <div
              v-for="item in earningsData.by_level"
              :key="item.writer_level__name"
              class="breakdown-item"
            >
              <h4>{{ item.writer_level__name }}</h4>
              <p>Tips: {{ item.tip_count }}</p>
              <p>Total: ${{ formatCurrency(item.total_tips) }}</p>
              <p>Writer Earnings: ${{ formatCurrency(item.writer_earnings) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { adminTipsApi } from '@/api/admin/tips' // Adjust import path

export default {
  name: 'TipManagement',
  data() {
    return {
      activeTab: 'dashboard',
      tabs: [
        { id: 'dashboard', label: 'Dashboard' },
        { id: 'list', label: 'List Tips' },
        { id: 'analytics', label: 'Analytics' },
        { id: 'earnings', label: 'Earnings' }
      ],
      loading: false,
      error: null,
      dashboardData: {},
      tipsData: {},
      analyticsData: {},
      earningsData: {},
      filters: {
        tip_type: '',
        payment_status: '',
        date_from: '',
        date_to: ''
      },
      earningsFilters: {
        date_from: '',
        date_to: ''
      },
      pagination: {
        limit: 50,
        offset: 0
      },
      analyticsDays: 90
    }
  },
  computed: {
    currentPage() {
      return Math.floor(this.pagination.offset / this.pagination.limit) + 1
    },
    totalPages() {
      return Math.ceil((this.tipsData.count || 0) / this.pagination.limit)
    }
  },
  mounted() {
    this.loadDashboard()
  },
  watch: {
    activeTab(newTab) {
      if (newTab === 'dashboard' && !this.dashboardData.summary) {
        this.loadDashboard()
      } else if (newTab === 'list' && !this.tipsData.results) {
        this.loadTips()
      } else if (newTab === 'analytics' && !this.analyticsData.trends) {
        this.loadAnalytics()
      } else if (newTab === 'earnings' && !this.earningsData.overall) {
        this.loadEarnings()
      }
    }
  },
  methods: {
    async loadDashboard() {
      this.loading = true
      this.error = null
      try {
        const response = await adminTipsApi.getDashboard({ days: 30 })
        this.dashboardData = response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to load dashboard'
        console.error('Dashboard error:', err)
      } finally {
        this.loading = false
      }
    },
    async loadTips() {
      this.loading = true
      this.error = null
      try {
        const params = {
          ...this.filters,
          limit: this.pagination.limit,
          offset: this.pagination.offset
        }
        // Remove empty filters
        Object.keys(params).forEach(key => {
          if (params[key] === '') delete params[key]
        })
        const response = await adminTipsApi.listTips(params)
        this.tipsData = response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to load tips'
        console.error('Tips error:', err)
      } finally {
        this.loading = false
      }
    },
    async loadAnalytics() {
      this.loading = true
      this.error = null
      try {
        const response = await adminTipsApi.getAnalytics({ days: this.analyticsDays })
        this.analyticsData = response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to load analytics'
        console.error('Analytics error:', err)
      } finally {
        this.loading = false
      }
    },
    async loadEarnings() {
      this.loading = true
      this.error = null
      try {
        const params = { ...this.earningsFilters }
        // Remove empty filters
        Object.keys(params).forEach(key => {
          if (params[key] === '') delete params[key]
        })
        const response = await adminTipsApi.getEarnings(params)
        this.earningsData = response.data
      } catch (err) {
        this.error = err.response?.data?.detail || 'Failed to load earnings'
        console.error('Earnings error:', err)
      } finally {
        this.loading = false
      }
    },
    refreshDashboard() {
      this.loadDashboard()
    },
    clearFilters() {
      this.filters = {
        tip_type: '',
        payment_status: '',
        date_from: '',
        date_to: ''
      }
      this.pagination.offset = 0
      this.loadTips()
    },
    previousPage() {
      if (this.pagination.offset > 0) {
        this.pagination.offset -= this.pagination.limit
        this.loadTips()
      }
    },
    nextPage() {
      if (this.pagination.offset + this.pagination.limit < this.tipsData.count) {
        this.pagination.offset += this.pagination.limit
        this.loadTips()
      }
    },
    formatCurrency(value) {
      const num = parseFloat(value || 0)
      // Format with thousand separators and 2 decimal places
      return num.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })
    },
    formatNumber(value) {
      return parseInt(value || 0).toLocaleString()
    },
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString()
    }
  }
}
</script>

<style scoped>
.tip-management {
  /* Uses shared dashboard-container from dashboard.css */
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
}

.tab {
  padding: 10px 20px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  font-size: 16px;
}

.tab.active {
  border-bottom-color: #007bff;
  color: #007bff;
}

.tab-content {
  padding: 20px 0;
}

.loading, .error {
  text-align: center;
  padding: 40px;
}

.error {
  color: #dc3545;
}

/* Styles now use shared dashboard.css */

.filters {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.filters select,
.filters input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.tips-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.tips-table th,
.tips-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.tips-table th {
  background: #f8f9fa;
  font-weight: 600;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.completed {
  background: #d4edda;
  color: #155724;
}

.status-badge.pending {
  background: #fff3cd;
  color: #856404;
}

.status-badge.processing {
  background: #cce5ff;
  color: #004085;
}

.status-badge.failed {
  background: #f8d7da;
  color: #721c24;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 20px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Breakdown and other sections */
.breakdown {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.breakdown-item {
  padding: 16px;
  background: white;
  border-radius: 10px;
  border-left: 3px solid #667eea;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.breakdown-item h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #1f2937;
  font-weight: 600;
}

.breakdown-item p {
  margin: 8px 0;
  font-size: 14px;
  color: #4b5563;
  word-break: break-word;
  overflow-wrap: break-word;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Style paragraphs that contain money values (they start with $ or contain currency) */
.breakdown-item p:first-of-type + p,
.breakdown-item p:nth-of-type(3),
.breakdown-item p:nth-of-type(4) {
  font-weight: 600;
  color: #1f2937;
  font-size: clamp(13px, 1.5vw, 15px);
}

.payment-status {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-top: 16px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.status-item span:last-child {
  font-weight: 600;
  font-size: 18px;
  color: #1f2937;
}

.trends,
.top-performers {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.trend-item,
.performer-item {
  padding: 16px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
}

.trend-item h4,
.performer-item h4 {
  margin: 0 0 12px 0;
  font-size: 15px;
  color: #1f2937;
  font-weight: 600;
}

.trend-item p,
.performer-item p {
  margin: 6px 0;
  font-size: 14px;
  color: #4b5563;
  word-break: break-word;
  overflow-wrap: break-word;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Style money values (typically the last or second-to-last paragraph) */
.trend-item p:last-child,
.performer-item p:last-child {
  font-weight: 600;
  color: #1f2937;
  font-size: clamp(13px, 1.5vw, 15px);
}

/* Mobile optimizations for breakdown and other sections */
@media (max-width: 768px) {
  .breakdown {
    grid-template-columns: 1fr;
  }

  .payment-status {
    flex-direction: column;
  }

  .trends,
  .top-performers {
    grid-template-columns: 1fr;
  }
}
</style>


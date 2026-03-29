# Frontend Integration Guide - Admin Dashboard Endpoints

This guide provides frontend integration examples for the newly implemented Admin Dashboard endpoints.

## 📋 Table of Contents

1. [Order Management Dashboard](#order-management-dashboard)
2. [Special Orders Management Dashboard](#special-orders-management-dashboard)
3. [Class Bundles Management Dashboard](#class-bundles-management-dashboard)
4. [Tip Management Dashboard](#tip-management-dashboard)
5. [Review Moderation Dashboard](#review-moderation-dashboard)
6. [Dispute Management Dashboard](#dispute-management-dashboard)
7. [Refund Management Dashboard](#refund-management-dashboard)

---

## Order Management Dashboard

### API Service File: `src/api/admin/orders.js`

```javascript
import apiClient from '../client'

export const adminOrdersApi = {
  // Get order statistics dashboard
  getDashboard: () => {
    return apiClient.get('/admin-management/orders/dashboard/')
  },

  // Get order analytics and trends
  getAnalytics: (params = {}) => {
    return apiClient.get('/admin-management/orders/analytics/', { params })
  },

  // Get orders needing assignment
  getAssignmentQueue: (params = {}) => {
    return apiClient.get('/admin-management/orders/assignment-queue/', { params })
  },

  // Get overdue orders
  getOverdueOrders: (params = {}) => {
    return apiClient.get('/admin-management/orders/overdue/', { params })
  },

  // Get stuck orders
  getStuckOrders: (params = {}) => {
    return apiClient.get('/admin-management/orders/stuck/', { params })
  },

  // Bulk assign orders to writers
  bulkAssign: (data) => {
    return apiClient.post('/admin-management/orders/bulk-assign/', data)
  },

  // Bulk actions on orders
  bulkAction: (data) => {
    return apiClient.post('/admin-management/orders/bulk-action/', data)
  },

  // Get order timeline/history
  getOrderTimeline: (orderId) => {
    return apiClient.get(`/admin-management/orders/${orderId}/timeline/`)
  }
}
```

### Vue Component Example: `src/views/admin/OrdersDashboard.vue`

```vue
<template>
  <div class="orders-dashboard">
    <h1>Order Management Dashboard</h1>

    <!-- Dashboard Stats -->
    <div class="stats-grid" v-if="dashboardData">
      <StatCard
        title="Total Orders"
        :value="dashboardData.summary.total_orders"
        icon="📦"
      />
      <StatCard
        title="Pending Orders"
        :value="dashboardData.summary.pending_orders"
        icon="⏳"
      />
      <StatCard
        title="In Progress"
        :value="dashboardData.summary.in_progress_orders"
        icon="🔄"
      />
      <StatCard
        title="Completed"
        :value="dashboardData.summary.completed_orders"
        icon="✅"
      />
      <StatCard
        title="Needs Assignment"
        :value="dashboardData.summary.needs_assignment"
        icon="👤"
      />
      <StatCard
        title="Overdue"
        :value="dashboardData.summary.overdue_orders"
        icon="⚠️"
      />
      <StatCard
        title="Total Revenue"
        :value="formatCurrency(dashboardData.summary.total_revenue)"
        icon="💰"
      />
      <StatCard
        title="Avg Order Value"
        :value="formatCurrency(dashboardData.summary.avg_order_value)"
        icon="📊"
      />
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="{ active: activeTab === tab.id }"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Assignment Queue -->
    <div v-if="activeTab === 'assignment'" class="tab-content">
      <h2>Orders Needing Assignment</h2>
      <OrderList
        :orders="assignmentQueue"
        :loading="loadingAssignment"
        @assign="handleBulkAssign"
      />
    </div>

    <!-- Overdue Orders -->
    <div v-if="activeTab === 'overdue'" class="tab-content">
      <h2>Overdue Orders</h2>
      <OrderList
        :orders="overdueOrders"
        :loading="loadingOverdue"
      />
    </div>

    <!-- Stuck Orders -->
    <div v-if="activeTab === 'stuck'" class="tab-content">
      <h2>Stuck Orders</h2>
      <OrderList
        :orders="stuckOrders"
        :loading="loadingStuck"
      />
    </div>

    <!-- Analytics -->
    <div v-if="activeTab === 'analytics'" class="tab-content">
      <h2>Order Analytics</h2>
      <AnalyticsChart :data="analyticsData" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { adminOrdersApi } from '@/api/admin/orders'
import StatCard from '@/components/common/StatCard.vue'
import OrderList from '@/components/admin/OrderList.vue'
import AnalyticsChart from '@/components/admin/AnalyticsChart.vue'

const dashboardData = ref(null)
const assignmentQueue = ref([])
const overdueOrders = ref([])
const stuckOrders = ref([])
const analyticsData = ref(null)
const loadingDashboard = ref(false)
const loadingAssignment = ref(false)
const loadingOverdue = ref(false)
const loadingStuck = ref(false)
const activeTab = ref('overview')

const tabs = [
  { id: 'overview', label: 'Overview' },
  { id: 'assignment', label: 'Assignment Queue' },
  { id: 'overdue', label: 'Overdue' },
  { id: 'stuck', label: 'Stuck' },
  { id: 'analytics', label: 'Analytics' }
]

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

const loadDashboard = async () => {
  loadingDashboard.value = true
  try {
    const response = await adminOrdersApi.getDashboard()
    dashboardData.value = response.data
  } catch (error) {
    console.error('Error loading dashboard:', error)
  } finally {
    loadingDashboard.value = false
  }
}

const loadAssignmentQueue = async () => {
  loadingAssignment.value = true
  try {
    const response = await adminOrdersApi.getAssignmentQueue({ limit: 50 })
    assignmentQueue.value = response.data.orders
  } catch (error) {
    console.error('Error loading assignment queue:', error)
  } finally {
    loadingAssignment.value = false
  }
}

const loadOverdueOrders = async () => {
  loadingOverdue.value = true
  try {
    const response = await adminOrdersApi.getOverdueOrders({ limit: 50 })
    overdueOrders.value = response.data.orders
  } catch (error) {
    console.error('Error loading overdue orders:', error)
  } finally {
    loadingOverdue.value = false
  }
}

const loadStuckOrders = async () => {
  loadingStuck.value = true
  try {
    const response = await adminOrdersApi.getStuckOrders({ limit: 50 })
    stuckOrders.value = response.data.orders
  } catch (error) {
    console.error('Error loading stuck orders:', error)
  } finally {
    loadingStuck.value = false
  }
}

const loadAnalytics = async () => {
  try {
    const response = await adminOrdersApi.getAnalytics({ days: 30 })
    analyticsData.value = response.data
  } catch (error) {
    console.error('Error loading analytics:', error)
  }
}

const handleBulkAssign = async (orderIds, writerId) => {
  try {
    const response = await adminOrdersApi.bulkAssign({
      order_ids: orderIds,
      writer_id: writerId,
      reason: 'Bulk assignment by admin'
    })
    // Refresh assignment queue
    await loadAssignmentQueue()
    return response.data
  } catch (error) {
    console.error('Error bulk assigning:', error)
    throw error
  }
}

onMounted(() => {
  loadDashboard()
  loadAssignmentQueue()
  loadOverdueOrders()
  loadStuckOrders()
  loadAnalytics()
})
</script>

<style scoped>
.orders-dashboard {
  padding: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  border-bottom: 2px solid #e5e7eb;
}

.tabs button {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
}

.tabs button.active {
  border-bottom-color: #3b82f6;
  color: #3b82f6;
}

.tab-content {
  padding: 1rem 0;
}
</style>
```

---

## Special Orders Management Dashboard

### API Service File: `src/api/admin/specialOrders.js`

```javascript
import apiClient from '../client'

export const adminSpecialOrdersApi = {
  // Get special order statistics dashboard
  getDashboard: () => {
    return apiClient.get('/admin-management/special-orders/dashboard/')
  },

  // Get orders awaiting approval
  getApprovalQueue: (params = {}) => {
    return apiClient.get('/admin-management/special-orders/approval-queue/', { params })
  },

  // Get orders needing cost estimation
  getEstimatedQueue: (params = {}) => {
    return apiClient.get('/admin-management/special-orders/estimated-queue/', { params })
  },

  // Get installment payment tracking
  getInstallmentTracking: (params = {}) => {
    return apiClient.get('/admin-management/special-orders/installment-tracking/', { params })
  },

  // Get special order analytics
  getAnalytics: (params = {}) => {
    return apiClient.get('/admin-management/special-orders/analytics/', { params })
  },

  // Get or create/update predefined order configs
  getConfigs: () => {
    return apiClient.get('/admin-management/special-orders/configs/')
  },

  createOrUpdateConfig: (data) => {
    return apiClient.post('/admin-management/special-orders/configs/', data)
  }
}
```

### Vue Component Example: `src/views/admin/SpecialOrdersDashboard.vue`

```vue
<template>
  <div class="special-orders-dashboard">
    <h1>Special Orders Management</h1>

    <!-- Dashboard Stats -->
    <div class="stats-grid" v-if="dashboardData">
      <StatCard
        title="Total Orders"
        :value="dashboardData.summary.total_orders"
        icon="📦"
      />
      <StatCard
        title="Awaiting Approval"
        :value="dashboardData.summary.awaiting_approval"
        icon="⏳"
        :highlight="dashboardData.summary.needs_approval > 0"
      />
      <StatCard
        title="Needs Estimation"
        :value="dashboardData.summary.needs_estimation"
        icon="💰"
        :highlight="dashboardData.summary.needs_estimation > 0"
      />
      <StatCard
        title="In Progress"
        :value="dashboardData.summary.in_progress"
        icon="🔄"
      />
      <StatCard
        title="Completed"
        :value="dashboardData.summary.completed"
        icon="✅"
      />
      <StatCard
        title="Total Revenue"
        :value="formatCurrency(dashboardData.summary.total_revenue)"
        icon="💵"
      />
      <StatCard
        title="Pending Installments"
        :value="dashboardData.summary.pending_installments"
        icon="📅"
      />
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="{ active: activeTab === tab.id }"
      >
        {{ tab.label }}
        <span v-if="tab.badge" class="badge">{{ tab.badge }}</span>
      </button>
    </div>

    <!-- Approval Queue -->
    <div v-if="activeTab === 'approval'" class="tab-content">
      <h2>Orders Awaiting Approval</h2>
      <SpecialOrderList
        :orders="approvalQueue"
        :loading="loadingApproval"
        @approve="handleApprove"
      />
    </div>

    <!-- Estimation Queue -->
    <div v-if="activeTab === 'estimation'" class="tab-content">
      <h2>Orders Needing Cost Estimation</h2>
      <SpecialOrderList
        :orders="estimatedQueue"
        :loading="loadingEstimation"
        @estimate="handleEstimate"
      />
    </div>

    <!-- Installment Tracking -->
    <div v-if="activeTab === 'installments'" class="tab-content">
      <h2>Installment Payment Tracking</h2>
      <InstallmentList
        :installments="installments"
        :statistics="installmentStats"
        :loading="loadingInstallments"
      />
    </div>

    <!-- Analytics -->
    <div v-if="activeTab === 'analytics'" class="tab-content">
      <h2>Special Orders Analytics</h2>
      <AnalyticsChart :data="analyticsData" />
    </div>

    <!-- Configs -->
    <div v-if="activeTab === 'configs'" class="tab-content">
      <h2>Predefined Order Configurations</h2>
      <ConfigList
        :configs="configs"
        :loading="loadingConfigs"
        @create="handleCreateConfig"
        @update="handleUpdateConfig"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { adminSpecialOrdersApi } from '@/api/admin/specialOrders'
import StatCard from '@/components/common/StatCard.vue'
import SpecialOrderList from '@/components/admin/SpecialOrderList.vue'
import InstallmentList from '@/components/admin/InstallmentList.vue'
import AnalyticsChart from '@/components/admin/AnalyticsChart.vue'
import ConfigList from '@/components/admin/ConfigList.vue'

const dashboardData = ref(null)
const approvalQueue = ref([])
const estimatedQueue = ref([])
const installments = ref([])
const installmentStats = ref(null)
const analyticsData = ref(null)
const configs = ref([])
const loadingDashboard = ref(false)
const loadingApproval = ref(false)
const loadingEstimation = ref(false)
const loadingInstallments = ref(false)
const loadingConfigs = ref(false)
const activeTab = ref('overview')

const tabs = computed(() => [
  { id: 'overview', label: 'Overview' },
  {
    id: 'approval',
    label: 'Approval Queue',
    badge: dashboardData.value?.summary.needs_approval || 0
  },
  {
    id: 'estimation',
    label: 'Estimation Queue',
    badge: dashboardData.value?.summary.needs_estimation || 0
  },
  { id: 'installments', label: 'Installments' },
  { id: 'analytics', label: 'Analytics' },
  { id: 'configs', label: 'Configs' }
])

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

const loadDashboard = async () => {
  loadingDashboard.value = true
  try {
    const response = await adminSpecialOrdersApi.getDashboard()
    dashboardData.value = response.data
  } catch (error) {
    console.error('Error loading dashboard:', error)
  } finally {
    loadingDashboard.value = false
  }
}

const loadApprovalQueue = async () => {
  loadingApproval.value = true
  try {
    const response = await adminSpecialOrdersApi.getApprovalQueue({ limit: 50 })
    approvalQueue.value = response.data.orders
  } catch (error) {
    console.error('Error loading approval queue:', error)
  } finally {
    loadingApproval.value = false
  }
}

const loadEstimatedQueue = async () => {
  loadingEstimation.value = true
  try {
    const response = await adminSpecialOrdersApi.getEstimatedQueue({ limit: 50 })
    estimatedQueue.value = response.data.orders
  } catch (error) {
    console.error('Error loading estimated queue:', error)
  } finally {
    loadingEstimation.value = false
  }
}

const loadInstallments = async () => {
  loadingInstallments.value = true
  try {
    const response = await adminSpecialOrdersApi.getInstallmentTracking({ limit: 50 })
    installments.value = response.data.installments
    installmentStats.value = response.data.statistics
  } catch (error) {
    console.error('Error loading installments:', error)
  } finally {
    loadingInstallments.value = false
  }
}

const loadAnalytics = async () => {
  try {
    const response = await adminSpecialOrdersApi.getAnalytics({ days: 30 })
    analyticsData.value = response.data
  } catch (error) {
    console.error('Error loading analytics:', error)
  }
}

const loadConfigs = async () => {
  loadingConfigs.value = true
  try {
    const response = await adminSpecialOrdersApi.getConfigs()
    configs.value = response.data.configs
  } catch (error) {
    console.error('Error loading configs:', error)
  } finally {
    loadingConfigs.value = false
  }
}

const handleApprove = async (orderId) => {
  // Use existing special orders API
  // This would call the approve endpoint
  await loadApprovalQueue()
  await loadDashboard()
}

const handleEstimate = async (orderId, cost) => {
  // Use existing special orders API to update cost
  await loadEstimatedQueue()
  await loadDashboard()
}

const handleCreateConfig = async (configData) => {
  try {
    await adminSpecialOrdersApi.createOrUpdateConfig(configData)
    await loadConfigs()
  } catch (error) {
    console.error('Error creating config:', error)
    throw error
  }
}

const handleUpdateConfig = async (configData) => {
  try {
    await adminSpecialOrdersApi.createOrUpdateConfig(configData)
    await loadConfigs()
  } catch (error) {
    console.error('Error updating config:', error)
    throw error
  }
}

onMounted(() => {
  loadDashboard()
  loadApprovalQueue()
  loadEstimatedQueue()
  loadInstallments()
  loadAnalytics()
  loadConfigs()
})
</script>

<style scoped>
.special-orders-dashboard {
  padding: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  border-bottom: 2px solid #e5e7eb;
}

.tabs button {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  position: relative;
}

.tabs button.active {
  border-bottom-color: #3b82f6;
  color: #3b82f6;
}

.badge {
  background: #ef4444;
  color: white;
  border-radius: 9999px;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  margin-left: 0.5rem;
}

.tab-content {
  padding: 1rem 0;
}
</style>
```

---

## Class Bundles Management Dashboard

### API Service File: `src/api/admin/classBundles.js`

```javascript
import apiClient from '../client'

export const adminClassBundlesApi = {
  // Get class bundle statistics dashboard
  getDashboard: () => {
    return apiClient.get('/admin-management/class-bundles/dashboard/')
  },

  // Get installment payment tracking
  getInstallmentTracking: (params = {}) => {
    return apiClient.get('/admin-management/class-bundles/installment-tracking/', { params })
  },

  // Get bundles with pending deposits
  getDepositPending: (params = {}) => {
    return apiClient.get('/admin-management/class-bundles/deposit-pending/', { params })
  },

  // Get class bundle analytics
  getAnalytics: (params = {}) => {
    return apiClient.get('/admin-management/class-bundles/analytics/', { params })
  },

  // Get or create/update bundle configs
  getConfigs: () => {
    return apiClient.get('/admin-management/class-bundles/configs/')
  },

  createOrUpdateConfig: (data) => {
    return apiClient.post('/admin-management/class-bundles/configs/', data)
  },

  // Get communication threads
  getCommunicationThreads: (params = {}) => {
    return apiClient.get('/admin-management/class-bundles/communication-threads/', { params })
  },

  // Get support tickets
  getSupportTickets: (params = {}) => {
    return apiClient.get('/admin-management/class-bundles/support-tickets/', { params })
  }
}
```

### Vue Component Example: `src/views/admin/ClassBundlesDashboard.vue`

```vue
<template>
  <div class="class-bundles-dashboard">
    <h1>Class Bundles Management</h1>

    <!-- Dashboard Stats -->
    <div class="stats-grid" v-if="dashboardData">
      <StatCard
        title="Total Bundles"
        :value="dashboardData.summary.total_bundles"
        icon="📦"
      />
      <StatCard
        title="Not Started"
        :value="dashboardData.summary.not_started"
        icon="⏸️"
      />
      <StatCard
        title="In Progress"
        :value="dashboardData.summary.in_progress"
        icon="🔄"
      />
      <StatCard
        title="Completed"
        :value="dashboardData.summary.completed"
        icon="✅"
      />
      <StatCard
        title="Pending Deposits"
        :value="dashboardData.summary.pending_deposits"
        icon="💰"
        :highlight="dashboardData.summary.pending_deposits > 0"
      />
      <StatCard
        title="Pending Installments"
        :value="dashboardData.summary.pending_installments"
        icon="📅"
        :highlight="dashboardData.summary.pending_installments > 0"
      />
      <StatCard
        title="Total Revenue"
        :value="formatCurrency(dashboardData.summary.total_revenue)"
        icon="💵"
      />
      <StatCard
        title="Avg Bundle Value"
        :value="formatCurrency(dashboardData.summary.avg_bundle_value)"
        icon="📊"
      />
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="{ active: activeTab === tab.id }"
      >
        {{ tab.label }}
        <span v-if="tab.badge" class="badge">{{ tab.badge }}</span>
      </button>
    </div>

    <!-- Deposit Pending -->
    <div v-if="activeTab === 'deposits'" class="tab-content">
      <h2>Bundles with Pending Deposits</h2>
      <ClassBundleList
        :bundles="depositPending"
        :loading="loadingDeposits"
      />
    </div>

    <!-- Installment Tracking -->
    <div v-if="activeTab === 'installments'" class="tab-content">
      <h2>Installment Payment Tracking</h2>
      <InstallmentList
        :installments="installments"
        :statistics="installmentStats"
        :loading="loadingInstallments"
      />
    </div>

    <!-- Analytics -->
    <div v-if="activeTab === 'analytics'" class="tab-content">
      <h2>Class Bundles Analytics</h2>
      <AnalyticsChart :data="analyticsData" />
    </div>

    <!-- Configs -->
    <div v-if="activeTab === 'configs'" class="tab-content">
      <h2>Bundle Configurations</h2>
      <ConfigList
        :configs="configs"
        :loading="loadingConfigs"
        @create="handleCreateConfig"
        @update="handleUpdateConfig"
      />
    </div>

    <!-- Communication Threads -->
    <div v-if="activeTab === 'threads'" class="tab-content">
      <h2>Communication Threads</h2>
      <ThreadList
        :threads="threads"
        :loading="loadingThreads"
      />
    </div>

    <!-- Support Tickets -->
    <div v-if="activeTab === 'tickets'" class="tab-content">
      <h2>Support Tickets</h2>
      <TicketList
        :tickets="tickets"
        :loading="loadingTickets"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { adminClassBundlesApi } from '@/api/admin/classBundles'
import StatCard from '@/components/common/StatCard.vue'
import ClassBundleList from '@/components/admin/ClassBundleList.vue'
import InstallmentList from '@/components/admin/InstallmentList.vue'
import AnalyticsChart from '@/components/admin/AnalyticsChart.vue'
import ConfigList from '@/components/admin/ConfigList.vue'
import ThreadList from '@/components/admin/ThreadList.vue'
import TicketList from '@/components/admin/TicketList.vue'

const dashboardData = ref(null)
const depositPending = ref([])
const installments = ref([])
const installmentStats = ref(null)
const analyticsData = ref(null)
const configs = ref([])
const threads = ref([])
const tickets = ref([])
const loadingDashboard = ref(false)
const loadingDeposits = ref(false)
const loadingInstallments = ref(false)
const loadingConfigs = ref(false)
const loadingThreads = ref(false)
const loadingTickets = ref(false)
const activeTab = ref('overview')

const tabs = computed(() => [
  { id: 'overview', label: 'Overview' },
  {
    id: 'deposits',
    label: 'Pending Deposits',
    badge: dashboardData.value?.summary.pending_deposits || 0
  },
  {
    id: 'installments',
    label: 'Installments',
    badge: dashboardData.value?.summary.pending_installments || 0
  },
  { id: 'analytics', label: 'Analytics' },
  { id: 'configs', label: 'Configs' },
  { id: 'threads', label: 'Threads' },
  { id: 'tickets', label: 'Tickets' }
])

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

const loadDashboard = async () => {
  loadingDashboard.value = true
  try {
    const response = await adminClassBundlesApi.getDashboard()
    dashboardData.value = response.data
  } catch (error) {
    console.error('Error loading dashboard:', error)
  } finally {
    loadingDashboard.value = false
  }
}

const loadDepositPending = async () => {
  loadingDeposits.value = true
  try {
    const response = await adminClassBundlesApi.getDepositPending({ limit: 50 })
    depositPending.value = response.data.bundles
  } catch (error) {
    console.error('Error loading deposit pending:', error)
  } finally {
    loadingDeposits.value = false
  }
}

const loadInstallments = async () => {
  loadingInstallments.value = true
  try {
    const response = await adminClassBundlesApi.getInstallmentTracking({ limit: 50 })
    installments.value = response.data.installments
    installmentStats.value = response.data.statistics
  } catch (error) {
    console.error('Error loading installments:', error)
  } finally {
    loadingInstallments.value = false
  }
}

const loadAnalytics = async () => {
  try {
    const response = await adminClassBundlesApi.getAnalytics({ days: 30 })
    analyticsData.value = response.data
  } catch (error) {
    console.error('Error loading analytics:', error)
  }
}

const loadConfigs = async () => {
  loadingConfigs.value = true
  try {
    const response = await adminClassBundlesApi.getConfigs()
    configs.value = response.data.configs
  } catch (error) {
    console.error('Error loading configs:', error)
  } finally {
    loadingConfigs.value = false
  }
}

const loadThreads = async () => {
  loadingThreads.value = true
  try {
    const response = await adminClassBundlesApi.getCommunicationThreads({ limit: 50 })
    threads.value = response.data.threads
  } catch (error) {
    console.error('Error loading threads:', error)
  } finally {
    loadingThreads.value = false
  }
}

const loadTickets = async () => {
  loadingTickets.value = true
  try {
    const response = await adminClassBundlesApi.getSupportTickets({ limit: 50 })
    tickets.value = response.data.tickets
  } catch (error) {
    console.error('Error loading tickets:', error)
  } finally {
    loadingTickets.value = false
  }
}

const handleCreateConfig = async (configData) => {
  try {
    await adminClassBundlesApi.createOrUpdateConfig(configData)
    await loadConfigs()
  } catch (error) {
    console.error('Error creating config:', error)
    throw error
  }
}

const handleUpdateConfig = async (configData) => {
  try {
    await adminClassBundlesApi.createOrUpdateConfig(configData)
    await loadConfigs()
  } catch (error) {
    console.error('Error updating config:', error)
    throw error
  }
}

onMounted(() => {
  loadDashboard()
  loadDepositPending()
  loadInstallments()
  loadAnalytics()
  loadConfigs()
  loadThreads()
  loadTickets()
})
</script>

<style scoped>
.class-bundles-dashboard {
  padding: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  border-bottom: 2px solid #e5e7eb;
}

.tabs button {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  position: relative;
}

.tabs button.active {
  border-bottom-color: #3b82f6;
  color: #3b82f6;
}

.badge {
  background: #ef4444;
  color: white;
  border-radius: 9999px;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  margin-left: 0.5rem;
}

.tab-content {
  padding: 1rem 0;
}
</style>
```

---

## Tip Management Dashboard

### API Service File: `src/api/admin/tips.js`

```javascript
import apiClient from '../client'

export const adminTipsApi = {
  // Get tip statistics dashboard with earnings breakdown
  getDashboard: (params = {}) => {
    return apiClient.get('/admin-management/tips/dashboard/', { params })
  },

  // List all tips with earnings breakdown
  listTips: (params = {}) => {
    return apiClient.get('/admin-management/tips/list_tips/', { params })
  },

  // Get tip analytics with trends and breakdowns
  getAnalytics: (params = {}) => {
    return apiClient.get('/admin-management/tips/analytics/', { params })
  },

  // Get detailed earnings breakdown
  getEarnings: (params = {}) => {
    return apiClient.get('/admin-management/tips/earnings/', { params })
  },
}
```

### Vue Component Example: `src/views/admin/TipManagementDashboard.vue`

```vue
<template>
  <div class="tip-management-dashboard">
    <h1>Tip Management & Earnings Tracking</h1>

    <!-- Dashboard Stats -->
    <div class="stats-grid" v-if="dashboardData">
      <StatCard
        title="Total Tips"
        :value="dashboardData.summary.total_tips"
        icon="💰"
      />
      <StatCard
        title="Total Tip Amount"
        :value="formatCurrency(dashboardData.summary.total_tip_amount)"
        icon="💵"
      />
      <StatCard
        title="Writer Earnings"
        :value="formatCurrency(dashboardData.summary.total_writer_earnings)"
        icon="✍️"
      />
      <StatCard
        title="Platform Profit"
        :value="formatCurrency(dashboardData.summary.total_platform_profit)"
        icon="🏢"
      />
      <StatCard
        title="Avg Tip Amount"
        :value="formatCurrency(dashboardData.summary.avg_tip_amount)"
        icon="📊"
      />
      <StatCard
        title="Avg Writer %"
        :value="dashboardData.summary.avg_writer_percentage + '%'"
        icon="📈"
      />
    </div>

    <!-- Recent Summary -->
    <div class="recent-summary card p-4 mb-4" v-if="dashboardData">
      <h2 class="text-xl font-bold mb-2">Last {{ dashboardData.recent_summary.days }} Days</h2>
      <div class="grid grid-cols-4 gap-4">
        <div>
          <p class="text-sm text-gray-600">Tips</p>
          <p class="text-2xl font-bold">{{ dashboardData.recent_summary.total_tips }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-600">Total Amount</p>
          <p class="text-2xl font-bold">${{ formatCurrency(dashboardData.recent_summary.total_tip_amount) }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-600">Writer Earnings</p>
          <p class="text-2xl font-bold text-green-600">${{ formatCurrency(dashboardData.recent_summary.total_writer_earnings) }}</p>
        </div>
        <div>
          <p class="text-sm text-gray-600">Platform Profit</p>
          <p class="text-2xl font-bold text-blue-600">${{ formatCurrency(dashboardData.recent_summary.total_platform_profit) }}</p>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        :class="{ active: activeTab === tab.id }"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Tips List -->
    <div v-if="activeTab === 'tips'" class="tab-content">
      <h2 class="text-xl font-bold mb-4">All Tips</h2>
      <TipList
        :tips="tips"
        :summary="tipsSummary"
        :loading="loadingTips"
        @filter="handleFilter"
      />
    </div>

    <!-- Analytics -->
    <div v-if="activeTab === 'analytics'" class="tab-content">
      <h2 class="text-xl font-bold mb-4">Tip Analytics</h2>
      <AnalyticsChart :data="analyticsData" />
    </div>

    <!-- Earnings -->
    <div v-if="activeTab === 'earnings'" class="tab-content">
      <h2 class="text-xl font-bold mb-4">Earnings Breakdown</h2>
      <EarningsBreakdown :data="earningsData" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminTipsApi } from '@/api/admin/tips'
import StatCard from '@/components/common/StatCard.vue'
import TipList from '@/components/admin/TipList.vue'
import AnalyticsChart from '@/components/admin/AnalyticsChart.vue'
import EarningsBreakdown from '@/components/admin/EarningsBreakdown.vue'

const dashboardData = ref(null)
const tips = ref([])
const tipsSummary = ref(null)
const analyticsData = ref(null)
const earningsData = ref(null)
const loadingDashboard = ref(false)
const loadingTips = ref(false)
const loadingAnalytics = ref(false)
const loadingEarnings = ref(false)
const activeTab = ref('overview')

const tabs = [
  { id: 'overview', label: 'Overview' },
  { id: 'tips', label: 'All Tips' },
  { id: 'analytics', label: 'Analytics' },
  { id: 'earnings', label: 'Earnings' }
]

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value)
}

const loadDashboard = async () => {
  loadingDashboard.value = true
  try {
    const response = await adminTipsApi.getDashboard({ days: 30 })
    dashboardData.value = response.data
  } catch (error) {
    console.error('Error loading dashboard:', error)
  } finally {
    loadingDashboard.value = false
  }
}

const loadTips = async (params = {}) => {
  loadingTips.value = true
  try {
    const response = await adminTipsApi.listTips({ limit: 50, ...params })
    tips.value = response.data.results
    tipsSummary.value = response.data.summary
  } catch (error) {
    console.error('Error loading tips:', error)
  } finally {
    loadingTips.value = false
  }
}

const loadAnalytics = async () => {
  loadingAnalytics.value = true
  try {
    const response = await adminTipsApi.getAnalytics({ days: 90 })
    analyticsData.value = response.data
  } catch (error) {
    console.error('Error loading analytics:', error)
  } finally {
    loadingAnalytics.value = false
  }
}

const loadEarnings = async () => {
  loadingEarnings.value = true
  try {
    const response = await adminTipsApi.getEarnings()
    earningsData.value = response.data
  } catch (error) {
    console.error('Error loading earnings:', error)
  } finally {
    loadingEarnings.value = false
  }
}

const handleFilter = (filters) => {
  loadTips(filters)
}

onMounted(() => {
  loadDashboard()
  loadTips()
  loadAnalytics()
  loadEarnings()
})
</script>

<style scoped>
.tip-management-dashboard {
  padding: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.recent-summary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.tabs {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
  border-bottom: 2px solid #e5e7eb;
}

.tabs button {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
}

.tabs button.active {
  border-bottom-color: #3b82f6;
  color: #3b82f6;
}

.tab-content {
  padding: 1rem 0;
}
</style>
```

---

## Review Moderation Dashboard

### API Service File: `src/api/admin/reviews.js`

```javascript
import apiClient from '../client'

export const adminReviewsApi = {
  // Get moderation queue
  getModerationQueue: (params = {}) => {
    return apiClient.get('/admin-management/reviews/moderation-queue/', { params })
  },

  // Approve review
  approveReview: (reviewType, reviewId) => {
    return apiClient.post(`/admin-management/reviews/${reviewId}/approve/`, {
      review_type: reviewType
    })
  },

  // Reject review
  rejectReview: (reviewType, reviewId, reason) => {
    return apiClient.post(`/admin-management/reviews/${reviewId}/reject/`, {
      review_type: reviewType,
      reason
    })
  },

  // Flag review
  flagReview: (reviewType, reviewId, reason) => {
    return apiClient.post(`/admin-management/reviews/${reviewId}/flag/`, {
      review_type: reviewType,
      reason
    })
  },

  // Shadow hide review
  shadowReview: (reviewType, reviewId) => {
    return apiClient.post(`/admin-management/reviews/${reviewId}/shadow/`, {
      review_type: reviewType
    })
  },

  // Get review analytics
  getAnalytics: () => {
    return apiClient.get('/admin-management/reviews/analytics/')
  },

  // Get spam detection alerts
  getSpamDetection: () => {
    return apiClient.get('/admin-management/reviews/spam-detection/')
  }
}
```

---

## Dispute Management Dashboard

### API Service File: `src/api/admin/disputes.js`

```javascript
import apiClient from '../client'

export const adminDisputesApi = {
  // Get dispute statistics dashboard
  getDashboard: () => {
    return apiClient.get('/admin-management/disputes/dashboard/')
  },

  // Get dispute analytics
  getAnalytics: (params = {}) => {
    return apiClient.get('/admin-management/disputes/analytics/', { params })
  },

  // Get pending disputes
  getPendingDisputes: (params = {}) => {
    return apiClient.get('/admin-management/disputes/pending/', { params })
  },

  // Bulk resolve disputes
  bulkResolve: (data) => {
    return apiClient.post('/admin-management/disputes/bulk-resolve/', data)
  }
}
```

---

## Refund Management Dashboard

### API Service File: `src/api/admin/refunds.js`

```javascript
import apiClient from '../client'

export const adminRefundsApi = {
  // Get refund statistics dashboard
  getDashboard: () => {
    return apiClient.get('/admin-management/refunds/dashboard/')
  },

  // Get refund analytics
  getAnalytics: (params = {}) => {
    return apiClient.get('/admin-management/refunds/analytics/', { params })
  },

  // Get pending refunds
  getPendingRefunds: (params = {}) => {
    return apiClient.get('/admin-management/refunds/pending/', { params })
  },

  // Get refund history
  getHistory: (params = {}) => {
    return apiClient.get('/admin-management/refunds/history/', { params })
  }
}
```

---

## Usage Example

### In a Vue Component

```vue
<script setup>
import { ref, onMounted } from 'vue'
import { adminOrdersApi } from '@/api/admin/orders'
import { adminSpecialOrdersApi } from '@/api/admin/specialOrders'

const orders = ref([])
const loading = ref(false)

const loadOrders = async () => {
  loading.value = true
  try {
    const response = await adminOrdersApi.getDashboard()
    // Handle response
  } catch (error) {
    console.error('Error:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadOrders()
})
</script>
```

---

## Error Handling

All API calls should include proper error handling:

```javascript
try {
  const response = await adminOrdersApi.getDashboard()
  // Success
} catch (error) {
  if (error.response) {
    // Server responded with error
    console.error('Error:', error.response.data)
  } else if (error.request) {
    // Request made but no response
    console.error('No response:', error.request)
  } else {
    // Error setting up request
    console.error('Error:', error.message)
  }
}
```

---

## TypeScript Support

If using TypeScript, you can define types:

```typescript
// types/admin.ts
export interface OrderDashboard {
  summary: {
    total_orders: number
    pending_orders: number
    in_progress_orders: number
    completed_orders: number
    needs_assignment: number
    overdue_orders: number
    total_revenue: number
    avg_order_value: number
  }
  status_breakdown: Record<string, number>
  weekly_trends: Array<{
    week: string
    count: number
  }>
}

// In API service
import type { OrderDashboard } from '@/types/admin'

export const adminOrdersApi = {
  getDashboard: async (): Promise<OrderDashboard> => {
    const response = await apiClient.get('/admin-management/orders/dashboard/')
    return response.data
  }
}
```

---

## Next Steps

1. Copy the API service files to your frontend project's `src/api/admin/` directory
2. Create Vue components using the examples provided
3. Add routes to your Vue Router configuration
4. Test the integration with your backend
5. Add loading states and error handling
6. Implement real-time updates if needed (using WebSockets or polling)


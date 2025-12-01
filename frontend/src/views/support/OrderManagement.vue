<template>
  <div class="order-management space-y-6 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Order Management</h1>
        <p class="mt-2 text-gray-600">Manage and track orders requiring support</p>
      </div>
      <div class="flex items-center gap-4">
        <select
          v-model="statusFilter"
          @change="fetchOrders"
          class="px-4 py-2 border rounded-lg"
        >
          <option value="">All Statuses</option>
          <option value="needs_attention">Needs Attention</option>
          <option value="disputed">Disputed</option>
          <option value="on_hold">On Hold</option>
          <option value="revision_requested">Revision Requested</option>
        </select>
        <button
          @click="fetchOrders"
          class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          :disabled="loading"
        >
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div v-if="ordersData?.summary" class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <StatsCard
        name="Total Orders"
        :value="ordersData.summary.total_orders || 0"
        icon="📦"
        bgColor="bg-blue-100"
      />
      <StatsCard
        name="Needs Attention"
        :value="ordersData.summary.needs_attention || 0"
        icon="⚠️"
        bgColor="bg-yellow-100"
      />
      <StatsCard
        name="Disputed"
        :value="ordersData.summary.disputed || 0"
        icon="⚖️"
        bgColor="bg-red-100"
      />
      <StatsCard
        name="On Hold"
        :value="ordersData.summary.on_hold || 0"
        icon="⏸️"
        bgColor="bg-orange-100"
      />
    </div>

    <!-- Orders List -->
    <div class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Orders Requiring Support</h2>
      <div v-if="loading" class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
      </div>
      <div v-else-if="ordersData?.orders?.length > 0" class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Order ID</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Client</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Topic</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Priority</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="order in ordersData.orders" :key="order.id">
              <td class="px-4 py-3 whitespace-nowrap">
                <div class="font-medium text-gray-900">#{{ order.id }}</div>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {{ order.client_username || 'N/A' }}
              </td>
              <td class="px-4 py-3 text-sm text-gray-900">
                {{ order.topic || 'No topic' }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <span
                  :class="getStatusColor(order.status)"
                  class="px-2 py-1 text-xs font-medium rounded-full"
                >
                  {{ order.status || 'N/A' }}
                </span>
              </td>
              <td class="px-4 py-3 whitespace-nowrap">
                <span
                  :class="getPriorityColor(order.priority)"
                  class="px-2 py-1 text-xs font-medium rounded-full"
                >
                  {{ order.priority || 'Normal' }}
                </span>
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(order.created_at) }}
              </td>
              <td class="px-4 py-3 whitespace-nowrap text-sm">
                <button
                  @click="viewOrder(order.id)"
                  class="text-primary-600 hover:text-primary-800 font-medium"
                >
                  View
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-else class="text-center py-8 text-gray-500">
        <div class="text-4xl mb-2">📦</div>
        <p>No orders found</p>
      </div>
    </div>

    <!-- Orders by Status Breakdown -->
    <div v-if="ordersData?.status_breakdown" class="card bg-white rounded-lg shadow-sm p-6">
      <h2 class="text-xl font-bold text-gray-900 mb-4">Orders by Status</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div
          v-for="(count, status) in ordersData.status_breakdown"
          :key="status"
          class="p-4 bg-gray-50 rounded-lg"
        >
          <div class="text-sm text-gray-600 capitalize">{{ status.replace(/_/g, ' ') }}</div>
          <div class="text-2xl font-bold text-gray-900">{{ count }}</div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="card bg-red-50 border border-red-200 rounded-lg p-6">
      <div class="flex items-center">
        <span class="text-red-600 text-xl mr-2">⚠️</span>
        <p class="text-red-800">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import supportDashboardAPI from '@/api/support-dashboard'
import StatsCard from '@/components/dashboard/StatsCard.vue'

const loading = ref(false)
const error = ref(null)
const statusFilter = ref('')
const ordersData = ref(null)

const fetchOrders = async () => {
  loading.value = true
  error.value = null
  try {
    const params = statusFilter.value ? { status: statusFilter.value } : {}
    const response = await supportDashboardAPI.getDashboardOrders(params)
    ordersData.value = response.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load orders'
    console.error('Error fetching orders:', err)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

const getStatusColor = (status) => {
  const colors = {
    'needs_attention': 'bg-yellow-100 text-yellow-800',
    'disputed': 'bg-red-100 text-red-800',
    'on_hold': 'bg-orange-100 text-orange-800',
    'revision_requested': 'bg-blue-100 text-blue-800',
    'in_progress': 'bg-green-100 text-green-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

const getPriorityColor = (priority) => {
  const colors = {
    'high': 'bg-red-100 text-red-800',
    'medium': 'bg-yellow-100 text-yellow-800',
    'low': 'bg-green-100 text-green-800'
  }
  return colors[priority?.toLowerCase()] || 'bg-gray-100 text-gray-800'
}

const viewOrder = (orderId) => {
  // Navigate to order detail page
  window.location.href = `/orders/${orderId}`
}

onMounted(() => {
  fetchOrders()
})
</script>

<style scoped>
.order-management {
  max-width: 1400px;
  margin: 0 auto;
}
</style>


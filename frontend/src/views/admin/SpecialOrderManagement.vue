<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Special Orders Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage special and custom orders</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div v-if="dashboardData" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900 dark:to-blue-800 border border-blue-200 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Special Orders</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ dashboardData.summary?.total_orders || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900 dark:to-yellow-800 border border-yellow-200 dark:border-yellow-700">
        <p class="text-sm font-medium text-yellow-700 dark:text-yellow-300 mb-1">Awaiting Approval</p>
        <p class="text-3xl font-bold text-yellow-900 dark:text-yellow-100">{{ dashboardData.summary?.awaiting_approval || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900 dark:to-green-800 border border-green-200 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">In Progress</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ dashboardData.summary?.in_progress || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900 dark:to-purple-800 border border-purple-200 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Completed</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ dashboardData.summary?.completed || 0 }}</p>
      </div>
    </div>
    
    <!-- Quick Action Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700 mb-4">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="activeTab = tab.key"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === tab.key
              ? 'border-blue-500 text-blue-600 dark:text-blue-400'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Orders List -->
    <div class="card bg-white dark:bg-gray-800 rounded-lg shadow-sm">
      <div v-if="loading" class="p-8 text-center">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600 dark:text-gray-400">Loading special orders...</p>
    </div>

      <div v-else-if="specialOrders.length === 0" class="p-8 text-center text-gray-500 dark:text-gray-400">
        <p>No special orders found.</p>
    </div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">ID</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Client</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Total Cost</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Created</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="order in specialOrders" :key="order.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">#{{ order.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ order.client?.username || 'N/A' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                <span class="px-2 py-1 text-xs rounded-full" :class="order.order_type === 'predefined' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' : 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'">
                    {{ order.order_type === 'predefined' ? 'Predefined' : 'Estimated' }}
                  </span>
                </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm">
                <span class="px-2 py-1 text-xs rounded-full" :class="getStatusClass(order.status)">
                    {{ getStatusLabel(order.status) }}
                  </span>
                </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                ${{ formatCurrency(order.total_cost || 0) }}
                </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                  {{ formatDate(order.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                  @click="viewSpecialOrder(order)"
                  class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 hover:underline"
                >
                  View
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import specialOrdersAPI from '@/api/special-orders'
import adminSpecialOrdersAPI from '@/api/admin-special-orders'

const router = useRouter()

const loading = ref(false)
const dashboardData = ref(null)
const specialOrders = ref([])
const activeTab = ref('all')

const tabs = [
  { key: 'all', label: 'All Orders' },
  { key: 'approval', label: 'Approval Queue' },
  { key: 'estimated', label: 'Estimated Queue' },
  { key: 'in_progress', label: 'In Progress' },
  { key: 'completed', label: 'Completed' },
]

const loadDashboard = async () => {
  try {
    const res = await adminSpecialOrdersAPI.getDashboard()
    dashboardData.value = res.data
  } catch (error) {
    console.error('Error loading dashboard:', error)
  }
}

const loadSpecialOrders = async () => {
  loading.value = true
  try {
    const params = {}
    
    if (activeTab.value === 'approval') {
      const res = await adminSpecialOrdersAPI.getApprovalQueue()
      specialOrders.value = res.data.results || res.data || []
      return
    } else if (activeTab.value === 'estimated') {
      const res = await adminSpecialOrdersAPI.getEstimatedQueue()
      specialOrders.value = res.data.results || res.data || []
      return
    } else if (activeTab.value === 'in_progress') {
      params.status = 'in_progress'
    } else if (activeTab.value === 'completed') {
      params.status = 'completed'
    }
    
    const res = await specialOrdersAPI.list(params)
    specialOrders.value = res.data.results || res.data || []
  } catch (error) {
    console.error('Error loading special orders:', error)
  } finally {
    loading.value = false
  }
}

const getStatusClass = (status) => {
  const classes = {
    'inquiry': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200',
    'awaiting_approval': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    'in_progress': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    'completed': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  }
  return classes[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
}

const getStatusLabel = (status) => {
  const labels = {
    'inquiry': 'Inquiry',
    'awaiting_approval': 'Awaiting Approval',
    'in_progress': 'In Progress',
    'completed': 'Completed',
  }
  return labels[status] || status
}

const formatCurrency = (value) => {
  return parseFloat(value || 0).toFixed(2)
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

const viewSpecialOrder = (order) => {
  router.push({ name: 'AdminSpecialOrderDetail', params: { id: order.id } })
}

watch(activeTab, () => {
  loadSpecialOrders()
})

onMounted(() => {
  loadDashboard()
  loadSpecialOrders()
})
</script>

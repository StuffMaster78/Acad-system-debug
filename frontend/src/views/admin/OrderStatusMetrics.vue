<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Order Status Metrics</h1>
        <p class="mt-2 text-gray-600">Track order status distribution and workflow metrics</p>
      </div>
      <button
        @click="refreshMetrics"
        :disabled="loading"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
      >
        {{ loading ? 'Refreshing...' : 'Refresh' }}
      </button>
    </div>

    <!-- Order Status Breakdown -->
    <div class="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
      <div
        v-for="status in orderStatusBreakdown"
        :key="status.name"
        class="card bg-white rounded-lg shadow-sm p-4 border-l-4 hover:shadow-md transition-shadow cursor-pointer"
        :class="status.borderColor"
        @click="viewOrdersByStatus(status.status)"
      >
        <div class="flex items-center justify-between mb-1">
          <p class="text-xs font-medium text-gray-600">{{ status.name }}</p>
          <span class="text-sm" :class="status.textColor">{{ status.icon }}</span>
        </div>
        <p class="text-xl font-bold" :class="status.textColor">{{ status.value }}</p>
        <p v-if="status.percentage" class="text-xs text-gray-500 mt-1">{{ status.percentage }}%</p>
      </div>
    </div>

    <!-- Status Distribution Chart -->
    <div class="card">
      <h2 class="text-xl font-semibold mb-4">Status Distribution</h2>
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else class="space-y-3">
        <div
          v-for="status in orderStatusBreakdown"
          :key="status.name"
          class="flex items-center gap-3"
        >
          <div class="flex-1">
            <div class="flex items-center justify-between mb-1">
              <span class="text-sm font-medium text-gray-700">{{ status.name }}</span>
              <span class="text-sm text-gray-600">{{ status.value }} ({{ status.percentage }}%)</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="h-2 rounded-full transition-all duration-300"
                :class="status.bgColor"
                :style="{ width: `${status.percentage}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="card">
        <h2 class="text-xl font-semibold mb-4">Quick Actions</h2>
        <div class="space-y-3">
          <router-link
            to="/admin/orders"
            class="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div class="font-medium text-gray-900">View All Orders</div>
            <div class="text-sm text-gray-600 mt-1">Manage and filter all orders</div>
          </router-link>
          <router-link
            to="/admin/orders?status=pending"
            class="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div class="font-medium text-gray-900">Pending Orders</div>
            <div class="text-sm text-gray-600 mt-1">Review and assign pending orders</div>
          </router-link>
          <router-link
            to="/admin/orders?status=in_progress"
            class="block p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div class="font-medium text-gray-900">Orders in Progress</div>
            <div class="text-sm text-gray-600 mt-1">Monitor active work</div>
          </router-link>
        </div>
      </div>

      <div class="card">
        <h2 class="text-xl font-semibold mb-4">Status Summary</h2>
        <div class="space-y-4">
          <div class="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
            <span class="text-sm font-medium text-gray-700">Total Orders</span>
            <span class="text-lg font-bold text-blue-700">{{ totalOrders }}</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-green-50 rounded-lg">
            <span class="text-sm font-medium text-gray-700">Completed</span>
            <span class="text-lg font-bold text-green-700">{{ completedCount }}</span>
          </div>
          <div class="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
            <span class="text-sm font-medium text-gray-700">In Progress</span>
            <span class="text-lg font-bold text-yellow-700">{{ inProgressCount }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import dashboardAPI from '@/api/dashboard'

const router = useRouter()
const loading = ref(false)
const summaryData = ref(null)

const orderStatusBreakdown = computed(() => {
  if (!summaryData.value || !summaryData.value.orders_by_status) {
    return []
  }
  
  const statusMap = {
    'pending': { 
      name: 'Pending', 
      icon: '⏳', 
      borderColor: 'border-yellow-400', 
      textColor: 'text-yellow-600',
      bgColor: 'bg-yellow-500'
    },
    'in_progress': { 
      name: 'In Progress', 
      icon: '🔄', 
      borderColor: 'border-blue-400', 
      textColor: 'text-blue-600',
      bgColor: 'bg-blue-500'
    },
    'under_editing': { 
      name: 'Editing', 
      icon: '✏️', 
      borderColor: 'border-purple-400', 
      textColor: 'text-purple-600',
      bgColor: 'bg-purple-500'
    },
    'completed': { 
      name: 'Completed', 
      icon: '✅', 
      borderColor: 'border-green-400', 
      textColor: 'text-green-600',
      bgColor: 'bg-green-500'
    },
    'on_revision': { 
      name: 'Revision', 
      icon: '📝', 
      borderColor: 'border-orange-400', 
      textColor: 'text-orange-600',
      bgColor: 'bg-orange-500'
    },
    'disputed': { 
      name: 'Disputed', 
      icon: '⚠️', 
      borderColor: 'border-red-400', 
      textColor: 'text-red-600',
      bgColor: 'bg-red-500'
    },
    'canceled': { 
      name: 'Canceled', 
      icon: '❌', 
      borderColor: 'border-gray-400', 
      textColor: 'text-gray-600',
      bgColor: 'bg-gray-500'
    },
    'closed': { 
      name: 'Closed', 
      icon: '🔒', 
      borderColor: 'border-gray-500', 
      textColor: 'text-gray-700',
      bgColor: 'bg-gray-600'
    },
  }
  
  const ordersByStatus = summaryData.value.orders_by_status || {}
  const totalOrders = summaryData.value.total_orders || 0
  
  return Object.entries(ordersByStatus).map(([status, count]) => {
    const statusInfo = statusMap[status] || { 
      name: status, 
      icon: '📋', 
      borderColor: 'border-gray-300', 
      textColor: 'text-gray-600',
      bgColor: 'bg-gray-400'
    }
    return {
      status,
      name: statusInfo.name,
      value: count.toLocaleString(),
      icon: statusInfo.icon,
      borderColor: statusInfo.borderColor,
      textColor: statusInfo.textColor,
      bgColor: statusInfo.bgColor,
      percentage: totalOrders > 0 ? ((count / totalOrders) * 100).toFixed(1) : '0',
    }
  }).sort((a, b) => parseInt(b.value) - parseInt(a.value))
})

const totalOrders = computed(() => {
  return summaryData.value?.total_orders || 0
})

const completedCount = computed(() => {
  return orderStatusBreakdown.value.find(s => s.status === 'completed')?.value || '0'
})

const inProgressCount = computed(() => {
  const inProgress = orderStatusBreakdown.value.find(s => s.status === 'in_progress')?.value || '0'
  const underEditing = orderStatusBreakdown.value.find(s => s.status === 'under_editing')?.value || '0'
  return (parseInt(inProgress) + parseInt(underEditing)).toLocaleString()
})

const fetchSummary = async () => {
  loading.value = true
  try {
    const response = await dashboardAPI.getDashboard()
    // Extract order status data from dashboard response
    summaryData.value = {
      total_orders: response.data?.total_orders || 0,
      orders_by_status: response.data?.orders_by_status || {}
    }
  } catch (error) {
    console.error('Failed to fetch order status metrics:', error)
  } finally {
    loading.value = false
  }
}

const refreshMetrics = () => {
  fetchSummary()
}

const viewOrdersByStatus = (status) => {
  router.push(`/admin/orders?status=${status}`)
}

onMounted(() => {
  fetchSummary()
})
</script>

<style scoped>
.card {
  background-color: #ffffff;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px 0 rgba(15, 23, 42, 0.08);
  border: 1px solid #e5e7eb;
  padding: 1.5rem;
}
</style>


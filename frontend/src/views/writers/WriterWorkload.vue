<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Workload & Capacity</h1>
        <p class="mt-2 text-gray-600">Track your current workload vs capacity</p>
      </div>
      <div class="flex items-center gap-3">
        <label class="flex items-center gap-2 text-sm text-gray-600">
          <input
            type="checkbox"
            v-model="autoRefresh"
            class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
          />
          <span>Auto-refresh (30s)</span>
        </label>
        <button @click="loadWorkload" :disabled="loading" class="btn btn-secondary">
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="bg-white rounded-lg shadow-sm p-12">
      <div class="flex items-center justify-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    </div>

    <div v-else-if="workloadData" class="space-y-6">
      <!-- Capacity Overview -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Capacity Overview</h2>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Capacity Gauge -->
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700">Current Capacity</span>
              <span
                :class="[
                  'text-lg font-bold',
                  workloadData.capacity.is_at_capacity ? 'text-red-600' :
                  workloadData.capacity.is_near_capacity ? 'text-orange-600' :
                  'text-green-600'
                ]"
              >
                {{ workloadData.capacity.capacity_percentage }}%
              </span>
            </div>
            
            <!-- Progress Bar -->
            <div class="w-full bg-gray-200 rounded-full h-8 mb-4">
              <div
                :class="[
                  'h-8 rounded-full flex items-center justify-center text-sm font-medium text-white transition-all',
                  workloadData.capacity.is_at_capacity ? 'bg-red-600' :
                  workloadData.capacity.is_near_capacity ? 'bg-orange-600' :
                  'bg-green-600'
                ]"
                :style="{ width: `${Math.min(workloadData.capacity.capacity_percentage, 100)}%` }"
              >
                {{ workloadData.capacity.current_orders }} / {{ workloadData.capacity.max_orders }}
              </div>
            </div>
            
            <div class="grid grid-cols-3 gap-4 text-center">
              <div>
                <p class="text-2xl font-bold text-gray-900">{{ workloadData.capacity.current_orders }}</p>
                <p class="text-xs text-gray-600">Current</p>
              </div>
              <div>
                <p class="text-2xl font-bold text-gray-900">{{ workloadData.capacity.max_orders }}</p>
                <p class="text-xs text-gray-600">Max</p>
              </div>
              <div>
                <p class="text-2xl font-bold text-green-600">{{ workloadData.capacity.available_slots }}</p>
                <p class="text-xs text-gray-600">Available</p>
              </div>
            </div>
          </div>

          <!-- Status Indicators -->
          <div class="space-y-4">
            <div
              :class="[
                'p-4 rounded-lg border-2',
                workloadData.capacity.is_at_capacity
                  ? 'bg-red-50 border-red-200'
                  : workloadData.capacity.is_near_capacity
                  ? 'bg-orange-50 border-orange-200'
                  : 'bg-green-50 border-green-200'
              ]"
            >
              <div class="flex items-center gap-2 mb-2">
                <span class="text-2xl">
                  {{ workloadData.capacity.is_at_capacity ? '⚠️' : workloadData.capacity.is_near_capacity ? '⚡' : '✅' }}
                </span>
                <span class="font-semibold text-gray-900">
                  {{ workloadData.capacity.is_at_capacity ? 'At Capacity' : workloadData.capacity.is_near_capacity ? 'Near Capacity' : 'Capacity Available' }}
                </span>
              </div>
              <p class="text-sm text-gray-600">
                {{ workloadData.capacity.is_at_capacity
                  ? 'You have reached your maximum order limit. Complete existing orders before taking new ones.'
                  : workloadData.capacity.is_near_capacity
                  ? 'You are approaching your capacity limit. Consider completing orders before taking more.'
                  : 'You have available capacity to take on more orders.' }}
              </p>
            </div>

            <div class="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div class="flex items-center gap-2 mb-2">
                <span class="text-xl">📊</span>
                <span class="font-semibold text-gray-900">Writer Level</span>
              </div>
              <p class="text-sm text-gray-600">
                <span class="font-medium">{{ workloadData.writer_level.name }}</span>
                (Max: {{ workloadData.writer_level.max_orders }} orders)
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Status Breakdown -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold text-gray-900">Orders by Status</h2>
          <router-link
            to="/orders?assigned_writer=true"
            class="text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            View All Orders →
          </router-link>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
          <button
            v-for="(count, status) in workloadData.status_breakdown"
            :key="status"
            @click="filterByStatus(status)"
            :class="[
              'text-center p-4 border rounded-lg transition-all cursor-pointer',
              selectedStatus === status
                ? 'bg-primary-50 border-primary-300 shadow-md'
                : 'hover:bg-gray-50 hover:border-gray-300'
            ]"
          >
            <p class="text-2xl font-bold text-gray-900">{{ count }}</p>
            <p class="text-xs text-gray-600 capitalize mt-1">{{ formatStatus(status) }}</p>
          </button>
        </div>
      </div>

      <!-- Workload Estimate -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Workload Estimate</h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="text-center p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p class="text-3xl font-bold text-blue-900">{{ workloadData.workload_estimate.total_pages }}</p>
            <p class="text-sm text-gray-600 mt-1">Total Pages</p>
          </div>
          <div class="text-center p-4 bg-purple-50 border border-purple-200 rounded-lg">
            <p class="text-3xl font-bold text-purple-900">{{ workloadData.workload_estimate.estimated_hours }}h</p>
            <p class="text-sm text-gray-600 mt-1">Estimated Hours</p>
          </div>
          <div class="text-center p-4 bg-indigo-50 border border-indigo-200 rounded-lg">
            <p class="text-3xl font-bold text-indigo-900">{{ workloadData.workload_estimate.estimated_days }}d</p>
            <p class="text-sm text-gray-600 mt-1">Estimated Days</p>
            <p class="text-xs text-gray-500 mt-1">(8-hour workday)</p>
          </div>
        </div>
      </div>

      <!-- Active Orders List -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-semibold text-gray-900">Active Orders</h2>
          <router-link
            to="/orders?assigned_writer=true"
            class="text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            View All →
          </router-link>
        </div>
        <div v-if="activeOrders.length === 0" class="text-center py-12">
          <div class="flex flex-col items-center gap-3">
            <svg class="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <div>
              <p class="text-lg font-medium text-gray-900">You don't have any orders in progress</p>
              <p class="text-sm text-gray-500 mt-1">Check the order queue to find available orders to work on</p>
            </div>
            <router-link
              to="/writer/queue"
              class="mt-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
            >
              View Order Queue
            </router-link>
          </div>
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="order in activeOrders"
            :key="order.id"
            class="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div class="flex-1">
              <div class="flex items-center gap-3">
                <router-link
                  :to="`/orders/${order.id}`"
                  class="font-medium text-gray-900 hover:text-primary-600"
                >
                  Order #{{ order.id }}
                </router-link>
                <span
                  :class="[
                    'px-2 py-1 text-xs font-medium rounded',
                    getStatusColor(order.status)
                  ]"
                >
                  {{ formatStatus(order.status) }}
                </span>
              </div>
              <div class="text-sm text-gray-600 mt-1">
                {{ order.topic || 'No topic' }} • {{ order.pages || 0 }} pages
              </div>
              <div v-if="order.deadline" class="text-xs text-gray-500 mt-1">
                Due: {{ formatDeadline(order.deadline) }}
                <span
                  v-if="order.hours_remaining !== undefined"
                  :class="[
                    'ml-2 font-medium',
                    order.hours_remaining <= 24 ? 'text-red-600' :
                    order.hours_remaining <= 48 ? 'text-orange-600' :
                    'text-gray-600'
                  ]"
                >
                  ({{ formatTimeRemaining(order.hours_remaining) }} remaining)
                </span>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <router-link
                :to="`/orders/${order.id}`"
                class="px-3 py-1.5 text-sm font-medium text-primary-600 hover:text-primary-700 hover:bg-primary-50 rounded-lg transition-colors"
              >
                View
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Upcoming Deadlines -->
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4">Upcoming Deadlines</h2>
        <div v-if="workloadData.upcoming_deadlines.length === 0" class="text-center py-8 text-gray-500">
          No upcoming deadlines
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="deadline in workloadData.upcoming_deadlines"
            :key="deadline.id"
            class="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div class="flex-1">
              <div class="flex items-center gap-2">
                <router-link
                  :to="`/orders/${deadline.id}`"
                  class="font-medium text-gray-900 hover:text-primary-600"
                >
                  Order #{{ deadline.id }}
                </router-link>
                <span class="text-sm text-gray-500">{{ deadline.topic }}</span>
              </div>
              <div class="text-sm text-gray-600 mt-1">
                {{ deadline.pages }} pages • {{ formatDeadline(deadline.deadline) }}
              </div>
            </div>
            <div class="text-right">
              <div
                :class="[
                  'text-sm font-semibold',
                  deadline.hours_remaining <= 24 ? 'text-red-600' :
                  deadline.hours_remaining <= 48 ? 'text-orange-600' :
                  'text-gray-600'
                ]"
              >
                {{ formatTimeRemaining(deadline.hours_remaining) }}
              </div>
              <div class="text-xs text-gray-500">remaining</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import writerDashboardAPI from '@/api/writer-dashboard'
import ordersAPI from '@/api/orders'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const router = useRouter()
const { error: showError } = useToast()

const loading = ref(false)
const workloadData = ref(null)
const activeOrders = ref([])
const selectedStatus = ref(null)
const autoRefresh = ref(false)
let refreshInterval = null

const loadWorkload = async () => {
  loading.value = true
  try {
    const response = await writerDashboardAPI.getWorkload()
    workloadData.value = response.data
    
    // Load active orders
    await loadActiveOrders()
  } catch (error) {
    console.error('Failed to load workload:', error)
    
    // Check if it's a 404 or empty result (no orders is a valid state)
    if (error.response?.status === 404 || error.response?.status === 200) {
      // No workload data available - writer might not have any orders
      workloadData.value = {
        capacity: {
          current_orders: 0,
          max_orders: 10,
          available_slots: 10,
          capacity_percentage: 0,
          is_at_capacity: false,
          is_near_capacity: false,
        },
        status_breakdown: {},
        workload_estimate: {
          total_pages: 0,
          estimated_hours: 0,
          estimated_days: 0,
        },
        upcoming_deadlines: [],
        writer_level: {
          name: 'Unknown',
          max_orders: 10,
        },
      }
      activeOrders.value = []
    } else {
      // Real error - show message
      const errorMsg = getErrorMessage(error, 'Failed to load workload data. Please try again.')
      showError(errorMsg)
    }
  } finally {
    loading.value = false
  }
}

const loadActiveOrders = async () => {
  try {
    const params = {
      assigned_writer: true,
      status__in: ['in_progress', 'on_hold', 'revision_requested', 'submitted', 'under_editing', 'revision_in_progress'],
      page_size: 10,
    }
    
    if (selectedStatus.value) {
      params.status = selectedStatus.value
    }
    
    const response = await ordersAPI.list(params)
    const orders = response.data.results || response.data || []
    
    // Calculate hours remaining for each order
    const now = new Date()
    activeOrders.value = orders.map(order => {
      const deadline = order.writer_deadline || order.client_deadline || order.deadline
      let hours_remaining = null
      if (deadline) {
        const deadlineDate = new Date(deadline)
        hours_remaining = (deadlineDate - now) / (1000 * 60 * 60)
      }
      
      return {
        ...order,
        deadline,
        hours_remaining,
        pages: order.number_of_pages || order.pages || 0,
      }
    })
  } catch (error) {
    // If it's a 404 or empty result, that's fine - just no orders
    if (error.response?.status === 404) {
      activeOrders.value = []
    } else {
      // Only log real errors, don't show error message for empty results
      console.error('Failed to load active orders:', error)
      activeOrders.value = []
    }
  }
}

const filterByStatus = (status) => {
  if (selectedStatus.value === status) {
    selectedStatus.value = null
  } else {
    selectedStatus.value = status
  }
  loadActiveOrders()
}

const formatStatus = (status) => {
  return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const getStatusColor = (status) => {
  const colors = {
    'in_progress': 'bg-blue-100 text-blue-800',
    'on_hold': 'bg-yellow-100 text-yellow-800',
    'revision_requested': 'bg-orange-100 text-orange-800',
    'revision_in_progress': 'bg-orange-100 text-orange-800',
    'submitted': 'bg-green-100 text-green-800',
    'under_editing': 'bg-purple-100 text-purple-800',
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

const formatDeadline = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatTimeRemaining = (hours) => {
  if (hours === null || hours === undefined) return 'N/A'
  if (hours < 0) return 'Overdue'
  if (hours < 1) {
    return `${Math.round(hours * 60)}m`
  } else if (hours < 24) {
    return `${Math.round(hours)}h`
  } else {
    const days = Math.floor(hours / 24)
    const remainingHours = Math.round(hours % 24)
    return `${days}d ${remainingHours}h`
  }
}

// Watch autoRefresh and set up interval
watch(autoRefresh, (newVal) => {
  if (newVal && !refreshInterval) {
    refreshInterval = setInterval(() => {
      if (!loading.value) {
        loadWorkload()
      }
    }, 30000) // 30 seconds
  } else if (!newVal && refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
})

onMounted(() => {
  loadWorkload()
})

onBeforeUnmount(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
    refreshInterval = null
  }
})
</script>

<style scoped>
/* Styles are applied via Tailwind classes directly in template */
</style>


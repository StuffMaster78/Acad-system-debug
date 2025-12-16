<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <h2 class="text-xl font-bold text-gray-900">Order Activity Timeline</h2>
      <div class="flex items-center gap-4">
        <!-- Order Filter -->
        <select
          v-model="selectedOrderId"
          @change="handleOrderChange"
          class="px-3 py-2 border rounded-lg text-sm"
        >
          <option value="">All Orders</option>
          <option v-for="order in availableOrders" :key="order.id" :value="order.id">
            Order #{{ order.id }} - {{ order.topic }}
          </option>
        </select>
        <!-- Date Range Filter -->
        <div class="flex items-center gap-2">
          <input
            type="date"
            v-model="dateFrom"
            @change="handleDateChange"
            class="px-3 py-2 border rounded-lg text-sm"
            placeholder="From"
          />
          <input
            type="date"
            v-model="dateTo"
            @change="handleDateChange"
            class="px-3 py-2 border rounded-lg text-sm"
            placeholder="To"
          />
        </div>
        <button
          @click="refreshTimeline"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm"
          :disabled="loading"
        >
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!timelineData || Object.keys(timelineData.timeline || {}).length === 0" class="text-center py-12">
      <div class="text-4xl mb-4">📅</div>
      <p class="text-gray-600">No activity found for the selected period.</p>
    </div>

    <!-- Timeline -->
    <div v-else class="space-y-6">
      <div
        v-for="(events, date) in sortedTimeline"
        :key="date"
        class="card bg-white rounded-lg shadow-sm p-6"
      >
        <!-- Date Header -->
        <div class="flex items-center gap-3 mb-4 pb-4 border-b border-gray-200">
          <div class="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
            <span class="text-primary-600 font-bold">{{ formatDay(date) }}</span>
          </div>
          <div>
            <div class="font-semibold text-gray-900">{{ formatDate(date) }}</div>
            <div class="text-sm text-gray-500">{{ events.length }} event{{ events.length !== 1 ? 's' : '' }}</div>
          </div>
        </div>

        <!-- Events -->
        <div class="space-y-4">
          <div
            v-for="(event, index) in events"
            :key="`${event.timestamp}-${index}`"
            class="flex gap-4"
          >
            <!-- Timeline Line -->
            <div class="flex flex-col items-center">
              <div
                class="w-3 h-3 rounded-full border-2 border-white shadow-sm"
                :class="getEventTypeColor(event.type)"
              ></div>
              <div
                v-if="index < events.length - 1"
                class="w-0.5 h-full bg-gray-200 mt-2"
              ></div>
            </div>

            <!-- Event Content -->
            <div class="flex-1 pb-4">
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-1">
                    <span :class="getEventTypeIconClass(event.type)">
                      {{ getEventTypeIcon(event.type) }}
                    </span>
                    <span class="font-medium text-gray-900">{{ getEventTypeLabel(event.type) }}</span>
                    <span
                      v-if="event.order_id"
                      class="text-xs px-2 py-1 bg-gray-100 rounded text-gray-600"
                    >
                      Order #{{ event.order_id }}
                    </span>
                  </div>
                  <p class="text-sm text-gray-700 mb-2">{{ event.description }}</p>
                  <div v-if="event.details && Object.keys(event.details).length > 0" class="mt-2">
                    <div
                      v-for="(value, key) in event.details"
                      :key="key"
                      class="text-xs text-gray-500 mb-1"
                    >
                      <span class="font-medium capitalize">{{ formatDetailKey(key) }}:</span>
                      <span class="ml-1">{{ formatDetailValue(value) }}</span>
                    </div>
                  </div>
                </div>
                <div class="text-xs text-gray-500 ml-4">
                  {{ formatTime(event.timestamp) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Summary -->
    <div v-if="timelineData" class="card bg-gray-50 rounded-lg p-4">
      <div class="text-sm text-gray-600">
        Showing <strong>{{ timelineData.total_events || 0 }}</strong> event{{ timelineData.total_events !== 1 ? 's' : '' }}
        <span v-if="selectedOrderId">for Order #{{ selectedOrderId }}</span>
        <span v-else>across all orders</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import clientDashboardAPI from '@/api/client-dashboard'
import ordersAPI from '@/api/orders'

const props = defineProps({
  orderId: {
    type: [String, Number],
    default: null
  },
  autoLoad: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['order-selected', 'date-range-changed'])

// State
const loading = ref(false)
const timelineData = ref(null)
const availableOrders = ref([])
const selectedOrderId = ref(props.orderId || '')
const dateFrom = ref('')
const dateTo = ref('')

// Computed
const sortedTimeline = computed(() => {
  if (!timelineData.value?.timeline) return {}

  const timeline = timelineData.value.timeline
  const sorted = {}

  // Sort dates in descending order (most recent first)
  Object.keys(timeline)
    .sort((a, b) => new Date(b) - new Date(a))
    .forEach((date) => {
      const entries = Array.isArray(timeline[date]) ? timeline[date] : []
      sorted[date] = [...entries].sort((a, b) => {
        return new Date(b.timestamp) - new Date(a.timestamp)
      })
    })

  return sorted
})

// Methods
const fetchTimeline = async () => {
  loading.value = true
  try {
    const params = {}
    if (selectedOrderId.value) {
      params.order_id = selectedOrderId.value
    }
    if (dateFrom.value) {
      params.date_from = dateFrom.value
    }
    if (dateTo.value) {
      params.date_to = dateTo.value
    }
    
    const response = await clientDashboardAPI.getOrderActivityTimeline(params)
    timelineData.value = response?.data || null
  } catch (err) {
    console.error('Failed to fetch order activity timeline:', err)
    timelineData.value = null
  } finally {
    loading.value = false
  }
}

const fetchAvailableOrders = async () => {
  try {
    const response = await ordersAPI.list({ page_size: 100, ordering: '-created_at' })
    availableOrders.value = Array.isArray(response.data?.results)
      ? response.data.results
      : (Array.isArray(response.data) ? response.data : [])
  } catch (err) {
    console.error('Failed to fetch available orders:', err)
    availableOrders.value = []
  }
}

const refreshTimeline = () => {
  fetchTimeline()
}

const handleOrderChange = () => {
  emit('order-selected', selectedOrderId.value)
  fetchTimeline()
}

const handleDateChange = () => {
  emit('date-range-changed', { dateFrom: dateFrom.value, dateTo: dateTo.value })
  fetchTimeline()
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatDay = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.getDate()
}

const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const getEventTypeIcon = (type) => {
  const icons = {
    'order_created': '📝',
    'status_changed': '🔄',
    'payment_event': '💳',
    'writer_assigned': '✍️',
    'order_submitted': '📤',
    'client_deadline': '⏰',
    'writer_deadline': '⏰',
  }
  return icons[type] || '📌'
}

const getEventTypeLabel = (type) => {
  const labels = {
    'order_created': 'Order Created',
    'status_changed': 'Status Changed',
    'payment_event': 'Payment Event',
    'writer_assigned': 'Writer Assigned',
    'order_submitted': 'Order Submitted',
    'client_deadline': 'Client Deadline',
    'writer_deadline': 'Writer Deadline',
  }
  return labels[type] || type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const getEventTypeColor = (type) => {
  const colors = {
    'order_created': 'bg-blue-500',
    'status_changed': 'bg-purple-500',
    'payment_event': 'bg-green-500',
    'writer_assigned': 'bg-indigo-500',
    'order_submitted': 'bg-yellow-500',
    'client_deadline': 'bg-orange-500',
    'writer_deadline': 'bg-red-500',
  }
  return colors[type] || 'bg-gray-500'
}

const getEventTypeIconClass = (type) => {
  return 'text-lg'
}

const formatDetailKey = (key) => {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatDetailValue = (value) => {
  if (typeof value === 'object' && value !== null) {
    return JSON.stringify(value)
  }
  if (typeof value === 'boolean') {
    return value ? 'Yes' : 'No'
  }
  return String(value)
}

// Watch for prop changes
watch(() => props.orderId, (newId) => {
  if (newId) {
    selectedOrderId.value = newId
    fetchTimeline()
  }
})

// Lifecycle
onMounted(async () => {
  if (props.autoLoad) {
    await fetchAvailableOrders()
    await fetchTimeline()
  }
})
</script>

<style scoped>
.card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
}
</style>


<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-xl font-bold text-gray-900">Enhanced Order Status</h2>
        <p class="text-sm text-gray-600 mt-1">Detailed tracking for Order #{{ orderId }}</p>
      </div>
      <button
        @click="refreshStatus"
        :disabled="loading"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm disabled:opacity-50"
      >
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="text-red-800">{{ error }}</span>
      </div>
    </div>

    <!-- Status Content -->
    <div v-else-if="statusData" class="space-y-6">
      <!-- Current Status Card -->
      <div class="card bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Current Status</h3>
        <div class="flex items-center gap-4">
          <div class="px-4 py-2 bg-primary-100 text-primary-700 rounded-lg font-semibold">
            {{ formatStatus(statusData.current_status) }}
          </div>
          <div v-if="statusData.progress" class="flex-1">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm text-gray-600">Progress</span>
              <span class="text-sm font-semibold text-gray-900">{{ statusData.progress.percentage }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="bg-primary-600 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${statusData.progress.percentage}%` }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Estimated Completion -->
      <div v-if="statusData.estimated_completion" class="card bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Estimated Completion</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="p-4 bg-blue-50 rounded-lg">
            <div class="text-sm text-gray-600 mb-1">Deadline</div>
            <div class="text-lg font-semibold text-gray-900">
              {{ formatDateTime(statusData.estimated_completion.deadline) }}
            </div>
          </div>
          <div class="p-4 bg-orange-50 rounded-lg">
            <div class="text-sm text-gray-600 mb-1">Time Remaining</div>
            <div class="text-lg font-semibold text-gray-900">
              {{ statusData.estimated_completion.days_remaining }} days
              <span class="text-sm text-gray-600">({{ statusData.estimated_completion.hours_remaining }} hours)</span>
            </div>
          </div>
          <div class="p-4" :class="statusData.estimated_completion.is_overdue ? 'bg-red-50' : 'bg-green-50'">
            <div class="text-sm text-gray-600 mb-1">Status</div>
            <div class="text-lg font-semibold" :class="statusData.estimated_completion.is_overdue ? 'text-red-700' : 'text-green-700'">
              {{ statusData.estimated_completion.is_overdue ? '⚠️ Overdue' : '✅ On Track' }}
            </div>
          </div>
        </div>
      </div>

      <!-- Writer Activity -->
      <div v-if="statusData.writer_activity" class="card bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Writer Activity</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div class="text-sm text-gray-600 mb-1">Writer</div>
            <div class="text-lg font-semibold text-gray-900">{{ statusData.writer_activity.writer_username }}</div>
          </div>
          <div>
            <div class="text-sm text-gray-600 mb-1">Activity Status</div>
            <div class="flex items-center gap-2">
              <span
                class="px-3 py-1 rounded-full text-sm font-semibold"
                :class="statusData.writer_activity.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'"
              >
                {{ statusData.writer_activity.is_active ? '🟢 Active' : '⚪ Inactive' }}
              </span>
            </div>
          </div>
          <div v-if="statusData.writer_activity.last_activity">
            <div class="text-sm text-gray-600 mb-1">Last Activity</div>
            <div class="text-lg font-semibold text-gray-900">
              {{ formatDateTime(statusData.writer_activity.last_activity) }}
            </div>
            <div class="text-xs text-gray-500 mt-1">
              {{ statusData.writer_activity.hours_since_activity }} hours ago
            </div>
          </div>
        </div>
      </div>

      <!-- Quality Metrics -->
      <div v-if="statusData.quality_metrics" class="card bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Quality Metrics</h3>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="text-center p-4 bg-blue-50 rounded-lg">
            <div class="text-2xl font-bold text-blue-600">{{ statusData.quality_metrics.revision_count || 0 }}</div>
            <div class="text-sm text-gray-600 mt-1">Revisions</div>
          </div>
          <div class="text-center p-4 bg-orange-50 rounded-lg">
            <div class="text-2xl font-bold text-orange-600">{{ statusData.quality_metrics.dispute_count || 0 }}</div>
            <div class="text-sm text-gray-600 mt-1">Disputes</div>
          </div>
          <div class="text-center p-4 bg-green-50 rounded-lg">
            <div class="text-2xl font-bold text-green-600">
              {{ statusData.quality_metrics.average_rating || 'N/A' }}
            </div>
            <div class="text-sm text-gray-600 mt-1">Avg Rating</div>
          </div>
          <div class="text-center p-4 bg-purple-50 rounded-lg">
            <div class="text-2xl font-bold text-purple-600">
              {{ statusData.quality_metrics.has_reviews ? '✅' : '❌' }}
            </div>
            <div class="text-sm text-gray-600 mt-1">Has Reviews</div>
          </div>
        </div>
      </div>

      <!-- Recent Progress Updates -->
      <div v-if="statusData.progress?.recent_updates?.length" class="card bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Recent Progress Updates</h3>
        <div class="space-y-3">
          <div
            v-for="(update, index) in statusData.progress.recent_updates"
            :key="index"
            class="flex items-center gap-4 p-3 bg-gray-50 rounded-lg"
          >
            <div class="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
              <span class="text-primary-600 font-bold">{{ update.progress_percentage }}%</span>
            </div>
            <div class="flex-1">
              <div class="text-sm font-medium text-gray-900">{{ formatDateTime(update.timestamp) }}</div>
              <div v-if="update.notes" class="text-sm text-gray-600 mt-1">{{ update.notes }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Status Timeline -->
      <div v-if="statusData.status_timeline?.length" class="card bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Status Timeline</h3>
        <div class="space-y-4">
          <div
            v-for="(transition, index) in statusData.status_timeline"
            :key="index"
            class="flex gap-4"
          >
            <div class="flex flex-col items-center">
              <div class="w-3 h-3 rounded-full bg-primary-500 border-2 border-white shadow-sm"></div>
              <div v-if="index < statusData.status_timeline.length - 1" class="w-0.5 h-full bg-gray-200 mt-2"></div>
            </div>
            <div class="flex-1 pb-4">
              <div class="flex items-center justify-between">
                <div>
                  <div class="font-medium text-gray-900">
                    {{ formatStatus(transition.from_status) }} → {{ formatStatus(transition.to_status) }}
                  </div>
                  <div class="text-sm text-gray-600 mt-1">{{ transition.action }}</div>
                  <div class="text-xs text-gray-500 mt-1">
                    {{ transition.is_automatic ? 'Automatic' : 'Manual' }} by {{ transition.actor }}
                  </div>
                </div>
                <div class="text-xs text-gray-500">{{ formatDateTime(transition.timestamp) }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Writer Reassignments -->
      <div v-if="statusData.writer_reassignments?.length" class="card bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Writer Reassignments</h3>
        <div class="space-y-3">
          <div
            v-for="(reassignment, index) in statusData.writer_reassignments"
            :key="index"
            class="p-4 bg-yellow-50 rounded-lg border border-yellow-200"
          >
            <div class="flex items-center justify-between mb-2">
              <div class="font-medium text-gray-900">
                {{ reassignment.previous_writer || 'Unassigned' }} → {{ reassignment.new_writer || 'Unassigned' }}
              </div>
              <div class="text-xs text-gray-500">{{ formatDateTime(reassignment.timestamp) }}</div>
            </div>
            <div class="text-sm text-gray-600">{{ reassignment.reason }}</div>
            <div class="text-xs text-gray-500 mt-1">Reassigned by: {{ reassignment.reassigned_by }}</div>
          </div>
        </div>
      </div>

      <!-- Order Details -->
      <div class="card bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">Order Details</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div class="text-sm text-gray-600 mb-1">Topic</div>
            <div class="text-lg font-semibold text-gray-900">{{ statusData.order_topic }}</div>
          </div>
          <div v-if="statusData.order_details.type_of_work">
            <div class="text-sm text-gray-600 mb-1">Type of Work</div>
            <div class="text-lg font-semibold text-gray-900">{{ statusData.order_details.type_of_work }}</div>
          </div>
          <div v-if="statusData.order_details.paper_type">
            <div class="text-sm text-gray-600 mb-1">Paper Type</div>
            <div class="text-lg font-semibold text-gray-900">{{ statusData.order_details.paper_type }}</div>
          </div>
          <div v-if="statusData.order_details.number_of_pages">
            <div class="text-sm text-gray-600 mb-1">Pages</div>
            <div class="text-lg font-semibold text-gray-900">{{ statusData.order_details.number_of_pages }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import clientDashboardAPI from '@/api/client-dashboard'

const props = defineProps({
  orderId: {
    type: [String, Number],
    required: true
  },
  autoLoad: {
    type: Boolean,
    default: true
  }
})

const loading = ref(false)
const error = ref(null)
const statusData = ref(null)

const fetchStatus = async () => {
  if (!props.orderId) return
  
  loading.value = true
  error.value = null
  try {
    const response = await clientDashboardAPI.getEnhancedOrderStatus(props.orderId)
    statusData.value = response?.data || null
  } catch (err) {
    console.error('Failed to fetch enhanced order status:', err)
    error.value = err.response?.data?.detail || 'Failed to load order status'
    statusData.value = null
  } finally {
    loading.value = false
  }
}

const refreshStatus = () => {
  fetchStatus()
}

const formatStatus = (status) => {
  if (!status) return 'Unknown'
  return status.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

watch(() => props.orderId, (newId) => {
  if (newId && props.autoLoad) {
    fetchStatus()
  }
})

onMounted(() => {
  if (props.autoLoad && props.orderId) {
    fetchStatus()
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


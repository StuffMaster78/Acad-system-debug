<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Order Request Status</h1>
        <p class="mt-2 text-gray-600">Track your order requests and their approval status</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="loadRequests" :disabled="loading" class="btn btn-secondary">
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
        <span v-if="lastUpdated" class="text-xs text-gray-500">
          Updated: {{ formatTime(lastUpdated) }}
        </span>
      </div>
    </div>

    <!-- Statistics -->
    <div v-if="requestData" class="grid grid-cols-1 sm:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
        <p class="text-sm font-medium text-blue-700 mb-1">Total Requests</p>
        <p class="text-3xl font-bold text-blue-900">{{ requestData.statistics.total || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Pending</p>
        <p class="text-3xl font-bold text-yellow-900">{{ requestData.statistics.pending || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Approved</p>
        <p class="text-3xl font-bold text-green-900">{{ requestData.statistics.approved || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-red-50 to-red-100 border border-red-200">
        <p class="text-sm font-medium text-red-700 mb-1">Rejected</p>
        <p class="text-3xl font-bold text-red-900">{{ requestData.statistics.rejected || 0 }}</p>
      </div>
    </div>

    <!-- Requests List -->
    <div v-if="loading" class="bg-white rounded-lg shadow-sm p-12">
      <div class="flex items-center justify-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    </div>

    <div v-else-if="requestData && requestData.requests.length === 0" class="bg-white rounded-lg shadow-sm p-12 text-center">
      <p class="text-gray-500 text-lg">No order requests found.</p>
      <p class="text-gray-400 text-sm mt-2">Request orders from the order queue to see them here.</p>
      <router-link to="/writer/queue" class="mt-4 inline-block btn btn-primary">
        View Order Queue
      </router-link>
    </div>

    <div v-else-if="requestData" class="space-y-4">
      <!-- Filter Tabs -->
      <div class="bg-white rounded-lg shadow-sm p-4">
        <div class="flex gap-2">
          <button
            @click="filterStatus = 'all'"
            :class="[
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              filterStatus === 'all'
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            ]"
          >
            All ({{ requestData.statistics.total }})
          </button>
          <button
            @click="filterStatus = 'pending'"
            :class="[
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              filterStatus === 'pending'
                ? 'bg-yellow-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            ]"
          >
            Pending ({{ requestData.statistics.pending }})
          </button>
          <button
            @click="filterStatus = 'approved'"
            :class="[
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              filterStatus === 'approved'
                ? 'bg-green-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            ]"
          >
            Approved ({{ requestData.statistics.approved }})
          </button>
          <button
            @click="filterStatus = 'rejected'"
            :class="[
              'px-4 py-2 rounded-lg text-sm font-medium transition-colors',
              filterStatus === 'rejected'
                ? 'bg-red-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            ]"
          >
            Rejected ({{ requestData.statistics.rejected }})
          </button>
        </div>
      </div>

      <!-- Requests -->
      <div class="space-y-3">
        <div
          v-for="request in filteredRequests"
          :key="`${request.type}-${request.id}`"
          class="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
        >
          <div class="p-6">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <router-link
                    :to="`/orders/${request.order_id}`"
                    class="text-lg font-semibold text-gray-900 hover:text-primary-600"
                  >
                    Order #{{ request.order_id }}
                  </router-link>
                  <span
                    :class="getStatusBadgeClass(request.status)"
                    class="px-2 py-1 rounded-full text-xs font-medium"
                  >
                    {{ formatStatus(request.status) }}
                  </span>
                  <span
                    v-if="request.type === 'order_request'"
                    class="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-700"
                  >
                    Order Request
                  </span>
                  <span
                    v-else
                    class="px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-700"
                  >
                    Writer Request
                  </span>
                </div>
                
                <p class="text-gray-900 font-medium mb-2">{{ request.order_topic }}</p>
                
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4 text-sm">
                  <div>
                    <span class="text-gray-500">Pages:</span>
                    <span class="ml-2 font-medium text-gray-900">{{ request.order_pages }}</span>
                  </div>
                  <div>
                    <span class="text-gray-500">Price:</span>
                    <span class="ml-2 font-medium text-green-600">${{ formatCurrency(request.order_price) }}</span>
                  </div>
                  <div>
                    <span class="text-gray-500">Order Status:</span>
                    <span class="ml-2 font-medium text-gray-900 capitalize">{{ request.order_status }}</span>
                  </div>
                  <div>
                    <span class="text-gray-500">Requested:</span>
                    <span class="ml-2 font-medium text-gray-900">{{ formatDate(request.requested_at) }}</span>
                  </div>
                </div>

                <div v-if="request.reviewed_by" class="mt-3 text-sm text-gray-600">
                  Reviewed by: <span class="font-medium">{{ request.reviewed_by }}</span>
                  <span v-if="request.reviewed_at" class="ml-2">
                    on {{ formatDate(request.reviewed_at) }}
                  </span>
                </div>
              </div>

              <div class="flex flex-col gap-2 ml-4">
                <router-link
                  :to="`/orders/${request.order_id}`"
                  class="btn btn-secondary text-sm whitespace-nowrap"
                >
                  View Order
                </router-link>
                <button
                  v-if="request.status === 'pending'"
                  @click="cancelRequest(request)"
                  class="btn btn-warning text-sm whitespace-nowrap"
                >
                  Cancel Request
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import writerDashboardAPI from '@/api/writer-dashboard'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const router = useRouter()
const { error: showError, warning: showWarning } = useToast()

const loading = ref(false)
const requestData = ref(null)
const filterStatus = ref('all')
const lastUpdated = ref(null)

const filteredRequests = computed(() => {
  if (!requestData.value || !requestData.value.requests) return []
  
  if (filterStatus.value === 'all') {
    return requestData.value.requests
  }
  
  return requestData.value.requests.filter(r => r.status === filterStatus.value)
})

const loadRequests = async () => {
  loading.value = true
  try {
    const response = await writerDashboardAPI.getOrderRequests()
    requestData.value = response.data
    lastUpdated.value = response.data.last_updated
  } catch (error) {
    console.error('Failed to load order requests:', error)
    const errorMsg = getErrorMessage(error, 'Failed to load order requests. Please try again.')
    showError(errorMsg)
  } finally {
    loading.value = false
  }
}

const cancelRequest = async (request) => {
  if (!confirm(`Are you sure you want to cancel your request for Order #${request.order_id}?`)) {
    return
  }
  
  // TODO: Implement cancel request API call
  showWarning('Cancel request functionality coming soon.')
}

const formatStatus = (status) => {
  const statusMap = {
    'pending': 'Pending',
    'approved': 'Approved',
    'accepted': 'Accepted',
    'rejected': 'Rejected',
  }
  return statusMap[status] || status
}

const getStatusBadgeClass = (status) => {
  const classes = {
    'pending': 'bg-yellow-100 text-yellow-700',
    'approved': 'bg-green-100 text-green-700',
    'accepted': 'bg-green-100 text-green-700',
    'rejected': 'bg-red-100 text-red-700',
  }
  return classes[status] || 'bg-gray-100 text-gray-700'
}

const formatDate = (dateString) => {
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

const formatTime = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toFixed(2)
}

onMounted(() => {
  loadRequests()
  
  // Auto-refresh every 30 seconds for real-time updates
  setInterval(() => {
    loadRequests()
  }, 30000)
})
</script>

<style scoped>
/* Styles are applied via Tailwind classes directly in template */
</style>


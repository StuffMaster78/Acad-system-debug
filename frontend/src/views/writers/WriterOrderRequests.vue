<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
          <div class="space-y-2">
            <h1 class="text-3xl sm:text-4xl font-bold text-gray-900 tracking-tight">
              Order Request Status
            </h1>
            <p class="text-base text-gray-600 leading-relaxed max-w-2xl">
              Track your order requests and their approval status
            </p>
          </div>
          <div class="flex items-center gap-3">
            <span
              v-if="lastUpdated"
              class="text-xs font-medium text-gray-500 hidden sm:block"
            >
              Updated: {{ formatTime(lastUpdated) }}
            </span>
            <button
              @click="loadRequests"
              :disabled="loading"
              class="inline-flex items-center justify-center px-5 py-2.5 bg-white border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm"
            >
              {{ loading ? 'Loading...' : 'Refresh' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Statistics -->
      <div v-if="requestData" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5 mb-8">
        <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl shadow-md p-6 border-l-4 border-blue-600 hover:shadow-lg transition-shadow">
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-blue-700 uppercase tracking-wide mb-2">
                Total Requests
              </p>
              <p class="text-3xl sm:text-4xl font-bold text-blue-900">
                {{ requestData.statistics.total || 0 }}
              </p>
            </div>
            <div class="ml-4 shrink-0">
              <div class="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                <span class="text-2xl">📊</span>
              </div>
            </div>
          </div>
        </div>
        <div class="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-xl shadow-md p-6 border-l-4 border-yellow-600 hover:shadow-lg transition-shadow">
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-yellow-700 uppercase tracking-wide mb-2">
                Pending
              </p>
              <p class="text-3xl sm:text-4xl font-bold text-yellow-900">
                {{ requestData.statistics.pending || 0 }}
              </p>
            </div>
            <div class="ml-4 shrink-0">
              <div class="w-12 h-12 bg-yellow-600 rounded-lg flex items-center justify-center">
                <span class="text-2xl">⏳</span>
              </div>
            </div>
          </div>
        </div>
        <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-xl shadow-md p-6 border-l-4 border-green-600 hover:shadow-lg transition-shadow">
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-green-700 uppercase tracking-wide mb-2">
                Approved
              </p>
              <p class="text-3xl sm:text-4xl font-bold text-green-900">
                {{ requestData.statistics.approved || 0 }}
              </p>
            </div>
            <div class="ml-4 shrink-0">
              <div class="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center">
                <span class="text-2xl">✅</span>
              </div>
            </div>
          </div>
        </div>
        <div class="bg-gradient-to-br from-red-50 to-red-100 rounded-xl shadow-md p-6 border-l-4 border-red-600 hover:shadow-lg transition-shadow">
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-red-700 uppercase tracking-wide mb-2">
                Rejected
              </p>
              <p class="text-3xl sm:text-4xl font-bold text-red-900">
                {{ requestData.statistics.rejected || 0 }}
              </p>
            </div>
            <div class="ml-4 shrink-0">
              <div class="w-12 h-12 bg-red-600 rounded-lg flex items-center justify-center">
                <span class="text-2xl">❌</span>
              </div>
            </div>
          </div>
        </div>
        <div
          v-if="requestData.statistics.recent_7_days !== undefined"
          class="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-xl shadow-md p-6 border-l-4 border-indigo-600 hover:shadow-lg transition-shadow"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1 min-w-0">
              <p class="text-sm font-semibold text-indigo-700 uppercase tracking-wide mb-2">
                Recent (7 days)
              </p>
              <p class="text-3xl sm:text-4xl font-bold text-indigo-900">
                {{ requestData.statistics.recent_7_days || 0 }}
              </p>
            </div>
            <div class="ml-4 shrink-0">
              <div class="w-12 h-12 bg-indigo-600 rounded-lg flex items-center justify-center">
                <span class="text-2xl">📅</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Requests List -->
      <div v-if="loading" class="bg-white rounded-xl shadow-sm p-16">
        <div class="flex flex-col items-center justify-center gap-4">
          <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-200 border-t-primary-600"></div>
          <p class="text-sm font-medium text-gray-500">Loading requests...</p>
        </div>
      </div>

      <div
        v-else-if="requestData && requestData.requests.length === 0"
        class="bg-white rounded-xl shadow-sm p-16 text-center"
      >
        <div class="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gray-100 mb-6">
          <span class="text-4xl">📭</span>
        </div>
        <p class="text-lg font-semibold text-gray-900 mb-2">
          No order requests found
        </p>
        <p class="text-sm text-gray-500 mb-6 max-w-md mx-auto">
          Request orders from the order queue to see them here.
        </p>
        <router-link
          to="/writer/queue"
          class="inline-flex items-center justify-center px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 transition-all shadow-md hover:shadow-lg"
        >
          View Order Queue
        </router-link>
      </div>

      <div v-else-if="requestData" class="space-y-6">
        <!-- Filter Tabs -->
        <div class="bg-white rounded-xl shadow-md p-4">
          <div class="flex flex-wrap gap-3">
            <button
              @click="filterStatus = 'all'"
              :class="[
                'px-5 py-2.5 rounded-lg text-sm font-bold transition-all shadow-sm',
                filterStatus === 'all'
                  ? 'bg-primary-600 text-white shadow-md'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
            >
              All
              <span
                class="ml-2 px-2 py-0.5 rounded-full text-xs font-bold"
                :class="filterStatus === 'all' ? 'bg-primary-700 text-white' : 'bg-gray-200 text-gray-700'"
              >
                {{ requestData.statistics.total }}
              </span>
            </button>
            <button
              @click="filterStatus = 'pending'"
              :class="[
                'px-5 py-2.5 rounded-lg text-sm font-bold transition-all shadow-sm',
                filterStatus === 'pending'
                  ? 'bg-yellow-600 text-white shadow-md'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
            >
              Pending
              <span
                class="ml-2 px-2 py-0.5 rounded-full text-xs font-bold"
                :class="filterStatus === 'pending' ? 'bg-yellow-700 text-white' : 'bg-gray-200 text-gray-700'"
              >
                {{ requestData.statistics.pending }}
              </span>
            </button>
            <button
              @click="filterStatus = 'approved'"
              :class="[
                'px-5 py-2.5 rounded-lg text-sm font-bold transition-all shadow-sm',
                filterStatus === 'approved'
                  ? 'bg-green-600 text-white shadow-md'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
            >
              Approved
              <span
                class="ml-2 px-2 py-0.5 rounded-full text-xs font-bold"
                :class="filterStatus === 'approved' ? 'bg-green-700 text-white' : 'bg-gray-200 text-gray-700'"
              >
                {{ requestData.statistics.approved }}
              </span>
            </button>
            <button
              @click="filterStatus = 'rejected'"
              :class="[
                'px-5 py-2.5 rounded-lg text-sm font-bold transition-all shadow-sm',
                filterStatus === 'rejected'
                  ? 'bg-red-600 text-white shadow-md'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              ]"
            >
              Rejected
              <span
                class="ml-2 px-2 py-0.5 rounded-full text-xs font-bold"
                :class="filterStatus === 'rejected' ? 'bg-red-700 text-white' : 'bg-gray-200 text-gray-700'"
              >
                {{ requestData.statistics.rejected }}
              </span>
            </button>
          </div>
        </div>

        <!-- Requests -->
        <div class="space-y-5">
          <div
            v-for="request in filteredRequests"
            :key="`${request.type}-${request.id}`"
            class="bg-white rounded-xl shadow-md border-2 border-gray-200 hover:shadow-lg transition-all"
          >
            <div class="p-6 sm:p-8">
              <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
                <div class="flex-1 min-w-0">
                  <div class="flex flex-wrap items-center gap-3 mb-4">
                    <router-link
                      :to="`/orders/${request.order_id}`"
                      class="text-xl font-bold text-gray-900 hover:text-primary-600 transition-colors"
                    >
                      Order #{{ request.order_id }}
                    </router-link>
                    <span
                      :class="getStatusBadgeClass(request.status)"
                      class="px-3 py-1.5 rounded-full text-xs font-bold uppercase tracking-wide"
                    >
                      {{ formatStatus(request.status) }}
                    </span>
                    <span
                      v-if="request.type === 'order_request'"
                      class="px-3 py-1.5 rounded-full text-xs font-bold bg-blue-100 text-blue-700 uppercase tracking-wide"
                    >
                      Order Request
                    </span>
                    <span
                      v-else
                      class="px-3 py-1.5 rounded-full text-xs font-bold bg-purple-100 text-purple-700 uppercase tracking-wide"
                    >
                      Writer Request
                    </span>
                  </div>
                  
                  <p class="text-base font-bold text-gray-900 mb-4 line-clamp-2">
                    {{ request.order_topic }}
                  </p>
                  
                  <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
                    <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                      <p class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">
                        Pages
                      </p>
                      <p class="text-sm font-bold text-gray-900">
                        {{ request.order_pages }}
                      </p>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                      <p class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">
                        Price
                      </p>
                      <p class="text-sm font-bold text-green-600 truncate">
                        ${{ formatCurrency(request.order_price) }}
                      </p>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                      <p class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">
                        Order Status
                      </p>
                      <p class="text-sm font-semibold text-gray-900 capitalize line-clamp-1">
                        {{ request.order_status }}
                      </p>
                    </div>
                    <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                      <p class="text-xs font-bold text-gray-500 uppercase tracking-wide mb-1">
                        Requested
                      </p>
                      <p class="text-xs font-semibold text-gray-900 line-clamp-1">
                        {{ formatDate(request.requested_at) }}
                      </p>
                    </div>
                  </div>

                  <div
                    v-if="request.reason"
                    class="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200"
                  >
                    <p class="text-xs font-bold text-gray-600 uppercase tracking-wide mb-2">
                      Your Request Reason:
                    </p>
                    <p class="text-sm text-gray-700 leading-relaxed">
                      {{ request.reason }}
                    </p>
                  </div>
                  
                  <div
                    v-if="request.type === 'writer_request' && (request.additional_pages || request.additional_slides)"
                    class="mt-4 p-4 bg-blue-50 rounded-lg border-2 border-blue-200"
                  >
                    <p class="text-xs font-bold text-blue-700 uppercase tracking-wide mb-2">
                      Additional Request:
                    </p>
                    <p class="text-sm font-semibold text-blue-900 mb-2">
                      <span v-if="request.additional_pages">
                        {{ request.additional_pages }} additional page{{ request.additional_pages !== 1 ? 's' : '' }}
                      </span>
                      <span
                        v-if="request.additional_pages && request.additional_slides"
                        class="mx-2"
                      >
                        +
                      </span>
                      <span v-if="request.additional_slides">
                        {{ request.additional_slides }} additional slide{{ request.additional_slides !== 1 ? 's' : '' }}
                      </span>
                    </p>
                    <p
                      v-if="request.has_counter_offer"
                      class="text-xs font-bold text-orange-700 mt-2 flex items-center gap-1"
                    >
                      <span>⚠️</span>
                      <span>Client has made a counter offer</span>
                    </p>
                  </div>
                  
                  <div
                    v-if="request.reviewed_by"
                    class="mt-4 pt-4 border-t border-gray-200"
                  >
                    <p class="text-sm font-medium text-gray-600">
                      Reviewed by:
                      <span class="font-bold text-gray-900">{{ request.reviewed_by }}</span>
                      <span
                        v-if="request.reviewed_at"
                        class="ml-2 text-gray-500"
                      >
                        on {{ formatDate(request.reviewed_at) }}
                      </span>
                    </p>
                  </div>
                </div>

                <div class="flex flex-col gap-3 lg:ml-6 lg:shrink-0">
                  <router-link
                    :to="`/orders/${request.order_id}`"
                    class="inline-flex items-center justify-center px-5 py-2.5 bg-white border border-gray-300 text-gray-700 font-semibold rounded-lg hover:bg-gray-50 transition-all shadow-sm text-sm whitespace-nowrap"
                  >
                    View Order
                  </router-link>
                  <button
                    v-if="request.status === 'pending'"
                    @click="cancelRequest(request)"
                    :disabled="cancelingRequestId === request.id"
                    class="inline-flex items-center justify-center px-5 py-2.5 bg-yellow-600 text-white font-semibold rounded-lg hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md text-sm whitespace-nowrap"
                  >
                    {{ cancelingRequestId === request.id ? 'Cancelling...' : 'Cancel Request' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Confirmation Dialog -->
  <ConfirmationDialog
    v-model:show="confirm.show"
    :title="confirm.title"
    :message="confirm.message"
    :details="confirm.details"
    :variant="confirm.variant"
    :confirm-text="confirm.confirmText"
    :cancel-text="confirm.cancelText"
    :icon="confirm.icon"
    @confirm="confirm.onConfirm"
    @cancel="confirm.onCancel"
  />
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import writerDashboardAPI from '@/api/writer-dashboard'
import writerOrderRequestsAPI from '@/api/writer-order-requests'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { getErrorMessage } from '@/utils/errorHandler'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const router = useRouter()
const { error: showError, warning: showWarning, success: showSuccess } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const requestData = ref(null)
const filterStatus = ref('all')
const lastUpdated = ref(null)
const cancelingRequestId = ref(null)

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
    const errorMsg = getErrorMessage(error, 'Failed to load order requests. Please try again.')
    showError(errorMsg)
  } finally {
    loading.value = false
  }
}

const cancelRequest = async (request) => {
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to cancel your request for Order #${request.order_id}? This action cannot be undone.`,
    'Cancel Order Request'
  )
  
  if (!confirmed) {
    return
  }
  
  cancelingRequestId.value = request.id
  try {
    await writerOrderRequestsAPI.delete(request.id)
    showSuccess('Order request cancelled successfully')
    await loadRequests()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to cancel order request. Please try again.')
    showError(errorMsg)
  } finally {
    cancelingRequestId.value = null
  }
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


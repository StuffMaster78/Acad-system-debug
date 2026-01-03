<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="mb-10">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-6">
          <div class="space-y-3">
            <h1 class="text-4xl sm:text-5xl font-extrabold text-gray-900 tracking-tight bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
              Order Request Status
            </h1>
            <p class="text-base sm:text-lg text-gray-600 leading-relaxed max-w-2xl">
              Track your order requests and their approval status in real-time
            </p>
          </div>
          <div class="flex items-center gap-4">
            <span
              v-if="lastUpdated"
              class="text-sm font-medium text-gray-500 hidden sm:flex items-center gap-2"
            >
              <ClockIcon class="w-4 h-4" />
              Updated: {{ formatTime(lastUpdated) }}
            </span>
            <button
              @click="loadRequests"
              :disabled="loading"
              class="inline-flex items-center justify-center gap-2 px-6 py-3 bg-white border-2 border-gray-200 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 hover:border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm hover:shadow-md transform hover:-translate-y-0.5"
            >
              <ArrowPathIcon :class="['w-5 h-5', loading && 'animate-spin']" />
              <span>{{ loading ? 'Refreshing...' : 'Refresh' }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Statistics -->
      <div v-if="requestData" class="space-y-5 mb-10">
        <!-- First Row: Main Metrics (3 cards) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          <!-- Total Requests Card -->
          <div class="group relative bg-white rounded-2xl shadow-lg p-5 border-l-4 border-blue-500 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 overflow-hidden">
            <div class="absolute inset-0 bg-gradient-to-br from-blue-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div class="relative flex items-center justify-between">
              <div class="flex-1 min-w-0">
                <p class="text-xs font-bold text-blue-600 uppercase tracking-wider mb-2">
                  Total Requests
                </p>
                <p class="text-4xl font-extrabold text-blue-900">
                  {{ requestData.statistics.total || 0 }}
                </p>
              </div>
              <div class="ml-4 shrink-0">
                <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
                  <ChartBarIcon class="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          </div>

          <!-- Pending Card -->
          <div class="group relative bg-white rounded-2xl shadow-lg p-5 border-l-4 border-amber-500 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 overflow-hidden">
            <div class="absolute inset-0 bg-gradient-to-br from-amber-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div class="relative flex items-center justify-between">
              <div class="flex-1 min-w-0">
                <p class="text-xs font-bold text-amber-600 uppercase tracking-wider mb-2">
                  Pending
                </p>
                <p class="text-4xl font-extrabold text-amber-900">
                  {{ requestData.statistics.pending || 0 }}
                </p>
              </div>
              <div class="ml-4 shrink-0">
                <div class="w-12 h-12 bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
                  <ClockIcon class="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          </div>

          <!-- Approved Card -->
          <div class="group relative bg-white rounded-2xl shadow-lg p-5 border-l-4 border-emerald-500 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 overflow-hidden">
            <div class="absolute inset-0 bg-gradient-to-br from-emerald-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div class="relative flex items-center justify-between">
              <div class="flex-1 min-w-0">
                <p class="text-xs font-bold text-emerald-600 uppercase tracking-wider mb-2">
                  Approved
                </p>
                <p class="text-4xl font-extrabold text-emerald-900">
                  {{ requestData.statistics.approved || 0 }}
                </p>
              </div>
              <div class="ml-4 shrink-0">
                <div class="w-12 h-12 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
                  <CheckCircleIcon class="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Second Row: Secondary Metrics (2 cards) -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <!-- Rejected Card -->
          <div class="group relative bg-white rounded-2xl shadow-lg p-5 border-l-4 border-red-500 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 overflow-hidden">
            <div class="absolute inset-0 bg-gradient-to-br from-red-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div class="relative flex items-center justify-between">
              <div class="flex-1 min-w-0">
                <p class="text-xs font-bold text-red-600 uppercase tracking-wider mb-2">
                  Rejected
                </p>
                <p class="text-4xl font-extrabold text-red-900">
                  {{ requestData.statistics.rejected || 0 }}
                </p>
              </div>
              <div class="ml-4 shrink-0">
                <div class="w-12 h-12 bg-gradient-to-br from-red-500 to-red-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
                  <XCircleIcon class="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          </div>

          <!-- Recent (7 Days) Card -->
          <div
            v-if="requestData.statistics.recent_7_days !== undefined"
            class="group relative bg-white rounded-2xl shadow-lg p-5 border-l-4 border-indigo-500 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 overflow-hidden"
          >
            <div class="absolute inset-0 bg-gradient-to-br from-indigo-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
            <div class="relative flex items-center justify-between">
              <div class="flex-1 min-w-0">
                <p class="text-xs font-bold text-indigo-600 uppercase tracking-wider mb-2">
                  Recent (7 days)
                </p>
                <p class="text-4xl font-extrabold text-indigo-900">
                  {{ requestData.statistics.recent_7_days || 0 }}
                </p>
              </div>
              <div class="ml-4 shrink-0">
                <div class="w-12 h-12 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
                  <CalendarDaysIcon class="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Requests List -->
      <div v-if="loading" class="bg-white rounded-2xl shadow-lg p-20 border border-gray-100">
        <div class="flex flex-col items-center justify-center gap-5">
          <div class="relative">
            <div class="animate-spin rounded-full h-16 w-16 border-4 border-primary-100 border-t-primary-600"></div>
            <div class="absolute inset-0 animate-ping rounded-full h-16 w-16 border-4 border-primary-200 opacity-20"></div>
          </div>
          <p class="text-base font-semibold text-gray-600">Loading requests...</p>
        </div>
      </div>

      <div
        v-else-if="requestData && requestData.requests.length === 0"
        class="bg-white rounded-2xl shadow-lg p-16 text-center border border-gray-100"
      >
        <div class="inline-flex items-center justify-center w-24 h-24 rounded-2xl bg-gradient-to-br from-gray-100 to-gray-50 mb-6 shadow-inner">
          <InboxIcon class="w-12 h-12 text-gray-400" />
        </div>
        <p class="text-xl font-bold text-gray-900 mb-3">
          No order requests found
        </p>
        <p class="text-sm text-gray-500 mb-8 max-w-md mx-auto leading-relaxed">
          Request orders from the order queue to see them here. Start by browsing available orders and submitting your requests.
        </p>
        <router-link
          to="/writer/queue"
          class="inline-flex items-center justify-center gap-2 px-8 py-3.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-bold rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
        >
          <ClipboardDocumentListIcon class="w-5 h-5" />
          View Order Queue
        </router-link>
      </div>

      <div v-else-if="requestData" class="space-y-6">
        <!-- Filter Tabs -->
        <div class="bg-white rounded-2xl shadow-lg p-5 border border-gray-100">
          <div class="flex flex-wrap gap-3">
            <button
              @click="filterStatus = 'all'"
              :class="[
                'px-6 py-3 rounded-xl text-sm font-bold transition-all duration-200 flex items-center gap-2',
                filterStatus === 'all'
                  ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg transform scale-105'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200 hover:shadow-md'
              ]"
            >
              All
              <span
                class="px-2.5 py-1 rounded-full text-xs font-extrabold"
                :class="filterStatus === 'all' ? 'bg-white/20 text-white' : 'bg-gray-200 text-gray-700'"
              >
                {{ requestData.statistics.total }}
              </span>
            </button>
            <button
              @click="filterStatus = 'pending'"
              :class="[
                'px-6 py-3 rounded-xl text-sm font-bold transition-all duration-200 flex items-center gap-2',
                filterStatus === 'pending'
                  ? 'bg-gradient-to-r from-amber-500 to-amber-600 text-white shadow-lg transform scale-105'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200 hover:shadow-md'
              ]"
            >
              Pending
              <span
                class="px-2.5 py-1 rounded-full text-xs font-extrabold"
                :class="filterStatus === 'pending' ? 'bg-white/20 text-white' : 'bg-gray-200 text-gray-700'"
              >
                {{ requestData.statistics.pending }}
              </span>
            </button>
            <button
              @click="filterStatus = 'approved'"
              :class="[
                'px-6 py-3 rounded-xl text-sm font-bold transition-all duration-200 flex items-center gap-2',
                filterStatus === 'approved'
                  ? 'bg-gradient-to-r from-emerald-500 to-emerald-600 text-white shadow-lg transform scale-105'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200 hover:shadow-md'
              ]"
            >
              Approved
              <span
                class="px-2.5 py-1 rounded-full text-xs font-extrabold"
                :class="filterStatus === 'approved' ? 'bg-white/20 text-white' : 'bg-gray-200 text-gray-700'"
              >
                {{ requestData.statistics.approved }}
              </span>
            </button>
            <button
              @click="filterStatus = 'rejected'"
              :class="[
                'px-6 py-3 rounded-xl text-sm font-bold transition-all duration-200 flex items-center gap-2',
                filterStatus === 'rejected'
                  ? 'bg-gradient-to-r from-red-500 to-red-600 text-white shadow-lg transform scale-105'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200 hover:shadow-md'
              ]"
            >
              Rejected
              <span
                class="px-2.5 py-1 rounded-full text-xs font-extrabold"
                :class="filterStatus === 'rejected' ? 'bg-white/20 text-white' : 'bg-gray-200 text-gray-700'"
              >
                {{ requestData.statistics.rejected }}
              </span>
            </button>
          </div>
        </div>

        <!-- Requests -->
        <div class="space-y-6">
          <div
            v-for="request in filteredRequests"
            :key="`${request.type}-${request.id}`"
            class="group bg-white rounded-2xl shadow-lg border border-gray-200 hover:shadow-2xl hover:border-gray-300 transition-all duration-300 overflow-hidden"
          >
            <div class="p-6 sm:p-8">
              <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
                <div class="flex-1 min-w-0">
                  <div class="flex flex-wrap items-center gap-3 mb-5">
                    <router-link
                      :to="`/orders/${request.order_id}`"
                      class="text-2xl font-extrabold text-gray-900 hover:text-primary-600 transition-colors group-hover:text-primary-600"
                    >
                      Order #{{ request.order_id }}
                    </router-link>
                    <span
                      :class="getStatusBadgeClass(request.status)"
                      class="px-4 py-2 rounded-xl text-xs font-extrabold uppercase tracking-wider shadow-sm"
                    >
                      {{ formatStatus(request.status) }}
                    </span>
                    <span
                      v-if="request.type === 'order_request'"
                      class="px-4 py-2 rounded-xl text-xs font-extrabold bg-gradient-to-r from-blue-100 to-blue-200 text-blue-700 uppercase tracking-wider shadow-sm border border-blue-300"
                    >
                      Order Request
                    </span>
                    <span
                      v-else
                      class="px-4 py-2 rounded-xl text-xs font-extrabold bg-gradient-to-r from-purple-100 to-purple-200 text-purple-700 uppercase tracking-wider shadow-sm border border-purple-300"
                    >
                      Writer Request
                    </span>
                  </div>
                  
                  <p class="text-lg font-bold text-gray-900 mb-5 line-clamp-2 leading-relaxed">
                    {{ request.order_topic }}
                  </p>
                  
                  <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
                    <div class="bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl p-4 border border-gray-200 hover:shadow-md transition-shadow">
                      <p class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">
                        Pages
                      </p>
                      <p class="text-lg font-extrabold text-gray-900">
                        {{ request.order_pages }}
                      </p>
                    </div>
                    <div class="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl p-4 border border-emerald-200 hover:shadow-md transition-shadow">
                      <p class="text-xs font-bold text-emerald-600 uppercase tracking-wider mb-2">
                        Price
                      </p>
                      <p class="text-lg font-extrabold text-emerald-700 truncate">
                        ${{ formatCurrency(request.order_price) }}
                      </p>
                    </div>
                    <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 border border-blue-200 hover:shadow-md transition-shadow">
                      <p class="text-xs font-bold text-blue-600 uppercase tracking-wider mb-2">
                        Order Status
                      </p>
                      <p class="text-sm font-bold text-blue-900 capitalize line-clamp-1">
                        {{ request.order_status }}
                      </p>
                    </div>
                    <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4 border border-purple-200 hover:shadow-md transition-shadow">
                      <p class="text-xs font-bold text-purple-600 uppercase tracking-wider mb-2">
                        Requested
                      </p>
                      <p class="text-xs font-bold text-purple-900 line-clamp-1">
                        {{ formatDate(request.requested_at) }}
                      </p>
                    </div>
                  </div>

                  <div
                    v-if="request.reason"
                    class="mt-4 p-5 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl border-2 border-gray-200 shadow-sm"
                  >
                    <p class="text-xs font-bold text-gray-600 uppercase tracking-wider mb-3 flex items-center gap-2">
                      <span class="w-1.5 h-1.5 rounded-full bg-gray-400"></span>
                      Your Request Reason
                    </p>
                    <p class="text-sm text-gray-700 leading-relaxed font-medium">
                      {{ request.reason }}
                    </p>
                  </div>
                  
                  <div
                    v-if="request.type === 'writer_request' && (request.additional_pages || request.additional_slides)"
                    class="mt-4 p-5 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl border-2 border-blue-300 shadow-sm"
                  >
                    <p class="text-xs font-bold text-blue-700 uppercase tracking-wider mb-3 flex items-center gap-2">
                      <span class="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                      Additional Request
                    </p>
                    <p class="text-sm font-bold text-blue-900 mb-2">
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
                      class="text-xs font-bold text-orange-700 mt-3 flex items-center gap-2 px-3 py-2 bg-orange-50 rounded-lg border border-orange-200"
                    >
                      <ExclamationTriangleIcon class="w-4 h-4" />
                      <span>Client has made a counter offer</span>
                    </p>
                  </div>
                  
                  <div
                    v-if="request.reviewed_by"
                    class="mt-5 pt-5 border-t-2 border-gray-200"
                  >
                    <p class="text-sm font-semibold text-gray-600 flex items-center gap-2">
                      <span class="text-gray-400">Reviewed by:</span>
                      <span class="font-bold text-gray-900">{{ request.reviewed_by }}</span>
                      <span
                        v-if="request.reviewed_at"
                        class="ml-2 text-gray-500 text-xs"
                      >
                        on {{ formatDate(request.reviewed_at) }}
                      </span>
                    </p>
                  </div>
                </div>

                <div class="flex flex-col gap-3 lg:ml-6 lg:shrink-0">
                  <button
                    @click="viewOrder(request.order_id)"
                    class="inline-flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white font-bold rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all shadow-md hover:shadow-lg text-sm whitespace-nowrap transform hover:-translate-y-0.5"
                  >
                    <EyeIcon class="w-4 h-4" />
                    View Order Details
                  </button>
                  <button
                    v-if="request.status === 'pending'"
                    @click="cancelRequest(request)"
                    :disabled="cancelingRequestId === request.id"
                    class="inline-flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-amber-500 to-amber-600 text-white font-bold rounded-xl hover:from-amber-600 hover:to-amber-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg text-sm whitespace-nowrap transform hover:-translate-y-0.5"
                  >
                    <XMarkIcon class="w-4 h-4" />
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
    v-model:show="confirmShow"
    :title="confirmTitle"
    :message="confirmMessage"
    :details="confirmDetails"
    :variant="confirmVariant"
    :confirm-text="confirmConfirmText"
    :cancel-text="confirmCancelText"
    :icon="confirmIcon"
    @confirm="confirm.onConfirm"
    @cancel="confirm.onCancel"
  />
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import {
  ClockIcon,
  ArrowPathIcon,
  ChartBarIcon,
  CheckCircleIcon,
  XCircleIcon,
  CalendarDaysIcon,
  InboxIcon,
  ClipboardDocumentListIcon,
  EyeIcon,
  XMarkIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'
import writerDashboardAPI from '@/api/writer-dashboard'
import writerOrderRequestsAPI from '@/api/writer-order-requests'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { getErrorMessage } from '@/utils/errorHandler'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const router = useRouter()
const { error: showError, warning: showWarning, success: showSuccess } = useToast()
const confirm = useConfirmDialog()

// Computed properties to unwrap refs for ConfirmationDialog
const confirmShow = computed({
  get: () => confirm.show.value,
  set: (val) => { confirm.show.value = val }
})
const confirmTitle = computed(() => confirm.title.value)
const confirmMessage = computed(() => confirm.message.value)
const confirmDetails = computed(() => confirm.details.value)
const confirmVariant = computed(() => confirm.variant.value)
const confirmConfirmText = computed(() => confirm.confirmText.value)
const confirmCancelText = computed(() => confirm.cancelText.value)
const confirmIcon = computed(() => confirm.icon.value)

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

const viewOrder = (orderId) => {
  if (!orderId) {
    showError('Invalid order ID')
    return
  }
  router.push(`/orders/${orderId}`)
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
    'pending': 'bg-gradient-to-r from-amber-100 to-amber-200 text-amber-800 border border-amber-300',
    'approved': 'bg-gradient-to-r from-emerald-100 to-emerald-200 text-emerald-800 border border-emerald-300',
    'accepted': 'bg-gradient-to-r from-emerald-100 to-emerald-200 text-emerald-800 border border-emerald-300',
    'rejected': 'bg-gradient-to-r from-red-100 to-red-200 text-red-800 border border-red-300',
  }
  return classes[status] || 'bg-gradient-to-r from-gray-100 to-gray-200 text-gray-700 border border-gray-300'
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


<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6 py-4">
    <PageHeader
      title="Payment Requests"
      subtitle="Manage writer payment requests - approve, reject, or process payments"
      @refresh="loadPaymentRequests"
    />

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg shadow border border-yellow-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
        <p class="text-xs font-medium text-yellow-700 truncate">Pending Requests</p>
        <p class="text-base sm:text-lg lg:text-xl font-bold text-yellow-900 break-all leading-tight">{{ summary.pending || 0 }}</p>
        <p class="text-xs text-yellow-600">awaiting review</p>
      </div>
      <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-lg shadow border border-green-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
        <p class="text-xs font-medium text-green-700 truncate">Approved</p>
        <p class="text-base sm:text-lg lg:text-xl font-bold text-green-900 break-all leading-tight">{{ summary.approved || 0 }}</p>
        <p class="text-xs text-green-600">approved requests</p>
      </div>
      <div class="bg-gradient-to-br from-red-50 to-red-100 rounded-lg shadow border border-red-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
        <p class="text-xs font-medium text-red-700 truncate">Rejected</p>
        <p class="text-base sm:text-lg lg:text-xl font-bold text-red-900 break-all leading-tight">{{ summary.rejected || 0 }}</p>
        <p class="text-xs text-red-600">rejected requests</p>
      </div>
      <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg shadow border border-blue-200 p-4 min-w-0 overflow-hidden h-24 flex flex-col justify-between">
        <p class="text-xs font-medium text-blue-700 truncate">Total Amount</p>
        <p class="text-base sm:text-lg lg:text-xl font-bold text-blue-900 break-all leading-tight">${{ formatCurrency(summary.total_amount || 0) }}</p>
        <p class="text-xs text-blue-600">all requests</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white p-4 rounded-lg shadow border border-gray-200">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Website</label>
          <select
            v-model="filters.website_id"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            @change="loadPaymentRequests"
          >
            <option value="">All Websites</option>
            <option v-for="website in websites" :key="website.id" :value="website.id">
              {{ website.name }}
            </option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Status</label>
          <select
            v-model="filters.status"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            @change="loadPaymentRequests"
          >
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="processed">Processed</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Search</label>
          <input
            v-model="filters.search"
            type="text"
            placeholder="Writer email or name..."
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            @input="debouncedSearch"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1.5">Date From</label>
          <input
            v-model="filters.date_from"
            type="date"
            class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            @change="loadPaymentRequests"
          />
        </div>
        <div class="flex items-end">
          <button
            @click="clearFilters"
            class="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors font-medium text-sm"
          >
            Clear Filters
          </button>
        </div>
      </div>
    </div>

    <!-- Payment Requests Table -->
    <div class="bg-white rounded-lg shadow-sm overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else-if="paymentRequests.length === 0" class="text-center py-12 text-gray-500">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="mt-2 text-sm font-medium">No payment requests found</p>
        <p class="mt-1 text-xs text-gray-400">Try adjusting your filters</p>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 text-xs">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-3 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Date</th>
              <th class="px-3 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Writer</th>
              <th class="px-3 py-2 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">Requested</th>
              <th class="px-3 py-2 text-right text-xs font-semibold text-gray-600 uppercase tracking-wider">Available</th>
              <th class="px-3 py-2 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">Status</th>
              <th class="px-3 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Reason</th>
              <th class="px-3 py-2 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">Reviewed By</th>
              <th class="px-3 py-2 text-center text-xs font-semibold text-gray-600 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="request in paymentRequests" :key="request.id" class="hover:bg-gray-50 transition-colors">
              <td class="px-3 py-2 text-xs text-gray-900 font-normal">
                {{ formatDate(request.created_at) }}
              </td>
              <td class="px-3 py-2 text-xs">
                <div class="font-medium text-gray-900">{{ request.writer_wallet?.writer?.username || 'N/A' }}</div>
                <div class="text-gray-500 text-xs">{{ request.writer_wallet?.writer?.email || '' }}</div>
              </td>
              <td class="px-3 py-2 text-xs text-right font-semibold text-gray-900">
                ${{ formatCurrency(request.requested_amount) }}
              </td>
              <td class="px-3 py-2 text-xs text-right font-normal text-gray-600">
                ${{ formatCurrency(request.available_balance) }}
              </td>
              <td class="px-3 py-2 text-xs text-center">
                <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                      :class="getStatusClass(request.status)">
                  {{ request.status }}
                </span>
              </td>
              <td class="px-3 py-2 text-xs text-gray-600 font-normal max-w-xs truncate" :title="request.reason">
                {{ request.reason || '—' }}
              </td>
              <td class="px-3 py-2 text-xs text-gray-600 font-normal">
                <div v-if="request.reviewed_by">
                  <div class="font-medium">{{ request.reviewed_by?.username || 'N/A' }}</div>
                  <div class="text-gray-500 text-xs">{{ formatDate(request.reviewed_at) }}</div>
                </div>
                <span v-else class="text-gray-400">—</span>
              </td>
              <td class="px-3 py-2 text-xs text-center">
                <div class="flex items-center justify-center gap-1">
                  <button
                    v-if="request.status === 'pending'"
                    @click="approveRequest(request)"
                    class="px-2 py-1 bg-green-600 text-white rounded hover:bg-green-700 transition-colors text-xs font-medium"
                    title="Approve Request"
                  >
                    Approve
                  </button>
                  <button
                    v-if="request.status === 'pending'"
                    @click="rejectRequest(request)"
                    class="px-2 py-1 bg-red-600 text-white rounded hover:bg-red-700 transition-colors text-xs font-medium"
                    title="Reject Request"
                  >
                    Reject
                  </button>
                  <button
                    @click="viewDetails(request)"
                    class="px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors text-xs font-medium"
                    title="View Details"
                  >
                    View
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="paymentRequests.length > 0 && pagination.count > pagination.page_size" class="bg-gray-50 px-4 py-3 flex items-center justify-between border-t border-gray-200">
        <div class="flex-1 flex justify-between sm:hidden">
          <button
            @click="previousPage"
            :disabled="!pagination.previous"
            class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <button
            @click="nextPage"
            :disabled="!pagination.next"
            class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
        <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <div>
            <p class="text-sm text-gray-700">
              Showing <span class="font-medium">{{ ((pagination.page - 1) * pagination.page_size) + 1 }}</span>
              to <span class="font-medium">{{ Math.min(pagination.page * pagination.page_size, pagination.count) }}</span>
              of <span class="font-medium">{{ pagination.count }}</span> results
            </p>
          </div>
          <div>
            <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
              <button
                @click="previousPage"
                :disabled="!pagination.previous"
                class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                @click="nextPage"
                :disabled="!pagination.next"
                class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </nav>
          </div>
        </div>
      </div>
    </div>

    <!-- Request Details Modal -->
    <div v-if="showDetailsModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4" @click.self="showDetailsModal = false">
      <div class="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-2xl font-bold">Payment Request Details</h3>
            <button
              @click="showDetailsModal = false"
              class="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div v-if="selectedRequest" class="space-y-4">
            <!-- Writer Info -->
            <div class="bg-gray-50 rounded-lg p-4">
              <h4 class="font-semibold text-gray-900 mb-2">Writer Information</h4>
              <div class="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <span class="text-gray-600">Name:</span>
                  <span class="ml-2 font-medium">{{ selectedRequest.writer_wallet?.writer?.username || 'N/A' }}</span>
                </div>
                <div>
                  <span class="text-gray-600">Email:</span>
                  <span class="ml-2 font-medium">{{ selectedRequest.writer_wallet?.writer?.email || 'N/A' }}</span>
                </div>
              </div>
            </div>

            <!-- Request Details -->
            <div class="bg-blue-50 rounded-lg p-4">
              <h4 class="font-semibold text-gray-900 mb-2">Request Details</h4>
              <div class="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <span class="text-gray-600">Requested Amount:</span>
                  <span class="ml-2 font-semibold text-blue-900">${{ formatCurrency(selectedRequest.requested_amount) }}</span>
                </div>
                <div>
                  <span class="text-gray-600">Available Balance:</span>
                  <span class="ml-2 font-medium">${{ formatCurrency(selectedRequest.available_balance) }}</span>
                </div>
                <div>
                  <span class="text-gray-600">Status:</span>
                  <span class="ml-2">
                    <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium"
                          :class="getStatusClass(selectedRequest.status)">
                      {{ selectedRequest.status }}
                    </span>
                  </span>
                </div>
                <div>
                  <span class="text-gray-600">Created:</span>
                  <span class="ml-2 font-medium">{{ formatDate(selectedRequest.created_at) }}</span>
                </div>
              </div>
            </div>

            <!-- Reason -->
            <div v-if="selectedRequest.reason" class="bg-gray-50 rounded-lg p-4">
              <h4 class="font-semibold text-gray-900 mb-2">Reason</h4>
              <p class="text-sm text-gray-700">{{ selectedRequest.reason }}</p>
            </div>

            <!-- Review Info -->
            <div v-if="selectedRequest.reviewed_by" class="bg-green-50 rounded-lg p-4">
              <h4 class="font-semibold text-gray-900 mb-2">Review Information</h4>
              <div class="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <span class="text-gray-600">Reviewed By:</span>
                  <span class="ml-2 font-medium">{{ selectedRequest.reviewed_by?.username || 'N/A' }}</span>
                </div>
                <div>
                  <span class="text-gray-600">Reviewed At:</span>
                  <span class="ml-2 font-medium">{{ formatDate(selectedRequest.reviewed_at) }}</span>
                </div>
              </div>
              <div v-if="selectedRequest.review_notes" class="mt-2">
                <span class="text-gray-600">Notes:</span>
                <p class="mt-1 text-sm text-gray-700">{{ selectedRequest.review_notes }}</p>
              </div>
            </div>

            <!-- Actions -->
            <div v-if="selectedRequest.status === 'pending'" class="flex gap-2 pt-4 border-t">
              <button
                @click="approveRequest(selectedRequest)"
                class="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
              >
                Approve Request
              </button>
              <button
                @click="rejectRequest(selectedRequest)"
                class="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium"
              >
                Reject Request
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Confirmation Dialog -->
    <ConfirmationDialog
      v-if="showConfirmDialog"
      :show="showConfirmDialog"
      :title="confirmDialog.title"
      :message="confirmDialog.message"
      :confirm-text="confirmDialog.confirmText"
      :cancel-text="confirmDialog.cancelText"
      :type="confirmDialog.type"
      @confirm="handleConfirm"
      @cancel="showConfirmDialog = false"
    />

    <!-- Toast Notifications -->
    <ToastContainer />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { debounce } from '@/utils/debounce'
import PageHeader from '@/components/common/PageHeader.vue'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import ToastContainer from '@/components/common/ToastContainer.vue'
import { useToast } from '@/composables/useToast'
import paymentsAPI from '@/api/payments'
import apiClient from '@/api/client'

const loading = ref(false)
const paymentRequests = ref([])
const websites = ref([])
const showDetailsModal = ref(false)
const selectedRequest = ref(null)
const showConfirmDialog = ref(false)
const confirmDialog = ref({})
const pendingAction = ref(null)

const filters = ref({
  website_id: '',
  status: '',
  search: '',
  date_from: '',
  date_to: '',
})

const pagination = ref({
  page: 1,
  page_size: 50,
  count: 0,
  next: null,
  previous: null,
})

const { showToast } = useToast()

const summary = computed(() => {
  const pending = paymentRequests.value.filter(r => r.status === 'pending').length
  const approved = paymentRequests.value.filter(r => r.status === 'approved').length
  const rejected = paymentRequests.value.filter(r => r.status === 'rejected').length
  const total_amount = paymentRequests.value.reduce((sum, r) => sum + parseFloat(r.requested_amount || 0), 0)
  
  return {
    pending,
    approved,
    rejected,
    total_amount,
  }
})

const loadWebsites = async () => {
  try {
    const response = await apiClient.get('/websites/websites/')
    websites.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load websites:', error)
  }
}

const loadPaymentRequests = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      page_size: pagination.value.page_size,
    }
    
    if (filters.value.website_id) params.website_id = filters.value.website_id
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.date_from) params.date_from = filters.value.date_from
    if (filters.value.date_to) params.date_to = filters.value.date_to
    
    const response = await paymentsAPI.listPaymentRequests(params)
    paymentRequests.value = response.data.results || response.data || []
    
    pagination.value = {
      page: pagination.value.page,
      page_size: pagination.value.page_size,
      count: response.data.count || paymentRequests.value.length,
      next: response.data.next,
      previous: response.data.previous,
    }
  } catch (error) {
    console.error('Failed to load payment requests:', error)
    showToast('Failed to load payment requests', 'error')
    paymentRequests.value = []
  } finally {
    loading.value = false
  }
}

const clearFilters = () => {
  filters.value = {
    website_id: '',
    status: '',
    search: '',
    date_from: '',
    date_to: '',
  }
  pagination.value.page = 1
  loadPaymentRequests()
}

const debouncedSearch = debounce(() => {
  pagination.value.page = 1
  loadPaymentRequests()
}, 500)

const nextPage = () => {
  if (pagination.value.next) {
    pagination.value.page += 1
    loadPaymentRequests()
  }
}

const previousPage = () => {
  if (pagination.value.previous) {
    pagination.value.page -= 1
    loadPaymentRequests()
  }
}

const viewDetails = (request) => {
  selectedRequest.value = request
  showDetailsModal.value = true
}

const approveRequest = (request) => {
  pendingAction.value = { type: 'approve', request }
  confirmDialog.value = {
    title: 'Approve Payment Request',
    message: `Are you sure you want to approve this payment request of $${formatCurrency(request.requested_amount)} for ${request.writer_wallet?.writer?.username || 'this writer'}?`,
    confirmText: 'Approve',
    cancelText: 'Cancel',
    type: 'success',
  }
  showConfirmDialog.value = true
}

const rejectRequest = (request) => {
  pendingAction.value = { type: 'reject', request }
  confirmDialog.value = {
    title: 'Reject Payment Request',
    message: `Are you sure you want to reject this payment request of $${formatCurrency(request.requested_amount)}? You can add a reason for rejection.`,
    confirmText: 'Reject',
    cancelText: 'Cancel',
    type: 'danger',
  }
  showConfirmDialog.value = true
}

const handleConfirm = async () => {
  showConfirmDialog.value = false
  
  if (!pendingAction.value) return
  
  const { type, request } = pendingAction.value
  pendingAction.value = null
  
  try {
    if (type === 'approve') {
      await paymentsAPI.approvePaymentRequest(request.id)
      showToast('Payment request approved successfully', 'success')
    } else if (type === 'reject') {
      await paymentsAPI.rejectPaymentRequest(request.id, {
        review_notes: 'Rejected by admin',
      })
      showToast('Payment request rejected', 'success')
    }
    
    await loadPaymentRequests()
    if (showDetailsModal.value) {
      showDetailsModal.value = false
    }
  } catch (error) {
    console.error(`Failed to ${type} payment request:`, error)
    showToast(`Failed to ${type} payment request`, 'error')
  }
}

const formatCurrency = (amount) => {
  if (!amount) return '0.00'
  return parseFloat(amount).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

const getStatusClass = (status) => {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
    processed: 'bg-blue-100 text-blue-800',
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

onMounted(async () => {
  await Promise.all([loadPaymentRequests(), loadWebsites()])
})
</script>

<style scoped>
@reference "tailwindcss";
</style>


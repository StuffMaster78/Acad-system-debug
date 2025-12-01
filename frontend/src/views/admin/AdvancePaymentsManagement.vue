<template>
  <div class="space-y-6">
    <PageHeader
      title="Advance Payments Management"
      description="Review and manage writer advance payment requests"
    />

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="text-sm text-gray-600 dark:text-gray-400">Pending Requests</div>
        <div class="text-3xl font-bold text-gray-900 dark:text-white">{{ stats.pending || 0 }}</div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="text-sm text-gray-600 dark:text-gray-400">Approved</div>
        <div class="text-3xl font-bold text-green-600 dark:text-green-400">{{ stats.approved || 0 }}</div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="text-sm text-gray-600 dark:text-gray-400">Disbursed</div>
        <div class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ stats.disbursed || 0 }}</div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <div class="text-sm text-gray-600 dark:text-gray-400">Total Outstanding</div>
        <div class="text-3xl font-bold text-orange-600 dark:text-orange-400">
          ${{ formatCurrency(stats.total_outstanding || 0) }}
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label for="filter-status" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Status</label>
          <select
            id="filter-status"
            name="filter-status"
            v-model="filters.status"
            @change="loadRequests"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white"
          >
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="disbursed">Disbursed</option>
            <option value="repaid">Repaid</option>
          </select>
        </div>
        <div>
          <label for="filter-writer" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Writer</label>
          <input
            id="filter-writer"
            name="filter-writer"
            v-model="filters.writer"
            @input="debouncedSearch"
            type="text"
            placeholder="Search by writer..."
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white"
          />
        </div>
        <div>
          <label for="filter-date-from" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Date From</label>
          <input
            id="filter-date-from"
            name="filter-date-from"
            v-model="filters.date_from"
            @change="loadRequests"
            type="date"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white"
          />
        </div>
        <div>
          <label for="filter-date-to" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Date To</label>
          <input
            id="filter-date-to"
            name="filter-date-to"
            v-model="filters.date_to"
            @change="loadRequests"
            type="date"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white"
          />
        </div>
      </div>
    </div>

    <!-- Requests Table -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
      <div v-if="loading" class="p-6 text-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
      </div>
      <div v-else-if="requests.length === 0" class="p-6 text-center text-gray-500 dark:text-gray-400">
        No advance payment requests found
      </div>
      <table v-else class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-700">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Writer</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Requested</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Approved</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Outstanding</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Date</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
          <tr v-for="request in requests" :key="request.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm font-medium text-gray-900 dark:text-white">{{ request.writer_full_name || request.writer_username }}</div>
              <div class="text-sm text-gray-500 dark:text-gray-400">{{ request.writer_email }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
              ${{ formatCurrency(request.requested_amount) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
              <span v-if="request.approved_amount">
                ${{ formatCurrency(request.approved_amount) }}
                <span v-if="request.approved_amount < request.requested_amount" class="text-blue-600 dark:text-blue-400 text-xs">
                  (counteroffer)
                </span>
              </span>
              <span v-else class="text-gray-400">-</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <StatusBadge :status="request.status" />
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
              <span v-if="request.outstanding_amount > 0" class="text-orange-600 dark:text-orange-400">
                ${{ formatCurrency(request.outstanding_amount) }}
              </span>
              <span v-else class="text-gray-400">-</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
              {{ formatDate(request.requested_at) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <div class="flex gap-2">
                <button
                  v-if="request.status === 'pending'"
                  @click="openApproveModal(request)"
                  class="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300"
                >
                  Approve
                </button>
                <button
                  v-if="request.status === 'pending'"
                  @click="openRejectModal(request)"
                  class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                >
                  Reject
                </button>
                <button
                  v-if="request.status === 'approved'"
                  @click="handleDisburse(request)"
                  class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
                >
                  Disburse
                </button>
                <button
                  @click="viewDetails(request)"
                  class="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-300"
                >
                  View
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Approve Modal -->
    <div v-if="showApproveModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full">
        <h3 class="text-xl font-semibold mb-4 dark:text-white">Approve Advance Request</h3>
        <form @submit.prevent="handleApprove" class="space-y-4">
          <div>
            <div class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Requested Amount: ${{ formatCurrency(selectedRequest?.requested_amount || 0) }}
            </div>
          </div>
          <div>
            <label for="approve-amount" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Approved Amount (Counteroffer)
            </label>
            <input
              id="approve-amount"
              name="approve-amount"
              v-model.number="approveForm.approved_amount"
              type="number"
              step="0.01"
              min="0.01"
              :max="selectedRequest?.max_advance_amount || selectedRequest?.requested_amount"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white"
              placeholder="Leave empty to approve full amount"
            />
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Maximum: ${{ formatCurrency(selectedRequest?.max_advance_amount || 0) }}
            </p>
          </div>
          <div>
            <label for="approve-notes" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Notes (Optional)
            </label>
            <textarea
              id="approve-notes"
              name="approve-notes"
              v-model="approveForm.review_notes"
              rows="3"
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white"
              placeholder="Add notes about approval or counteroffer..."
            ></textarea>
          </div>
          <div class="flex gap-3">
            <button
              type="submit"
              :disabled="processing"
              class="flex-1 px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
            >
              {{ processing ? 'Processing...' : 'Approve' }}
            </button>
            <button
              type="button"
              @click="closeApproveModal"
              class="px-4 py-2 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-400 dark:hover:bg-gray-500"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Reject Modal -->
    <div v-if="showRejectModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full">
        <h3 class="text-xl font-semibold mb-4 dark:text-white">Reject Advance Request</h3>
        <form @submit.prevent="handleReject" class="space-y-4">
          <div>
            <label for="reject-reason" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Rejection Reason <span class="text-red-600">*</span>
            </label>
            <textarea
              id="reject-reason"
              name="reject-reason"
              v-model="rejectForm.review_notes"
              rows="4"
              required
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white"
              placeholder="Please provide a reason for rejection..."
            ></textarea>
          </div>
          <div class="flex gap-3">
            <button
              type="submit"
              :disabled="processing || !rejectForm.review_notes"
              class="flex-1 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
            >
              {{ processing ? 'Processing...' : 'Reject' }}
            </button>
            <button
              type="button"
              @click="closeRejectModal"
              class="px-4 py-2 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-400 dark:hover:bg-gray-500"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Details Modal -->
    <div v-if="showDetailsModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <h3 class="text-xl font-semibold mb-4 dark:text-white">Advance Request Details</h3>
        <div v-if="selectedRequest" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <div class="text-sm text-gray-600 dark:text-gray-400">Writer</div>
              <div class="font-medium dark:text-white">{{ selectedRequest.writer_full_name || selectedRequest.writer_username }}</div>
            </div>
            <div>
              <div class="text-sm text-gray-600 dark:text-gray-400">Status</div>
              <StatusBadge :status="selectedRequest.status" />
            </div>
            <div>
              <div class="text-sm text-gray-600 dark:text-gray-400">Requested Amount</div>
              <div class="font-medium dark:text-white">${{ formatCurrency(selectedRequest.requested_amount) }}</div>
            </div>
            <div>
              <div class="text-sm text-gray-600 dark:text-gray-400">Approved Amount</div>
              <div class="font-medium dark:text-white">
                {{ selectedRequest.approved_amount ? `$${formatCurrency(selectedRequest.approved_amount)}` : '-' }}
              </div>
            </div>
            <div>
              <div class="text-sm text-gray-600 dark:text-gray-400">Disbursed Amount</div>
              <div class="font-medium dark:text-white">
                {{ selectedRequest.disbursed_amount ? `$${formatCurrency(selectedRequest.disbursed_amount)}` : '-' }}
              </div>
            </div>
            <div>
              <div class="text-sm text-gray-600 dark:text-gray-400">Outstanding</div>
              <div class="font-medium text-orange-600 dark:text-orange-400">
                ${{ formatCurrency(selectedRequest.outstanding_amount) }}
              </div>
            </div>
            <div>
              <div class="text-sm text-gray-600 dark:text-gray-400">Requested At</div>
              <div class="font-medium dark:text-white">{{ formatDate(selectedRequest.requested_at) }}</div>
            </div>
            <div v-if="selectedRequest.reviewed_at">
              <div class="text-sm text-gray-600 dark:text-gray-400">Reviewed At</div>
              <div class="font-medium dark:text-white">{{ formatDate(selectedRequest.reviewed_at) }}</div>
            </div>
          </div>
          <div v-if="selectedRequest.reason">
            <div class="text-sm text-gray-600 dark:text-gray-400">Reason</div>
            <div class="mt-1 p-3 bg-gray-50 dark:bg-gray-700 rounded dark:text-white">{{ selectedRequest.reason }}</div>
          </div>
          <div v-if="selectedRequest.review_notes">
            <div class="text-sm text-gray-600 dark:text-gray-400">Review Notes</div>
            <div class="mt-1 p-3 bg-gray-50 dark:bg-gray-700 rounded dark:text-white">{{ selectedRequest.review_notes }}</div>
          </div>
          <div v-if="selectedRequest.deductions && selectedRequest.deductions.length > 0">
            <div class="text-sm font-medium mb-2 dark:text-white">Repayment History</div>
            <div class="space-y-2">
              <div
                v-for="deduction in selectedRequest.deductions"
                :key="deduction.id"
                class="p-3 bg-gray-50 dark:bg-gray-700 rounded text-sm dark:text-white"
              >
                ${{ formatCurrency(deduction.amount_deducted) }} on {{ formatDate(deduction.deducted_at) }}
                <span v-if="deduction.order_number" class="text-gray-500">
                  (Order #{{ deduction.order_number }})
                </span>
              </div>
            </div>
          </div>
        </div>
        <div class="mt-6 flex justify-end">
          <button
            @click="closeDetailsModal"
            class="px-4 py-2 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-300 rounded hover:bg-gray-400 dark:hover:bg-gray-500"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { writerAdvanceAPI } from '@/api'
import PageHeader from '@/components/common/PageHeader.vue'
import StatusBadge from '@/components/common/StatusBadge.vue'
import { debounce } from '@/utils/debounce'

const { success, error } = useToast()

// Get website ID from localStorage (set by API client interceptor)
const getWebsiteId = () => {
  return localStorage.getItem('current_website')
}

// Format currency amount
const formatCurrency = (amount) => {
  if (!amount && amount !== 0) return '0.00'
  return parseFloat(amount).toFixed(2)
}

// Format date string
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

const loading = ref(false)
const processing = ref(false)
const requests = ref([])
const stats = ref({})
const selectedRequest = ref(null)
const showApproveModal = ref(false)
const showRejectModal = ref(false)
const showDetailsModal = ref(false)

const filters = ref({
  status: '',
  writer: '',
  date_from: '',
  date_to: ''
})

const approveForm = ref({
  approved_amount: null,
  review_notes: ''
})

const rejectForm = ref({
  review_notes: ''
})

const loadRequests = async () => {
  loading.value = true
  try {
    const params = {
      website: getWebsiteId(),
      ...filters.value
    }
    // Remove empty filters
    Object.keys(params).forEach(key => {
      if (!params[key]) delete params[key]
    })
    
    const response = await writerAdvanceAPI.listRequests(params)
    requests.value = response.data.results || response.data
    
    // Calculate stats
    stats.value = {
      pending: requests.value.filter(r => r.status === 'pending').length,
      approved: requests.value.filter(r => r.status === 'approved').length,
      disbursed: requests.value.filter(r => r.status === 'disbursed').length,
      total_outstanding: requests.value
        .filter(r => r.outstanding_amount > 0)
        .reduce((sum, r) => sum + parseFloat(r.outstanding_amount), 0)
    }
  } catch (err) {
    error(err.response?.data?.detail || 'Failed to load requests')
  } finally {
    loading.value = false
  }
}

const openApproveModal = (request) => {
  selectedRequest.value = request
  approveForm.value = {
    approved_amount: request.requested_amount,
    review_notes: ''
  }
  showApproveModal.value = true
}

const closeApproveModal = () => {
  showApproveModal.value = false
  selectedRequest.value = null
  approveForm.value = { approved_amount: null, review_notes: '' }
}

const openRejectModal = (request) => {
  selectedRequest.value = request
  rejectForm.value = { review_notes: '' }
  showRejectModal.value = true
}

const closeRejectModal = () => {
  showRejectModal.value = false
  selectedRequest.value = null
  rejectForm.value = { review_notes: '' }
}

const viewDetails = (request) => {
  selectedRequest.value = request
  showDetailsModal.value = true
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
  selectedRequest.value = null
}

const handleApprove = async () => {
  if (!selectedRequest.value) return
  
  processing.value = true
  try {
    const data = {
      approved_amount: approveForm.value.approved_amount || selectedRequest.value.requested_amount,
      review_notes: approveForm.value.review_notes
    }
    
    await writerAdvanceAPI.approve(selectedRequest.value.id, data)
    success('Advance request approved successfully')
    closeApproveModal()
    await loadRequests()
  } catch (err) {
    error(err.response?.data?.detail || 'Failed to approve request')
  } finally {
    processing.value = false
  }
}

const handleReject = async () => {
  if (!selectedRequest.value || !rejectForm.value.review_notes) return
  
  processing.value = true
  try {
    await writerAdvanceAPI.reject(selectedRequest.value.id, rejectForm.value)
    success('Advance request rejected')
    closeRejectModal()
    await loadRequests()
  } catch (err) {
    error(err.response?.data?.detail || 'Failed to reject request')
  } finally {
    processing.value = false
  }
}

const handleDisburse = async (request) => {
  if (!confirm(`Disburse $${formatCurrency(request.approved_amount)} to ${request.writer_full_name || request.writer_username}?`)) {
    return
  }
  
  processing.value = true
  try {
    await writerAdvanceAPI.disburse(request.id)
    success('Advance disbursed successfully')
    await loadRequests()
  } catch (err) {
    error(err.response?.data?.detail || 'Failed to disburse advance')
  } finally {
    processing.value = false
  }
}

const debouncedSearch = debounce(() => {
  loadRequests()
}, 500)

onMounted(() => {
  loadRequests()
})
</script>

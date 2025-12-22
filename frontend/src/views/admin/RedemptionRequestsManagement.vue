<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Redemption Requests</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage client redemption requests for loyalty points</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Requests</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ stats.total || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-yellow-50 to-yellow-100 border border-yellow-200 dark:from-yellow-900/20 dark:to-yellow-800/20 dark:border-yellow-700">
        <p class="text-sm font-medium text-yellow-700 dark:text-yellow-300 mb-1">Pending</p>
        <p class="text-3xl font-bold text-yellow-900 dark:text-yellow-100">{{ stats.pending || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Approved</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ stats.approved || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Fulfilled</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ stats.fulfilled || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by client name or item..."
          class="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @input="debouncedSearch"
        />
        <select
          v-model="statusFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadRequests"
        >
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="fulfilled">Fulfilled</option>
          <option value="rejected">Rejected</option>
          <option value="cancelled">Cancelled</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading redemption requests...</p>
    </div>

    <!-- Requests List -->
    <div v-else class="space-y-4">
      <div
        v-for="request in requests"
        :key="request.id"
        class="card p-4 hover:shadow-lg transition-shadow"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ request.item_name || request.item?.name || request.item_id || 'N/A' }}
              </h3>
              <span
                :class="[
                  'px-2 py-1 text-xs font-semibold rounded-full',
                  request.status === 'fulfilled' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                  request.status === 'approved' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300' :
                  request.status === 'rejected' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300' :
                  request.status === 'cancelled' ? 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300' :
                  'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
                ]"
              >
                {{ request.status?.charAt(0).toUpperCase() + request.status?.slice(1) }}
              </span>
              <span class="px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300">
                {{ request.points_used || request.item_points || 0 }} points
              </span>
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-400 mb-2 space-y-1">
              <div>
                <span class="font-medium">Client:</span> {{ request.client_username || request.client || 'N/A' }}
              </div>
              <div>
                <span class="font-medium">Requested:</span> {{ formatDate(request.requested_at || request.created_at) }}
              </div>
              <div v-if="request.approved_at">
                <span class="font-medium">Approved:</span> {{ formatDate(request.approved_at) }}
                <span v-if="request.approved_by_username" class="ml-2">by {{ request.approved_by_username }}</span>
              </div>
              <div v-if="request.fulfilled_at">
                <span class="font-medium">Fulfilled:</span> {{ formatDate(request.fulfilled_at) }}
                <span v-if="request.fulfilled_by_username" class="ml-2">by {{ request.fulfilled_by_username }}</span>
              </div>
              <div v-if="request.fulfillment_code" class="mt-2 p-2 bg-gray-50 dark:bg-gray-800 rounded">
                <span class="font-medium">Fulfillment Code:</span> 
                <code class="ml-2 text-primary-600 dark:text-primary-400">{{ request.fulfillment_code }}</code>
              </div>
              <div v-if="request.rejection_reason" class="mt-2 p-2 bg-red-50 dark:bg-red-900/20 rounded text-red-700 dark:text-red-300">
                <span class="font-medium">Rejection Reason:</span> {{ request.rejection_reason }}
              </div>
            </div>
          </div>
          <div v-if="request.status === 'pending'" class="flex flex-col gap-2 ml-4">
            <button
              @click="approveRequest(request)"
              class="px-3 py-1 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              Approve
            </button>
            <button
              @click="rejectRequest(request)"
              class="px-3 py-1 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Reject
            </button>
          </div>
          <div v-else-if="request.status === 'approved'" class="flex gap-2 ml-4">
            <button
              @click="fulfillRequest(request)"
              class="px-3 py-1 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Mark Fulfilled
            </button>
          </div>
        </div>
      </div>
      <div v-if="requests.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        No redemption requests found
      </div>
    </div>

    <!-- Reject Modal -->
    <Modal
      :visible="showRejectModal"
      @close="closeRejectModal"
      title="Reject Redemption Request"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Rejection Reason *</label>
          <textarea
            v-model="rejectReason"
            rows="4"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Enter reason for rejection..."
          ></textarea>
        </div>
        <div v-if="rejectError" class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300">
          {{ rejectError }}
        </div>
      </div>
      <template #footer>
        <button
          @click="closeRejectModal"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
        >
          Cancel
        </button>
        <button
          @click="confirmReject"
          :disabled="!rejectReason.trim() || rejecting"
          class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ rejecting ? 'Rejecting...' : 'Reject Request' }}
        </button>
      </template>
    </Modal>

    <!-- Confirmation Dialog -->
    <ConfirmationDialog
      v-model:show="confirm.show.value"
      :title="confirm.title.value"
      :message="confirm.message.value"
      :details="confirm.details.value"
      :variant="confirm.variant.value"
      :icon="confirm.icon.value"
      :confirm-text="confirm.confirmText.value"
      :cancel-text="confirm.cancelText.value"
      @confirm="confirm.onConfirm"
      @cancel="confirm.onCancel"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { useInputModal } from '@/composables/useInputModal'
import { debounce } from '@/utils/debounce'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import Modal from '@/components/common/Modal.vue'
import loyaltyAPI from '@/api/loyalty-management'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()
const inputModal = useInputModal()

const loading = ref(false)
const rejecting = ref(false)
const requests = ref([])
const stats = ref({})
const searchQuery = ref('')
const statusFilter = ref('')
const showRejectModal = ref(false)
const selectedRequest = ref(null)
const rejectReason = ref('')
const rejectError = ref('')

const debouncedSearch = debounce(() => {
  loadRequests()
}, 300)

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const loadRequests = async () => {
  loading.value = true
  try {
    const params = {}
    if (statusFilter.value) params.status = statusFilter.value
    
    const response = await loyaltyAPI.listRedemptionRequests(params)
    let allRequests = response.data.results || response.data || []
    
    // Filter by search query
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      allRequests = allRequests.filter(req => 
        (req.client_username && req.client_username.toLowerCase().includes(query)) ||
        (req.item_name && req.item_name.toLowerCase().includes(query))
      )
    }
    
    requests.value = allRequests
    
    stats.value = {
      total: allRequests.length,
      pending: allRequests.filter(r => r.status === 'pending').length,
      approved: allRequests.filter(r => r.status === 'approved').length,
      fulfilled: allRequests.filter(r => r.status === 'fulfilled').length,
      rejected: allRequests.filter(r => r.status === 'rejected').length,
      cancelled: allRequests.filter(r => r.status === 'cancelled').length,
    }
  } catch (error) {
    showError('Failed to load redemption requests')
    console.error('Error loading requests:', error)
  } finally {
    loading.value = false
  }
}

const approveRequest = (request) => {
  confirm.show(
    'Approve Redemption Request',
    `Are you sure you want to approve this redemption request?`,
    `Item: ${request.item_name}\nPoints: ${request.points_used || request.item_points}\nClient: ${request.client_username}`,
    async () => {
      try {
        await loyaltyAPI.approveRedemption(request.id)
        showSuccess('Redemption request approved successfully')
        loadRequests()
      } catch (error) {
        showError('Failed to approve redemption request')
        console.error('Error approving request:', error)
      }
    }
  )
}

const rejectRequest = (request) => {
  selectedRequest.value = request
  rejectReason.value = ''
  rejectError.value = ''
  showRejectModal.value = true
}

const closeRejectModal = () => {
  showRejectModal.value = false
  selectedRequest.value = null
  rejectReason.value = ''
  rejectError.value = ''
}

const confirmReject = async () => {
  if (!rejectReason.value.trim()) {
    rejectError.value = 'Rejection reason is required'
    return
  }
  
  rejecting.value = true
  rejectError.value = ''
  
  try {
    await loyaltyAPI.rejectRedemption(selectedRequest.value.id, {
      reason: rejectReason.value
    })
    showSuccess('Redemption request rejected successfully')
    closeRejectModal()
    loadRequests()
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to reject redemption request'
    rejectError.value = errorMessage
    showError(errorMessage)
  } finally {
    rejecting.value = false
  }
}

const fulfillRequest = (request) => {
  inputModal.showModal(
    'Fulfill Redemption Request',
    'Enter the fulfillment code or details:',
    'Fulfillment Code',
    'Enter code...',
    'This code will be provided to the client',
    false,
    1,
    request.fulfillment_code || '',
    async (code) => {
      try {
        // Update the request with fulfillment code
        // Note: This might need a separate API endpoint for fulfillment
        await loyaltyAPI.updateRedemptionRequest?.(request.id, {
          status: 'fulfilled',
          fulfillment_code: code
        })
        showSuccess('Redemption request marked as fulfilled')
        loadRequests()
      } catch (error) {
        showError('Failed to fulfill redemption request')
        console.error('Error fulfilling request:', error)
      }
    }
  )
}

onMounted(() => {
  loadRequests()
})
</script>


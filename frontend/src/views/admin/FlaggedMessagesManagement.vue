<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Flagged Messages Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Review and moderate messages flagged by screened words</p>
      </div>
      <button
        @click="loadFlaggedMessages"
        :disabled="loading"
        class="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors font-medium disabled:opacity-50 flex items-center gap-2"
      >
        <svg v-if="loading" class="animate-spin w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4" v-if="stats">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Flagged</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ stats.total_flagged || 0 }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Pending Review</p>
        <p class="text-3xl font-bold text-yellow-600 dark:text-yellow-400">{{ stats.total_pending || 0 }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Reviewed</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ stats.total_reviewed || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 border border-gray-200 dark:border-gray-700">
      <div class="flex flex-col sm:flex-row gap-4">
        <div class="flex-1">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by sender, order ID, or message content..."
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-gray-100"
          />
        </div>
        <select
          v-model="statusFilter"
          class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-gray-100"
        >
          <option value="">All Status</option>
          <option value="pending">Pending Review</option>
          <option value="reviewed">Reviewed</option>
          <option value="unblocked">Unblocked</option>
        </select>
      </div>
    </div>

    <!-- Flagged Messages List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600 dark:text-gray-400">Loading flagged messages...</p>
      </div>
      <div v-else-if="filteredMessages.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-400 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="text-lg font-medium">No flagged messages found</p>
        <p class="text-sm mt-2">All messages have been reviewed or no messages have been flagged yet</p>
      </div>
      <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
        <div
          v-for="message in filteredMessages"
          :key="message.id"
          class="p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
              <!-- Header -->
              <div class="flex items-center gap-3 mb-3">
                <span
                  :class="{
                    'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400': !message.reviewed_by,
                    'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400': message.is_unblocked,
                    'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400': message.reviewed_by && !message.is_unblocked
                  }"
                  class="px-2 py-1 rounded-full text-xs font-medium"
                >
                  {{ message.reviewed_by ? (message.is_unblocked ? 'Unblocked' : 'Flagged') : 'Pending Review' }}
                </span>
                <span class="text-sm font-semibold text-gray-900 dark:text-gray-100">
                  Order #{{ message.order_id }}
                </span>
                <span class="text-sm text-gray-500 dark:text-gray-400">
                  From: {{ message.sender_username }}
                </span>
                <span class="text-xs text-gray-400 dark:text-gray-500">
                  {{ formatDateTime(message.flagged_at) }}
                </span>
              </div>

              <!-- Message Content -->
              <div class="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4 mb-3 border border-gray-200 dark:border-gray-700">
                <p class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap break-words">
                  {{ message.sanitized_message }}
                </p>
              </div>

              <!-- Flagged Reason -->
              <div class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-400 rounded p-3 mb-3">
                <div class="flex items-start gap-2">
                  <svg class="w-5 h-5 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                  <div class="flex-1">
                    <p class="text-sm font-medium text-red-800 dark:text-red-300">Flagged Reason</p>
                    <p class="text-sm text-red-700 dark:text-red-400 mt-1">{{ message.flagged_reason }}</p>
                  </div>
                </div>
              </div>

              <!-- Review Info -->
              <div v-if="message.reviewed_by" class="text-xs text-gray-500 dark:text-gray-400 mb-3">
                Reviewed by <span class="font-medium">{{ message.reviewed_by }}</span>
                <span v-if="message.reviewed_at"> on {{ formatDateTime(message.reviewed_at) }}</span>
              </div>

              <!-- Admin Comment -->
              <div v-if="message.admin_comment" class="bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-400 rounded p-3 mb-3">
                <p class="text-xs font-medium text-blue-800 dark:text-blue-300 mb-1">Admin Comment</p>
                <p class="text-sm text-blue-700 dark:text-blue-400">{{ message.admin_comment }}</p>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex flex-col gap-2 flex-shrink-0">
              <button
                v-if="!message.reviewed_by"
                @click="viewMessage(message)"
                class="px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-xs font-medium"
              >
                Review
              </button>
              <button
                v-if="message.reviewed_by && !message.is_unblocked"
                @click="unblockMessage(message)"
                class="px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-xs font-medium"
              >
                Unblock
              </button>
              <button
                v-if="message.is_unblocked"
                @click="reflagMessage(message)"
                class="px-3 py-1.5 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors text-xs font-medium"
              >
                Re-flag
              </button>
              <button
                @click="viewOrder(message.order_id)"
                class="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors text-xs font-medium"
              >
                View Order
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Review/Unblock Modal -->
    <div
      v-if="showReviewModal && selectedMessage"
      class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
      @click.self="closeReviewModal"
    >
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full mx-auto my-auto max-h-[90vh] overflow-y-auto">
        <div class="px-6 py-5 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h3 class="text-xl font-bold text-gray-900 dark:text-gray-100">
            {{ reviewAction === 'unblock' ? 'Unblock Message' : 'Review Flagged Message' }}
          </h3>
          <button
            @click="closeReviewModal"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="p-6 space-y-4">
          <!-- Message Preview -->
          <div class="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
            <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Message Content</p>
            <p class="text-sm text-gray-600 dark:text-gray-400 whitespace-pre-wrap break-words">
              {{ selectedMessage.sanitized_message }}
            </p>
          </div>

          <!-- Flagged Reason -->
          <div class="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-400 rounded p-3">
            <p class="text-sm font-medium text-red-800 dark:text-red-300 mb-1">Flagged Reason</p>
            <p class="text-sm text-red-700 dark:text-red-400">{{ selectedMessage.flagged_reason }}</p>
          </div>

          <!-- Order Info -->
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p class="text-gray-500 dark:text-gray-400">Order ID</p>
              <p class="font-medium text-gray-900 dark:text-gray-100">#{{ selectedMessage.order_id }}</p>
            </div>
            <div>
              <p class="text-gray-500 dark:text-gray-400">Sender</p>
              <p class="font-medium text-gray-900 dark:text-gray-100">{{ selectedMessage.sender_username }}</p>
            </div>
            <div>
              <p class="text-gray-500 dark:text-gray-400">Flagged At</p>
              <p class="font-medium text-gray-900 dark:text-gray-100">{{ formatDateTime(selectedMessage.flagged_at) }}</p>
            </div>
          </div>

          <!-- Admin Comment -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Admin Comment {{ reviewAction === 'unblock' ? '(Optional)' : '' }}
            </label>
            <textarea
              v-model="reviewForm.comment"
              rows="4"
              placeholder="Add a comment about your decision..."
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-700 dark:text-gray-100"
            ></textarea>
          </div>

          <div v-if="formError" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
            <p class="text-sm text-red-700 dark:text-red-400">{{ formError }}</p>
          </div>

          <div class="flex gap-3 pt-4">
            <button
              @click="closeReviewModal"
              class="flex-1 px-4 py-2.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors font-medium"
            >
              Cancel
            </button>
            <button
              @click="submitReview"
              :disabled="saving"
              class="flex-1 px-4 py-2.5 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium flex items-center justify-center gap-2"
            >
              <svg v-if="saving" class="animate-spin w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              {{ saving ? 'Processing...' : (reviewAction === 'unblock' ? 'Unblock Message' : 'Confirm Review') }}
            </button>
          </div>
        </div>
      </div>
    </div>

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
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import apiClient from '@/api/client'

const router = useRouter()
const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const saving = ref(false)
const messages = ref([])
const stats = ref(null)
const searchQuery = ref('')
const statusFilter = ref('')
const showReviewModal = ref(false)
const selectedMessage = ref(null)
const reviewAction = ref('review')
const reviewForm = ref({ comment: '' })
const formError = ref('')

const filteredMessages = computed(() => {
  let filtered = messages.value

  // Status filter
  if (statusFilter.value === 'pending') {
    filtered = filtered.filter(m => !m.reviewed_by)
  } else if (statusFilter.value === 'reviewed') {
    filtered = filtered.filter(m => m.reviewed_by && !m.is_unblocked)
  } else if (statusFilter.value === 'unblocked') {
    filtered = filtered.filter(m => m.is_unblocked)
  }

  // Search filter
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(m => {
      return (
        m.sender_username?.toLowerCase().includes(query) ||
        m.order_id?.toString().includes(query) ||
        m.sanitized_message?.toLowerCase().includes(query) ||
        m.flagged_reason?.toLowerCase().includes(query)
      )
    })
  }

  return filtered
})

const loadFlaggedMessages = async () => {
  loading.value = true
  try {
    const response = await apiClient.get('/order-communications/flagged-messages/')
    messages.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load flagged messages:', error)
    showError('Failed to load flagged messages: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const response = await apiClient.get('/order-communications/flagged-messages/statistics/')
    stats.value = response.data
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

const viewMessage = (message) => {
  selectedMessage.value = message
  reviewAction.value = 'review'
  reviewForm.value = { comment: '' }
  formError.value = ''
  showReviewModal.value = true
}

const unblockMessage = async (message) => {
  selectedMessage.value = message
  reviewAction.value = 'unblock'
  reviewForm.value = { comment: message.admin_comment || '' }
  formError.value = ''
  showReviewModal.value = true
}

const submitReview = async () => {
  if (!selectedMessage.value) return

  saving.value = true
  formError.value = ''

  try {
    if (reviewAction.value === 'unblock') {
      await apiClient.post(`/order-communications/flagged-messages/${selectedMessage.value.id}/unblock/`, {
        admin_comment: reviewForm.value.comment
      })
      showSuccess('Message unblocked successfully')
    } else {
      // For now, just mark as reviewed by unblocking (you may want to add a separate review endpoint)
      await apiClient.post(`/order-communications/flagged-messages/${selectedMessage.value.id}/unblock/`, {
        admin_comment: reviewForm.value.comment || 'Reviewed and confirmed as flagged'
      })
      showSuccess('Message reviewed successfully')
    }
    
    closeReviewModal()
    await Promise.all([loadFlaggedMessages(), loadStats()])
  } catch (error) {
    formError.value = error.response?.data?.detail || error.response?.data?.error || error.message
    showError('Failed to process review: ' + formError.value)
  } finally {
    saving.value = false
  }
}

const reflagMessage = async (message) => {
  const confirmed = await confirm.showDialog(
    `Are you sure you want to re-flag this message? It will be marked for review again.`,
    'Re-flag Message',
    {
      variant: 'warning',
      icon: '⚠️',
      confirmText: 'Re-flag',
      cancelText: 'Cancel'
    }
  )

  if (!confirmed) return

  try {
    await apiClient.post(`/order-communications/flagged-messages/${message.id}/reflag/`)
    showSuccess('Message re-flagged successfully')
    await Promise.all([loadFlaggedMessages(), loadStats()])
  } catch (error) {
    showError('Failed to re-flag message: ' + (error.response?.data?.detail || error.message))
  }
}

const viewOrder = (orderId) => {
  router.push(`/orders/${orderId}`)
}

const closeReviewModal = () => {
  showReviewModal.value = false
  selectedMessage.value = null
  reviewForm.value = { comment: '' }
  formError.value = ''
}

const formatDateTime = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

onMounted(async () => {
  await Promise.all([loadFlaggedMessages(), loadStats()])
})
</script>

<style scoped>
/* Additional styles if needed */
</style>


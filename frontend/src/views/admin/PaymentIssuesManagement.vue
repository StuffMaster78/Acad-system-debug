<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Payment Issues Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Log and track payment-related issues reported by users</p>
      </div>
      <button
        @click="openCreateModal"
        class="btn btn-primary flex items-center gap-2"
      >
        <span>➕</span>
        <span>Report Payment Issue</span>
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Issues</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ stats.total || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200 dark:from-yellow-900/20 dark:to-yellow-800/20 dark:border-yellow-700">
        <p class="text-sm font-medium text-yellow-700 dark:text-yellow-300 mb-1">Pending</p>
        <p class="text-3xl font-bold text-yellow-900 dark:text-yellow-100">{{ stats.pending || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Resolved</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ stats.resolved || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-red-50 to-red-100 border border-red-200 dark:from-red-900/20 dark:to-red-800/20 dark:border-red-700">
        <p class="text-sm font-medium text-red-700 dark:text-red-300 mb-1">Escalated</p>
        <p class="text-3xl font-bold text-red-900 dark:text-red-100">{{ stats.escalated || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by order ID or description..."
          class="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @input="debouncedSearch"
        />
        <select
          v-model="statusFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadIssues"
        >
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="resolved">Resolved</option>
          <option value="escalated">Escalated</option>
        </select>
        <select
          v-model="issueTypeFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadIssues"
        >
          <option value="">All Types</option>
          <option value="unpaid_order">Unpaid Order</option>
          <option value="overpayment">Overpayment</option>
          <option value="underpayment">Underpayment</option>
          <option value="refund_request">Refund Request</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading payment issues...</p>
    </div>

    <!-- Issues List -->
    <div v-else class="space-y-4">
      <div
        v-for="issue in issues"
        :key="issue.id"
        class="card p-4 hover:shadow-lg transition-shadow"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                Order #{{ issue.order || issue.order_id || 'N/A' }}
              </h3>
              <span
                :class="[
                  'px-2 py-1 text-xs font-semibold rounded-full',
                  issue.status === 'resolved' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                  issue.status === 'escalated' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300' :
                  'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
                ]"
              >
                {{ issue.status?.charAt(0).toUpperCase() + issue.status?.slice(1) }}
              </span>
              <span class="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                {{ issue.issue_type ? issue.issue_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'N/A' }}
              </span>
            </div>
            <p class="text-gray-600 dark:text-gray-400 mb-2">{{ issue.description }}</p>
            <div class="text-sm text-gray-500 dark:text-gray-400">
              <span>Reported by: {{ issue.reported_by_name || issue.reported_by || 'N/A' }}</span>
              <span class="mx-2">•</span>
              <span>{{ formatDate(issue.created_at || issue.timestamp) }}</span>
            </div>
          </div>
          <div class="flex gap-2 ml-4">
            <button
              v-if="issue.status === 'pending'"
              @click="escalateIssue(issue)"
              class="px-3 py-1 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Escalate
            </button>
            <button
              @click="viewIssue(issue)"
              class="px-3 py-1 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              View
            </button>
          </div>
        </div>
      </div>
      <div v-if="issues.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        No payment issues found
      </div>
    </div>

    <!-- Create Modal -->
    <Modal
      :visible="showModal"
      @close="closeModal"
      title="Report Payment Issue"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Order ID *</label>
          <input
            v-model.number="form.order"
            type="number"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Enter order ID"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Issue Type *</label>
          <select
            v-model="form.issue_type"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          >
            <option value="unpaid_order">Unpaid Order</option>
            <option value="overpayment">Overpayment</option>
            <option value="underpayment">Underpayment</option>
            <option value="refund_request">Refund Request</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Description *</label>
          <textarea
            v-model="form.description"
            rows="4"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Describe the payment issue..."
          ></textarea>
        </div>
        <div v-if="formError" class="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300">
          {{ formError }}
        </div>
      </div>
      <template #footer>
        <button
          @click="closeModal"
          class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
        >
          Cancel
        </button>
        <button
          @click="saveIssue"
          :disabled="saving || !canSave"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ saving ? 'Saving...' : 'Report Issue' }}
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
import { debounce } from '@/utils/debounce'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import Modal from '@/components/common/Modal.vue'
import supportManagementAPI from '@/api/support-management'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const saving = ref(false)
const issues = ref([])
const stats = ref({})
const searchQuery = ref('')
const statusFilter = ref('')
const issueTypeFilter = ref('')
const showModal = ref(false)
const formError = ref('')

const form = ref({
  order: null,
  issue_type: 'unpaid_order',
  description: '',
})

const canSave = computed(() => {
  return form.value.order && form.value.description.trim()
})

const debouncedSearch = debounce(() => {
  loadIssues()
}, 300)

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const loadIssues = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value) params.search = searchQuery.value
    if (statusFilter.value) params.status = statusFilter.value
    if (issueTypeFilter.value) params.issue_type = issueTypeFilter.value
    const response = await supportManagementAPI.listPaymentIssues(params)
    issues.value = response.data.results || response.data || []
    
    stats.value = {
      total: issues.value.length,
      pending: issues.value.filter(i => i.status === 'pending').length,
      resolved: issues.value.filter(i => i.status === 'resolved').length,
      escalated: issues.value.filter(i => i.status === 'escalated').length,
    }
  } catch (error) {
    showError('Failed to load payment issues')
    console.error('Error loading issues:', error)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  form.value = {
    order: null,
    issue_type: 'unpaid_order',
    description: '',
  }
  formError.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  formError.value = ''
}

const saveIssue = async () => {
  if (!canSave.value) return
  saving.value = true
  formError.value = ''
  try {
    await supportManagementAPI.createPaymentIssue(form.value)
    showSuccess('Payment issue reported successfully')
    closeModal()
    loadIssues()
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to report payment issue'
    formError.value = errorMessage
    showError(errorMessage)
  } finally {
    saving.value = false
  }
}

const escalateIssue = (issue) => {
  confirm.showDestructive(
    'Escalate Payment Issue',
    `Are you sure you want to escalate this payment issue?`,
    `This will notify administrators for immediate review.`,
    async () => {
      try {
        await supportManagementAPI.escalatePaymentIssue(issue.id)
        showSuccess('Payment issue escalated successfully')
        loadIssues()
      } catch (error) {
        showError('Failed to escalate payment issue')
      }
    }
  )
}

const viewIssue = (issue) => {
  // Could open a detail modal or navigate to order detail
  console.log('View issue:', issue)
}

onMounted(() => {
  loadIssues()
})
</script>


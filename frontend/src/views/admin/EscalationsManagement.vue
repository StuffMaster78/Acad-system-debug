<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Escalations Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Track escalated tickets and issues requiring admin review</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Escalations</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ stats.total || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200 dark:from-yellow-900/20 dark:to-yellow-800/20 dark:border-yellow-700">
        <p class="text-sm font-medium text-yellow-700 dark:text-yellow-300 mb-1">Pending</p>
        <p class="text-3xl font-bold text-yellow-900 dark:text-yellow-100">{{ stats.pending || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Approved</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ stats.approved || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-red-50 to-red-100 border border-red-200 dark:from-red-900/20 dark:to-red-800/20 dark:border-red-700">
        <p class="text-sm font-medium text-red-700 dark:text-red-300 mb-1">Rejected</p>
        <p class="text-3xl font-bold text-red-900 dark:text-red-100">{{ stats.rejected || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by action type or reason..."
          class="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @input="debouncedSearch"
        />
        <select
          v-model="statusFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadEscalations"
        >
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
        </select>
        <select
          v-model="actionTypeFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadEscalations"
        >
          <option value="">All Action Types</option>
          <option value="blacklist_client">Blacklist Client</option>
          <option value="promote_writer">Promote Writer</option>
          <option value="demote_writer">Demote Writer</option>
          <option value="writer_probation">Writer Probation</option>
          <option value="suspend_writer">Suspend Writer</option>
          <option value="suspend_client">Suspend Client</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading escalations...</p>
    </div>

    <!-- Escalations List -->
    <div v-else class="space-y-4">
      <div
        v-for="escalation in escalations"
        :key="escalation.id"
        class="card p-4 hover:shadow-lg transition-shadow"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ formatActionType(escalation.action_type) }}
              </h3>
              <span
                :class="[
                  'px-2 py-1 text-xs font-semibold rounded-full',
                  escalation.status === 'approved' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                  escalation.status === 'rejected' ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300' :
                  'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
                ]"
              >
                {{ escalation.status?.charAt(0).toUpperCase() + escalation.status?.slice(1) }}
              </span>
            </div>
            <p class="text-gray-600 dark:text-gray-400 mb-2">{{ escalation.reason }}</p>
            <div class="text-sm text-gray-500 dark:text-gray-400 space-y-1">
              <div>
                <span class="font-medium">Target User:</span> {{ escalation.target_user_name || escalation.target_user || 'N/A' }}
              </div>
              <div>
                <span class="font-medium">Escalated by:</span> {{ escalation.escalated_by_name || escalation.escalated_by || 'N/A' }}
                <span class="mx-2">•</span>
                <span>{{ formatDate(escalation.timestamp || escalation.created_at) }}</span>
              </div>
              <div v-if="escalation.reviewed_by">
                <span class="font-medium">Reviewed by:</span> {{ escalation.reviewed_by_name || escalation.reviewed_by }}
                <span class="mx-2">•</span>
                <span>{{ formatDate(escalation.reviewed_at) }}</span>
              </div>
            </div>
          </div>
          <div v-if="escalation.status === 'pending'" class="flex gap-2 ml-4">
            <button
              @click="approveEscalation(escalation)"
              class="px-3 py-1 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              Approve
            </button>
            <button
              @click="rejectEscalation(escalation)"
              class="px-3 py-1 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Reject
            </button>
          </div>
        </div>
      </div>
      <div v-if="escalations.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        No escalations found
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
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { useInputModal } from '@/composables/useInputModal'
import { debounce } from '@/utils/debounce'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import supportManagementAPI from '@/api/support-management'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()
const inputModal = useInputModal()

const loading = ref(false)
const escalations = ref([])
const stats = ref({})
const searchQuery = ref('')
const statusFilter = ref('')
const actionTypeFilter = ref('')

const debouncedSearch = debounce(() => {
  loadEscalations()
}, 300)

const formatActionType = (type) => {
  if (!type) return 'N/A'
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const loadEscalations = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value) params.search = searchQuery.value
    if (statusFilter.value) params.status = statusFilter.value
    if (actionTypeFilter.value) params.action_type = actionTypeFilter.value
    const response = await supportManagementAPI.listEscalations(params)
    escalations.value = response.data.results || response.data || []
    
    stats.value = {
      total: escalations.value.length,
      pending: escalations.value.filter(e => e.status === 'pending').length,
      approved: escalations.value.filter(e => e.status === 'approved').length,
      rejected: escalations.value.filter(e => e.status === 'rejected').length,
    }
  } catch (error) {
    showError('Failed to load escalations')
    console.error('Error loading escalations:', error)
  } finally {
    loading.value = false
  }
}

const approveEscalation = (escalation) => {
  confirm.show(
    'Approve Escalation',
    `Are you sure you want to approve this escalation?`,
    `Action: ${formatActionType(escalation.action_type)}\nTarget: ${escalation.target_user_name || escalation.target_user}`,
    async () => {
      try {
        await supportManagementAPI.approveEscalation(escalation.id)
        showSuccess('Escalation approved successfully')
        loadEscalations()
      } catch (error) {
        showError('Failed to approve escalation')
      }
    }
  )
}

const rejectEscalation = (escalation) => {
  inputModal.showModal(
    'Reject Escalation',
    'Please provide a reason for rejecting this escalation:',
    'Rejection Reason',
    'Enter reason...',
    'This reason will be added to the escalation record.',
    true,
    4,
    '',
    async (reason) => {
      if (!reason || !reason.trim()) {
        showError('Rejection reason is required')
        return
      }
      try {
        await supportManagementAPI.updateEscalation(escalation.id, {
          status: 'rejected',
          reason: escalation.reason + `\n[Admin Rejection Note]: ${reason}`,
        })
        showSuccess('Escalation rejected successfully')
        loadEscalations()
      } catch (error) {
        showError('Failed to reject escalation')
      }
    }
  )
}

onMounted(() => {
  loadEscalations()
})
</script>


<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Appeals Management</h1>
        <p class="mt-2 text-gray-600">Review and manage appeals from users regarding suspensions, blacklists, and probation</p>
      </div>
      <div class="flex items-center gap-3">
        <button
          @click="showPendingOnly = !showPendingOnly"
          :class="showPendingOnly ? 'btn btn-primary' : 'btn btn-secondary'"
        >
          {{ showPendingOnly ? 'Show All' : 'Show Pending Only' }}
        </button>
      </div>
    </div>

    <!-- Info Banner -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <h3 class="font-semibold text-blue-900 mb-2">About Appeals</h3>
      <p class="text-sm text-blue-800">
        Users can submit appeals to request reconsideration of disciplinary actions (suspension, blacklist, or probation). 
        Review each appeal carefully, considering the user's explanation and history. You can approve appeals to reverse 
        the disciplinary action, or reject them to maintain the current status.
      </p>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="card p-4 bg-yellow-50 border border-yellow-200">
        <p class="text-sm font-medium text-yellow-700 mb-1">Pending Appeals</p>
        <p class="text-2xl font-bold text-yellow-900">{{ stats.pending || 0 }}</p>
        <p class="text-xs text-yellow-600 mt-1">Awaiting review</p>
      </div>
      <div class="card p-4 bg-green-50 border border-green-200">
        <p class="text-sm font-medium text-green-700 mb-1">Approved</p>
        <p class="text-2xl font-bold text-green-900">{{ stats.approved || 0 }}</p>
        <p class="text-xs text-green-600 mt-1">This month</p>
      </div>
      <div class="card p-4 bg-red-50 border border-red-200">
        <p class="text-sm font-medium text-red-700 mb-1">Rejected</p>
        <p class="text-2xl font-bold text-red-900">{{ stats.rejected || 0 }}</p>
        <p class="text-xs text-red-600 mt-1">This month</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1">Search User</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Username, email..."
            class="w-full border rounded px-3 py-2"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Appeal Type</label>
          <select v-model="filters.appeal_type" @change="loadAppeals" class="w-full border rounded px-3 py-2">
            <option value="">All Types</option>
            <option value="probation">Probation</option>
            <option value="blacklist">Blacklist</option>
            <option value="suspension">Suspension</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1">Status</label>
          <select v-model="filters.status" @change="loadAppeals" class="w-full border rounded px-3 py-2">
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Appeals Table -->
    <div class="card overflow-hidden">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Appeal Type</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reason</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Submitted</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Reviewed By</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="appeal in appeals" :key="appeal.id" class="hover:bg-gray-50">
                <td class="px-4 py-3 whitespace-nowrap">
                  <div>
                    <div class="font-medium text-gray-900">{{ appeal.user_username }}</div>
                    <div class="text-sm text-gray-500">{{ appeal.user_email }}</div>
                  </div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <span :class="getAppealTypeClass(appeal.appeal_type)" class="px-2 py-1 rounded text-xs font-medium">
                    {{ appeal.appeal_type }}
                  </span>
                </td>
                <td class="px-4 py-3">
                  <div class="text-sm text-gray-900 max-w-md truncate">{{ appeal.reason }}</div>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(appeal.submitted_at) }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <span :class="getStatusClass(appeal.status)" class="px-2 py-1 rounded text-xs font-medium">
                    {{ appeal.status }}
                  </span>
                </td>
                <td class="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                  {{ appeal.reviewed_by_username || '—' }}
                </td>
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="flex items-center gap-2">
                    <button
                      @click="viewAppeal(appeal)"
                      class="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      View
                    </button>
                    <template v-if="appeal.status === 'pending'">
                      <button
                        @click="approveAppeal(appeal)"
                        class="text-green-600 hover:text-green-800 text-sm font-medium"
                      >
                        Approve
                      </button>
                      <button
                        @click="rejectAppeal(appeal)"
                        class="text-red-600 hover:text-red-800 text-sm font-medium"
                      >
                        Reject
                      </button>
                    </template>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="!appeals.length" class="text-center py-12 text-gray-500">
          No appeals found.
        </div>
      </div>
    </div>

    <!-- Appeal Detail Modal -->
    <div v-if="viewingAppeal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div class="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-bold">Appeal Details</h2>
          <button @click="viewingAppeal = null" class="text-gray-500 hover:text-gray-700">✕</button>
        </div>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">User</label>
            <div class="text-gray-900">
              {{ viewingAppeal.user_username }} ({{ viewingAppeal.user_email }})
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Appeal Type</label>
            <span :class="getAppealTypeClass(viewingAppeal.appeal_type)" class="px-2 py-1 rounded text-xs font-medium">
              {{ viewingAppeal.appeal_type }}
            </span>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Reason for Appeal</label>
            <div class="bg-gray-50 border rounded p-3 text-gray-900 whitespace-pre-wrap">
              {{ viewingAppeal.reason }}
            </div>
            <p class="text-xs text-gray-500 mt-1">
              This is the user's explanation for why they believe the disciplinary action should be reconsidered.
            </p>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Submitted</label>
              <div class="text-gray-900">{{ formatDateTime(viewingAppeal.submitted_at) }}</div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <span :class="getStatusClass(viewingAppeal.status)" class="px-2 py-1 rounded text-xs font-medium">
                {{ viewingAppeal.status }}
              </span>
            </div>
          </div>

          <div v-if="viewingAppeal.reviewed_by_username">
            <label class="block text-sm font-medium text-gray-700 mb-1">Reviewed By</label>
            <div class="text-gray-900">{{ viewingAppeal.reviewed_by_username }}</div>
          </div>

          <div v-if="viewingAppeal.status === 'pending'" class="flex gap-2 pt-4 border-t">
            <button
              @click="approveAppeal(viewingAppeal)"
              class="btn btn-primary flex-1"
            >
              Approve Appeal
            </button>
            <button
              @click="rejectAppeal(viewingAppeal)"
              class="btn bg-red-600 text-white hover:bg-red-700 flex-1"
            >
              Reject Appeal
            </button>
          </div>

          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mt-4">
            <h3 class="font-semibold text-yellow-900 mb-2">What happens when you approve?</h3>
            <ul class="text-sm text-yellow-800 space-y-1 list-disc list-inside">
              <li v-if="viewingAppeal.appeal_type === 'probation'">The writer will be removed from probation status</li>
              <li v-if="viewingAppeal.appeal_type === 'blacklist'">The writer will be removed from the blacklist</li>
              <li v-if="viewingAppeal.appeal_type === 'suspension'">The writer's suspension will be lifted</li>
              <li>The action will be logged in the system for audit purposes</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Messages -->
    <div v-if="message" class="p-3 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'">
      {{ message }}
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
import { ref, computed, onMounted, watch } from 'vue'
import { appealsAPI } from '@/api'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const { showToast } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const appeals = ref([])
const viewingAppeal = ref(null)
const message = ref('')
const messageSuccess = ref(false)
const showPendingOnly = ref(false)

const stats = ref({
  pending: 0,
  approved: 0,
  rejected: 0,
})

const filters = ref({
  search: '',
  appeal_type: '',
  status: '',
})

let searchTimeout = null

const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadAppeals()
  }, 500)
}

watch(showPendingOnly, (val) => {
  if (val) {
    filters.value.status = 'pending'
  } else {
    filters.value.status = ''
  }
  loadAppeals()
})

const loadAppeals = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.appeal_type) params.appeal_type = filters.value.appeal_type
    if (filters.value.status) params.status = filters.value.status
    
    const res = await appealsAPI.listAppeals(params)
    appeals.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : [])
    
    // Calculate stats
    stats.value.pending = appeals.value.filter(a => a.status === 'pending').length
    stats.value.approved = appeals.value.filter(a => a.status === 'approved').length
    stats.value.rejected = appeals.value.filter(a => a.status === 'rejected').length
  } catch (e) {
    message.value = 'Failed to load appeals: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
  } finally {
    loading.value = false
  }
}

const viewAppeal = (appeal) => {
  viewingAppeal.value = appeal
}

const approveAppeal = async (appeal) => {
  const actionDescription = appeal.appeal_type === 'probation' 
    ? 'remove the writer from probation' 
    : appeal.appeal_type === 'blacklist' 
    ? 'remove the writer from the blacklist' 
    : 'lift the writer\'s suspension'
  
  const confirmed = await confirm.showWarning(
    `Are you sure you want to APPROVE this appeal?`,
    'Approve Appeal',
    {
      details: `This will ${actionDescription}.\n\nUser: ${appeal.user_username}\nType: ${appeal.appeal_type}\nReason: ${appeal.reason.substring(0, 100)}...`,
      confirmText: 'Approve',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await appealsAPI.approveAppeal(appeal.id)
    message.value = 'Appeal approved successfully'
    messageSuccess.value = true
    viewingAppeal.value = null
    await loadAppeals()
    showToast('Appeal approved successfully. The disciplinary action has been reversed.', 'success')
  } catch (e) {
    message.value = 'Failed to approve appeal: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    showToast(message.value, 'error')
  }
}

const rejectAppeal = async (appeal) => {
  const confirmed = await confirm.showWarning(
    'Are you sure you want to REJECT this appeal?',
    'Reject Appeal',
    {
      details: `The current disciplinary action (${appeal.appeal_type}) will remain in effect.\n\nUser: ${appeal.user_username}`,
      confirmText: 'Reject',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await appealsAPI.rejectAppeal(appeal.id)
    message.value = 'Appeal rejected'
    messageSuccess.value = true
    viewingAppeal.value = null
    await loadAppeals()
    showToast('Appeal rejected. The disciplinary action remains in effect.', 'info')
  } catch (e) {
    message.value = 'Failed to reject appeal: ' + (e.response?.data?.detail || e.message)
    messageSuccess.value = false
    showToast(message.value, 'error')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString()
}

const formatDateTime = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getAppealTypeClass = (type) => {
  const classes = {
    probation: 'bg-yellow-100 text-yellow-800',
    blacklist: 'bg-black text-white',
    suspension: 'bg-red-100 text-red-800',
  }
  return classes[type] || 'bg-gray-100 text-gray-800'
}

const getStatusClass = (status) => {
  const classes = {
    pending: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800',
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

onMounted(async () => {
  await loadAppeals()
})
</script>

<style scoped>
.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-weight: 500;
  transition-property: color, background-color, border-color;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
.btn-primary {
  background-color: #2563eb;
  color: white;
}
.btn-primary:hover {
  background-color: #1d4ed8;
}
.btn-secondary {
  background-color: #e5e7eb;
  color: #1f2937;
}
.btn-secondary:hover {
  background-color: #d1d5db;
}
.card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  padding: 1.5rem;
}
</style>


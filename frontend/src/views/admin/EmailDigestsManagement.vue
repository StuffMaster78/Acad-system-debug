<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Email Digests Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage email digest configurations and schedules</p>
      </div>
      <div class="flex gap-2">
        <button
          @click="sendDueDigests"
          :disabled="sending"
          class="btn btn-secondary flex items-center gap-2"
        >
          <span>📧</span>
          <span>{{ sending ? 'Sending...' : 'Send Due Digests' }}</span>
        </button>
        <button
          @click="openCreateModal"
          class="btn btn-primary flex items-center gap-2"
        >
          <span>➕</span>
          <span>Create Digest</span>
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Digests</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ stats.total || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Active</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ stats.active || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 border border-yellow-200 dark:from-yellow-900/20 dark:to-yellow-800/20 dark:border-yellow-700">
        <p class="text-sm font-medium text-yellow-700 dark:text-yellow-300 mb-1">Pending</p>
        <p class="text-3xl font-bold text-yellow-900 dark:text-yellow-100">{{ stats.pending || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Sent</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ stats.sent || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search digests..."
          class="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @input="debouncedSearch"
        />
        <select
          v-model="statusFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadDigests"
        >
          <option value="">All Statuses</option>
          <option value="pending">Pending</option>
          <option value="sent">Sent</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading email digests...</p>
    </div>

    <!-- Digests List -->
    <div v-else class="space-y-4">
      <div
        v-for="digest in digests"
        :key="digest.id"
        class="card p-4 hover:shadow-lg transition-shadow"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                User ID: {{ digest.user_id || digest.user || 'N/A' }}
              </h3>
              <span
                :class="[
                  'px-2 py-1 text-xs font-semibold rounded-full',
                  digest.status === 'sent' ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                  'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
                ]"
              >
                {{ digest.status?.charAt(0).toUpperCase() + digest.status?.slice(1) || 'Pending' }}
              </span>
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <div v-if="digest.frequency">
                <span class="font-medium">Frequency:</span> {{ digest.frequency }}
              </div>
              <div v-if="digest.next_send_at">
                <span class="font-medium">Next Send:</span> {{ formatDate(digest.next_send_at) }}
              </div>
              <div v-if="digest.last_sent_at">
                <span class="font-medium">Last Sent:</span> {{ formatDate(digest.last_sent_at) }}
              </div>
              <div v-if="digest.notification_count">
                <span class="font-medium">Notifications:</span> {{ digest.notification_count }}
              </div>
            </div>
          </div>
          <div class="flex gap-2 ml-4">
            <button
              v-if="digest.status !== 'sent'"
              @click="sendDigest(digest)"
              class="px-3 py-1 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Send Now
            </button>
            <button
              @click="editDigest(digest)"
              class="px-3 py-1 text-sm bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Edit
            </button>
            <button
              @click="deleteDigest(digest)"
              class="px-3 py-1 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
      <div v-if="digests.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        No email digests found
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <Modal
      :visible="showModal"
      @close="closeModal"
      :title="editingDigest ? 'Edit Email Digest' : 'Create Email Digest'"
      size="lg"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">User ID *</label>
          <input
            v-model.number="form.user_id"
            type="number"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Enter user ID"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Frequency</label>
          <select
            v-model="form.frequency"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Next Send At</label>
          <input
            v-model="form.next_send_at"
            type="datetime-local"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          />
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
          @click="saveDigest"
          :disabled="saving || !canSave"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ saving ? 'Saving...' : (editingDigest ? 'Update' : 'Create') }}
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
import adminManagementAPI from '@/api/admin-management'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const saving = ref(false)
const sending = ref(false)
const digests = ref([])
const stats = ref({})
const searchQuery = ref('')
const statusFilter = ref('')
const showModal = ref(false)
const editingDigest = ref(null)
const formError = ref('')

const form = ref({
  user_id: null,
  frequency: 'daily',
  next_send_at: '',
})

const canSave = computed(() => {
  return form.value.user_id
})

const debouncedSearch = debounce(() => {
  loadDigests()
}, 300)

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const loadDigests = async () => {
  loading.value = true
  try {
    const params = {}
    if (statusFilter.value) params.status = statusFilter.value
    
    const response = await adminManagementAPI.listEmailDigests(params)
    let allDigests = response.data.results || response.data || []
    
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      allDigests = allDigests.filter(d => 
        String(d.user_id || d.user || '').includes(query)
      )
    }
    
    digests.value = allDigests
    
    stats.value = {
      total: allDigests.length,
      active: allDigests.filter(d => d.status !== 'sent').length,
      pending: allDigests.filter(d => d.status === 'pending' || !d.status).length,
      sent: allDigests.filter(d => d.status === 'sent').length,
    }
  } catch (error) {
    showError('Failed to load email digests')
    console.error('Error loading digests:', error)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingDigest.value = null
  form.value = {
    user_id: null,
    frequency: 'daily',
    next_send_at: '',
  }
  formError.value = ''
  showModal.value = true
}

const editDigest = (digest) => {
  editingDigest.value = digest
  form.value = {
    user_id: digest.user_id || digest.user || null,
    frequency: digest.frequency || 'daily',
    next_send_at: digest.next_send_at ? new Date(digest.next_send_at).toISOString().slice(0, 16) : '',
  }
  formError.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingDigest.value = null
  formError.value = ''
}

const saveDigest = async () => {
  if (!canSave.value) return
  saving.value = true
  formError.value = ''
  try {
    if (editingDigest.value) {
      await adminManagementAPI.updateEmailDigest(editingDigest.value.id, form.value)
      showSuccess('Email digest updated successfully')
    } else {
      await adminManagementAPI.createEmailDigest(form.value)
      showSuccess('Email digest created successfully')
    }
    closeModal()
    loadDigests()
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to save email digest'
    formError.value = errorMessage
    showError(errorMessage)
  } finally {
    saving.value = false
  }
}

const sendDigest = (digest) => {
  confirm.show(
    'Send Email Digest',
    `Are you sure you want to send this digest now?`,
    `User ID: ${digest.user_id || digest.user}`,
    async () => {
      try {
        await adminManagementAPI.sendEmailDigest(digest.id)
        showSuccess('Email digest sent successfully')
        loadDigests()
      } catch (error) {
        showError('Failed to send email digest')
      }
    }
  )
}

const sendDueDigests = () => {
  confirm.show(
    'Send All Due Digests',
    'Are you sure you want to send all due email digests?',
    'This will send digests to all users who have pending notifications.',
    async () => {
      sending.value = true
      try {
        await adminManagementAPI.sendDueDigests()
        showSuccess('Due digests sent successfully')
        loadDigests()
      } catch (error) {
        showError('Failed to send due digests')
      } finally {
        sending.value = false
      }
    }
  )
}

const deleteDigest = (digest) => {
  confirm.showDestructive(
    'Delete Email Digest',
    `Are you sure you want to delete this email digest?`,
    `User ID: ${digest.user_id || digest.user}`,
    async () => {
      try {
        await adminManagementAPI.deleteEmailDigest(digest.id)
        showSuccess('Email digest deleted successfully')
        loadDigests()
      } catch (error) {
        showError('Failed to delete email digest')
      }
    }
  )
}

onMounted(() => {
  loadDigests()
})
</script>


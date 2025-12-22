<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Broadcast Messages Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage broadcast email messages to all users</p>
      </div>
      <button
        @click="openCreateModal"
        class="btn btn-primary flex items-center gap-2"
      >
        <span>➕</span>
        <span>Create Broadcast</span>
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Broadcasts</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ stats.total || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Active</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ stats.active || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Total Recipients</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ stats.total_recipients || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-orange-50 to-orange-100 border border-orange-200 dark:from-orange-900/20 dark:to-orange-800/20 dark:border-orange-700">
        <p class="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">Acknowledged</p>
        <p class="text-3xl font-bold text-orange-900 dark:text-orange-100">{{ stats.acknowledged || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search broadcasts by title or message..."
          class="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @input="debouncedSearch"
        />
        <select
          v-model="activeFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadBroadcasts"
        >
          <option value="">All Statuses</option>
          <option value="true">Active</option>
          <option value="false">Inactive</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading broadcasts...</p>
    </div>

    <!-- Broadcasts List -->
    <div v-else class="space-y-4">
      <div
        v-for="broadcast in broadcasts"
        :key="broadcast.id"
        class="card p-4 hover:shadow-lg transition-shadow"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ broadcast.title }}
              </h3>
              <span
                :class="[
                  'px-2 py-1 text-xs font-semibold rounded-full',
                  broadcast.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                  'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                ]"
              >
                {{ broadcast.is_active ? 'Active' : 'Inactive' }}
              </span>
              <span
                v-if="broadcast.event_type"
                class="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300"
              >
                {{ broadcast.event_type }}
              </span>
            </div>
            <p class="text-gray-600 dark:text-gray-400 mb-2 line-clamp-2">{{ broadcast.message }}</p>
            <div class="text-sm text-gray-500 dark:text-gray-400 space-y-1">
              <div v-if="broadcast.sent_at">
                <span class="font-medium">Sent:</span> {{ formatDate(broadcast.sent_at) }}
              </div>
              <div v-if="broadcast.channels">
                <span class="font-medium">Channels:</span> {{ Array.isArray(broadcast.channels) ? broadcast.channels.join(', ') : broadcast.channels }}
              </div>
            </div>
          </div>
          <div class="flex gap-2 ml-4">
            <button
              v-if="!broadcast.sent_at"
              @click="sendBroadcast(broadcast)"
              class="px-3 py-1 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Send Now
            </button>
            <button
              @click="previewBroadcast(broadcast)"
              class="px-3 py-1 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Preview
            </button>
            <button
              @click="viewStats(broadcast)"
              class="px-3 py-1 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              Stats
            </button>
            <button
              @click="editBroadcast(broadcast)"
              class="px-3 py-1 text-sm bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Edit
            </button>
            <button
              @click="deleteBroadcast(broadcast)"
              class="px-3 py-1 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
      <div v-if="broadcasts.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        No broadcast messages found
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <Modal
      :visible="showModal"
      @close="closeModal"
      :title="editingBroadcast ? 'Edit Broadcast Message' : 'Create Broadcast Message'"
      size="lg"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Title *</label>
          <input
            v-model="form.title"
            type="text"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Broadcast title"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Message *</label>
          <textarea
            v-model="form.message"
            rows="6"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Broadcast message content"
          ></textarea>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Event Type</label>
          <input
            v-model="form.event_type"
            type="text"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="e.g., system_announcement"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Channels</label>
          <div class="flex flex-wrap gap-2">
            <label class="flex items-center gap-2">
              <input
                v-model="form.channels"
                type="checkbox"
                value="in_app"
                class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span class="text-sm">In-App</span>
            </label>
            <label class="flex items-center gap-2">
              <input
                v-model="form.channels"
                type="checkbox"
                value="email"
                class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span class="text-sm">Email</span>
            </label>
          </div>
        </div>
        <div>
          <label class="flex items-center gap-2">
            <input
              v-model="form.is_active"
              type="checkbox"
              class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Active</span>
          </label>
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
          @click="saveBroadcast"
          :disabled="saving || !canSave"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ saving ? 'Saving...' : (editingBroadcast ? 'Update' : 'Create') }}
        </button>
      </template>
    </Modal>

    <!-- Stats Modal -->
    <Modal
      :visible="showStatsModal"
      @close="closeStatsModal"
      title="Broadcast Statistics"
    >
      <div v-if="broadcastStats" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Total Recipients</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ broadcastStats.total_recipients || 0 }}</p>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">Acknowledged</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ broadcastStats.acknowledged || 0 }}</p>
          </div>
        </div>
        <div>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Acknowledgement Rate</p>
          <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-4">
            <div
              class="bg-primary-600 h-4 rounded-full transition-all"
              :style="{ width: `${broadcastStats.acknowledgement_rate || 0}%` }"
            ></div>
          </div>
          <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ formatNumber(broadcastStats.acknowledgement_rate) }}%</p>
        </div>
      </div>
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
const broadcasts = ref([])
const stats = ref({})
const searchQuery = ref('')
const activeFilter = ref('')
const showModal = ref(false)
const showStatsModal = ref(false)
const editingBroadcast = ref(null)
const selectedBroadcast = ref(null)
const broadcastStats = ref(null)
const formError = ref('')

const form = ref({
  title: '',
  message: '',
  event_type: '',
  channels: ['in_app', 'email'],
  is_active: true,
})

const canSave = computed(() => {
  return form.value.title.trim() && form.value.message.trim()
})

const debouncedSearch = debounce(() => {
  loadBroadcasts()
}, 300)

const formatNumber = (num) => {
  if (!num && num !== 0) return '0'
  return Number(num).toFixed(2)
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const loadBroadcasts = async () => {
  loading.value = true
  try {
    const params = {}
    if (activeFilter.value !== '') params.is_active = activeFilter.value === 'true'
    
    const response = await adminManagementAPI.listBroadcastMessages(params)
    let allBroadcasts = response.data.results || response.data || []
    
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      allBroadcasts = allBroadcasts.filter(b => 
        (b.title && b.title.toLowerCase().includes(query)) ||
        (b.message && b.message.toLowerCase().includes(query))
      )
    }
    
    broadcasts.value = allBroadcasts
    
    stats.value = {
      total: allBroadcasts.length,
      active: allBroadcasts.filter(b => b.is_active).length,
      total_recipients: allBroadcasts.reduce((sum, b) => sum + (b.total_recipients || 0), 0),
      acknowledged: allBroadcasts.reduce((sum, b) => sum + (b.acknowledged || 0), 0),
    }
  } catch (error) {
    showError('Failed to load broadcast messages')
    console.error('Error loading broadcasts:', error)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingBroadcast.value = null
  form.value = {
    title: '',
    message: '',
    event_type: '',
    channels: ['in_app', 'email'],
    is_active: true,
  }
  formError.value = ''
  showModal.value = true
}

const editBroadcast = (broadcast) => {
  editingBroadcast.value = broadcast
  form.value = {
    title: broadcast.title || '',
    message: broadcast.message || '',
    event_type: broadcast.event_type || '',
    channels: Array.isArray(broadcast.channels) ? broadcast.channels : (broadcast.channels ? [broadcast.channels] : ['in_app', 'email']),
    is_active: broadcast.is_active !== undefined ? broadcast.is_active : true,
  }
  formError.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingBroadcast.value = null
  formError.value = ''
}

const saveBroadcast = async () => {
  if (!canSave.value) return
  saving.value = true
  formError.value = ''
  try {
    if (editingBroadcast.value) {
      await adminManagementAPI.updateBroadcastMessage(editingBroadcast.value.id, form.value)
      showSuccess('Broadcast message updated successfully')
    } else {
      await adminManagementAPI.createBroadcastMessage(form.value)
      showSuccess('Broadcast message created successfully')
    }
    closeModal()
    loadBroadcasts()
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to save broadcast message'
    formError.value = errorMessage
    showError(errorMessage)
  } finally {
    saving.value = false
  }
}

const sendBroadcast = (broadcast) => {
  confirm.show(
    'Send Broadcast Message',
    `Are you sure you want to send this broadcast message now?`,
    `Title: ${broadcast.title}\n\nThis will send the message to all active users.`,
    async () => {
      try {
        await adminManagementAPI.sendBroadcastNow(broadcast.id)
        showSuccess('Broadcast message sent successfully')
        loadBroadcasts()
      } catch (error) {
        showError('Failed to send broadcast message')
      }
    }
  )
}

const previewBroadcast = async (broadcast) => {
  try {
    await adminManagementAPI.previewBroadcast(broadcast.id)
    showSuccess('Preview sent to your email')
  } catch (error) {
    showError('Failed to send preview')
  }
}

const viewStats = async (broadcast) => {
  selectedBroadcast.value = broadcast
  try {
    const response = await adminManagementAPI.getBroadcastStats(broadcast.id)
    broadcastStats.value = response.data
    showStatsModal.value = true
  } catch (error) {
    showError('Failed to load broadcast statistics')
  }
}

const closeStatsModal = () => {
  showStatsModal.value = false
  selectedBroadcast.value = null
  broadcastStats.value = null
}

const deleteBroadcast = (broadcast) => {
  confirm.showDestructive(
    'Delete Broadcast Message',
    `Are you sure you want to delete "${broadcast.title}"?`,
    'This action cannot be undone.',
    async () => {
      try {
        await adminManagementAPI.deleteBroadcastMessage(broadcast.id)
        showSuccess('Broadcast message deleted successfully')
        loadBroadcasts()
      } catch (error) {
        showError('Failed to delete broadcast message')
      }
    }
  )
}

onMounted(() => {
  loadBroadcasts()
})
</script>


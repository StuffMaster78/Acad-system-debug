<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Webhook Endpoints</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage webhook endpoints for notification delivery</p>
      </div>
      <button
        @click="openAddModal"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
      >
        Add Webhook
      </button>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Endpoints</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ webhooks.length }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Active</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ webhooks.filter(w => w.is_active).length }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Total Deliveries</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ totalDeliveries }}</p>
      </div>
    </div>

    <!-- Webhooks Table -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>
    <div v-else class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">URL</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Event Types</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Last Delivery</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="webhook in webhooks"
              :key="webhook.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-800"
            >
              <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                <div class="max-w-xs truncate" :title="webhook.url">
                  {{ webhook.url || 'N/A' }}
                </div>
              </td>
              <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="event in (webhook.event_types || [])"
                    :key="event"
                    class="px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded dark:bg-gray-800 dark:text-gray-300"
                  >
                    {{ event }}
                  </span>
                  <span v-if="!webhook.event_types || webhook.event_types.length === 0" class="text-gray-500 dark:text-gray-400">All events</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'px-2 py-1 text-xs font-semibold rounded-full',
                    webhook.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                    'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                  ]"
                >
                  {{ webhook.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ formatDate(webhook.last_delivery_at || webhook.updated_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                  @click="editWebhook(webhook)"
                  class="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300 mr-4"
                >
                  Edit
                </button>
                <button
                  @click="deleteWebhook(webhook)"
                  class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                >
                  Delete
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="webhooks.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        No webhook endpoints found. Create your first webhook to get started.
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <Modal
      :visible="showModal"
      @close="closeModal"
      :title="editingWebhook ? 'Edit Webhook Endpoint' : 'Add Webhook Endpoint'"
      size="lg"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">URL *</label>
          <input
            v-model="form.url"
            type="url"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="https://your-endpoint.com/webhook"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Event Types</label>
          <textarea
            v-model="eventTypesText"
            rows="4"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="notification.sent&#10;notification.read&#10;notification.created"
          ></textarea>
          <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">Enter one event type per line. Leave empty for all events.</p>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Secret Key</label>
          <input
            v-model="form.secret_key"
            type="text"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Optional secret for webhook verification"
          />
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
          @click="saveWebhook"
          :disabled="saving"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ saving ? 'Saving...' : (editingWebhook ? 'Update' : 'Create') }}
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
import Modal from '@/components/common/Modal.vue'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'
import notificationsAPI from '@/api/notifications'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const saving = ref(false)
const webhooks = ref([])
const showModal = ref(false)
const editingWebhook = ref(null)
const formError = ref('')

const form = ref({
  url: '',
  event_types: [],
  secret_key: '',
  is_active: true,
})

const eventTypesText = ref('')

const totalDeliveries = computed(() => {
  return webhooks.value.reduce((sum, w) => sum + (w.delivery_count || w.successful_deliveries || 0), 0)
})

const formatDate = (date) => {
  if (!date) return 'Never'
  return new Date(date).toLocaleString()
}

const loadWebhooks = async () => {
  loading.value = true
  try {
    const response = await notificationsAPI.listWebhookEndpoints()
    webhooks.value = response.data.results || response.data || []
  } catch (error) {
    showError('Failed to load webhook endpoints')
    console.error('Error loading webhooks:', error)
  } finally {
    loading.value = false
  }
}

const openAddModal = () => {
  editingWebhook.value = null
  form.value = {
    url: '',
    event_types: [],
    secret_key: '',
    is_active: true,
  }
  eventTypesText.value = ''
  formError.value = ''
  showModal.value = true
}

const editWebhook = (webhook) => {
  editingWebhook.value = webhook
  form.value = {
    url: webhook.url || '',
    event_types: webhook.event_types || [],
    secret_key: webhook.secret_key || '',
    is_active: webhook.is_active !== undefined ? webhook.is_active : true,
  }
  eventTypesText.value = (webhook.event_types || []).join('\n')
  formError.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingWebhook.value = null
  formError.value = ''
}

const saveWebhook = async () => {
  saving.value = true
  formError.value = ''
  
  try {
    // Parse event types from text
    form.value.event_types = eventTypesText.value
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0)
    
    if (editingWebhook.value) {
      await notificationsAPI.updateWebhookEndpoint(editingWebhook.value.id, form.value)
      showSuccess('Webhook endpoint updated successfully')
    } else {
      await notificationsAPI.createWebhookEndpoint(form.value)
      showSuccess('Webhook endpoint created successfully')
    }
    
    closeModal()
    loadWebhooks()
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to save webhook endpoint'
    formError.value = errorMessage
    showError(errorMessage)
  } finally {
    saving.value = false
  }
}

const deleteWebhook = (webhook) => {
  confirm.showDestructive(
    'Delete Webhook Endpoint',
    `Are you sure you want to delete this webhook endpoint?`,
    `URL: ${webhook.url}`,
    async () => {
      try {
        await notificationsAPI.deleteWebhookEndpoint(webhook.id)
        showSuccess('Webhook endpoint deleted successfully')
        loadWebhooks()
      } catch (error) {
        showError('Failed to delete webhook endpoint')
      }
    }
  )
}

onMounted(() => {
  loadWebhooks()
})
</script>


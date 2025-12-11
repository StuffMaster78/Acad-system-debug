<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Dashboard Widgets</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage customizable dashboard widgets for analytics</p>
      </div>
      <button
        @click="openAddModal"
        class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
      >
        Add Widget
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Widgets</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ widgets.length }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Visible</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ widgets.filter(w => w.is_visible).length }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 dark:from-orange-900/20 dark:to-orange-800/20 dark:border-orange-700">
        <p class="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">Hidden</p>
        <p class="text-3xl font-bold text-orange-900 dark:text-orange-100">{{ widgets.filter(w => !w.is_visible).length }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Widget Types</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ uniqueTypes.length }}</p>
      </div>
    </div>

    <!-- Widgets Grid -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading widgets...</p>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="widget in sortedWidgets"
        :key="widget.id"
        :class="[
          'card p-4 transition-all',
          widget.is_visible ? '' : 'opacity-60'
        ]"
      >
        <div class="flex items-start justify-between mb-3">
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">{{ widget.title }}</h3>
            <p class="text-sm text-gray-500 dark:text-gray-400">{{ formatWidgetType(widget.widget_type) }}</p>
          </div>
          <div class="flex gap-2">
            <span
              :class="[
                'px-2 py-1 text-xs font-semibold rounded-full',
                widget.is_visible ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
              ]"
            >
              {{ widget.is_visible ? 'Visible' : 'Hidden' }}
            </span>
          </div>
        </div>
        <div class="text-xs text-gray-500 dark:text-gray-400 mb-3">
          Position: {{ widget.position || 0 }} | Created: {{ formatDate(widget.created_at) }}
        </div>
        <div v-if="widget.config && Object.keys(widget.config).length > 0" class="mb-3">
          <p class="text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Configuration:</p>
          <pre class="text-xs bg-gray-50 dark:bg-gray-800 p-2 rounded overflow-auto max-h-24">{{ JSON.stringify(widget.config, null, 2) }}</pre>
        </div>
        <div class="flex gap-2">
          <button
            @click="editWidget(widget)"
            class="flex-1 px-3 py-2 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
          >
            Edit
          </button>
          <button
            @click="toggleVisibility(widget)"
            class="px-3 py-2 text-sm bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            {{ widget.is_visible ? 'Hide' : 'Show' }}
          </button>
          <button
            @click="deleteWidget(widget)"
            class="px-3 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
          >
            Delete
          </button>
        </div>
      </div>
      <div v-if="widgets.length === 0" class="col-span-full text-center py-12 text-gray-500 dark:text-gray-400">
        No widgets found. Create your first widget to get started.
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <Modal
      :visible="showModal"
      @close="closeModal"
      :title="editingWidget ? 'Edit Widget' : 'Add Widget'"
      size="lg"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Title</label>
          <input
            v-model="form.title"
            type="text"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Widget title"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Widget Type</label>
          <select
            v-model="form.widget_type"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          >
            <option value="points_issued">Points Issued Over Time</option>
            <option value="redemptions_trend">Redemptions Trend</option>
            <option value="tier_distribution">Loyalty Tier Distribution</option>
            <option value="top_redemptions">Top Redemption Items</option>
            <option value="engagement_rate">Client Engagement Rate</option>
            <option value="points_balance">Total Points Balance</option>
            <option value="conversion_rate">Points to Wallet Conversion</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Position</label>
          <input
            v-model.number="form.position"
            type="number"
            min="0"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="0"
          />
        </div>
        <div>
          <label class="flex items-center gap-2">
            <input
              v-model="form.is_visible"
              type="checkbox"
              class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Visible</span>
          </label>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Configuration (JSON)</label>
          <textarea
            v-model="configJson"
            rows="6"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white font-mono text-sm"
            placeholder='{"date_range": "30d", "chart_type": "line"}'
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
          @click="saveWidget"
          :disabled="saving"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ saving ? 'Saving...' : (editingWidget ? 'Update' : 'Create') }}
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
import loyaltyAPI from '@/api/loyalty-management'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const saving = ref(false)
const widgets = ref([])
const showModal = ref(false)
const editingWidget = ref(null)
const formError = ref('')

const form = ref({
  title: '',
  widget_type: 'points_issued',
  position: 0,
  is_visible: true,
  config: {},
})

const configJson = ref('{}')

const sortedWidgets = computed(() => {
  return [...widgets.value].sort((a, b) => (a.position || 0) - (b.position || 0))
})

const uniqueTypes = computed(() => {
  return [...new Set(widgets.value.map(w => w.widget_type))]
})

const formatWidgetType = (type) => {
  if (!type) return 'Unknown'
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const loadWidgets = async () => {
  loading.value = true
  try {
    const response = await loyaltyAPI.listWidgets()
    widgets.value = response.data.results || response.data || []
  } catch (error) {
    showError('Failed to load widgets')
    console.error('Error loading widgets:', error)
  } finally {
    loading.value = false
  }
}

const openAddModal = () => {
  editingWidget.value = null
  form.value = {
    title: '',
    widget_type: 'points_issued',
    position: 0,
    is_visible: true,
    config: {},
  }
  configJson.value = '{}'
  formError.value = ''
  showModal.value = true
}

const editWidget = (widget) => {
  editingWidget.value = widget
  form.value = {
    title: widget.title || '',
    widget_type: widget.widget_type || 'points_issued',
    position: widget.position || 0,
    is_visible: widget.is_visible !== undefined ? widget.is_visible : true,
    config: widget.config || {},
  }
  configJson.value = JSON.stringify(widget.config || {}, null, 2)
  formError.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingWidget.value = null
  formError.value = ''
}

const saveWidget = async () => {
  saving.value = true
  formError.value = ''
  
  try {
    // Parse config JSON
    try {
      form.value.config = JSON.parse(configJson.value || '{}')
    } catch (e) {
      formError.value = 'Invalid JSON in configuration'
      saving.value = false
      return
    }
    
    if (editingWidget.value) {
      await loyaltyAPI.updateWidget(editingWidget.value.id, form.value)
      showSuccess('Widget updated successfully')
    } else {
      await loyaltyAPI.createWidget(form.value)
      showSuccess('Widget created successfully')
    }
    
    closeModal()
    loadWidgets()
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to save widget'
    formError.value = errorMessage
    showError(errorMessage)
  } finally {
    saving.value = false
  }
}

const toggleVisibility = async (widget) => {
  try {
    await loyaltyAPI.updateWidget(widget.id, { is_visible: !widget.is_visible })
    showSuccess(`Widget ${widget.is_visible ? 'hidden' : 'shown'} successfully`)
    loadWidgets()
  } catch (error) {
    showError('Failed to update widget visibility')
  }
}

const deleteWidget = (widget) => {
  confirm.showDestructive(
    'Delete Widget',
    `Are you sure you want to delete "${widget.title}"?`,
    'This action cannot be undone.',
    async () => {
      try {
        await loyaltyAPI.deleteWidget(widget.id)
        showSuccess('Widget deleted successfully')
        loadWidgets()
      } catch (error) {
        showError('Failed to delete widget')
      }
    }
  )
}

onMounted(() => {
  loadWidgets()
})
</script>


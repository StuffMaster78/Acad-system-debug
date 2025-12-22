<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Class Analytics</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Analytics for class bundles and bulk orders</p>
      </div>
      <button
        @click="openCreateModal"
        class="btn btn-primary flex items-center gap-2"
      >
        <span>➕</span>
        <span>Create Analytics</span>
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-linear-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Classes</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ stats.total_classes || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Total Orders</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ stats.total_orders || 0 }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Total Revenue</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">${{ formatCurrency(stats.total_revenue) }}</p>
      </div>
      <div class="card p-4 bg-linear-to-br from-orange-50 to-orange-100 border border-orange-200 dark:from-orange-900/20 dark:to-orange-800/20 dark:border-orange-700">
        <p class="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">Avg Orders/Class</p>
        <p class="text-3xl font-bold text-orange-900 dark:text-orange-100">{{ formatNumber(stats.avg_orders_per_class) }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by class name..."
          class="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @input="debouncedSearch"
        />
        <input
          v-model="periodStart"
          type="date"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadAnalytics"
        />
        <input
          v-model="periodEnd"
          type="date"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadAnalytics"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading class analytics...</p>
    </div>

    <!-- Analytics List -->
    <div v-else class="space-y-4">
      <div
        v-for="analytics in analyticsList"
        :key="analytics.id"
        class="card p-4 hover:shadow-lg transition-shadow"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                {{ analytics.class_name || 'Unnamed Class' }}
              </h3>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mb-2">
              <div>
                <span class="text-gray-500 dark:text-gray-400">Period:</span>
                <span class="ml-2 font-medium text-gray-900 dark:text-white">
                  {{ formatDate(analytics.period_start) }} - {{ formatDate(analytics.period_end) }}
                </span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">Total Orders:</span>
                <span class="ml-2 font-medium text-gray-900 dark:text-white">{{ analytics.total_orders || 0 }}</span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">Total Revenue:</span>
                <span class="ml-2 font-medium text-gray-900 dark:text-white">${{ formatCurrency(analytics.total_revenue || 0) }}</span>
              </div>
              <div>
                <span class="text-gray-500 dark:text-gray-400">Avg Order Value:</span>
                <span class="ml-2 font-medium text-gray-900 dark:text-white">${{ formatCurrency(analytics.avg_order_value || 0) }}</span>
              </div>
            </div>
            <div v-if="analytics.website_name" class="text-xs text-gray-500 dark:text-gray-400">
              Website: {{ analytics.website_name }}
            </div>
          </div>
          <div class="flex gap-2 ml-4">
            <button
              @click="recalculateAnalytics(analytics)"
              class="px-3 py-1 text-sm bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Recalculate
            </button>
            <button
              @click="generateReport(analytics)"
              class="px-3 py-1 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Generate Report
            </button>
            <button
              @click="editAnalytics(analytics)"
              class="px-3 py-1 text-sm bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              Edit
            </button>
            <button
              @click="deleteAnalytics(analytics)"
              class="px-3 py-1 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
      <div v-if="analyticsList.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        No class analytics found
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <Modal
      :visible="showModal"
      @close="closeModal"
      :title="editingAnalytics ? 'Edit Class Analytics' : 'Create Class Analytics'"
      size="lg"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Class Name *</label>
          <input
            v-model="form.class_name"
            type="text"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Enter class name"
          />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Period Start *</label>
            <input
              v-model="form.period_start"
              type="date"
              class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Period End *</label>
            <input
              v-model="form.period_end"
              type="date"
              class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            />
          </div>
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
          @click="saveAnalytics"
          :disabled="saving || !canSave"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ saving ? 'Saving...' : (editingAnalytics ? 'Update' : 'Create') }}
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
import { analyticsAPI } from '@/api/analytics'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const saving = ref(false)
const analyticsList = ref([])
const stats = ref({})
const searchQuery = ref('')
const periodStart = ref('')
const periodEnd = ref('')
const showModal = ref(false)
const editingAnalytics = ref(null)
const formError = ref('')

const form = ref({
  class_name: '',
  period_start: '',
  period_end: '',
})

const canSave = computed(() => {
  return form.value.class_name.trim() && form.value.period_start && form.value.period_end
})

const debouncedSearch = debounce(() => {
  loadAnalytics()
}, 300)

const formatNumber = (num) => {
  if (!num && num !== 0) return '0'
  return Number(num).toFixed(1)
}

const formatCurrency = (amount) => {
  if (!amount && amount !== 0) return '0.00'
  return Number(amount).toFixed(2)
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

const loadAnalytics = async () => {
  loading.value = true
  try {
    const params = {}
    if (periodStart.value) params.period_start = periodStart.value
    if (periodEnd.value) params.period_end = periodEnd.value
    
    const response = await analyticsAPI.class.list(params)
    let allAnalytics = response.data.results || response.data || []
    
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      allAnalytics = allAnalytics.filter(a => 
        (a.class_name && a.class_name.toLowerCase().includes(query))
      )
    }
    
    analyticsList.value = allAnalytics
    
    stats.value = {
      total_classes: allAnalytics.length,
      total_orders: allAnalytics.reduce((sum, a) => sum + (a.total_orders || 0), 0),
      total_revenue: allAnalytics.reduce((sum, a) => sum + (a.total_revenue || 0), 0),
      avg_orders_per_class: allAnalytics.length > 0 ? 
        allAnalytics.reduce((sum, a) => sum + (a.total_orders || 0), 0) / allAnalytics.length : 0,
    }
  } catch (error) {
    showError('Failed to load class analytics')
    console.error('Error loading analytics:', error)
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  editingAnalytics.value = null
  const today = new Date()
  const thirtyDaysAgo = new Date(today)
  thirtyDaysAgo.setDate(today.getDate() - 30)
  
  form.value = {
    class_name: '',
    period_start: thirtyDaysAgo.toISOString().split('T')[0],
    period_end: today.toISOString().split('T')[0],
  }
  formError.value = ''
  showModal.value = true
}

const editAnalytics = (analytics) => {
  editingAnalytics.value = analytics
  form.value = {
    class_name: analytics.class_name || '',
    period_start: analytics.period_start ? new Date(analytics.period_start).toISOString().split('T')[0] : '',
    period_end: analytics.period_end ? new Date(analytics.period_end).toISOString().split('T')[0] : '',
  }
  formError.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingAnalytics.value = null
  formError.value = ''
}

const saveAnalytics = async () => {
  if (!canSave.value) return
  saving.value = true
  formError.value = ''
  try {
    if (editingAnalytics.value) {
      await analyticsAPI.class.update(editingAnalytics.value.id, form.value)
      showSuccess('Class analytics updated successfully')
    } else {
      await analyticsAPI.class.create(form.value)
      showSuccess('Class analytics created successfully')
    }
    closeModal()
    loadAnalytics()
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to save class analytics'
    formError.value = errorMessage
    showError(errorMessage)
  } finally {
    saving.value = false
  }
}

const recalculateAnalytics = (analytics) => {
  confirm.show(
    'Recalculate Analytics',
    `Are you sure you want to recalculate analytics for "${analytics.class_name}"?`,
    'This will update all metrics based on current data.',
    async () => {
      try {
        await analyticsAPI.class.recalculate(analytics.id)
        showSuccess('Analytics recalculated successfully')
        loadAnalytics()
      } catch (error) {
        showError('Failed to recalculate analytics')
      }
    }
  )
}

const generateReport = async (analytics) => {
  try {
    await analyticsAPI.class.generateReport(analytics.id, {})
    showSuccess('Performance report generated successfully')
  } catch (error) {
    showError('Failed to generate report')
  }
}

const deleteAnalytics = (analytics) => {
  confirm.showDestructive(
    'Delete Class Analytics',
    `Are you sure you want to delete analytics for "${analytics.class_name}"?`,
    'This action cannot be undone.',
    async () => {
      try {
        await analyticsAPI.class.delete(analytics.id)
        showSuccess('Class analytics deleted successfully')
        loadAnalytics()
      } catch (error) {
        showError('Failed to delete analytics')
      }
    }
  )
}

onMounted(() => {
  loadAnalytics()
})
</script>


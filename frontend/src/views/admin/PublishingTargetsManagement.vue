<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Publishing Targets Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage publishing targets and track content goals</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create Target
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Targets</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ stats.total }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">On Track</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ stats.on_track }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Behind</p>
        <p class="text-3xl font-bold text-yellow-600 dark:text-yellow-400">{{ stats.behind }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Completed</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ stats.completed }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 border border-gray-200 dark:border-gray-700">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Search</label>
          <input
            v-model="filters.search"
            @input="debouncedSearch"
            type="text"
            placeholder="Search targets..."
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Website</label>
          <select
            v-model="filters.website"
            @change="loadTargets"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option value="">All Websites</option>
            <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Targets List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else-if="!targets.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        <p class="mt-2 text-sm font-medium">No publishing targets found</p>
        <button @click="showCreateModal = true" class="mt-4 btn btn-primary">Create Your First Target</button>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Period</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Website</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Target</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Published</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Progress</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="target in targets" :key="target.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ formatPeriod(target.period_start, target.period_end) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ target.website?.name || target.website_id || '—' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ formatNumber(target.target_count || 0) }} posts
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ formatNumber(target.published_count || 0) }} posts
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 mr-2">
                    <div
                      :class="getProgressColor(target)"
                      class="h-2 rounded-full"
                      :style="{ width: getProgressPercent(target) + '%' }"
                    ></div>
                  </div>
                  <span class="text-xs text-gray-500 dark:text-gray-400">{{ getProgressPercent(target) }}%</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusBadgeClass(target)" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ getStatusText(target) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button @click="viewTarget(target)" class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">View</button>
                  <button @click="editTarget(target)" class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300">Edit</button>
                  <button @click="deleteTarget(target)" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || editingTarget" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="closeModal">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto m-4">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            {{ editingTarget ? 'Edit Publishing Target' : 'Create Publishing Target' }}
          </h3>
        </div>
        <form @submit.prevent="saveTarget" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Website *</label>
            <select
              v-model.number="targetForm.website"
              required
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            >
              <option value="">Select Website</option>
              <option v-for="site in websites" :key="site.id" :value="site.id">{{ site.name }}</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Period Start *</label>
              <input
                v-model="targetForm.period_start"
                type="date"
                required
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Period End *</label>
              <input
                v-model="targetForm.period_end"
                type="date"
                required
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Target Count *</label>
            <input
              v-model.number="targetForm.target_count"
              type="number"
              min="1"
              required
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Number of posts to publish in this period</p>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Threshold (%)</label>
            <input
              v-model.number="targetForm.threshold_percentage"
              type="number"
              min="0"
              max="100"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Alert threshold percentage (optional)</p>
          </div>
          <div class="flex gap-3 pt-4">
            <button type="submit" :disabled="saving" class="btn btn-primary flex-1">
              {{ saving ? 'Saving...' : (editingTarget ? 'Update' : 'Create') }}
            </button>
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
          </div>
        </form>
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
import { ref, computed, onMounted, watch } from 'vue'
import blogPagesAPI from '@/api/blog-pages'
import websitesAPI from '@/api/websites'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { debounce } from '@/utils/debounce'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const { showSuccess, showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const saving = ref(false)
const targets = ref([])
const websites = ref([])
const stats = ref({ total: 0, on_track: 0, behind: 0, completed: 0 })
const showCreateModal = ref(false)
const editingTarget = ref(null)

const filters = ref({
  search: '',
  website: '',
})

const targetForm = ref({
  website: null,
  period_start: '',
  period_end: '',
  target_count: 10,
  threshold_percentage: 80,
})

const debouncedSearch = debounce(() => {
  loadTargets()
}, 300)

const loadTargets = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.website) params.website = filters.value.website
    
    const res = await blogPagesAPI.getPublishingTargets(params)
    targets.value = res.data?.results || res.data || []
    
    // Calculate stats
    stats.value = {
      total: targets.value.length,
      on_track: targets.value.filter(t => {
        const progress = getProgressPercent(t)
        return progress >= 80 && progress < 100
      }).length,
      behind: targets.value.filter(t => getProgressPercent(t) < 80).length,
      completed: targets.value.filter(t => getProgressPercent(t) >= 100).length,
    }
  } catch (error) {
    console.error('Failed to load targets:', error)
    showError('Failed to load targets: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const loadWebsites = async () => {
  try {
    const res = await websitesAPI.listWebsites({ is_active: true })
    websites.value = res.data?.results || res.data || []
  } catch (error) {
    console.error('Failed to load websites:', error)
  }
}

const saveTarget = async () => {
  saving.value = true
  try {
    const data = { ...targetForm.value }
    
    if (editingTarget.value) {
      await blogPagesAPI.updatePublishingTarget(editingTarget.value.id, data)
      showSuccess('Publishing target updated successfully')
    } else {
      await blogPagesAPI.createPublishingTarget(data)
      showSuccess('Publishing target created successfully')
    }
    
    closeModal()
    await loadTargets()
  } catch (error) {
    console.error('Failed to save target:', error)
    showError('Failed to save target: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const editTarget = (target) => {
  editingTarget.value = target
  targetForm.value = {
    website: target.website?.id || target.website_id || null,
    period_start: target.period_start ? new Date(target.period_start).toISOString().split('T')[0] : '',
    period_end: target.period_end ? new Date(target.period_end).toISOString().split('T')[0] : '',
    target_count: target.target_count || 10,
    threshold_percentage: target.threshold_percentage || 80,
  }
  showCreateModal.value = true
}

const viewTarget = (target) => {
  // Show target details
  alert(`Target: ${formatPeriod(target.period_start, target.period_end)}\nProgress: ${getProgressPercent(target)}%\nPublished: ${target.published_count || 0}/${target.target_count || 0}`)
}

const deleteTarget = async (target) => {
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to delete this publishing target?',
    'Delete Publishing Target',
    {
      details: 'This action cannot be undone. The target and its tracking data will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await blogPagesAPI.deletePublishingTarget(target.id)
    showSuccess('Publishing target deleted successfully')
    await loadTargets()
  } catch (error) {
    console.error('Failed to delete target:', error)
    showError('Failed to delete target: ' + (error.response?.data?.detail || error.message))
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingTarget.value = null
  targetForm.value = {
    website: null,
    period_start: '',
    period_end: '',
    target_count: 10,
    threshold_percentage: 80,
  }
}

const resetFilters = () => {
  filters.value = { search: '', website: '' }
  loadTargets()
}

const formatPeriod = (start, end) => {
  if (!start || !end) return '—'
  const startDate = new Date(start).toLocaleDateString()
  const endDate = new Date(end).toLocaleDateString()
  return `${startDate} - ${endDate}`
}

const getProgressPercent = (target) => {
  if (!target.target_count || target.target_count === 0) return 0
  const percent = ((target.published_count || 0) / target.target_count) * 100
  return Math.min(100, Math.round(percent))
}

const getProgressColor = (target) => {
  const percent = getProgressPercent(target)
  if (percent >= 100) return 'bg-green-600'
  if (percent >= 80) return 'bg-blue-600'
  if (percent >= 50) return 'bg-yellow-600'
  return 'bg-red-600'
}

const getStatusBadgeClass = (target) => {
  const percent = getProgressPercent(target)
  if (percent >= 100) return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
  if (percent >= 80) return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
  if (percent >= 50) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
  return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
}

const getStatusText = (target) => {
  const percent = getProgressPercent(target)
  if (percent >= 100) return 'Completed'
  if (percent >= 80) return 'On Track'
  if (percent >= 50) return 'Behind'
  return 'Critical'
}

const formatNumber = (value) => {
  return parseInt(value || 0).toLocaleString()
}

onMounted(async () => {
  await Promise.all([loadTargets(), loadWebsites()])
})
</script>

<style scoped>
@reference "tailwindcss";
.btn {
  @apply px-4 py-2 rounded-lg font-medium transition-colors;
}
.btn-primary {
  @apply bg-blue-600 text-white hover:bg-blue-700;
}
.btn-secondary {
  @apply bg-gray-200 text-gray-800 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:hover:bg-gray-600;
}
</style>



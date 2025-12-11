<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Writer Portfolios Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage writer portfolios and showcase their work</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Portfolios</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ stats.total || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Enabled</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ stats.enabled || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Public</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ stats.public || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 dark:from-orange-900/20 dark:to-orange-800/20 dark:border-orange-700">
        <p class="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">Total Samples</p>
        <p class="text-3xl font-bold text-orange-900 dark:text-orange-100">{{ stats.total_samples || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by writer email or name..."
          class="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @input="debouncedSearch"
        />
        <select
          v-model="enabledFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadPortfolios"
        >
          <option value="">All Statuses</option>
          <option value="true">Enabled</option>
          <option value="false">Disabled</option>
        </select>
        <select
          v-model="visibilityFilter"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadPortfolios"
        >
          <option value="">All Visibility</option>
          <option value="private">Private</option>
          <option value="clients_only">Clients Only</option>
          <option value="public">Public</option>
        </select>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading portfolios...</p>
    </div>

    <!-- Portfolios Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="portfolio in portfolios"
        :key="portfolio.id"
        class="card p-4 hover:shadow-lg transition-shadow"
      >
        <div class="flex justify-between items-start mb-3">
          <div class="flex-1">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">
              {{ portfolio.writer_email || portfolio.writer?.email || portfolio.writer?.username || portfolio.writer_id || 'N/A' }}
            </h3>
            <div class="flex flex-wrap items-center gap-2 mb-2">
              <span
                :class="[
                  'px-2 py-1 text-xs font-semibold rounded-full',
                  portfolio.is_enabled ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' :
                  'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                ]"
              >
                {{ portfolio.is_enabled ? 'Enabled' : 'Disabled' }}
              </span>
              <span
                :class="[
                  'px-2 py-1 text-xs font-semibold rounded-full',
                  portfolio.visibility === 'public' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300' :
                  portfolio.visibility === 'clients_only' ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300' :
                  'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300'
                ]"
              >
                {{ portfolio.visibility?.replace('_', ' ') || 'Private' }}
              </span>
            </div>
            <p v-if="portfolio.bio" class="text-sm text-gray-600 dark:text-gray-400 mb-2 line-clamp-2">
              {{ portfolio.bio }}
            </p>
            <div class="text-xs text-gray-500 dark:text-gray-400 space-y-1">
              <div v-if="portfolio.total_orders_completed !== undefined">
                Orders: {{ portfolio.total_orders_completed }}
              </div>
              <div v-if="portfolio.average_rating">
                Rating: {{ formatNumber(portfolio.average_rating) }}/5.0
              </div>
              <div v-if="portfolio.on_time_delivery_rate">
                On-Time: {{ formatNumber(portfolio.on_time_delivery_rate) }}%
              </div>
              <div v-if="portfolio.sample_works">
                Samples: {{ Array.isArray(portfolio.sample_works) ? portfolio.sample_works.length : 0 }}
              </div>
            </div>
          </div>
          <div class="flex gap-2 ml-4">
            <button
              @click="editPortfolio(portfolio)"
              class="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300"
              title="Edit"
            >
              ✏️
            </button>
            <button
              @click="viewSamples(portfolio)"
              class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
              title="View Samples"
            >
              📄
            </button>
            <button
              @click="updateStats(portfolio)"
              class="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300"
              title="Update Stats"
            >
              🔄
            </button>
          </div>
        </div>
      </div>
      <div v-if="portfolios.length === 0" class="col-span-full text-center py-12 text-gray-500 dark:text-gray-400">
        No portfolios found
      </div>
    </div>

    <!-- Edit Portfolio Modal -->
    <Modal
      :visible="showModal"
      @close="closeModal"
      title="Edit Portfolio"
      size="lg"
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Bio</label>
          <textarea
            v-model="form.bio"
            rows="4"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Writer bio/introduction"
          ></textarea>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Years of Experience</label>
          <input
            v-model.number="form.years_of_experience"
            type="number"
            min="0"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="0"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Education</label>
          <textarea
            v-model="form.education"
            rows="2"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            placeholder="Educational background"
          ></textarea>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Visibility</label>
          <select
            v-model="form.visibility"
            class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          >
            <option value="private">Private</option>
            <option value="clients_only">Clients Only</option>
            <option value="public">Public</option>
          </select>
        </div>
        <div class="space-y-2">
          <label class="flex items-center gap-2">
            <input
              v-model="form.is_enabled"
              type="checkbox"
              class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Enabled</span>
          </label>
          <label class="flex items-center gap-2">
            <input
              v-model="form.show_contact_info"
              type="checkbox"
              class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Show Contact Info</span>
          </label>
          <label class="flex items-center gap-2">
            <input
              v-model="form.show_order_history"
              type="checkbox"
              class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Show Order History</span>
          </label>
          <label class="flex items-center gap-2">
            <input
              v-model="form.show_earnings"
              type="checkbox"
              class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Show Earnings</span>
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
          @click="savePortfolio"
          :disabled="saving"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ saving ? 'Saving...' : 'Update' }}
        </button>
      </template>
    </Modal>

    <!-- Samples Modal -->
    <Modal
      :visible="showSamplesModal"
      @close="closeSamplesModal"
      :title="`Portfolio Samples - ${selectedPortfolio?.writer_email || 'Writer'}`"
      size="xl"
    >
      <div class="space-y-4">
        <div class="flex justify-end">
          <button
            @click="openAddSampleModal"
            class="btn btn-primary text-sm"
          >
            Add Sample
          </button>
        </div>
        <div v-if="samplesLoading" class="text-center py-8">
          <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
        <div v-else-if="samples.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          No samples found
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="sample in samples"
            :key="sample.id"
            class="p-3 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <h4 class="font-medium text-gray-900 dark:text-white">{{ sample.title }}</h4>
                <p v-if="sample.description" class="text-sm text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
                  {{ sample.description }}
                </p>
                <div class="flex items-center gap-2 mt-2">
                  <span
                    v-if="sample.is_featured"
                    class="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300"
                  >
                    Featured
                  </span>
                  <span
                    v-if="sample.subject_name"
                    class="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300"
                  >
                    {{ sample.subject_name }}
                  </span>
                </div>
              </div>
              <div class="flex gap-2 ml-4">
                <button
                  @click="toggleFeatured(sample)"
                  class="px-2 py-1 text-xs bg-yellow-600 text-white rounded hover:bg-yellow-700 transition-colors"
                >
                  {{ sample.is_featured ? 'Unfeature' : 'Feature' }}
                </button>
                <button
                  @click="deleteSample(sample)"
                  class="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
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
import writerManagementAPI from '@/api/writer-management'

const { success: showSuccess, error: showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const saving = ref(false)
const portfolios = ref([])
const samples = ref([])
const samplesLoading = ref(false)
const stats = ref({})
const searchQuery = ref('')
const enabledFilter = ref('')
const visibilityFilter = ref('')
const showModal = ref(false)
const showSamplesModal = ref(false)
const editingPortfolio = ref(null)
const selectedPortfolio = ref(null)
const formError = ref('')

const form = ref({
  bio: '',
  years_of_experience: null,
  education: '',
  visibility: 'clients_only',
  is_enabled: false,
  show_contact_info: false,
  show_order_history: false,
  show_earnings: false,
})

const debouncedSearch = debounce(() => {
  loadPortfolios()
}, 300)

const formatNumber = (num) => {
  if (!num && num !== 0) return '0'
  return Number(num).toFixed(2)
}

const loadPortfolios = async () => {
  loading.value = true
  try {
    const params = {}
    if (enabledFilter.value !== '') params.is_enabled = enabledFilter.value === 'true'
    if (visibilityFilter.value) params.visibility = visibilityFilter.value
    
    const response = await writerManagementAPI.listPortfolios(params)
    let allPortfolios = response.data.results || response.data || []
    
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      allPortfolios = allPortfolios.filter(p => 
        (p.writer_email && p.writer_email.toLowerCase().includes(query)) ||
        (p.writer && String(p.writer).toLowerCase().includes(query))
      )
    }
    
    portfolios.value = allPortfolios
    
    stats.value = {
      total: allPortfolios.length,
      enabled: allPortfolios.filter(p => p.is_enabled).length,
      public: allPortfolios.filter(p => p.visibility === 'public').length,
      total_samples: allPortfolios.reduce((sum, p) => sum + (Array.isArray(p.sample_works) ? p.sample_works.length : 0), 0),
    }
  } catch (error) {
    showError('Failed to load portfolios')
    console.error('Error loading portfolios:', error)
  } finally {
    loading.value = false
  }
}

const editPortfolio = (portfolio) => {
  editingPortfolio.value = portfolio
  form.value = {
    bio: portfolio.bio || '',
    years_of_experience: portfolio.years_of_experience || null,
    education: portfolio.education || '',
    visibility: portfolio.visibility || 'clients_only',
    is_enabled: portfolio.is_enabled !== undefined ? portfolio.is_enabled : false,
    show_contact_info: portfolio.show_contact_info || false,
    show_order_history: portfolio.show_order_history || false,
    show_earnings: portfolio.show_earnings || false,
  }
  formError.value = ''
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingPortfolio.value = null
  formError.value = ''
}

const savePortfolio = async () => {
  saving.value = true
  formError.value = ''
  try {
    await writerManagementAPI.updatePortfolio(editingPortfolio.value.id, form.value)
    showSuccess('Portfolio updated successfully')
    closeModal()
    loadPortfolios()
  } catch (error) {
    const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Failed to update portfolio'
    formError.value = errorMessage
    showError(errorMessage)
  } finally {
    saving.value = false
  }
}

const updateStats = (portfolio) => {
  confirm.show(
    'Update Statistics',
    `Update statistics for this portfolio?`,
    'This will recalculate orders completed, ratings, and on-time delivery rates.',
    async () => {
      try {
        await writerManagementAPI.updatePortfolio?.(portfolio.id, { update_statistics: true })
        showSuccess('Portfolio statistics updated successfully')
        loadPortfolios()
      } catch (error) {
        showError('Failed to update statistics')
      }
    }
  )
}

const viewSamples = async (portfolio) => {
  selectedPortfolio.value = portfolio
  samplesLoading.value = true
  try {
    const response = await writerManagementAPI.listPortfolioSamples({ writer: portfolio.writer })
    samples.value = response.data.results || response.data || []
    showSamplesModal.value = true
  } catch (error) {
    showError('Failed to load portfolio samples')
  } finally {
    samplesLoading.value = false
  }
}

const closeSamplesModal = () => {
  showSamplesModal.value = false
  selectedPortfolio.value = null
  samples.value = []
}

const openAddSampleModal = () => {
  // Could open a modal to add samples
  showError('Add sample functionality coming soon')
}

const toggleFeatured = async (sample) => {
  try {
    await writerManagementAPI.updatePortfolioSample?.(sample.id, { is_featured: !sample.is_featured })
    showSuccess('Sample featured status updated')
    await viewSamples(selectedPortfolio.value)
  } catch (error) {
    showError('Failed to update sample')
  }
}

const deleteSample = (sample) => {
  confirm.showDestructive(
    'Delete Sample',
    `Are you sure you want to delete "${sample.title}"?`,
    'This action cannot be undone.',
    async () => {
      try {
        await writerManagementAPI.deletePortfolioSample(sample.id)
        showSuccess('Sample deleted successfully')
        await viewSamples(selectedPortfolio.value)
      } catch (error) {
        showError('Failed to delete sample')
      }
    }
  )
}

onMounted(() => {
  loadPortfolios()
})
</script>


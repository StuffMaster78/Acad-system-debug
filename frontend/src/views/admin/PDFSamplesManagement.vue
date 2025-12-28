<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">PDF Samples Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage PDF samples and sections for service pages</p>
      </div>
      <div class="flex gap-2">
        <button @click="activeTab = 'samples'" :class="['btn', activeTab === 'samples' ? 'btn-primary' : 'btn-secondary']">
          PDF Samples
        </button>
        <button @click="activeTab = 'sections'" :class="['btn', activeTab === 'sections' ? 'btn-primary' : 'btn-secondary']">
          Sections
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Samples</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ stats.total_samples }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Sections</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ stats.total_sections }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Downloads</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ formatNumber(stats.total_downloads) }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Active Samples</p>
        <p class="text-3xl font-bold text-purple-600 dark:text-purple-400">{{ stats.active_samples }}</p>
      </div>
    </div>

    <!-- PDF Samples Tab -->
    <div v-if="activeTab === 'samples'" class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">PDF Samples</h2>
        <button @click="showCreateSampleModal = true" class="btn btn-primary">
          <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Sample
        </button>
      </div>
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else-if="!samples.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <p class="text-sm font-medium">No PDF samples found</p>
        <button @click="showCreateSampleModal = true" class="mt-4 btn btn-primary">Create Your First Sample</button>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Title</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Service Page</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">File</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Downloads</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="sample in samples" :key="sample.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ sample.title || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ sample.service_page?.title || sample.service_page_id || '—' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ sample.file_name || '—' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ formatNumber(sample.download_count || 0) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="sample.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ sample.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button @click="viewSample(sample)" class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">View</button>
                  <button @click="editSample(sample)" class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300">Edit</button>
                  <button @click="deleteSample(sample)" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Sections Tab -->
    <div v-if="activeTab === 'sections'" class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">PDF Sample Sections</h2>
        <button @click="showCreateSectionModal = true" class="btn btn-primary">
          <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Add Section
        </button>
      </div>
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else-if="!sections.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <p class="text-sm font-medium">No sections found</p>
        <button @click="showCreateSectionModal = true" class="mt-4 btn btn-primary">Create Your First Section</button>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Title</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">PDF Sample</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Order</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="section in sections" :key="section.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ section.title || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ section.pdf_sample?.title || section.pdf_sample_id || '—' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ section.display_order || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="section.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ section.is_active ? 'Active' : 'Inactive' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button @click="viewSection(section)" class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">View</button>
                  <button @click="editSection(section)" class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300">Edit</button>
                  <button @click="deleteSection(section)" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Edit Sample Modal -->
    <div v-if="showEditSampleModal && editingSample" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4" @click.self="closeEditSampleModal">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-2xl font-bold text-gray-900 dark:text-white">Edit PDF Sample</h3>
            <button @click="closeEditSampleModal" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <form @submit.prevent="saveSample" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Title *</label>
              <input
                v-model="sampleForm.title"
                type="text"
                required
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 dark:bg-gray-700 dark:text-white"
                placeholder="Enter sample title"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Service Page ID</label>
              <input
                v-model.number="sampleForm.service_page_id"
                type="number"
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 dark:bg-gray-700 dark:text-white"
                placeholder="Service page ID (optional)"
              />
            </div>
            
            <div>
              <label class="flex items-center gap-2">
                <input
                  v-model="sampleForm.is_active"
                  type="checkbox"
                  class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Active</span>
              </label>
            </div>
            
            <div class="flex gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <button
                type="button"
                @click="closeEditSampleModal"
                class="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="saving"
                class="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {{ saving ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Edit Section Modal -->
    <div v-if="showEditSectionModal && editingSection" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4" @click.self="closeEditSectionModal">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-2xl font-bold text-gray-900 dark:text-white">Edit PDF Sample Section</h3>
            <button @click="closeEditSectionModal" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <form @submit.prevent="saveSection" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Title *</label>
              <input
                v-model="sectionForm.title"
                type="text"
                required
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 dark:bg-gray-700 dark:text-white"
                placeholder="Enter section title"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">PDF Sample ID *</label>
              <input
                v-model.number="sectionForm.pdf_sample_id"
                type="number"
                required
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 dark:bg-gray-700 dark:text-white"
                placeholder="PDF Sample ID"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Display Order</label>
              <input
                v-model.number="sectionForm.display_order"
                type="number"
                min="0"
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 dark:bg-gray-700 dark:text-white"
                placeholder="Display order (0 for default)"
              />
            </div>
            
            <div>
              <label class="flex items-center gap-2">
                <input
                  v-model="sectionForm.is_active"
                  type="checkbox"
                  class="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Active</span>
              </label>
            </div>
            
            <div class="flex gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <button
                type="button"
                @click="closeEditSectionModal"
                class="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="saving"
                class="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {{ saving ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </form>
        </div>
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
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const { showSuccess, showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const activeTab = ref('samples')
const samples = ref([])
const sections = ref([])
const stats = ref({ total_samples: 0, total_sections: 0, total_downloads: 0, active_samples: 0 })
const showCreateSampleModal = ref(false)
const showCreateSectionModal = ref(false)
const showEditSampleModal = ref(false)
const showEditSectionModal = ref(false)
const editingSample = ref(null)
const editingSection = ref(null)
const saving = ref(false)
const sampleForm = ref({
  title: '',
  service_page_id: null,
  is_active: true
})
const sectionForm = ref({
  title: '',
  pdf_sample_id: null,
  display_order: 0,
  is_active: true
})

const loadSamples = async () => {
  loading.value = true
  try {
    const res = await blogPagesAPI.listPDFSamples({})
    samples.value = res.data?.results || res.data || []
    
    // Calculate stats
    stats.value = {
      total_samples: samples.value.length,
      active_samples: samples.value.filter(s => s.is_active).length,
      total_downloads: samples.value.reduce((sum, s) => sum + (s.download_count || 0), 0),
      total_sections: sections.value.length,
    }
  } catch (error) {
    console.error('Failed to load samples:', error)
    showError('Failed to load samples: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const loadSections = async () => {
  loading.value = true
  try {
    const res = await blogPagesAPI.listPDFSampleSections({})
    sections.value = res.data?.results || res.data || []
    
    // Update stats
    stats.value.total_sections = sections.value.length
  } catch (error) {
    console.error('Failed to load sections:', error)
    showError('Failed to load sections: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const viewSample = (sample) => {
  alert(`PDF Sample: ${sample.title}\nDownloads: ${sample.download_count || 0}\nStatus: ${sample.is_active ? 'Active' : 'Inactive'}`)
}

const editSample = (sample) => {
  editingSample.value = sample
  sampleForm.value = {
    title: sample.title || '',
    service_page_id: sample.service_page_id || sample.service_page?.id || null,
    is_active: sample.is_active !== false
  }
  showEditSampleModal.value = true
}

const closeEditSampleModal = () => {
  showEditSampleModal.value = false
  editingSample.value = null
  sampleForm.value = {
    title: '',
    service_page_id: null,
    is_active: true
  }
}

const saveSample = async () => {
  if (!editingSample.value) return
  
  saving.value = true
  try {
    await blogPagesAPI.updatePDFSample(editingSample.value.id, sampleForm.value)
    showSuccess('PDF sample updated successfully')
    await loadSamples()
    closeEditSampleModal()
  } catch (error) {
    console.error('Failed to update sample:', error)
    showError('Failed to update sample: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const deleteSample = async (sample) => {
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to delete "${sample.title}"?`,
    'Delete PDF Sample',
    {
      details: 'This action cannot be undone. The PDF sample and all its sections will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await blogPagesAPI.deletePDFSample(sample.id)
    showSuccess('PDF sample deleted successfully')
    await loadSamples()
  } catch (error) {
    console.error('Failed to delete sample:', error)
    showError('Failed to delete sample: ' + (error.response?.data?.detail || error.message))
  }
}

const viewSection = (section) => {
  alert(`Section: ${section.title}\nOrder: ${section.display_order || 0}\nStatus: ${section.is_active ? 'Active' : 'Inactive'}`)
}

const editSection = (section) => {
  editingSection.value = section
  sectionForm.value = {
    title: section.title || '',
    pdf_sample_id: section.pdf_sample_id || section.pdf_sample?.id || null,
    display_order: section.display_order || 0,
    is_active: section.is_active !== false
  }
  showEditSectionModal.value = true
}

const closeEditSectionModal = () => {
  showEditSectionModal.value = false
  editingSection.value = null
  sectionForm.value = {
    title: '',
    pdf_sample_id: null,
    display_order: 0,
    is_active: true
  }
}

const saveSection = async () => {
  if (!editingSection.value) return
  
  saving.value = true
  try {
    await blogPagesAPI.updatePDFSampleSection(editingSection.value.id, sectionForm.value)
    showSuccess('PDF sample section updated successfully')
    await loadSections()
    closeEditSectionModal()
  } catch (error) {
    console.error('Failed to update section:', error)
    showError('Failed to update section: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const deleteSection = async (section) => {
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to delete "${section.title}"?`,
    'Delete Section',
    {
      details: 'This action cannot be undone. The section will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await blogPagesAPI.deletePDFSampleSection(section.id)
    showSuccess('Section deleted successfully')
    await loadSections()
  } catch (error) {
    console.error('Failed to delete section:', error)
    showError('Failed to delete section: ' + (error.response?.data?.detail || error.message))
  }
}

const formatNumber = (value) => {
  return parseInt(value || 0).toLocaleString()
}

watch(activeTab, () => {
  if (activeTab.value === 'samples') {
    loadSamples()
  } else {
    loadSections()
  }
})

onMounted(() => {
  loadSamples()
  loadSections()
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


<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Service Pages Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage service pages, PDF samples, and content</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create Service Page
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Pages</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ stats.total }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Published</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ stats.published }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Draft</p>
        <p class="text-3xl font-bold text-yellow-600 dark:text-yellow-400">{{ stats.draft }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Clicks</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ stats.total_clicks }}</p>
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
            placeholder="Search pages..."
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Status</label>
          <select
            v-model="filters.is_published"
            @change="loadServicePages"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option value="">All Status</option>
            <option value="true">Published</option>
            <option value="false">Draft</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Service Pages List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else-if="!servicePages.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="mt-2 text-sm font-medium">No service pages found</p>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Title</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Slug</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Clicks</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Updated</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="page in servicePages" :key="page.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ page.title }}</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">{{ page.header || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-500 dark:text-gray-400">{{ page.slug }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusBadgeClass(page.is_published)" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ page.is_published ? 'Published' : 'Draft' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ page.click_count || 0 }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(page.updated_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button @click="viewPage(page)" class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">View</button>
                  <button @click="editPage(page)" class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300">Edit</button>
                  <button v-if="!page.is_published" @click="publishPage(page)" class="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300">Publish</button>
                  <button v-else @click="unpublishPage(page)" class="text-yellow-600 hover:text-yellow-900 dark:text-yellow-400 dark:hover:text-yellow-300">Unpublish</button>
                  <button @click="deletePage(page)" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || editingPage" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="closeModal">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto m-4">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            {{ editingPage ? 'Edit Service Page' : 'Create Service Page' }}
          </h3>
        </div>
        <form @submit.prevent="savePage" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Title *</label>
            <input
              v-model="pageForm.title"
              type="text"
              required
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Slug *</label>
            <input
              v-model="pageForm.slug"
              type="text"
              required
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Header</label>
            <input
              v-model="pageForm.header"
              type="text"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Content *</label>
            <textarea
              v-model="pageForm.content"
              rows="10"
              required
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            ></textarea>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Meta Title</label>
              <input
                v-model="pageForm.meta_title"
                type="text"
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Publish Status</label>
              <select
                v-model="pageForm.is_published"
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
              >
                <option :value="false">Draft</option>
                <option :value="true">Published</option>
              </select>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Meta Description</label>
            <textarea
              v-model="pageForm.meta_description"
              rows="3"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            ></textarea>
          </div>
          <div class="flex gap-3 pt-4">
            <button type="submit" :disabled="saving" class="btn btn-primary flex-1">
              {{ saving ? 'Saving...' : (editingPage ? 'Update' : 'Create') }}
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
import servicePagesAPI from '@/api/service-pages'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { debounce } from '@/utils/debounce'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const { showSuccess, showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const saving = ref(false)
const servicePages = ref([])
const stats = ref({ total: 0, published: 0, draft: 0, total_clicks: 0 })
const showCreateModal = ref(false)
const editingPage = ref(null)

const filters = ref({
  search: '',
  is_published: '',
})

const pageForm = ref({
  title: '',
  slug: '',
  header: '',
  content: '',
  meta_title: '',
  meta_description: '',
  is_published: false,
})

const debouncedSearch = debounce(() => {
  loadServicePages()
}, 300)

const loadServicePages = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.is_published !== '') params.is_published = filters.value.is_published === 'true'
    
    const res = await servicePagesAPI.listServicePages(params)
    servicePages.value = res.data?.results || res.data || []
    
    // Calculate stats
    stats.value = {
      total: servicePages.value.length,
      published: servicePages.value.filter(p => p.is_published).length,
      draft: servicePages.value.filter(p => !p.is_published).length,
      total_clicks: servicePages.value.reduce((sum, p) => sum + (p.click_count || 0), 0),
    }
  } catch (error) {
    console.error('Failed to load service pages:', error)
    showError('Failed to load service pages: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const savePage = async () => {
  saving.value = true
  try {
    const data = { ...pageForm.value }
    
    if (editingPage.value) {
      await servicePagesAPI.updateServicePage(editingPage.value.id, data)
      showSuccess('Service page updated successfully')
    } else {
      await servicePagesAPI.createServicePage(data)
      showSuccess('Service page created successfully')
    }
    
    closeModal()
    await loadServicePages()
  } catch (error) {
    console.error('Failed to save service page:', error)
    showError('Failed to save service page: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const editPage = (page) => {
  editingPage.value = page
  pageForm.value = {
    title: page.title || '',
    slug: page.slug || '',
    header: page.header || '',
    content: page.content || '',
    meta_title: page.meta_title || '',
    meta_description: page.meta_description || '',
    is_published: page.is_published || false,
  }
  showCreateModal.value = true
}

const viewPage = (page) => {
  // Navigate to service page detail or open view modal
  window.open(`/service/${page.slug}`, '_blank')
}

const publishPage = async (page) => {
  try {
    await servicePagesAPI.publishServicePage(page.id)
    showSuccess('Service page published successfully')
    await loadServicePages()
  } catch (error) {
    console.error('Failed to publish service page:', error)
    showError('Failed to publish service page: ' + (error.response?.data?.detail || error.message))
  }
}

const unpublishPage = async (page) => {
  try {
    await servicePagesAPI.unpublishServicePage(page.id)
    showSuccess('Service page unpublished successfully')
    await loadServicePages()
  } catch (error) {
    console.error('Failed to unpublish service page:', error)
    showError('Failed to unpublish service page: ' + (error.response?.data?.detail || error.message))
  }
}

const deletePage = async (page) => {
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to delete "${page.title}"?`,
    'Delete Service Page',
    {
      details: 'This action cannot be undone. The service page will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await servicePagesAPI.deleteServicePage(page.id)
    showSuccess('Service page deleted successfully')
    await loadServicePages()
  } catch (error) {
    console.error('Failed to delete service page:', error)
    showError('Failed to delete service page: ' + (error.response?.data?.detail || error.message))
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingPage.value = null
  pageForm.value = {
    title: '',
    slug: '',
    header: '',
    content: '',
    meta_title: '',
    meta_description: '',
    is_published: false,
  }
}

const resetFilters = () => {
  filters.value = { search: '', is_published: '' }
  loadServicePages()
}

const getStatusBadgeClass = (isPublished) => {
  return isPublished
    ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
    : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadServicePages()
})
</script>

<style scoped>
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


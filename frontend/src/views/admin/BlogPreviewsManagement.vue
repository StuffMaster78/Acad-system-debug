<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Blog Previews Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage blog post previews and preview tokens</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create Preview
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Previews</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(stats.total) }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Active</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ stats.active }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Expired</p>
        <p class="text-3xl font-bold text-yellow-600 dark:text-yellow-400">{{ stats.expired }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Views</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ formatNumber(stats.total_views) }}</p>
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
            placeholder="Search posts..."
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Status</label>
          <select
            v-model="filters.status"
            @change="loadPreviews"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="expired">Expired</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Previews List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else-if="!previews.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
        </svg>
        <p class="mt-2 text-sm font-medium">No previews found</p>
        <button @click="showCreateModal = true" class="mt-4 btn btn-primary">Create Your First Preview</button>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Blog Post</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Preview Token</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Created By</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Views</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Expires At</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="preview in previews" :key="preview.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ preview.blog_post?.title || preview.blog_post_id || '—' }}</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">{{ preview.blog_post?.slug || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-mono text-gray-900 dark:text-gray-100">{{ preview.token?.substring(0, 20) || '—' }}...</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ preview.created_by?.username || preview.created_by?.email || '—' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ formatNumber(preview.view_count || 0) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(preview.expires_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="isPreviewExpired(preview) ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300' : 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ isPreviewExpired(preview) ? 'Expired' : 'Active' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button @click="viewPreview(preview)" class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">View</button>
                  <button @click="copyPreviewLink(preview)" class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300">Copy Link</button>
                  <button @click="deletePreview(preview)" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="closeModal">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto m-4">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Create Preview</h3>
        </div>
        <form @submit.prevent="savePreview" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Blog Post ID *</label>
            <input
              v-model.number="previewForm.blog_post"
              type="number"
              required
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Expires At</label>
            <input
              v-model="previewForm.expires_at"
              type="datetime-local"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Leave empty for no expiration</p>
          </div>
          <div class="flex gap-3 pt-4">
            <button type="submit" :disabled="saving" class="btn btn-primary flex-1">
              {{ saving ? 'Creating...' : 'Create Preview' }}
            </button>
            <button type="button" @click="closeModal" class="btn btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import blogPagesAPI from '@/api/blog-pages'
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { debounce } from '@/utils/debounce'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const { showSuccess, showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const saving = ref(false)
const previews = ref([])
const stats = ref({ total: 0, active: 0, expired: 0, total_views: 0 })
const showCreateModal = ref(false)

const filters = ref({
  search: '',
  status: '',
})

const previewForm = ref({
  blog_post: null,
  expires_at: '',
})

const debouncedSearch = debounce(() => {
  loadPreviews()
}, 300)

const loadPreviews = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    
    const res = await blogPagesAPI.listPreviews(params)
    let allPreviews = res.data?.results || res.data || []
    
    // Filter by status if selected
    if (filters.value.status === 'active') {
      allPreviews = allPreviews.filter(p => !isPreviewExpired(p))
    } else if (filters.value.status === 'expired') {
      allPreviews = allPreviews.filter(p => isPreviewExpired(p))
    }
    
    previews.value = allPreviews
    
    // Calculate stats
    const now = new Date()
    const active = previews.value.filter(p => !isPreviewExpired(p))
    const expired = previews.value.filter(p => isPreviewExpired(p))
    
    stats.value = {
      total: previews.value.length,
      active: active.length,
      expired: expired.length,
      total_views: previews.value.reduce((sum, p) => sum + (p.view_count || 0), 0),
    }
  } catch (error) {
    console.error('Failed to load previews:', error)
    showError('Failed to load previews: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const isPreviewExpired = (preview) => {
  if (!preview.expires_at) return false
  return new Date(preview.expires_at) < new Date()
}

const savePreview = async () => {
  saving.value = true
  try {
    const data = { ...previewForm.value }
    if (!data.expires_at) delete data.expires_at
    
    await blogPagesAPI.createPreview(data)
    showSuccess('Preview created successfully')
    closeModal()
    await loadPreviews()
  } catch (error) {
    console.error('Failed to create preview:', error)
    showError('Failed to create preview: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const viewPreview = (preview) => {
  if (preview.token) {
    const previewUrl = `${window.location.origin}/api/v1/blog_pages_management/preview/${preview.token}/`
    window.open(previewUrl, '_blank')
  } else {
    showError('Preview token not available')
  }
}

const copyPreviewLink = async (preview) => {
  if (preview.token) {
    const previewUrl = `${window.location.origin}/api/v1/blog_pages_management/preview/${preview.token}/`
    try {
      await navigator.clipboard.writeText(previewUrl)
      showSuccess('Preview link copied to clipboard')
    } catch (error) {
      showError('Failed to copy link')
    }
  } else {
    showError('Preview token not available')
  }
}

const deletePreview = async (preview) => {
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to delete this preview?',
    'Delete Preview',
    {
      details: 'This action cannot be undone. The preview token will be invalidated.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await blogPagesAPI.deletePreview(preview.id)
    showSuccess('Preview deleted successfully')
    await loadPreviews()
  } catch (error) {
    console.error('Failed to delete preview:', error)
    showError('Failed to delete preview: ' + (error.response?.data?.detail || error.message))
  }
}

const closeModal = () => {
  showCreateModal.value = false
  previewForm.value = {
    blog_post: null,
    expires_at: '',
  }
}

const resetFilters = () => {
  filters.value = { search: '', status: '' }
  loadPreviews()
}

const formatNumber = (value) => {
  return parseInt(value || 0).toLocaleString()
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadPreviews()
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


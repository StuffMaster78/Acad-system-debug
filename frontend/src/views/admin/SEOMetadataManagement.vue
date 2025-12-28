<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">SEO Metadata Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Manage SEO metadata for blog posts</p>
      </div>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Create Metadata
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Metadata</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ stats.total }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">With Meta Title</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ stats.with_title }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">With Meta Desc</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ stats.with_description }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">With OG Image</p>
        <p class="text-3xl font-bold text-purple-600 dark:text-purple-400">{{ stats.with_og_image }}</p>
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
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Blog Post ID</label>
          <input
            v-model="filters.blog_post"
            type="number"
            placeholder="Filter by Blog Post ID..."
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            @input="loadMetadata"
          />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Metadata List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else-if="!metadata.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p class="mt-2 text-sm font-medium">No SEO metadata found</p>
        <button @click="showCreateModal = true" class="mt-4 btn btn-primary">Create Your First Metadata</button>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Blog Post</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Meta Title</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Meta Description</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">OG Image</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="item in metadata" :key="item.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ item.blog_post?.title || item.blog_post_id || '—' }}</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">{{ item.blog_post?.slug || '—' }}</div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-900 dark:text-gray-100 max-w-xs truncate">{{ item.meta_title || '—' }}</div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-500 dark:text-gray-400 max-w-xs truncate">{{ item.meta_description || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span v-if="item.og_image" class="text-green-600 dark:text-green-400">✓</span>
                <span v-else class="text-gray-400">—</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button @click="viewMetadata(item)" class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">View</button>
                  <button @click="editMetadata(item)" class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300">Edit</button>
                  <button @click="deleteMetadata(item)" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || editingMetadata" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="closeModal">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto m-4">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700">
          <h3 class="text-xl font-semibold text-gray-900 dark:text-gray-100">
            {{ editingMetadata ? 'Edit SEO Metadata' : 'Create SEO Metadata' }}
          </h3>
        </div>
        <form @submit.prevent="saveMetadata" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Blog Post ID *</label>
            <input
              v-model.number="metadataForm.blog_post"
              type="number"
              required
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Meta Title</label>
            <input
              v-model="metadataForm.meta_title"
              type="text"
              maxlength="60"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ metadataForm.meta_title?.length || 0 }}/60 characters</p>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Meta Description</label>
            <textarea
              v-model="metadataForm.meta_description"
              rows="3"
              maxlength="160"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            ></textarea>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ metadataForm.meta_description?.length || 0 }}/160 characters</p>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">OG Image URL</label>
            <input
              v-model="metadataForm.og_image"
              type="url"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Keywords</label>
            <input
              v-model="metadataForm.keywords"
              type="text"
              placeholder="keyword1, keyword2, keyword3"
              class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
            />
          </div>
          <div class="flex gap-3 pt-4">
            <button type="submit" :disabled="saving" class="btn btn-primary flex-1">
              {{ saving ? 'Saving...' : (editingMetadata ? 'Update' : 'Create') }}
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
import { useToast } from '@/composables/useToast'
import { useConfirmDialog } from '@/composables/useConfirmDialog'
import { debounce } from '@/utils/debounce'
import ConfirmationDialog from '@/components/common/ConfirmationDialog.vue'

const { showSuccess, showError } = useToast()
const confirm = useConfirmDialog()

const loading = ref(false)
const saving = ref(false)
const metadata = ref([])
const stats = ref({ total: 0, with_title: 0, with_description: 0, with_og_image: 0 })
const showCreateModal = ref(false)
const editingMetadata = ref(null)

const filters = ref({
  search: '',
  blog_post: '',
})

const metadataForm = ref({
  blog_post: null,
  meta_title: '',
  meta_description: '',
  og_image: '',
  keywords: '',
})

const debouncedSearch = debounce(() => {
  loadMetadata()
}, 300)

const loadMetadata = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.blog_post) params.blog_post = filters.value.blog_post
    
    const res = await blogPagesAPI.listSEOMetadata(params)
    metadata.value = res.data?.results || res.data || []
    
    // Calculate stats
    stats.value = {
      total: metadata.value.length,
      with_title: metadata.value.filter(m => m.meta_title).length,
      with_description: metadata.value.filter(m => m.meta_description).length,
      with_og_image: metadata.value.filter(m => m.og_image).length,
    }
  } catch (error) {
    console.error('Failed to load metadata:', error)
    showError('Failed to load metadata: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const saveMetadata = async () => {
  saving.value = true
  try {
    const data = { ...metadataForm.value }
    
    if (editingMetadata.value) {
      await blogPagesAPI.updateSEOMetadata(editingMetadata.value.id, data)
      showSuccess('SEO metadata updated successfully')
    } else {
      await blogPagesAPI.createSEOMetadata(data)
      showSuccess('SEO metadata created successfully')
    }
    
    closeModal()
    await loadMetadata()
  } catch (error) {
    console.error('Failed to save metadata:', error)
    showError('Failed to save metadata: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const editMetadata = (item) => {
  editingMetadata.value = item
  metadataForm.value = {
    blog_post: item.blog_post?.id || item.blog_post_id || null,
    meta_title: item.meta_title || '',
    meta_description: item.meta_description || '',
    og_image: item.og_image || '',
    keywords: item.keywords || '',
  }
  showCreateModal.value = true
}

const viewMetadata = (item) => {
  alert(`SEO Metadata\n\nBlog: ${item.blog_post?.title || item.blog_post_id}\nTitle: ${item.meta_title || 'N/A'}\nDescription: ${item.meta_description || 'N/A'}\nOG Image: ${item.og_image ? 'Yes' : 'No'}`)
}

const deleteMetadata = async (item) => {
  const confirmed = await confirm.showDestructive(
    `Are you sure you want to delete SEO metadata for "${item.blog_post?.title || item.blog_post_id}"?`,
    'Delete SEO Metadata',
    {
      details: 'This action cannot be undone. The SEO metadata will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await blogPagesAPI.deleteSEOMetadata(item.id)
    showSuccess('SEO metadata deleted successfully')
    await loadMetadata()
  } catch (error) {
    console.error('Failed to delete metadata:', error)
    showError('Failed to delete metadata: ' + (error.response?.data?.detail || error.message))
  }
}

const closeModal = () => {
  showCreateModal.value = false
  editingMetadata.value = null
  metadataForm.value = {
    blog_post: null,
    meta_title: '',
    meta_description: '',
    og_image: '',
    keywords: '',
  }
}

const resetFilters = () => {
  filters.value = { search: '', blog_post: '' }
  loadMetadata()
}

onMounted(() => {
  loadMetadata()
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


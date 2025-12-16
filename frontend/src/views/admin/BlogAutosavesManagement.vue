<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Blog Auto-saves Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">View and manage auto-saved blog post drafts</p>
      </div>
      <button @click="loadAutosaves" :disabled="loading" class="btn btn-secondary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Refresh
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Auto-saves</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(stats.total) }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Today</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ formatNumber(stats.today) }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Unique Posts</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ formatNumber(stats.unique_posts) }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Oldest Save</p>
        <p class="text-sm font-bold text-purple-600 dark:text-purple-400">{{ stats.oldest_save || '—' }}</p>
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
            @input="loadAutosaves"
          />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Auto-saves List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else-if="!autosaves.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
        </svg>
        <p class="mt-2 text-sm font-medium">No auto-saves found</p>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Blog Post</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Saved By</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Content Preview</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Last Saved</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="autosave in autosaves" :key="autosave.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ autosave.blog_post?.title || autosave.blog_post_id || '—' }}</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">{{ autosave.blog_post?.slug || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ autosave.saved_by?.username || autosave.saved_by?.email || '—' }}
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-500 dark:text-gray-400 max-w-xs truncate">{{ getContentPreview(autosave) }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(autosave.saved_at || autosave.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button @click="viewAutosave(autosave)" class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">View</button>
                  <button @click="restoreAutosave(autosave)" class="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300">Restore</button>
                  <button @click="deleteAutosave(autosave)" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">Delete</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
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
const autosaves = ref([])
const stats = ref({ total: 0, today: 0, unique_posts: 0, oldest_save: '' })

const filters = ref({
  search: '',
  blog_post: '',
})

const debouncedSearch = debounce(() => {
  loadAutosaves()
}, 300)

const loadAutosaves = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.blog_post) params.blog_post = filters.value.blog_post
    
    const res = await blogPagesAPI.listAutosaves(params)
    autosaves.value = res.data?.results || res.data || []
    
    // Calculate stats
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    const todaySaves = autosaves.value.filter(a => {
      const saveDate = new Date(a.saved_at || a.created_at)
      return saveDate >= today
    })
    const uniquePosts = new Set(autosaves.value.map(a => a.blog_post?.id || a.blog_post_id))
    const sortedByDate = [...autosaves.value].sort((a, b) => {
      const dateA = new Date(a.saved_at || a.created_at)
      const dateB = new Date(b.saved_at || b.created_at)
      return dateA - dateB
    })
    const oldest = sortedByDate[0]
    
    stats.value = {
      total: autosaves.value.length,
      today: todaySaves.length,
      unique_posts: uniquePosts.size,
      oldest_save: oldest ? formatDate(oldest.saved_at || oldest.created_at) : '—',
    }
  } catch (error) {
    console.error('Failed to load autosaves:', error)
    showError('Failed to load autosaves: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const getContentPreview = (autosave) => {
  const content = autosave.content || autosave.saved_content || ''
  return content.substring(0, 100) + (content.length > 100 ? '...' : '') || '—'
}

const viewAutosave = (autosave) => {
  alert(`Auto-save\n\nBlog: ${autosave.blog_post?.title || autosave.blog_post_id}\nSaved By: ${autosave.saved_by?.username || autosave.saved_by?.email}\nDate: ${formatDate(autosave.saved_at || autosave.created_at)}`)
}

const restoreAutosave = async (autosave) => {
  const confirmed = await confirm.showWarning(
    'Are you sure you want to restore this auto-save?',
    'Restore Auto-save',
    {
      details: 'This will replace the current content with the selected auto-save. This action cannot be undone.',
      confirmText: 'Restore',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await blogPagesAPI.restoreAutosave(autosave.id)
    showSuccess('Auto-save restored successfully')
    await loadAutosaves()
  } catch (error) {
    console.error('Failed to restore autosave:', error)
    showError('Failed to restore autosave: ' + (error.response?.data?.detail || error.message))
  }
}

const deleteAutosave = async (autosave) => {
  const confirmed = await confirm.showDestructive(
    'Are you sure you want to delete this auto-save?',
    'Delete Auto-save',
    {
      details: 'This action cannot be undone. The auto-save will be permanently removed.',
      confirmText: 'Delete',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await blogPagesAPI.deleteAutosave(autosave.id)
    showSuccess('Auto-save deleted successfully')
    await loadAutosaves()
  } catch (error) {
    console.error('Failed to delete autosave:', error)
    showError('Failed to delete autosave: ' + (error.response?.data?.detail || error.message))
  }
}

const resetFilters = () => {
  filters.value = { search: '', blog_post: '' }
  loadAutosaves()
}

const formatNumber = (value) => {
  return parseInt(value || 0).toLocaleString()
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadAutosaves()
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


<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Blog Revisions Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">View and manage blog post revision history</p>
      </div>
      <button @click="loadRevisions" :disabled="loading" class="btn btn-secondary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Refresh
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Revisions</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(stats.total) }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">This Week</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ formatNumber(stats.this_week) }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Unique Posts</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ formatNumber(stats.unique_posts) }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Avg. Revisions/Post</p>
        <p class="text-3xl font-bold text-purple-600 dark:text-purple-400">{{ stats.avg_revisions }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 border border-gray-200 dark:border-gray-700">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
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
            @input="loadRevisions"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Date From</label>
          <input
            v-model="filters.date_from"
            type="date"
            @change="loadRevisions"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Revisions List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else-if="!revisions.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="mt-2 text-sm font-medium">No revisions found</p>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Blog Post</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Revision #</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Created By</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Changes</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Date</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="revision in revisions" :key="revision.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ revision.blog_post?.title || revision.blog_post_id || '—' }}</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">{{ revision.blog_post?.slug || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                #{{ revision.revision_number || revision.id }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ revision.created_by?.username || revision.created_by?.email || '—' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ revision.changes_summary || '—' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(revision.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button @click="viewRevision(revision)" class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">View</button>
                  <button @click="restoreRevision(revision)" class="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300">Restore</button>
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
const revisions = ref([])
const stats = ref({ total: 0, this_week: 0, unique_posts: 0, avg_revisions: 0 })

const filters = ref({
  search: '',
  blog_post: '',
  date_from: '',
})

const debouncedSearch = debounce(() => {
  loadRevisions()
}, 300)

const loadRevisions = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.blog_post) params.blog_post = filters.value.blog_post
    if (filters.value.date_from) params.date_from = filters.value.date_from
    
    const res = await blogPagesAPI.listRevisions(params)
    revisions.value = res.data?.results || res.data || []
    
    // Calculate stats
    const weekAgo = new Date()
    weekAgo.setDate(weekAgo.getDate() - 7)
    
    const thisWeek = revisions.value.filter(r => new Date(r.created_at) >= weekAgo)
    const uniquePosts = new Set(revisions.value.map(r => r.blog_post?.id || r.blog_post_id))
    const postRevisionCounts = {}
    revisions.value.forEach(r => {
      const postId = r.blog_post?.id || r.blog_post_id
      postRevisionCounts[postId] = (postRevisionCounts[postId] || 0) + 1
    })
    const avgRevisions = uniquePosts.size > 0 
      ? (revisions.value.length / uniquePosts.size).toFixed(1)
      : 0
    
    stats.value = {
      total: revisions.value.length,
      this_week: thisWeek.length,
      unique_posts: uniquePosts.size,
      avg_revisions: avgRevisions,
    }
  } catch (error) {
    console.error('Failed to load revisions:', error)
    showError('Failed to load revisions: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const viewRevision = (revision) => {
  alert(`Revision #${revision.revision_number || revision.id}\n\nBlog: ${revision.blog_post?.title || revision.blog_post_id}\nCreated By: ${revision.created_by?.username || revision.created_by?.email}\nDate: ${formatDate(revision.created_at)}\nChanges: ${revision.changes_summary || 'N/A'}`)
}

const restoreRevision = async (revision) => {
  const confirmed = await confirm.showWarning(
    'Are you sure you want to restore this revision?',
    'Restore Revision',
    {
      details: 'This will replace the current content with the selected revision. This action cannot be undone.',
      confirmText: 'Restore',
      cancelText: 'Cancel'
    }
  )
  
  if (!confirmed) return
  
  try {
    await blogPagesAPI.restoreRevision(revision.id)
    showSuccess('Revision restored successfully')
    await loadRevisions()
  } catch (error) {
    console.error('Failed to restore revision:', error)
    showError('Failed to restore revision: ' + (error.response?.data?.detail || error.message))
  }
}

const resetFilters = () => {
  filters.value = { search: '', blog_post: '', date_from: '' }
  loadRevisions()
}

const formatNumber = (value) => {
  return parseInt(value || 0).toLocaleString()
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadRevisions()
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


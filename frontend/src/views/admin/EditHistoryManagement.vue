<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Edit History Management</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">View and manage blog post edit history</p>
      </div>
      <button @click="loadHistory" :disabled="loading" class="btn btn-secondary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Refresh
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Edits</p>
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
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Top Editor</p>
        <p class="text-lg font-bold text-purple-600 dark:text-purple-400 truncate">{{ stats.top_editor || '—' }}</p>
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
            @input="loadHistory"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Date From</label>
          <input
            v-model="filters.date_from"
            type="date"
            @change="loadHistory"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- History List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else-if="!history.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="mt-2 text-sm font-medium">No edit history found</p>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Blog Post</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Edited By</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Edit Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Changes</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Date</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="entry in history" :key="entry.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ entry.blog_post?.title || entry.blog_post_id || '—' }}</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">{{ entry.blog_post?.slug || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ entry.edited_by?.username || entry.edited_by?.email || '—' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                  {{ entry.edit_type || 'update' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ entry.changes_summary || '—' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(entry.edited_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button @click="viewDetails(entry)" class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">View</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import blogPagesAPI from '@/api/blog-pages'
import { useToast } from '@/composables/useToast'
import { debounce } from '@/utils/debounce'

const { showError } = useToast()

const loading = ref(false)
const history = ref([])
const stats = ref({ total: 0, this_week: 0, unique_posts: 0, top_editor: '' })

const filters = ref({
  search: '',
  blog_post: '',
  date_from: '',
})

const debouncedSearch = debounce(() => {
  loadHistory()
}, 300)

const loadHistory = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.blog_post) params.blog_post = filters.value.blog_post
    if (filters.value.date_from) params.date_from = filters.value.date_from
    
    const res = await blogPagesAPI.listEditHistory(params)
    history.value = res.data?.results || res.data || []
    
    // Calculate stats
    const weekAgo = new Date()
    weekAgo.setDate(weekAgo.getDate() - 7)
    
    const thisWeek = history.value.filter(h => new Date(h.edited_at) >= weekAgo)
    const uniquePosts = new Set(history.value.map(h => h.blog_post?.id || h.blog_post_id))
    const editorCounts = {}
    history.value.forEach(h => {
      const editor = h.edited_by?.username || h.edited_by?.email || 'unknown'
      editorCounts[editor] = (editorCounts[editor] || 0) + 1
    })
    const topEditor = Object.entries(editorCounts).sort((a, b) => b[1] - a[1])[0]
    
    stats.value = {
      total: history.value.length,
      this_week: thisWeek.length,
      unique_posts: uniquePosts.size,
      top_editor: topEditor ? topEditor[0] : '—',
    }
  } catch (error) {
    console.error('Failed to load history:', error)
    showError('Failed to load edit history: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const viewDetails = (entry) => {
  alert(`Edit History Entry\n\nBlog: ${entry.blog_post?.title || entry.blog_post_id}\nEditor: ${entry.edited_by?.username || entry.edited_by?.email}\nType: ${entry.edit_type}\nDate: ${formatDate(entry.edited_at)}\nChanges: ${entry.changes_summary || 'N/A'}`)
}

const resetFilters = () => {
  filters.value = { search: '', blog_post: '', date_from: '' }
  loadHistory()
}

const formatNumber = (value) => {
  return parseInt(value || 0).toLocaleString()
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString()
}

onMounted(() => {
  loadHistory()
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


<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Content Freshness Reminders</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Track and manage content that needs updating</p>
      </div>
      <div class="flex gap-2">
        <button @click="refreshReminders" :disabled="loading" class="btn btn-secondary">
          <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh Reminders
        </button>
        <button @click="loadReminders" :disabled="loading" class="btn btn-secondary">
          Refresh
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Reminders</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ stats.total }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Unacknowledged</p>
        <p class="text-3xl font-bold text-yellow-600 dark:text-yellow-400">{{ stats.unacknowledged }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Acknowledged</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ stats.acknowledged }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Stale Content</p>
        <p class="text-3xl font-bold text-red-600 dark:text-red-400">{{ stats.stale }}</p>
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
            placeholder="Search content..."
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Status</label>
          <select
            v-model="filters.is_acknowledged"
            @change="loadReminders"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option value="">All Status</option>
            <option value="false">Unacknowledged</option>
            <option value="true">Acknowledged</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Reminders List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else-if="!reminders.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="mt-2 text-sm font-medium">No freshness reminders found</p>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Blog Post</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Last Updated</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Days Since Update</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Acknowledged By</th>
              <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="reminder in reminders" :key="reminder.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ reminder.blog_post?.title || reminder.blog_post_id || '—' }}</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">{{ reminder.blog_post?.slug || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(reminder.blog_post?.updated_at || reminder.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ getDaysSinceUpdate(reminder.blog_post?.updated_at || reminder.created_at) }} days
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="reminder.is_acknowledged ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ reminder.is_acknowledged ? 'Acknowledged' : 'Pending' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ reminder.acknowledged_by?.username || reminder.acknowledged_by?.email || '—' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex items-center justify-end gap-2">
                  <button @click="viewPost(reminder)" class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">View</button>
                  <button v-if="!reminder.is_acknowledged" @click="acknowledgeReminder(reminder)" class="text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300">Acknowledge</button>
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

const { showSuccess, showError } = useToast()

const loading = ref(false)
const reminders = ref([])
const staleContent = ref([])
const stats = ref({ total: 0, unacknowledged: 0, acknowledged: 0, stale: 0 })

const filters = ref({
  search: '',
  is_acknowledged: '',
})

const debouncedSearch = debounce(() => {
  loadReminders()
}, 300)

const loadReminders = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.is_acknowledged !== '') params.is_acknowledged = filters.value.is_acknowledged === 'true'
    
    const res = await blogPagesAPI.getContentFreshnessReminders(params)
    reminders.value = res.data?.results || res.data || []
    
    // Load stale content
    const staleRes = await blogPagesAPI.getStaleContent({ months: 3 })
    staleContent.value = staleRes.data?.results || staleRes.data || []
    
    // Calculate stats
    stats.value = {
      total: reminders.value.length,
      unacknowledged: reminders.value.filter(r => !r.is_acknowledged).length,
      acknowledged: reminders.value.filter(r => r.is_acknowledged).length,
      stale: staleContent.value.length,
    }
  } catch (error) {
    console.error('Failed to load reminders:', error)
    showError('Failed to load reminders: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const refreshReminders = async () => {
  loading.value = true
  try {
    await blogPagesAPI.refreshFreshnessReminders({})
    showSuccess('Reminders refreshed successfully')
    await loadReminders()
  } catch (error) {
    console.error('Failed to refresh reminders:', error)
    showError('Failed to refresh reminders: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const acknowledgeReminder = async (reminder) => {
  try {
    await blogPagesAPI.acknowledgeFreshnessReminder(reminder.id)
    showSuccess('Reminder acknowledged successfully')
    await loadReminders()
  } catch (error) {
    console.error('Failed to acknowledge reminder:', error)
    showError('Failed to acknowledge reminder: ' + (error.response?.data?.detail || error.message))
  }
}

const viewPost = (reminder) => {
  if (reminder.blog_post?.id) {
    window.open(`/admin/blog?post=${reminder.blog_post.id}`, '_blank')
  } else {
    showError('Blog post ID not available')
  }
}

const resetFilters = () => {
  filters.value = { search: '', is_acknowledged: '' }
  loadReminders()
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString()
}

const getDaysSinceUpdate = (dateString) => {
  if (!dateString) return 0
  const now = new Date()
  const updated = new Date(dateString)
  const diffTime = Math.abs(now - updated)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays
}

onMounted(() => {
  loadReminders()
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



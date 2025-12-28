<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Blog Shares Tracking</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Track social media shares for blog posts</p>
      </div>
      <button @click="loadShares" :disabled="loading" class="btn btn-secondary">
        <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Refresh
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Shares</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(stats.total) }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Top Platform</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ stats.top_platform || '—' }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Most Shared Post</p>
        <p class="text-lg font-bold text-green-600 dark:text-green-400 truncate">{{ stats.top_post || '—' }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Unique Posts</p>
        <p class="text-3xl font-bold text-purple-600 dark:text-purple-400">{{ stats.unique_posts }}</p>
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
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Platform</label>
          <select
            v-model="filters.platform"
            @change="loadShares"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          >
            <option value="">All Platforms</option>
            <option v-for="platform in platforms" :key="platform.id" :value="platform.platform_name">{{ platform.display_name || platform.platform_name }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Date From</label>
          <input
            v-model="filters.date_from"
            type="date"
            @change="loadShares"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Shares List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      
      <div v-else-if="!shares.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
        </svg>
        <p class="mt-2 text-sm font-medium">No shares found</p>
      </div>
      
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Blog Post</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Platform</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Shared By</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">IP Address</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Date</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="share in shares" :key="share.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ share.blog_post?.title || share.blog_post_id || '—' }}</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">{{ share.blog_post?.slug || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                  {{ share.platform?.platform_name || share.platform_name || '—' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ share.user?.username || share.user?.email || 'Anonymous' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ share.ip_address || '—' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(share.created_at) }}
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
const shares = ref([])
const platforms = ref([])
const stats = ref({ total: 0, top_platform: '', top_post: '', unique_posts: 0 })

const filters = ref({
  search: '',
  platform: '',
  date_from: '',
})

const debouncedSearch = debounce(() => {
  loadShares()
}, 300)

const loadShares = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.platform) params.platform = filters.value.platform
    if (filters.value.date_from) params.date_from = filters.value.date_from
    
    const res = await blogPagesAPI.listBlogShares(params)
    shares.value = res.data?.results || res.data || []
    
    // Calculate stats
    const platformCounts = {}
    const postCounts = {}
    shares.value.forEach(share => {
      const platform = share.platform?.platform_name || share.platform_name || 'unknown'
      platformCounts[platform] = (platformCounts[platform] || 0) + 1
      
      const postId = share.blog_post?.id || share.blog_post_id
      if (postId) {
        postCounts[postId] = (postCounts[postId] || 0) + 1
      }
    })
    
    const topPlatform = Object.entries(platformCounts).sort((a, b) => b[1] - a[1])[0]
    const topPost = Object.entries(postCounts).sort((a, b) => b[1] - a[1])[0]
    
    stats.value = {
      total: shares.value.length,
      top_platform: topPlatform ? topPlatform[0] : '—',
      top_post: topPost ? shares.value.find(s => (s.blog_post?.id || s.blog_post_id) === parseInt(topPost[0]))?.blog_post?.title : '—',
      unique_posts: Object.keys(postCounts).length,
    }
  } catch (error) {
    console.error('Failed to load shares:', error)
    showError('Failed to load shares: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const loadPlatforms = async () => {
  try {
    const res = await blogPagesAPI.listSocialPlatforms({})
    platforms.value = res.data?.results || res.data || []
  } catch (error) {
    console.error('Failed to load platforms:', error)
  }
}

const resetFilters = () => {
  filters.value = { search: '', platform: '', date_from: '' }
  loadShares()
}

const formatNumber = (value) => {
  return parseInt(value || 0).toLocaleString()
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString()
}

onMounted(async () => {
  await Promise.all([loadShares(), loadPlatforms()])
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



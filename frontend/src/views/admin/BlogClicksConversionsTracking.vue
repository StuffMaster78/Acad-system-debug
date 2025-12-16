<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Blog Clicks & Conversions Tracking</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Track clicks and conversions for blog posts</p>
      </div>
      <div class="flex gap-2">
        <button @click="activeTab = 'clicks'" :class="['btn', activeTab === 'clicks' ? 'btn-primary' : 'btn-secondary']">
          Clicks
        </button>
        <button @click="activeTab = 'conversions'" :class="['btn', activeTab === 'conversions' ? 'btn-primary' : 'btn-secondary']">
          Conversions
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Clicks</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(stats.total_clicks) }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Conversions</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ formatNumber(stats.total_conversions) }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Conversion Rate</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ stats.conversion_rate }}%</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Top Post</p>
        <p class="text-sm font-bold text-purple-600 dark:text-purple-400 truncate">{{ stats.top_post || '—' }}</p>
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
            @input="loadData"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1 text-gray-700 dark:text-gray-300">Date From</label>
          <input
            v-model="filters.date_from"
            type="date"
            @change="loadData"
            class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
          />
        </div>
        <div class="flex items-end">
          <button @click="resetFilters" class="btn btn-secondary w-full">Reset</button>
        </div>
      </div>
    </div>

    <!-- Clicks Tab -->
    <div v-if="activeTab === 'clicks'" class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Clicks</h2>
      </div>
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else-if="!clicks.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <p class="text-sm font-medium">No clicks found</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Blog Post</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Click Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">IP Address</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">User Agent</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Date</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="click in clicks" :key="click.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ click.blog_post?.title || click.blog_post_id || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300">
                  {{ click.click_type || 'view' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ click.ip_address || '—' }}
              </td>
              <td class="px-6 py-4">
                <div class="text-sm text-gray-500 dark:text-gray-400 max-w-xs truncate">{{ click.user_agent || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(click.clicked_at || click.created_at) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Conversions Tab -->
    <div v-if="activeTab === 'conversions'" class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Conversions</h2>
      </div>
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else-if="!conversions.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <p class="text-sm font-medium">No conversions found</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Blog Post</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Conversion Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Value</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">User</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Date</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="conversion in conversions" :key="conversion.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ conversion.blog_post?.title || conversion.blog_post_id || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300">
                  {{ conversion.conversion_type || 'purchase' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ conversion.value ? `$${formatNumber(conversion.value)}` : '—' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ conversion.user?.username || conversion.user?.email || 'Anonymous' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(conversion.converted_at || conversion.created_at) }}
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
const activeTab = ref('clicks')
const clicks = ref([])
const conversions = ref([])
const stats = ref({ total_clicks: 0, total_conversions: 0, conversion_rate: 0, top_post: '' })

const filters = ref({
  search: '',
  blog_post: '',
  date_from: '',
})

const debouncedSearch = debounce(() => {
  loadData()
}, 300)

const loadData = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.blog_post) params.blog_post = filters.value.blog_post
    if (filters.value.date_from) params.date_from = filters.value.date_from
    
    if (activeTab.value === 'clicks') {
      const res = await blogPagesAPI.listBlogClicks(params)
      clicks.value = res.data?.results || res.data || []
    } else {
      const res = await blogPagesAPI.listBlogConversions(params)
      conversions.value = res.data?.results || res.data || []
    }
    
    // Calculate stats
    const clicksRes = await blogPagesAPI.listBlogClicks({})
    const conversionsRes = await blogPagesAPI.listBlogConversions({})
    const allClicks = clicksRes.data?.results || clicksRes.data || []
    const allConversions = conversionsRes.data?.results || conversionsRes.data || []
    
    const conversionRate = allClicks.length > 0 
      ? ((allConversions.length / allClicks.length) * 100).toFixed(2)
      : 0
    
    const postClickCounts = {}
    allClicks.forEach(c => {
      const postId = c.blog_post?.id || c.blog_post_id
      postClickCounts[postId] = (postClickCounts[postId] || 0) + 1
    })
    const topPostId = Object.entries(postClickCounts).sort((a, b) => b[1] - a[1])[0]?.[0]
    const topPost = topPostId ? allClicks.find(c => (c.blog_post?.id || c.blog_post_id) === parseInt(topPostId))?.blog_post?.title : ''
    
    stats.value = {
      total_clicks: allClicks.length,
      total_conversions: allConversions.length,
      conversion_rate: conversionRate,
      top_post: topPost || '—',
    }
  } catch (error) {
    console.error('Failed to load data:', error)
    showError('Failed to load data: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value = { search: '', blog_post: '', date_from: '' }
  loadData()
}

const formatNumber = (value) => {
  return parseFloat(value || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString()
}

watch(activeTab, () => {
  loadData()
})

onMounted(() => {
  loadData()
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


<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Blog Analytics Dashboard</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Comprehensive analytics and performance metrics for blog content</p>
      </div>
      <div class="flex gap-2">
        <input
          v-model="dateRange.start"
          type="date"
          class="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
        />
        <span class="self-center text-gray-500">to</span>
        <input
          v-model="dateRange.end"
          type="date"
          class="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100"
        />
        <button @click="loadAnalytics" :disabled="loading" class="btn btn-secondary">
          <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>
    </div>

    <!-- Overview Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Views</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(overview.total_views) }}</p>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ overview.views_change || 0 }}% vs last period</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Clicks</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ formatNumber(overview.total_clicks) }}</p>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ overview.clicks_change || 0 }}% vs last period</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Conversion Rate</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ formatPercent(overview.conversion_rate) }}%</p>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ overview.conversion_change || 0 }}% vs last period</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Avg. Engagement</p>
        <p class="text-3xl font-bold text-purple-600 dark:text-purple-400">{{ formatPercent(overview.avg_engagement) }}%</p>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ overview.engagement_change || 0 }}% vs last period</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="border-b border-gray-200 dark:border-gray-700">
      <nav class="-mb-px flex space-x-8">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors',
            activeTab === tab.id
              ? 'border-blue-500 text-blue-600 dark:text-blue-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Top Performing Posts -->
    <div v-if="activeTab === 'posts'" class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Top Performing Posts</h2>
      </div>
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else-if="!topPosts.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <p class="text-sm font-medium">No data available</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Post</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Views</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Clicks</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Conversions</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Engagement</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="post in topPosts" :key="post.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ post.title }}</div>
                <div class="text-sm text-gray-500 dark:text-gray-400">{{ post.slug }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ formatNumber(post.views || 0) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ formatNumber(post.clicks || 0) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ formatNumber(post.conversions || 0) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ formatPercent(post.engagement_rate || 0) }}%
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Content Metrics -->
    <div v-if="activeTab === 'metrics'" class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Content Performance Metrics</h2>
      </div>
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else-if="!contentMetrics.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <p class="text-sm font-medium">No data available</p>
      </div>
      <div v-else class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div v-for="metric in contentMetrics" :key="metric.id" class="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">{{ metric.metric_name }}</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(metric.value) }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ metric.description || '' }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Website Metrics -->
    <div v-if="activeTab === 'website'" class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Website-Level Metrics</h2>
      </div>
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else-if="!websiteMetrics" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <p class="text-sm font-medium">No data available</p>
      </div>
      <div v-else class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Latest Metrics</h3>
            <div class="space-y-3">
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600 dark:text-gray-400">Total Posts</span>
                <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ websiteMetrics.total_posts || 0 }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600 dark:text-gray-400">Published Posts</span>
                <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ websiteMetrics.published_posts || 0 }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600 dark:text-gray-400">Total Views</span>
                <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ formatNumber(websiteMetrics.total_views || 0) }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600 dark:text-gray-400">Avg. Views per Post</span>
                <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ formatNumber(websiteMetrics.avg_views_per_post || 0) }}</span>
              </div>
            </div>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">By Category</h3>
            <div v-if="categoryMetrics.length" class="space-y-3">
              <div v-for="cat in categoryMetrics" :key="cat.category_id" class="flex justify-between items-center">
                <span class="text-sm text-gray-600 dark:text-gray-400">{{ cat.category_name }}</span>
                <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ formatNumber(cat.post_count || 0) }} posts</span>
              </div>
            </div>
            <p v-else class="text-sm text-gray-500 dark:text-gray-400">No category data available</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Content Audit -->
    <div v-if="activeTab === 'audit'" class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100">Content Audit Overview</h2>
      </div>
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else-if="!auditOverview" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <p class="text-sm font-medium">No data available</p>
      </div>
      <div v-else class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Stale Content</p>
            <p class="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{{ auditOverview.stale_content_count || 0 }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Posts needing updates</p>
          </div>
          <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Low Performance</p>
            <p class="text-2xl font-bold text-red-600 dark:text-red-400">{{ auditOverview.low_performance_count || 0 }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Posts below threshold</p>
          </div>
          <div class="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Missing SEO</p>
            <p class="text-2xl font-bold text-orange-600 dark:text-orange-400">{{ auditOverview.missing_seo_count || 0 }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Posts without metadata</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import blogPagesAPI from '@/api/blog-pages'
import { useToast } from '@/composables/useToast'

const { showError } = useToast()

const loading = ref(false)
const activeTab = ref('posts')
const overview = ref({
  total_views: 0,
  total_clicks: 0,
  conversion_rate: 0,
  avg_engagement: 0,
  views_change: 0,
  clicks_change: 0,
  conversion_change: 0,
  engagement_change: 0,
})
const topPosts = ref([])
const contentMetrics = ref([])
const websiteMetrics = ref(null)
const categoryMetrics = ref([])
const auditOverview = ref(null)

const dateRange = ref({
  start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  end: new Date().toISOString().split('T')[0],
})

const tabs = [
  { id: 'posts', label: 'Top Posts' },
  { id: 'metrics', label: 'Content Metrics' },
  { id: 'website', label: 'Website Metrics' },
  { id: 'audit', label: 'Content Audit' },
]

const loadAnalytics = async () => {
  loading.value = true
  try {
    const params = {
      start_date: dateRange.value.start,
      end_date: dateRange.value.end,
    }
    
    // Load different data based on active tab
    if (activeTab.value === 'posts') {
      // Load top performing posts
      const res = await blogPagesAPI.getContentMetrics(params)
      topPosts.value = res.data?.results || res.data?.top_posts || []
    } else if (activeTab.value === 'metrics') {
      const res = await blogPagesAPI.getContentMetrics(params)
      contentMetrics.value = res.data?.results || res.data?.metrics || []
    } else if (activeTab.value === 'website') {
      const res = await blogPagesAPI.getWebsiteMetricsLatest(params)
      websiteMetrics.value = res.data
      
      // Load category metrics
      const catRes = await blogPagesAPI.getWebsiteMetricsByCategory(params)
      categoryMetrics.value = catRes.data?.results || catRes.data || []
    } else if (activeTab.value === 'audit') {
      const res = await blogPagesAPI.getContentAuditOverview(params)
      auditOverview.value = res.data
    }
    
    // Load overview stats
    await loadOverview()
  } catch (error) {
    console.error('Failed to load analytics:', error)
    showError('Failed to load analytics: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const loadOverview = async () => {
  try {
    const params = {
      start_date: dateRange.value.start,
      end_date: dateRange.value.end,
    }
    const res = await blogPagesAPI.getContentMetrics(params)
    
    if (res.data) {
      overview.value = {
        total_views: res.data.total_views || 0,
        total_clicks: res.data.total_clicks || 0,
        conversion_rate: res.data.conversion_rate || 0,
        avg_engagement: res.data.avg_engagement || 0,
        views_change: res.data.views_change || 0,
        clicks_change: res.data.clicks_change || 0,
        conversion_change: res.data.conversion_change || 0,
        engagement_change: res.data.engagement_change || 0,
      }
    }
  } catch (error) {
    console.error('Failed to load overview:', error)
  }
}

const formatNumber = (value) => {
  return parseInt(value || 0).toLocaleString()
}

const formatPercent = (value) => {
  return parseFloat(value || 0).toFixed(2)
}

watch(activeTab, () => {
  loadAnalytics()
})

onMounted(() => {
  loadAnalytics()
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


<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-gray-100">Editor Analytics Dashboard</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Track editor performance, productivity, and session analytics</p>
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
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Sessions</p>
        <p class="text-3xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(overview.total_sessions) }}</p>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ overview.sessions_change || 0 }}% vs last period</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Avg. Session Time</p>
        <p class="text-3xl font-bold text-blue-600 dark:text-blue-400">{{ formatDuration(overview.avg_session_time) }}</p>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ overview.session_time_change || 0 }}% vs last period</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Posts Created</p>
        <p class="text-3xl font-bold text-green-600 dark:text-green-400">{{ formatNumber(overview.posts_created) }}</p>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ overview.posts_change || 0 }}% vs last period</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Productivity Score</p>
        <p class="text-3xl font-bold text-purple-600 dark:text-purple-400">{{ formatNumber(overview.productivity_score) }}</p>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ overview.productivity_change || 0 }}% vs last period</p>
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

    <!-- Editor Sessions -->
    <div v-if="activeTab === 'sessions'" class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Editor Sessions</h2>
      </div>
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else-if="!editorSessions.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <p class="text-sm font-medium">No sessions found</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Editor</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Blog Post</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Start Time</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Duration</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="session in editorSessions" :key="session.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ session.editor?.username || session.editor?.email || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900 dark:text-gray-100">{{ session.blog_post?.title || session.blog_post_id || '—' }}</div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatDate(session.started_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                {{ formatDuration(session.duration || 0) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ formatNumber(session.actions_count || 0) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="session.ended_at ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300' : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'" class="px-2 py-1 text-xs font-medium rounded-full">
                  {{ session.ended_at ? 'Completed' : 'Active' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Productivity Metrics -->
    <div v-if="activeTab === 'productivity'" class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Productivity Metrics</h2>
      </div>
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else-if="!productivityMetrics.length" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <p class="text-sm font-medium">No productivity data available</p>
      </div>
      <div v-else class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div v-for="metric in productivityMetrics" :key="metric.id" class="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">{{ metric.editor?.username || metric.editor?.email || 'Unknown' }}</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-gray-100">{{ formatNumber(metric.productivity_score || 0) }}</p>
            <div class="mt-2 space-y-1 text-xs text-gray-500 dark:text-gray-400">
              <div>Posts: {{ metric.posts_created || 0 }}</div>
              <div>Avg Time: {{ formatDuration(metric.avg_edit_time || 0) }}</div>
              <div>Sessions: {{ metric.total_sessions || 0 }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Editor Analytics -->
    <div v-if="activeTab === 'analytics'" class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">Editor Analytics</h2>
      </div>
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else-if="!editorAnalytics" class="text-center py-12 text-gray-500 dark:text-gray-400">
        <p class="text-sm font-medium">No analytics data available</p>
      </div>
      <div v-else class="p-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Performance Overview</h3>
            <div class="space-y-3">
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600 dark:text-gray-400">Total Edits</span>
                <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ formatNumber(editorAnalytics.total_edits || 0) }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600 dark:text-gray-400">Avg. Edits per Session</span>
                <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ formatNumber(editorAnalytics.avg_edits_per_session || 0) }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm text-gray-600 dark:text-gray-400">Most Active Time</span>
                <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ editorAnalytics.most_active_time || '—' }}</span>
              </div>
            </div>
          </div>
          <div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">Top Editors</h3>
            <div v-if="topEditors.length" class="space-y-3">
              <div v-for="editor in topEditors" :key="editor.id" class="flex justify-between items-center">
                <span class="text-sm text-gray-600 dark:text-gray-400">{{ editor.username || editor.email }}</span>
                <span class="text-sm font-medium text-gray-900 dark:text-gray-100">{{ formatNumber(editor.posts_count || 0) }} posts</span>
              </div>
            </div>
            <p v-else class="text-sm text-gray-500 dark:text-gray-400">No editor data available</p>
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
const activeTab = ref('sessions')
const editorSessions = ref([])
const productivityMetrics = ref([])
const editorAnalytics = ref(null)
const topEditors = ref([])
const overview = ref({
  total_sessions: 0,
  avg_session_time: 0,
  posts_created: 0,
  productivity_score: 0,
  sessions_change: 0,
  session_time_change: 0,
  posts_change: 0,
  productivity_change: 0,
})

const dateRange = ref({
  start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  end: new Date().toISOString().split('T')[0],
})

const tabs = [
  { id: 'sessions', label: 'Editor Sessions' },
  { id: 'productivity', label: 'Productivity Metrics' },
  { id: 'analytics', label: 'Editor Analytics' },
]

const loadAnalytics = async () => {
  loading.value = true
  try {
    const params = {
      start_date: dateRange.value.start,
      end_date: dateRange.value.end,
    }
    
    // Load different data based on active tab
    if (activeTab.value === 'sessions') {
      const res = await blogPagesAPI.listEditorSessions(params)
      editorSessions.value = res.data?.results || res.data || []
    } else if (activeTab.value === 'productivity') {
      // Load productivity metrics for all editors
      const res = await blogPagesAPI.getMyProductivityMetrics(params)
      productivityMetrics.value = res.data?.results || res.data || []
    } else if (activeTab.value === 'analytics') {
      const res = await blogPagesAPI.getEditorAnalytics(params)
      editorAnalytics.value = res.data
      topEditors.value = res.data?.top_editors || []
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
    const sessionsRes = await blogPagesAPI.listEditorSessions(params)
    const sessions = sessionsRes.data?.results || sessionsRes.data || []
    
    overview.value = {
      total_sessions: sessions.length,
      avg_session_time: sessions.reduce((sum, s) => sum + (s.duration || 0), 0) / (sessions.length || 1),
      posts_created: sessions.filter(s => s.blog_post_id).length,
      productivity_score: sessions.reduce((sum, s) => sum + (s.actions_count || 0), 0) / (sessions.length || 1),
      sessions_change: 0,
      session_time_change: 0,
      posts_change: 0,
      productivity_change: 0,
    }
  } catch (error) {
    console.error('Failed to load overview:', error)
  }
}

const formatNumber = (value) => {
  return parseInt(value || 0).toLocaleString()
}

const formatDuration = (seconds) => {
  if (!seconds) return '0m'
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  if (hours > 0) {
    return `${hours}h ${minutes}m`
  }
  return `${minutes}m`
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString()
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

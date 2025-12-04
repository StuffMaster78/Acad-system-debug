<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Editor Analytics Dashboard</h1>
        <p class="mt-2 text-gray-600">Track editor productivity and usage patterns</p>
      </div>
      <div class="flex items-center gap-4">
        <select
          v-model="selectedWebsiteId"
          @change="loadMetrics"
          class="border rounded px-3 py-2"
        >
          <option value="">Select Website</option>
          <option v-for="website in websites" :key="website.id" :value="website.id">
            {{ website.name }}
          </option>
        </select>
        <button
          @click="calculateMetrics"
          :disabled="!selectedWebsiteId || calculating"
          class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {{ calculating ? 'Calculating...' : 'Calculate Metrics' }}
        </button>
      </div>
    </div>

    <!-- Current User Metrics -->
    <div v-if="myMetrics" class="card">
      <h2 class="text-xl font-semibold mb-4">My Productivity Metrics</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="p-4 bg-blue-50 rounded-lg">
          <div class="text-sm text-gray-600 mb-1">Productivity Score</div>
          <div class="text-3xl font-bold text-blue-700">{{ Math.round(myMetrics.productivity_score) }}/100</div>
        </div>
        <div class="p-4 bg-green-50 rounded-lg">
          <div class="text-sm text-gray-600 mb-1">Total Sessions</div>
          <div class="text-3xl font-bold text-green-700">{{ myMetrics.total_sessions }}</div>
        </div>
        <div class="p-4 bg-purple-50 rounded-lg">
          <div class="text-sm text-gray-600 mb-1">Words/Min</div>
          <div class="text-3xl font-bold text-purple-700">{{ Math.round(myMetrics.words_per_minute) }}</div>
        </div>
        <div class="p-4 bg-yellow-50 rounded-lg">
          <div class="text-sm text-gray-600 mb-1">Avg Session</div>
          <div class="text-3xl font-bold text-yellow-700">{{ Math.round(myMetrics.average_session_duration) }}m</div>
        </div>
      </div>

      <!-- Tool Usage -->
      <div class="mt-6">
        <h3 class="text-lg font-semibold mb-3">Tool Usage</h3>
        <div class="grid grid-cols-3 gap-4">
          <div class="text-center p-3 bg-gray-50 rounded">
            <div class="text-2xl font-bold">{{ myMetrics.templates_used_count }}</div>
            <div class="text-sm text-gray-600">Templates Used</div>
          </div>
          <div class="text-center p-3 bg-gray-50 rounded">
            <div class="text-2xl font-bold">{{ myMetrics.snippets_used_count }}</div>
            <div class="text-sm text-gray-600">Snippets Used</div>
          </div>
          <div class="text-center p-3 bg-gray-50 rounded">
            <div class="text-2xl font-bold">{{ myMetrics.blocks_used_count }}</div>
            <div class="text-sm text-gray-600">Blocks Used</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Sessions -->
    <div class="card">
      <h2 class="text-xl font-semibold mb-4">Recent Editing Sessions</h2>
      <div v-if="loadingSessions" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
      <div v-else-if="sessions.length" class="space-y-3">
        <div
          v-for="session in sessions"
          :key="session.id"
          class="border rounded-lg p-4"
        >
          <div class="flex items-center justify-between">
            <div class="flex-1">
              <div class="font-medium">{{ session.content_title }}</div>
              <div class="text-sm text-gray-600 mt-1">
                {{ formatDate(session.session_start) }} • 
                Duration: {{ Math.round(session.duration_minutes) }} minutes
              </div>
            </div>
            <div class="flex items-center gap-4 text-sm">
              <div>
                <span class="text-gray-600">Keystrokes:</span>
                <span class="font-semibold ml-1">{{ session.total_keystrokes }}</span>
              </div>
              <div>
                <span class="text-gray-600">Actions:</span>
                <span class="font-semibold ml-1">{{ session.total_actions }}</span>
              </div>
              <span
                class="px-2 py-1 rounded text-xs"
                :class="session.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
              >
                {{ session.is_active ? 'Active' : 'Ended' }}
              </span>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-12 text-gray-500">
        No editing sessions found.
      </div>
    </div>

    <!-- Productivity Trends -->
    <div v-if="productivityHistory.length" class="card">
      <h2 class="text-xl font-semibold mb-4">Productivity Trends</h2>
      <div class="space-y-4">
        <div
          v-for="period in productivityHistory"
          :key="period.id"
          class="border rounded-lg p-4"
        >
          <div class="flex items-center justify-between mb-2">
            <div>
              <div class="font-medium">{{ formatPeriod(period.period_start, period.period_end) }}</div>
              <div class="text-sm text-gray-600">{{ period.user_username }}</div>
            </div>
            <div class="text-right">
              <div class="text-2xl font-bold" :class="getScoreClass(period.productivity_score)">
                {{ Math.round(period.productivity_score) }}
              </div>
              <div class="text-xs text-gray-500">Productivity Score</div>
            </div>
          </div>
          <div class="grid grid-cols-4 gap-2 text-sm">
            <div>
              <span class="text-gray-600">Sessions:</span>
              <span class="font-semibold ml-1">{{ period.total_sessions }}</span>
            </div>
            <div>
              <span class="text-gray-600">WPM:</span>
              <span class="font-semibold ml-1">{{ Math.round(period.words_per_minute) }}</span>
            </div>
            <div>
              <span class="text-gray-600">Keystrokes:</span>
              <span class="font-semibold ml-1">{{ period.total_keystrokes.toLocaleString() }}</span>
            </div>
            <div>
              <span class="text-gray-600">Tools:</span>
              <span class="font-semibold ml-1">
                {{ period.templates_used_count + period.snippets_used_count + period.blocks_used_count }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import blogPagesAPI from '@/api/blog-pages'
import websitesAPI from '@/api/websites'

const websites = ref([])
const selectedWebsiteId = ref('')
const myMetrics = ref(null)
const sessions = ref([])
const productivityHistory = ref([])
const loadingSessions = ref(false)
const calculating = ref(false)

const loadWebsites = async () => {
  try {
    const res = await websitesAPI.listWebsites({})
    websites.value = res.data?.results || res.data || []
  } catch (e) {
    console.error('Failed to load websites:', e)
  }
}

const loadMetrics = async () => {
  if (!selectedWebsiteId.value) {
    myMetrics.value = null
    sessions.value = []
    return
  }

  try {
    // Load my metrics
    const metricsRes = await blogPagesAPI.getMyProductivityMetrics({
      website_id: selectedWebsiteId.value
    })
    myMetrics.value = metricsRes.data

    // Load recent sessions
    await loadSessions()
  } catch (e) {
    console.error('Failed to load metrics:', e)
  }
}

const loadSessions = async () => {
  if (!selectedWebsiteId.value) return

  loadingSessions.value = true
  try {
    const res = await blogPagesAPI.listEditorSessions({
      website: selectedWebsiteId.value,
      is_active: false
    })
    sessions.value = (res.data?.results || res.data || []).slice(0, 10) // Last 10 sessions
  } catch (e) {
    console.error('Failed to load sessions:', e)
  } finally {
    loadingSessions.value = false
  }
}

const calculateMetrics = async () => {
  if (!selectedWebsiteId.value) return

  calculating.value = true
  try {
    await blogPagesAPI.calculateProductivityMetrics({
      website_id: selectedWebsiteId.value
    })
    await loadMetrics()
  } catch (e) {
    console.error('Failed to calculate metrics:', e)
    alert('Failed to calculate metrics. Please try again.')
  } finally {
    calculating.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatPeriod = (start, end) => {
  const startDate = new Date(start).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  const endDate = new Date(end).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  return `${startDate} - ${endDate}`
}

const getScoreClass = (score) => {
  if (score >= 80) return 'text-green-700'
  if (score >= 60) return 'text-blue-700'
  if (score >= 40) return 'text-yellow-700'
  return 'text-red-700'
}

onMounted(async () => {
  await loadWebsites()
})
</script>

<style scoped>
.card {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
}
</style>


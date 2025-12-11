<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Writer Badge Analytics</h1>
        <p class="mt-2 text-gray-600 dark:text-gray-400">Analytics and insights for writer badge achievements</p>
      </div>
      <button
        @click="refreshData"
        :disabled="loading"
        class="btn btn-secondary flex items-center gap-2"
      >
        <span>🔄</span>
        <span>Refresh</span>
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card p-4 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 dark:from-blue-900/20 dark:to-blue-800/20 dark:border-blue-700">
        <p class="text-sm font-medium text-blue-700 dark:text-blue-300 mb-1">Total Badges</p>
        <p class="text-3xl font-bold text-blue-900 dark:text-blue-100">{{ analytics.total_badges || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-green-50 to-green-100 border border-green-200 dark:from-green-900/20 dark:to-green-800/20 dark:border-green-700">
        <p class="text-sm font-medium text-green-700 dark:text-green-300 mb-1">Writers with Badges</p>
        <p class="text-3xl font-bold text-green-900 dark:text-green-100">{{ analytics.writers_with_badges || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 dark:from-purple-900/20 dark:to-purple-800/20 dark:border-purple-700">
        <p class="text-sm font-medium text-purple-700 dark:text-purple-300 mb-1">Total Achievements</p>
        <p class="text-3xl font-bold text-purple-900 dark:text-purple-100">{{ analytics.total_achievements || 0 }}</p>
      </div>
      <div class="card p-4 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 dark:from-orange-900/20 dark:to-orange-800/20 dark:border-orange-700">
        <p class="text-sm font-medium text-orange-700 dark:text-orange-300 mb-1">Avg Badges/Writer</p>
        <p class="text-3xl font-bold text-orange-900 dark:text-orange-100">{{ formatNumber(analytics.avg_badges_per_writer) }}</p>
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
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
          ]"
        >
          {{ tab.label }}
        </button>
      </nav>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Loading badge analytics...</p>
    </div>

    <!-- Overview Tab -->
    <div v-else-if="activeTab === 'overview'" class="space-y-6">
      <div class="card p-6">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Badge Distribution</h2>
        <div v-if="distribution.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          No badge distribution data available
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="item in distribution"
            :key="item.badge_type || item.name"
            class="p-4 border rounded-lg hover:shadow-md transition-shadow"
          >
            <h3 class="font-semibold text-gray-900 dark:text-white mb-2">{{ item.badge_type || item.name }}</h3>
            <p class="text-2xl font-bold text-primary-600 dark:text-primary-400">{{ item.count || 0 }}</p>
            <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">{{ item.percentage || 0 }}% of writers</p>
          </div>
        </div>
      </div>

      <div class="card p-6">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Recent Achievements</h2>
        <div v-if="achievements.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
          No achievements data available
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="achievement in achievements.slice(0, 10)"
            :key="achievement.id"
            class="p-3 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          >
            <div class="flex justify-between items-center">
              <div>
                <p class="font-medium text-gray-900 dark:text-white">{{ achievement.writer_name || achievement.writer?.user?.username || achievement.writer?.username || achievement.writer_id || 'N/A' }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">{{ achievement.badge_name || achievement.badge || 'Badge' }}</p>
              </div>
              <span class="text-sm text-gray-500 dark:text-gray-400">{{ formatDate(achievement.earned_at || achievement.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Leaderboard Tab -->
    <div v-else-if="activeTab === 'leaderboard'" class="card overflow-hidden">
      <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">Badge Leaderboard</h2>
        <select
          v-model="leaderboardType"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadLeaderboard"
        >
          <option value="">All Badges</option>
          <option v-for="badgeType in badgeTypes" :key="badgeType" :value="badgeType">
            {{ badgeType }}
          </option>
        </select>
      </div>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-800">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Rank</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Writer</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Badge</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Count</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-if="leaderboard.length === 0" class="text-center">
              <td colspan="4" class="px-6 py-12 text-gray-500 dark:text-gray-400">
                No leaderboard data available
              </td>
            </tr>
            <tr
              v-for="(entry, index) in leaderboard"
              :key="entry.writer_id || index"
              class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="text-lg font-bold text-primary-600 dark:text-primary-400">#{{ index + 1 }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                {{ entry.writer_name || entry.writer?.user?.username || entry.writer?.username || entry.writer_id || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ entry.badge_name || entry.badge || 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                {{ entry.count || entry.badge_count || 0 }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Trends Tab -->
    <div v-else-if="activeTab === 'trends'" class="card p-6">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">Badge Trends</h2>
        <select
          v-model.number="trendDays"
          class="px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
          @change="loadTrends"
        >
          <option :value="7">Last 7 days</option>
          <option :value="30">Last 30 days</option>
          <option :value="90">Last 90 days</option>
          <option :value="180">Last 180 days</option>
        </select>
      </div>
      <div v-if="trends.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
        No trends data available
      </div>
      <div v-else class="space-y-4">
        <div
          v-for="trend in trends"
          :key="trend.date || trend.period"
          class="p-4 border rounded-lg"
        >
          <div class="flex justify-between items-center mb-2">
            <span class="font-medium text-gray-900 dark:text-white">{{ formatDate(trend.date || trend.period) }}</span>
            <span class="text-sm text-gray-500 dark:text-gray-400">{{ trend.count || 0 }} badges earned</span>
          </div>
          <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              class="bg-primary-600 h-2 rounded-full transition-all"
              :style="{ width: `${Math.min((trend.count / maxTrendCount) * 100, 100)}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'
import writerManagementAPI from '@/api/writer-management'

const { error: showError } = useToast()

const loading = ref(false)
const activeTab = ref('overview')
const analytics = ref({})
const distribution = ref([])
const achievements = ref([])
const leaderboard = ref([])
const trends = ref([])
const leaderboardType = ref('')
const trendDays = ref(30)
const badgeTypes = ref([])

const tabs = [
  { id: 'overview', label: 'Overview' },
  { id: 'leaderboard', label: 'Leaderboard' },
  { id: 'trends', label: 'Trends' },
]

const maxTrendCount = computed(() => {
  if (trends.value.length === 0) return 1
  return Math.max(...trends.value.map(t => t.count || 0), 1)
})

const formatNumber = (num) => {
  if (!num && num !== 0) return '0'
  return Number(num).toFixed(1)
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString()
}

const loadAnalytics = async () => {
  try {
    const response = await writerManagementAPI.getBadgeAnalytics()
    analytics.value = response.data || {}
  } catch (error) {
    console.error('Error loading analytics:', error)
  }
}

const loadDistribution = async () => {
  try {
    const response = await writerManagementAPI.getBadgeDistribution()
    distribution.value = response.data.distribution || response.data || []
  } catch (error) {
    console.error('Error loading distribution:', error)
  }
}

const loadAchievements = async () => {
  try {
    const response = await writerManagementAPI.getBadgeAchievements()
    achievements.value = response.data.results || response.data.achievements || response.data || []
  } catch (error) {
    console.error('Error loading achievements:', error)
  }
}

const loadLeaderboard = async () => {
  try {
    const response = await writerManagementAPI.getBadgeLeaderboard(leaderboardType.value || null, 50)
    leaderboard.value = response.data.leaderboard || response.data || []
  } catch (error) {
    console.error('Error loading leaderboard:', error)
  }
}

const loadTrends = async () => {
  try {
    const response = await writerManagementAPI.getBadgeTrends(trendDays.value)
    trends.value = response.data.trends || response.data || []
  } catch (error) {
    console.error('Error loading trends:', error)
  }
}

const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadAnalytics(),
      loadDistribution(),
      loadAchievements(),
      loadLeaderboard(),
      loadTrends(),
    ])
  } catch (error) {
    showError('Failed to refresh badge analytics')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  refreshData()
})
</script>


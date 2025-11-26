<template>
  <div class="space-y-6 p-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Badge Analytics & Achievements</h1>
        <p class="mt-2 text-gray-600">Track your badge progress and achievements</p>
      </div>
      <button
        @click="loadAllData"
        :disabled="loading"
        class="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition-colors disabled:opacity-50"
      >
        {{ loading ? 'Loading...' : 'Refresh' }}
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="bg-white rounded-lg shadow-sm p-12">
      <div class="flex items-center justify-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    </div>

    <!-- Content -->
    <div v-else class="space-y-6">
      <!-- Achievement Milestones -->
      <div v-if="achievements && achievements.length > 0" class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <span>🏆</span> Achievement Milestones
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="achievement in achievements"
            :key="achievement.key"
            class="p-4 border rounded-lg hover:shadow-md transition-shadow"
            :class="achievement.achieved ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'"
          >
            <div class="flex items-center gap-3">
              <span class="text-3xl">{{ achievement.icon }}</span>
              <div class="flex-1">
                <p class="font-semibold text-gray-900">{{ achievement.name }}</p>
                <p class="text-sm text-gray-600">{{ achievement.description }}</p>
                <div v-if="achievement.progress !== undefined" class="mt-2">
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div
                      class="bg-primary-600 h-2 rounded-full transition-all duration-300"
                      :style="{ width: `${Math.min(100, (achievement.progress / achievement.threshold) * 100)}%` }"
                    ></div>
                  </div>
                  <p class="text-xs text-gray-500 mt-1">
                    {{ achievement.progress }} / {{ achievement.threshold }}
                  </p>
                </div>
                <p v-else-if="achievement.achieved" class="text-xs text-green-600 mt-1 font-medium">
                  ✓ Achieved
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Badge Performance -->
      <div v-if="badgePerformance" class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <span>📊</span> Badge Performance
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="text-center p-4 bg-gray-50 rounded-lg">
            <p class="text-3xl font-bold text-gray-900">{{ badgePerformance.total_badges || 0 }}</p>
            <p class="text-sm text-gray-600 mt-1">Total Badges</p>
          </div>
          <div class="text-center p-4 bg-gray-50 rounded-lg">
            <p class="text-3xl font-bold text-primary-600">{{ badgePerformance.active_badges || 0 }}</p>
            <p class="text-sm text-gray-600 mt-1">Active Badges</p>
          </div>
          <div class="text-center p-4 bg-gray-50 rounded-lg">
            <p class="text-3xl font-bold text-green-600">{{ badgePerformance.recent_badges || 0 }}</p>
            <p class="text-sm text-gray-600 mt-1">Recent (30 days)</p>
          </div>
        </div>
      </div>

      <!-- Badge Analytics -->
      <div v-if="analytics" class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <span>📈</span> Badge Analytics
        </h2>
        <div class="space-y-4">
          <div v-if="analytics.badge_distribution" class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div
              v-for="(count, type) in analytics.badge_distribution"
              :key="type"
              class="p-4 bg-gray-50 rounded-lg text-center"
            >
              <p class="text-2xl font-bold text-gray-900">{{ count }}</p>
              <p class="text-sm text-gray-600 mt-1 capitalize">{{ type.replace('_', ' ') }}</p>
            </div>
          </div>

          <div v-if="analytics.top_badges && analytics.top_badges.length > 0" class="mt-6">
            <h3 class="text-lg font-medium text-gray-900 mb-3">Top Badges</h3>
            <div class="space-y-2">
              <div
                v-for="badge in analytics.top_badges"
                :key="badge.id"
                class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div class="flex items-center gap-3">
                  <span class="text-2xl">{{ badge.icon || '🏅' }}</span>
                  <div>
                    <p class="font-medium text-gray-900">{{ badge.name }}</p>
                    <p class="text-xs text-gray-600">{{ badge.type }}</p>
                  </div>
                </div>
                <div class="text-right">
                  <p class="text-sm font-medium text-gray-900">{{ badge.count || 0 }} writers</p>
                  <p class="text-xs text-gray-500">Have this badge</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Performance Milestones -->
      <div v-if="performanceMilestones && performanceMilestones.length > 0" class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <span>🎯</span> Performance Milestones
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div
            v-for="milestone in performanceMilestones"
            :key="milestone.key"
            class="p-4 border rounded-lg"
            :class="milestone.achieved ? 'bg-green-50 border-green-200' : 'bg-gray-50 border-gray-200'"
          >
            <div class="flex items-center gap-3">
              <span class="text-2xl">{{ milestone.icon }}</span>
              <div class="flex-1">
                <p class="font-semibold text-gray-900">{{ milestone.name }}</p>
                <p class="text-sm text-gray-600">{{ milestone.description }}</p>
                <p v-if="milestone.achieved" class="text-xs text-green-600 mt-1 font-medium">
                  ✓ Achieved on {{ formatDate(milestone.achieved_at) }}
                </p>
                <p v-else class="text-xs text-gray-500 mt-1">
                  Progress: {{ milestone.current }} / {{ milestone.threshold }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Link to Badge Management -->
      <div class="bg-white rounded-lg shadow-sm p-6 text-center">
        <router-link
          to="/writer/badges"
          class="inline-block px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium"
        >
          View All My Badges →
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import writerManagementAPI from '@/api/writer-management'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const { error: showError } = useToast()

const loading = ref(false)
const achievements = ref([])
const badgePerformance = ref(null)
const analytics = ref(null)
const performanceMilestones = ref([])

const loadAllData = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadAchievements(),
      loadBadgePerformance(),
      loadAnalytics(),
      loadPerformanceMilestones(),
    ])
  } catch (error) {
    console.error('Failed to load badge data:', error)
    showError(getErrorMessage(error, 'Failed to load badge analytics'))
  } finally {
    loading.value = false
  }
}

const loadAchievements = async () => {
  try {
    const response = await writerManagementAPI.getBadgeAchievements()
    achievements.value = response.data.results || response.data || []
  } catch (error) {
    console.error('Failed to load achievements:', error)
    achievements.value = []
  }
}

const loadBadgePerformance = async () => {
  try {
    const response = await writerManagementAPI.getBadgePerformance()
    badgePerformance.value = response.data
  } catch (error) {
    console.error('Failed to load badge performance:', error)
    badgePerformance.value = null
  }
}

const loadAnalytics = async () => {
  try {
    const response = await writerManagementAPI.getBadgeAnalytics()
    analytics.value = response.data
  } catch (error) {
    console.error('Failed to load analytics:', error)
    analytics.value = null
  }
}

const loadPerformanceMilestones = async () => {
  try {
    // This might come from achievements or a separate endpoint
    // For now, we'll extract from achievements
    const response = await writerManagementAPI.getBadgeAchievements()
    const data = response.data.results || response.data || []
    performanceMilestones.value = data.filter(a => a.type === 'performance_milestone')
  } catch (error) {
    console.error('Failed to load performance milestones:', error)
    performanceMilestones.value = []
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

onMounted(() => {
  loadAllData()
})
</script>


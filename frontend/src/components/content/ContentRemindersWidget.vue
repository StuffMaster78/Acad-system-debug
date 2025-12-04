<template>
  <div class="space-y-4">
    <!-- Website Selector for Historical Trends -->
    <div v-if="monthlyStats.length > 0" class="card">
      <label class="block text-sm font-medium mb-2">View Historical Trends</label>
      <select
        v-model="selectedWebsiteId"
        @change="loadHistoricalTrends"
        class="w-full border rounded px-3 py-2"
      >
        <option value="">Select Website</option>
        <option
          v-for="stat in monthlyStats"
          :key="stat.website_id"
          :value="stat.website_id"
        >
          {{ stat.website_name }}
        </option>
      </select>
    </div>

    <!-- Historical Trends -->
    <div v-if="selectedWebsiteId && historicalTrends" class="card">
      <h3 class="text-lg font-semibold mb-4">Publishing Trends (Last 12 Months)</h3>
      <div v-if="loadingTrends" class="flex items-center justify-center py-8">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
      </div>
      <div v-else class="space-y-4">
        <div class="grid grid-cols-3 gap-4 mb-4">
          <div class="text-center p-3 bg-blue-50 rounded">
            <div class="text-2xl font-bold text-blue-700">{{ historicalTrends.summary.average_published }}</div>
            <div class="text-sm text-gray-600">Avg Posts/Month</div>
          </div>
          <div class="text-center p-3 bg-green-50 rounded">
            <div class="text-2xl font-bold text-green-700">{{ historicalTrends.summary.months_met_target }}</div>
            <div class="text-sm text-gray-600">Months Met Target</div>
          </div>
          <div class="text-center p-3 bg-purple-50 rounded">
            <div class="text-2xl font-bold text-purple-700">{{ historicalTrends.summary.success_rate }}%</div>
            <div class="text-sm text-gray-600">Success Rate</div>
          </div>
        </div>

        <!-- Simple Bar Chart -->
        <div class="space-y-2">
          <div
            v-for="month in historicalTrends.monthly_data"
            :key="month.month"
            class="flex items-center gap-2"
          >
            <div class="w-24 text-xs text-gray-600">{{ formatMonthShort(month.month) }}</div>
            <div class="flex-1 bg-gray-200 rounded-full h-6 relative">
              <div
                class="h-6 rounded-full flex items-center justify-end pr-2 text-xs font-semibold"
                :class="month.status === 'met' ? 'bg-green-500 text-white' : 'bg-yellow-500 text-white'"
                :style="{ width: `${Math.min(month.percentage, 100)}%` }"
              >
                <span v-if="month.percentage >= 20">{{ month.published }}</span>
              </div>
              <span
                v-if="month.percentage < 20"
                class="absolute left-2 text-xs font-semibold text-gray-700"
              >
                {{ month.published }}
              </span>
            </div>
            <div class="w-16 text-xs text-gray-600 text-right">
              {{ month.published }}/{{ month.target }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Monthly Publishing Targets -->
    <div class="card">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold">Monthly Publishing Targets</h3>
        <router-link
          to="/admin/category-publishing-targets"
          class="text-sm text-blue-600 hover:text-blue-800"
        >
          Manage Category Targets →
        </router-link>
      </div>
      <div v-if="loadingTargets" class="flex items-center justify-center py-8">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
      </div>
      <div v-else-if="monthlyStats.length" class="space-y-3">
        <div
          v-for="stat in monthlyStats"
          :key="stat.website_id"
          class="border rounded-lg p-4"
          :class="getProgressClass(stat.percentage)"
        >
          <div class="flex items-center justify-between mb-2">
            <div>
              <h4 class="font-medium">{{ stat.website_name }}</h4>
              <p class="text-sm text-gray-600">{{ stat.month }}</p>
            </div>
            <div class="text-right">
              <div class="text-2xl font-bold">{{ stat.published }}</div>
              <div class="text-sm text-gray-500">of {{ stat.target }}</div>
            </div>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-2 mb-2">
            <div
              class="h-2 rounded-full transition-all"
              :class="getProgressBarClass(stat.percentage)"
              :style="{ width: `${Math.min(stat.percentage, 100)}%` }"
            ></div>
          </div>
          <p class="text-sm" :class="getMessageClass(stat.percentage)">
            <span v-if="stat.published === 0">
              You have not published any content this month.
            </span>
            <span v-else-if="stat.percentage < 50">
              You only published {{ stat.published }} article(s) this month. Target: {{ stat.target }}. Please strive to add more.
            </span>
            <span v-else-if="stat.percentage < 100">
              Good progress! {{ stat.remaining }} more article(s) needed to reach target.
            </span>
            <span v-else>
              🎉 Target achieved! Great work!
            </span>
          </p>
        </div>
      </div>
      <div v-else class="text-center py-8 text-gray-500">
        No publishing targets configured.
      </div>
    </div>

    <!-- Stale Content Reminders -->
    <div class="card">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold">Content Freshness Reminders</h3>
        <button
          @click="refreshReminders"
          :disabled="refreshingReminders"
          class="text-sm text-blue-600 hover:text-blue-800 disabled:opacity-50"
        >
          {{ refreshingReminders ? 'Refreshing...' : 'Refresh' }}
        </button>
      </div>
      <div v-if="loadingReminders" class="flex items-center justify-center py-8">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
      </div>
      <div v-else-if="staleContent.length" class="space-y-2">
        <div
          v-for="item in staleContent"
          :key="item.id"
          class="border rounded-lg p-3 flex items-center justify-between"
          :class="item.is_acknowledged ? 'bg-gray-50 opacity-75' : 'bg-yellow-50'"
        >
          <div class="flex-1">
            <div class="font-medium">{{ item.blog_title }}</div>
            <div class="text-sm text-gray-600">
              {{ item.website_name }} • Not updated in {{ item.days_since_update }} days
            </div>
          </div>
          <div class="flex items-center gap-2">
            <button
              v-if="!item.is_acknowledged"
              @click="acknowledgeReminder(item.id)"
              class="text-sm text-blue-600 hover:text-blue-800"
            >
              Acknowledge
            </button>
            <a
              :href="item.blog_url"
              target="_blank"
              class="text-sm text-purple-600 hover:text-purple-800"
            >
              Edit
            </a>
          </div>
        </div>
      </div>
      <div v-else class="text-center py-8 text-gray-500">
        <p>✅ All content is up to date!</p>
        <p class="text-xs mt-2">Content is considered stale if not updated in 3+ months.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import blogPagesAPI from '@/api/blog-pages'

const monthlyStats = ref([])
const staleContent = ref([])
const historicalTrends = ref(null)
const loadingTargets = ref(false)
const loadingReminders = ref(false)
const loadingTrends = ref(false)
const refreshingReminders = ref(false)
const selectedWebsiteId = ref('')

const loadMonthlyStats = async () => {
  loadingTargets.value = true
  try {
    const res = await blogPagesAPI.getMonthlyStats()
    monthlyStats.value = res.data || []
  } catch (e) {
    console.error('Failed to load monthly stats:', e)
  } finally {
    loadingTargets.value = false
  }
}

const loadStaleContent = async () => {
  loadingReminders.value = true
  try {
    const res = await blogPagesAPI.getContentFreshnessReminders({ is_acknowledged: false })
    staleContent.value = res.data?.results || res.data || []
  } catch (e) {
    console.error('Failed to load stale content:', e)
  } finally {
    loadingReminders.value = false
  }
}

const refreshReminders = async () => {
  refreshingReminders.value = true
  try {
    await blogPagesAPI.refreshFreshnessReminders({ months: 3 })
    await loadStaleContent()
  } catch (e) {
    console.error('Failed to refresh reminders:', e)
  } finally {
    refreshingReminders.value = false
  }
}

const acknowledgeReminder = async (id) => {
  try {
    await blogPagesAPI.acknowledgeFreshnessReminder(id)
    await loadStaleContent()
  } catch (e) {
    console.error('Failed to acknowledge reminder:', e)
  }
}

const getProgressClass = (percentage) => {
  if (percentage === 0) return 'border-red-200 bg-red-50'
  if (percentage < 50) return 'border-yellow-200 bg-yellow-50'
  if (percentage < 100) return 'border-blue-200 bg-blue-50'
  return 'border-green-200 bg-green-50'
}

const getProgressBarClass = (percentage) => {
  if (percentage === 0) return 'bg-red-500'
  if (percentage < 50) return 'bg-yellow-500'
  if (percentage < 100) return 'bg-blue-500'
  return 'bg-green-500'
}

const getMessageClass = (percentage) => {
  if (percentage === 0) return 'text-red-700'
  if (percentage < 50) return 'text-yellow-700'
  if (percentage < 100) return 'text-blue-700'
  return 'text-green-700'
}

const loadHistoricalTrends = async () => {
  if (!selectedWebsiteId.value) {
    historicalTrends.value = null
    return
  }

  loadingTrends.value = true
  try {
    const res = await blogPagesAPI.getPublishingHistory({
      website_id: selectedWebsiteId.value,
      months: 12
    })
    historicalTrends.value = res.data
  } catch (e) {
    console.error('Failed to load historical trends:', e)
  } finally {
    loadingTrends.value = false
  }
}

const formatMonthShort = (monthString) => {
  const [year, month] = monthString.split('-')
  const date = new Date(year, parseInt(month) - 1, 1)
  return date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' })
}

watch(selectedWebsiteId, () => {
  if (selectedWebsiteId.value) {
    loadHistoricalTrends()
  }
})

onMounted(async () => {
  await Promise.all([loadMonthlyStats(), loadStaleContent()])
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


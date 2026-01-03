<template>
  <div class="space-y-6">
    <!-- Summary Stats -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="card p-4">
        <div class="text-sm text-gray-600 dark:text-gray-400">Total Views</div>
        <div class="text-2xl font-bold text-gray-900 dark:text-white">{{ analytics.total_views || 0 }}</div>
      </div>
      <div class="card p-4">
        <div class="text-sm text-gray-600 dark:text-gray-400">Unique Viewers</div>
        <div class="text-2xl font-bold text-gray-900 dark:text-white">{{ analytics.unique_viewers || 0 }}</div>
      </div>
      <div class="card p-4">
        <div class="text-sm text-gray-600 dark:text-gray-400">Acknowledged</div>
        <div class="text-2xl font-bold text-gray-900 dark:text-white">{{ analytics.acknowledged_count || 0 }}</div>
      </div>
      <div class="card p-4">
        <div class="text-sm text-gray-600 dark:text-gray-400">Engagement Rate</div>
        <div class="text-2xl font-bold text-primary-600 dark:text-primary-400">{{ analytics.engagement_rate || 0 }}%</div>
      </div>
    </div>

    <!-- Views by Role -->
    <div class="card p-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold">Views by Role</h3>
      </div>
      <div class="space-y-2">
        <div
          v-for="(count, role) in analytics.views_by_role"
          :key="role"
          class="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded"
        >
          <span class="font-medium capitalize">{{ role }}</span>
          <span class="text-primary-600 dark:text-primary-400 font-semibold">{{ count }}</span>
        </div>
        <div v-if="!analytics.views_by_role || Object.keys(analytics.views_by_role).length === 0" class="text-gray-500 text-center py-4">
          No data available
        </div>
      </div>
    </div>

    <!-- Views Over Time Chart -->
    <div class="card p-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold">Views Over Time (Last 30 Days)</h3>
      </div>
      <div class="space-y-2">
        <div
          v-for="item in analytics.views_over_time"
          :key="item.date"
          class="flex items-center gap-4"
        >
          <div class="w-24 text-sm text-gray-600 dark:text-gray-400">{{ formatDate(item.date) }}</div>
          <div class="flex-1">
            <div class="flex items-center gap-2">
              <div class="h-4 bg-primary-600 rounded" :style="{ width: `${(item.count / maxViews) * 100}%` }"></div>
              <span class="text-sm font-medium">{{ item.count }}</span>
            </div>
          </div>
        </div>
        <div v-if="!analytics.views_over_time || analytics.views_over_time.length === 0" class="text-gray-500 text-center py-4">
          No data available
        </div>
      </div>
    </div>

    <!-- Readers List -->
    <div class="card p-6">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold">Readers ({{ analytics.readers?.length || 0 }})</h3>
        <button
          @click="exportCSV"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-sm"
        >
          Export to CSV
        </button>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-200 dark:border-gray-700">
              <th class="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">User</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Viewed At</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Time Spent</th>
              <th class="text-left py-3 px-4 font-semibold text-gray-700 dark:text-gray-300">Acknowledged</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="reader in analytics.readers"
              :key="reader.id"
              class="border-b border-gray-100 dark:border-gray-800"
            >
              <td class="py-3 px-4">
                <div>
                  <div class="font-medium">{{ reader.user_name || reader.user_email }}</div>
                  <div class="text-sm text-gray-500 dark:text-gray-400">{{ reader.user_email }}</div>
                </div>
              </td>
              <td class="py-3 px-4 text-sm">{{ formatDateTime(reader.viewed_at) }}</td>
              <td class="py-3 px-4 text-sm">{{ reader.time_spent ? `${reader.time_spent}s` : '—' }}</td>
              <td class="py-3 px-4">
                <span :class="reader.acknowledged ? 'text-green-600' : 'text-gray-500'" class="text-sm">
                  {{ reader.acknowledged ? '✓ Yes' : 'No' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="!analytics.readers || analytics.readers.length === 0" class="text-center py-8 text-gray-500">
          No readers yet
        </div>
      </div>
    </div>

    <!-- Non-Readers Info -->
    <div v-if="analytics.non_readers_count > 0" class="card p-6 bg-yellow-50 dark:bg-yellow-900/20">
      <div class="flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold text-yellow-800 dark:text-yellow-200">Non-Readers</h3>
          <p class="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
            {{ analytics.non_readers_count }} user(s) haven't viewed this announcement yet
          </p>
        </div>
        <button
          @click="viewNonReaders"
          class="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 text-sm"
        >
          View List
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  analytics: {
    type: Object,
    required: true
  },
  announcement: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['export'])

const maxViews = computed(() => {
  if (!props.analytics.views_over_time || props.analytics.views_over_time.length === 0) return 1
  return Math.max(...props.analytics.views_over_time.map(item => item.count), 1)
})

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric'
  })
}

const formatDateTime = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const exportCSV = () => {
  emit('export')
}

const viewNonReaders = () => {
  // This could open a modal or navigate to a detailed view
  alert(`There are ${props.analytics.non_readers_count} users who haven't viewed this announcement.`)
}
</script>


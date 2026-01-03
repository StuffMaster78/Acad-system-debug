<template>
  <div
    :class="[
      'card p-6 cursor-pointer transition-all hover:shadow-lg',
      announcement.is_read ? 'bg-white dark:bg-gray-800' : 'bg-blue-50 dark:bg-gray-700 border-blue-200 dark:border-blue-600',
      announcement.is_pinned ? 'border-l-4 border-yellow-500' : ''
    ]"
    @click="$emit('view', announcement)"
  >
    <div class="flex items-start gap-4">
      <!-- Featured Image -->
      <img
        v-if="announcement.featured_image_url"
        :src="announcement.featured_image_url"
        :alt="announcement.title"
        class="w-24 h-24 object-cover rounded-lg flex-shrink-0"
      />

      <div class="flex-1 min-w-0">
        <!-- Header -->
        <div class="flex items-start justify-between gap-2 mb-2">
          <div class="flex items-center gap-2 flex-1 min-w-0">
            <span v-if="!announcement.is_read" class="w-2 h-2 bg-blue-600 rounded-full flex-shrink-0"></span>
            <h3 class="font-semibold text-lg text-gray-900 dark:text-white truncate">
              {{ announcement.title }}
            </h3>
            <span
              :class="getCategoryBadgeClass(announcement.category)"
              class="px-2 py-0.5 rounded text-xs flex-shrink-0"
            >
              {{ getCategoryLabel(announcement.category) }}
            </span>
            <span v-if="announcement.is_pinned" class="text-yellow-500 flex-shrink-0">📌</span>
          </div>
        </div>

        <!-- Message Preview -->
        <p class="text-sm text-gray-600 dark:text-gray-300 mb-3 line-clamp-2">
          {{ truncateMessage(announcement.message) }}
        </p>

        <!-- Footer -->
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
            <span>{{ formatDate(announcement.created_at) }}</span>
            <span v-if="announcement.website_name">{{ announcement.website_name }}</span>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2" @click.stop>
            <button
              v-if="announcement.require_acknowledgement && !announcement.is_acknowledged"
              @click="handleAcknowledge"
              class="px-3 py-1 bg-primary-600 text-white rounded text-xs hover:bg-primary-700 transition-colors"
            >
              Acknowledge
            </button>
            <router-link
              :to="`/announcements/${announcement.id}`"
              class="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 text-sm"
              @click.stop
            >
              Read More →
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import announcementsAPI from '@/api/announcements'

const props = defineProps({
  announcement: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['view', 'acknowledge'])

const truncateMessage = (message) => {
  if (!message) return ''
  const text = message.replace(/<[^>]*>/g, '') // Strip HTML
  return text.length > 150 ? text.substring(0, 150) + '...' : text
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const getCategoryLabel = (category) => {
  const labels = {
    news: 'News',
    update: 'Update',
    maintenance: 'Maintenance',
    promotion: 'Promotion',
    general: 'General'
  }
  return labels[category] || category
}

const getCategoryBadgeClass = (category) => {
  const classes = {
    news: 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300',
    update: 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300',
    maintenance: 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300',
    promotion: 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300',
    general: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
  }
  return classes[category] || classes.general
}

const handleAcknowledge = async () => {
  emit('acknowledge', props.announcement)
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>


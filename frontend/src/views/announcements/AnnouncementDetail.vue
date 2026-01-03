<template>
  <div class="space-y-6">
    <!-- Back Button -->
    <router-link
      to="/announcements"
      class="inline-flex items-center gap-2 text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300"
    >
      ← Back to Announcements
    </router-link>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="card p-6 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300">
      {{ error }}
    </div>

    <!-- Announcement Detail -->
    <div v-else-if="announcement" class="card p-8">
      <!-- Header -->
      <div class="flex items-start justify-between mb-6">
        <div class="flex-1">
          <div class="flex items-center gap-3 mb-3">
            <span
              :class="getCategoryBadgeClass(announcement.category)"
              class="px-3 py-1 rounded text-sm font-medium"
            >
              {{ getCategoryLabel(announcement.category) }}
            </span>
            <span v-if="announcement.is_pinned" class="text-yellow-500 text-xl">📌</span>
            <span v-if="!announcement.is_read" class="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs">
              New
            </span>
          </div>
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            {{ announcement.title }}
          </h1>
          <div class="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
            <span>{{ formatDate(announcement.created_at) }}</span>
            <span v-if="announcement.created_by_name">by {{ announcement.created_by_name }}</span>
            <span v-if="announcement.website_name">{{ announcement.website_name }}</span>
          </div>
        </div>
      </div>

      <!-- Featured Image -->
      <img
        v-if="announcement.featured_image_url"
        :src="announcement.featured_image_url"
        :alt="announcement.title"
        class="w-full h-64 object-cover rounded-lg mb-6"
      />

      <!-- Content -->
      <div
        class="prose dark:prose-invert max-w-none mb-6"
        v-html="formatMessage(announcement.message)"
      ></div>

      <!-- Read More Link -->
      <div v-if="announcement.read_more_url" class="mb-6">
        <a
          :href="announcement.read_more_url"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex items-center gap-2 text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300"
        >
          Read More <span>→</span>
        </a>
      </div>

      <!-- Expiration Notice -->
      <div v-if="announcement.expires_at" class="mb-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
        <p class="text-sm text-yellow-800 dark:text-yellow-200">
          ⏱️ This announcement expires on {{ formatDate(announcement.expires_at) }}
        </p>
      </div>

      <!-- Actions -->
      <div class="flex items-center gap-4 pt-6 border-t border-gray-200 dark:border-gray-700">
        <button
          v-if="announcement.require_acknowledgement && !announcement.is_acknowledged"
          @click="handleAcknowledge"
          class="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Acknowledge
        </button>
        <span v-else-if="announcement.is_acknowledged" class="text-sm text-green-600 dark:text-green-400">
          ✓ Acknowledged
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import announcementsAPI from '@/api/announcements'

const route = useRoute()
const announcement = ref(null)
const loading = ref(false)
const error = ref(null)

const loadAnnouncement = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await announcementsAPI.getAnnouncement(route.params.id)
    announcement.value = response.data

    // Track view (silently fail if it doesn't work)
    try {
      await announcementsAPI.trackView(route.params.id)
      announcement.value.is_read = true
    } catch (viewError) {
      // Silently handle view tracking errors (404s are expected if announcement doesn't exist)
      console.debug('Error tracking view:', viewError)
    }
  } catch (e) {
    error.value = 'Failed to load announcement: ' + (e.response?.data?.detail || e.message)
    console.error('Error loading announcement:', e)
  } finally {
    loading.value = false
  }
}

const handleAcknowledge = async () => {
  try {
    await announcementsAPI.acknowledge(route.params.id)
    announcement.value.is_acknowledged = true
  } catch (e) {
    error.value = 'Failed to acknowledge announcement: ' + (e.response?.data?.detail || e.message)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatMessage = (message) => {
  if (!message) return ''
  // Basic HTML sanitization - in production, use a proper sanitizer
  return message.replace(/\n/g, '<br>')
}

const getCategoryLabel = (category) => {
  const labels = {
    news: 'News',
    update: 'System Update',
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

onMounted(() => {
  loadAnnouncement()
})
</script>


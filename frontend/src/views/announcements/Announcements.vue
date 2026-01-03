<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white">📢 Announcements</h1>
        <p class="text-gray-600 dark:text-gray-400 mt-1">Stay updated with the latest news and updates</p>
      </div>
      <div class="flex items-center gap-4">
        <div v-if="unreadCount > 0" class="text-sm text-gray-600 dark:text-gray-400">
          <span class="font-medium text-primary-600 dark:text-primary-400">{{ unreadCount }}</span> unread
        </div>
        <router-link
          v-if="isAdmin"
          to="/admin/announcements"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm"
        >
          Manage Announcements
        </router-link>
      </div>
    </div>

    <!-- Filters -->
    <div class="card p-4">
      <div class="flex flex-wrap gap-3">
        <select v-model="filters.category" @change="loadAnnouncements" class="border rounded px-3 py-2 dark:bg-gray-800 dark:border-gray-700">
          <option value="">All Categories</option>
          <option value="news">News</option>
          <option value="update">System Update</option>
          <option value="maintenance">Maintenance</option>
          <option value="promotion">Promotion</option>
          <option value="general">General</option>
        </select>
        <select v-model="filters.pinned" @change="loadAnnouncements" class="border rounded px-3 py-2 dark:bg-gray-800 dark:border-gray-700">
          <option value="">All</option>
          <option value="true">Pinned Only</option>
        </select>
        <select v-model="filters.unread" @change="loadAnnouncements" class="border rounded px-3 py-2 dark:bg-gray-800 dark:border-gray-700">
          <option value="">All</option>
          <option value="true">Unread Only</option>
        </select>
        <input
          v-model="filters.search"
          @input="loadAnnouncements"
          type="text"
          placeholder="Search announcements..."
          class="border rounded px-3 py-2 flex-1 min-w-[200px] dark:bg-gray-800 dark:border-gray-700"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!announcements.length" class="card p-12 text-center">
      <p class="text-gray-500 dark:text-gray-400">No announcements found.</p>
    </div>

    <!-- Announcements List -->
    <div v-else class="space-y-4">
      <!-- Pinned Announcements -->
      <div v-if="pinnedAnnouncements.length > 0" class="space-y-4">
        <h2 class="text-lg font-semibold text-gray-700 dark:text-gray-300 flex items-center gap-2">
          <span class="text-yellow-500">📌</span> Pinned
        </h2>
        <AnnouncementCard
          v-for="announcement in pinnedAnnouncements"
          :key="announcement.id"
          :announcement="announcement"
          @view="trackView"
          @acknowledge="handleAcknowledge"
        />
      </div>

      <!-- Regular Announcements -->
      <div v-if="regularAnnouncements.length > 0" class="space-y-4">
        <h2 v-if="pinnedAnnouncements.length > 0" class="text-lg font-semibold text-gray-700 dark:text-gray-300 mt-6">
          Recent
        </h2>
        <AnnouncementCard
          v-for="announcement in regularAnnouncements"
          :key="announcement.id"
          :announcement="announcement"
          @view="trackView"
          @acknowledge="handleAcknowledge"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import announcementsAPI from '@/api/announcements'
import AnnouncementCard from './components/AnnouncementCard.vue'

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.isAdmin || authStore.isSuperAdmin)

const announcements = ref([])
const loading = ref(false)
const unreadCount = ref(0)
const error = ref(null)

const filters = ref({
  category: '',
  pinned: '',
  unread: '',
  search: ''
})

const pinnedAnnouncements = computed(() => {
  return announcements.value.filter(a => a.is_pinned)
})

const regularAnnouncements = computed(() => {
  return announcements.value.filter(a => !a.is_pinned)
})

const loadAnnouncements = async () => {
  loading.value = true
  error.value = null
  try {
    const params = {}
    if (filters.value.category) params.category = filters.value.category
    if (filters.value.pinned === 'true') params.pinned = true
    if (filters.value.unread === 'true') params.unread = true
    if (filters.value.search) params.search = filters.value.search

    const response = await announcementsAPI.listAnnouncements(params)
    // Handle both paginated (results) and non-paginated responses
    if (response.data && Array.isArray(response.data)) {
      announcements.value = response.data
    } else if (response.data && response.data.results && Array.isArray(response.data.results)) {
      announcements.value = response.data.results
    } else {
      announcements.value = []
    }
  } catch (e) {
    error.value = 'Failed to load announcements: ' + (e.response?.data?.detail || e.message)
    console.error('Error loading announcements:', e)
  } finally {
    loading.value = false
  }
}

const loadUnreadCount = async () => {
  try {
    const response = await announcementsAPI.getUnreadCount()
    unreadCount.value = response.data.unread_count || 0
  } catch (e) {
    console.error('Error loading unread count:', e)
  }
}

const trackView = async (announcement) => {
  try {
    await announcementsAPI.trackView(announcement.id)
    // Update local state
    const index = announcements.value.findIndex(a => a.id === announcement.id)
    if (index !== -1) {
      announcements.value[index].is_read = true
    }
    await loadUnreadCount()
  } catch (e) {
    console.error('Error tracking view:', e)
  }
}

const handleAcknowledge = async (announcement) => {
  try {
    await announcementsAPI.acknowledge(announcement.id)
    // Update local state
    const index = announcements.value.findIndex(a => a.id === announcement.id)
    if (index !== -1) {
      announcements.value[index].is_acknowledged = true
    }
  } catch (e) {
    error.value = 'Failed to acknowledge announcement: ' + (e.response?.data?.detail || e.message)
  }
}

onMounted(async () => {
  await Promise.all([loadAnnouncements(), loadUnreadCount()])
})
</script>


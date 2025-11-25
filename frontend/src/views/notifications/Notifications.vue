<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <h1 class="text-3xl font-bold text-gray-900">Notifications</h1>
      <div class="flex items-center gap-4">
        <div class="text-sm text-gray-600">
          <span class="font-medium">{{ unreadCount }}</span> unread
        </div>
        <button
          @click="markAllAsRead"
          :disabled="markingAll || unreadCount === 0"
          class="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50 text-sm"
        >
          {{ markingAll ? 'Marking...' : 'Mark All Read' }}
        </button>
      </div>
    </div>

    <div v-if="message" class="p-3 rounded" :class="messageSuccess ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'">
      {{ message }}
    </div>
    <div v-if="error" class="p-3 rounded bg-red-50 text-red-700">{{ error }}</div>

    <!-- Filters -->
    <div class="card p-4">
      <form @submit.prevent="loadNotifications" class="grid grid-cols-1 md:grid-cols-4 gap-3">
        <select v-model="filters.is_read" class="border rounded px-3 py-2">
          <option value="">All Status</option>
          <option value="false">Unread</option>
          <option value="true">Read</option>
        </select>
        <select v-model="filters.category" class="border rounded px-3 py-2">
          <option value="">All Categories</option>
          <option value="order">Order</option>
          <option value="payment">Payment</option>
          <option value="ticket">Ticket</option>
          <option value="system">System</option>
        </select>
        <input v-model="filters.search" type="text" placeholder="Search..." class="border rounded px-3 py-2" />
        <button class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">Filter</button>
      </form>
    </div>

    <!-- Notifications List -->
    <div class="card p-6">
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>

      <div v-else-if="!notifications.length" class="text-center py-12">
        <p class="text-gray-500">No notifications found.</p>
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="notif in notifications"
          :key="notif.id"
          :class="[
            'p-4 border rounded-lg cursor-pointer transition-colors',
            notif.is_read ? 'bg-white border-gray-200' : 'bg-blue-50 border-blue-200'
          ]"
          @click="viewNotification(notif)"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-2 mb-2">
                <span v-if="!notif.is_read" class="w-2 h-2 bg-blue-600 rounded-full"></span>
                <h3 class="font-semibold">{{ notif.title || notif.rendered_title || 'Notification' }}</h3>
                <span :class="getCategoryBadgeClass(notif.category)" class="px-2 py-0.5 rounded text-xs">
                  {{ notif.category || 'General' }}
                </span>
              </div>
              <p class="text-sm text-gray-600 mb-2">{{ notif.message || notif.rendered_message || notif.description }}</p>
              <div class="flex items-center gap-4 text-xs text-gray-500">
                <span>{{ formatDate(notif.created_at || notif.sent_at) }}</span>
                <span v-if="notif.priority" class="font-medium">{{ notif.priority_label || notif.priority }}</span>
              </div>
            </div>
            <div class="flex items-center gap-2 ml-4">
              <button
                v-if="!notif.is_read"
                @click.stop="markAsRead(notif.id)"
                class="text-primary-600 hover:text-primary-700 text-sm"
              >
                Mark Read
              </button>
              <a v-if="notif.link || notif.rendered_link" :href="notif.link || notif.rendered_link" class="text-primary-600 hover:text-primary-700 text-sm">
                View →
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import notificationsAPI from '@/api/notifications'

const loading = ref(true)
const notifications = ref([])
const unreadCount = ref(0)
const markingAll = ref(false)
const filters = ref({
  is_read: '',
  category: '',
  search: '',
})
const error = ref('')
const message = ref('')
const messageSuccess = ref(false)

const loadNotifications = async () => {
  loading.value = true
  try {
    const params = {}
    if (filters.value.is_read) params.is_read = filters.value.is_read === 'true'
    if (filters.value.category) params.category = filters.value.category
    if (filters.value.search) params.search = filters.value.search
    const res = await notificationsAPI.getNotifications(params)
    notifications.value = Array.isArray(res.data?.results) ? res.data.results : (res.data || [])
  } catch (e) {
    console.error('Failed to load notifications:', e)
    error.value = 'Failed to load notifications'
  } finally {
    loading.value = false
  }
}

const loadUnreadCount = async () => {
  try {
    const res = await notificationsAPI.getUnreadCount()
    unreadCount.value = res.data?.unread_count || 0
  } catch (e) {
    // Handle 429 (rate limiting) gracefully - don't log as error
    if (e.response?.status === 429) {
      // Silently handle rate limiting
      return
    }
    // Only log non-rate-limit errors
    if (e.response?.status !== 429) {
      console.error('Failed to load unread count:', e)
    }
  }
}

const markAsRead = async (id) => {
  try {
    await notificationsAPI.markAsRead(id)
    const notif = notifications.value.find(n => n.id === id)
    if (notif) notif.is_read = true
    await loadUnreadCount()
  } catch (e) {
    error.value = 'Failed to mark notification as read'
  }
}

const markAllAsRead = async () => {
  markingAll.value = true
  try {
    await notificationsAPI.markAllAsRead()
    notifications.value.forEach(n => { n.is_read = true })
    await loadUnreadCount()
    message.value = 'All notifications marked as read'
    messageSuccess.value = true
  } catch (e) {
    error.value = 'Failed to mark all as read'
  } finally {
    markingAll.value = false
  }
}

const viewNotification = (notif) => {
  if (!notif.is_read) {
    markAsRead(notif.id)
  }
  if (notif.link || notif.rendered_link) {
    window.open(notif.link || notif.rendered_link, '_blank')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '—'
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const getCategoryBadgeClass = (category) => {
  if (category === 'order') return 'bg-blue-100 text-blue-700'
  if (category === 'payment') return 'bg-green-100 text-green-700'
  if (category === 'ticket') return 'bg-yellow-100 text-yellow-700'
  if (category === 'system') return 'bg-gray-100 text-gray-700'
  return 'bg-gray-100 text-gray-700'
}

onMounted(async () => {
  await Promise.all([loadNotifications(), loadUnreadCount()])
})
</script>


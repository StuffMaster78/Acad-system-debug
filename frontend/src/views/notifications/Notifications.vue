<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Header -->
      <div class="mb-8">
        <div class="flex items-center justify-between mb-4">
          <div>
            <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">Notifications</h1>
            <p class="text-gray-600 dark:text-gray-400">Stay updated with your latest activities</p>
          </div>
          <div class="flex items-center gap-4">
            <div class="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
              <div class="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
              <span class="text-sm font-semibold text-gray-700 dark:text-gray-300">{{ unreadCount }}</span>
              <span class="text-sm text-gray-500 dark:text-gray-400">unread</span>
            </div>
            <button
              @click="markAllAsRead"
              :disabled="markingAll || unreadCount === 0"
              class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm hover:shadow-md flex items-center gap-2"
            >
              <svg v-if="!markingAll" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <div v-else class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              {{ markingAll ? 'Marking...' : 'Mark All Read' }}
            </button>
          </div>
        </div>

        <!-- Alert Messages -->
        <transition name="slide-down">
          <div v-if="message" class="mb-4 p-4 rounded-lg shadow-sm" :class="messageSuccess ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-yellow-50 text-yellow-700 border border-yellow-200'">
            <div class="flex items-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ message }}
            </div>
          </div>
        </transition>
        <transition name="slide-down">
          <div v-if="error" class="mb-4 p-4 rounded-lg bg-red-50 text-red-700 border border-red-200 shadow-sm">
            <div class="flex items-center gap-2">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ error }}
            </div>
          </div>
        </transition>
      </div>

      <!-- Filters -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 mb-6">
        <form @submit.prevent="loadNotifications" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <!-- Status Filter -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Status</label>
              <select 
                v-model="filters.is_read" 
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
              >
                <option value="">All Status</option>
                <option value="false">Unread</option>
                <option value="true">Read</option>
              </select>
            </div>
            
            <!-- Category Filter -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Category</label>
              <select 
                v-model="filters.category" 
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
              >
                <option value="">All Categories</option>
                <option value="order">Order</option>
                <option value="payment">Payment</option>
                <option value="ticket">Ticket</option>
                <option value="system">System</option>
                <option value="message">Message</option>
                <option value="file">File</option>
              </select>
            </div>
            
            <!-- Priority Filter -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Priority</label>
              <select 
                v-model="filters.priority" 
                class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
              >
                <option value="">All Priorities</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>
            
            <!-- Search -->
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Search</label>
              <div class="relative">
                <input 
                  v-model="filters.search" 
                  type="text" 
                  placeholder="Search notifications..." 
                  class="w-full border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 pl-10 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                />
                <svg class="absolute left-3 top-2.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>
          </div>
          
          <div class="flex items-center justify-between pt-2">
            <button 
              type="submit"
              class="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-all shadow-sm hover:shadow-md flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              Apply Filters
            </button>
            <button 
              type="button"
              @click="clearFilters"
              class="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 transition-colors"
            >
              Clear
            </button>
          </div>
        </form>
      </div>

      <!-- Notifications List -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div v-if="loading" class="flex items-center justify-center py-16">
          <div class="flex flex-col items-center gap-4">
            <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-200 border-t-primary-600"></div>
            <p class="text-gray-500 dark:text-gray-400">Loading notifications...</p>
          </div>
        </div>

        <div v-else-if="!notifications.length" class="text-center py-16">
          <div class="max-w-md mx-auto">
            <svg class="w-24 h-24 mx-auto text-gray-300 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">No notifications found</h3>
            <p class="text-gray-500 dark:text-gray-400">Try adjusting your filters or check back later.</p>
          </div>
        </div>

        <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
          <transition-group name="notification-list" tag="div">
            <NotificationItem
              v-for="notif in notifications"
              :key="notif.id"
              :notification="notif"
              @read="handleRead"
              @click="viewNotification"
            />
          </transition-group>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import notificationsAPI from '@/api/notifications'
import NotificationItem from '@/components/notifications/NotificationItem.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const route = useRoute()

const loading = ref(true)
const notifications = ref([])
const unreadCount = ref(0)
const markingAll = ref(false)
const filters = ref({
  is_read: '',
  category: '',
  search: '',
  priority: '',
})
const error = ref('')
const message = ref('')
const messageSuccess = ref(false)

const loadNotifications = async () => {
  loading.value = true
  error.value = ''
  try {
    const params = {}
    if (filters.value.is_read) params.is_read = filters.value.is_read === 'true'
    if (filters.value.category) params.category = filters.value.category
    if (filters.value.priority) params.priority_label = filters.value.priority
    if (filters.value.search) {
      // Search in title and message
      params.search = filters.value.search
    }
    
    const res = await notificationsAPI.getNotifications(params)
    
    // Handle both paginated and non-paginated responses
    if (Array.isArray(res.data?.results)) {
      notifications.value = res.data.results
    } else if (Array.isArray(res.data)) {
      notifications.value = res.data
    } else {
      notifications.value = []
    }
    
    // Sort by created_at descending (newest first)
    notifications.value.sort((a, b) => {
      const dateA = new Date(a.created_at || a.sent_at || 0)
      const dateB = new Date(b.created_at || b.sent_at || 0)
      return dateB - dateA
    })
  } catch (e) {
    console.error('Failed to load notifications:', e)
    error.value = 'Failed to load notifications. Please try again.'
  } finally {
    loading.value = false
  }
}

const clearFilters = () => {
  filters.value = {
    is_read: '',
    category: '',
    search: '',
    priority: '',
  }
  loadNotifications()
}

const handleRead = (notificationId) => {
  const notif = notifications.value.find(n => n.id === notificationId)
  if (notif) {
    notif.is_read = true
    loadUnreadCount()
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

const markAllAsRead = async () => {
  markingAll.value = true
  message.value = ''
  error.value = ''
  try {
    await notificationsAPI.markAllAsRead()
    notifications.value.forEach(n => { n.is_read = true })
    await loadUnreadCount()
    message.value = 'All notifications marked as read'
    messageSuccess.value = true
    setTimeout(() => {
      message.value = ''
      messageSuccess.value = false
    }, 3000)
  } catch (e) {
    console.error('Failed to mark all as read:', e)
    error.value = 'Failed to mark all notifications as read'
  } finally {
    markingAll.value = false
  }
}

const viewNotification = (notif) => {
  if (notif.link || notif.rendered_link) {
    const link = notif.link || notif.rendered_link
    // Check if it's an internal route
    if (link.startsWith('/')) {
      window.location.href = link
    } else {
      window.open(link, '_blank')
    }
  }
}

// Watch for route changes to reload notifications
watch(() => route.query, () => {
  loadNotifications()
}, { deep: true })

onMounted(async () => {
  await Promise.all([loadNotifications(), loadUnreadCount()])
  
  // Auto-refresh unread count every 30 seconds
  setInterval(() => {
    loadUnreadCount()
  }, 30000)
})
</script>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

.notification-list-enter-active {
  transition: all 0.3s ease;
}

.notification-list-leave-active {
  transition: all 0.3s ease;
}

.notification-list-enter-from {
  opacity: 0;
  transform: translateX(-20px);
}

.notification-list-leave-to {
  opacity: 0;
  transform: translateX(20px);
}

.notification-list-move {
  transition: transform 0.3s ease;
}
</style>


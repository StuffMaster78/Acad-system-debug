<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Client Header -->
    <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <div class="flex items-center">
            <router-link to="/client" class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                <span class="text-white font-bold text-lg">WS</span>
              </div>
              <span class="text-xl font-bold text-gray-900 dark:text-white">Writing System</span>
            </router-link>
          </div>

          <!-- Navigation -->
          <nav class="hidden md:flex items-center space-x-1">
            <router-link
              to="/client"
              class="px-4 py-2 text-sm font-medium rounded-lg transition-colors"
              :class="$route.path === '/client' ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
            >
              Dashboard
            </router-link>
            <router-link
              to="/client/orders"
              class="px-4 py-2 text-sm font-medium rounded-lg transition-colors"
              :class="$route.path.startsWith('/client/orders') ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
            >
              My Orders
            </router-link>
            <router-link
              to="/client/orders/create"
              class="px-4 py-2 text-sm font-medium rounded-lg transition-colors"
              :class="$route.path === '/client/orders/create' ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
            >
              Place Order
            </router-link>
            <router-link
              to="/client/payments"
              class="px-4 py-2 text-sm font-medium rounded-lg transition-colors"
              :class="$route.path.startsWith('/client/payments') ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
            >
              Payments
            </router-link>
            <router-link
              to="/client/messages"
              class="px-4 py-2 text-sm font-medium rounded-lg transition-colors"
              :class="$route.path.startsWith('/client/messages') ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
            >
              Messages
            </router-link>
            <router-link
              to="/client/profile"
              class="px-4 py-2 text-sm font-medium rounded-lg transition-colors"
              :class="$route.path.startsWith('/client/profile') ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'"
            >
              Profile
            </router-link>
          </nav>

          <!-- User Menu -->
          <div class="flex items-center space-x-4">
            <!-- Wallet Balance -->
            <div v-if="walletBalance !== null" class="hidden md:flex items-center space-x-2 px-3 py-1.5 bg-primary-50 dark:bg-primary-900/30 rounded-lg">
              <svg class="w-5 h-5 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span class="text-sm font-semibold text-primary-700 dark:text-primary-300">${{ walletBalance.toFixed(2) }}</span>
            </div>

            <!-- Notifications -->
            <button
              @click="showNotifications = !showNotifications"
              class="relative p-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <span
                v-if="unreadCount > 0"
                class="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-500 ring-2 ring-white dark:ring-gray-800"
              ></span>
            </button>

            <!-- User Dropdown -->
            <div class="relative">
              <button
                @click="showUserMenu = !showUserMenu"
                class="flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              >
                <div class="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                  <span class="text-white text-sm font-semibold">
                    {{ userInitials }}
                  </span>
                </div>
                <span class="hidden md:block text-sm font-medium text-gray-700 dark:text-gray-300">
                  {{ authStore.user?.full_name || authStore.user?.email || 'Client' }}
                </span>
                <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <!-- Dropdown Menu -->
              <div
                v-if="showUserMenu"
                v-click-outside="() => showUserMenu = false"
                class="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-50"
              >
                <router-link
                  to="/client/profile"
                  class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  @click="showUserMenu = false"
                >
                  Profile Settings
                </router-link>
                <router-link
                  to="/client/loyalty"
                  class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  @click="showUserMenu = false"
                >
                  Loyalty & Rewards
                </router-link>
                <router-link
                  to="/client/referrals"
                  class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                  @click="showUserMenu = false"
                >
                  Referrals
                </router-link>
                <hr class="my-1 border-gray-200 dark:border-gray-700" />
                <button
                  @click="handleLogout"
                  class="block w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Mobile Menu -->
    <div class="md:hidden bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <nav class="px-4 py-2 space-y-1">
        <router-link
          to="/client"
          class="block px-3 py-2 text-sm font-medium rounded-lg"
          :class="$route.path === '/client' ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'text-gray-700 dark:text-gray-300'"
        >
          Dashboard
        </router-link>
        <router-link
          to="/client/orders"
          class="block px-3 py-2 text-sm font-medium rounded-lg"
          :class="$route.path.startsWith('/client/orders') ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'text-gray-700 dark:text-gray-300'"
        >
          My Orders
        </router-link>
        <router-link
          to="/client/orders/create"
          class="block px-3 py-2 text-sm font-medium rounded-lg"
          :class="$route.path === '/client/orders/create' ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'text-gray-700 dark:text-gray-300'"
        >
          Place Order
        </router-link>
        <router-link
          to="/client/payments"
          class="block px-3 py-2 text-sm font-medium rounded-lg"
          :class="$route.path.startsWith('/client/payments') ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'text-gray-700 dark:text-gray-300'"
        >
          Payments
        </router-link>
        <router-link
          to="/client/messages"
          class="block px-3 py-2 text-sm font-medium rounded-lg"
          :class="$route.path.startsWith('/client/messages') ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'text-gray-700 dark:text-gray-300'"
        >
          Messages
        </router-link>
      </nav>
    </div>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <router-view />
    </main>

    <!-- Notifications Panel -->
    <div
      v-if="showNotifications"
      v-click-outside="() => showNotifications = false"
      class="fixed right-4 top-20 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 z-50 max-h-96 overflow-y-auto"
    >
      <div class="p-4 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Notifications</h3>
          <button
            @click="showNotifications = false"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
      <div class="p-4">
        <div v-if="notificationsLoading" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        </div>
        <div v-else-if="notifications.length === 0" class="text-center py-8 text-gray-500">
          No notifications
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="notification in notifications"
            :key="notification.id"
            class="p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors"
          >
            <p class="text-sm text-gray-900 dark:text-white">{{ notification.message || notification.title }}</p>
            <p class="text-xs text-gray-500 mt-1">{{ formatDate(notification.created_at) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import walletAPI from '@/api/wallet'
import notificationsAPI from '@/api/notifications'

const router = useRouter()
const authStore = useAuthStore()

const showUserMenu = ref(false)
const showNotifications = ref(false)
const walletBalance = ref(null)
const notifications = ref([])
const notificationsLoading = ref(false)
const unreadCount = ref(0)

const userInitials = computed(() => {
  const user = authStore.user
  if (user?.full_name) {
    const names = user.full_name.split(' ')
    if (names.length >= 2) {
      return `${names[0][0]}${names[1][0]}`.toUpperCase()
    }
    return names[0][0].toUpperCase()
  }
  if (user?.email) {
    return user.email[0].toUpperCase()
  }
  return 'C'
})

const fetchWalletBalance = async () => {
  try {
    const response = await walletAPI.getBalance()
    walletBalance.value = response.data.balance || response.data.wallet?.balance || 0
  } catch (err) {
    console.error('Failed to fetch wallet balance:', err)
    walletBalance.value = 0
  }
}

const fetchNotifications = async () => {
  notificationsLoading.value = true
  try {
    const response = await notificationsAPI.getNotifications({ page_size: 10, ordering: '-created_at' })
    const notifs = Array.isArray(response.data?.results)
      ? response.data.results
      : (Array.isArray(response.data) ? response.data : [])
    notifications.value = notifs
    unreadCount.value = notifs.filter(n => !n.read).length
  } catch (err) {
    console.error('Failed to fetch notifications:', err)
    notifications.value = []
  } finally {
    notificationsLoading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days < 7) return `${days}d ago`
  return date.toLocaleDateString()
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    router.push('/login')
  } catch (err) {
    console.error('Logout failed:', err)
  }
}

// Click outside directive
const vClickOutside = {
  mounted(el, binding) {
    el.clickOutsideEvent = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value()
      }
    }
    document.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el) {
    document.removeEventListener('click', el.clickOutsideEvent)
  }
}

onMounted(() => {
  fetchWalletBalance()
  fetchNotifications()
  // Refresh notifications every 30 seconds
  setInterval(fetchNotifications, 30000)
})
</script>

<style scoped>
/* Custom scrollbar for notifications */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>


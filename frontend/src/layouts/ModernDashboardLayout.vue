<template>
  <div class="min-h-screen bg-gray-50 dark:bg-slate-950 transition-colors duration-300">
    <!-- Modern Sidebar -->
    <ModernSidebar
      :sidebar-open="sidebarOpen"
      :badge-counts="badgeCounts"
      @close="sidebarOpen = false"
    />

    <!-- Main Content Area -->
    <div
      :class="[
        'transition-all duration-300 ease-out',
        sidebarCollapsed ? 'lg:ml-20' : 'lg:ml-72'
      ]"
    >
      <!-- Top Header Bar -->
      <header class="sticky top-0 z-30 glass-strong border-b border-gray-200/50 dark:border-slate-700/50">
        <div class="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
          <!-- Left: Mobile Menu + Breadcrumbs -->
          <div class="flex items-center gap-4 flex-1 min-w-0">
            <!-- Mobile Menu Button -->
            <button
              @click="sidebarOpen = true"
              class="lg:hidden p-2 rounded-xl text-gray-600 dark:text-slate-400 hover:bg-gray-100 dark:hover:bg-slate-800 transition-all group"
              aria-label="Open menu"
            >
              <svg class="w-6 h-6 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>

            <!-- Breadcrumbs -->
            <nav class="flex items-center gap-2 text-sm overflow-x-auto" aria-label="Breadcrumb">
              <router-link
                to="/dashboard"
                class="text-gray-500 dark:text-slate-400 hover:text-gray-900 dark:hover:text-slate-100 transition-colors whitespace-nowrap"
              >
                Dashboard
              </router-link>
              <svg v-if="breadcrumbs.length > 0" class="w-4 h-4 text-gray-300 dark:text-slate-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
              <template v-for="(crumb, index) in breadcrumbs">
                <router-link
                  v-if="crumb.to && index < breadcrumbs.length - 1"
                  :key="`crumb-link-${index}`"
                  :to="crumb.to"
                  class="text-gray-500 dark:text-slate-400 hover:text-gray-900 dark:hover:text-slate-100 transition-colors whitespace-nowrap"
                >
                  {{ crumb.label }}
                </router-link>
                <span
                  v-else
                  :key="`crumb-text-${index}`"
                  class="text-gray-900 dark:text-slate-100 font-medium whitespace-nowrap"
                >
                  {{ crumb.label }}
                </span>
                <svg v-if="index < breadcrumbs.length - 1" :key="`crumb-arrow-${index}`" class="w-4 h-4 text-gray-300 dark:text-slate-600 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </template>
            </nav>
          </div>

          <!-- Right: Actions -->
          <div class="flex items-center gap-2 sm:gap-3 shrink-0">
            <!-- Global Search -->
            <button
              @click="showGlobalSearch = true"
              class="hidden sm:flex items-center gap-2 px-3 py-2 text-sm text-gray-600 dark:text-slate-400 bg-gray-100 dark:bg-slate-800 rounded-lg hover:bg-gray-200 dark:hover:bg-slate-700 transition-all group"
              title="Search (⌘K)"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <span class="hidden md:inline text-xs opacity-60">⌘K</span>
            </button>

            <!-- Notifications -->
            <button
              @click="showNotifications = !showNotifications"
              class="relative p-2 rounded-xl text-gray-600 dark:text-slate-400 hover:bg-gray-100 dark:hover:bg-slate-800 transition-all group"
              title="Notifications"
            >
              <svg class="w-6 h-6 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <span
                v-if="unreadCount > 0"
                class="absolute -top-1 -right-1 w-5 h-5 bg-error-500 text-white text-xs font-bold rounded-full flex items-center justify-center ring-2 ring-white dark:ring-slate-900 animate-pulse"
              >
                {{ unreadCount > 9 ? '9+' : unreadCount }}
              </span>
            </button>

            <!-- Messages -->
            <router-link
              to="/messages"
              class="relative p-2 rounded-xl text-gray-600 dark:text-slate-400 hover:bg-gray-100 dark:hover:bg-slate-800 transition-all group"
              title="Messages"
            >
              <svg class="w-6 h-6 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <span
                v-if="unreadMessages > 0"
                class="absolute -top-1 -right-1 w-5 h-5 bg-info-500 text-white text-xs font-bold rounded-full flex items-center justify-center ring-2 ring-white dark:ring-slate-900"
              >
                {{ unreadMessages > 9 ? '9+' : unreadMessages }}
              </span>
            </router-link>

            <!-- Profile Dropdown -->
            <div class="relative">
              <button
                @click="showProfileMenu = !showProfileMenu"
                class="flex items-center gap-2 p-1.5 rounded-xl hover:bg-gray-100 dark:hover:bg-slate-800 transition-all group"
                :aria-expanded="showProfileMenu"
              >
                <div class="w-9 h-9 rounded-lg bg-linear-to-br from-primary-600 to-primary-700 flex items-center justify-center text-white font-semibold shadow-md group-hover:shadow-lg transition-shadow">
                  {{ userInitials }}
                </div>
                <svg class="hidden sm:block w-4 h-4 text-gray-400 transition-transform" :class="showProfileMenu ? 'rotate-180' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <!-- Profile Dropdown Menu -->
              <Transition
                enter-active-class="transition-all duration-200 ease-out"
                enter-from-class="opacity-0 scale-95 -translate-y-2"
                enter-to-class="opacity-100 scale-100 translate-y-0"
                leave-active-class="transition-all duration-150 ease-in"
                leave-from-class="opacity-100 scale-100 translate-y-0"
                leave-to-class="opacity-0 scale-95 -translate-y-2"
              >
                <div
                  v-if="showProfileMenu"
                  class="absolute right-0 top-full mt-2 w-64 glass-strong border border-gray-200/50 dark:border-slate-700/50 rounded-xl shadow-2xl overflow-hidden"
                >
                  <div class="p-4 border-b border-gray-200/50 dark:border-slate-700/50">
                    <div class="text-sm font-semibold text-gray-900 dark:text-slate-100">
                      {{ userName }}
                    </div>
                    <div class="text-xs text-gray-500 dark:text-slate-400 mt-0.5">
                      {{ userEmail }}
                    </div>
                    <div class="mt-2">
                      <span :class="['inline-flex items-center px-2 py-1 text-xs font-medium rounded-full', getRoleBadgeClasses()]">
                        {{ userRole }}
                      </span>
                    </div>
                  </div>
                  <div class="p-2">
                    <router-link
                      to="/profile"
                      @click="showProfileMenu = false"
                      class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-800 transition-all group"
                    >
                      <svg class="w-5 h-5 text-gray-500 dark:text-slate-400 group-hover:text-gray-700 dark:group-hover:text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      <span class="text-sm text-gray-700 dark:text-slate-300">Profile</span>
                    </router-link>
                    <router-link
                      to="/settings"
                      @click="showProfileMenu = false"
                      class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-50 dark:hover:bg-slate-800 transition-all group"
                    >
                      <svg class="w-5 h-5 text-gray-500 dark:text-slate-400 group-hover:text-gray-700 dark:group-hover:text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      <span class="text-sm text-gray-700 dark:text-slate-300">Settings</span>
                    </router-link>
                    <button
                      @click="handleLogout"
                      class="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-error-50 dark:hover:bg-error-900/20 transition-all group text-left"
                    >
                      <svg class="w-5 h-5 text-gray-500 dark:text-slate-400 group-hover:text-error-600 dark:group-hover:text-error-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                      </svg>
                      <span class="text-sm text-gray-700 dark:text-slate-300 group-hover:text-error-600 dark:group-hover:text-error-400">
                        Sign Out
                      </span>
                    </button>
                  </div>
                </div>
              </Transition>
            </div>
          </div>
        </div>
      </header>

      <!-- Main Content -->
      <main class="p-4 sm:p-6 lg:p-8">
        <router-view v-slot="{ Component }">
          <Transition
            mode="out-in"
            enter-active-class="transition-all duration-200 ease-out"
            enter-from-class="opacity-0 translate-y-4"
            enter-to-class="opacity-100 translate-y-0"
            leave-active-class="transition-all duration-150 ease-in"
            leave-from-class="opacity-100 translate-y-0"
            leave-to-class="opacity-0 translate-y-4"
          >
            <component :is="Component" />
          </Transition>
        </router-view>
      </main>
    </div>

    <!-- Global Search Modal (⌘K) -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-all duration-200 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-all duration-150 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="showGlobalSearch"
          class="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4 bg-black/50 backdrop-blur-sm"
          @click="showGlobalSearch = false"
        >
          <div
            @click.stop
            class="w-full max-w-2xl glass-strong border border-gray-200/50 dark:border-slate-700/50 rounded-2xl shadow-2xl overflow-hidden"
          >
            <div class="p-4 border-b border-gray-200/50 dark:border-slate-700/50">
              <input
                v-model="globalSearchQuery"
                type="text"
                placeholder="Search everything..."
                class="w-full px-4 py-3 text-lg bg-transparent border-0 focus:outline-none text-gray-900 dark:text-slate-100 placeholder-gray-400 dark:placeholder-slate-500"
                autofocus
              />
            </div>
            <div class="p-2 max-h-96 overflow-y-auto">
              <div class="text-sm text-gray-500 dark:text-slate-400 px-4 py-2">
                Global search coming soon...
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Notifications Dropdown -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-all duration-200 ease-out"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition-all duration-150 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div
          v-if="showNotifications"
          v-click-outside="() => showNotifications = false"
          class="fixed top-20 right-4 w-96 max-w-[calc(100vw-2rem)] glass-strong border border-gray-200/50 dark:border-slate-700/50 rounded-2xl shadow-2xl overflow-hidden z-50"
        >
          <div class="p-4 border-b border-gray-200/50 dark:border-slate-700/50">
            <div class="flex items-center justify-between">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-slate-100">
                Notifications
              </h3>
              <button
                @click="showNotifications = false"
                class="p-1 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-800 transition-all"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
          <div class="p-4 max-h-96 overflow-y-auto">
            <div class="text-sm text-gray-500 dark:text-slate-400 text-center py-8">
              No new notifications
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Toast Container -->
    <ToastContainer />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ModernSidebar from '@/components/layout/ModernSidebar.vue'
import ToastContainer from '@/components/common/ToastContainer.vue'
import notificationsAPI from '@/api/notifications'
import messagesAPI from '@/api/messages'
import ordersAPI from '@/api/orders'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// State
const sidebarOpen = ref(false)
const sidebarCollapsed = ref(false)
const showGlobalSearch = ref(false)
const showNotifications = ref(false)
const showProfileMenu = ref(false)
const globalSearchQuery = ref('')
const unreadCount = ref(0)
const unreadMessages = ref(0)

// Badge Counts for Sidebar
const badgeCounts = computed(() => ({
  orders: 0, // Will be fetched from API
  messages: unreadMessages.value,
  notifications: unreadCount.value,
}))

let badgeCountsInterval = null

// Computed
const userName = computed(() => {
  return authStore.user?.full_name || authStore.user?.username || 'User'
})

const userEmail = computed(() => {
  return authStore.user?.email || ''
})

const userInitials = computed(() => {
  const name = userName.value
  const parts = name.split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.substring(0, 2).toUpperCase()
})

const userRole = computed(() => {
  if (authStore.isSuperAdmin) return 'Super Admin'
  if (authStore.isAdmin) return 'Admin'
  if (authStore.isSupport) return 'Support'
  if (authStore.isWriter) return 'Writer'
  if (authStore.isEditor) return 'Editor'
  if (authStore.isClient) return 'Client'
  return 'User'
})

const breadcrumbs = computed(() => {
  // Generate breadcrumbs from route meta or path
  const crumbs = []
  const path = route.path
  
  // Simple breadcrumb logic - can be enhanced
  if (path !== '/dashboard') {
    const segments = path.split('/').filter(Boolean)
    segments.forEach((segment, index) => {
      crumbs.push({
        label: segment.split('-').map(word => 
          word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' '),
        to: index === segments.length - 1 ? null : '/' + segments.slice(0, index + 1).join('/')
      })
    })
  }
  
  return crumbs
})

// Methods
function getRoleBadgeClasses() {
  const roleColors = {
    'Super Admin': 'bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300',
    'Admin': 'bg-primary-100 dark:bg-primary-900/40 text-primary-700 dark:text-primary-300',
    'Support': 'bg-orange-100 dark:bg-orange-900/40 text-orange-700 dark:text-orange-300',
    'Writer': 'bg-teal-100 dark:bg-teal-900/40 text-teal-700 dark:text-teal-300',
    'Editor': 'bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300',
    'Client': 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300',
  }
  return roleColors[userRole.value] || 'bg-gray-100 dark:bg-gray-900/40 text-gray-700 dark:text-gray-300'
}

async function handleLogout() {
  showProfileMenu.value = false
  await authStore.logout()
  router.push('/login')
}

// Keyboard shortcuts
function handleKeydown(e) {
  // ⌘K for global search
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    showGlobalSearch.value = true
  }
  
  // Escape to close overlays
  if (e.key === 'Escape') {
    showGlobalSearch.value = false
    showNotifications.value = false
    showProfileMenu.value = false
  }
}

// Click outside directive
const vClickOutside = {
  mounted(el, binding) {
    el._clickOutside = (event) => {
      if (!el.contains(event.target)) {
        binding.value()
      }
    }
    document.addEventListener('click', el._clickOutside)
  },
  unmounted(el) {
    document.removeEventListener('click', el._clickOutside)
  },
}

// Badge count fetching
const fetchBadgeCounts = async () => {
  if (!authStore.isAuthenticated) return

  try {
    // Fetch unread notifications
    const notifResponse = await notificationsAPI.getUnreadCount()
    unreadCount.value = notifResponse.data.unread_count || notifResponse.data.count || 0
  } catch (error) {
    if (error.response?.status !== 429 && error.response?.status !== 401) {
      console.error('Failed to fetch notifications count:', error)
    }
  }

  try {
    // Fetch unread messages
    const messagesResponse = await messagesAPI.getUnreadCount()
    unreadMessages.value = messagesResponse.data.unread_count || 0
  } catch (error) {
    if (error.response?.status !== 429 && error.response?.status !== 401) {
      console.error('Failed to fetch messages count:', error)
    }
  }
}

// Lifecycle
onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
  
  // Check saved collapsed state
  const savedCollapsed = localStorage.getItem('sidebarCollapsed')
  if (savedCollapsed !== null) {
    sidebarCollapsed.value = savedCollapsed === 'true'
  }

  // Fetch initial badge counts
  fetchBadgeCounts()

  // Poll for updates every 60 seconds
  badgeCountsInterval = setInterval(fetchBadgeCounts, 60000)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  
  // Clean up interval
  if (badgeCountsInterval) {
    clearInterval(badgeCountsInterval)
  }
})

// Watch collapsed state and save to localStorage
watch(() => sidebarCollapsed.value, (newVal) => {
  localStorage.setItem('sidebarCollapsed', newVal.toString())
})
</script>

<style scoped>
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgb(203 213 225) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgb(203 213 225);
  border-radius: 3px;
}

.dark .custom-scrollbar {
  scrollbar-color: rgb(51 65 85) transparent;
}

.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgb(51 65 85);
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>

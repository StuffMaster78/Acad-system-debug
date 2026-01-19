<template>
  <div class="messages-page min-h-dvh bg-gray-50 dark:bg-gray-900">
    <div class="max-w-7xl mx-auto page-shell">
      <!-- Breadcrumbs -->
      <nav class="mb-6 flex items-center gap-2 text-xs sm:text-sm overflow-x-auto whitespace-nowrap" aria-label="Breadcrumb">
        <router-link to="/dashboard" class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
          Dashboard
        </router-link>
        <span class="text-gray-400 dark:text-gray-600">/</span>
        <span class="text-gray-900 dark:text-gray-100 font-medium truncate max-w-[60vw] sm:max-w-none">Messages</span>
      </nav>
      
      <!-- Header -->
      <div class="mb-6">
        <h1 class="page-title text-gray-900 dark:text-white mb-2">Messages</h1>
        <p class="text-gray-600 dark:text-gray-400">Communicate with team members and clients</p>
      </div>

      <!-- Recipient Type Tabs -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
        <div class="border-b border-gray-200 dark:border-gray-700">
          <nav class="flex overflow-x-auto" aria-label="Tabs">
            <button
              v-for="tab in recipientTabs"
              :key="tab.id"
              @click="activeTab = tab.id"
              :class="[
                'px-6 py-4 text-sm font-medium border-b-2 transition-colors whitespace-nowrap',
                activeTab === tab.id
                  ? 'border-blue-600 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              ]"
            >
              <span class="flex items-center gap-2">
                <component :is="tab.icon" class="w-5 h-5" />
                {{ tab.label }}
                <span class="ml-2 inline-flex items-center gap-1">
                  <span class="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 text-xs rounded-full">
                    {{ getThreadCountForTab(tab.id) }}
                  </span>
                  <span
                    v-if="getUnreadCountForTab(tab.id) > 0"
                    class="px-2 py-0.5 bg-red-500 text-white text-xs rounded-full"
                  >
                    {{ getUnreadCountForTab(tab.id) }}
                  </span>
                </span>
              </span>
            </button>
          </nav>
        </div>

        <!-- Search and New Message -->
        <div class="p-4 border-b border-gray-200 dark:border-gray-700 space-y-3">
          <!-- Search Input -->
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search conversations..."
              class="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white"
            />
          </div>
          
          <!-- New Message Button -->
          <button
            @click="openNewMessageModal"
            class="w-full px-4 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-lg font-semibold transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
            New Message
          </button>
        </div>
      </div>

      <!-- Threads List -->
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
        <div v-if="loadingThreads" class="p-12 text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p class="mt-4 text-gray-600 dark:text-gray-400">Loading conversations...</p>
        </div>

        <div v-else-if="filteredThreads.length === 0" class="p-12 text-center">
          <svg class="w-16 h-16 mx-auto mb-4 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <p class="text-lg font-medium text-gray-900 dark:text-white mb-2">No conversations yet</p>
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
            Start a new conversation by clicking "New Message" above
          </p>
          <button
            @click="openNewMessageModal"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Start Conversation
          </button>
        </div>

        <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
          <!-- Paginated Threads -->
          <div
            v-for="thread in paginatedThreads"
            :key="thread.id"
            @click="openThread(thread)"
            class="p-4 cursor-pointer transition-all border-l-4"
            :class="thread.unread_count > 0 
              ? 'bg-blue-50 dark:bg-blue-900/20 border-l-blue-500 hover:bg-blue-100 dark:hover:bg-blue-900/30' 
              : 'hover:bg-gray-50 dark:hover:bg-gray-700/50 border-l-transparent'"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-3 mb-2">
                  <div 
                    class="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold shrink-0"
                    :class="thread.unread_count > 0 
                      ? 'bg-gradient-to-br from-blue-500 to-blue-600 ring-2 ring-blue-300 dark:ring-blue-700' 
                      : 'bg-gradient-to-br from-gray-400 to-gray-600'"
                  >
                    {{ getThreadInitials(thread) }}
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2">
                      <h3 
                        class="font-semibold truncate"
                        :class="thread.unread_count > 0 
                          ? 'text-gray-900 dark:text-white font-bold' 
                          : 'text-gray-700 dark:text-gray-300'"
                      >
                        {{ getThreadTitle(thread) }}
                      </h3>
                      <span
                        v-if="thread.unread_count > 0"
                        class="px-2 py-0.5 bg-red-500 text-white text-xs rounded-full font-bold shrink-0"
                      >
                        {{ thread.unread_count }}
                      </span>
                    </div>
                    <p class="text-sm text-gray-500 dark:text-gray-400">
                      {{ getThreadSubtitle(thread) }}
                    </p>
                  </div>
                </div>
                <p 
                  v-if="thread.last_message" 
                  class="text-sm truncate ml-13"
                  :class="thread.unread_count > 0 
                    ? 'text-gray-700 dark:text-gray-200 font-medium' 
                    : 'text-gray-600 dark:text-gray-300'"
                >
                  {{ thread.last_message.message || '📎 File attachment' }}
                </p>
              </div>
              <div class="flex flex-col items-end gap-2 shrink-0">
                <span 
                  class="text-xs"
                  :class="thread.unread_count > 0 
                    ? 'text-gray-700 dark:text-gray-300 font-medium' 
                    : 'text-gray-500 dark:text-gray-400'"
                >
                  {{ formatTime(thread.last_message?.sent_at || thread.updated_at) }}
                </span>
              </div>
            </div>
          </div>
          
          <!-- Pagination -->
          <div v-if="totalPages > 1" class="p-4 border-t border-gray-200 dark:border-gray-700 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
            <div class="text-sm text-gray-600 dark:text-gray-400">
              Showing {{ (currentPage - 1) * threadsPerPage + 1 }} - {{ Math.min(currentPage * threadsPerPage, filteredThreads.length) }} of {{ filteredThreads.length }}
            </div>
            <div class="flex flex-wrap items-center gap-2">
              <button
                @click="currentPage = Math.max(1, currentPage - 1)"
                :disabled="currentPage === 1"
                class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <span class="text-sm text-gray-600 dark:text-gray-400">
                Page {{ currentPage }} of {{ totalPages }}
              </span>
              <button
                @click="currentPage = Math.min(totalPages, currentPage + 1)"
                :disabled="currentPage === totalPages"
                class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- New Message Modal -->
    <NewMessageModal
      v-if="showNewMessageModal"
      :show="showNewMessageModal"
      :default-recipient-type="activeTab"
      @close="showNewMessageModal = false"
      @message-sent="handleMessageSent"
    />

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, shallowRef } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { communicationsAPI } from '@/api'
import { useAuthStore } from '@/stores/auth'
import messagesStore from '@/stores/messages'
import NewMessageModal from '@/components/messages/NewMessageModal.vue'
import { useDebounceFn } from '@vueuse/core'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const currentUser = authStore.user

// Tabs configuration based on user role
const recipientTabs = computed(() => {
  const role = currentUser?.role
  const tabs = []

  if (role === 'client') {
    tabs.push(
      { id: 'admin', label: 'To Admin', icon: 'AdminIcon', roles: ['admin', 'superadmin'] },
      { id: 'support', label: 'To Support', icon: 'SupportIcon', roles: ['support'] },
      { id: 'writer', label: 'To Writer', icon: 'WriterIcon', roles: ['writer'] },
      { id: 'editor', label: 'To Editor', icon: 'EditorIcon', roles: ['editor'] }
    )
  } else if (role === 'writer') {
    tabs.push(
      { id: 'client', label: 'To Client', icon: 'ClientIcon', roles: ['client'] },
      { id: 'admin', label: 'To Admin', icon: 'AdminIcon', roles: ['admin', 'superadmin'] },
      { id: 'support', label: 'To Support', icon: 'SupportIcon', roles: ['support'] },
      { id: 'editor', label: 'To Editor', icon: 'EditorIcon', roles: ['editor'] }
    )
  } else if (role === 'admin' || role === 'superadmin') {
    tabs.push(
      { id: 'client', label: 'To Client', icon: 'ClientIcon', roles: ['client'] },
      { id: 'writer', label: 'To Writer', icon: 'WriterIcon', roles: ['writer'] },
      { id: 'editor', label: 'To Editor', icon: 'EditorIcon', roles: ['editor'] },
      { id: 'support', label: 'To Support', icon: 'SupportIcon', roles: ['support'] }
    )
  } else if (role === 'support') {
    tabs.push(
      { id: 'client', label: 'To Client', icon: 'ClientIcon', roles: ['client'] },
      { id: 'writer', label: 'To Writer', icon: 'WriterIcon', roles: ['writer'] },
      { id: 'admin', label: 'To Admin', icon: 'AdminIcon', roles: ['admin', 'superadmin'] },
      { id: 'editor', label: 'To Editor', icon: 'EditorIcon', roles: ['editor'] }
    )
  } else if (role === 'editor') {
    tabs.push(
      { id: 'client', label: 'To Client', icon: 'ClientIcon', roles: ['client'] },
      { id: 'writer', label: 'To Writer', icon: 'WriterIcon', roles: ['writer'] },
      { id: 'admin', label: 'To Admin', icon: 'AdminIcon', roles: ['admin', 'superadmin'] },
      { id: 'support', label: 'To Support', icon: 'SupportIcon', roles: ['support'] }
    )
  }

  return tabs
})

const activeTab = ref(recipientTabs.value[0]?.id || 'admin')
const threads = shallowRef([]) // Use shallowRef for better performance with large arrays
const loadingThreads = ref(false)
const showNewMessageModal = ref(false)
const searchQuery = ref('')
const threadsPerPage = 20
const currentPage = ref(1)

// Icon components (simple SVG components)
const AdminIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>' }
const ClientIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>' }
const WriterIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>' }
const EditorIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>' }
const SupportIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" /></svg>' }

// Memoized filtered threads with search and pagination
const filteredThreads = computed(() => {
  const activeTabData = recipientTabs.value.find(t => t.id === activeTab.value)
  if (!activeTabData) return []

  let filtered = threads.value.filter(thread => {
    // Get other participants (excluding current user)
    const otherParticipants = thread.participants?.filter(p => {
      const participantId = typeof p === 'object' ? p.id : p
      return participantId !== currentUser?.id
    }) || []

    if (otherParticipants.length === 0) return false

    // Check if any participant matches the active tab's roles
    const matchesTab = otherParticipants.some(participant => {
      let participantRole = null
      if (typeof participant === 'object') {
        participantRole = participant.role || null
      }
      return participantRole && activeTabData.roles.includes(participantRole)
    })

    if (!matchesTab) return false

    // Apply search filter if query exists
    if (searchQuery.value.trim()) {
      const query = searchQuery.value.toLowerCase()
      const threadTitle = getThreadTitle(thread).toLowerCase()
      const lastMessage = thread.last_message?.message?.toLowerCase() || ''
      const participantNames = otherParticipants
        .map(p => typeof p === 'object' ? (p.username || p.email || '').toLowerCase() : '')
        .join(' ')
      
      if (!threadTitle.includes(query) && 
          !lastMessage.includes(query) && 
          !participantNames.includes(query)) {
        return false
      }
    }

    return true
  })

  // Sort by last message time or updated time
  filtered = filtered.sort((a, b) => {
    const aTime = a.last_message?.sent_at || a.updated_at || a.created_at
    const bTime = b.last_message?.sent_at || b.updated_at || b.created_at
    return new Date(bTime) - new Date(aTime)
  })

  return filtered
})

// Paginated threads for display
const paginatedThreads = computed(() => {
  const start = (currentPage.value - 1) * threadsPerPage
  const end = start + threadsPerPage
  return filteredThreads.value.slice(start, end)
})

// Total pages
const totalPages = computed(() => {
  return Math.ceil(filteredThreads.value.length / threadsPerPage)
})

const openThreadFromOrder = () => {
  if (!route.query.order || threads.value.length === 0) return
  const orderId = parseInt(route.query.order, 10)
  if (Number.isNaN(orderId)) return
  const match = threads.value.find(thread => thread.order_id === orderId)
  if (match) {
    openThread(match)
  }
}

// Debounced load threads to prevent rapid API calls
const loadThreads = useDebounceFn(async (forceRefresh = false) => {
  if (loadingThreads.value && !forceRefresh) return // Prevent concurrent loads
  
  loadingThreads.value = true
  try {
    // Use shared cache store
    const fetchedThreads = await messagesStore.getThreads(forceRefresh)
    // Use shallowRef assignment for better performance
    threads.value = fetchedThreads
    // Reset to first page when threads change
    currentPage.value = 1
    openThreadFromOrder()
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to load threads:', error)
    }
  } finally {
    loadingThreads.value = false
  }
}, 300)

// Memoized unread counts per tab
const unreadCountsCache = ref(new Map())
const threadCountsCache = ref(new Map())

const getUnreadCountForTab = (tabId) => {
  // Return cached value if available
  if (unreadCountsCache.value.has(tabId)) {
    return unreadCountsCache.value.get(tabId)
  }

  const activeTabData = recipientTabs.value.find(t => t.id === tabId)
  if (!activeTabData) {
    unreadCountsCache.value.set(tabId, 0)
    return 0
  }

  const count = threads.value
    .filter(thread => {
      const otherParticipants = thread.participants?.filter(p => {
        const participantId = typeof p === 'object' ? p.id : p
        return participantId !== currentUser?.id
      }) || []
      
      return otherParticipants.some(participant => {
        const participantRole = typeof participant === 'object' ? participant.role : null
        return participantRole && activeTabData.roles.includes(participantRole)
      })
    })
    .reduce((sum, thread) => sum + (thread.unread_count || 0), 0)

  unreadCountsCache.value.set(tabId, count)
  return count
}

const getThreadCountForTab = (tabId) => {
  if (threadCountsCache.value.has(tabId)) {
    return threadCountsCache.value.get(tabId)
  }

  const activeTabData = recipientTabs.value.find(t => t.id === tabId)
  if (!activeTabData) {
    threadCountsCache.value.set(tabId, 0)
    return 0
  }

  const count = threads.value.filter(thread => {
    const otherParticipants = thread.participants?.filter(p => {
      const participantId = typeof p === 'object' ? p.id : p
      return participantId !== currentUser?.id
    }) || []

    return otherParticipants.some(participant => {
      const participantRole = typeof participant === 'object' ? participant.role : null
      return participantRole && activeTabData.roles.includes(participantRole)
    })
  }).length

  threadCountsCache.value.set(tabId, count)
  return count
}

// Memoized thread title computation
const threadTitleCache = ref(new WeakMap())

const getThreadTitle = (thread) => {
  // Use WeakMap for memory-efficient caching
  if (threadTitleCache.value.has(thread)) {
    return threadTitleCache.value.get(thread)
  }

  const otherParticipants = thread.participants?.filter(p => 
    (typeof p === 'object' ? p.id : p) !== currentUser?.id
  ) || []

  let title = 'Conversation'
  if (otherParticipants.length === 1) {
    const p = otherParticipants[0]
    title = typeof p === 'object' ? (p.username || p.email) : 'User'
  } else if (otherParticipants.length > 1) {
    title = `${otherParticipants.length} participants`
  }

  threadTitleCache.value.set(thread, title)
  return title
}

// Memoized thread subtitle computation
const threadSubtitleCache = ref(new WeakMap())

const getThreadSubtitle = (thread) => {
  if (threadSubtitleCache.value.has(thread)) {
    return threadSubtitleCache.value.get(thread)
  }

  const otherParticipants = thread.participants?.filter(p => 
    (typeof p === 'object' ? p.id : p) !== currentUser?.id
  ) || []

  let subtitle = 'No other participants'
  if (otherParticipants.length > 0) {
    const roles = otherParticipants.map(p => {
      const role = typeof p === 'object' ? p.role : null
      return role ? role.charAt(0).toUpperCase() + role.slice(1) : 'User'
    })
    subtitle = roles.join(', ')
  }

  threadSubtitleCache.value.set(thread, subtitle)
  return subtitle
}

// Memoized thread initials computation
const threadInitialsCache = ref(new WeakMap())

const getThreadInitials = (thread) => {
  if (threadInitialsCache.value.has(thread)) {
    return threadInitialsCache.value.get(thread)
  }

  const title = getThreadTitle(thread)
  const words = title.split(' ')
  let initials = title.substring(0, 2).toUpperCase()
  if (words.length >= 2) {
    initials = (words[0][0] + words[1][0]).toUpperCase()
  }

  threadInitialsCache.value.set(thread, initials)
  return initials
}

// Optimized time formatting with caching
const timeFormatCache = ref(new Map())
const CACHE_DURATION = 60000 // 1 minute

const formatTime = (dateString) => {
  if (!dateString) return ''
  
  // Check cache
  const cacheKey = `${dateString}_${Math.floor(Date.now() / CACHE_DURATION)}`
  if (timeFormatCache.value.has(cacheKey)) {
    return timeFormatCache.value.get(cacheKey)
  }

  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  
  let formatted = ''
  if (minutes < 1) formatted = 'Just now'
  else if (minutes < 60) formatted = `${minutes}m ago`
  else if (minutes < 1440) formatted = `${Math.floor(minutes / 60)}h ago`
  else formatted = date.toLocaleDateString()

  // Cache the result
  timeFormatCache.value.set(cacheKey, formatted)
  
  // Clean old cache entries periodically
  if (timeFormatCache.value.size > 100) {
    const keysToDelete = Array.from(timeFormatCache.value.keys()).slice(0, 50)
    keysToDelete.forEach(key => timeFormatCache.value.delete(key))
  }

  return formatted
}

const openNewMessageModal = () => {
  showNewMessageModal.value = true
}

const openThread = (thread) => {
  // Navigate to thread detail page instead of opening modal
  router.push(`/messages/thread/${thread.id}`)
}


const handleMessageSent = () => {
  showNewMessageModal.value = false
  // Clear caches
  unreadCountsCache.value.clear()
  threadCountsCache.value.clear()
  threadTitleCache.value = new WeakMap()
  threadSubtitleCache.value = new WeakMap()
  threadInitialsCache.value = new WeakMap()
  // Invalidate cache and reload
  messagesStore.invalidateThreadsCache()
  loadThreads(true) // Force refresh
}

const handleThreadUpdated = () => {
  // Clear caches
  unreadCountsCache.value.clear()
  threadCountsCache.value.clear()
  // Invalidate cache and reload
  messagesStore.invalidateThreadsCache()
  loadThreads(true) // Force refresh
}

watch(activeTab, () => {
  currentPage.value = 1 // Reset to first page
  // Clear unread counts cache when tab changes
  unreadCountsCache.value.clear()
  threadCountsCache.value.clear()
})

// Debounced search
const debouncedSearch = useDebounceFn(() => {
  currentPage.value = 1 // Reset to first page on search
}, 300)

watch(searchQuery, () => {
  debouncedSearch()
})

watch(
  () => [route.query.order, threads.value.length],
  () => {
    openThreadFromOrder()
  }
)

watch(
  () => threads.value,
  () => {
    unreadCountsCache.value.clear()
    threadCountsCache.value.clear()
  }
)

onMounted(async () => {
  await loadThreads()
  // Use shared refresh system to prevent multiple intervals
  // Increased interval to 45 seconds to reduce API calls
  messagesStore.startSharedRefresh(() => {
    loadThreads()
  }, 45000)
})

onUnmounted(() => {
  // Cleanup is handled by shared store
  messagesStore.stopAllRefreshes()
  // Clear all caches
  unreadCountsCache.value.clear()
  threadCountsCache.value.clear()
  timeFormatCache.value.clear()
  threadTitleCache.value = new WeakMap()
  threadSubtitleCache.value = new WeakMap()
  threadInitialsCache.value = new WeakMap()
})
</script>

<style scoped>
.messages-page {
  min-height: calc(100vh - 4rem);
}
</style>


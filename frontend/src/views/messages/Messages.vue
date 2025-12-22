<template>
  <div class="messages-page min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="max-w-7xl mx-auto p-6">
      <!-- Header -->
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">Messages</h1>
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
                <span
                  v-if="getUnreadCountForTab(tab.id) > 0"
                  class="ml-2 px-2 py-0.5 bg-red-500 text-white text-xs rounded-full"
                >
                  {{ getUnreadCountForTab(tab.id) }}
                </span>
              </span>
            </button>
          </nav>
        </div>

        <!-- New Message Button -->
        <div class="p-4 border-b border-gray-200 dark:border-gray-700">
          <button
            @click="openNewMessageModal"
            class="w-full px-4 py-2.5 bg-linear-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-lg font-semibold transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
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
          <div
            v-for="thread in filteredThreads"
            :key="thread.id"
            @click="openThread(thread)"
            class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors"
            :class="{ 'bg-blue-50 dark:bg-blue-900/20': selectedThreadId === thread.id }"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-3 mb-2">
                  <div class="w-10 h-10 rounded-full bg-linear-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-semibold shrink-0">
                    {{ getThreadInitials(thread) }}
                  </div>
                  <div class="flex-1 min-w-0">
                    <h3 class="font-semibold text-gray-900 dark:text-white truncate">
                      {{ getThreadTitle(thread) }}
                    </h3>
                    <p class="text-sm text-gray-500 dark:text-gray-400">
                      {{ getThreadSubtitle(thread) }}
                    </p>
                  </div>
                </div>
                <p v-if="thread.last_message" class="text-sm text-gray-600 dark:text-gray-300 truncate ml-13">
                  {{ thread.last_message.message || '📎 File attachment' }}
                </p>
              </div>
              <div class="flex flex-col items-end gap-2 shrink-0">
                <span class="text-xs text-gray-500 dark:text-gray-400">
                  {{ formatTime(thread.last_message?.sent_at || thread.updated_at) }}
                </span>
                <span
                  v-if="thread.unread_count > 0"
                  class="px-2 py-1 bg-red-500 text-white text-xs rounded-full font-medium"
                >
                  {{ thread.unread_count }}
                </span>
              </div>
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

    <!-- Thread View Modal -->
    <ThreadViewModal
      v-if="selectedThread"
      :thread="selectedThread"
      :show="!!selectedThread"
      @close="closeThread"
      @thread-updated="handleThreadUpdated"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { communicationsAPI } from '@/api'
import { useAuthStore } from '@/stores/auth'
import messagesStore from '@/stores/messages'
import NewMessageModal from '@/components/messages/NewMessageModal.vue'
import ThreadViewModal from '@/components/messages/ThreadViewModal.vue'

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
const threads = ref([])
const loadingThreads = ref(false)
const showNewMessageModal = ref(false)
const selectedThread = ref(null)
const selectedThreadId = ref(null)

// Icon components (simple SVG components)
const AdminIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>' }
const ClientIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>' }
const WriterIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>' }
const EditorIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>' }
const SupportIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" /></svg>' }

const filteredThreads = computed(() => {
  const activeTabData = recipientTabs.value.find(t => t.id === activeTab.value)
  if (!activeTabData) return []

  return threads.value.filter(thread => {
    // Get other participants (excluding current user)
    const otherParticipants = thread.participants?.filter(p => {
      const participantId = typeof p === 'object' ? p.id : p
      return participantId !== currentUser?.id
    }) || []

    if (otherParticipants.length === 0) return false

    // Check if any participant matches the active tab's roles
    return otherParticipants.some(participant => {
      let participantRole = null
      
      if (typeof participant === 'object') {
        participantRole = participant.role || null
      }
      
      return participantRole && activeTabData.roles.includes(participantRole)
    })
  }).sort((a, b) => {
    // Sort by last message time or updated time
    const aTime = a.last_message?.sent_at || a.updated_at || a.created_at
    const bTime = b.last_message?.sent_at || b.updated_at || b.created_at
    return new Date(bTime) - new Date(aTime)
  })
})

const loadThreads = async (forceRefresh = false) => {
  loadingThreads.value = true
  try {
    // Use shared cache store
    threads.value = await messagesStore.getThreads(forceRefresh)
  } catch (error) {
    console.error('Failed to load threads:', error)
  } finally {
    loadingThreads.value = false
  }
}

const getUnreadCountForTab = (tabId) => {
  const activeTabData = recipientTabs.value.find(t => t.id === tabId)
  if (!activeTabData) return 0

  return filteredThreads.value.reduce((sum, thread) => {
    return sum + (thread.unread_count || 0)
  }, 0)
}

const getThreadTitle = (thread) => {
  const otherParticipants = thread.participants?.filter(p => 
    (typeof p === 'object' ? p.id : p) !== currentUser?.id
  ) || []

  if (otherParticipants.length === 0) return 'Conversation'
  if (otherParticipants.length === 1) {
    const p = otherParticipants[0]
    return typeof p === 'object' ? (p.username || p.email) : 'User'
  }
  return `${otherParticipants.length} participants`
}

const getThreadSubtitle = (thread) => {
  const otherParticipants = thread.participants?.filter(p => 
    (typeof p === 'object' ? p.id : p) !== currentUser?.id
  ) || []

  if (otherParticipants.length === 0) return 'No other participants'
  
  const roles = otherParticipants.map(p => {
    const role = typeof p === 'object' ? p.role : null
    return role ? role.charAt(0).toUpperCase() + role.slice(1) : 'User'
  })
  
  return roles.join(', ')
}

const getThreadInitials = (thread) => {
  const title = getThreadTitle(thread)
  const words = title.split(' ')
  if (words.length >= 2) {
    return (words[0][0] + words[1][0]).toUpperCase()
  }
  return title.substring(0, 2).toUpperCase()
}

const formatTime = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (minutes < 1440) return `${Math.floor(minutes / 60)}h ago`
  return date.toLocaleDateString()
}

const openNewMessageModal = () => {
  showNewMessageModal.value = true
}

const openThread = (thread) => {
  selectedThread.value = thread
  selectedThreadId.value = thread.id
}

const closeThread = () => {
  selectedThread.value = null
  selectedThreadId.value = null
}

const handleMessageSent = () => {
  showNewMessageModal.value = false
  // Invalidate cache and reload
  messagesStore.invalidateThreadsCache()
  loadThreads(true) // Force refresh
}

const handleThreadUpdated = () => {
  // Invalidate cache and reload
  messagesStore.invalidateThreadsCache()
  loadThreads(true) // Force refresh
}

watch(activeTab, () => {
  selectedThread.value = null
  selectedThreadId.value = null
})

onMounted(async () => {
  await loadThreads()
  // Use shared refresh system to prevent multiple intervals
  messagesStore.startSharedRefresh(() => {
    loadThreads()
  }, 30000)
})

onUnmounted(() => {
  // Cleanup is handled by shared store
  messagesStore.stopAllRefreshes()
})
</script>

<style scoped>
.messages-page {
  min-height: calc(100vh - 4rem);
}
</style>


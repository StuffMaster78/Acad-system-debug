<template>
  <div class="order-messages-tabbed">
    <!-- Header with Order Context -->
    <div class="mb-6 p-5 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl border-2 border-blue-200 dark:border-blue-700 shadow-sm">
      <div class="flex items-center justify-between">
        <div class="flex-1">
          <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-1">Order Messages</h3>
          <p class="text-sm text-gray-600 dark:text-gray-400 mb-2">
            Order #{{ orderId }} • {{ orderTopic || 'N/A' }}
          </p>
          <p v-if="authStore.isWriter" class="text-xs text-blue-700 dark:text-blue-300 font-medium">
            💬 You can message the client, admin, support, or editor about this order
          </p>
        </div>
        <button
          @click="openNewMessageModal"
          class="ml-4 px-5 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-lg font-semibold transition-all shadow-lg hover:shadow-xl flex items-center gap-2 shrink-0"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          New Message
        </button>
      </div>
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
                <div class="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-semibold shrink-0">
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

    <!-- New Message Modal (Order-Specific) -->
    <OrderNewMessageModal
      v-if="showNewMessageModal"
      :show="showNewMessageModal"
      :order-id="orderId"
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
import OrderNewMessageModal from '@/components/order/OrderNewMessageModal.vue'
import ThreadViewModal from '@/components/messages/ThreadViewModal.vue'
import { useToast } from '@/composables/useToast'

const { success: showSuccess, error: showError } = useToast()

const props = defineProps({
  orderId: {
    type: [Number, String],
    required: true
  },
  orderTopic: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['unread-count-update'])

const authStore = useAuthStore()
const currentUser = authStore.user

// Initialize state variables first
const activeTab = ref('admin')
const threads = ref([])
const loadingThreads = ref(false)
const showNewMessageModal = ref(false)
const selectedThread = ref(null)
const selectedThreadId = ref(null)

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

// Set active tab after recipientTabs is computed
watch(recipientTabs, (tabs) => {
  if (tabs.length > 0 && !tabs.find(t => t.id === activeTab.value)) {
    activeTab.value = tabs[0].id
  }
}, { immediate: true })

// Computed property for total unread count across all tabs
const totalUnreadCount = computed(() => {
  if (!threads.value || !Array.isArray(threads.value)) {
    return 0
  }
  const orderThreads = threads.value.filter(thread => {
    const threadOrderId = thread.order || thread.order_id
    return threadOrderId && parseInt(threadOrderId) === parseInt(props.orderId)
  })
  
  return orderThreads.reduce((sum, thread) => {
    return sum + (thread.unread_count || 0)
  }, 0)
})

// Watch for changes in total unread count and emit to parent
watch(totalUnreadCount, (newCount) => {
  if (threads.value !== undefined) {
    emit('unread-count-update', newCount)
  }
}, { immediate: false })

// Icon components
const AdminIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>' }
const ClientIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" /></svg>' }
const WriterIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" /></svg>' }
const EditorIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>' }
const SupportIcon = { template: '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" /></svg>' }

// Helper: derive the "other participant" role for this thread relative to the current user.
// We prioritize the recipient_role from the last message to determine which tab to show it under.
// This ensures threads appear in only ONE tab based on who the message was sent TO.
const getOtherParticipantRoles = (thread) => {
  const roles = new Set()
  const viewerRole = currentUser?.role || null

  // PRIORITY 1: Use recipient_role from last message (most reliable for tab filtering)
  // This tells us who the message was sent TO, which determines the tab
  const last = thread.last_message
  if (last && last.recipient_role) {
    // The recipient_role is the definitive answer for which tab this thread belongs to
    // If admin sends to support, recipient_role is 'support' -> appears in Support tab only
    // If admin sends to client, recipient_role is 'client' -> appears in Client tab only
    // IMPORTANT: We ONLY use recipient_role and ignore participant roles to prevent
    // threads from appearing in multiple tabs
    const recipientRole = last.recipient_role
    // Normalize role (e.g., 'superadmin' -> 'admin' for tab matching)
    if (recipientRole === 'superadmin') {
      roles.add('admin')
    } else {
      roles.add(recipientRole)
    }
    // Return early with just the recipient role to avoid matching multiple tabs
    return Array.from(roles)
  }

  // PRIORITY 2: Fallback to participant roles if no last message
  // But only if we're the viewer, we want to know who the OTHER participants are
  const participants = thread.participants || []
  const otherParticipants = participants.filter(p => {
    const participantId = typeof p === 'object' ? p.id : p
    return participantId !== currentUser?.id
  })

  // Extract roles from other participants (fallback only)
  otherParticipants.forEach(p => {
    const role = typeof p === 'object' ? p.role : null
    if (role) roles.add(role)
  })

  return Array.from(roles)
}

const filteredThreads = computed(() => {
  const activeTabData = recipientTabs.value.find(t => t.id === activeTab.value)
  if (!activeTabData) return []

  // Filter threads that are related to this order
  const orderThreads = threads.value.filter(thread => {
    const threadOrderId = thread.order || thread.order_id
    return threadOrderId && parseInt(threadOrderId) === parseInt(props.orderId)
  })

  // Filter threads based on the recipient role of the last message
  // This ensures threads appear under the correct tab (only ONE tab)
  return orderThreads.filter(thread => {
    const otherRoles = getOtherParticipantRoles(thread)
    if (!otherRoles.length) {
      // If no roles found, check if thread has participants with roles
      const participants = thread.participants || []
      const otherParticipants = participants.filter(p => {
        const participantId = typeof p === 'object' ? p.id : p
        return participantId !== currentUser?.id
      })
      
      // Extract roles from participants
      const participantRoles = otherParticipants
        .map(p => typeof p === 'object' ? p.role : null)
        .filter(Boolean)
      
      if (participantRoles.length > 0) {
        // Only match if ONE of the participant roles matches the active tab
        return participantRoles.some(role => activeTabData.roles.includes(role))
      }
      
      return false
    }
    
    // Check if the recipient role (from last message) matches the active tab
    // This ensures threads appear in only ONE tab based on who the message was sent TO
    return otherRoles.some(role => activeTabData.roles.includes(role))
  }).sort((a, b) => {
    // Sort by last message time or updated time (newest first)
    const aTime = a.last_message?.sent_at || a.updated_at || a.created_at
    const bTime = b.last_message?.sent_at || b.updated_at || b.created_at
    return new Date(bTime) - new Date(aTime)
  })
})

const loadThreads = async (forceRefresh = false) => {
  loadingThreads.value = true
  try {
    // Try using shared cache store first
    let allThreads = []
    try {
      allThreads = await messagesStore.getThreads(forceRefresh)
    } catch (storeError) {
      // Fallback to direct API call if store fails
      console.warn('Messages store failed, using direct API call:', storeError)
      const response = await communicationsAPI.listThreads({ order: props.orderId })
      allThreads = response.data.results || response.data || []
    }
    
    // Filter threads that belong to this order
    threads.value = allThreads.filter(thread => {
      const threadOrderId = thread.order || thread.order_id
      return threadOrderId && parseInt(threadOrderId) === parseInt(props.orderId)
    })
  } catch (error) {
    console.error('Failed to load threads:', error)
    // Show user-friendly error message
    const errorMsg = error.response?.data?.detail || error.message || 'Failed to load conversations'
    showError(errorMsg)
    threads.value = [] // Clear threads on error
  } finally {
    loadingThreads.value = false
  }
}

const getUnreadCountForTab = (tabId) => {
  const activeTabData = recipientTabs.value.find(t => t.id === tabId)
  if (!activeTabData) return 0

  // Use the same filtering logic as filteredThreads to ensure count matches visible threads
  const orderThreads = threads.value.filter(thread => {
    const threadOrderId = thread.order || thread.order_id
    return threadOrderId && parseInt(threadOrderId) === parseInt(props.orderId)
  })

  return orderThreads.reduce((sum, thread) => {
    // Use the same logic as filteredThreads - prioritize recipient_role from last message
    const otherRoles = getOtherParticipantRoles(thread)
    
    // Check if the thread matches the active tab using the same logic as filteredThreads
    let matchesTab = false
    if (otherRoles.length > 0) {
      matchesTab = otherRoles.some(role => activeTabData.roles.includes(role))
    } else {
      // Fallback to participant roles if no recipient_role
      const participants = thread.participants || []
      const otherParticipants = participants.filter(p => {
        const participantId = typeof p === 'object' ? p.id : p
        return participantId !== currentUser?.id
      })
      
      const participantRoles = otherParticipants
        .map(p => typeof p === 'object' ? p.role : null)
        .filter(Boolean)
      
      if (participantRoles.length > 0) {
        matchesTab = participantRoles.some(role => activeTabData.roles.includes(role))
      }
    }

    return matchesTab ? sum + (thread.unread_count || 0) : sum
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
  
  try {
    const date = new Date(dateString)
    const now = new Date()
    
    // Check if date is valid
    if (isNaN(date.getTime())) {
      return 'Invalid date'
    }
    
    const diff = now - date
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(minutes / 60)
    const days = Math.floor(hours / 24)
    
    // Show relative time for recent messages
    if (minutes < 1) return 'Just now'
    if (minutes < 60) return `${minutes}m ago`
    if (hours < 24) return `${hours}h ago`
    if (days < 7) return `${days}d ago`
    
    // For older messages, show formatted date and time
    const isToday = date.toDateString() === now.toDateString()
    const isYesterday = date.toDateString() === new Date(now.getTime() - 86400000).toDateString()
    
    if (isToday) {
      return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
    } else if (isYesterday) {
      return `Yesterday ${date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })}`
    } else if (days < 365) {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', hour12: true })
    } else {
      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
    }
  } catch (error) {
    console.error('Error formatting time:', error, dateString)
    return 'Invalid date'
  }
}

const openNewMessageModal = () => {
  showNewMessageModal.value = true
}

const openThread = (thread) => {
  if (!thread || !thread.id) {
    console.error('Invalid thread:', thread)
    showError('Invalid conversation')
    return
  }
  selectedThread.value = thread
  selectedThreadId.value = thread.id
}

const closeThread = () => {
  selectedThread.value = null
  selectedThreadId.value = null
}

const handleMessageSent = (success = true) => {
  if (success) {
    showSuccess('Message sent successfully!')
    showNewMessageModal.value = false
    // Invalidate cache and reload
    messagesStore.invalidateThreadsCache()
    loadThreads(true) // Force refresh
  } else {
    showError('Failed to send message. Please try again.')
  }
}

const handleThreadUpdated = (success = true) => {
  if (success) {
    showSuccess('Message sent successfully!')
    // Invalidate cache and reload
    messagesStore.invalidateThreadsCache()
    loadThreads(true) // Force refresh
  } else {
    showError('Failed to send message. Please try again.')
  }
}

watch(activeTab, () => {
  selectedThread.value = null
  selectedThreadId.value = null
})

watch(() => props.orderId, () => {
  if (props.orderId) {
    loadThreads()
  }
})

onMounted(async () => {
  if (props.orderId) {
    await loadThreads()
    // Emit initial count after threads are loaded
    emit('unread-count-update', totalUnreadCount.value)
    // Prefer SSE-based updates over polling to reduce HTTP chatter
    messagesStore.connectRealtime()
  }
})

onUnmounted(() => {
  // Keep SSE connection alive for other consumers; no explicit disconnect here.
})
</script>

<style scoped>
.order-messages-tabbed {
  min-height: 400px;
}
</style>


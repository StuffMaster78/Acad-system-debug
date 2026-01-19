<template>
  <div class="thread-detail-page min-h-dvh bg-gray-50 dark:bg-gray-900">
    <div class="max-w-6xl mx-auto page-shell">
      <!-- Loading State -->
      <div v-if="loadingThread" class="flex items-center justify-center min-h-[500px]">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p class="text-gray-600 dark:text-gray-400 text-lg">Loading thread...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="!thread" class="flex items-center justify-center min-h-[500px]">
        <div class="text-center max-w-md">
          <div class="w-20 h-20 mx-auto mb-6 rounded-full bg-red-100 dark:bg-red-900/20 flex items-center justify-center">
            <svg class="w-10 h-10 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">Thread Not Found</h2>
          <p class="text-gray-600 dark:text-gray-400 mb-6">The thread you're looking for doesn't exist or you don't have permission to view it.</p>
          <router-link
            to="/messages"
            class="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-sm hover:shadow-md"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Messages
          </router-link>
        </div>
      </div>

      <!-- Thread Content -->
      <div v-else>
        <!-- Breadcrumb -->
        <div class="mb-4">
          <nav class="flex flex-wrap items-center gap-2 text-sm text-gray-600 dark:text-gray-400" aria-label="Breadcrumb">
            <router-link to="/dashboard" class="hover:text-gray-900 dark:hover:text-gray-200">Dashboard</router-link>
            <span>/</span>
            <router-link to="/messages" class="hover:text-gray-900 dark:hover:text-gray-200">Messages</router-link>
            <span>/</span>
            <span class="text-gray-900 dark:text-gray-200 font-medium">Thread #{{ threadId }}</span>
          </nav>
        </div>

        <!-- Header -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
          <div class="p-4 sm:p-6">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div class="flex flex-wrap items-center gap-3 sm:gap-4">
                <div class="w-12 h-12 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white font-bold text-lg">
                  {{ getThreadInitials(thread) }}
                </div>
                <div>
                  <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ getThreadTitle(thread) }}</h1>
                  <div class="flex items-center gap-4 mt-2 text-sm text-gray-600 dark:text-gray-400">
                    <span>{{ getThreadSubtitle(thread) }}</span>
                    <span v-if="thread && thread.order" class="flex items-center gap-1">
                      <span>Order #{{ thread.order.id || thread.order }}</span>
                    </span>
                  </div>
                  <!-- Client/Writer Info -->
                  <div v-if="otherParticipant" class="mt-2 text-sm">
                    <div v-if="authStore.isWriter && otherParticipant.role === 'client'" class="text-gray-600 dark:text-gray-400">
                      <span class="font-semibold">Client ID:</span> {{ otherParticipant.id }}
                      <span v-if="otherParticipant.nickname" class="ml-2">
                        <span class="font-semibold">Nickname:</span> {{ otherParticipant.nickname }}
                      </span>
                    </div>
                    <div v-else-if="authStore.isClient && otherParticipant.role === 'writer'" class="text-gray-600 dark:text-gray-400">
                      <span class="font-semibold">Writer ID:</span> {{ otherParticipant.id }}
                      <span v-if="otherParticipant.writer_profile?.pen_name" class="ml-2">
                        <span class="font-semibold">Pen Name:</span> {{ otherParticipant.writer_profile.pen_name }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              <button 
                @click="$router.push('/messages')" 
                class="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors self-start sm:self-auto"
              >
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <!-- Messaging Lock Warning -->
            <div v-if="isMessagingLocked" class="mt-4 p-3 bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-lg">
              <div class="flex items-center gap-2 text-amber-800 dark:text-amber-200">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
                <span class="font-medium">Messaging is locked for this order. You can view messages but cannot send new ones.</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Messages List (Table Format) -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
        <!-- Table Controls -->
        <div class="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 bg-gray-50 dark:bg-gray-700/50 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center gap-2">
            <label class="text-sm text-gray-700 dark:text-gray-300">Show</label>
            <select
              v-model="itemsPerPage"
              @change="loadMessages(false)"
              class="border border-gray-300 dark:border-gray-600 rounded px-2 py-1 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-800 dark:text-white"
            >
              <option :value="10">10</option>
              <option :value="25">25</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
            <label class="text-sm text-gray-700 dark:text-gray-300">entries</label>
          </div>
          <div class="flex flex-wrap items-center gap-2 w-full sm:w-auto">
            <label class="text-sm text-gray-700 dark:text-gray-300">Search:</label>
            <input
              v-model="searchQuery"
              @input="debouncedSearch"
              type="text"
              placeholder="Search messages..."
              class="border border-gray-300 dark:border-gray-600 rounded px-3 py-1.5 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-full sm:w-48 dark:bg-gray-800 dark:text-white"
            />
          </div>
        </div>

        <!-- Messages Table -->
        <div class="table-scroll">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-teal-50 dark:bg-teal-900/20">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                  <div class="flex items-center gap-2">
                    <input type="checkbox" class="w-3 h-3" />
                    #
                  </div>
                </th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                  <div class="flex items-center gap-2">
                    <input type="checkbox" class="w-3 h-3" />
                    Time
                  </div>
                </th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                  <div class="flex items-center gap-2">
                    <input type="checkbox" class="w-3 h-3" />
                    From / To
                  </div>
                </th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                  <div class="flex items-center gap-2">
                    <input type="checkbox" class="w-3 h-3" />
                    Message
                  </div>
                </th>
                <th class="px-4 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">
                  <div class="flex items-center gap-2">
                    <input type="checkbox" class="w-3 h-3" />
                    Status
                  </div>
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-if="loadingMessages" class="bg-gray-50 dark:bg-gray-900">
                <td colspan="5" class="px-4 py-12 text-center">
                  <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                  <p class="mt-4 text-gray-600 dark:text-gray-400">Loading messages...</p>
                </td>
              </tr>
              <tr v-else-if="filteredMessages.length === 0" class="bg-gray-50 dark:bg-gray-900">
                <td colspan="5" class="px-4 py-12 text-center text-gray-500 dark:text-gray-400">
                  <svg class="w-16 h-16 mx-auto mb-4 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <p class="text-lg font-medium">No messages yet</p>
                  <p class="text-sm mt-2">Start the conversation below!</p>
                </td>
              </tr>
              <tr
                v-else
                v-for="message in paginatedMessages"
                :key="message.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
              >
                <!-- Message ID -->
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="flex items-center gap-2">
                    <div class="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center">
                      <span class="text-white text-xs font-bold">+</span>
                    </div>
                    <span class="text-sm font-medium text-gray-900 dark:text-white">{{ message.id }}</span>
                  </div>
                </td>
                
                <!-- Time -->
                <td class="px-4 py-3 whitespace-nowrap">
                  <span class="text-sm text-gray-900 dark:text-white">{{ formatTableTime(message.sent_at) }}</span>
                </td>
                
                <!-- From / To -->
                <td class="px-4 py-3">
                  <span class="text-sm text-gray-900 dark:text-white">
                    {{ isCurrentUser(message.sender) ? 'From Me' : `From ${getSenderName(message.sender)}` }}
                    <span v-if="message.recipient && !isCurrentUser(message.recipient)" class="text-gray-500 dark:text-gray-400">
                      to {{ getRecipientName(message.recipient) }}
                    </span>
                  </span>
                </td>
                
                <!-- Message Content -->
                <td class="px-4 py-3">
                  <div class="text-sm text-gray-900 dark:text-white max-w-2xl">
                    <span v-if="message.reply_to" class="text-xs text-gray-500 dark:text-gray-400 italic mr-2">(Reply)</span>
                    <span v-if="message.attachment" class="text-xs text-blue-600 dark:text-blue-400 mr-2">📎 Attachment</span>
                    <span class="whitespace-pre-wrap">{{ message.message || '📎 File attachment' }}</span>
                  </div>
                </td>
                
                <!-- Status -->
                <td class="px-4 py-3 whitespace-nowrap">
                  <div class="flex items-center gap-2">
                    <div v-if="isCurrentUser(message.sender)" class="flex items-center">
                      <svg
                        v-if="message.is_read"
                        class="w-4 h-4 text-green-500"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                        title="Read"
                      >
                        <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                      </svg>
                      <svg
                        v-else
                        class="w-4 h-4 text-gray-400"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                        title="Sent"
                      >
                        <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                      </svg>
                    </div>
                    <span v-else class="text-xs text-gray-500 dark:text-gray-400">Received</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-200 dark:border-gray-700">
          <div class="text-sm text-gray-700 dark:text-gray-300">
            Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to {{ Math.min(currentPage * itemsPerPage, filteredMessages.length) }} of {{ filteredMessages.length }} entries
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="currentPage = Math.max(1, currentPage - 1)"
              :disabled="currentPage === 1"
              class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed dark:text-white"
            >
              Previous
            </button>
            <span class="text-sm text-gray-600 dark:text-gray-400">
              Page {{ currentPage }} of {{ totalPages }}
            </span>
            <button
              @click="currentPage = Math.min(totalPages, currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed dark:text-white"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      <!-- Message Composer -->
      <div v-if="!isMessagingLocked" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700">
        <SimplifiedMessageComposer
          :thread-id="threadId"
          @message-sent="handleMessageSent"
        />
      </div>
      <div v-else class="bg-gray-100 dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 text-center text-gray-500 dark:text-gray-400">
        <p>Messaging is locked for this thread. You cannot send new messages.</p>
      </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, shallowRef, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { communicationsAPI } from '@/api'
import { useAuthStore } from '@/stores/auth'
import messagesStore from '@/stores/messages'
import SimplifiedMessageComposer from '@/components/communications/SimplifiedMessageComposer.vue'
import { useDebounceFn } from '@vueuse/core'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const currentUser = authStore.user

const threadId = computed(() => parseInt(route.params.id))
const thread = shallowRef(null)
const messages = shallowRef([])
const loadingThread = ref(false)
const loadingMessages = ref(false)
const searchQuery = ref('')
const itemsPerPage = ref(10)
const currentPage = ref(1)

// SSE state
let threadEventSource = null

// Load thread details
const loadThread = async () => {
  if (!threadId.value) return
  
  loadingThread.value = true
  try {
    const response = await communicationsAPI.getThread(threadId.value)
    thread.value = response.data
    
    // Mark thread as read
    try {
      await communicationsAPI.markThreadAsRead(threadId.value)
      messagesStore.invalidateThreadsCache()
    } catch (error) {
      if (import.meta.env.DEV) {
        console.warn('Failed to mark thread as read:', error)
      }
    }
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to load thread:', error)
    }
    // Redirect to messages if thread not found
    router.push('/messages')
  } finally {
    loadingThread.value = false
  }
}

// Load messages
const loadMessages = async () => {
  if (!threadId.value) return
  
  loadingMessages.value = true
  try {
    const response = await communicationsAPI.listMessages(threadId.value, {
      page: currentPage.value,
      page_size: itemsPerPage.value
    })
    
    let raw = []
    if (response.data?.results) {
      raw = response.data.results
    } else if (Array.isArray(response.data)) {
      raw = response.data
    } else if (response.data?.data && Array.isArray(response.data.data)) {
      raw = response.data.data
    }
    
    // Sort by sent_at (oldest first)
    if (Array.isArray(raw) && raw.length > 0) {
      messages.value = [...raw].sort((a, b) => {
        const timeA = a.sent_at ? new Date(a.sent_at).getTime() : 0
        const timeB = b.sent_at ? new Date(b.sent_at).getTime() : 0
        return timeA - timeB
      })
    } else {
      messages.value = []
    }
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to load messages:', error)
    }
    messages.value = []
  } finally {
    loadingMessages.value = false
  }
}

// Filtered messages based on search
const filteredMessages = computed(() => {
  if (!searchQuery.value.trim()) {
    return messages.value
  }
  
  const query = searchQuery.value.toLowerCase()
  return messages.value.filter(msg => {
    const messageText = (msg.message || '').toLowerCase()
    const senderName = getSenderName(msg.sender).toLowerCase()
    return messageText.includes(query) || senderName.includes(query)
  })
})

// Paginated messages
const paginatedMessages = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredMessages.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredMessages.value.length / itemsPerPage.value)
})

// Check if messaging is locked
const isMessagingLocked = computed(() => {
  if (!thread.value) return false
  if (thread.value.admin_override) return false
  if (!thread.value.is_active) return true
  
  const order = thread.value.order
  if (!order) return false
  
  // Check if order is archived or cancelled
  if (typeof order === 'object') {
    return order.status === 'archived' || order.status === 'cancelled' || order.is_archived
  }
  
  return false
})

// Get other participant (for client/writer info)
const otherParticipant = computed(() => {
  if (!thread.value?.participants) return null
  
  const other = thread.value.participants.find(p => {
    const participantId = typeof p === 'object' ? p.id : p
    return participantId !== currentUser?.id
  })
  
  return typeof other === 'object' ? other : null
})

// Helper functions
const getThreadTitle = (thread) => {
  if (!thread) return 'Loading...'
  const otherParticipants = thread.participants?.filter(p => {
    const participantId = typeof p === 'object' ? p.id : p
    return participantId !== currentUser?.id
  }) || []

  if (otherParticipants.length === 0) return 'Conversation'
  if (otherParticipants.length === 1) {
    const p = otherParticipants[0]
    return typeof p === 'object' ? (p.username || p.email || 'User') : 'User'
  }
  return `${otherParticipants.length} participants`
}

const getThreadSubtitle = (thread) => {
  if (!thread) return ''
  const otherParticipants = thread.participants?.filter(p => {
    const participantId = typeof p === 'object' ? p.id : p
    return participantId !== currentUser?.id
  }) || []

  if (otherParticipants.length === 0) return 'No other participants'
  
  const roles = otherParticipants.map(p => {
    const role = typeof p === 'object' ? p.role : null
    return role ? role.charAt(0).toUpperCase() + role.slice(1) : 'User'
  })
  
  return roles.join(', ')
}

const getThreadInitials = (thread) => {
  if (!thread) return '??'
  const title = getThreadTitle(thread)
  if (!title || title === 'Loading...') return '??'
  const words = title.split(' ').filter(w => w.length > 0)
  if (words.length >= 2) {
    return (words[0][0] + words[1][0]).toUpperCase()
  }
  return title.substring(0, 2).toUpperCase() || '??'
}

const isCurrentUser = (sender) => {
  if (!sender) return false
  const senderId = typeof sender === 'object' ? sender.id : sender
  return senderId === currentUser?.id
}

const getSenderName = (sender) => {
  if (!sender) return 'Unknown'
  if (isCurrentUser(sender)) return 'Me'
  if (typeof sender === 'object') {
    return sender.username || sender.email || 'Unknown'
  }
  return 'Unknown'
}

const getRecipientName = (recipient) => {
  if (!recipient) return 'Unknown'
  if (typeof recipient === 'object') {
    return recipient.username || recipient.email || 'Unknown'
  }
  return 'Unknown'
}

const formatTableTime = (dateString) => {
  if (!dateString) return ''
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return 'Invalid date'
    
    // Format as DD/MM/YYYY HH:MM
    const day = String(date.getDate()).padStart(2, '0')
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const year = date.getFullYear()
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    
    return `${day}/${month}/${year} ${hours}:${minutes}`
  } catch (error) {
    return 'Invalid date'
  }
}

const handleMessageSent = async () => {
  await loadMessages()
  messagesStore.invalidateThreadMessagesCache(threadId.value)
  messagesStore.invalidateThreadsCache()
  
  // Reset to last page to show new message
  await nextTick()
  currentPage.value = totalPages.value
}

// Connect to SSE stream
const connectThreadStream = () => {
  if (!threadId.value || threadEventSource) return

  try {
    const token = localStorage.getItem('access_token')
    const url = token
      ? `/api/v1/order-communications/communication-threads-stream/${threadId.value}/?token=${encodeURIComponent(token)}`
      : `/api/v1/order-communications/communication-threads-stream/${threadId.value}/`
    
    threadEventSource = new EventSource(url)

    threadEventSource.addEventListener('thread_messages', (event) => {
      try {
        const payload = JSON.parse(event.data || '[]')
        const newMessages = Array.isArray(payload) ? payload : []
        
        if (newMessages.length > 0) {
          const existingIds = new Set(messages.value.map(m => m.id))
          const uniqueNewMessages = newMessages.filter(m => !existingIds.has(m.id))
          
          if (uniqueNewMessages.length > 0) {
            const merged = [...messages.value, ...uniqueNewMessages].sort((a, b) => {
              const timeA = a.sent_at ? new Date(a.sent_at).getTime() : 0
              const timeB = b.sent_at ? new Date(b.sent_at).getTime() : 0
              return timeA - timeB
            })
            messages.value = merged
          }
        }
      } catch (error) {
        if (import.meta.env.DEV) {
          console.error('Failed to parse thread_messages payload', error)
        }
      }
    })

    threadEventSource.onerror = () => {
      if (threadEventSource) {
        threadEventSource.close()
        threadEventSource = null
      }
    }
  } catch (error) {
    console.error('Failed to open thread SSE stream', error)
  }
}

const cleanupThreadStream = () => {
  if (threadEventSource) {
    threadEventSource.close()
    threadEventSource = null
  }
}

// Debounced search
const debouncedSearch = useDebounceFn(() => {
  currentPage.value = 1
}, 300)

watch(searchQuery, () => {
  debouncedSearch()
})

watch(() => route.params.id, async (newId) => {
  if (newId) {
    cleanupThreadStream()
    await loadThread()
    await loadMessages()
    connectThreadStream()
  }
})

watch(itemsPerPage, () => {
  currentPage.value = 1
  loadMessages()
})

watch(currentPage, () => {
  loadMessages()
})

onMounted(async () => {
  await loadThread()
  await loadMessages()
  connectThreadStream()
})

onUnmounted(() => {
  cleanupThreadStream()
})
</script>

<style scoped>
.thread-detail-page {
  min-height: calc(100vh - 4rem);
}
</style>


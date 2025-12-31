<template>
  <Transition name="modal">
    <div v-if="show" class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" @click.self="$emit('close')">
      <div class="bg-white dark:bg-gray-800 rounded-2xl max-w-4xl w-full shadow-2xl max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="bg-gradient-to-r from-blue-600 to-blue-700 dark:from-blue-700 dark:to-blue-800 px-6 py-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center text-white font-bold text-lg">
                {{ getThreadInitials(thread) }}
              </div>
              <div>
                <h3 class="text-xl font-bold text-white">{{ getThreadTitle(thread) }}</h3>
                <p class="text-sm text-blue-100 mt-1">{{ getThreadSubtitle(thread) }}</p>
              </div>
            </div>
            <button 
              @click="$emit('close')" 
              class="text-white/80 hover:text-white hover:bg-white/20 rounded-lg p-1.5 transition-colors"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Messages -->
        <div class="flex-1 overflow-y-auto p-6 bg-gray-50 dark:bg-gray-900">
          <div v-if="loadingMessages" class="text-center py-12">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p class="mt-4 text-gray-600 dark:text-gray-400">Loading messages...</p>
          </div>

          <div v-else-if="messages.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
            <svg class="w-16 h-16 mx-auto mb-4 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <p class="text-lg font-medium">No messages yet</p>
            <p class="text-sm mt-2">Start the conversation below!</p>
          </div>

          <div v-else class="space-y-4">
            <!-- Load More Button -->
            <div v-if="hasMoreMessages && !loadingMore" class="text-center py-2">
              <button
                @click="loadMessages(true)"
                class="px-4 py-2 text-sm text-blue-600 hover:text-blue-700 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
              >
                Load older messages
              </button>
            </div>
            <div v-if="loadingMore" class="text-center py-2">
              <div class="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
            </div>
            
            <div
              v-for="message in messages"
              :key="message.id"
              class="flex"
              :class="isCurrentUser(message.sender) ? 'justify-end' : 'justify-start'"
            >
              <div
                :class="[
                  'max-w-[70%] rounded-2xl px-4 py-3',
                  isCurrentUser(message.sender)
                    ? 'bg-blue-600 text-white'
                    : 'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-white'
                ]"
              >
                <div v-if="!isCurrentUser(message.sender)" class="text-xs font-semibold mb-1 opacity-75">
                  {{ message.sender?.username || 'User' }}
                </div>
                <div class="text-sm whitespace-pre-wrap">{{ message.message }}</div>
                <div
                  :class="[
                    'text-xs mt-1 flex items-center gap-2',
                    isCurrentUser(message.sender) ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'
                  ]"
                >
                  <span>{{ formatTime(message.sent_at) }}</span>
                  <!-- Read Status Indicator (only for sent messages) -->
                  <span v-if="isCurrentUser(message.sender)" class="flex items-center gap-1">
                    <svg
                      v-if="message.is_read"
                      class="w-3.5 h-3.5 text-blue-200"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                      title="Read"
                    >
                      <path d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" />
                    </svg>
                    <svg
                      v-else
                      class="w-3.5 h-3.5 text-blue-200 opacity-50"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                      title="Sent"
                    >
                      <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Message Composer -->
        <div class="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
          <SimplifiedMessageComposer
            :thread-id="thread.id"
            @message-sent="handleMessageSent"
          />
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, shallowRef, nextTick } from 'vue'
import { communicationsAPI } from '@/api'
import { useAuthStore } from '@/stores/auth'
import messagesStore from '@/stores/messages'
import SimplifiedMessageComposer from '@/components/communications/SimplifiedMessageComposer.vue'
import { useDebounceFn } from '@vueuse/core'

const props = defineProps({
  thread: {
    type: Object,
    required: true
  },
  show: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'thread-updated'])

const authStore = useAuthStore()
const currentUser = authStore.user

const messages = shallowRef([]) // Use shallowRef for better performance
const loadingMessages = ref(false)
const messagesPerPage = 50
const currentPage = ref(1)
const hasMoreMessages = ref(false)
const loadingMore = ref(false)

// SSE state for this thread
const sseStatus = ref('idle')
let threadEventSource = null

// Message format cache
const messageFormatCache = ref(new WeakMap())

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

const isCurrentUser = (sender) => {
  return sender?.id === currentUser?.id
}

const cleanupThreadStream = () => {
  if (threadEventSource) {
    threadEventSource.close()
    threadEventSource = null
  }
}

const connectThreadStream = () => {
  if (!props.thread?.id || threadEventSource) return

  sseStatus.value = 'connecting'

  try {
    // EventSource can't send custom headers, so we pass the token as a query parameter
    const token = localStorage.getItem('access_token')
    const url = token
      ? `/api/v1/order-communications/communication-threads-stream/${props.thread.id}/?token=${encodeURIComponent(token)}`
      : `/api/v1/order-communications/communication-threads-stream/${props.thread.id}/`
    
    threadEventSource = new EventSource(url)

    threadEventSource.addEventListener('thread_messages', (event) => {
      try {
        const payload = JSON.parse(event.data || '[]')
        const newMessages = Array.isArray(payload) ? payload : []
        
        // Merge with existing messages, avoiding duplicates
        if (newMessages.length > 0) {
          const existingIds = new Set(messages.value.map(m => m.id))
          const uniqueNewMessages = newMessages.filter(m => !existingIds.has(m.id))
          
          if (uniqueNewMessages.length > 0) {
            // Sort and merge
            const merged = [...messages.value, ...uniqueNewMessages].sort((a, b) => {
              const timeA = a.sent_at ? new Date(a.sent_at).getTime() : 0
              const timeB = b.sent_at ? new Date(b.sent_at).getTime() : 0
              return timeA - timeB
            })
            messages.value = merged
          }
        }
        
        sseStatus.value = 'connected'
      } catch (error) {
        if (import.meta.env.DEV) {
          console.error('Failed to parse thread_messages payload', error)
        }
      }
    })

    threadEventSource.onopen = () => {
      sseStatus.value = 'connected'
    }

    threadEventSource.onerror = () => {
      sseStatus.value = 'disconnected'
      cleanupThreadStream()
    }
  } catch (error) {
    console.error('Failed to open thread SSE stream', error)
    sseStatus.value = 'disconnected'
    cleanupThreadStream()
  }
}

// Optimized time formatting with caching
const formatTime = (dateString) => {
  if (!dateString) return ''
  
  try {
    const date = new Date(dateString)
    const now = new Date()
    
    // Check if date is valid
    if (isNaN(date.getTime())) {
      return 'Invalid date'
    }
    
    // Use cache key based on time bucket (1 minute buckets)
    const timeBucket = Math.floor(date.getTime() / 60000)
    const cacheKey = `${timeBucket}_${Math.floor(now.getTime() / 60000)}`
    
    // Simple relative time calculation
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
    if (import.meta.env.DEV) {
      console.error('Error formatting time:', error, dateString)
    }
    return 'Invalid date'
  }
}

// Debounced load messages
const loadMessages = useDebounceFn(async (loadMore = false) => {
  if (!props.thread?.id) {
    if (import.meta.env.DEV) {
      console.warn('loadMessages: No thread ID available')
    }
    messages.value = []
    return
  }

  if (loadMore) {
    loadingMore.value = true
  } else {
    loadingMessages.value = true
    messages.value = [] // Clear previous messages immediately
    currentPage.value = 1
  }
  
  try {
    // Fetch messages with pagination
    const params = {
      page: loadMore ? currentPage.value + 1 : 1,
      page_size: messagesPerPage
    }
    
    const response = await communicationsAPI.listMessages(props.thread.id, params)
    
    // Handle paginated or direct array responses
    let raw = []
    let totalCount = 0
    
    if (response.data?.results) {
      raw = response.data.results
      totalCount = response.data.count || raw.length
      hasMoreMessages.value = response.data.next !== null
    } else if (Array.isArray(response.data)) {
      raw = response.data
      hasMoreMessages.value = false
    } else if (response.data?.data && Array.isArray(response.data.data)) {
      raw = response.data.data
      hasMoreMessages.value = false
    }
    
    // Sort messages by sent_at (oldest first) for chronological display
    if (Array.isArray(raw) && raw.length > 0) {
      const sorted = [...raw].sort((a, b) => {
        const timeA = a.sent_at ? new Date(a.sent_at).getTime() : 0
        const timeB = b.sent_at ? new Date(b.sent_at).getTime() : 0
        return timeA - timeB  // Ascending order (oldest first)
      })
      
      if (loadMore) {
        // Prepend older messages
        messages.value = [...sorted, ...messages.value]
        currentPage.value += 1
      } else {
        messages.value = sorted
        currentPage.value = 1
        // Check if there are more messages
        hasMoreMessages.value = sorted.length >= messagesPerPage
      }
    } else {
      if (!loadMore) {
        messages.value = []
      }
      hasMoreMessages.value = false
    }

    // Mark all messages in thread as read when opening (only on initial load)
    if (!loadMore) {
      try {
        await communicationsAPI.markThreadAsRead(props.thread.id)
        messagesStore.invalidateThreadsCache()
      } catch (error) {
        if (import.meta.env.DEV) {
          console.warn('Failed to mark thread as read:', error)
        }
      }
    }
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to load messages:', error)
    }
    if (!loadMore) {
      messages.value = [] // Ensure we show empty state on error
    }
  } finally {
    loadingMessages.value = false
    loadingMore.value = false
  }
}, 200)

const handleMessageSent = async () => {
  // Reload messages immediately after sending to show the new message
  await loadMessages(false)
  messagesStore.invalidateThreadMessagesCache(props.thread.id)
  messagesStore.invalidateThreadsCache()
  emit('thread-updated')
  
  // Scroll to bottom after new message
  await nextTick()
  const messagesContainer = document.querySelector('.overflow-y-auto')
  if (messagesContainer) {
    messagesContainer.scrollTop = messagesContainer.scrollHeight
  }
}

watch(() => props.show, (newVal) => {
  if (newVal && props.thread?.id) {
    console.log('ThreadViewModal: Opening thread', props.thread.id)
    loadMessages()
    connectThreadStream()
  } else {
    cleanupThreadStream()
    messages.value = [] // Clear messages when closing
  }
}, { immediate: true })

onUnmounted(() => {
  cleanupThreadStream()
})

watch(() => props.thread?.id, (newId, oldId) => {
  if (newId && newId !== oldId && props.show) {
    console.log('ThreadViewModal: Thread ID changed', { oldId, newId })
    cleanupThreadStream()
    loadMessages()
    connectThreadStream()
  }
})
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active > div,
.modal-leave-active > div {
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.modal-enter-from > div,
.modal-leave-to > div {
  transform: scale(0.95) translateY(-10px);
  opacity: 0;
}
</style>


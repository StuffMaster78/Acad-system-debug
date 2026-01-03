<template>
  <div class="simplified-order-messages">
    <!-- Thread List (if multiple threads) -->
    <div v-if="showThreadList && threads.length > 1" class="border-b border-gray-200 p-4 bg-gray-50">
      <div class="flex items-center justify-between mb-3">
        <h3 class="text-sm font-semibold text-gray-700">Conversations</h3>
        <button
          @click="createNewThread"
          :disabled="creatingThread"
          class="text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          + New Conversation
        </button>
      </div>
      <div class="space-y-2">
        <button
          v-for="thread in threads"
          :key="thread.id"
          @click="selectThread(thread)"
          :class="[
            'w-full text-left p-2 rounded-lg text-sm transition-colors',
            selectedThreadId === thread.id
              ? 'bg-primary-100 text-primary-900 border border-primary-300'
              : 'bg-white hover:bg-gray-100 border border-gray-200'
          ]"
        >
          <div class="font-medium">{{ getThreadName(thread) }}</div>
          <div class="text-xs text-gray-500 mt-1">
            {{ thread.unread_count || 0 }} unread
          </div>
        </button>
      </div>
    </div>

    <!-- Messages Area -->
    <div class="flex flex-col h-full">
      <!-- Messages List -->
      <div 
        ref="messagesContainer"
        class="flex-1 overflow-y-auto bg-gray-50 px-4 py-4 space-y-3"
      >
        <div v-if="loadingMessages" class="flex items-center justify-center py-8">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
        </div>

        <div v-else-if="messages.length === 0" class="text-center py-12 text-gray-500">
          <div class="text-4xl mb-4">💬</div>
          <p class="text-lg font-medium">No messages yet</p>
          <p class="text-sm mt-2">Start the conversation by sending a message below!</p>
        </div>

        <template v-else>
          <div
            v-for="(message, index) in messages"
            :key="message.id"
            :class="[
              'flex gap-3',
              isCurrentUser(message.sender) ? 'flex-row-reverse' : 'flex-row'
            ]"
          >
            <!-- Avatar -->
            <div
              v-if="shouldShowAvatar(message, index)"
              class="shrink-0 w-8 h-8 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-sm font-semibold"
            >
              {{ getInitials(message.sender) }}
            </div>
            <div v-else class="shrink-0 w-8"></div>

            <!-- Message Bubble -->
            <div
              :class="[
                'max-w-[70%] rounded-lg px-4 py-2',
                isCurrentUser(message.sender)
                  ? 'bg-primary-600 text-white'
                  : 'bg-white border border-gray-200 text-gray-900'
              ]"
            >
              <!-- Sender Name (if not current user) -->
              <div
                v-if="!isCurrentUser(message.sender) && shouldShowAvatar(message, index)"
                class="text-xs font-semibold mb-1 text-gray-600"
              >
                {{ message.sender?.username || 'User' }}
              </div>

              <!-- Reply Preview -->
              <div
                v-if="message.reply_to"
                :class="[
                  'mb-2 p-2 rounded text-xs border-l-2',
                  isCurrentUser(message.sender)
                    ? 'bg-primary-700 border-primary-300'
                    : 'bg-gray-100 border-gray-300'
                ]"
              >
                <div class="font-medium opacity-75">
                  {{ message.reply_to?.sender?.username || 'User' }}
                </div>
                <div class="truncate opacity-75">
                  {{ message.reply_to?.message || '📎 File' }}
                </div>
              </div>

              <!-- Message Content -->
              <div class="text-sm whitespace-pre-wrap">
                <template v-for="(segment, index) in parseMessage(message.message)" :key="index">
                  <span v-if="segment.type === 'text'">{{ segment.content }}</span>
                  <router-link
                    v-else-if="segment.type === 'link'"
                    :to="segment.to"
                    :class="[
                      'underline font-medium',
                      isCurrentUser(message.sender)
                        ? 'text-primary-200 hover:text-primary-100'
                        : 'text-blue-600 hover:text-blue-800'
                    ]"
                  >
                    {{ segment.content }}
                  </router-link>
                </template>
              </div>

              <!-- Attachment -->
              <div v-if="message.attachment" class="mt-2">
                <a
                  :href="getAttachmentUrl(message)"
                  target="_blank"
                  :class="[
                    'inline-flex items-center gap-2 px-3 py-1.5 rounded text-sm',
                    isCurrentUser(message.sender)
                      ? 'bg-primary-700 hover:bg-primary-800'
                      : 'bg-gray-100 hover:bg-gray-200'
                  ]"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                  </svg>
                  {{ message.attachment.filename || 'Attachment' }}
                </a>
              </div>

              <!-- Timestamp -->
              <div
                :class="[
                  'text-xs mt-1',
                  isCurrentUser(message.sender) ? 'text-primary-100' : 'text-gray-500'
                ]"
              >
                {{ formatTime(message.sent_at) }}
                <span v-if="message.is_read && isCurrentUser(message.sender)" class="ml-1">✓✓</span>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- Simplified Message Composer -->
      <div v-if="selectedThreadId && (thread?.is_active || thread?.admin_override)" class="border-t bg-white">
        <SimplifiedMessageComposer
          :thread-id="selectedThreadId"
          :reply-to="replyToMessage"
          :typing-users="typingUsers"
          @message-sent="handleMessageSent"
          @cancel-reply="replyToMessage = null"
        />
      </div>

      <div v-else-if="selectedThreadId" class="border-t bg-gray-50 px-4 py-3 text-center text-sm text-gray-500">
        Messaging is disabled for this conversation
      </div>

      <!-- No Thread Selected -->
      <div v-else class="border-t bg-gray-50 px-4 py-8 text-center">
        <div class="text-4xl mb-4">💬</div>
        <p class="text-gray-600 mb-4">No conversation selected</p>
        <button
          @click="createNewThread"
          :disabled="creatingThread"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          <span v-if="creatingThread">Creating...</span>
          <span v-else>Start Conversation</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { communicationsAPI } from '@/api'
import { useAuthStore } from '@/stores/auth'
import SimplifiedMessageComposer from '@/components/communications/SimplifiedMessageComposer.vue'
import { useToast } from '@/composables/useToast'
import { parseMessageLinks } from '@/utils/messageUtils'

const props = defineProps({
  orderId: {
    type: [Number, String],
    required: true
  },
  showThreadList: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['thread-created', 'message-sent'])

const authStore = useAuthStore()
const currentUserId = authStore.user?.id
const { success: showSuccess, error: showError } = useToast()

const threads = ref([])
const messages = ref([])
const selectedThreadId = ref(null)
const thread = ref(null)
const loadingMessages = ref(false)
const creatingThread = ref(false)
const messagesContainer = ref(null)
const typingUsers = ref([])
const replyToMessage = ref(null)
const pollingInterval = ref(null)
const typingStatusInterval = ref(null)

const loadThreads = async () => {
  try {
    const response = await communicationsAPI.listThreads({ order: props.orderId })
    threads.value = response.data.results || response.data || []
    
    // Auto-select first thread if none selected
    if (!selectedThreadId.value && threads.value.length > 0) {
      selectedThreadId.value = threads.value[0].id
      thread.value = threads.value[0]
      loadMessages()
    }
  } catch (error) {
    console.error('Failed to load threads:', error)
    showError('Failed to load conversations')
  }
}

const createNewThread = async () => {
  creatingThread.value = true
  try {
    const response = await communicationsAPI.startThreadForOrder(props.orderId)
    const threadData = response.data?.thread || response.data
    
    if (threadData) {
      // Add to threads list
      threads.value = [threadData, ...threads.value]
      
      // Select the new thread
      selectedThreadId.value = threadData.id
      thread.value = threadData
      
      await loadMessages()
      showSuccess('Conversation started!')
      emit('thread-created', threadData)
    }
  } catch (error) {
    console.error('Failed to create thread:', error)
    const errorMsg = error.response?.data?.detail || 'Failed to start conversation'
    showError(errorMsg)
  } finally {
    creatingThread.value = false
  }
}

const selectThread = async (selectedThread) => {
  selectedThreadId.value = selectedThread.id
  thread.value = selectedThread
  await loadMessages()
}

const loadMessages = async (silent = false) => {
  if (!selectedThreadId.value) return
  
  if (!silent) loadingMessages.value = true
  try {
    const response = await communicationsAPI.listMessages(selectedThreadId.value)
    messages.value = (response.data.results || response.data || []).reverse() // Reverse to show oldest first
    
    // Mark all messages in thread as read when opening (not during silent refresh)
    if (!silent) {
      try {
        await communicationsAPI.markThreadAsRead(selectedThreadId.value)
        await loadThreads() // Refresh thread list to update unread counts
      } catch (error) {
        // Silently fail - marking as read is not critical
        console.warn('Failed to mark thread as read:', error)
      }
    }
    
    await nextTick()
    scrollToBottom()
  } catch (error) {
    console.error('Failed to load messages:', error)
    if (!silent) {
      showError('Failed to load messages')
    }
  } finally {
    loadingMessages.value = false
  }
}

const handleMessageSent = async () => {
  await loadMessages()
  await loadThreads() // Refresh thread list to update unread counts
  emit('message-sent')
}

const loadTypingStatus = async () => {
  if (!selectedThreadId.value) return
  try {
    const response = await communicationsAPI.getTypingStatus(selectedThreadId.value)
    typingUsers.value = response.data.typing_users || []
  } catch (error) {
    // Silently fail - typing status is not critical
  }
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    nextTick(() => {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    })
  }
}

const isCurrentUser = (sender) => {
  return sender?.id === currentUserId
}

const shouldShowAvatar = (message, index) => {
  if (index === 0) return true
  const prevMessage = messages.value[index - 1]
  return prevMessage.sender?.id !== message.sender?.id
}

const getInitials = (user) => {
  if (!user) return '?'
  const username = user.username || user.email || ''
  const words = username.split(' ')
  if (words.length >= 2) {
    return (words[0][0] + words[1][0]).toUpperCase()
  }
  return username.substring(0, 2).toUpperCase()
}

const getThreadName = (thread) => {
  if (thread.participants && thread.participants.length > 0) {
    const otherParticipants = thread.participants.filter(p => p.id !== currentUserId)
    if (otherParticipants.length > 0) {
      return otherParticipants.map(p => p.username || p.email).join(', ')
    }
  }
  return `Conversation #${thread.id}`
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

const getAttachmentUrl = (message) => {
  return `/api/v1/order-communications/communication-threads/${selectedThreadId.value}/communication-messages/${message.id}/download_attachment/`
}

const parseMessage = (text) => {
  if (!text) return []
  return parseMessageLinks(text)
}

onMounted(() => {
  loadThreads()
  
  // Start polling for new messages
  pollingInterval.value = setInterval(() => {
    if (selectedThreadId.value) {
      loadMessages(true)
    }
  }, 3000)
  
  // Start polling for typing status
  typingStatusInterval.value = setInterval(() => {
    if (selectedThreadId.value) {
      loadTypingStatus()
    }
  }, 2000)
})

watch(() => selectedThreadId.value, () => {
  if (selectedThreadId.value) {
    loadMessages()
    loadTypingStatus()
  }
})

onUnmounted(() => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
  }
  if (typingStatusInterval.value) {
    clearInterval(typingStatusInterval.value)
  }
})
</script>

<style scoped>
.simplified-order-messages {
  display: flex;
  flex-direction: column;
  height: 100%;
}
</style>


<template>
  <div class="fixed inset-0 bg-gray-100 z-50 flex items-center justify-center" @click.self="close">
    <div class="bg-white rounded-lg max-w-md w-full h-[90vh] max-h-[800px] overflow-hidden flex flex-col shadow-xl">
      <!-- Header (Chat Header Style) -->
      <div class="bg-primary-600 text-white px-4 py-3 flex items-center justify-between">
        <div class="flex items-center gap-3 flex-1 min-w-0">
          <button @click="close" class="text-white hover:text-gray-200 mr-2">
            ←
          </button>
        <div class="shrink-0">
            <div class="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-semibold">
              {{ getThreadInitials(thread) }}
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="font-semibold truncate">{{ getThreadName(thread) }}</h3>
            <p class="text-xs text-primary-100">
              <span v-if="thread.participants && thread.participants.length > 0">
                {{ thread.participants.length }} participant{{ thread.participants.length > 1 ? 's' : '' }}
              </span>
              <span v-else>Thread #{{ thread.id }}</span>
            </p>
          </div>
        </div>
      </div>

      <!-- Messages Area (Chat Bubbles) -->
      <div 
        ref="messagesContainer"
        class="flex-1 overflow-y-auto bg-gray-50 px-4 py-4 space-y-2"
      >
        <div v-if="messagesLoading" class="flex items-center justify-center py-8">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
        </div>

        <div v-else-if="messages.length === 0" class="text-center py-12 text-gray-500">
          <div class="text-4xl mb-4">💬</div>
          <p>No messages yet</p>
          <p class="text-sm mt-2">Start the conversation!</p>
        </div>

        <template v-else>
          <EnhancedMessageBubble
            v-for="message in messages"
            :key="message.id"
            :message="message"
            :thread-id="thread.id"
            @reaction-updated="loadMessages"
            @reply="handleReplyToMessage"
            @attachment-downloaded="loadMessages"
          />
        </template>
      </div>

      <!-- Enhanced Input Area -->
      <div v-if="thread.is_active || thread.admin_override" class="border-t bg-white dark:bg-gray-800">
        <!-- Recipient Selection -->
        <div class="px-4 pt-3 pb-2 border-b border-gray-200 dark:border-gray-700">
          <select 
            v-model="messageForm.recipient" 
            required 
            class="w-full text-sm border rounded-lg px-3 py-2 bg-gray-50 dark:bg-gray-700 focus:bg-white dark:focus:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-primary-500 text-gray-900 dark:text-white"
            :disabled="loadingRecipients || sending"
          >
            <option value="">Select recipient...</option>
            <option
              v-for="recipient in availableRecipients"
              :key="recipient.id"
              :value="recipient.id"
            >
              {{ recipient.username || recipient.email }} 
              <span v-if="recipient.role">({{ recipient.role }})</span>
            </option>
          </select>
          <p v-if="loadingRecipients" class="text-xs text-gray-500 dark:text-gray-400 mt-1">Loading recipients...</p>
        </div>

        <!-- Simplified Message Composer (No recipient selection needed) -->
        <SimplifiedMessageComposer
          :thread-id="thread.id"
          :reply-to="replyToMessage"
          :typing-users="typingUsers"
          @message-sent="handleMessageSent"
          @cancel-reply="replyToMessage = null"
        />

        <!-- Error Message -->
        <div v-if="sendError" class="px-4 pb-3 text-xs text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 p-2 rounded">
          {{ sendError }}
        </div>
      </div>

      <div v-else class="border-t bg-gray-50 px-4 py-3 text-center text-sm text-gray-500">
        Messaging is disabled for this thread
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { communicationsAPI } from '@/api'
import { useAuthStore } from '@/stores/auth'
import RichTextEditor from '@/components/common/RichTextEditor.vue'
import EnhancedMessageBubble from '@/components/communications/EnhancedMessageBubble.vue'
import SimplifiedMessageComposer from '@/components/communications/SimplifiedMessageComposer.vue'

const props = defineProps({
  thread: {
    type: Object,
    required: true
  },
  orderId: {
    type: [Number, String],
    required: true
  }
})

const emit = defineEmits(['close', 'thread-updated'])

const authStore = useAuthStore()
const currentUserId = authStore.user?.id

const messages = ref([])
const messagesLoading = ref(false)
const sending = ref(false)
const messagesContainer = ref(null)
const pollingInterval = ref(null)
const lastMessageId = ref(null)
const typingUsers = ref([])
const typingStatusInterval = ref(null)
const replyToMessage = ref(null)

const loadMessages = async (silent = false) => {
  // Mark messages as read when loading
  if (!silent) {
    await markMessagesAsRead()
  }
  if (!silent) messagesLoading.value = true
  try {
    const res = await communicationsAPI.listMessages(props.thread.id)
    const newMessages = res.data.results || res.data || []
    
    // Check if we have new messages
    if (newMessages.length > 0 && lastMessageId.value) {
      const hasNew = newMessages.some(m => m.id > lastMessageId.value)
      if (hasNew && silent) {
        // Auto-scroll only if user is near bottom
        const isNearBottom = messagesContainer.value.scrollHeight - messagesContainer.value.scrollTop < messagesContainer.value.clientHeight + 100
        messages.value = newMessages
        if (isNearBottom) {
          await nextTick()
          scrollToBottom()
        }
      } else {
        messages.value = newMessages
        await nextTick()
        scrollToBottom()
      }
    } else {
      messages.value = newMessages
      await nextTick()
      scrollToBottom()
    }
    
    // Update last message ID
    if (messages.value.length > 0) {
      lastMessageId.value = Math.max(...messages.value.map(m => m.id))
    }
  } catch (error) {
    console.error('Failed to load messages:', error)
  } finally {
    messagesLoading.value = false
  }
}

// Simplified - no need to load recipients or handle file selection manually
// The SimplifiedMessageComposer handles everything

const handleReplyToMessage = (message) => {
  replyToMessage.value = message
}

const handleMessageSent = async () => {
  await loadMessages()
  emit('thread-updated')
  replyToMessage.value = null
  sendError.value = ''
}

// Removed - SimplifiedMessageComposer handles files internally

const loadTypingStatus = async () => {
  if (!props.thread?.id) return
  try {
    const response = await communicationsAPI.getTypingStatus(props.thread.id)
    typingUsers.value = response.data.typing_users || []
  } catch (error) {
    // Silently fail - typing status is not critical
  }
}

const markMessagesAsRead = async () => {
  // Mark all unread messages as read
  const unreadMessages = messages.value.filter(m => 
    !m.is_read && m.recipient?.id === currentUserId
  )
  
  for (const message of unreadMessages) {
    try {
      await communicationsAPI.markMessageAsRead(props.thread.id, message.id)
    } catch (error) {
      // Silently fail
    }
  }
}

const repliedToMessage = (messageId) => {
  return messages.value.find(m => m.id === messageId)
}

const getRepliedToSender = (messageId) => {
  const msg = repliedToMessage(messageId)
  return msg?.sender?.username || 'Unknown'
}

const getRepliedToContent = (messageId) => {
  const msg = repliedToMessage(messageId)
  if (!msg) return 'Message not found'
  if (msg.attachment) return `📎 ${msg.attachment.filename}`
  return msg.message || 'No content'
}

const downloadAttachment = async (message) => {
  if (!message.attachment) return
  try {
    const url = `/api/v1/order-communications/communication-threads/${props.thread.id}/communication-messages/${message.id}/download_attachment/`
    window.open(url, '_blank')
  } catch (error) {
    console.error('Failed to download attachment:', error)
    alert('Failed to download file')
  }
}

const getAttachmentUrl = (message) => {
  if (!message.attachment) return '#'
  return message.attachment.preview_url || 
         `/api/v1/order-communications/communication-threads/${props.thread.id}/communication-messages/${message.id}/download_attachment/`
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const openImagePreview = (url) => {
  window.open(url, '_blank')
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
  // Show avatar if it's the first message from this sender, or if previous message is from different sender
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
  return `Thread #${thread.id}`
}

const getThreadInitials = (thread) => {
  const name = getThreadName(thread)
  const words = name.split(' ')
  if (words.length >= 2) {
    return (words[0][0] + words[1][0]).toUpperCase()
  }
  return name.substring(0, 2).toUpperCase()
}

const formatTime = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
}

const close = () => {
  emit('close')
}

onMounted(() => {
  loadMessages()
  loadTypingStatus()
  
  // Start polling for new messages every 3 seconds
  pollingInterval.value = setInterval(() => {
    if (props.thread.id) {
      loadMessages(true) // Silent update
    }
  }, 3000)
  
  // Start polling for typing status every 2 seconds
  typingStatusInterval.value = setInterval(() => {
    if (props.thread.id) {
      loadTypingStatus()
    }
  }, 2000)
})

watch(() => props.thread.id, () => {
  // Clear old intervals
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
  }
  if (typingStatusInterval.value) {
    clearInterval(typingStatusInterval.value)
  }
  
  loadMessages()
  loadTypingStatus()
  lastMessageId.value = null
  
  // Start new polling
  pollingInterval.value = setInterval(() => {
    if (props.thread.id) {
      loadMessages(true)
    }
  }, 3000)
  
  typingStatusInterval.value = setInterval(() => {
    if (props.thread.id) {
      loadTypingStatus()
    }
  }, 2000)
})

// Cleanup on unmount
onUnmounted(() => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
  }
  if (typingStatusInterval.value) {
    clearInterval(typingStatusInterval.value)
  }
})

// Auto-scroll when new messages arrive (only if near bottom)
watch(() => messages.value.length, () => {
  const isNearBottom = messagesContainer.value && 
    (messagesContainer.value.scrollHeight - messagesContainer.value.scrollTop < messagesContainer.value.clientHeight + 100)
  if (isNearBottom) {
    nextTick(() => scrollToBottom())
  }
})
</script>

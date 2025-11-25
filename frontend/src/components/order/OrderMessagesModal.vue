<template>
  <div class="fixed inset-0 bg-gray-100 z-50 flex items-center justify-center" @click.self="close">
    <div class="bg-white rounded-lg max-w-md w-full h-[90vh] max-h-[800px] overflow-hidden flex flex-col shadow-xl">
      <!-- Header (Chat Header Style) -->
      <div class="bg-primary-600 text-white px-4 py-3 flex items-center justify-between">
        <div class="flex items-center gap-3 flex-1 min-w-0">
          <button @click="close" class="text-white hover:text-gray-200 mr-2">
            ←
          </button>
          <div class="flex-shrink-0">
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
          <div
            v-for="(message, index) in messages"
            :key="message.id"
            class="flex"
            :class="isCurrentUser(message.sender) ? 'justify-end' : 'justify-start'"
          >
            <div class="flex items-end gap-2 max-w-[75%]" :class="isCurrentUser(message.sender) ? 'flex-row-reverse' : 'flex-row'">
              <!-- Avatar (only for received messages) -->
              <div v-if="!isCurrentUser(message.sender) && shouldShowAvatar(message, index)" class="flex-shrink-0 w-6 h-6 rounded-full bg-gray-300 flex items-center justify-center text-xs font-semibold text-gray-600">
                {{ getInitials(message.sender) }}
              </div>
              
              <!-- Message Bubble -->
              <div
                class="rounded-2xl px-4 py-2 shadow-sm cursor-pointer hover:opacity-90 transition-opacity"
                :class="isCurrentUser(message.sender) 
                  ? 'bg-primary-600 text-white rounded-br-sm' 
                  : 'bg-white text-gray-900 rounded-bl-sm border border-gray-200'"
                @click="replyToMessage(message)"
              >
                <!-- Reply indicator with quoted message -->
                <div v-if="message.reply_to_id && repliedToMessage(message.reply_to_id)" class="mb-2 p-2 rounded border-l-2 bg-opacity-20 text-xs" :class="isCurrentUser(message.sender) ? 'bg-white bg-opacity-20 border-white' : 'bg-gray-200 border-gray-400'">
                  <div class="font-medium opacity-75 mb-1">
                    Replying to {{ getRepliedToSender(message.reply_to_id) }}
                  </div>
                  <div class="opacity-75 truncate">
                    {{ getRepliedToContent(message.reply_to_id) }}
                  </div>
                </div>

                <!-- Message content -->
                <div class="text-sm whitespace-pre-wrap break-words">{{ message.message }}</div>

                <!-- Attachment -->
                <div v-if="message.attachment" class="mt-2">
                  <div v-if="message.attachment.is_image && message.attachment.preview_url" class="mb-2">
                    <img 
                      :src="message.attachment.preview_url" 
                      :alt="message.attachment.filename"
                      class="max-w-full rounded-lg cursor-pointer hover:opacity-90"
                      @click="openImagePreview(message.attachment.preview_url)"
                    />
                  </div>
                  <a
                    :href="getAttachmentUrl(message)"
                    target="_blank"
                    class="text-xs underline flex items-center gap-1 hover:opacity-80"
                    :class="isCurrentUser(message.sender) ? 'text-primary-100' : 'text-primary-600'"
                    @click.prevent="downloadAttachment(message)"
                  >
                    📎 {{ message.attachment.filename }}
                    <span v-if="message.attachment.filesize" class="opacity-75">
                      ({{ formatFileSize(message.attachment.filesize) }})
                    </span>
                  </a>
                </div>

                <!-- Timestamp and read status -->
                <div class="flex items-center justify-end gap-1 mt-1">
                  <span 
                    class="text-xs opacity-75"
                    :class="isCurrentUser(message.sender) ? 'text-primary-100' : 'text-gray-500'"
                  >
                    {{ formatTime(message.sent_at) }}
                  </span>
                  <span v-if="isCurrentUser(message.sender)" class="text-xs">
                    <span v-if="message.is_read" class="text-blue-300">✓✓</span>
                    <span v-else class="text-gray-300">✓</span>
                  </span>
                </div>

                <!-- Flagged indicator -->
                <div v-if="message.is_flagged" class="mt-1 text-xs opacity-75">
                  ⚠️ Flagged for review
                </div>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- Input Area (Sticky at bottom) -->
      <div v-if="thread.is_active || thread.admin_override" class="border-t bg-white px-4 py-3">
        <form @submit.prevent="sendMessage" class="space-y-2">
          <!-- Recipient Selection -->
          <div>
            <select 
              v-model="messageForm.recipient" 
              required 
              class="w-full text-sm border rounded-lg px-3 py-2 bg-gray-50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-primary-500"
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
            <p v-if="loadingRecipients" class="text-xs text-gray-500 mt-1">Loading recipients...</p>
          </div>

          <!-- Reply Preview -->
          <div v-if="messageForm.reply_to" class="p-2 bg-gray-100 rounded-lg border-l-2 border-primary-500 text-xs">
            <div class="flex items-start justify-between">
              <div class="flex-1 min-w-0">
                <div class="font-medium text-gray-700 mb-1">
                  Replying to {{ getRepliedToSender(messageForm.reply_to) }}
                </div>
                <div class="text-gray-600 truncate">
                  {{ getRepliedToContent(messageForm.reply_to) }}
                </div>
              </div>
              <button
                @click="messageForm.reply_to = null"
                class="ml-2 text-gray-500 hover:text-gray-700"
                type="button"
              >
                ✕
              </button>
            </div>
          </div>

          <!-- Selected File Preview -->
          <div v-if="selectedFile" class="p-2 bg-gray-100 rounded-lg text-xs flex items-center justify-between">
            <div class="flex items-center gap-2 flex-1 min-w-0">
              <span class="text-lg">📎</span>
              <span class="truncate">{{ selectedFile.name }}</span>
              <span v-if="selectedFile.size" class="text-gray-500">({{ formatFileSize(selectedFile.size) }})</span>
            </div>
            <button
              @click="selectedFile = null"
              class="ml-2 text-gray-500 hover:text-gray-700"
              type="button"
            >
              ✕
            </button>
          </div>

          <!-- Message Input -->
          <div class="flex items-end gap-2">
            <input
              ref="fileInput"
              type="file"
              class="hidden"
              @change="handleFileSelect"
              :disabled="sending"
            />
            <button
              type="button"
              @click="$refs.fileInput?.click()"
              class="flex-shrink-0 w-10 h-10 bg-gray-200 text-gray-700 rounded-full hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-colors"
              :disabled="sending"
              title="Attach file"
            >
              📎
            </button>
            <div class="flex-1">
              <RichTextEditor
                v-model="messageForm.message"
                :required="!selectedFile"
                placeholder="Type a message..."
                toolbar="minimal"
                height="80px"
                :allow-images="true"
                :disabled="sending"
                :strip-html="true"
              />
            </div>
            <button
              type="submit"
              :disabled="sending || !messageForm.recipient || (!messageForm.message.trim() && !selectedFile)"
              class="flex-shrink-0 w-10 h-10 bg-primary-600 text-white rounded-full hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center transition-colors"
            >
              <span v-if="sending" class="animate-spin">⏳</span>
              <span v-else>➤</span>
            </button>
          </div>

          <!-- Error Message -->
          <div v-if="sendError" class="text-xs text-red-600 bg-red-50 p-2 rounded">
            {{ sendError }}
          </div>
        </form>
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
const availableRecipients = ref([])
const loadingRecipients = ref(false)
const sendError = ref('')
const selectedFile = ref(null)
const fileInput = ref(null)
const pollingInterval = ref(null)
const lastMessageId = ref(null)

const messageForm = ref({
  recipient: '',
  message: '',
  reply_to: null,
  message_type: 'text',
})

const loadMessages = async (silent = false) => {
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

const loadAvailableRecipients = async () => {
  loadingRecipients.value = true
  try {
    const res = await communicationsAPI.getAvailableRecipients(props.thread.id)
    availableRecipients.value = Array.isArray(res.data) ? res.data : []
  } catch (error) {
    console.error('Failed to load recipients:', error)
    availableRecipients.value = props.thread.participants
      ?.filter(p => p.id !== currentUserId)
      .map(p => ({
        id: p.id,
        username: p.username,
        email: p.email,
        role: p.role,
      })) || []
  } finally {
    loadingRecipients.value = false
  }
}

const handleFileSelect = (event) => {
  const file = event.target.files?.[0]
  if (file) {
    selectedFile.value = file
    sendError.value = ''
  }
}

const sendMessage = async () => {
  if (!messageForm.value.message.trim() && !selectedFile.value) {
    sendError.value = 'Please enter a message or attach a file.'
    return
  }
  
  if (!messageForm.value.recipient) {
    sendError.value = 'Please select a recipient.'
    return
  }

  sending.value = true
  sendError.value = ''
  
  try {
    // If file is selected, upload as attachment
    if (selectedFile.value) {
      const formData = new FormData()
      formData.append('file', selectedFile.value)
      formData.append('thread_id', props.thread.id)
      formData.append('recipient_id', messageForm.value.recipient)
      
      if (messageForm.value.message.trim()) {
        // If there's a message, send it separately after attachment
        await communicationsAPI.uploadAttachment(formData)
        // Then send the text message
        const data = {
          recipient: messageForm.value.recipient,
          message: messageForm.value.message,
          message_type: 'text',
        }
        if (messageForm.value.reply_to) {
          data.reply_to = messageForm.value.reply_to
        }
        await communicationsAPI.sendMessage(props.thread.id, data)
      } else {
        await communicationsAPI.uploadAttachment(formData)
      }
    } else {
      // Regular text message
      const data = {
        recipient: messageForm.value.recipient,
        message: messageForm.value.message,
        message_type: messageForm.value.message_type,
      }
      
      if (messageForm.value.reply_to) {
        data.reply_to = messageForm.value.reply_to
      }

      await communicationsAPI.sendMessage(props.thread.id, data)
    }
    
    // Reset form
    messageForm.value.message = ''
    messageForm.value.reply_to = null
    selectedFile.value = null
    if (fileInput.value) {
      fileInput.value.value = ''
    }
    
    await Promise.all([loadMessages(), loadAvailableRecipients()])
    emit('thread-updated')
  } catch (error) {
    console.error('Failed to send message:', error)
    sendError.value = error.response?.data?.recipient?.[0] || 
                     error.response?.data?.detail || 
                     error.response?.data?.error ||
                     error.message || 'Failed to send message'
  } finally {
    sending.value = false
  }
}

const replyToMessage = (message) => {
  messageForm.value.reply_to = message.id
  // Scroll to input
  nextTick(() => {
    const textarea = document.querySelector('textarea')
    if (textarea) textarea.focus()
  })
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
  loadAvailableRecipients()
  
  // Start polling for new messages every 3 seconds
  pollingInterval.value = setInterval(() => {
    if (props.thread.id) {
      loadMessages(true) // Silent update
    }
  }, 3000)
})

watch(() => props.thread.id, () => {
  // Clear old interval
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
  }
  
  loadMessages()
  loadAvailableRecipients()
  lastMessageId.value = null
  
  // Start new polling
  pollingInterval.value = setInterval(() => {
    if (props.thread.id) {
      loadMessages(true)
    }
  }, 3000)
})

// Cleanup on unmount
onUnmounted(() => {
  if (pollingInterval.value) {
    clearInterval(pollingInterval.value)
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

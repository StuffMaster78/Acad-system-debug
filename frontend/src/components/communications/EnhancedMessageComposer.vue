<template>
  <div class="message-composer border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-4">
    <!-- Typing Indicator -->
    <div v-if="typingUsers.length > 0" class="mb-2 text-sm text-gray-500 dark:text-gray-400 italic">
      <span v-for="(user, index) in typingUsers" :key="user.id">
        {{ user.username }}<span v-if="index < typingUsers.length - 1">, </span>
      </span>
      <span v-if="typingUsers.length === 1"> is typing...</span>
      <span v-else> are typing...</span>
    </div>

    <!-- File Preview -->
    <div v-if="selectedFiles.length > 0" class="mb-3 flex flex-wrap gap-2">
      <div
        v-for="(file, index) in selectedFiles"
        :key="index"
        class="flex items-center gap-2 p-2 bg-gray-100 dark:bg-gray-700 rounded-lg"
      >
        <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
        </svg>
        <span class="text-sm truncate max-w-[200px]">{{ file.name }}</span>
        <button
          @click="removeFile(index)"
          class="text-red-500 hover:text-red-700"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Reply Preview -->
    <div v-if="replyTo" class="mb-3 p-3 bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500 rounded">
      <div class="flex items-center justify-between">
        <div class="flex-1 min-w-0">
          <div class="text-xs font-medium text-blue-700 dark:text-blue-300 mb-1">
            Replying to {{ replyTo.sender_display_name || replyTo.sender?.username }}
          </div>
          <div class="text-sm text-blue-600 dark:text-blue-400 truncate">
            {{ replyTo.message }}
          </div>
        </div>
        <button
          @click="$emit('cancel-reply')"
          class="text-blue-500 hover:text-blue-700 ml-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Composer Area -->
    <div
      :class="[
        'flex items-end gap-2 p-3 border-2 rounded-lg transition-colors',
        isDragging
          ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
          : 'border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-900'
      ]"
      @drop="handleDrop"
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
      @dragenter.prevent
    >
      <!-- File Upload Button -->
      <button
        @click="triggerFileInput"
        class="shrink-0 p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
        title="Attach file"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
        </svg>
      </button>

      <!-- Text Input -->
      <textarea
        ref="messageInput"
        v-model="messageText"
        @input="handleTyping"
        @keydown.enter.exact.prevent="handleEnter"
        @keydown.enter.shift.exact="handleShiftEnter"
        :placeholder="replyTo ? 'Type your reply...' : 'Type a message...'"
        rows="1"
        class="flex-1 resize-none border-0 bg-transparent focus:outline-none focus:ring-0 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
        style="max-height: 120px;"
      />

      <!-- Send Button -->
      <button
        @click="sendMessage"
        :disabled="!canSend"
        :class="[
          'shrink-0 p-2 rounded-lg transition-colors',
          canSend
            ? 'bg-primary-600 text-white hover:bg-primary-700'
            : 'bg-gray-300 dark:bg-gray-600 text-gray-500 cursor-not-allowed'
        ]"
        title="Send message (Enter)"
      >
        <svg v-if="!sending" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
        </svg>
        <svg v-else class="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </button>
    </div>

    <!-- Hidden File Input -->
    <input
      ref="fileInput"
      type="file"
      multiple
      class="hidden"
      @change="handleFileSelect"
    />

    <!-- Error Message -->
    <div v-if="error" class="mt-2 p-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg text-sm text-red-600 dark:text-red-400">
      {{ error }}
    </div>

    <!-- Drag & Drop Overlay -->
    <div
      v-if="isDragging"
      class="fixed inset-0 bg-blue-500 bg-opacity-10 z-50 flex items-center justify-center pointer-events-none"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg p-8 shadow-xl border-2 border-dashed border-blue-500">
        <div class="text-center">
          <svg class="w-16 h-16 mx-auto text-blue-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
          <p class="text-lg font-semibold text-gray-900 dark:text-white">Drop files here to attach</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import { communicationsAPI } from '@/api'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  threadId: {
    type: [Number, String],
    required: true
  },
  recipientId: {
    type: [Number, String],
    required: false,
    default: null
  },
  replyTo: {
    type: Object,
    default: null
  },
  typingUsers: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['message-sent', 'reply-cancelled', 'files-selected'])

const { error: showError } = useToast()

const messageText = ref('')
const selectedFiles = ref([])
const fileInput = ref(null)
const messageInput = ref(null)
const isDragging = ref(false)
const typingTimeout = ref(null)
const sending = ref(false)
const error = ref('')

const canSend = computed(() => {
  return messageText.value.trim().length > 0 || selectedFiles.value.length > 0
})

const handleTyping = () => {
  // Send typing indicator
  if (messageText.value.trim().length > 0) {
    communicationsAPI.setTyping(props.threadId).catch(() => {})
  }

  // Clear existing timeout
  if (typingTimeout.value) {
    clearTimeout(typingTimeout.value)
  }

  // Auto-resize textarea
  if (messageInput.value) {
    messageInput.value.style.height = 'auto'
    messageInput.value.style.height = `${Math.min(messageInput.value.scrollHeight, 120)}px`
  }
  
  // Clear error when user starts typing
  if (error.value) {
    error.value = ''
  }
}

const handleEnter = () => {
  if (canSend.value) {
    sendMessage()
  }
}

const handleShiftEnter = () => {
  // Allow new line with Shift+Enter
  messageText.value += '\n'
  handleTyping()
}

const handleDrop = (event) => {
  event.preventDefault()
  isDragging.value = false

  const files = Array.from(event.dataTransfer.files)
  if (files.length > 0) {
    addFiles(files)
  }
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  if (files.length > 0) {
    addFiles(files)
  }
  // Reset input
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const addFiles = (files) => {
  // Validate file sizes (max 10MB per file)
  const maxSize = 10 * 1024 * 1024
  const validFiles = files.filter(file => {
    if (file.size > maxSize) {
      alert(`File ${file.name} is too large. Maximum size is 10MB.`)
      return false
    }
    return true
  })

  selectedFiles.value.push(...validFiles)
  emit('files-selected', validFiles)
}

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
}

const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

const sendMessage = async () => {
  if (!canSend.value) return

  sending.value = true
  error.value = ''

  try {
    const message = messageText.value.trim()
    const attachment = selectedFiles.value.length > 0 ? selectedFiles.value[0] : null
    const replyToId = props.replyTo?.id || null

    // Always try to get explicit recipient first
    let recipientToUse = props.recipientId
    
    // If no recipient provided, fetch available recipients
    if (!recipientToUse) {
      try {
        const response = await communicationsAPI.getAvailableRecipients(props.threadId)
        const recipients = response.data?.recipients || []
        if (recipients.length > 0) {
          // If replying, prefer the original sender
          if (replyToId && props.replyTo?.sender?.id) {
            const replySender = recipients.find(r => 
              (typeof r === 'object' ? r.id : r) === props.replyTo.sender.id
            )
            if (replySender) {
              recipientToUse = typeof replySender === 'object' ? replySender.id : replySender
            }
          }
          
          // Otherwise use first recipient
          if (!recipientToUse) {
            recipientToUse = typeof recipients[0] === 'object' ? recipients[0].id : recipients[0]
          }
        }
      } catch (error) {
        console.warn('Failed to load recipients, falling back to auto-detection:', error)
      }
    }
    
    // If we have an explicit recipient, use the regular sendMessage endpoint
    // Otherwise, fall back to sendMessageSimple for auto-detection
    if (recipientToUse) {
      // Use explicit recipient to ensure message is received
      if (selectedFiles.value.length > 1) {
        // Send first file with message if any
        await communicationsAPI.sendMessage(props.threadId, {
          recipient: recipientToUse,
          message: message || '📎 File attachments',
          attachment: selectedFiles.value[0],
          reply_to: replyToId,
          message_type: 'file'
        })
        
        // Send remaining files
        for (let i = 1; i < selectedFiles.value.length; i++) {
          await communicationsAPI.sendMessage(props.threadId, {
            recipient: recipientToUse,
            message: '',
            attachment: selectedFiles.value[i],
            message_type: 'file'
          })
        }
      } else {
        // Single file or text only
        await communicationsAPI.sendMessage(props.threadId, {
          recipient: recipientToUse,
          message: message || '📎 File attachment',
          attachment: attachment,
          reply_to: replyToId,
          message_type: attachment ? 'file' : 'text'
        })
      }
    } else {
      // Fall back to auto-detection when no explicit recipient
      if (selectedFiles.value.length > 1) {
        // Send first file with message if any
        await communicationsAPI.sendMessageSimple(
          props.threadId,
          message || '📎 File attachments',
          selectedFiles.value[0],
          replyToId
        )
        
        // Send remaining files
        for (let i = 1; i < selectedFiles.value.length; i++) {
          await communicationsAPI.sendMessageSimple(
            props.threadId,
            '',
            selectedFiles.value[i],
            null
          )
        }
      } else {
        // Single file or text only
        await communicationsAPI.sendMessageSimple(
          props.threadId,
          message,
          attachment,
          replyToId
        )
      }
    }

    // Clear form
    messageText.value = ''
    selectedFiles.value = []
    if (messageInput.value) {
      messageInput.value.style.height = 'auto'
    }
    
    // Clear reply if was replying
    if (props.replyTo) {
      emit('cancel-reply')
    }

    // Emit event
    emit('message-sent')
  } catch (err) {
    console.error('Failed to send message:', err)
    const errorMsg = err.response?.data?.detail || 
                    err.response?.data?.error || 
                    err.message || 
                    'Failed to send message. Please try again.'
    error.value = errorMsg
    showError(errorMsg)
  } finally {
    sending.value = false
  }
}

watch(() => props.replyTo, (newVal) => {
  if (newVal && messageInput.value) {
    messageInput.value.focus()
  }
})

onUnmounted(() => {
  if (typingTimeout.value) {
    clearTimeout(typingTimeout.value)
  }
})
</script>

<style scoped>
.message-composer textarea {
  scrollbar-width: thin;
  scrollbar-color: rgba(156, 163, 175, 0.5) transparent;
}

.message-composer textarea::-webkit-scrollbar {
  width: 6px;
}

.message-composer textarea::-webkit-scrollbar-track {
  background: transparent;
}

.message-composer textarea::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 3px;
}
</style>


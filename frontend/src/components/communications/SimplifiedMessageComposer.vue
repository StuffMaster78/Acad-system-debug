<template>
  <div class="simplified-message-composer bg-white border-t border-gray-200 p-4">
    <!-- Reply Preview -->
    <div v-if="replyTo" class="mb-3 p-3 bg-blue-50 border-l-4 border-blue-500 rounded-lg">
      <div class="flex items-center justify-between">
        <div class="flex-1 min-w-0">
          <div class="text-xs font-medium text-blue-700 mb-1">
            Replying to {{ replyTo.sender_display_name || replyTo.sender?.username || 'User' }}
          </div>
          <div class="text-sm text-blue-600 truncate">
            {{ replyTo.message || '📎 File attachment' }}
          </div>
        </div>
        <button
          @click="$emit('cancel-reply')"
          class="text-blue-500 hover:text-blue-700 ml-2 flex-shrink-0"
          title="Cancel reply"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- File Preview -->
    <div v-if="selectedFiles.length > 0" class="mb-3 flex flex-wrap gap-2">
      <div
        v-for="(file, index) in selectedFiles"
        :key="index"
        class="flex items-center gap-2 p-2 bg-gray-100 rounded-lg"
      >
        <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
        </svg>
        <span class="text-sm truncate max-w-[200px]">{{ file.name }}</span>
        <span class="text-xs text-gray-500">({{ formatFileSize(file.size) }})</span>
        <button
          @click="removeFile(index)"
          class="text-red-500 hover:text-red-700 flex-shrink-0"
          title="Remove file"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Typing Indicator -->
    <div v-if="typingUsers.length > 0" class="mb-2 text-sm text-gray-500 italic">
      <span v-for="(user, index) in typingUsers" :key="user.id">
        {{ user.username }}<span v-if="index < typingUsers.length - 1">, </span>
      </span>
      <span v-if="typingUsers.length === 1"> is typing...</span>
      <span v-else> are typing...</span>
    </div>

    <!-- Composer Area -->
    <div class="flex items-end gap-2">
      <!-- File Upload Button -->
      <button
        @click="triggerFileInput"
        class="flex-shrink-0 p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
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
        class="flex-1 resize-none border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-gray-900 placeholder-gray-400"
        style="max-height: 120px; min-height: 40px;"
      />

      <!-- Send Button -->
      <button
        @click="sendMessage"
        :disabled="!canSend || sending"
        :class="[
          'flex-shrink-0 px-4 py-2 rounded-lg font-medium transition-colors',
          canSend && !sending
            ? 'bg-primary-600 text-white hover:bg-primary-700'
            : 'bg-gray-300 text-gray-500 cursor-not-allowed'
        ]"
        title="Send message (Enter)"
      >
        <span v-if="sending" class="flex items-center gap-2">
          <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Sending...
        </span>
        <span v-else class="flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
          </svg>
          Send
        </span>
      </button>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="mt-2 p-2 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
      {{ error }}
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="mt-2 p-2 bg-green-50 border border-green-200 rounded-lg text-sm text-green-600">
      {{ successMessage }}
    </div>

    <!-- Hidden File Input -->
    <input
      ref="fileInput"
      type="file"
      multiple
      class="hidden"
      @change="handleFileSelect"
      accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted, nextTick } from 'vue'
import { communicationsAPI } from '@/api'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  threadId: {
    type: [Number, String],
    required: true
  },
  replyTo: {
    type: Object,
    default: null
  },
  typingUsers: {
    type: Array,
    default: () => []
  },
  autoFocus: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['message-sent', 'cancel-reply'])

const { success: showSuccess, error: showError } = useToast()

const messageText = ref('')
const selectedFiles = ref([])
const fileInput = ref(null)
const messageInput = ref(null)
const sending = ref(false)
const error = ref('')
const successMessage = ref('')
const typingTimeout = ref(null)

const canSend = computed(() => {
  return (messageText.value.trim().length > 0 || selectedFiles.value.length > 0) && !sending.value
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
      showError(`File ${file.name} is too large. Maximum size is 10MB.`)
      return false
    }
    return true
  })

  selectedFiles.value.push(...validFiles)
  error.value = ''
}

const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
}

const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

const sendMessage = async () => {
  if (!canSend.value) return

  sending.value = true
  error.value = ''
  successMessage.value = ''

  try {
    // Use simplified endpoint that auto-detects recipient
    const message = messageText.value.trim()
    const attachment = selectedFiles.value.length > 0 ? selectedFiles.value[0] : null
    const replyToId = props.replyTo?.id || null

    // If multiple files, send them one by one
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

    // Clear form
    messageText.value = ''
    selectedFiles.value = []
    if (messageInput.value) {
      messageInput.value.style.height = 'auto'
    }
    
    // Show success
    successMessage.value = 'Message sent successfully!'
    setTimeout(() => {
      successMessage.value = ''
    }, 3000)

    // Emit event
    emit('message-sent')
    
    // Clear reply if was replying
    if (props.replyTo) {
      emit('cancel-reply')
    }
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

// Auto-focus on mount
watch(() => props.threadId, () => {
  nextTick(() => {
    if (props.autoFocus && messageInput.value) {
      messageInput.value.focus()
    }
  })
}, { immediate: true })

watch(() => props.replyTo, (newVal) => {
  if (newVal && messageInput.value) {
    nextTick(() => {
      messageInput.value.focus()
    })
  }
})

onUnmounted(() => {
  if (typingTimeout.value) {
    clearTimeout(typingTimeout.value)
  }
})
</script>

<style scoped>
.simplified-message-composer textarea {
  scrollbar-width: thin;
  scrollbar-color: rgba(156, 163, 175, 0.5) transparent;
}

.simplified-message-composer textarea::-webkit-scrollbar {
  width: 6px;
}

.simplified-message-composer textarea::-webkit-scrollbar-track {
  background: transparent;
}

.simplified-message-composer textarea::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 3px;
}
</style>


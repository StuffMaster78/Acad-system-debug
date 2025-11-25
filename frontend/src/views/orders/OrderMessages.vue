<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Order Messages</h1>
        <p class="mt-2 text-gray-600">Communicate with {{ order?.writer?.username || 'writer' }} about this order</p>
      </div>
      <router-link
        :to="`/orders/${orderId}`"
        class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
      >
        ← Back to Order
      </router-link>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !thread" class="card p-12">
      <div class="flex items-center justify-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <p class="ml-3 text-gray-600">Loading messages...</p>
      </div>
    </div>

    <!-- No Thread State -->
    <div v-else-if="!thread && !loading" class="card p-12">
      <div class="text-center mb-6">
        <p class="text-gray-500 text-lg mb-2">No conversation thread found for this order</p>
        <p class="text-gray-400 text-sm">Start a conversation to communicate about this order</p>
      </div>
      
      <div v-if="availableRecipients.length > 1" class="mb-4">
        <label class="block text-sm font-medium text-gray-700 mb-2">
          Select Recipient <span class="text-red-500">*</span>
        </label>
        <select
          v-model="messageForm.recipient_id"
          class="w-full max-w-md mx-auto border rounded-lg px-4 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
        >
          <option value="">Select a recipient...</option>
          <option v-for="recipient in availableRecipients" :key="recipient.id" :value="recipient.id">
            {{ recipient.username }} ({{ recipient.role }})
          </option>
        </select>
      </div>
      
      <div class="text-center">
        <button
          @click="createThread"
          :disabled="creatingThread || (availableRecipients.length > 1 && !messageForm.recipient_id)"
          class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ creatingThread ? 'Creating...' : 'Start Conversation' }}
        </button>
      </div>
    </div>

    <!-- Messages Thread -->
    <div v-else-if="thread" class="space-y-4">
      <!-- Thread Info -->
      <div class="card p-4 bg-blue-50 border border-blue-200">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-semibold text-blue-900">Conversation Thread</h3>
            <p class="text-sm text-blue-700 mt-1">
              Participants: {{ thread.participants?.map(p => p.username || p).join(', ') || 'N/A' }}
            </p>
          </div>
          <span
            v-if="thread.unread_count > 0"
            class="px-3 py-1 bg-red-500 text-white rounded-full text-sm font-medium"
          >
            {{ thread.unread_count }} unread
          </span>
        </div>
      </div>

      <!-- Messages List -->
      <div class="card p-4">
        <div
          ref="messagesContainer"
          class="space-y-4 max-h-96 overflow-y-auto mb-4"
        >
          <div v-if="loadingMessages" class="text-center py-4">
            <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mx-auto"></div>
            <p class="mt-2 text-sm text-gray-500">Loading messages...</p>
          </div>
          
          <div v-else-if="messages.length === 0" class="text-center py-8 text-gray-500">
            <p>No messages yet. Start the conversation!</p>
          </div>

          <div
            v-for="message in messages"
            :key="message.id"
            class="flex"
            :class="message.sender?.id === currentUserId ? 'justify-end' : 'justify-start'"
          >
            <div
              class="max-w-md rounded-lg p-4"
              :class="message.sender?.id === currentUserId 
                ? 'bg-primary-600 text-white' 
                : 'bg-gray-100 text-gray-900'"
            >
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium">
                  {{ message.sender?.username || 'Unknown' }}
                </span>
                <span class="text-xs opacity-75 ml-2">
                  {{ formatDateTime(message.sent_at || message.created_at) }}
                </span>
              </div>
              <div class="text-sm whitespace-pre-wrap">{{ message.message }}</div>
              
              <!-- Attachment -->
              <div v-if="message.attachment" class="mt-2 pt-2 border-t border-opacity-20">
                <a
                  :href="getAttachmentUrl(message)"
                  target="_blank"
                  class="text-xs underline flex items-center gap-1"
                  :class="message.sender?.id === currentUserId ? 'text-white' : 'text-primary-600'"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                  </svg>
                  {{ getFileName(message.attachment) }}
                </a>
              </div>

              <!-- Internal Note Badge -->
              <span
                v-if="message.is_internal_note"
                class="inline-block mt-2 px-2 py-0.5 bg-yellow-500 text-white text-xs rounded"
              >
                Internal Note
              </span>
            </div>
          </div>
        </div>

        <!-- Message Composer -->
        <div class="border-t pt-4">
          <div class="space-y-3">
            <div v-if="availableRecipients.length > 1">
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Send to
              </label>
              <select
                v-model="messageForm.recipient_id"
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option v-for="recipient in availableRecipients" :key="recipient.id" :value="recipient.id">
                  {{ recipient.username }} ({{ recipient.role }})
                </option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Message <span class="text-red-500">*</span>
              </label>
              <textarea
                v-model="messageForm.message"
                rows="4"
                placeholder="Type your message..."
                class="w-full border rounded-lg px-3 py-2 focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                @keydown.ctrl.enter="sendMessage"
                @keydown.meta.enter="sendMessage"
              ></textarea>
            </div>

            <div class="flex items-center gap-4">
              <div>
                <label class="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    v-model="messageForm.is_internal_note"
                    class="rounded border-gray-300"
                  />
                  <span class="text-sm text-gray-700">Internal note (visible to staff only)</span>
                </label>
              </div>

              <div class="flex-1">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                  Attachment (Optional)
                </label>
                <input
                  type="file"
                  @change="handleFileSelect"
                  class="w-full border rounded-lg px-3 py-2 text-sm"
                  accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
                />
                <p v-if="messageForm.attachment" class="text-xs text-gray-500 mt-1">
                  Selected: {{ messageForm.attachment.name }}
                </p>
              </div>
            </div>

            <div class="flex justify-end gap-2">
              <button
                @click="clearForm"
                class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                Clear
              </button>
              <button
                @click="sendMessage"
                :disabled="sending || !messageForm.message || !messageForm.recipient_id"
                class="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {{ sending ? 'Sending...' : 'Send Message' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Message Toast -->
    <div
      v-if="message"
      class="fixed bottom-4 right-4 p-4 rounded-lg shadow-lg z-50"
      :class="messageSuccess ? 'bg-green-500 text-white' : 'bg-red-500 text-white'"
    >
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import communicationsAPI from '@/api/communications'
import ordersAPI from '@/api/orders'
import { getErrorMessage } from '@/utils/errorHandler'

const route = useRoute()
const authStore = useAuthStore()
const orderId = computed(() => parseInt(route.params.id))

const loading = ref(false)
const loadingMessages = ref(false)
const creatingThread = ref(false)
const sending = ref(false)
const thread = ref(null)
const messages = ref([])
const order = ref(null)
const availableRecipients = ref([])
const messagesContainer = ref(null)

const messageForm = ref({
  recipient_id: null,
  message: '',
  attachment: null,
  is_internal_note: false
})

const message = ref('')
const messageSuccess = ref(false)

const currentUserId = computed(() => authStore.user?.id)

const loadOrder = async () => {
  try {
    const res = await ordersAPI.get(orderId.value)
    order.value = res.data
  } catch (error) {
      const errorMsg = getErrorMessage(error, 'Failed to load order', 'Unable to load order')
      showMessage(errorMsg, false)
  }
}

const loadThread = async () => {
  loading.value = true
  try {
    // Try to get threads for this order
    const res = await communicationsAPI.listThreads({ order: orderId.value })
    const threads = res.data?.results || res.data || []
    
    if (threads.length > 0) {
      thread.value = threads[0]
      await loadMessages()
      await loadAvailableRecipients()
    } else {
      thread.value = null
      // Still try to load available recipients in case we need to create a thread
      if (order.value) {
        await loadAvailableRecipientsForNewThread()
      }
    }
  } catch (error) {
    console.error('Failed to load thread:', error)
    thread.value = null
    // If order exists, we can still create a thread
    if (order.value && error.response?.status !== 404) {
      const errorMsg = getErrorMessage(error, 'Failed to load conversation', 'Unable to load conversation')
      showMessage(errorMsg, false)
    }
  } finally {
    loading.value = false
  }
}

const loadAvailableRecipientsForNewThread = async () => {
  // For new threads, we'll determine recipients from the order
  if (order.value) {
    const recipients = []
    
    // Add writer if exists
    if (order.value.writer?.id && order.value.writer.id !== currentUserId.value) {
      recipients.push({
        id: order.value.writer.id,
        username: order.value.writer.username || 'Writer',
        role: 'writer'
      })
    }
    
    // Add client if exists and not current user
    if (order.value.client?.id && order.value.client.id !== currentUserId.value) {
      recipients.push({
        id: order.value.client.id,
        username: order.value.client.username || 'Client',
        role: 'client'
      })
    }
    
    availableRecipients.value = recipients
    
    // Set default recipient
    if (recipients.length > 0 && !messageForm.value.recipient_id) {
      messageForm.value.recipient_id = recipients[0].id
    }
  }
}

const loadMessages = async () => {
  if (!thread.value) return
  
  loadingMessages.value = true
  try {
    const res = await communicationsAPI.listMessages(thread.value.id)
    messages.value = (res.data?.results || res.data || []).reverse() // Reverse to show oldest first
    
    // Scroll to bottom
    await nextTick()
    scrollToBottom()
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to load messages', 'Unable to load messages')
    showMessage(errorMsg, false)
  } finally {
    loadingMessages.value = false
  }
}

const loadAvailableRecipients = async () => {
  if (!thread.value) return
  
  try {
    const res = await communicationsAPI.getAvailableRecipients(thread.value.id)
    availableRecipients.value = res.data || []
    
    // Set default recipient if not set
    if (!messageForm.value.recipient_id && availableRecipients.value.length > 0) {
      // Prefer the other participant (not current user)
      const other = availableRecipients.value.find(r => r.id !== currentUserId.value)
      messageForm.value.recipient_id = other?.id || availableRecipients.value[0].id
    }
  } catch (error) {
    console.error('Failed to load recipients:', error)
  }
}

const createThread = async () => {
  creatingThread.value = true
  try {
    // Use simplified endpoint that auto-determines participants
    const res = await communicationsAPI.startThreadForOrder(orderId.value)
    
    // Handle response format (could be { thread: {...} } or direct thread object)
    const threadData = res.data.thread || res.data
    thread.value = threadData
    
    // Set recipient if available
    if (threadData.participants && threadData.participants.length > 0) {
      const otherParticipant = threadData.participants.find(p => 
        (typeof p === 'object' ? p.id : p) !== currentUserId.value
      )
      if (otherParticipant) {
        messageForm.value.recipient_id = typeof otherParticipant === 'object' ? otherParticipant.id : otherParticipant
      }
    }
    
    await loadAvailableRecipients()
    await loadMessages()
    
    // Start auto-refresh for new thread
    if (refreshInterval) {
      clearInterval(refreshInterval)
    }
    refreshInterval = setInterval(() => {
      if (thread.value && !sending.value) {
        loadMessages()
      }
    }, 30000)
    
    showMessage('Conversation started successfully!', true)
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to create conversation', 'Unable to start conversation')
    showMessage(errorMsg, false)
  } finally {
    creatingThread.value = false
  }
}

const sendMessage = async () => {
  if (!messageForm.value.message || !messageForm.value.recipient_id || !thread.value) return
  
  sending.value = true
  try {
    await communicationsAPI.sendMessage(thread.value.id, {
      recipient_id: messageForm.value.recipient_id,
      message: messageForm.value.message,
      attachment: messageForm.value.attachment,
      is_internal_note: messageForm.value.is_internal_note
    })
    
    messageForm.value.message = ''
    messageForm.value.attachment = null
    await loadMessages()
    showMessage('Message sent successfully!', true)
  } catch (error) {
    const errorMsg = getErrorMessage(error, 'Failed to send message', 'Unable to send message')
    showMessage(errorMsg, false)
  } finally {
    sending.value = false
  }
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    messageForm.value.attachment = file
  }
}

const clearForm = () => {
  messageForm.value.message = ''
  messageForm.value.attachment = null
  messageForm.value.is_internal_note = false
}

const scrollToBottom = () => {
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

const getAttachmentUrl = (message) => {
  if (typeof message.attachment === 'string') {
    return message.attachment
  }
  return `/api/v1/communications/communication-threads/${thread.value.id}/communication-messages/${message.id}/download_attachment/`
}

const getFileName = (attachment) => {
  if (typeof attachment === 'string') {
    return attachment.split('/').pop() || 'attachment'
  }
  return attachment?.name || 'attachment'
}

const formatDateTime = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const showMessage = (msg, success) => {
  message.value = msg
  messageSuccess.value = success
  setTimeout(() => {
    message.value = ''
  }, 5000)
}

let refreshInterval = null

onMounted(async () => {
  await loadOrder()
  await nextTick()
  await loadThread()
  
  // Auto-refresh messages every 30 seconds if thread exists
  if (thread.value) {
    refreshInterval = setInterval(() => {
      if (thread.value && !sending.value) {
        loadMessages()
      }
    }, 30000)
  }
})

watch(() => route.params.id, async (newId) => {
  if (newId) {
    // Clear previous interval
    if (refreshInterval) {
      clearInterval(refreshInterval)
      refreshInterval = null
    }
    
    await loadOrder()
    await nextTick()
    await loadThread()
    
    // Start new interval
    if (thread.value) {
      refreshInterval = setInterval(() => {
        if (thread.value && !sending.value) {
          loadMessages()
        }
      }, 30000)
    }
  }
})

// Cleanup interval on unmount
onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  padding: 1rem;
}
</style>



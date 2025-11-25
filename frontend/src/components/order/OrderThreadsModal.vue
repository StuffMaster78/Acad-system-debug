<template>
  <div class="fixed inset-0 bg-gray-100 z-50 flex items-center justify-center" @click.self="close">
    <div class="bg-white rounded-lg max-w-md w-full h-[90vh] max-h-[800px] overflow-hidden flex flex-col shadow-xl">
      <!-- Header -->
      <div class="bg-primary-600 text-white px-4 py-3 flex items-center justify-between">
        <div>
          <h3 class="text-lg font-semibold">Messages</h3>
          <p class="text-xs text-primary-100">Order #{{ orderId }}</p>
        </div>
        <button @click="close" class="text-white hover:text-gray-200 text-xl">✕</button>
      </div>

      <!-- Threads List (Chat List Style) -->
      <div class="flex-1 overflow-y-auto">
        <div v-if="loading" class="flex items-center justify-center py-12">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>

        <div v-else-if="threads.length === 0" class="text-center py-12 text-gray-500">
          <div class="text-4xl mb-4">💬</div>
          <p>No conversations yet</p>
          <button 
            @click="createNewThread" 
            class="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            :disabled="creatingThread"
          >
            {{ creatingThread ? 'Creating...' : 'Start Conversation' }}
          </button>
        </div>

        <div v-else class="divide-y divide-gray-200">
          <div
            v-for="thread in threads"
            :key="thread.id"
            @click="openMessagesModal(thread)"
            class="px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors active:bg-gray-100"
            :class="{ 'bg-blue-50': selectedThread?.id === thread.id }"
          >
            <div class="flex items-start gap-3">
              <!-- Avatar -->
              <div class="flex-shrink-0">
                <div class="w-12 h-12 rounded-full bg-primary-100 flex items-center justify-center text-primary-600 font-semibold text-lg">
                  {{ getThreadInitials(thread) }}
                </div>
                <div v-if="thread.unread_count > 0" class="relative -mt-3 ml-8">
                  <span class="absolute bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
                    {{ thread.unread_count > 9 ? '9+' : thread.unread_count }}
                  </span>
                </div>
              </div>

              <!-- Thread Info -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between mb-1">
                  <div class="flex items-center gap-2">
                    <span class="font-medium text-gray-900 truncate">
                      {{ getThreadName(thread) }}
                    </span>
                    <span v-if="!thread.is_active" class="text-xs px-1.5 py-0.5 rounded bg-gray-200 text-gray-600">
                      Inactive
                    </span>
                  </div>
                  <span class="text-xs text-gray-500 flex-shrink-0 ml-2">
                    {{ formatTime(thread.last_message?.sent_at || thread.updated_at) }}
                  </span>
                </div>
                
                <div class="flex items-center justify-between">
                  <p class="text-sm text-gray-600 truncate flex-1">
                    <span v-if="thread.last_message" class="inline-flex items-center gap-1">
                      <span v-if="isCurrentUser(thread.last_message.sender)" class="text-primary-600">You:</span>
                      <span>{{ truncateMessage(thread.last_message.message) }}</span>
                    </span>
                    <span v-else class="text-gray-400 italic">No messages yet</span>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="border-t bg-white px-4 py-3">
        <button 
          @click="createNewThread" 
          class="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium"
          :disabled="creatingThread"
        >
          {{ creatingThread ? 'Creating...' : '+ New Conversation' }}
        </button>
      </div>
    </div>

    <!-- Messages Modal (nested) -->
    <OrderMessagesModal
      v-if="showMessagesModal && selectedThread"
      :thread="selectedThread"
      :order-id="orderId"
      @close="closeMessagesModal"
      @thread-updated="loadThreads"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { communicationsAPI } from '@/api'
import ordersAPI from '@/api/orders'
import { useAuthStore } from '@/stores/auth'
import OrderMessagesModal from './OrderMessagesModal.vue'

const props = defineProps({
  orderId: {
    type: [Number, String],
    required: true
  },
  initialThreadId: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['close'])

const authStore = useAuthStore()
const threads = ref([])
const loading = ref(false)
const selectedThread = ref(null)
const showMessagesModal = ref(false)
const creatingThread = ref(false)

const loadThreads = async () => {
  loading.value = true
  try {
    const res = await communicationsAPI.listThreads({ order: props.orderId })
    threads.value = res.data.results || res.data || []
    // Sort by last message time or updated time
    threads.value.sort((a, b) => {
      const timeA = a.last_message?.sent_at || a.updated_at
      const timeB = b.last_message?.sent_at || b.updated_at
      return new Date(timeB) - new Date(timeA)
    })
    
    // If initialThreadId is provided, open that thread
    if (props.initialThreadId) {
      const thread = threads.value.find(t => t.id === parseInt(props.initialThreadId))
      if (thread) {
        selectedThread.value = thread
        showMessagesModal.value = true
      }
    }
  } catch (error) {
    console.error('Failed to load threads:', error)
  } finally {
    loading.value = false
  }
}

const openMessagesModal = (thread) => {
  selectedThread.value = thread
  showMessagesModal.value = true
}

const closeMessagesModal = () => {
  showMessagesModal.value = false
  selectedThread.value = null
}

const createNewThread = async () => {
  creatingThread.value = true
  try {
    const orderRes = await ordersAPI.get(props.orderId)
    const order = orderRes.data
    
    const participants = []
    if (order.client) participants.push(order.client.id)
    if (order.assigned_writer) participants.push(order.assigned_writer.id)
    
    if (authStore.user && !participants.includes(authStore.user.id)) {
      participants.push(authStore.user.id)
    }
    
    const threadData = {
      order: props.orderId,
      website: order.website || order.website_id,
      participants: participants,
      thread_type: 'order'
    }
    
    const res = await communicationsAPI.createThread(threadData)
    const newThread = res.data
    
    await loadThreads()
    
    selectedThread.value = newThread
    showMessagesModal.value = true
  } catch (error) {
    console.error('Failed to create thread:', error)
    alert('Failed to create thread: ' + (error.response?.data?.detail || error.message))
  } finally {
    creatingThread.value = false
  }
}

const getThreadName = (thread) => {
  if (thread.participants && thread.participants.length > 0) {
    const otherParticipants = thread.participants.filter(p => p.id !== authStore.user?.id)
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

const truncateMessage = (message) => {
  if (!message) return ''
  return message.length > 50 ? message.substring(0, 50) + '...' : message
}

const formatTime = (date) => {
  if (!date) return ''
  const d = new Date(date)
  const now = new Date()
  const diff = now - d
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (days === 0) {
    return d.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true })
  } else if (days === 1) {
    return 'Yesterday'
  } else if (days < 7) {
    return d.toLocaleDateString('en-US', { weekday: 'short' })
  } else {
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }
}

const isCurrentUser = (sender) => {
  return sender?.id === authStore.user?.id
}

const close = () => {
  emit('close')
}

const formatDateTime = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

onMounted(() => {
  loadThreads()
})

watch(() => props.orderId, () => {
  loadThreads()
})
</script>

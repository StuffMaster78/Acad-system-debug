<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Messages</h1>
      <p class="mt-2 text-gray-600 dark:text-gray-400">Communicate with writers about your orders</p>
    </div>

    <!-- Messages List -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Threads List -->
      <div class="lg:col-span-1 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        <div class="p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 class="font-semibold text-gray-900 dark:text-white">Conversations</h2>
        </div>
        <div v-if="loadingThreads" class="text-center py-8">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mx-auto"></div>
        </div>
        <div v-else-if="threads.length === 0" class="text-center py-8 text-gray-500 text-sm">
          No conversations yet
        </div>
        <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
          <button
            v-for="thread in threads"
            :key="thread.id"
            @click="selectedThread = thread"
            class="w-full p-4 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            :class="selectedThread?.id === thread.id ? 'bg-primary-50 dark:bg-primary-900/20' : ''"
          >
            <div class="flex items-center justify-between mb-1">
              <p class="font-medium text-gray-900 dark:text-white">
                {{ thread.order?.topic || `Order #${thread.order_id}` }}
              </p>
              <span v-if="thread.unread_count > 0" class="px-2 py-1 text-xs bg-primary-600 text-white rounded-full">
                {{ thread.unread_count }}
              </span>
            </div>
            <p class="text-sm text-gray-500 truncate">
              {{ thread.last_message?.content || 'No messages yet' }}
            </p>
            <p class="text-xs text-gray-400 mt-1">
              {{ formatDate(thread.updated_at) }}
            </p>
          </button>
        </div>
      </div>

      <!-- Messages View -->
      <div class="lg:col-span-2 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        <div v-if="!selectedThread" class="flex items-center justify-center h-96 text-gray-500">
          <div class="text-center">
            <svg class="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
            <p>Select a conversation to view messages</p>
          </div>
        </div>

        <div v-else class="flex flex-col h-96">
          <!-- Thread Header -->
          <div class="p-4 border-b border-gray-200 dark:border-gray-700">
            <h3 class="font-semibold text-gray-900 dark:text-white">
              {{ selectedThread.order?.topic || `Order #${selectedThread.order_id}` }}
            </h3>
          </div>

          <!-- Messages -->
          <div class="flex-1 overflow-y-auto p-4 space-y-4">
            <div v-if="loadingMessages" class="text-center py-8">
              <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mx-auto"></div>
            </div>
            <div v-else-if="messages.length === 0" class="text-center py-8 text-gray-500 text-sm">
              No messages yet. Start the conversation!
            </div>
            <div
              v-for="message in messages"
              :key="message.id"
              class="flex"
              :class="message.sender?.id === authStore.user?.id ? 'justify-end' : 'justify-start'"
            >
              <div
                class="max-w-xs lg:max-w-md px-4 py-2 rounded-lg"
                :class="message.sender?.id === authStore.user?.id
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'"
              >
                <p class="text-sm">{{ message.content }}</p>
                <p class="text-xs mt-1 opacity-75">
                  {{ formatDate(message.created_at) }}
                </p>
              </div>
            </div>
          </div>

          <!-- Message Input -->
          <div class="p-4 border-t border-gray-200 dark:border-gray-700">
            <form @submit.prevent="sendMessage" class="flex space-x-2">
              <input
                v-model="newMessage"
                type="text"
                placeholder="Type your message..."
                class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
              />
              <button
                type="submit"
                :disabled="!newMessage.trim() || sending"
                class="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Send
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import communicationsAPI from '@/api/communications'

const route = useRoute()
const authStore = useAuthStore()

const loadingThreads = ref(true)
const loadingMessages = ref(false)
const threads = ref([])
const selectedThread = ref(null)
const messages = ref([])
const newMessage = ref('')
const sending = ref(false)

const fetchThreads = async () => {
  loadingThreads.value = true
  try {
    const response = await communicationsAPI.listThreads({ ordering: '-updated_at' })
    threads.value = Array.isArray(response.data?.results)
      ? response.data.results
      : (Array.isArray(response.data) ? response.data : [])
    
    // Auto-select thread if order query param exists
    if (route.query.order && threads.value.length > 0) {
      const thread = threads.value.find(t => t.order_id === parseInt(route.query.order))
      if (thread) {
        selectedThread.value = thread
      }
    }
  } catch (err) {
    console.error('Failed to fetch threads:', err)
    threads.value = []
  } finally {
    loadingThreads.value = false
  }
}

const fetchMessages = async () => {
  if (!selectedThread.value) return

  loadingMessages.value = true
  try {
    const response = await communicationsAPI.getMessages(selectedThread.value.id, { ordering: 'created_at' })
    messages.value = Array.isArray(response.data?.results)
      ? response.data.results
      : (Array.isArray(response.data) ? response.data : [])
  } catch (err) {
    console.error('Failed to fetch messages:', err)
    messages.value = []
  } finally {
    loadingMessages.value = false
  }
}

const sendMessage = async () => {
  if (!newMessage.value.trim() || !selectedThread.value) return

  sending.value = true
  try {
    await communicationsAPI.sendMessage(selectedThread.value.id, {
      content: newMessage.value
    })
    newMessage.value = ''
    await fetchMessages()
    await fetchThreads() // Refresh threads to update last message
  } catch (err) {
    console.error('Failed to send message:', err)
    alert(err.response?.data?.detail || 'Failed to send message')
  } finally {
    sending.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days < 7) return `${days}d ago`
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

watch(selectedThread, () => {
  if (selectedThread.value) {
    fetchMessages()
  }
})

onMounted(() => {
  fetchThreads()
})
</script>


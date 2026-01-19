<template>
  <div class="space-y-6 p-4 sm:p-6">
    <!-- Breadcrumbs -->
    <nav class="flex items-center gap-2 text-xs sm:text-sm overflow-x-auto whitespace-nowrap" aria-label="Breadcrumb">
      <router-link to="/dashboard" class="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
        Dashboard
      </router-link>
      <span class="text-gray-400 dark:text-gray-600">/</span>
      <span class="text-gray-900 dark:text-gray-100 font-medium truncate max-w-[60vw] sm:max-w-none">Communications</span>
    </nav>
    
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="page-title text-gray-900">Client Communications</h1>
        <p class="mt-2 text-gray-600">Manage your conversations with clients</p>
      </div>
      <button
        @click="loadCommunications"
        :disabled="loading"
        class="flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 w-full sm:w-auto"
      >
        <svg
          class="w-5 h-5"
          :class="{ 'animate-spin': loading }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Refresh
      </button>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-4 sm:p-6 border-l-4 border-blue-500">
        <p class="text-sm font-medium text-gray-600 mb-1">Total Threads</p>
        <p class="text-3xl font-bold text-blue-600">{{ communicationsData?.total_threads || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 sm:p-6 border-l-4 border-orange-500">
        <p class="text-sm font-medium text-gray-600 mb-1">Unread Messages</p>
        <p class="text-3xl font-bold text-orange-600">{{ communicationsData?.total_unread || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 sm:p-6 border-l-4 border-green-500">
        <p class="text-sm font-medium text-gray-600 mb-1">Active Conversations</p>
        <p class="text-3xl font-bold text-green-600">{{ communicationsData?.active_conversations || 0 }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-4 sm:p-6 border-l-4 border-purple-500">
        <p class="text-sm font-medium text-gray-600 mb-1">This Week</p>
        <p class="text-3xl font-bold text-purple-600">{{ communicationsData?.summary?.threads_this_week || 0 }}</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="bg-white rounded-lg shadow-sm p-4">
      <div class="flex flex-col sm:flex-row sm:items-center gap-4">
        <div class="flex-1">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by client name, order topic, or message..."
            class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            @input="filterThreads"
          />
        </div>
        <select
          v-model="filterType"
          @change="filterThreads"
          class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 w-full sm:w-auto"
        >
          <option value="all">All Threads</option>
          <option value="unread">Unread Only</option>
          <option value="active">Active Conversations</option>
          <option value="by_client">By Client</option>
        </select>
      </div>
    </div>

    <!-- Error Message (only show if no data loaded) -->
    <div v-if="error && !communicationsData" class="bg-red-50 border-l-4 border-red-400 p-4 rounded-lg mb-4">
      <div class="flex items-center justify-between">
        <div class="flex items-start">
          <div class="shrink-0">
            <svg class="h-5 w-5 text-red-400 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3 flex-1">
            <h3 class="text-sm font-medium text-red-800">Failed to load communications</h3>
            <p class="text-sm text-red-700 mt-1">{{ error }}</p>
          </div>
        </div>
        <button 
          @click="loadCommunications" 
          class="ml-4 px-3 py-1.5 text-sm font-medium text-red-700 bg-red-100 hover:bg-red-200 rounded-lg transition-colors"
        >
          Retry
        </button>
      </div>
    </div>

    <!-- Threads List -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <div v-else-if="error && !communicationsData" class="text-center py-12 bg-white rounded-lg shadow-sm">
      <div class="text-4xl mb-4">⚠️</div>
      <p class="text-gray-600">{{ error }}</p>
      <button @click="loadCommunications" class="mt-4 btn btn-primary">Retry</button>
    </div>

    <div v-else-if="filteredThreads.length === 0" class="text-center py-12 bg-white rounded-lg shadow-sm">
      <div class="text-4xl mb-4">💬</div>
      <p class="text-gray-600">No conversations found</p>
      <p class="text-sm text-gray-400 mt-2">Start a conversation from an order page</p>
    </div>

    <div v-else class="space-y-4">
      <!-- Group by Client View -->
      <div v-if="filterType === 'by_client'" class="space-y-6">
        <div
          v-for="clientGroup in groupedByClient"
          :key="clientGroup.client_id"
          class="bg-white rounded-lg shadow-sm overflow-hidden"
        >
          <div class="bg-gray-50 px-6 py-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <div>
                <h3 class="font-semibold text-gray-900">{{ clientGroup.client_name }}</h3>
                <p class="text-sm text-gray-600">
                  {{ clientGroup.threads.length }} conversation(s)
                  <span v-if="clientGroup.unread_count > 0" class="ml-2 text-orange-600 font-medium">
                    • {{ clientGroup.unread_count }} unread
                  </span>
                </p>
              </div>
            </div>
          </div>
          <div class="divide-y divide-gray-200">
            <div
              v-for="thread in clientGroup.threads"
              :key="thread.id"
              class="p-6 transition-all cursor-pointer border-l-4"
              :class="thread.unread_count > 0 
                ? 'border-l-blue-500 bg-blue-50 hover:bg-blue-100' 
                : 'border-l-transparent hover:bg-gray-50'"
              @click="openThread(thread)"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-3 mb-2 flex-wrap">
                    <router-link
                      v-if="thread.order_id"
                      :to="`/orders/${thread.order_id}`"
                      class="font-semibold text-primary-600 hover:underline"
                      @click.stop
                    >
                      Order #{{ thread.order_id }}
                    </router-link>
                    <span v-else class="font-semibold text-gray-900">General Conversation</span>
                    <span
                      :class="getStatusClass(thread.order_status)"
                      class="px-2 py-1 text-xs font-medium rounded-full"
                    >
                      {{ thread.order_status || 'N/A' }}
                    </span>
                    <span
                      v-if="thread.unread_count > 0"
                      class="px-2 py-1 text-xs font-bold bg-red-500 text-white rounded-full"
                    >
                      {{ thread.unread_count }} unread
                    </span>
                  </div>
                  <p 
                    class="text-sm mb-2"
                    :class="thread.unread_count > 0 ? 'text-gray-700 font-medium' : 'text-gray-600'"
                  >
                    {{ thread.order_topic }}
                  </p>
                  <div 
                    v-if="thread.last_message" 
                    class="flex items-center gap-2 text-sm"
                    :class="thread.unread_count > 0 ? 'text-gray-600 font-medium' : 'text-gray-500'"
                  >
                    <span class="font-medium">{{ thread.last_message.sender }}</span>
                    <span>•</span>
                    <span>{{ formatDate(thread.last_message.created_at) }}</span>
                    <span v-if="thread.last_message.has_attachment" class="ml-2">📎</span>
                  </div>
                  <p 
                    v-if="thread.last_message" 
                    class="text-sm mt-2 line-clamp-2"
                    :class="thread.unread_count > 0 ? 'text-gray-800 font-medium' : 'text-gray-700'"
                  >
                    {{ thread.last_message.message }}
                  </p>
                </div>
                <button
                  @click.stop="openThread(thread)"
                  class="ml-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-sm whitespace-nowrap transition-colors"
                >
                  Open
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Standard List View -->
      <div v-else class="space-y-4">
        <div
          v-for="thread in filteredThreads"
          :key="thread.id"
          class="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-all cursor-pointer border-l-4"
          :class="thread.unread_count > 0 
            ? 'border-l-blue-500 bg-blue-50 hover:bg-blue-100' 
            : 'border-l-gray-200 hover:bg-gray-50'"
          @click="openThread(thread)"
        >
          <div class="flex items-start justify-between">
            <div class="flex-1">
              <div class="flex items-center gap-3 mb-2 flex-wrap">
                <router-link
                  v-if="thread.order_id"
                  :to="`/orders/${thread.order_id}`"
                  class="font-semibold text-primary-600 hover:underline"
                  @click.stop
                >
                  Order #{{ thread.order_id }}
                </router-link>
                <span v-else class="font-semibold text-gray-900">General Conversation</span>
                <span
                  :class="getStatusClass(thread.order_status)"
                  class="px-2 py-1 text-xs font-medium rounded-full"
                >
                  {{ thread.order_status || 'N/A' }}
                </span>
                <span
                  v-if="thread.unread_count > 0"
                  class="px-2 py-1 text-xs font-bold bg-red-500 text-white rounded-full"
                >
                  {{ thread.unread_count }} unread
                </span>
              </div>
              <div class="flex items-center gap-4 mb-2">
                <span 
                  class="text-sm"
                  :class="thread.unread_count > 0 ? 'text-gray-700 font-medium' : 'text-gray-600'"
                >
                  <span class="font-medium">Client:</span> {{ thread.client_name }}
                </span>
                <span 
                  class="text-sm"
                  :class="thread.unread_count > 0 ? 'text-gray-700 font-medium' : 'text-gray-600'"
                >
                  <span class="font-medium">Topic:</span> {{ thread.order_topic }}
                </span>
              </div>
              <div 
                v-if="thread.last_message" 
                class="mt-3 p-3 rounded-lg"
                :class="thread.unread_count > 0 ? 'bg-blue-100' : 'bg-gray-50'"
              >
                <div class="flex items-center gap-2 text-sm mb-1"
                  :class="thread.unread_count > 0 ? 'text-gray-700 font-medium' : 'text-gray-600'"
                >
                  <span class="font-medium">{{ thread.last_message.sender }}</span>
                  <span class="text-gray-400">({{ thread.last_message.sender_role }})</span>
                  <span>•</span>
                  <span>{{ formatDate(thread.last_message.created_at) }}</span>
                  <span v-if="thread.last_message.has_attachment" class="ml-2 text-primary-600">📎 Attachment</span>
                </div>
                <p 
                  class="text-sm line-clamp-2"
                  :class="thread.unread_count > 0 ? 'text-gray-800 font-medium' : 'text-gray-700'"
                >
                  {{ thread.last_message.message }}
                </p>
              </div>
            </div>
            <button
              @click.stop="openThread(thread)"
              class="ml-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-sm whitespace-nowrap transition-colors"
            >
              Open Conversation
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import writerDashboardAPI from '@/api/writer-dashboard'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const router = useRouter()
const { error: showError, success: showSuccess } = useToast()

const loading = ref(false)
const error = ref(null)
const communicationsData = ref(null)
const searchQuery = ref('')
const filterType = ref('all')
let refreshInterval = null

const loadCommunications = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await writerDashboardAPI.getCommunications()
    if (response && response.data) {
      communicationsData.value = response.data
    } else {
      throw new Error('Invalid response format')
    }
  } catch (err) {
    console.error('Failed to load communications:', err)
    const errorMsg = getErrorMessage(err, 'Failed to load communications. Please try again.')
    error.value = errorMsg
    showError(errorMsg)
  } finally {
    loading.value = false
  }
}

const filteredThreads = computed(() => {
  if (!communicationsData.value) return []
  
  let threads = communicationsData.value.threads || []
  
  // Apply filter type
  if (filterType.value === 'unread') {
    threads = threads.filter(t => t.unread_count > 0)
  } else if (filterType.value === 'active') {
    threads = communicationsData.value.active_threads || []
  }
  
  // Apply search query
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    threads = threads.filter(thread => {
      return (
        thread.client_name?.toLowerCase().includes(query) ||
        thread.order_topic?.toLowerCase().includes(query) ||
        thread.last_message?.message?.toLowerCase().includes(query)
      )
    })
  }
  
  return threads
})

const groupedByClient = computed(() => {
  if (!communicationsData.value) return []
  return communicationsData.value.threads_by_client || []
})

const openThread = (thread) => {
  // Navigate to dedicated thread detail page
  router.push(`/messages/thread/${thread.id}`)
}

const getStatusClass = (status) => {
  const classes = {
    'in_progress': 'bg-blue-100 text-blue-800',
    'submitted': 'bg-green-100 text-green-800',
    'revision_requested': 'bg-orange-100 text-orange-800',
    'completed': 'bg-green-100 text-green-800',
    'cancelled': 'bg-red-100 text-red-800',
    'on_hold': 'bg-yellow-100 text-yellow-800',
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)
  
  if (diffMins < 1) return 'Just now'
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(() => {
  loadCommunications()
  // Auto-refresh every 30 seconds
  refreshInterval = setInterval(() => {
    if (!loading.value) {
      loadCommunications()
    }
  }, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>


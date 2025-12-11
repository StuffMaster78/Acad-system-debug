<template>
  <div class="space-y-6 p-6">
    <div>
      <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Unified Search</h1>
      <p class="mt-2 text-gray-600 dark:text-gray-400">Search across orders, users, payments, and messages</p>
    </div>

    <!-- Search Bar -->
    <div class="card p-4">
      <div class="flex flex-col sm:flex-row gap-4">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Enter search query (minimum 2 characters)..."
          class="flex-1 px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white text-lg"
          @keyup.enter="performSearch"
          @input="debouncedSearch"
        />
        <div class="flex gap-2">
          <select
            v-model="selectedTypes"
            multiple
            class="px-4 py-3 border rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-700 dark:text-white"
            style="min-width: 200px;"
          >
            <option value="orders">Orders</option>
            <option value="users">Users</option>
            <option value="payments">Payments</option>
            <option value="messages">Messages</option>
          </select>
          <button
            @click="performSearch"
            :disabled="loading || searchQuery.length < 2"
            class="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {{ loading ? 'Searching...' : 'Search' }}
          </button>
        </div>
      </div>
      <p v-if="searchQuery.length > 0 && searchQuery.length < 2" class="text-sm text-red-600 dark:text-red-400 mt-2">
        Search query must be at least 2 characters
      </p>
    </div>

    <!-- Results -->
    <div v-if="searchResults && searchResults.total_results > 0" class="space-y-6">
      <div class="flex items-center justify-between">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
          Results ({{ searchResults.total_results }})
        </h2>
        <span class="text-sm text-gray-500 dark:text-gray-400">
          Query: "{{ searchResults.query }}"
        </span>
      </div>

      <!-- Orders Results -->
      <div v-if="searchResults.orders && searchResults.orders.length > 0" class="card p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Orders ({{ searchResults.orders.length }})</h3>
        <div class="space-y-3">
          <div
            v-for="order in searchResults.orders"
            :key="order.id"
            class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-pointer"
            @click="viewOrder(order.id)"
          >
            <div class="flex items-center justify-between">
              <div>
                <p class="font-semibold text-gray-900 dark:text-white">Order #{{ order.id }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">{{ order.title || 'No title' }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-500 mt-1">
                  Status: {{ order.status }} | Client: {{ order.client_email || order.client }}
                </p>
              </div>
              <span class="text-primary-600 dark:text-primary-400">→</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Users Results -->
      <div v-if="searchResults.users && searchResults.users.length > 0" class="card p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Users ({{ searchResults.users.length }})</h3>
        <div class="space-y-3">
          <div
            v-for="user in searchResults.users"
            :key="user.id"
            class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-pointer"
            @click="viewUser(user.id)"
          >
            <div class="flex items-center justify-between">
              <div>
                <p class="font-semibold text-gray-900 dark:text-white">{{ user.username || user.email }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">{{ user.email }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-500 mt-1">
                  Role: {{ user.role }} | {{ user.first_name }} {{ user.last_name }}
                </p>
              </div>
              <span class="text-primary-600 dark:text-primary-400">→</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Payments Results -->
      <div v-if="searchResults.payments && searchResults.payments.length > 0" class="card p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Payments ({{ searchResults.payments.length }})</h3>
        <div class="space-y-3">
          <div
            v-for="payment in searchResults.payments"
            :key="payment.id"
            class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <div class="flex items-center justify-between">
              <div>
                <p class="font-semibold text-gray-900 dark:text-white">Payment #{{ payment.id }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  Amount: ${{ formatCurrency(payment.amount) }} | Status: {{ payment.status }}
                </p>
                <p class="text-xs text-gray-500 dark:text-gray-500 mt-1">
                  Order: #{{ payment.order_id || 'N/A' }} | {{ formatDate(payment.created_at) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Messages Results -->
      <div v-if="searchResults.messages && searchResults.messages.length > 0" class="card p-6">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Messages ({{ searchResults.messages.length }})</h3>
        <div class="space-y-3">
          <div
            v-for="message in searchResults.messages"
            :key="message.id"
            class="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors cursor-pointer"
            @click="viewMessage(message.thread_id)"
          >
            <div class="flex items-center justify-between">
              <div>
                <p class="font-semibold text-gray-900 dark:text-white">{{ message.subject || 'No subject' }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400 line-clamp-2">{{ message.content || message.body }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-500 mt-1">
                  From: {{ message.sender_email || message.sender }} | {{ formatDate(message.sent_at || message.created_at) }}
                </p>
              </div>
              <span class="text-primary-600 dark:text-primary-400">→</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Results -->
    <div v-else-if="hasSearched && searchResults && searchResults.total_results === 0" class="card p-12 text-center">
      <p class="text-lg text-gray-500 dark:text-gray-400">No results found for "{{ searchQuery }}"</p>
      <p class="text-sm text-gray-400 dark:text-gray-500 mt-2">Try adjusting your search query or filters</p>
    </div>

    <!-- Initial State -->
    <div v-else-if="!hasSearched" class="card p-12 text-center">
      <p class="text-lg text-gray-500 dark:text-gray-400">Enter a search query to begin</p>
      <p class="text-sm text-gray-400 dark:text-gray-500 mt-2">Search across orders, users, payments, and messages</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="mt-4 text-gray-600 dark:text-gray-400">Searching...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { debounce } from '@/utils/debounce'
import adminManagementAPI from '@/api/admin-management'

const router = useRouter()
const { error: showError } = useToast()

const loading = ref(false)
const searchQuery = ref('')
const selectedTypes = ref([])
const searchResults = ref(null)
const hasSearched = ref(false)

const debouncedSearch = debounce(() => {
  if (searchQuery.value.length >= 2) {
    performSearch()
  }
}, 500)

const formatCurrency = (amount) => {
  if (!amount && amount !== 0) return '0.00'
  return Number(amount).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleString()
}

const performSearch = async () => {
  if (searchQuery.value.length < 2) return
  
  loading.value = true
  hasSearched.value = true
  try {
    const response = await adminManagementAPI.unifiedSearch(
      searchQuery.value,
      selectedTypes.value.length > 0 ? selectedTypes.value : null,
      10
    )
    searchResults.value = response.data || {}
  } catch (error) {
    showError('Failed to perform search')
    console.error('Error searching:', error)
    searchResults.value = { total_results: 0, orders: [], users: [], payments: [], messages: [] }
  } finally {
    loading.value = false
  }
}

const viewOrder = (orderId) => {
  router.push(`/admin/orders/${orderId}`)
}

const viewUser = (userId) => {
  router.push(`/admin/users/${userId}`)
}

const viewMessage = (threadId) => {
  router.push(`/admin/communications/${threadId}`)
}
</script>


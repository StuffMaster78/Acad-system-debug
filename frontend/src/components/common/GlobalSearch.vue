<template>
  <div class="relative">
    <!-- Search Input -->
    <div class="relative">
      <input
        v-model="searchQuery"
        @input="handleSearch"
        @focus="showResults = true"
        @keydown.escape="closeSearch"
        @keydown.enter.prevent="handleEnter"
        @keydown.down.prevent="navigateResults(1)"
        @keydown.up.prevent="navigateResults(-1)"
        type="text"
        placeholder="Search orders, users, payments, messages..."
        class="w-full px-4 py-2 pl-10 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none"
        :class="{ 'border-primary-500': showResults && hasResults }"
      />
      <div class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
      <button
        v-if="searchQuery"
        @click="clearSearch"
        class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Search Results Dropdown -->
    <div
      v-if="showResults && (searchQuery.length >= 2 || hasResults)"
      class="absolute z-50 w-full mt-2 bg-white border border-gray-200 rounded-lg shadow-lg max-h-96 overflow-y-auto"
    >
      <!-- Loading State -->
      <div v-if="loading" class="p-4 text-center text-gray-500">
        <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-2 text-sm">Searching...</p>
      </div>

      <!-- No Results -->
      <div v-else-if="!hasResults && searchQuery.length >= 2" class="p-4 text-center text-gray-500">
        <p class="text-sm">No results found for "{{ searchQuery }}"</p>
      </div>

      <!-- Results -->
      <div v-else-if="hasResults" class="py-2">
        <!-- Orders -->
        <div v-if="results.orders && results.orders.length > 0" class="mb-2">
          <div class="px-4 py-2 bg-gray-50 border-b border-gray-200">
            <h3 class="text-xs font-semibold text-gray-600 uppercase tracking-wide">Orders</h3>
          </div>
          <div
            v-for="(order, index) in results.orders"
            :key="`order-${order.id}`"
            @click="navigateToResult(order)"
            @mouseenter="selectedIndex = `order-${index}`"
            class="px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors"
            :class="{ 'bg-gray-50': selectedIndex === `order-${index}` }"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">{{ order.title }}</p>
                <p class="text-xs text-gray-500 mt-1">{{ order.subtitle }}</p>
              </div>
              <span class="ml-2 px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                Order
              </span>
            </div>
          </div>
        </div>

        <!-- Users -->
        <div v-if="results.users && results.users.length > 0" class="mb-2">
          <div class="px-4 py-2 bg-gray-50 border-b border-gray-200">
            <h3 class="text-xs font-semibold text-gray-600 uppercase tracking-wide">Users</h3>
          </div>
          <div
            v-for="(user, index) in results.users"
            :key="`user-${user.id}`"
            @click="navigateToResult(user)"
            @mouseenter="selectedIndex = `user-${index}`"
            class="px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors"
            :class="{ 'bg-gray-50': selectedIndex === `user-${index}` }"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">{{ user.title }}</p>
                <p class="text-xs text-gray-500 mt-1">{{ user.subtitle }}</p>
              </div>
              <span class="ml-2 px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                User
              </span>
            </div>
          </div>
        </div>

        <!-- Payments -->
        <div v-if="results.payments && results.payments.length > 0" class="mb-2">
          <div class="px-4 py-2 bg-gray-50 border-b border-gray-200">
            <h3 class="text-xs font-semibold text-gray-600 uppercase tracking-wide">Payments</h3>
          </div>
          <div
            v-for="(payment, index) in results.payments"
            :key="`payment-${payment.id}`"
            @click="navigateToResult(payment)"
            @mouseenter="selectedIndex = `payment-${index}`"
            class="px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors"
            :class="{ 'bg-gray-50': selectedIndex === `payment-${index}` }"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">{{ payment.title }}</p>
                <p class="text-xs text-gray-500 mt-1">{{ payment.subtitle }}</p>
              </div>
              <span class="ml-2 px-2 py-1 text-xs rounded-full bg-purple-100 text-purple-800">
                Payment
              </span>
            </div>
          </div>
        </div>

        <!-- Messages -->
        <div v-if="results.messages && results.messages.length > 0" class="mb-2">
          <div class="px-4 py-2 bg-gray-50 border-b border-gray-200">
            <h3 class="text-xs font-semibold text-gray-600 uppercase tracking-wide">Messages</h3>
          </div>
          <div
            v-for="(message, index) in results.messages"
            :key="`message-${message.id}`"
            @click="navigateToResult(message)"
            @mouseenter="selectedIndex = `message-${index}`"
            class="px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors"
            :class="{ 'bg-gray-50': selectedIndex === `message-${index}` }"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <p class="text-sm font-medium text-gray-900">{{ message.title }}</p>
                <p class="text-xs text-gray-500 mt-1">{{ message.subtitle }}</p>
              </div>
              <span class="ml-2 px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800">
                Message
              </span>
            </div>
          </div>
        </div>

        <!-- View All Results Link -->
        <div
          v-if="results.total_results > 10"
          @click="viewAllResults"
          class="px-4 py-3 border-t border-gray-200 bg-gray-50 hover:bg-gray-100 cursor-pointer text-center"
        >
          <p class="text-sm font-medium text-primary-600">
            View all {{ results.total_results }} results
          </p>
        </div>
      </div>

      <!-- Initial State -->
      <div v-else-if="searchQuery.length < 2" class="p-4 text-center text-gray-500">
        <p class="text-sm">Type at least 2 characters to search</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import searchAPI from '@/api/search'

const router = useRouter()

const searchQuery = ref('')
const results = ref({
  orders: [],
  users: [],
  payments: [],
  messages: [],
  total_results: 0
})
const loading = ref(false)
const showResults = ref(false)
const selectedIndex = ref(null)

let searchTimeout = null

const hasResults = computed(() => {
  return results.value.total_results > 0
})

const handleSearch = () => {
  clearTimeout(searchTimeout)
  
  if (searchQuery.value.length < 2) {
    results.value = {
      orders: [],
      users: [],
      payments: [],
      messages: [],
      total_results: 0
    }
    return
  }
  
  searchTimeout = setTimeout(() => {
    performSearch()
  }, 300)
}

const performSearch = async () => {
  if (searchQuery.value.length < 2) return
  
  try {
    loading.value = true
    const response = await searchAPI.search(searchQuery.value, { limit: 5 })
    results.value = response.data
  } catch (error) {
    console.error('Search error:', error)
    results.value = {
      orders: [],
      users: [],
      payments: [],
      messages: [],
      total_results: 0
    }
  } finally {
    loading.value = false
  }
}

const navigateToResult = (result) => {
  if (result.url) {
    router.push(result.url)
    closeSearch()
  }
}

const navigateResults = (direction) => {
  // Simple navigation - can be enhanced
  const allResults = [
    ...results.value.orders.map((r, i) => ({ ...r, key: `order-${i}` })),
    ...results.value.users.map((r, i) => ({ ...r, key: `user-${i}` })),
    ...results.value.payments.map((r, i) => ({ ...r, key: `payment-${i}` })),
    ...results.value.messages.map((r, i) => ({ ...r, key: `message-${i}` }))
  ]
  
  if (allResults.length === 0) return
  
  const currentIndex = allResults.findIndex(r => r.key === selectedIndex.value)
  let newIndex = currentIndex + direction
  
  if (newIndex < 0) newIndex = allResults.length - 1
  if (newIndex >= allResults.length) newIndex = 0
  
  selectedIndex.value = allResults[newIndex].key
}

const handleEnter = () => {
  const allResults = [
    ...results.value.orders.map((r, i) => ({ ...r, key: `order-${i}` })),
    ...results.value.users.map((r, i) => ({ ...r, key: `user-${i}` })),
    ...results.value.payments.map((r, i) => ({ ...r, key: `payment-${i}` })),
    ...results.value.messages.map((r, i) => ({ ...r, key: `message-${i}` }))
  ]
  
  if (allResults.length > 0) {
    const current = allResults.find(r => r.key === selectedIndex.value) || allResults[0]
    navigateToResult(current)
  } else if (searchQuery.value.length >= 2) {
    viewAllResults()
  }
}

const viewAllResults = () => {
  router.push({
    name: 'SearchResults',
    query: { q: searchQuery.value }
  })
  closeSearch()
}

const clearSearch = () => {
  searchQuery.value = ''
  results.value = {
    orders: [],
    users: [],
    payments: [],
    messages: [],
    total_results: 0
  }
  showResults.value = false
}

const closeSearch = () => {
  showResults.value = false
  selectedIndex.value = null
}

// Close results when clicking outside
const handleClickOutside = (event) => {
  const searchContainer = event.target.closest('.relative')
  if (!searchContainer) {
    closeSearch()
  }
}

watch(showResults, (isOpen) => {
  if (isOpen) {
    setTimeout(() => {
      document.addEventListener('click', handleClickOutside)
    }, 100)
  } else {
    document.removeEventListener('click', handleClickOutside)
  }
})
</script>


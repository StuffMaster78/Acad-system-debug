<template>
  <div class="space-y-8">
    <!-- Welcome Section -->
    <div class="bg-linear-to-r from-primary-600 to-primary-700 rounded-xl p-8 text-white shadow-lg">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold mb-2">Welcome back, {{ authStore.user?.full_name || 'Client' }}!</h1>
          <p class="text-primary-100">Here's an overview of your account and recent activity</p>
        </div>
        <router-link
          to="/client/orders/create"
          class="hidden md:flex items-center space-x-2 px-6 py-3 bg-white text-primary-600 rounded-lg font-semibold hover:bg-primary-50 transition-colors shadow-md"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          <span>Place New Order</span>
        </router-link>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <!-- Active Orders -->
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">Active Orders</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-2">
              {{ stats.active_orders || 0 }}
            </p>
          </div>
          <div class="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Total Spent -->
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">Total Spent</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-2">
              ${{ (stats.total_spent || 0).toFixed(2) }}
            </p>
          </div>
          <div class="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Wallet Balance -->
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">Wallet Balance</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-2">
              ${{ (walletBalance || 0).toFixed(2) }}
            </p>
          </div>
          <div class="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Loyalty Points -->
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 dark:text-gray-400">Loyalty Points</p>
            <p class="text-3xl font-bold text-gray-900 dark:text-white mt-2">
              {{ loyaltyData.points || 0 }}
            </p>
            <p class="text-xs text-gray-500 mt-1">{{ loyaltyData.tier || 'Bronze' }} Tier</p>
          </div>
          <div class="w-12 h-12 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-yellow-600 dark:text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <router-link
          to="/client/orders/create"
          class="flex items-center space-x-3 p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          <div class="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
            </svg>
          </div>
          <div>
            <p class="font-medium text-gray-900 dark:text-white">Place New Order</p>
            <p class="text-sm text-gray-500">Create a new writing order</p>
          </div>
        </router-link>

        <router-link
          to="/client/orders"
          class="flex items-center space-x-3 p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          <div class="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div>
            <p class="font-medium text-gray-900 dark:text-white">View Orders</p>
            <p class="text-sm text-gray-500">Manage your orders</p>
          </div>
        </router-link>

        <router-link
          to="/client/payments"
          class="flex items-center space-x-3 p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          <div class="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
            <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <div>
            <p class="font-medium text-gray-900 dark:text-white">Payments</p>
            <p class="text-sm text-gray-500">View payment history</p>
          </div>
        </router-link>
      </div>
    </div>

    <!-- Recent Orders -->
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Recent Orders</h2>
        <router-link
          to="/client/orders"
          class="text-sm text-primary-600 dark:text-primary-400 hover:underline"
        >
          View all
        </router-link>
      </div>

      <div v-if="ordersLoading" class="text-center py-8">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
      </div>

      <div v-else-if="recentOrders.length === 0" class="text-center py-8 text-gray-500">
        <svg class="w-12 h-12 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p>No orders yet</p>
        <router-link
          to="/client/orders/create"
          class="mt-4 inline-block text-primary-600 dark:text-primary-400 hover:underline"
        >
          Place your first order
        </router-link>
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="order in recentOrders"
          :key="order.id"
          class="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors cursor-pointer"
          @click="$router.push(`/client/orders/${order.id}`)"
        >
          <div class="flex-1">
            <div class="flex items-center space-x-3">
              <h3 class="font-medium text-gray-900 dark:text-white">{{ order.topic || 'Untitled Order' }}</h3>
              <span
                class="px-2 py-1 text-xs font-semibold rounded-full"
                :class="getStatusClass(order.status)"
              >
                {{ formatStatus(order.status) }}
              </span>
            </div>
            <p class="text-sm text-gray-500 mt-1">
              {{ formatDate(order.created_at) }} • {{ order.number_of_pages || 0 }} pages
            </p>
          </div>
          <div class="text-right">
            <p class="font-semibold text-gray-900 dark:text-white">${{ (order.total_price || 0).toFixed(2) }}</p>
            <p class="text-xs text-gray-500">Due: {{ formatDate(order.client_deadline) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Payment Reminders -->
    <div v-if="paymentReminders.length > 0" class="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6">
      <h2 class="text-lg font-semibold text-yellow-900 dark:text-yellow-300 mb-4">Payment Reminders</h2>
      <div class="space-y-3">
        <div
          v-for="reminder in paymentReminders"
          :key="reminder.id"
          class="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-lg"
        >
          <div>
            <p class="font-medium text-gray-900 dark:text-white">{{ reminder.order?.topic || 'Order' }}</p>
            <p class="text-sm text-gray-500">Due: {{ formatDate(reminder.due_date) }}</p>
          </div>
          <router-link
            :to="`/client/orders/${reminder.order_id}`"
            class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-sm font-medium"
          >
            Pay Now
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import clientDashboardAPI from '@/api/client-dashboard'
import walletAPI from '@/api/wallet'
import ordersAPI from '@/api/orders'

const authStore = useAuthStore()

const loading = ref(true)
const stats = ref({})
const loyaltyData = ref({})
const walletBalance = ref(0)
const recentOrders = ref([])
const ordersLoading = ref(false)
const paymentReminders = ref([])

const fetchDashboardData = async () => {
  loading.value = true
  try {
    const [statsRes, loyaltyRes, walletRes, remindersRes] = await Promise.all([
      clientDashboardAPI.getStats(30).catch(() => ({ data: {} })),
      clientDashboardAPI.getLoyalty().catch(() => ({ data: {} })),
      walletAPI.getBalance().catch(() => ({ data: { balance: 0 } })),
      clientDashboardAPI.getPaymentReminders().catch(() => ({ data: [] }))
    ])

    stats.value = statsRes.data || {}
    loyaltyData.value = loyaltyRes.data || {}
    walletBalance.value = walletRes.data.balance || walletRes.data.wallet?.balance || 0
    paymentReminders.value = Array.isArray(remindersRes.data) ? remindersRes.data : []
  } catch (err) {
    console.error('Failed to fetch dashboard data:', err)
  } finally {
    loading.value = false
  }
}

const fetchRecentOrders = async () => {
  ordersLoading.value = true
  try {
    const response = await ordersAPI.list({ page_size: 5, ordering: '-created_at' })
    const orders = Array.isArray(response.data?.results)
      ? response.data.results
      : (Array.isArray(response.data) ? response.data : [])
    recentOrders.value = orders.slice(0, 5)
  } catch (err) {
    console.error('Failed to fetch recent orders:', err)
    recentOrders.value = []
  } finally {
    ordersLoading.value = false
  }
}

const formatStatus = (status) => {
  const statusMap = {
    'pending': 'Pending',
    'in_progress': 'In Progress',
    'completed': 'Completed',
    'cancelled': 'Cancelled',
    'on_hold': 'On Hold',
    'revision': 'Revision',
    'disputed': 'Disputed'
  }
  return statusMap[status] || status
}

const getStatusClass = (status) => {
  const classMap = {
    'pending': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
    'in_progress': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
    'completed': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
    'cancelled': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
    'on_hold': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
    'revision': 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
    'disputed': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
  }
  return classMap[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

onMounted(async () => {
  await Promise.all([fetchDashboardData(), fetchRecentOrders()])
})
</script>


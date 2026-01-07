<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Client Dashboard</h1>
        <p class="mt-2 text-gray-600 flex items-center flex-wrap gap-2">
          <span>Welcome back, {{ displayName }}</span>
          <CopyableIdChip
            v-if="displayId"
            :label="displayIdLabel"
            :value="displayId"
          />
        </p>
      </div>
      <div class="flex items-center gap-3">
        <button
          @click="refreshDashboard"
          :disabled="refreshing"
          class="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors disabled:opacity-50"
        >
          <svg 
            class="w-5 h-5" 
            :class="{ 'animate-spin': refreshing }"
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          {{ refreshing ? 'Refreshing...' : 'Refresh' }}
      </button>
        <router-link
          to="/orders/wizard"
          class="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors shadow-sm hover:shadow-md"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Create Order
        </router-link>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
        
    <!-- Error State -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
      <div class="flex items-center gap-2">
        <svg class="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span class="text-red-800">{{ error }}</span>
          </div>
        </div>
        
    <!-- Dashboard Content -->
    <div v-else>
      <!-- Review reminders -->
      <section v-if="reviewReminders.length" class="space-y-3 mb-6">
        <div class="bg-white rounded-lg border border-yellow-100 p-4 shadow-sm">
          <h2 class="text-sm font-semibold text-gray-800 mb-3">Pending Reviews</h2>
          <ReviewReminderCard
            v-for="rem in reviewReminders"
            :key="rem.id"
            :reminder="rem"
            @updated="refreshReviewReminders"
          />
        </div>
      </section>

      <!-- Message reminders -->
      <section v-if="messageReminders.length" class="space-y-3 mb-6">
        <div class="bg-white rounded-lg border border-amber-100 p-4 shadow-sm">
          <h2 class="text-sm font-semibold text-gray-800 mb-3">Message Reminders</h2>
          <div class="space-y-3">
            <MessageReminderCard
              v-for="rem in messageReminders"
              :key="rem.id"
              :reminder="rem"
              @updated="refreshMessageReminders"
            />
          </div>
        </div>
      </section>

      <!-- Use the ClientDashboard component with fetched data -->
      <ClientDashboardComponent
        :client-dashboard-data="clientDashboardData"
        :client-loyalty-data="clientLoyaltyData"
        :client-analytics-data="clientAnalyticsData"
        :client-wallet-analytics="clientWalletAnalytics"
        :wallet-balance="walletBalance"
        :recent-orders="recentOrders"
        :recent-orders-loading="recentOrdersLoading"
        :recent-notifications="recentNotifications"
        :recent-notifications-loading="recentNotificationsLoading"
        :recent-communications="recentCommunications"
        :recent-communications-loading="recentCommunicationsLoading"
        :recent-tickets="recentTickets"
        :recent-tickets-loading="recentTicketsLoading"
        :loading="loading"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import CopyableIdChip from '@/components/common/CopyableIdChip.vue'
import clientDashboardAPI from '@/api/client-dashboard'
import walletAPI from '@/api/wallet'
import ordersAPI from '@/api/orders'
import notificationsAPI from '@/api/notifications'
import communicationsAPI from '@/api/communications'
import ticketsAPI from '@/api/tickets'
import ClientDashboardComponent from '@/views/dashboard/components/ClientDashboard.vue'
import { reviewRemindersAPI, messageRemindersAPI } from '@/api'
import ReviewReminderCard from '@/components/orders/ReviewReminderCard.vue'
import MessageReminderCard from '@/components/orders/MessageReminderCard.vue'

const authStore = useAuthStore()

// State
const loading = ref(true)
const refreshing = ref(false)
const error = ref(null)

const clientDashboardData = ref({})
const clientLoyaltyData = ref({})
const clientAnalyticsData = ref({})
const clientWalletAnalytics = ref({})
const walletBalance = ref(0)
const recentOrders = ref([])
const recentOrdersLoading = ref(false)
const recentNotifications = ref([])
const recentNotificationsLoading = ref(false)
const recentCommunications = ref([])
const recentCommunicationsLoading = ref(false)
const recentTickets = ref([])
const recentTicketsLoading = ref(false)
const reviewReminders = ref([])
const messageReminders = ref([])

const displayName = computed(() => {
  const user = authStore.user
  if (!user) return 'Client'
  return user.full_name || user.username || user.email
})

const displayIdLabel = computed(() => 'Client ID')

const displayId = computed(() => authStore.user?.id || null)

// Fetch functions
const fetchClientDashboard = async () => {
  try {
    const response = await clientDashboardAPI.getStats(30)
    clientDashboardData.value = response?.data || {}
  } catch (err) {
    console.error('Failed to fetch client dashboard:', err)
    error.value = err.response?.data?.detail || 'Failed to load dashboard'
    clientDashboardData.value = {}
  }
}

const fetchClientLoyalty = async () => {
  try {
    const response = await clientDashboardAPI.getLoyalty()
    clientLoyaltyData.value = response?.data || {}
  } catch (err) {
    console.error('Failed to fetch loyalty data:', err)
  }
}

const fetchClientAnalytics = async () => {
  try {
    const response = await clientDashboardAPI.getAnalytics(30)
    clientAnalyticsData.value = response?.data || {}
  } catch (err) {
    console.error('Failed to fetch analytics:', err)
  }
}

const fetchClientWalletAnalytics = async () => {
  try {
    const response = await clientDashboardAPI.getWalletAnalytics(30)
    clientWalletAnalytics.value = response?.data || {}
  } catch (err) {
    console.error('Failed to fetch wallet analytics:', err)
  }
}

const fetchWalletBalance = async () => {
  try {
    const response = await walletAPI.getBalance()
    walletBalance.value = response.data.balance || response.data.wallet?.balance || 0
  } catch (err) {
    console.error('Failed to fetch wallet balance:', err)
  }
}

const fetchRecentOrders = async () => {
  recentOrdersLoading.value = true
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
    recentOrdersLoading.value = false
  }
}

const fetchRecentNotifications = async () => {
  recentNotificationsLoading.value = true
  try {
    const response = await notificationsAPI.getNotifications({ page_size: 3, ordering: '-created_at' })
    const notifications = Array.isArray(response.data?.results)
      ? response.data.results
      : (Array.isArray(response.data) ? response.data : [])
    recentNotifications.value = notifications.slice(0, 3)
  } catch (err) {
    console.error('Failed to fetch notifications:', err)
    recentNotifications.value = []
  } finally {
    recentNotificationsLoading.value = false
  }
}

const fetchRecentCommunications = async () => {
  recentCommunicationsLoading.value = true
  try {
    const response = await communicationsAPI.listThreads({ page_size: 5, ordering: '-updated_at' })
    const threads = Array.isArray(response.data?.results)
      ? response.data.results
      : (Array.isArray(response.data) ? response.data : [])
    recentCommunications.value = threads.slice(0, 5)
  } catch (err) {
    console.error('Failed to fetch communications:', err)
    recentCommunications.value = []
  } finally {
    recentCommunicationsLoading.value = false
  }
}

const fetchRecentTickets = async () => {
  recentTicketsLoading.value = true
  try {
    const response = await ticketsAPI.list({ page_size: 5, ordering: '-updated_at' })
    const tickets = Array.isArray(response.data?.results)
      ? response.data.results
      : (Array.isArray(response.data) ? response.data : [])
    recentTickets.value = tickets.slice(0, 5)
      } catch (err) {
    console.error('Failed to fetch tickets:', err)
    recentTickets.value = []
      } finally {
    recentTicketsLoading.value = false
  }
}

const fetchReviewReminders = async () => {
  try {
    const res = await reviewRemindersAPI.myReminders()
    reviewReminders.value = Array.isArray(res.data) ? res.data : []
  } catch (err) {
    console.error('Failed to fetch review reminders:', err)
    reviewReminders.value = []
  }
}

const refreshReviewReminders = async () => {
  await fetchReviewReminders()
}

const fetchMessageReminders = async () => {
  try {
    const res = await messageRemindersAPI.myReminders()
    messageReminders.value = Array.isArray(res.data) ? res.data : []
  } catch (err) {
    console.error('Failed to fetch message reminders:', err)
    messageReminders.value = []
  }
}

const refreshMessageReminders = async () => {
  await fetchMessageReminders()
}

const refreshDashboard = async () => {
  refreshing.value = true
  error.value = null
  try {
    await Promise.all([
      fetchClientDashboard(),
      fetchClientLoyalty(),
      fetchClientAnalytics(),
      fetchClientWalletAnalytics(),
      fetchWalletBalance(),
      fetchRecentOrders(),
      fetchRecentNotifications(),
      fetchRecentCommunications(),
      fetchRecentTickets(),
      fetchReviewReminders(),
      fetchMessageReminders()
    ])
  } catch (err) {
    console.error('Failed to refresh dashboard:', err)
    error.value = err.response?.data?.detail || 'Failed to refresh dashboard'
  } finally {
    refreshing.value = false
  }
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    fetchClientDashboard(),
    fetchClientLoyalty(),
    fetchClientAnalytics(),
    fetchClientWalletAnalytics(),
    fetchWalletBalance(),
    fetchRecentOrders(),
    fetchRecentNotifications(),
    fetchRecentCommunications(),
    fetchRecentTickets(),
    fetchReviewReminders(),
    fetchMessageReminders()
  ])
  loading.value = false
})
</script>

<style scoped>
.card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
  border: 1px solid #e5e7eb;
}
</style>

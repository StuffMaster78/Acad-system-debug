<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-900">Writer Dashboard</h1>
        <p class="mt-2 text-gray-600">Welcome back, {{ authStore.user?.email }}</p>
      </div>
      <div class="flex items-center gap-4">
        <div class="flex items-center gap-2 text-xs text-gray-500">
          <span
            class="inline-block w-2 h-2 rounded-full"
            :class="{
              'bg-green-500': realtimeConnectionStatus === 'connected',
              'bg-yellow-400 animate-pulse': realtimeConnectionStatus === 'connecting',
              'bg-red-500 animate-pulse': realtimeConnectionStatus === 'disconnected'
            }"
          ></span>
          <span>{{ realtimeStatusText }}</span>
        </div>
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
      <!-- Engagement & reminders -->
      <section class="space-y-4 mb-6">
        <div v-if="writerAcknowledgments.length" class="bg-white rounded-lg border border-blue-100 p-4 shadow-sm">
          <h2 class="text-sm font-semibold text-gray-800 mb-3">Order Engagement</h2>
          <div class="space-y-3">
            <WriterAcknowledgmentCard
              v-for="ack in writerAcknowledgments"
              :key="ack.id"
              :acknowledgment="ack"
              @updated="refreshEngagement"
            />
          </div>
        </div>
        <div v-if="messageReminders.length" class="bg-white rounded-lg border border-amber-100 p-4 shadow-sm">
          <h2 class="text-sm font-semibold text-gray-800 mb-3">Message Reminders</h2>
          <div class="space-y-3">
            <MessageReminderCard
              v-for="rem in messageReminders"
              :key="rem.id"
              :reminder="rem"
              @updated="refreshEngagement"
            />
          </div>
        </div>
      </section>

      <!-- Use the WriterDashboard component with fetched data -->
      <WriterDashboardComponent
        :writer-earnings-data="writerEarningsData"
        :writer-performance-data="writerPerformanceData"
        :writer-queue-data="writerQueueData"
        :writer-badges-data="writerBadgesData"
        :writer-level-data="writerLevelData"
        :writer-summary-data="writerSummaryData"
        :writer-payment-status="writerPaymentStatus"
        :recent-orders="recentOrders"
        :recent-orders-loading="recentOrdersLoading"
        :loading="loading"
        :availability-status="availabilityStatus"
        :realtime-widget-data="realtimeWidgetData"
        @refresh-requested="handleWidgetRefresh"
        @order-requested="handleWidgetOrderRequest"
        @availability-updated="handleAvailabilityUpdated"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import writerDashboardAPI from '@/api/writer-dashboard'
import ordersAPI from '@/api/orders'
import WriterDashboardComponent from '@/views/dashboard/components/WriterDashboard.vue'
import { useWriterDashboardRealtime } from '@/composables/useWriterDashboardRealtime'
import { writerAcknowledgmentAPI, messageRemindersAPI } from '@/api'
import WriterAcknowledgmentCard from '@/components/orders/WriterAcknowledgmentCard.vue'
import MessageReminderCard from '@/components/orders/MessageReminderCard.vue'

const authStore = useAuthStore()

// State
const loading = ref(true)
const refreshing = ref(false)
const error = ref(null)

const writerEarningsData = ref(null)
const writerPerformanceData = ref(null)
const writerQueueData = ref(null)
const writerBadgesData = ref(null)
const writerLevelData = ref(null)
const writerSummaryData = ref(null)
const writerPaymentStatus = ref(null)
const recentOrders = ref([])
const recentOrdersLoading = ref(false)
const availabilityStatus = ref(null)
const realtimeWidgetData = ref(null)
const writerAcknowledgments = ref([])
const messageReminders = ref([])

const { status: realtimeConnectionStatus } = useWriterDashboardRealtime({
  onMessage: (payload) => {
    realtimeWidgetData.value = payload
  }
})

const realtimeStatusText = computed(() => {
  if (realtimeConnectionStatus.value === 'connected') return 'Live updates'
  if (realtimeConnectionStatus.value === 'connecting') return 'Connecting...'
  if (realtimeConnectionStatus.value === 'disconnected') return 'Reconnecting...'
  return 'Offline'
})

// Fetch functions
const fetchWriterEarnings = async () => {
  try {
    const response = await writerDashboardAPI.getEarnings(30)
    writerEarningsData.value = response?.data || null
  } catch (err) {
    console.error('Failed to fetch writer earnings:', err)
    writerEarningsData.value = null
  }
}

const fetchWriterPerformance = async () => {
  try {
    const response = await writerDashboardAPI.getPerformanceAnalytics(30)
    writerPerformanceData.value = response?.data || null
  } catch (err) {
    console.error('Failed to fetch writer performance:', err)
    writerPerformanceData.value = null
  }
}

const fetchWriterQueue = async () => {
  try {
    const response = await writerDashboardAPI.getOrderQueue()
    writerQueueData.value = response?.data || null
  } catch (err) {
    console.error('Failed to fetch writer queue:', err)
    writerQueueData.value = null
  }
}

const fetchWriterBadges = async () => {
  try {
    const response = await writerDashboardAPI.getBadgesAndAchievements()
    writerBadgesData.value = response?.data || null
  } catch (err) {
    console.error('Failed to fetch writer badges:', err)
    writerBadgesData.value = null
  }
}

const fetchWriterLevel = async () => {
  try {
    const response = await writerDashboardAPI.getLevelAndRanking()
    writerLevelData.value = response?.data || null
  } catch (err) {
    console.error('Failed to fetch writer level:', err)
    writerLevelData.value = null
  }
}

const fetchWriterSummary = async () => {
  try {
    const response = await writerDashboardAPI.getDashboardSummary()
    writerSummaryData.value = response?.data || null
  } catch (err) {
    console.error('Failed to fetch writer summary:', err)
    writerSummaryData.value = null
  }
}

const fetchRecentOrders = async () => {
  recentOrdersLoading.value = true
  try {
    const response = await ordersAPI.list({ 
      assigned_writer: true,
      page_size: 50, 
      ordering: '-created_at',
    })
    const orders = Array.isArray(response.data?.results) 
      ? response.data.results 
      : (Array.isArray(response.data) ? response.data : [])
    recentOrders.value = orders
  } catch (err) {
    console.error('Failed to fetch recent orders:', err)
    recentOrders.value = []
  } finally {
    recentOrdersLoading.value = false
  }
}

const fetchWriterAcknowledgments = async () => {
  try {
    const res = await writerAcknowledgmentAPI.myAcknowledgments()
    writerAcknowledgments.value = Array.isArray(res.data) ? res.data : []
  } catch (err) {
    console.error('Failed to fetch writer acknowledgments:', err)
    writerAcknowledgments.value = []
  }
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

const refreshEngagement = async () => {
  await Promise.all([fetchWriterAcknowledgments(), fetchMessageReminders()])
}

const handleWidgetRefresh = async ({ scope }) => {
  switch (scope) {
    case 'queue':
      await fetchWriterQueue()
      break
    case 'summary':
      await fetchWriterSummary()
      break
    case 'earnings':
      await fetchWriterEarnings()
      break
    case 'orders':
      await fetchRecentOrders()
      break
    default:
      break
  }
}

const handleWidgetOrderRequest = async () => {
  await fetchWriterQueue()
}

const handleWidgetRefresh = async ({ scope }) => {
  switch (scope) {
    case 'queue':
      await fetchWriterQueue()
      break
    case 'summary':
      await fetchWriterSummary()
      break
    case 'earnings':
      await fetchWriterEarnings()
      break
    case 'orders':
      await fetchRecentOrders()
      break
    default:
      break
  }
}await Promise.all([fetchWriterQueue(), fetchWriterSummary()])
}

const refreshDashboard = async () => {
  refreshing.value = true
  error.value = null
  try {
    await Promise.all([
      fetchWriterEarnings(),
      fetchWriterPerformance(),
      fetchWriterQueue(),
      fetchWriterBadges(),
      fetchWriterLevel(),
      fetchWriterSummary(),
      fetchWriterPaymentStatus(),
      fetchRecentOrders(),
      loadAvailabilityStatus(),
      fetchWriterAcknowledgments(),
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
    fetchWriterEarnings(),
    fetchWriterPerformance(),
    fetchWriterQueue(),
    fetchWriterBadges(),
    fetchWriterLevel(),
    fetchWriterSummary(),
    fetchWriterPaymentStatus(),
    fetchRecentOrders(),
    loadAvailabilityStatus(),
    fetchWriterAcknowledgments(),
    fetchMessageReminders()
  ])
  loading.value = false
})

const loadAvailabilityStatus = async () => {
  try {
    const response = await writerDashboardAPI.getAvailability()
    availabilityStatus.value = response?.data || null
  } catch (err) {
    console.error('Failed to load availability status:', err)
  }
}

const handleAvailabilityUpdated = (payload) => {
  availabilityStatus.value = payload
}
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

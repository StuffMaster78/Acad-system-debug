<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-100 shadow-sm">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <span class="text-4xl">📅</span>
          <span>Deadline Calendar</span>
        </h1>
        <p class="mt-2 text-gray-600">View your order deadlines in calendar format</p>
      </div>
      <div class="flex items-center gap-2">
        <button 
          @click="previousMonth" 
          class="btn btn-secondary text-sm hover:shadow-md transition-all duration-200 flex items-center gap-1"
        >
          <span>←</span>
          <span>Previous</span>
        </button>
        <button 
          @click="nextMonth" 
          class="btn btn-secondary text-sm hover:shadow-md transition-all duration-200 flex items-center gap-1"
        >
          <span>Next</span>
          <span>→</span>
        </button>
        <button 
          @click="goToToday" 
          class="btn btn-primary text-sm hover:shadow-md transition-all duration-200"
        >
          Today
        </button>
        <button 
          @click="loadCalendar" 
          :disabled="loading" 
          class="btn btn-secondary hover:shadow-md transition-all duration-200 flex items-center gap-2"
        >
          <span v-if="loading" class="animate-spin">⟳</span>
          <span>{{ loading ? 'Loading...' : 'Refresh' }}</span>
        </button>
        <button 
          @click="exportToCalendar" 
          :disabled="loading || calendarData.total_orders === 0"
          class="btn btn-primary hover:shadow-md transition-all duration-200 flex items-center gap-2"
          title="Export deadlines to your calendar (Google Calendar, Outlook, Apple Calendar)"
        >
          <span>📥</span>
          <span>Export to Calendar</span>
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 hover:shadow-md transition-all duration-200 transform hover:-translate-y-1">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-blue-700 mb-1">Total Orders</p>
            <p class="text-3xl font-bold text-blue-900">{{ calendarData.total_orders || 0 }}</p>
          </div>
          <div class="text-4xl opacity-20">📋</div>
        </div>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-red-50 to-red-100 border border-red-200 hover:shadow-md transition-all duration-200 transform hover:-translate-y-1">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-red-700 mb-1">Overdue</p>
            <p class="text-3xl font-bold text-red-900">{{ calendarData.overdue_count || 0 }}</p>
          </div>
          <div class="text-4xl opacity-20">⚠️</div>
        </div>
      </div>
      <div class="bg-white rounded-lg shadow-sm p-6 bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200 hover:shadow-md transition-all duration-200 transform hover:-translate-y-1">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-orange-700 mb-1">Urgent (24h)</p>
            <p class="text-3xl font-bold text-orange-900">{{ calendarData.urgent_count || 0 }}</p>
          </div>
          <div class="text-4xl opacity-20">⏰</div>
        </div>
      </div>
    </div>

    <!-- Calendar View -->
    <div v-if="loading" class="bg-white rounded-lg shadow-sm p-12">
      <div class="flex items-center justify-center">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    </div>

    <div v-else class="bg-white rounded-lg shadow-sm p-6">
      <div class="mb-4 text-center">
        <h2 class="text-xl font-semibold text-gray-900">{{ currentMonthYear }}</h2>
      </div>

      <!-- Calendar Grid -->
      <div class="grid grid-cols-7 gap-2">
        <!-- Day Headers -->
        <div
          v-for="day in dayHeaders"
          :key="day"
          class="text-center text-sm font-semibold text-gray-600 py-2"
        >
          {{ day }}
        </div>

        <!-- Calendar Days -->
        <div
          v-for="(day, index) in calendarDays"
          :key="index"
          :class="[
            'min-h-[100px] border rounded-lg p-2 transition-all duration-200',
            day.isCurrentMonth ? 'bg-white hover:bg-blue-50' : 'bg-gray-50',
            day.isToday ? 'ring-2 ring-primary-500 shadow-md' : 'hover:shadow-sm',
            day.orderCount > 0 ? 'cursor-pointer' : '',
          ]"
        >
          <div class="flex items-center justify-between mb-1">
            <span
              :class="[
                'text-sm font-medium',
                day.isToday ? 'text-primary-600' : day.isCurrentMonth ? 'text-gray-900' : 'text-gray-400',
              ]"
            >
              {{ day.day }}
            </span>
            <span
              v-if="day.orderCount > 0"
              class="px-2 py-0.5 text-xs font-bold rounded-full"
              :class="[
                day.overdueCount > 0 ? 'bg-red-100 text-red-700' :
                day.urgentCount > 0 ? 'bg-orange-100 text-orange-700' :
                'bg-blue-100 text-blue-700'
              ]"
            >
              {{ day.orderCount }}
            </span>
          </div>

          <!-- Orders for this day -->
          <div class="space-y-1">
            <div
              v-for="order in day.orders"
              :key="order.id"
              @click="viewOrder(order.id)"
              :class="[
                'text-xs p-1.5 rounded cursor-pointer transition-all duration-200 hover:scale-105 hover:shadow-sm',
                order.is_overdue ? 'bg-red-100 text-red-900 border border-red-300 hover:bg-red-200' :
                order.is_urgent ? 'bg-orange-100 text-orange-900 border border-orange-300 hover:bg-orange-200' :
                'bg-blue-50 text-blue-900 border border-blue-200 hover:bg-blue-100'
              ]"
              :title="`${order.topic} - ${order.service_type}${order.hours_remaining !== null ? ` (${formatTimeRemaining(order.hours_remaining)} remaining)` : ''}`"
            >
              <div class="font-medium truncate">#{{ order.id }}</div>
              <div class="text-xs opacity-75 truncate">{{ order.topic }}</div>
              <div v-if="order.hours_remaining !== null" class="text-xs opacity-75">
                {{ formatTimeRemaining(order.hours_remaining) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Order Details Modal (if needed) -->
    <div
      v-if="selectedOrder"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="selectedOrder = null"
    >
      <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold">Order #{{ selectedOrder.id }}</h3>
          <button @click="selectedOrder = null" class="text-gray-400 hover:text-gray-600">✕</button>
        </div>
        <div class="space-y-2 text-sm">
          <div><span class="font-medium">Topic:</span> {{ selectedOrder.topic }}</div>
          <div><span class="font-medium">Service:</span> {{ selectedOrder.service_type }}</div>
          <div><span class="font-medium">Pages:</span> {{ selectedOrder.pages }}</div>
          <div><span class="font-medium">Deadline:</span> {{ formatDate(selectedOrder.deadline) }}</div>
          <div><span class="font-medium">Status:</span> {{ selectedOrder.status }}</div>
        </div>
        <div class="mt-4 flex gap-2">
          <router-link
            :to="`/orders/${selectedOrder.id}`"
            class="btn btn-primary text-sm"
            @click="selectedOrder = null"
          >
            View Details
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import writerDashboardAPI from '@/api/writer-dashboard'
import { useToast } from '@/composables/useToast'
import { getErrorMessage } from '@/utils/errorHandler'

const router = useRouter()
const { error: showError, success: showSuccess } = useToast()

const loading = ref(false)
const calendarData = ref({
  calendar: {},
  total_orders: 0,
  overdue_count: 0,
  urgent_count: 0,
  from_date: null,
  to_date: null,
})

const currentDate = ref(new Date())
const selectedOrder = ref(null)

const dayHeaders = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

const currentMonthYear = computed(() => {
  return currentDate.value.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
})

const calendarDays = computed(() => {
  const year = currentDate.value.getFullYear()
  const month = currentDate.value.getMonth()
  
  // First day of the month
  const firstDay = new Date(year, month, 1)
  const firstDayOfWeek = firstDay.getDay()
  
  // Last day of the month
  const lastDay = new Date(year, month + 1, 0)
  const daysInMonth = lastDay.getDate()
  
  // Today's date
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  
  const days = []
  
  // Add days from previous month
  const prevMonthLastDay = new Date(year, month, 0).getDate()
  for (let i = firstDayOfWeek - 1; i >= 0; i--) {
    const date = new Date(year, month - 1, prevMonthLastDay - i)
    days.push(createDayObject(date, false, today))
  }
  
  // Add days from current month
  for (let day = 1; day <= daysInMonth; day++) {
    const date = new Date(year, month, day)
    days.push(createDayObject(date, true, today))
  }
  
  // Add days from next month to fill the grid
  const remainingDays = 42 - days.length // 6 weeks * 7 days
  for (let day = 1; day <= remainingDays; day++) {
    const date = new Date(year, month + 1, day)
    days.push(createDayObject(date, false, today))
  }
  
  return days
})

const createDayObject = (date, isCurrentMonth, today) => {
  const dateKey = date.toISOString().split('T')[0]
  const orders = calendarData.value.calendar[dateKey] || []
  
  const overdueCount = orders.filter(o => o.is_overdue).length
  const urgentCount = orders.filter(o => o.is_urgent && !o.is_overdue).length
  
  return {
    day: date.getDate(),
    date: date,
    dateKey: dateKey,
    isCurrentMonth: isCurrentMonth,
    isToday: date.getTime() === today.getTime(),
    orders: orders,
    orderCount: orders.length,
    overdueCount: overdueCount,
    urgentCount: urgentCount,
  }
}

const loadCalendar = async () => {
  loading.value = true
  try {
    const year = currentDate.value.getFullYear()
    const month = currentDate.value.getMonth()
    
    const fromDate = new Date(year, month, 1)
    const toDate = new Date(year, month + 1, 0, 23, 59, 59)
    
    const response = await writerDashboardAPI.getCalendar({
      from_date: fromDate.toISOString(),
      to_date: toDate.toISOString(),
    })
    
    calendarData.value = response.data
  } catch (error) {
    console.error('Failed to load calendar:', error)
    const errorMsg = getErrorMessage(error, 'Failed to load calendar. Please try again.')
    showError(errorMsg)
  } finally {
    loading.value = false
  }
}

const previousMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1)
  loadCalendar()
}

const nextMonth = () => {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1)
  loadCalendar()
}

const goToToday = () => {
  currentDate.value = new Date()
  loadCalendar()
}

const exportToCalendar = async () => {
  try {
    const year = currentDate.value.getFullYear()
    const month = currentDate.value.getMonth()
    
    // Export 3 months of data (current month + 2 months ahead)
    const fromDate = new Date(year, month, 1)
    const toDate = new Date(year, month + 3, 0, 23, 59, 59)
    
    await writerDashboardAPI.exportCalendarICS({
      from_date: fromDate.toISOString(),
      to_date: toDate.toISOString(),
    })
    
    showSuccess('Calendar exported successfully! You can now import it into Google Calendar, Outlook, or Apple Calendar.')
  } catch (error) {
    console.error('Failed to export calendar:', error)
    const errorMsg = getErrorMessage(error, 'Failed to export calendar. Please try again.')
    showError(errorMsg)
  }
}

const viewOrder = (orderId) => {
  router.push(`/orders/${orderId}`)
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatTimeRemaining = (hours) => {
  if (hours < 1) {
    return `${Math.round(hours * 60)}m`
  } else if (hours < 24) {
    return `${Math.round(hours)}h`
  } else {
    const days = Math.floor(hours / 24)
    const remainingHours = Math.round(hours % 24)
    return `${days}d ${remainingHours}h`
  }
}

onMounted(() => {
  loadCalendar()
})
</script>

<style scoped>
/* Styles are applied via Tailwind classes directly in template */
</style>


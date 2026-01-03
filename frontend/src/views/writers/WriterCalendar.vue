<template>
  <div class="space-y-6 p-6">
    <div class="flex items-center justify-between bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-100 shadow-sm">
      <div>
        <h1 class="text-3xl font-bold text-gray-900 flex items-center gap-3">
          <div class="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
            <CalendarIcon class="w-6 h-6 text-white" />
          </div>
          <span>Deadline Calendar</span>
        </h1>
        <p class="mt-2 text-gray-600">View your order deadlines in calendar format</p>
      </div>
      <div class="flex items-center gap-2">
        <button 
          @click="previousMonth" 
          class="btn btn-secondary text-sm hover:shadow-md transition-all duration-200 flex items-center gap-2 px-4 py-2 rounded-xl"
        >
          <ChevronLeftIcon class="w-4 h-4" />
          <span>Previous</span>
        </button>
        <button 
          @click="nextMonth" 
          class="btn btn-secondary text-sm hover:shadow-md transition-all duration-200 flex items-center gap-2 px-4 py-2 rounded-xl"
        >
          <span>Next</span>
          <ChevronRightIcon class="w-4 h-4" />
        </button>
        <button 
          @click="goToToday" 
          class="btn btn-primary text-sm hover:shadow-md transition-all duration-200 flex items-center gap-2 px-4 py-2 rounded-xl"
        >
          <CalendarDaysIcon class="w-4 h-4" />
          <span>Today</span>
        </button>
        <button 
          @click="loadCalendar" 
          :disabled="loading" 
          class="btn btn-secondary hover:shadow-md transition-all duration-200 flex items-center gap-2 px-4 py-2 rounded-xl"
        >
          <ArrowPathIcon :class="['w-4 h-4', loading && 'animate-spin']" />
          <span>{{ loading ? 'Loading...' : 'Refresh' }}</span>
        </button>
        <button 
          @click="exportToCalendar" 
          :disabled="loading || calendarData.total_orders === 0"
          class="btn btn-primary hover:shadow-md transition-all duration-200 flex items-center gap-2 px-4 py-2 rounded-xl"
          title="Export deadlines to your calendar (Google Calendar, Outlook, Apple Calendar)"
        >
          <ArrowDownTrayIcon class="w-4 h-4" />
          <span>Export to Calendar</span>
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="group relative bg-white rounded-2xl shadow-lg p-5 border-l-4 border-blue-500 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-br from-blue-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        <div class="relative flex items-center justify-between">
          <div class="flex-1 min-w-0">
            <p class="text-xs font-bold text-blue-600 uppercase tracking-wider mb-2">Total Orders</p>
            <p class="text-4xl font-extrabold text-blue-900">{{ calendarData.total_orders || 0 }}</p>
          </div>
          <div class="ml-4 shrink-0">
            <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
              <ClipboardDocumentListIcon class="w-6 h-6 text-white" />
            </div>
          </div>
        </div>
      </div>
      <div class="group relative bg-white rounded-2xl shadow-lg p-5 border-l-4 border-red-500 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-br from-red-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        <div class="relative flex items-center justify-between">
          <div class="flex-1 min-w-0">
            <p class="text-xs font-bold text-red-600 uppercase tracking-wider mb-2">Overdue</p>
            <p class="text-4xl font-extrabold text-red-900">{{ calendarData.overdue_count || 0 }}</p>
          </div>
          <div class="ml-4 shrink-0">
            <div class="w-12 h-12 bg-gradient-to-br from-red-500 to-red-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
              <ExclamationTriangleIcon class="w-6 h-6 text-white" />
            </div>
          </div>
        </div>
      </div>
      <div class="group relative bg-white rounded-2xl shadow-lg p-5 border-l-4 border-amber-500 hover:shadow-2xl hover:scale-[1.02] transition-all duration-300 overflow-hidden">
        <div class="absolute inset-0 bg-gradient-to-br from-amber-50/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        <div class="relative flex items-center justify-between">
          <div class="flex-1 min-w-0">
            <p class="text-xs font-bold text-amber-600 uppercase tracking-wider mb-2">Urgent (24h)</p>
            <p class="text-4xl font-extrabold text-amber-900">{{ calendarData.urgent_count || 0 }}</p>
          </div>
          <div class="ml-4 shrink-0">
            <div class="w-12 h-12 bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow">
              <ClockIcon class="w-6 h-6 text-white" />
            </div>
          </div>
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
          @click="day.orderCount > 0 ? selectDay(day) : null"
          :class="[
            'min-h-[100px] border rounded-lg p-2 transition-all duration-200',
            day.isCurrentMonth ? 'bg-white hover:bg-blue-50' : 'bg-gray-50',
            day.isToday ? 'ring-2 ring-primary-500 shadow-md' : 'hover:shadow-sm',
            day.orderCount > 0 ? 'cursor-pointer' : '',
            selectedDay?.dateKey === day.dateKey ? 'ring-2 ring-blue-500 bg-blue-50 shadow-lg' : '',
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

          <!-- Orders for this day (compact view) -->
          <div class="space-y-1">
            <div
              v-for="order in day.orders.slice(0, 2)"
              :key="order.id"
              @click.stop="viewOrder(order.id)"
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
            </div>
            <div
              v-if="day.orders.length > 2"
              class="text-xs text-gray-500 text-center py-1 font-medium"
            >
              +{{ day.orders.length - 2 }} more
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Day Tasks Sidebar -->
    <div
      v-if="selectedDay"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-end z-50"
      @click.self="selectedDay = null"
    >
      <div class="bg-white h-full w-full max-w-2xl shadow-2xl overflow-y-auto">
        <div class="sticky top-0 bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 shadow-lg">
          <div class="flex items-center justify-between">
            <div>
              <h2 class="text-2xl font-bold">Tasks Due</h2>
              <p class="text-blue-100 mt-1">{{ formatSelectedDate(selectedDay.date) }}</p>
            </div>
            <button
              @click="selectedDay = null"
              class="text-white hover:text-gray-200 w-10 h-10 flex items-center justify-center rounded-full hover:bg-white hover:bg-opacity-20 transition-colors"
            >
              <XMarkIcon class="w-6 h-6" />
            </button>
          </div>
          <div class="mt-4 flex gap-4">
            <div class="bg-white bg-opacity-20 rounded-lg px-4 py-2">
              <div class="text-xs text-blue-100">Total Tasks</div>
              <div class="text-xl font-bold">{{ selectedDay.orderCount }}</div>
            </div>
            <div v-if="selectedDay.overdueCount > 0" class="bg-red-500 bg-opacity-30 rounded-lg px-4 py-2">
              <div class="text-xs text-red-100">Overdue</div>
              <div class="text-xl font-bold">{{ selectedDay.overdueCount }}</div>
            </div>
            <div v-if="selectedDay.urgentCount > 0" class="bg-orange-500 bg-opacity-30 rounded-lg px-4 py-2">
              <div class="text-xs text-orange-100">Urgent</div>
              <div class="text-xl font-bold">{{ selectedDay.urgentCount }}</div>
            </div>
          </div>
        </div>

        <div class="p-6">
          <div v-if="selectedDay.orders.length === 0" class="text-center py-12">
            <div class="w-20 h-20 mx-auto mb-4 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center shadow-lg">
              <CalendarIcon class="w-10 h-10 text-gray-400" />
            </div>
            <p class="text-gray-500 text-lg font-medium">No tasks due on this day</p>
          </div>

          <div v-else class="space-y-4">
            <div
              v-for="order in sortedDayOrders"
              :key="order.id"
              :class="[
                'border rounded-lg p-4 transition-all duration-200 hover:shadow-lg cursor-pointer',
                order.is_overdue ? 'bg-red-50 border-red-300 hover:bg-red-100' :
                order.is_urgent ? 'bg-orange-50 border-orange-300 hover:bg-orange-100' :
                'bg-white border-gray-200 hover:bg-gray-50'
              ]"
              @click="viewOrder(order.id)"
            >
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <div class="flex items-center gap-3 mb-2">
                    <span
                      :class="[
                        'px-3 py-1 rounded-full text-xs font-bold',
                        order.is_overdue ? 'bg-red-200 text-red-800' :
                        order.is_urgent ? 'bg-orange-200 text-orange-800' :
                        'bg-blue-200 text-blue-800'
                      ]"
                    >
                      Order #{{ order.id }}
                    </span>
                    <span
                      :class="[
                        'px-2 py-1 rounded text-xs font-medium',
                        order.status === 'in_progress' ? 'bg-green-100 text-green-800' :
                        order.status === 'on_hold' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      ]"
                    >
                      {{ order.status.replace('_', ' ').toUpperCase() }}
                    </span>
                  </div>
                  
                  <h3 class="text-lg font-semibold text-gray-900 mb-2">{{ order.topic || 'No topic' }}</h3>
                  
                  <div class="grid grid-cols-2 gap-4 mt-3">
                    <div>
                      <div class="text-xs text-gray-500 mb-1">Service Type</div>
                      <div class="text-sm font-medium text-gray-900">{{ order.service_type }}</div>
                    </div>
                    <div>
                      <div class="text-xs text-gray-500 mb-1">Pages</div>
                      <div class="text-sm font-medium text-gray-900">{{ order.pages }} pages</div>
                    </div>
                    <div>
                      <div class="text-xs text-gray-500 mb-1">Deadline</div>
                      <div class="text-sm font-medium text-gray-900">{{ formatDate(order.deadline) }}</div>
                    </div>
                    <div>
                      <div class="text-xs text-gray-500 mb-1">Time Remaining</div>
                      <div
                        :class="[
                          'text-sm font-bold',
                          order.is_overdue ? 'text-red-600' :
                          order.is_urgent ? 'text-orange-600' :
                          'text-blue-600'
                        ]"
                      >
                        {{
                          order.is_overdue
                            ? 'OVERDUE'
                            : order.hours_remaining !== null
                            ? formatTimeRemaining(order.hours_remaining)
                            : 'N/A'
                        }}
                      </div>
                    </div>
                  </div>

                  <div v-if="order.total_price > 0" class="mt-3 pt-3 border-t border-gray-200">
                    <div class="text-xs text-gray-500 mb-1">Order Value</div>
                    <div class="text-lg font-bold text-green-600">${{ order.total_price.toFixed(2) }}</div>
                  </div>
                </div>

                <div class="ml-4">
                  <button
                    @click.stop="viewOrder(order.id)"
                    class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                  >
                    View Order
                  </button>
                </div>
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
          <button @click="selectedOrder = null" class="text-gray-400 hover:text-gray-600 w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors">
            <XMarkIcon class="w-5 h-5" />
          </button>
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
import {
  CalendarIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CalendarDaysIcon,
  ArrowPathIcon,
  ArrowDownTrayIcon,
  ClipboardDocumentListIcon,
  ExclamationTriangleIcon,
  ClockIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'
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
const selectedDay = ref(null)

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

const selectDay = (day) => {
  selectedDay.value = day
}

const viewOrder = (orderId) => {
  router.push(`/orders/${orderId}`)
}

const sortedDayOrders = computed(() => {
  if (!selectedDay.value) return []
  
  // Sort: overdue first, then urgent, then by deadline
  return [...selectedDay.value.orders].sort((a, b) => {
    if (a.is_overdue && !b.is_overdue) return -1
    if (!a.is_overdue && b.is_overdue) return 1
    if (a.is_urgent && !b.is_urgent) return -1
    if (!a.is_urgent && b.is_urgent) return 1
    return new Date(a.deadline) - new Date(b.deadline)
  })
})

const formatSelectedDate = (date) => {
  return date.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
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


<template>
  <div class="github-heatmap">
    <!-- Legend -->
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-3 text-sm text-gray-700">
        <span class="font-semibold">Less</span>
        <div class="flex gap-2">
          <div class="w-5 h-5 rounded-md bg-gray-100 border border-gray-200"></div>
          <div class="w-5 h-5 rounded-md bg-blue-200 border border-gray-200"></div>
          <div class="w-5 h-5 rounded-md bg-blue-400 border border-gray-200"></div>
          <div class="w-5 h-5 rounded-md bg-blue-600 border border-gray-200"></div>
          <div class="w-5 h-5 rounded-md bg-blue-800 border border-gray-200"></div>
        </div>
        <span class="font-semibold">More</span>
      </div>
      <div v-if="totalOrders > 0" class="text-base text-gray-800">
        <span class="font-bold text-gray-900 text-lg">{{ totalOrders }}</span> orders in <span class="font-semibold">{{ monthName }}</span>
      </div>
    </div>

    <!-- Calendar Grid -->
    <div class="flex gap-4 overflow-x-auto pb-3 items-start">
      <!-- Week labels -->
      <div class="flex flex-col pr-4 shrink-0">
        <div 
          v-for="(weekLabel, index) in weekLabels" 
          :key="index" 
          class="text-xs text-gray-600 flex items-center justify-center font-semibold"
          :style="{
            height: '20px',
            width: '20px',
            marginBottom: index < weekLabels.length - 1 ? '10px' : '0',
            lineHeight: '20px'
          }"
        >
          {{ weekLabel }}
        </div>
      </div>

      <!-- Calendar cells -->
      <div class="flex" style="gap: 10px;">
        <div
          v-for="(week, weekIndex) in calendarWeeks"
          :key="weekIndex"
          class="flex flex-col"
          style="gap: 10px;"
        >
          <div
            v-for="(day, dayIndex) in week"
            :key="dayIndex"
            :class="[
              'rounded-md cursor-pointer transition-all duration-200 shrink-0 border',
              getIntensityClass(day.count),
              day.count > 0 
                ? 'hover:ring-2 hover:ring-blue-500 hover:ring-offset-2 hover:scale-110 hover:shadow-md border-gray-300' 
                : 'border-gray-200'
            ]"
            style="width: 20px; height: 20px; box-sizing: border-box;"
            :title="day.tooltip"
            @mouseenter="showTooltip($event, day)"
            @mouseleave="hideTooltip"
          ></div>
        </div>
      </div>
    </div>

    <!-- Tooltip -->
    <div
      v-if="tooltip.visible"
      :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
      class="fixed z-50 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg shadow-xl pointer-events-none border border-gray-700"
      style="transform: translate(-50%, -100%); margin-top: -8px;"
    >
      <div class="font-semibold mb-1">{{ tooltip.date }}</div>
      <div class="text-gray-300">{{ tooltip.count }} {{ tooltip.count === 1 ? 'order' : 'orders' }}</div>
      <!-- Arrow -->
      <div class="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  data: {
    type: Array,
    default: () => [],
    validator: (value) => {
      return Array.isArray(value) && value.every(item => 
        item.day !== undefined && item.order_count !== undefined
      )
    }
  },
  year: {
    type: Number,
    default: () => new Date().getFullYear()
  },
  month: {
    type: Number,
    default: () => new Date().getMonth() + 1
  }
})

const tooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  date: '',
  count: 0
})

const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

const monthName = computed(() => monthNames[props.month - 1] || '')

const totalOrders = computed(() => {
  return props.data.reduce((sum, item) => sum + (item.order_count || 0), 0)
})

// Calculate max orders for dynamic intensity
const maxOrders = computed(() => {
  if (props.data.length === 0) return 0
  return Math.max(...props.data.map(item => item.order_count || 0))
})

// Get intensity class based on order count (dynamic based on max)
const getIntensityClass = (count) => {
  if (count === 0) return 'bg-gray-100'
  
  const max = maxOrders.value || 1
  const intensity = count / max
  
  if (intensity <= 0.2) return 'bg-blue-200'
  if (intensity <= 0.4) return 'bg-blue-400'
  if (intensity <= 0.7) return 'bg-blue-600'
  return 'bg-blue-800'
}

// Build calendar weeks
const calendarWeeks = computed(() => {
  const year = props.year
  const month = props.month - 1 // JavaScript months are 0-indexed
  
  // Create a map of day -> order_count from the data
  const ordersMap = new Map()
  props.data.forEach(item => {
    // Handle different data formats: item.day could be a number (day of month) or a date string
    let dayKey
    if (typeof item.day === 'number') {
      dayKey = item.day
    } else if (typeof item.day === 'string') {
      // Parse date string (format: "YYYY-MM-DD" or just day number)
      const parts = item.day.split('-')
      if (parts.length === 3) {
        dayKey = parseInt(parts[2], 10)
      } else {
        dayKey = parseInt(item.day, 10)
      }
    } else {
      return // Skip invalid entries
    }
    ordersMap.set(dayKey, item.order_count || 0)
  })

  // Get first day of month and last day
  const firstDay = new Date(year, month, 1)
  const lastDay = new Date(year, month + 1, 0)
  
  // Get the day of week for the first day (0 = Sunday, 6 = Saturday)
  const firstDayOfWeek = firstDay.getDay()
  const daysInMonth = lastDay.getDate()
  
  // Create calendar grid
  const weeks = []
  let currentWeek = []
  
  // Add empty cells for days before the first day of the month
  for (let i = 0; i < firstDayOfWeek; i++) {
    currentWeek.push({ day: null, count: 0, tooltip: '' })
  }
  
  // Add all days of the month
  for (let day = 1; day <= daysInMonth; day++) {
    const date = new Date(year, month, day)
    const count = ordersMap.get(day) || 0
    const dateStr = date.toLocaleDateString('en-US', { 
      weekday: 'short', 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    })
    
    currentWeek.push({
      day: day,
      count: count,
      date: dateStr,
      tooltip: `${dateStr}: ${count} ${count === 1 ? 'order' : 'orders'}`
    })
    
    // Start a new week on Sunday
    if (currentWeek.length === 7) {
      weeks.push(currentWeek)
      currentWeek = []
    }
  }
  
  // Fill remaining days of the last week with empty cells
  while (currentWeek.length < 7 && currentWeek.length > 0) {
    currentWeek.push({ day: null, count: 0, tooltip: '' })
  }
  
  if (currentWeek.length > 0) {
    weeks.push(currentWeek)
  }
  
  return weeks
})

// Week labels (first letter of weekday)
const weekLabels = computed(() => {
  const labels = ['S', 'M', 'T', 'W', 'T', 'F', 'S']
  // Only show labels if we have data
  return calendarWeeks.value.length > 0 ? labels : []
})

const showTooltip = (event, day) => {
  if (!day.day) return
  
  tooltip.value = {
    visible: true,
    x: event.pageX,
    y: event.pageY,
    date: day.date || day.tooltip.split(':')[0],
    count: day.count
  }
}

const hideTooltip = () => {
  tooltip.value.visible = false
}
</script>

<style scoped>
@reference "tailwindcss";

.github-heatmap {
  @apply w-full;
}

/* Custom scrollbar for horizontal scroll */
.github-heatmap::-webkit-scrollbar {
  height: 6px;
}

.github-heatmap::-webkit-scrollbar-track {
  @apply bg-gray-100 rounded;
}

.github-heatmap::-webkit-scrollbar-thumb {
  @apply bg-gray-300 rounded;
}

.github-heatmap::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-400;
}
</style>


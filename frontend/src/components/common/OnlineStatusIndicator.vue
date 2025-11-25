<template>
  <div class="flex items-center gap-2 group">
    <!-- Online Status with Tooltip -->
    <div class="relative">
      <div
        :class="[
          'w-3 h-3 rounded-full transition-all duration-300',
          isOnline ? 'bg-green-500 shadow-lg shadow-green-500/50' : 'bg-gray-400',
          isOnline ? 'animate-pulse' : ''
        ]"
        :title="tooltipText"
      ></div>
      <div
        v-if="isOnline"
        class="absolute inset-0 w-3 h-3 rounded-full bg-green-500 animate-ping opacity-75"
      ></div>
      
      <!-- Enhanced Tooltip -->
      <div
        v-if="showTooltip"
        class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-1.5 bg-gray-900 text-white text-xs rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50"
      >
        {{ tooltipText }}
        <div class="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
          <div class="border-4 border-transparent border-t-gray-900"></div>
        </div>
      </div>
    </div>
    
    <!-- Day/Night Indicator (for writers viewing clients) -->
    <div
      v-if="showTimeIndicator && timezone"
      :title="`${isDaytime ? 'Daytime' : 'Nighttime'} in ${timezone}`"
      class="text-lg transition-transform duration-300 hover:scale-110"
    >
      <span v-if="isDaytime" class="filter drop-shadow-sm">☀️</span>
      <span v-else class="filter drop-shadow-sm">🌙</span>
    </div>
    
    <!-- Status Text (optional) -->
    <span v-if="showText" class="text-xs text-gray-600 font-medium">
      {{ isOnline ? 'Online' : 'Offline' }}
    </span>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import apiClient from '@/api/client'

const props = defineProps({
  userId: {
    type: [Number, String],
    required: true
  },
  showTimeIndicator: {
    type: Boolean,
    default: false
  },
  showText: {
    type: Boolean,
    default: false
  },
  showTooltip: {
    type: Boolean,
    default: true
  },
  autoRefresh: {
    type: Boolean,
    default: true
  },
  refreshInterval: {
    type: Number,
    default: 30000 // 30 seconds
  }
})

const tooltipText = computed(() => {
  let text = isOnline.value ? 'Online' : 'Offline'
  if (timezone.value && showTimeIndicator.value) {
    text += ` • ${isDaytime.value ? 'Daytime' : 'Nighttime'} in ${timezone.value}`
  }
  return text
})

const isOnline = ref(false)
const timezone = ref(null)
const isDaytime = ref(true)

let refreshTimer = null

const loadStatus = async () => {
  try {
    const response = await apiClient.get(`/users/users/${props.userId}/get_user_online_status/`)
    const data = response.data
    isOnline.value = data.is_online
    timezone.value = data.timezone
    isDaytime.value = data.is_daytime
  } catch (error) {
    console.error('Failed to load online status:', error)
  }
}

onMounted(() => {
  loadStatus()
  if (props.autoRefresh) {
    refreshTimer = setInterval(loadStatus, props.refreshInterval)
  }
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>


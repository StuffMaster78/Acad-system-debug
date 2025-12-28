<template>
  <div 
    class="status-card group relative overflow-hidden rounded-xl border transition-all duration-300 hover:shadow-xl hover:scale-[1.02] cursor-pointer h-full flex flex-col backdrop-blur-sm"
    :class="cardClasses"
    @click="$emit('click')"
  >
    <!-- Decorative gradient overlay -->
    <div class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" :class="gradientOverlayClass"></div>
    
    <!-- Content -->
    <div class="relative p-4 sm:p-5 flex flex-col h-full z-10">
      <!-- Header Section: Icon, Label, Badge -->
      <div class="flex items-start justify-between mb-3 gap-3">
        <div class="flex items-start gap-3 flex-1 min-w-0">
          <!-- Icon Container with modern styling -->
          <div 
            class="icon-container flex-shrink-0 rounded-xl p-2.5 transition-all duration-300 group-hover:scale-110 group-hover:rotate-3"
            :class="iconContainerClass"
          >
            <svg 
              v-if="iconSvg" 
              class="w-5 h-5" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
              :class="iconColorClass"
            >
              <path 
                stroke-linecap="round" 
                stroke-linejoin="round" 
                stroke-width="2" 
                :d="iconSvg"
              />
            </svg>
            <span v-else class="text-lg leading-none" :class="iconColorClass">{{ icon }}</span>
          </div>
          
          <!-- Label and Subtitle -->
          <div class="flex-1 min-w-0 pt-0.5">
            <h3 class="text-xs font-bold text-gray-800 dark:text-gray-100 uppercase tracking-wider leading-tight">
              {{ label }}
            </h3>
            <p v-if="subtitle" class="text-[10px] text-gray-500 dark:text-gray-400 leading-tight font-medium mt-0.5">
              {{ subtitle }}
            </p>
          </div>
        </div>
        
        <!-- Badge -->
        <div v-if="badge" class="px-2 py-1 text-[10px] font-bold rounded-full shrink-0 whitespace-nowrap shadow-sm" :class="badgeClass">
          {{ badge }}
        </div>
      </div>
      
      <!-- Value Section -->
      <div class="mt-auto pt-2.5">
        <div class="flex items-baseline gap-1.5 flex-wrap">
          <span class="text-2xl sm:text-3xl font-extrabold leading-none tracking-tight" :class="valueClass">
            {{ formattedValue }}
          </span>
          <span v-if="unit" class="text-sm font-semibold text-gray-500 dark:text-gray-400">
            {{ unit }}
          </span>
        </div>
      </div>
      
      <!-- Trend Section -->
      <div v-if="trend !== null" class="mt-3 pt-2.5 border-t border-gray-200/50 dark:border-gray-700/50">
        <div class="flex items-center gap-1.5 text-[10px] font-semibold">
          <span :class="trendClass">
            <svg v-if="trend > 0" class="w-3 h-3 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
            <svg v-else-if="trend < 0" class="w-3 h-3 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
            </svg>
            <svg v-else class="w-3 h-3 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 12h14" />
            </svg>
            {{ Math.abs(trend) }}%
          </span>
          <span class="text-gray-500 dark:text-gray-400 hidden sm:inline font-medium">vs last period</span>
        </div>
      </div>
      
      <!-- Description -->
      <div v-if="description" class="mt-2.5 pt-2 text-[10px] text-gray-600 dark:text-gray-400 leading-relaxed font-medium">
        {{ description }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    required: true
  },
  icon: {
    type: String,
    default: '📊'
  },
  iconSvg: {
    type: String,
    default: null
  },
  variant: {
    type: String,
    default: 'default', // 'default', 'primary', 'success', 'warning', 'danger', 'info'
    validator: (value) => ['default', 'primary', 'success', 'warning', 'danger', 'info'].includes(value)
  },
  subtitle: {
    type: String,
    default: null
  },
  unit: {
    type: String,
    default: null
  },
  trend: {
    type: Number,
    default: null
  },
  badge: {
    type: String,
    default: null
  },
  description: {
    type: String,
    default: null
  },
  formatValue: {
    type: Function,
    default: null
  }
})

const emit = defineEmits(['click'])

// Icon SVG paths for common icons
const iconPaths = {
  'document': 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
  'check-circle': 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z',
  'clock': 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z',
  'user': 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
  'dollar-sign': 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  'chart-bar': 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z',
  'cog': 'M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z M15 12a3 3 0 11-6 0 3 3 0 016 0z',
  'hourglass': 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'
}

const iconSvg = computed(() => {
  if (props.iconSvg) return props.iconSvg
  // Try to match icon prop to SVG path
  const iconKey = props.icon.toLowerCase().replace(/[^a-z]/g, '')
  return iconPaths[iconKey] || null
})

const cardClasses = computed(() => {
  const variants = {
    default: 'bg-white/80 dark:bg-gray-800/80 border-gray-200/60 dark:border-gray-700/60 shadow-md hover:border-gray-300 dark:hover:border-gray-600',
    primary: 'bg-gradient-to-br from-blue-50/90 via-blue-50/80 to-blue-100/90 dark:from-blue-900/40 dark:via-blue-800/30 dark:to-blue-900/40 border-blue-200/80 dark:border-blue-700/60 shadow-lg hover:border-blue-300 dark:hover:border-blue-600',
    success: 'bg-gradient-to-br from-green-50/90 via-emerald-50/80 to-green-100/90 dark:from-green-900/40 dark:via-emerald-800/30 dark:to-green-900/40 border-green-200/80 dark:border-green-700/60 shadow-lg hover:border-green-300 dark:hover:border-green-600',
    warning: 'bg-gradient-to-br from-amber-50/90 via-yellow-50/80 to-amber-100/90 dark:from-amber-900/40 dark:via-yellow-800/30 dark:to-amber-900/40 border-amber-200/80 dark:border-amber-700/60 shadow-lg hover:border-amber-300 dark:hover:border-amber-600',
    danger: 'bg-gradient-to-br from-red-50/90 via-rose-50/80 to-red-100/90 dark:from-red-900/40 dark:via-rose-800/30 dark:to-red-900/40 border-red-200/80 dark:border-red-700/60 shadow-lg hover:border-red-300 dark:hover:border-red-600',
    info: 'bg-gradient-to-br from-indigo-50/90 via-purple-50/80 to-indigo-100/90 dark:from-indigo-900/40 dark:via-purple-800/30 dark:to-indigo-900/40 border-indigo-200/80 dark:border-indigo-700/60 shadow-lg hover:border-indigo-300 dark:hover:border-indigo-600'
  }
  return variants[props.variant] || variants.default
})

const gradientOverlayClass = computed(() => {
  const variants = {
    default: 'bg-gradient-to-br from-gray-50/50 to-transparent',
    primary: 'bg-gradient-to-br from-blue-100/30 to-transparent',
    success: 'bg-gradient-to-br from-green-100/30 to-transparent',
    warning: 'bg-gradient-to-br from-amber-100/30 to-transparent',
    danger: 'bg-gradient-to-br from-red-100/30 to-transparent',
    info: 'bg-gradient-to-br from-indigo-100/30 to-transparent'
  }
  return variants[props.variant] || variants.default
})

const iconContainerClass = computed(() => {
  const variants = {
    default: 'bg-gray-100/80 dark:bg-gray-700/80',
    primary: 'bg-blue-100/90 dark:bg-blue-800/60',
    success: 'bg-green-100/90 dark:bg-green-800/60',
    warning: 'bg-amber-100/90 dark:bg-amber-800/60',
    danger: 'bg-red-100/90 dark:bg-red-800/60',
    info: 'bg-indigo-100/90 dark:bg-indigo-800/60'
  }
  return variants[props.variant] || variants.default
})

const iconColorClass = computed(() => {
  const variants = {
    default: 'text-gray-700 dark:text-gray-300',
    primary: 'text-blue-700 dark:text-blue-300',
    success: 'text-green-700 dark:text-green-300',
    warning: 'text-amber-700 dark:text-amber-300',
    danger: 'text-red-700 dark:text-red-300',
    info: 'text-indigo-700 dark:text-indigo-300'
  }
  return variants[props.variant] || variants.default
})

const valueClass = computed(() => {
  const variants = {
    default: 'text-gray-900 dark:text-white',
    primary: 'text-blue-900 dark:text-blue-100',
    success: 'text-green-900 dark:text-green-100',
    warning: 'text-amber-900 dark:text-amber-100',
    danger: 'text-red-900 dark:text-red-100',
    info: 'text-indigo-900 dark:text-indigo-100'
  }
  return variants[props.variant] || variants.default
})

const badgeClass = computed(() => {
  const variants = {
    default: 'bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200',
    primary: 'bg-blue-500 dark:bg-blue-600 text-white',
    success: 'bg-green-500 dark:bg-green-600 text-white',
    warning: 'bg-amber-500 dark:bg-amber-600 text-white',
    danger: 'bg-red-500 dark:bg-red-600 text-white',
    info: 'bg-indigo-500 dark:bg-indigo-600 text-white'
  }
  return variants[props.variant] || variants.default
})

const trendClass = computed(() => {
  if (props.trend === null) return ''
  if (props.trend > 0) return 'text-green-600 dark:text-green-400 font-bold'
  if (props.trend < 0) return 'text-red-600 dark:text-red-400 font-bold'
  return 'text-gray-600 dark:text-gray-400 font-semibold'
})

const formattedValue = computed(() => {
  if (props.formatValue) {
    return props.formatValue(props.value)
  }
  if (typeof props.value === 'number') {
    return props.value.toLocaleString()
  }
  return props.value
})
</script>

<style scoped>
.status-card {
  min-height: 110px;
  position: relative;
}

@media (min-width: 640px) {
  .status-card {
    min-height: 115px;
  }
}

@media (min-width: 1024px) {
  .status-card {
    min-height: 120px;
  }
}

/* Smooth transitions */
.status-card {
  will-change: transform;
}

.icon-container {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.status-card:hover .icon-container {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}
</style>

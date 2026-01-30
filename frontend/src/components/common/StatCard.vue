<template>
  <div
    :class="[
      'group relative bg-white dark:bg-slate-900 rounded-2xl shadow-sm p-6 border transition-all duration-300 overflow-hidden',
      clickable ? 'cursor-pointer hover:shadow-xl hover:-translate-y-1' : 'hover:shadow-md',
      'border-gray-100 dark:border-slate-800 hover:border-gray-200 dark:hover:border-slate-700'
    ]"
    @click="handleClick"
  >
    <!-- Gradient Background Overlay -->
    <div 
      v-if="gradient"
      class="absolute inset-0 opacity-5 group-hover:opacity-10 transition-opacity duration-300 pointer-events-none"
      :class="gradientClass"
    />

    <!-- Content -->
    <div class="relative z-10">
      <!-- Header: Label + Icon -->
      <div class="flex items-start justify-between mb-4">
        <div class="flex-1 min-w-0">
          <p class="text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wider">
            {{ label }}
          </p>
        </div>

        <!-- Icon -->
        <StatIcon 
          v-if="iconName"
          :name="iconName" 
          :color="color"
          :size="iconSize"
          :gradient="iconGradient"
          :animated="true"
          class="ml-3 shrink-0"
        />
      </div>

      <!-- Value -->
      <div class="mb-3">
        <div class="flex items-baseline gap-2">
          <!-- Main Value -->
          <p 
            :class="[
              'font-bold tracking-tight transition-all duration-200',
              valueColorClass,
              valueSize
            ]"
          >
            <span v-if="loading" class="animate-pulse">—</span>
            <template v-else>
              <CountUp v-if="animateValue && typeof parsedValue === 'number'" :end-value="parsedValue" :duration="1000" />
              <template v-else>{{ formattedValue }}</template>
            </template>
          </p>

          <!-- Change Indicator -->
          <div 
            v-if="change !== null && change !== undefined && !loading"
            :class="[
              'flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold transition-all',
              changeColorClass
            ]"
          >
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path 
                v-if="change > 0" 
                stroke-linecap="round" 
                stroke-linejoin="round" 
                stroke-width="2.5" 
                d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" 
              />
              <path 
                v-else-if="change < 0" 
                stroke-linecap="round" 
                stroke-linejoin="round" 
                stroke-width="2.5" 
                d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" 
              />
              <path 
                v-else 
                stroke-linecap="round" 
                stroke-linejoin="round" 
                stroke-width="2.5" 
                d="M5 12h14" 
              />
            </svg>
            <span>{{ formattedChange }}</span>
          </div>
        </div>

        <!-- Subtitle/Description -->
        <p v-if="subtitle" class="text-xs text-gray-500 dark:text-slate-400 mt-2 leading-relaxed">
          <span v-if="loading" class="animate-pulse">Loading...</span>
          <span v-else>{{ subtitle }}</span>
        </p>
      </div>

      <!-- Sparkline Chart (Optional) -->
      <div v-if="trend && trend.length > 0" class="h-12 mt-4">
        <svg class="w-full h-full" viewBox="0 0 100 40" preserveAspectRatio="none">
          <polyline
            :points="sparklinePoints"
            :class="['fill-none stroke-2 transition-all duration-300', sparklineColorClass]"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
          <polyline
            :points="sparklineAreaPoints"
            :class="['transition-all duration-300', sparklineAreaClass]"
            stroke="none"
          />
        </svg>
      </div>

      <!-- Footer Action/Link -->
      <div v-if="actionLabel" class="mt-4 pt-4 border-t border-gray-100 dark:border-slate-800">
        <div class="flex items-center justify-between text-sm font-medium group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
          <span>{{ actionLabel }}</span>
          <svg class="w-4 h-4 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
          </svg>
        </div>
      </div>
    </div>

    <!-- Loading Overlay -->
    <div 
      v-if="loading && showLoadingOverlay"
      class="absolute inset-0 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm flex items-center justify-center z-20 rounded-2xl"
    >
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import StatIcon from './StatIcon.vue'
import { formatPercentageChange } from '@/utils/currencyFormatter'

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  subtitle: {
    type: String,
    default: null
  },
  change: {
    type: Number,
    default: null
  },
  iconName: {
    type: String,
    default: null
  },
  color: {
    type: String,
    default: 'blue',
    validator: (value) => ['blue', 'green', 'emerald', 'purple', 'amber', 'red', 'indigo', 'pink', 'cyan', 'orange', 'teal'].includes(value)
  },
  gradient: {
    type: Boolean,
    default: true
  },
  iconGradient: {
    type: Boolean,
    default: true
  },
  iconSize: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg', 'xl'].includes(value)
  },
  valueSize: {
    type: String,
    default: 'text-3xl',
    validator: (value) => ['text-xl', 'text-2xl', 'text-3xl', 'text-4xl', 'text-5xl'].includes(value)
  },
  trend: {
    type: Array,
    default: null
  },
  actionLabel: {
    type: String,
    default: null
  },
  clickable: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  showLoadingOverlay: {
    type: Boolean,
    default: false
  },
  animateValue: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['click'])

// Parse and format value
const parsedValue = computed(() => {
  if (typeof props.value === 'number') return props.value
  const num = parseFloat(props.value)
  return isNaN(num) ? props.value : num
})

const formattedValue = computed(() => {
  if (typeof parsedValue.value === 'number') {
    return parsedValue.value.toLocaleString()
  }
  return props.value
})

// Gradient class for background
const gradientClass = computed(() => {
  const gradients = {
    blue: 'bg-gradient-to-br from-blue-500 to-blue-600',
    green: 'bg-gradient-to-br from-green-500 to-green-600',
    emerald: 'bg-gradient-to-br from-emerald-500 to-emerald-600',
    purple: 'bg-gradient-to-br from-purple-500 to-purple-600',
    amber: 'bg-gradient-to-br from-amber-500 to-amber-600',
    red: 'bg-gradient-to-br from-red-500 to-red-600',
    indigo: 'bg-gradient-to-br from-indigo-500 to-indigo-600',
    pink: 'bg-gradient-to-br from-pink-500 to-pink-600',
    cyan: 'bg-gradient-to-br from-cyan-500 to-cyan-600',
    orange: 'bg-gradient-to-br from-orange-500 to-orange-600',
    teal: 'bg-gradient-to-br from-teal-500 to-teal-600',
  }
  return gradients[props.color]
})

// Value color class
const valueColorClass = computed(() => {
  const colors = {
    blue: 'text-blue-700 dark:text-blue-400',
    green: 'text-green-700 dark:text-green-400',
    emerald: 'text-emerald-700 dark:text-emerald-400',
    purple: 'text-purple-700 dark:text-purple-400',
    amber: 'text-amber-700 dark:text-amber-400',
    red: 'text-red-700 dark:text-red-400',
    indigo: 'text-indigo-700 dark:text-indigo-400',
    pink: 'text-pink-700 dark:text-pink-400',
    cyan: 'text-cyan-700 dark:text-cyan-400',
    orange: 'text-orange-700 dark:text-orange-400',
    teal: 'text-teal-700 dark:text-teal-400',
  }
  return colors[props.color]
})

// Change color class
const changeColorClass = computed(() => {
  if (props.change > 0) {
    return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
  } else if (props.change < 0) {
    return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
  } else {
    return 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
  }
})

// Formatted change value
const formattedChange = computed(() => {
  return formatPercentageChange(props.change)
})

// Sparkline calculations
const sparklinePoints = computed(() => {
  if (!props.trend || props.trend.length === 0) return ''
  
  const max = Math.max(...props.trend)
  const min = Math.min(...props.trend)
  const range = max - min || 1
  
  return props.trend
    .map((value, index) => {
      const x = (index / (props.trend.length - 1)) * 100
      const y = 35 - ((value - min) / range) * 30
      return `${x},${y}`
    })
    .join(' ')
})

const sparklineAreaPoints = computed(() => {
  if (!props.trend || props.trend.length === 0) return ''
  return `0,40 ${sparklinePoints.value} 100,40`
})

const sparklineColorClass = computed(() => {
  const colors = {
    blue: 'stroke-blue-500',
    green: 'stroke-green-500',
    emerald: 'stroke-emerald-500',
    purple: 'stroke-purple-500',
    amber: 'stroke-amber-500',
    red: 'stroke-red-500',
    indigo: 'stroke-indigo-500',
    pink: 'stroke-pink-500',
    cyan: 'stroke-cyan-500',
    orange: 'stroke-orange-500',
    teal: 'stroke-teal-500',
  }
  return colors[props.color]
})

const sparklineAreaClass = computed(() => {
  const colors = {
    blue: 'fill-blue-500/10',
    green: 'fill-green-500/10',
    emerald: 'fill-emerald-500/10',
    purple: 'fill-purple-500/10',
    amber: 'fill-amber-500/10',
    red: 'fill-red-500/10',
    indigo: 'fill-indigo-500/10',
    pink: 'fill-pink-500/10',
    cyan: 'fill-cyan-500/10',
    orange: 'fill-orange-500/10',
    teal: 'fill-teal-500/10',
  }
  return colors[props.color]
})

function handleClick() {
  if (props.clickable) {
    emit('click')
  }
}

// Simple count-up animation component
const CountUp = {
  props: ['endValue', 'duration'],
  setup(props) {
    const displayValue = ref(0)

    onMounted(() => {
      const start = 0
      const end = props.endValue
      const duration = props.duration || 1000
      const startTime = Date.now()

      const animate = () => {
        const elapsed = Date.now() - startTime
        const progress = Math.min(elapsed / duration, 1)
        
        // Easing function (ease-out)
        const easeOut = 1 - Math.pow(1 - progress, 3)
        
        displayValue.value = Math.round(start + (end - start) * easeOut)

        if (progress < 1) {
          requestAnimationFrame(animate)
        }
      }

      animate()
    })

    return { displayValue }
  },
  template: '<span>{{ displayValue.toLocaleString() }}</span>'
}
</script>

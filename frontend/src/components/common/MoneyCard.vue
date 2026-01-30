<template>
  <div
    class="group bg-white dark:bg-slate-800 rounded-2xl shadow-sm p-6 border border-gray-100 dark:border-slate-700 hover:shadow-xl transition-all duration-300 hover:border-gray-200 dark:hover:border-slate-600 relative overflow-hidden"
    @mouseenter="showTooltip = true"
    @mouseleave="showTooltip = false"
  >
    <!-- Gradient overlay on hover -->
    <div 
      class="absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-5 transition-opacity duration-300 rounded-2xl pointer-events-none"
      :class="gradientClass"
    ></div>

    <!-- Content -->
    <div class="relative z-10">
      <div class="flex items-start justify-between mb-4">
        <!-- Label -->
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
          size="md"
          :gradient="true"
          class="ml-3 shrink-0"
        />
      </div>

      <!-- Value with dynamic sizing -->
      <div class="mb-3">
        <!-- Main Value -->
        <div class="flex items-baseline gap-2">
          <p 
            :class="[
              'font-bold tracking-tight transition-all duration-200',
              valueColorClass,
              dynamicFontSize
            ]"
            :title="currencyData.abbreviated ? currencyData.full : null"
          >
            {{ currencyData.display }}
          </p>
          
          <!-- Abbreviated indicator -->
          <span 
            v-if="currencyData.abbreviated"
            class="text-xs text-gray-400 dark:text-slate-500 font-medium"
            :title="`Full amount: ${currencyData.full}`"
          >
            <svg class="w-3 h-3 inline-block" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </span>
        </div>

        <!-- Subtitle/Context -->
        <p v-if="subtitle" class="text-xs text-gray-500 dark:text-slate-400 mt-2 leading-relaxed">
          {{ subtitle }}
        </p>
      </div>

      <!-- Change indicator -->
      <div v-if="change !== null && change !== undefined" class="flex items-center gap-2">
        <div 
          class="flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold"
          :class="changeColorClass"
        >
          <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
        <span v-if="changePeriod" class="text-xs text-gray-400 dark:text-slate-500">
          {{ changePeriod }}
        </span>
      </div>
    </div>

    <!-- Tooltip for full value (when abbreviated) -->
    <Transition name="tooltip-fade">
      <div
        v-if="showTooltip && currencyData.abbreviated"
        class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50 pointer-events-none"
      >
        <div class="bg-gray-900 dark:bg-gray-800 text-white text-sm py-2 px-3 rounded-lg shadow-xl whitespace-nowrap border border-gray-700">
          <div class="font-semibold">{{ currencyData.full }}</div>
          <div class="absolute top-full left-1/2 -translate-x-1/2 -mt-1">
            <div class="border-4 border-transparent border-t-gray-900 dark:border-t-gray-800"></div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import StatIcon from './StatIcon.vue'
import { formatSmartCurrency, getDynamicFontSize, formatPercentageChange } from '@/utils/currencyFormatter'

const props = defineProps({
  amount: {
    type: Number,
    required: true
  },
  label: {
    type: String,
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
  changePeriod: {
    type: String,
    default: null
  },
  iconName: {
    type: String,
    default: 'dollar'
  },
  color: {
    type: String,
    default: 'green',
    validator: (value) => ['blue', 'green', 'emerald', 'purple', 'amber', 'red', 'indigo', 'pink', 'cyan', 'orange'].includes(value)
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg', 'xl'].includes(value)
  },
  maxLength: {
    type: Number,
    default: 10
  }
})

const showTooltip = ref(false)

// Format currency with smart abbreviation
const currencyData = computed(() => {
  return formatSmartCurrency(props.amount, {
    maxLength: props.maxLength,
    minDecimals: 0,
    maxDecimals: 2
  })
})

// Dynamic font size based on value length
const dynamicFontSize = computed(() => {
  const baseSizes = {
    sm: 'text-xl',
    md: 'text-3xl',
    lg: 'text-4xl',
    xl: 'text-5xl'
  }
  return getDynamicFontSize(currencyData.value.display, baseSizes[props.size])
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
  }
  return colors[props.color]
})

// Gradient class for hover effect
const gradientClass = computed(() => {
  const gradients = {
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
    emerald: 'from-emerald-500 to-emerald-600',
    purple: 'from-purple-500 to-purple-600',
    amber: 'from-amber-500 to-amber-600',
    red: 'from-red-500 to-red-600',
    indigo: 'from-indigo-500 to-indigo-600',
    pink: 'from-pink-500 to-pink-600',
    cyan: 'from-cyan-500 to-cyan-600',
    orange: 'from-orange-500 to-orange-600',
  }
  return gradients[props.color]
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
</script>

<style scoped>
.tooltip-fade-enter-active,
.tooltip-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.tooltip-fade-enter-from,
.tooltip-fade-leave-to {
  opacity: 0;
  transform: translateY(4px);
}

.tooltip-fade-enter-to,
.tooltip-fade-leave-from {
  opacity: 1;
  transform: translateY(0);
}
</style>

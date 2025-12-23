<template>
  <div class="relative inline-block">
    <span
      :class="[
        'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold transition-all',
        badgeClasses,
        showTooltip ? 'cursor-help' : '',
        pulse ? 'animate-pulse' : ''
      ]"
      @mouseenter="showTooltip && (tooltipVisible = true)"
      @mouseleave="tooltipVisible = false"
    >
      <span v-if="showIcon" class="text-sm">{{ statusConfig.icon }}</span>
      <span>{{ displayLabel }}</span>
      <span v-if="showPriority && statusConfig.priority === 'critical'" class="ml-1">🚨</span>
      <span v-if="showPriority && statusConfig.priority === 'high'" class="ml-1">⚠️</span>
    </span>
    
    <!-- Tooltip -->
    <Transition name="fade">
      <div
        v-if="tooltipVisible && showTooltip && statusConfig.description"
        class="absolute z-50 bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg shadow-lg whitespace-nowrap pointer-events-none"
        style="min-width: 200px;"
      >
        <div class="font-semibold mb-1">{{ statusConfig.label }}</div>
        <div class="text-gray-300">{{ statusConfig.description }}</div>
        <div v-if="statusConfig.category" class="mt-1 text-xs text-gray-400">
          Category: {{ categoryLabel }}
        </div>
        <!-- Tooltip arrow -->
        <div class="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
          <div class="w-2 h-2 bg-gray-900 transform rotate-45"></div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getStatusConfig, STATUS_CATEGORIES } from '@/utils/orderStatus'

const props = defineProps({
  status: {
    type: String,
    required: true
  },
  label: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'default', // default, outline, solid
    validator: (value) => ['default', 'outline', 'solid'].includes(value)
  },
  showIcon: {
    type: Boolean,
    default: true
  },
  showTooltip: {
    type: Boolean,
    default: true
  },
  showPriority: {
    type: Boolean,
    default: false
  },
  pulse: {
    type: Boolean,
    default: false
  },
  size: {
    type: String,
    default: 'default', // default, sm, lg
    validator: (value) => ['default', 'sm', 'lg'].includes(value)
  }
})

const tooltipVisible = ref(false)

const statusConfig = computed(() => getStatusConfig(props.status))

const displayLabel = computed(() => {
  return props.label || statusConfig.value.label
})

const categoryLabel = computed(() => {
  return STATUS_CATEGORIES[statusConfig.value.category] || statusConfig.value.category
})

const badgeClasses = computed(() => {
  const baseClasses = statusConfig.value.bgColor + ' ' + statusConfig.value.textColor
  
  if (props.variant === 'outline') {
    return `${statusConfig.value.borderColor} border-2 ${statusConfig.value.textColor} bg-transparent`
  }
  
  if (props.variant === 'solid') {
    // Solid variant with darker background
    const colorMap = {
      gray: 'bg-gray-600 text-white',
      yellow: 'bg-yellow-600 text-white',
      orange: 'bg-orange-600 text-white',
      red: 'bg-red-600 text-white',
      green: 'bg-green-600 text-white',
      blue: 'bg-blue-600 text-white',
      purple: 'bg-purple-600 text-white',
      indigo: 'bg-indigo-600 text-white',
      teal: 'bg-teal-600 text-white',
      amber: 'bg-amber-600 text-white',
      emerald: 'bg-emerald-600 text-white',
      lime: 'bg-lime-600 text-white',
      cyan: 'bg-cyan-600 text-white',
      pink: 'bg-pink-600 text-white',
      slate: 'bg-slate-600 text-white'
    }
    return colorMap[statusConfig.value.color] || baseClasses
  }
  
  // Size variants
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    default: 'px-3 py-1.5 text-xs',
    lg: 'px-4 py-2 text-sm'
  }
  
  return `${baseClasses} ${sizeClasses[props.size]}`
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>


<template>
  <div 
    class="relative group"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
    @focusin="handleFocusIn"
    @focusout="handleFocusOut"
  >
    <slot />
    
    <!-- Tooltip for collapsed sidebar -->
    <Transition name="tooltip-fade">
      <div
        v-if="show && collapsed"
        ref="tooltipRef"
        class="absolute left-full ml-3 top-1/2 -translate-y-1/2 z-[100] pointer-events-none whitespace-nowrap"
        role="tooltip"
        :aria-label="text"
      >
        <div class="bg-gray-900 dark:bg-gray-800 text-white text-xs font-medium py-2 px-3 rounded-lg shadow-xl border border-gray-700 dark:border-gray-600 backdrop-blur-sm">
          {{ text }}
          <!-- Arrow -->
          <div class="absolute right-full top-1/2 -translate-y-1/2 border-4 border-transparent border-r-gray-900 dark:border-r-gray-800"></div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onUnmounted } from 'vue'

const props = defineProps({
  text: {
    type: String,
    required: true
  },
  collapsed: {
    type: Boolean,
    default: false
  },
  delay: {
    type: Number,
    default: 300 // Delay in milliseconds before showing tooltip
  }
})

const show = ref(false)
const tooltipRef = ref(null)
let showTimeout = null
let hideTimeout = null

const handleMouseEnter = () => {
  if (!props.collapsed) return
  
  // Clear any pending hide
  if (hideTimeout) {
    clearTimeout(hideTimeout)
    hideTimeout = null
  }
  
  // Show with delay for better UX
  showTimeout = setTimeout(() => {
    if (props.collapsed) {
      show.value = true
      // Adjust position if needed
      nextTick(() => {
        adjustTooltipPosition()
      })
    }
  }, props.delay)
}

const handleMouseLeave = () => {
  // Clear any pending show
  if (showTimeout) {
    clearTimeout(showTimeout)
    showTimeout = null
  }
  
  // Hide immediately
  show.value = false
}

const handleFocusIn = () => {
  if (props.collapsed) {
    handleMouseEnter()
  }
}

const handleFocusOut = () => {
  handleMouseLeave()
}

// Adjust tooltip position to prevent overflow
const adjustTooltipPosition = () => {
  if (!tooltipRef.value) return
  
  const tooltip = tooltipRef.value
  const rect = tooltip.getBoundingClientRect()
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight
  
  // Check if tooltip overflows right edge
  if (rect.right > viewportWidth - 10) {
    // Position to the left instead
    tooltip.classList.remove('left-full', 'ml-3')
    tooltip.classList.add('right-full', 'mr-3')
    // Flip arrow
    const arrow = tooltip.querySelector('div[class*="border-r-gray"]')
    if (arrow) {
      arrow.classList.remove('right-full', 'border-r-gray-900', 'dark:border-r-gray-800')
      arrow.classList.add('left-full', 'border-l-gray-900', 'dark:border-l-gray-800')
    }
  } else {
    // Reset to default (right side)
    tooltip.classList.remove('right-full', 'mr-3')
    tooltip.classList.add('left-full', 'ml-3')
  }
  
  // Check if tooltip overflows bottom
  if (rect.bottom > viewportHeight - 10) {
    tooltip.style.top = 'auto'
    tooltip.style.bottom = '10px'
    tooltip.style.transform = 'translateY(0)'
  }
  
  // Check if tooltip overflows top
  if (rect.top < 10) {
    tooltip.style.top = '10px'
    tooltip.style.transform = 'translateY(0)'
  }
}

// Watch for collapsed changes
watch(() => props.collapsed, (newVal) => {
  if (!newVal) {
    if (showTimeout) {
      clearTimeout(showTimeout)
      showTimeout = null
    }
    show.value = false
  }
})

// Cleanup on unmount
onUnmounted(() => {
  if (showTimeout) clearTimeout(showTimeout)
  if (hideTimeout) clearTimeout(hideTimeout)
})
</script>

<style scoped>
.tooltip-fade-enter-active,
.tooltip-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.tooltip-fade-enter-from,
.tooltip-fade-leave-to {
  opacity: 0;
  transform: translateX(-8px) translateY(-50%);
}

.tooltip-fade-enter-to,
.tooltip-fade-leave-from {
  opacity: 1;
  transform: translateX(0) translateY(-50%);
}
</style>


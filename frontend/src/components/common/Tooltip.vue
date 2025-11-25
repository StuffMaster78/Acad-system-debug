<template>
  <div class="tooltip-wrapper relative inline-block">
    <button
      type="button"
      @mouseenter="showTooltip = true"
      @mouseleave="showTooltip = false"
      @focus="showTooltip = true"
      @blur="showTooltip = false"
      class="tooltip-trigger"
      :aria-label="text"
    >
      <svg
        class="w-4 h-4 text-gray-400 hover:text-gray-600 transition-colors"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    </button>
    
    <Transition name="tooltip">
      <div
        v-if="showTooltip"
        class="tooltip-content"
        :class="[
          position === 'top' ? 'bottom-full left-1/2 -translate-x-1/2 mb-2' : '',
          position === 'bottom' ? 'top-full left-1/2 -translate-x-1/2 mt-2' : '',
          position === 'left' ? 'right-full top-1/2 -translate-y-1/2 mr-2' : '',
          position === 'right' ? 'left-full top-1/2 -translate-y-1/2 ml-2' : '',
        ]"
      >
        <div class="tooltip-arrow" :class="[
          position === 'top' ? 'top-full left-1/2 -translate-x-1/2 border-t-gray-800' : '',
          position === 'bottom' ? 'bottom-full left-1/2 -translate-x-1/2 border-b-gray-800' : '',
          position === 'left' ? 'left-full top-1/2 -translate-y-1/2 border-l-gray-800' : '',
          position === 'right' ? 'right-full top-1/2 -translate-y-1/2 border-r-gray-800' : '',
        ]"></div>
        <p class="tooltip-text">{{ text }}</p>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  text: {
    type: String,
    required: true
  },
  position: {
    type: String,
    default: 'top',
    validator: (value) => ['top', 'bottom', 'left', 'right'].includes(value)
  }
})

const showTooltip = ref(false)
</script>

<style scoped>
.tooltip-wrapper {
  display: inline-flex;
  align-items: center;
}

.tooltip-trigger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: none;
  cursor: help;
  padding: 0;
  margin-left: 4px;
  outline: none;
}

.tooltip-content {
  position: absolute;
  z-index: 50;
  min-width: 200px;
  max-width: 300px;
  pointer-events: none;
}

.tooltip-arrow {
  position: absolute;
  width: 0;
  height: 0;
  border: 6px solid transparent;
}

.tooltip-text {
  background-color: #1f2937;
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
  line-height: 1.5;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.tooltip-enter-active,
.tooltip-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.tooltip-enter-from,
.tooltip-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.tooltip-enter-to,
.tooltip-leave-from {
  opacity: 1;
  transform: translateY(0);
}
</style>


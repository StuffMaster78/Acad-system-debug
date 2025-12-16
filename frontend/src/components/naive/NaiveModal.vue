<template>
  <NModal
    :show="localVisible"
    :preset="preset"
    :title="title"
    :show-icon="!!icon"
    :mask-closable="closeOnBackdrop"
    :close-on-esc="true"
    :auto-focus="autoFocus"
    :transform-origin="transformOrigin"
    :style="modalStyle"
    :class="modalClass"
    @update:show="handleUpdateShow"
  >
    <template v-if="icon" #header>
      <div class="flex items-center gap-2">
        <span class="text-2xl">{{ icon }}</span>
        <span>{{ title }}</span>
      </div>
    </template>

    <template v-if="subtitle" #header-extra>
      <p class="text-sm text-gray-500 dark:text-gray-400">{{ subtitle }}</p>
    </template>

    <div :class="bodyClass">
      <slot></slot>
    </div>

    <template v-if="$slots.footer" #footer>
      <div class="flex flex-col sm:flex-row-reverse gap-2 sm:gap-3">
        <slot name="footer"></slot>
      </div>
    </template>
  </NModal>
</template>

<script setup>
import { computed, watch } from 'vue'
import { NModal } from 'naive-ui'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  show: {
    type: Boolean,
    default: false,
  },
  title: {
    type: String,
    default: '',
  },
  subtitle: {
    type: String,
    default: '',
  },
  icon: {
    type: String,
    default: '',
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg', 'xl', '2xl', 'full'].includes(value),
  },
  closeOnBackdrop: {
    type: Boolean,
    default: true,
  },
  autoFocus: {
    type: Boolean,
    default: true,
  },
  scrollable: {
    type: Boolean,
    default: true,
  },
  bodyClass: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:visible', 'update:show', 'close'])

// Support both v-model:visible and :show prop
const localVisible = computed({
  get: () => props.visible || props.show,
  set: (value) => {
    emit('update:visible', value)
    emit('update:show', value)
    if (!value) {
      emit('close')
    }
  },
})

// Map size to Naive UI preset
const preset = computed(() => {
  if (props.size === 'full') return 'card'
  return 'card'
})

// Map size to modal width
const modalStyle = computed(() => {
  const sizeMap = {
    sm: 'width: 400px',
    md: 'width: 500px',
    lg: 'width: 600px',
    xl: 'width: 800px',
    '2xl': 'width: 1000px',
    full: 'width: 95vw; max-width: 1200px',
  }
  return sizeMap[props.size] || sizeMap.md
})

const modalClass = computed(() => {
  return props.scrollable ? 'max-h-[90vh] overflow-hidden' : ''
})

const transformOrigin = 'center'

const handleUpdateShow = (value) => {
  localVisible.value = value
}
</script>


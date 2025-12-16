<template>
  <NButton
    :type="type"
    :size="size"
    :disabled="disabled"
    :loading="loading"
    :secondary="secondary"
    :tertiary="tertiary"
    :dashed="dashed"
    :round="round"
    :circle="circle"
    :block="block"
    :strong="strong"
    :color="color"
    :class="buttonClass"
    @click="handleClick"
  >
    <template v-if="$slots.icon" #icon>
      <slot name="icon" />
    </template>
    <slot />
  </NButton>
</template>

<script setup>
import { computed } from 'vue'
import { NButton } from 'naive-ui'

const props = defineProps({
  type: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'primary', 'success', 'warning', 'error', 'info', 'tertiary'].includes(value),
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['tiny', 'small', 'medium', 'large'].includes(value),
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  secondary: {
    type: Boolean,
    default: false,
  },
  tertiary: {
    type: Boolean,
    default: false,
  },
  dashed: {
    type: Boolean,
    default: false,
  },
  round: {
    type: Boolean,
    default: false,
  },
  circle: {
    type: Boolean,
    default: false,
  },
  block: {
    type: Boolean,
    default: false,
  },
  strong: {
    type: Boolean,
    default: false,
  },
  color: {
    type: String,
    default: undefined,
  },
  class: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['click'])

const buttonClass = computed(() => {
  return props.class
})

const handleClick = (e) => {
  emit('click', e)
}
</script>


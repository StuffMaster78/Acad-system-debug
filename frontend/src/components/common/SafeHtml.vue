<template>
  <div 
    v-if="content" 
    :class="containerClass"
    v-html="sanitizedContent"
  ></div>
  <div v-else :class="containerClass">
    <slot></slot>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { sanitizeHtml } from '@/utils/htmlUtils'

const props = defineProps({
  content: {
    type: String,
    default: ''
  },
  containerClass: {
    type: String,
    default: ''
  }
})

const sanitizedContent = computed(() => {
  if (!props.content) return ''
  return sanitizeHtml(props.content)
})
</script>


<template>
  <div 
    :class="containerClass"
    v-html="sanitizedHtml"
  ></div>
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
    default: 'prose prose-sm max-w-none'
  }
})

const sanitizedHtml = computed(() => {
  if (!props.content) return ''
  return sanitizeHtml(props.content)
})
</script>

<style scoped>
/* Prose styles for rich text content */
:deep(.prose) {
  color: #374151;
}

:deep(.prose p) {
  margin-top: 1em;
  margin-bottom: 1em;
}

:deep(.prose img) {
  max-width: 100%;
  height: auto;
  border-radius: 0.5rem;
  margin: 1em 0;
}

:deep(.prose ul),
:deep(.prose ol) {
  margin: 1em 0;
  padding-left: 2em;
}

:deep(.prose li) {
  margin: 0.5em 0;
}

:deep(.prose strong),
:deep(.prose b) {
  font-weight: 600;
}

:deep(.prose em),
:deep(.prose i) {
  font-style: italic;
}

:deep(.prose a) {
  color: #3b82f6;
  text-decoration: underline;
}

:deep(.prose a:hover) {
  color: #2563eb;
}

:deep(.prose blockquote) {
  border-left: 4px solid #e5e7eb;
  padding-left: 1em;
  margin: 1em 0;
  font-style: italic;
  color: #6b7280;
}

:deep(.prose code) {
  background-color: #f3f4f6;
  padding: 0.125em 0.25em;
  border-radius: 0.25rem;
  font-size: 0.875em;
}

:deep(.prose pre) {
  background-color: #1f2937;
  color: #f9fafb;
  padding: 1em;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin: 1em 0;
}

:deep(.prose pre code) {
  background-color: transparent;
  padding: 0;
  color: inherit;
}

:deep(.prose h1),
:deep(.prose h2),
:deep(.prose h3),
:deep(.prose h4),
:deep(.prose h5),
:deep(.prose h6) {
  font-weight: 600;
  margin-top: 1.5em;
  margin-bottom: 0.5em;
  line-height: 1.25;
}

:deep(.prose h1) {
  font-size: 2em;
}

:deep(.prose h2) {
  font-size: 1.5em;
}

:deep(.prose h3) {
  font-size: 1.25em;
}
</style>


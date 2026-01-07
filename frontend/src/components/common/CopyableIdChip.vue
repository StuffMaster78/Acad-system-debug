<template>
  <button
    v-if="value"
    type="button"
    :disabled="!canCopy"
    @click.stop="handleCopy"
    class="inline-flex items-center gap-1.5 rounded-full border border-gray-200 bg-gray-50 px-2.5 py-0.5 text-[11px] font-mono text-gray-700 hover:bg-gray-100 hover:border-gray-300 disabled:opacity-70 disabled:cursor-default"
    :title="canCopy ? 'Click to copy' : ''"
  >
    <span>{{ label }}: {{ value }}</span>
    <component
      :is="copied ? CheckIcon : ClipboardDocumentIcon"
      class="h-3.5 w-3.5 text-gray-400"
    />
  </button>
  <span v-else class="inline-flex items-center text-[11px] text-gray-400">
    {{ label }}: N/A
  </span>
</template>

<script setup>
import { ref } from 'vue'
import { ClipboardDocumentIcon, CheckIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  label: {
    type: String,
    default: 'ID',
  },
  value: {
    type: [String, Number],
    default: null,
  },
  canCopy: {
    type: Boolean,
    default: true,
  },
})

const copied = ref(false)

const handleCopy = async () => {
  if (!props.canCopy || !props.value) return

  try {
    await navigator.clipboard.writeText(String(props.value))
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 1500)
  } catch (error) {
    if (import.meta.env.DEV) {
      console.error('Failed to copy to clipboard:', error)
    }
  }
}
</script>



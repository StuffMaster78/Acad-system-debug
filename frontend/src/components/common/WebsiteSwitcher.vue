<template>
  <div class="relative">
    <label v-if="showLabel" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
      {{ label }}
    </label>
    <select
      :value="modelValue"
      @change="handleChange"
      :disabled="disabled || !canSelectWebsite || websites.length === 0"
      class="w-full px-4 py-2.5 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-100 dark:disabled:bg-gray-900 disabled:cursor-not-allowed transition-colors duration-200"
    >
      <option v-if="showAllOption" value="">
        {{ allOptionLabel }}
      </option>
      <option
        v-for="website in websites"
        :key="website.id"
        :value="website.id"
      >
        {{ website.name }} ({{ formatDomain(website.domain) }})
      </option>
    </select>
    <p v-if="!canSelectWebsite && websites.length > 0" class="mt-1 text-xs text-gray-500 dark:text-gray-400">
      You can only manage content for your assigned website
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: [Number, String, null],
    default: null
  },
  websites: {
    type: Array,
    default: () => []
  },
  canSelectWebsite: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  showLabel: {
    type: Boolean,
    default: true
  },
  label: {
    type: String,
    default: 'Select Website'
  },
  showAllOption: {
    type: Boolean,
    default: false
  },
  allOptionLabel: {
    type: String,
    default: 'All Websites'
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const handleChange = (event) => {
  const value = event.target.value === '' ? null : parseInt(event.target.value)
  emit('update:modelValue', value)
  emit('change', value)
}

const formatDomain = (domain) => {
  if (!domain) return ''
  try {
    const url = new URL(domain)
    return url.hostname.replace('www.', '')
  } catch {
    return domain.replace(/^https?:\/\//, '').replace('www.', '')
  }
}
</script>


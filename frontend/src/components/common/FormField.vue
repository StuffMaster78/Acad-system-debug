<template>
  <div class="form-field-aligned" :class="containerClass">
    <label 
      v-if="label" 
      :for="fieldId"
      :class="labelClass"
    >
      {{ label }}
      <span v-if="required" class="text-red-600">*</span>
    </label>
    <div class="relative">
      <slot :id="fieldId" :name="name" :hasError="hasError" />
      <div v-if="hasError && errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
      <div v-if="hint && !hasError" class="hint-text">
        {{ hint }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: {
    type: String,
    default: null
  },
  name: {
    type: String,
    required: true
  },
  error: {
    type: [String, Array],
    default: null
  },
  hint: {
    type: String,
    default: null
  },
  required: {
    type: Boolean,
    default: false
  },
  containerClass: {
    type: String,
    default: ''
  },
  labelClass: {
    type: String,
    default: ''
  }
})

const fieldId = computed(() => `field-${props.name}`)
const hasError = computed(() => !!props.error)
const errorMessage = computed(() => {
  if (!props.error) return null
  if (typeof props.error === 'string') return props.error
  if (Array.isArray(props.error)) return props.error.join(', ')
  return 'Invalid input'
})
</script>


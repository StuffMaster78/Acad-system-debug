<template>
  <div :class="wrapperClass">
    <label v-if="label" :class="labelClass">
      {{ label }}
      <span v-if="required" class="text-red-500 ml-1">*</span>
    </label>
    <NInput
      v-model:value="localValue"
      :type="type"
      :placeholder="placeholder"
      :disabled="disabled"
      :readonly="readonly"
      :clearable="clearable"
      :show-password-on="showPasswordOn"
      :size="size"
      :round="round"
      :autofocus="autofocus"
      :maxlength="maxlength"
      :show-count="showCount"
      :status="status"
      :class="inputClass"
      @update:value="handleUpdate"
      @focus="handleFocus"
      @blur="handleBlur"
      @keydown="handleKeydown"
      @enter="handleEnter"
    />
    <div v-if="error" class="mt-1 text-sm text-red-600 dark:text-red-400">
      {{ error }}
    </div>
    <div v-if="helpText && !error" class="mt-1 text-sm text-gray-500 dark:text-gray-400">
      {{ helpText }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { NInput } from 'naive-ui'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: '',
  },
  label: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: '',
  },
  type: {
    type: String,
    default: 'text',
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  readonly: {
    type: Boolean,
    default: false,
  },
  clearable: {
    type: Boolean,
    default: false,
  },
  showPasswordOn: {
    type: String,
    default: 'click',
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value),
  },
  round: {
    type: Boolean,
    default: false,
  },
  autofocus: {
    type: Boolean,
    default: false,
  },
  maxlength: {
    type: Number,
    default: undefined,
  },
  showCount: {
    type: Boolean,
    default: false,
  },
  required: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: '',
  },
  helpText: {
    type: String,
    default: '',
  },
  status: {
    type: String,
    default: undefined,
    validator: (value) => !value || ['success', 'warning', 'error'].includes(value),
  },
  wrapperClass: {
    type: String,
    default: '',
  },
  labelClass: {
    type: String,
    default: 'block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2',
  },
  inputClass: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['update:modelValue', 'focus', 'blur', 'keydown', 'enter'])

const localValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const handleUpdate = (value) => {
  emit('update:modelValue', value)
}

const handleFocus = (e) => {
  emit('focus', e)
}

const handleBlur = (e) => {
  emit('blur', e)
}

const handleKeydown = (e) => {
  emit('keydown', e)
}

const handleEnter = () => {
  emit('enter')
}
</script>


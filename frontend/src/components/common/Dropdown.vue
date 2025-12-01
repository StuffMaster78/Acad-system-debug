<template>
  <div class="relative">
    <label
      v-if="label"
      :for="inputId"
      class="block text-sm font-medium text-gray-700 mb-2"
    >
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>

    <div class="relative">
      <select
        :id="inputId"
        :value="modelValue"
        @change="handleChange"
        :disabled="loading || disabled"
        :required="required"
        :class="[
          'w-full appearance-none bg-white border rounded-lg px-4 py-3 pr-10',
          'focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
          'disabled:bg-gray-100 disabled:cursor-not-allowed',
          'transition-colors duration-200',
          error ? 'border-red-300 focus:ring-red-500 focus:border-red-500' : 'border-gray-300',
          inputClass
        ]"
      >
        <option v-if="placeholder" value="" disabled>
          {{ placeholder }}
        </option>
        <option
          v-for="option in options"
          :key="getOptionValue(option)"
          :value="getOptionValue(option)"
        >
          {{ getOptionLabel(option) }}
        </option>
      </select>

      <!-- Dropdown Arrow -->
      <div
        :class="[
          'absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none',
          loading ? 'opacity-50' : ''
        ]"
      >
        <svg
          v-if="loading"
          class="animate-spin h-5 w-5 text-gray-400"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            class="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            stroke-width="4"
          ></circle>
          <path
            class="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          ></path>
        </svg>
        <svg
          v-else
          class="h-5 w-5 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </div>
    </div>

    <!-- Error Message -->
    <p v-if="error" class="mt-1 text-sm text-red-600">{{ error }}</p>

    <!-- Help Text -->
    <p v-if="helpText && !error" class="mt-1 text-sm text-gray-500">{{ helpText }}</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import dropdownOptionsAPI from '@/api/dropdown-options'

const props = defineProps({
  modelValue: {
    type: [String, Number, null],
    default: null
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'Select an option...'
  },
  required: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  helpText: {
    type: String,
    default: ''
  },
  inputClass: {
    type: String,
    default: ''
  },
  // Data source options
  source: {
    type: String,
    default: null, // 'api', 'static', or null for manual options
    validator: (value) => !value || ['api', 'static'].includes(value)
  },
  // API source configuration
  apiCategory: {
    type: String,
    default: null // e.g., 'paper_types', 'order_status', 'subjects'
  },
  apiParams: {
    type: Object,
    default: () => ({})
  },
  // Static options (if source is 'static' or manual)
  options: {
    type: Array,
    default: () => []
  },
  // Option value/label getters
  valueKey: {
    type: String,
    default: 'id' // or 'value' for enums
  },
  labelKey: {
    type: String,
    default: 'name' // or 'label' for enums
  },
  // Transform function for options
  transform: {
    type: Function,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'change', 'load'])

const loading = ref(false)
const loadedOptions = ref([])
const inputId = `dropdown-${Math.random().toString(36).substr(2, 9)}`

const fetchOptions = async () => {
  if (!props.source || props.source !== 'api' || !props.apiCategory) {
    return
  }

  loading.value = true
  try {
    const response = await dropdownOptionsAPI.getByCategory(props.apiCategory, props.apiParams)
    let options = response.data || []

    // Apply transform if provided
    if (props.transform && typeof props.transform === 'function') {
      options = options.map(props.transform)
    }

    loadedOptions.value = options
    emit('load', options)
  } catch (error) {
    console.error('Failed to load dropdown options:', error)
    loadedOptions.value = []
  } finally {
    loading.value = false
  }
}

const getOptions = () => {
  if (props.source === 'api') {
    return loadedOptions.value
  }
  return props.options || []
}

const options = computed(() => getOptions())

const getOptionValue = (option) => {
  if (typeof option === 'string' || typeof option === 'number') {
    return option
  }
  return option[props.valueKey] ?? option.value ?? option.id
}

const getOptionLabel = (option) => {
  if (typeof option === 'string') {
    return option
  }
  return option[props.labelKey] ?? option.label ?? option.name ?? String(option)
}

const handleChange = (event) => {
  const value = event.target.value
  emit('update:modelValue', value)
  emit('change', value)
}

// Watch for source changes
watch(() => [props.source, props.apiCategory], () => {
  if (props.source === 'api' && props.apiCategory) {
    fetchOptions()
  }
}, { immediate: true })

onMounted(() => {
  if (props.source === 'api' && props.apiCategory) {
    fetchOptions()
  }
})
</script>

<style scoped>
select {
  background-image: none; /* Remove default arrow */
}
</style>


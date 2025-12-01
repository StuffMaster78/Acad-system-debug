<template>
  <div class="database-select">
    <label
      v-if="label"
      :for="inputId"
      class="block text-sm font-medium text-gray-700 mb-2"
    >
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
      <span v-if="tooltip" class="ml-1 text-gray-400 cursor-help" :title="tooltip">ℹ️</span>
    </label>

    <div class="relative">
      <select
        :id="inputId"
        :value="modelValue"
        :disabled="loading || disabled"
        :required="required"
        :class="[
          'block w-full pl-3 pr-10 py-2 text-base border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 sm:text-sm transition-colors',
          error ? 'border-red-300 bg-red-50' : 'border-gray-300 bg-white',
          disabled || loading ? 'bg-gray-100 cursor-not-allowed opacity-60' : 'hover:border-gray-400',
          size === 'sm' ? 'py-1.5 text-sm' : size === 'lg' ? 'py-3 text-lg' : ''
        ]"
        @change="handleChange"
        @focus="$emit('focus', $event)"
        @blur="$emit('blur', $event)"
      >
        <option v-if="placeholder" value="" disabled>
          {{ loading ? 'Loading...' : placeholder }}
        </option>
        <option
          v-for="option in options"
          :key="getOptionValue(option)"
          :value="getOptionValue(option)"
        >
          {{ getOptionLabel(option) }}
        </option>
      </select>

      <!-- Loading Indicator -->
      <div
        v-if="loading"
        class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none"
      >
        <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
      </div>

      <!-- Dropdown Arrow -->
      <div
        v-else
        class="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none"
      >
        <svg
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

    <!-- Helper Text -->
    <p v-if="helperText && !error" class="mt-1 text-sm text-gray-500">{{ helperText }}</p>

    <!-- Empty State -->
    <div
      v-if="!loading && options.length === 0 && !error"
      class="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg"
    >
      <p class="text-sm text-yellow-800">
        {{ emptyMessage || 'No options available. Please contact an administrator to add options.' }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import orderConfigsAPI from '@/api/orderConfigs'
import usersAPI from '@/api/users'

const props = defineProps({
  modelValue: {
    type: [String, Number, null],
    default: null,
  },
  label: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: 'Select an option...',
  },
  required: {
    type: Boolean,
    default: false,
  },
  disabled: {
    type: Boolean,
    default: false,
  },
  error: {
    type: String,
    default: '',
  },
  helperText: {
    type: String,
    default: '',
  },
  tooltip: {
    type: String,
    default: '',
  },
  size: {
    type: String,
    default: 'md', // sm, md, lg
    validator: (value) => ['sm', 'md', 'lg'].includes(value),
  },
  // Data source configuration
  source: {
    type: String,
    required: true,
    validator: (value) => [
      'paper-types',
      'academic-levels',
      'formatting-styles',
      'subjects',
      'types-of-work',
      'english-types',
      'clients',
      'writers',
      'editors',
      'support',
      'admins',
      'custom',
    ].includes(value),
  },
  // For custom source, provide options directly
  customOptions: {
    type: Array,
    default: () => [],
  },
  // API parameters
  apiParams: {
    type: Object,
    default: () => ({}),
  },
  // Option value/label keys for custom options
  valueKey: {
    type: String,
    default: 'id',
  },
  labelKey: {
    type: String,
    default: 'name',
  },
  // Filter function for options
  filterFn: {
    type: Function,
    default: null,
  },
  // Sort function for options
  sortFn: {
    type: Function,
    default: null,
  },
  emptyMessage: {
    type: String,
    default: '',
  },
  // Auto-load on mount
  autoLoad: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['update:modelValue', 'change', 'focus', 'blur', 'load'])

const loading = ref(false)
const options = ref([])
const errorMessage = ref('')

const inputId = computed(() => `select-${Math.random().toString(36).substr(2, 9)}`)

// Use the unified dropdown endpoint when available
const useUnifiedEndpoint = computed(() => {
  return ['paper-types', 'academic-levels', 'formatting-styles', 'subjects', 'types-of-work', 'english-types'].includes(props.source)
})

// Map source types to API methods
const sourceApiMap = {
  'paper-types': () => orderConfigsAPI.getPaperTypes(props.apiParams),
  'academic-levels': () => orderConfigsAPI.getAcademicLevels(props.apiParams),
  'formatting-styles': () => orderConfigsAPI.getFormattingStyles(props.apiParams),
  'subjects': () => orderConfigsAPI.getSubjects(props.apiParams),
  'types-of-work': () => orderConfigsAPI.getTypesOfWork(props.apiParams),
  'english-types': () => orderConfigsAPI.getEnglishTypes(props.apiParams),
  'clients': () => usersAPI.list({ role: 'client', ...props.apiParams }),
  'writers': () => usersAPI.list({ role: 'writer', ...props.apiParams }),
  'editors': () => usersAPI.list({ role: 'editor', ...props.apiParams }),
  'support': () => usersAPI.list({ role: 'support', ...props.apiParams }),
  'admins': () => usersAPI.list({ role: 'admin', ...props.apiParams }),
}

const loadOptions = async () => {
  if (props.source === 'custom') {
    options.value = props.customOptions || []
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    let data = []

    // Use unified endpoint for order configs if available
    if (useUnifiedEndpoint.value) {
      try {
        const response = await orderConfigsAPI.getDropdownOptions(props.apiParams)
        const sourceKeyMap = {
          'paper-types': 'paper_types',
          'academic-levels': 'academic_levels',
          'formatting-styles': 'formatting_styles',
          'subjects': 'subjects',
          'types-of-work': 'types_of_work',
          'english-types': 'english_types',
        }
        const key = sourceKeyMap[props.source]
        data = response.data?.[key] || []
      } catch (err) {
        // Fallback to individual endpoint
        const apiMethod = sourceApiMap[props.source]
        if (apiMethod) {
          const response = await apiMethod()
          data = response.data?.results || response.data || []
        }
      }
    } else {
      // Use individual API method
      const apiMethod = sourceApiMap[props.source]
      if (!apiMethod) {
        throw new Error(`Unknown source type: ${props.source}`)
      }
      const response = await apiMethod()
      data = response.data?.results || response.data || []
    }

    // Apply filter if provided
    if (props.filterFn && typeof props.filterFn === 'function') {
      data = data.filter(props.filterFn)
    }

    // Apply sort if provided
    if (props.sortFn && typeof props.sortFn === 'function') {
      data = data.sort(props.sortFn)
    } else {
      // Default sort by label
      data = data.sort((a, b) => {
        const aLabel = getOptionLabel(a)
        const bLabel = getOptionLabel(b)
        return aLabel.localeCompare(bLabel)
      })
    }

    options.value = data
    emit('load', data)
  } catch (err) {
    console.error(`Failed to load ${props.source}:`, err)
    errorMessage.value = err.response?.data?.detail || `Failed to load ${props.source}`
    options.value = []
  } finally {
    loading.value = false
  }
}

const getOptionValue = (option) => {
  if (typeof option === 'string' || typeof option === 'number') {
    return option
  }
  return option[props.valueKey] ?? option.id ?? option.value
}

const getOptionLabel = (option) => {
  if (typeof option === 'string') {
    return option
  }
  if (typeof option === 'number') {
    return option.toString()
  }
  
  // Try multiple common label keys
  return (
    option[props.labelKey] ??
    option.name ??
    option.label ??
    option.title ??
    option.username ??
    option.email ??
    option.text ??
    JSON.stringify(option)
  )
}

const handleChange = (event) => {
  const value = event.target.value
  emit('update:modelValue', value === '' ? null : value)
  emit('change', value === '' ? null : value)
}

// Watch for custom options changes
watch(() => props.customOptions, (newOptions) => {
  if (props.source === 'custom') {
    options.value = newOptions || []
  }
}, { deep: true, immediate: true })

// Watch for source changes
watch(() => props.source, () => {
  if (props.autoLoad) {
    loadOptions()
  }
})

onMounted(() => {
  if (props.autoLoad) {
    loadOptions()
  }
})

// Expose load method for manual refresh
defineExpose({
  load: loadOptions,
  refresh: loadOptions,
})
</script>

<style scoped>
.database-select select {
  appearance: none;
  background-image: none;
}

.database-select select::-ms-expand {
  display: none;
}
</style>


<template>
  <div class="bg-white p-4 rounded-lg shadow border border-gray-200">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <div v-for="filter in filters" :key="filter.key" :class="filter.fullWidth ? 'md:col-span-2 lg:col-span-4' : ''">
        <label class="block text-sm font-medium mb-1">{{ filter.label }}</label>
        <input
          v-if="filter.type === 'text' || filter.type === 'number'"
          :type="filter.type"
          v-model="localFilters[filter.key]"
          @input="handleInput(filter.key)"
          :placeholder="filter.placeholder"
          :min="filter.min"
          :step="filter.step"
          class="w-full border rounded px-3 py-2"
        />
        <select
          v-else-if="filter.type === 'select'"
          v-model="localFilters[filter.key]"
          @change="handleChange(filter.key)"
          class="w-full border rounded px-3 py-2"
        >
          <option v-for="option in filter.options" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </div>
      <div v-if="showReset" class="flex items-end">
        <button 
          @click="resetFilters"
          class="w-full px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors"
        >
          Reset
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  filters: {
    type: Array,
    required: true
  },
  modelValue: {
    type: Object,
    default: () => ({})
  },
  showReset: {
    type: Boolean,
    default: true
  },
  debounceMs: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

const localFilters = ref({ ...props.modelValue })

// Initialize local filters from props
watch(() => props.modelValue, (newVal) => {
  localFilters.value = { ...newVal }
}, { deep: true })

let debounceTimer = null

const handleInput = (key) => {
  if (props.debounceMs > 0) {
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
      emit('update:modelValue', { ...localFilters.value })
      emit('change', { ...localFilters.value })
    }, props.debounceMs)
  } else {
    emit('update:modelValue', { ...localFilters.value })
    emit('change', { ...localFilters.value })
  }
}

const handleChange = (key) => {
  emit('update:modelValue', { ...localFilters.value })
  emit('change', { ...localFilters.value })
}

const resetFilters = () => {
  const reset = {}
  props.filters.forEach(filter => {
    reset[filter.key] = filter.defaultValue || ''
  })
  localFilters.value = reset
  emit('update:modelValue', reset)
  emit('change', reset)
}
</script>


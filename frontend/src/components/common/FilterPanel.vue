<template>
  <div class="filter-panel">
    <div class="bg-white border border-gray-200 rounded-lg p-4">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-lg font-semibold text-gray-900">Filters</h3>
        <button
          v-if="hasActiveFilters"
          @click="clearFilters"
          class="text-sm text-primary-600 hover:text-primary-700"
        >
          Clear All
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <!-- Search -->
        <div v-if="showSearch">
          <label class="block text-sm font-medium text-gray-700 mb-1">Search</label>
          <input
            v-model="localFilters.search"
            type="text"
            placeholder="Search..."
            class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            @input="debouncedUpdate"
          />
        </div>

        <!-- Status Filter -->
        <div v-if="statusOptions && statusOptions.length > 0">
          <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
          <select
            v-model="localFilters.status"
            class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            @change="updateFilters"
          >
            <option value="">All Statuses</option>
            <option v-for="option in statusOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>

        <!-- Date Range -->
        <div v-if="showDateRange">
          <label class="block text-sm font-medium text-gray-700 mb-1">Date From</label>
          <input
            v-model="localFilters.date_from"
            type="date"
            class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            @change="updateFilters"
          />
        </div>

        <div v-if="showDateRange">
          <label class="block text-sm font-medium text-gray-700 mb-1">Date To</label>
          <input
            v-model="localFilters.date_to"
            type="date"
            class="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            @change="updateFilters"
          />
        </div>

        <!-- Custom Filters Slot -->
        <slot name="custom-filters" :filters="localFilters" :update="updateFilters"></slot>
      </div>

      <!-- Active Filters Display -->
      <div v-if="hasActiveFilters" class="mt-4 pt-4 border-t border-gray-200">
        <div class="flex flex-wrap gap-2">
          <span
            v-for="(value, key) in activeFilters"
            :key="key"
            class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
          >
            {{ getFilterLabel(key) }}: {{ getFilterValue(key, value) }}
            <button
              @click="removeFilter(key)"
              class="hover:text-primary-900"
            >
              ✕
            </button>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  filters: {
    type: Object,
    default: () => ({})
  },
  statusOptions: {
    type: Array,
    default: () => []
  },
  showSearch: {
    type: Boolean,
    default: true
  },
  showDateRange: {
    type: Boolean,
    default: false
  },
  filterLabels: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:filters', 'filter-change'])

const localFilters = ref({ ...props.filters })

// Watch for external filter changes
watch(() => props.filters, (newFilters) => {
  localFilters.value = { ...newFilters }
}, { deep: true })

const hasActiveFilters = computed(() => {
  return Object.keys(activeFilters.value).length > 0
})

const activeFilters = computed(() => {
  const active = {}
  Object.keys(localFilters.value).forEach(key => {
    const value = localFilters.value[key]
    if (value !== null && value !== undefined && value !== '' && value !== []) {
      active[key] = value
    }
  })
  return active
})

const getFilterLabel = (key) => {
  return props.filterLabels[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const getFilterValue = (key, value) => {
  if (Array.isArray(value)) {
    return value.join(', ')
  }
  if (key.includes('date')) {
    return new Date(value).toLocaleDateString()
  }
  return value
}

const updateFilters = () => {
  emit('update:filters', { ...localFilters.value })
  emit('filter-change', { ...localFilters.value })
}

const removeFilter = (key) => {
  localFilters.value[key] = null
  updateFilters()
}

const clearFilters = () => {
  Object.keys(localFilters.value).forEach(key => {
    localFilters.value[key] = null
  })
  updateFilters()
}

// Debounced search
let searchTimeout = null
const debouncedUpdate = () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    updateFilters()
  }, 500)
}
</script>

<style scoped>
.filter-panel {
  width: 100%;
}
</style>


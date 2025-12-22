<template>
  <div class="enhanced-data-table bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
    <!-- Header with Search and Actions -->
    <div v-if="searchable || $slots.headerActions" class="px-6 py-4 bg-gray-50 border-b border-gray-200">
      <div class="flex items-center justify-between gap-4">
        <!-- Search -->
        <div v-if="searchable" class="flex-1 max-w-md">
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              v-model="searchQuery"
              type="text"
              :placeholder="searchPlaceholder || 'Search...'"
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              @input="handleSearch"
            />
            <button
              v-if="searchQuery"
              @click="clearSearch"
              class="absolute inset-y-0 right-0 pr-3 flex items-center"
            >
              <svg class="h-5 w-5 text-gray-400 hover:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Header Actions Slot -->
        <div v-if="$slots.headerActions" class="flex items-center gap-2">
          <slot name="headerActions"></slot>
        </div>
      </div>

      <!-- Active Filters -->
      <div v-if="activeFilters.length > 0" class="mt-3 flex flex-wrap items-center gap-2">
        <span class="text-xs text-gray-500 font-medium">Active filters:</span>
        <span
          v-for="filter in activeFilters"
          :key="filter.key"
          class="inline-flex items-center gap-1 px-2 py-1 bg-primary-100 text-primary-800 rounded-full text-xs font-medium"
        >
          {{ filter.label }}: {{ filter.value }}
          <button
            @click="removeFilter(filter.key)"
            class="hover:text-primary-900"
          >
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </span>
        <button
          @click="clearAllFilters"
          class="text-xs text-primary-600 hover:text-primary-800 font-medium"
        >
          Clear all
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-16">
      <div class="text-center">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600 mx-auto mb-4"></div>
        <p class="text-sm text-gray-500">{{ loadingMessage || 'Loading data...' }}</p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading && filteredItems.length === 0" class="text-center py-16">
      <div class="text-6xl mb-4">{{ emptyIcon || '📋' }}</div>
      <p class="text-gray-600 text-lg font-medium">{{ emptyMessage || 'No data available' }}</p>
      <p v-if="emptyDescription" class="text-sm text-gray-400 mt-2 max-w-md mx-auto">{{ emptyDescription }}</p>
      <div v-if="searchQuery || activeFilters.length > 0" class="mt-4">
        <button
          @click="clearAllFilters"
          class="text-sm text-primary-600 hover:text-primary-800 font-medium"
        >
          Clear filters to see all results
        </button>
      </div>
    </div>

    <!-- Table -->
    <div v-else class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-linear-to-r from-gray-50 to-gray-100">
          <tr>
            <th
              v-for="(column, index) in columns"
              :key="index"
              :class="[
                'px-6 py-4 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider',
                column.align === 'right' ? 'text-right' : 'text-left',
                column.class || '',
                column.sortable && sortable ? 'cursor-pointer hover:bg-gray-200' : ''
              ]"
              @click="column.sortable && sortable ? handleSort(column.key) : null"
            >
              <div class="flex items-center gap-2">
                <span>{{ column.label }}</span>
                <button
                  v-if="column.sortable && sortable"
                  class="text-gray-400 hover:text-gray-600 transition-colors flex flex-col"
                >
                  <svg
                    :class="[
                      'w-3 h-3',
                      sortKey === column.key && sortDirection === 'asc' ? 'text-primary-600' : ''
                    ]"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 15l7-7 7 7" />
                  </svg>
                  <svg
                    :class="[
                      'w-3 h-3 -mt-1',
                      sortKey === column.key && sortDirection === 'desc' ? 'text-primary-600' : ''
                    ]"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </div>
            </th>
            <th v-if="hasRowActions" class="px-6 py-4 text-right text-xs font-semibold text-gray-700 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr
            v-for="(item, rowIndex) in paginatedItems"
            :key="getItemKey(item, rowIndex)"
            :class="[
              'transition-all duration-150',
              rowClass ? rowClass(item, rowIndex) : 'hover:bg-blue-50',
              striped && rowIndex % 2 === 1 ? 'bg-gray-50/50' : '',
              clickable ? 'cursor-pointer' : ''
            ]"
            @click="clickable && $emit('row-click', item, rowIndex)"
          >
            <td
              v-for="(column, colIndex) in columns"
              :key="colIndex"
              :class="[
                'px-6 py-4 text-sm',
                column.align === 'right' ? 'text-right' : 'text-left',
                column.cellClass || '',
                !column.nowrap ? 'whitespace-normal' : 'whitespace-nowrap'
              ]"
            >
              <slot
                :name="`cell-${column.key}`"
                :item="item"
                :value="getNestedValue(item, column.key)"
                :column="column"
                :rowIndex="rowIndex"
              >
                <component
                  v-if="column.component"
                  :is="column.component"
                  :item="item"
                  :value="getNestedValue(item, column.key)"
                />
                <span v-else class="text-gray-900">{{ formatValue(getNestedValue(item, column.key), column) }}</span>
              </slot>
            </td>
            <td v-if="hasRowActions" class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <slot name="row-actions" :item="item" :rowIndex="rowIndex">
                <div class="flex items-center justify-end gap-2">
                  <button
                    v-if="showViewAction"
                    @click.stop="$emit('view', item)"
                    class="text-primary-600 hover:text-primary-900"
                    title="View"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </button>
                  <button
                    v-if="showEditAction"
                    @click.stop="$emit('edit', item)"
                    class="text-blue-600 hover:text-blue-900"
                    title="Edit"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button
                    v-if="showDeleteAction"
                    @click.stop="$emit('delete', item)"
                    class="text-red-600 hover:text-red-900"
                    title="Delete"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Footer with Pagination and Info -->
    <div
      v-if="showPagination || showInfo"
      class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex flex-col sm:flex-row items-center justify-between gap-4"
    >
      <div v-if="showInfo" class="text-sm text-gray-700">
        Showing <span class="font-medium">{{ startIndex }}</span> to
        <span class="font-medium">{{ endIndex }}</span> of
        <span class="font-medium">{{ totalItems }}</span> results
        <span v-if="searchQuery || activeFilters.length > 0" class="text-gray-500">
          (filtered from {{ originalTotalItems }} total)
        </span>
      </div>

      <div v-if="showPagination && totalPages > 1" class="flex items-center gap-2">
        <button
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage === 1"
          :class="[
            'px-3 py-2 text-sm font-medium rounded-lg transition-colors',
            currentPage === 1
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          ]"
        >
          Previous
        </button>

        <div class="flex items-center gap-1">
          <button
            v-for="page in visiblePages"
            :key="page"
            @click="goToPage(page)"
            :class="[
              'px-3 py-2 text-sm font-medium rounded-lg transition-colors',
              page === currentPage
                ? 'bg-primary-600 text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            ]"
          >
            {{ page }}
          </button>
        </div>

        <button
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          :class="[
            'px-3 py-2 text-sm font-medium rounded-lg transition-colors',
            currentPage === totalPages
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          ]"
        >
          Next
        </button>

        <select
          v-if="pageSizeOptions.length > 0"
          v-model="localPageSize"
          @change="handlePageSizeChange"
          class="ml-4 px-3 py-2 text-sm border border-gray-300 rounded-lg bg-white focus:ring-1 focus:ring-primary-500 focus:border-primary-500"
        >
          <option v-for="size in pageSizeOptions" :key="size" :value="size">
            {{ size }} per page
          </option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  items: {
    type: Array,
    required: true,
    default: () => [],
  },
  columns: {
    type: Array,
    required: true,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  sortable: {
    type: Boolean,
    default: true,
  },
  searchable: {
    type: Boolean,
    default: true,
  },
  searchPlaceholder: {
    type: String,
    default: 'Search...',
  },
  searchFields: {
    type: Array,
    default: () => [],
  },
  striped: {
    type: Boolean,
    default: true,
  },
  clickable: {
    type: Boolean,
    default: false,
  },
  rowClass: {
    type: Function,
    default: null,
  },
  pagination: {
    type: Object,
    default: null,
  },
  pageSize: {
    type: Number,
    default: 10,
  },
  pageSizeOptions: {
    type: Array,
    default: () => [10, 25, 50, 100],
  },
  emptyMessage: {
    type: String,
    default: 'No data available',
  },
  emptyDescription: {
    type: String,
    default: '',
  },
  emptyIcon: {
    type: String,
    default: '📋',
  },
  loadingMessage: {
    type: String,
    default: 'Loading data...',
  },
  itemKey: {
    type: [String, Function],
    default: 'id',
  },
  filters: {
    type: Array,
    default: () => [],
  },
  showViewAction: {
    type: Boolean,
    default: false,
  },
  showEditAction: {
    type: Boolean,
    default: false,
  },
  showDeleteAction: {
    type: Boolean,
    default: false,
  },
  showPagination: {
    type: Boolean,
    default: true,
  },
  showInfo: {
    type: Boolean,
    default: true,
  },
})

const emit = defineEmits(['page-change', 'sort', 'search', 'filter', 'row-click', 'view', 'edit', 'delete'])

const searchQuery = ref('')
const sortKey = ref(null)
const sortDirection = ref('asc')
const currentPage = ref(1)
const localPageSize = ref(props.pageSize)
const activeFilters = ref([])

const originalTotalItems = computed(() => props.items.length)

// Filter items based on search
const filteredItems = computed(() => {
  let result = [...props.items]

  // Apply search
  if (searchQuery.value && props.searchFields.length > 0) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(item => {
      return props.searchFields.some(field => {
        const value = getNestedValue(item, field)
        return value && value.toString().toLowerCase().includes(query)
      })
    })
  }

  // Apply active filters
  if (activeFilters.value.length > 0) {
    activeFilters.value.forEach(filter => {
      result = result.filter(item => {
        const value = getNestedValue(item, filter.key)
        return filter.fn ? filter.fn(value, filter.value) : value === filter.value
      })
    })
  }

  // Apply sorting
  if (sortKey.value) {
    result.sort((a, b) => {
      const aVal = getNestedValue(a, sortKey.value)
      const bVal = getNestedValue(b, sortKey.value)
      const multiplier = sortDirection.value === 'asc' ? 1 : -1
      
      if (aVal === bVal) return 0
      if (aVal == null) return 1
      if (bVal == null) return -1
      
      return (aVal > bVal ? 1 : -1) * multiplier
    })
  }

  return result
})

// Paginate items
const totalPages = computed(() => Math.ceil(filteredItems.value.length / localPageSize.value))

const paginatedItems = computed(() => {
  const start = (currentPage.value - 1) * localPageSize.value
  const end = start + localPageSize.value
  return filteredItems.value.slice(start, end)
})

const totalItems = computed(() => filteredItems.value.length)
const startIndex = computed(() => (currentPage.value - 1) * localPageSize.value + 1)
const endIndex = computed(() => Math.min(currentPage.value * localPageSize.value, totalItems.value))

const visiblePages = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 3) {
      for (let i = 1; i <= 5; i++) pages.push(i)
      pages.push('...')
      pages.push(total)
    } else if (current >= total - 2) {
      pages.push(1)
      pages.push('...')
      for (let i = total - 4; i <= total; i++) pages.push(i)
    } else {
      pages.push(1)
      pages.push('...')
      for (let i = current - 1; i <= current + 1; i++) pages.push(i)
      pages.push('...')
      pages.push(total)
    }
  }
  
  return pages.filter(p => p !== '...' || pages.indexOf(p) !== pages.lastIndexOf(p))
})

const hasRowActions = computed(() => {
  return props.showViewAction || props.showEditAction || props.showDeleteAction
})

const getItemKey = (item, index) => {
  if (typeof props.itemKey === 'function') {
    return props.itemKey(item, index)
  }
  return item[props.itemKey] || index
}

const getNestedValue = (obj, path) => {
  if (!path) return ''
  return path.split('.').reduce((current, prop) => current?.[prop], obj) ?? ''
}

const formatValue = (value, column) => {
  if (value === null || value === undefined) return '—'
  if (column.format && typeof column.format === 'function') {
    return column.format(value)
  }
  return value
}

const handleSort = (key) => {
  if (sortKey.value === key) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDirection.value = 'asc'
  }
  emit('sort', { key: sortKey.value, direction: sortDirection.value })
}

const handleSearch = () => {
  currentPage.value = 1
  emit('search', searchQuery.value)
}

const clearSearch = () => {
  searchQuery.value = ''
  handleSearch()
}

const addFilter = (key, value, label, fn = null) => {
  const existing = activeFilters.value.findIndex(f => f.key === key)
  if (existing >= 0) {
    activeFilters.value[existing] = { key, value, label, fn }
  } else {
    activeFilters.value.push({ key, value, label, fn })
  }
  currentPage.value = 1
  emit('filter', activeFilters.value)
}

const removeFilter = (key) => {
  activeFilters.value = activeFilters.value.filter(f => f.key !== key)
  currentPage.value = 1
  emit('filter', activeFilters.value)
}

const clearAllFilters = () => {
  searchQuery.value = ''
  activeFilters.value = []
  currentPage.value = 1
  emit('search', '')
  emit('filter', [])
}

const goToPage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  emit('page-change', page)
}

const handlePageSizeChange = () => {
  currentPage.value = 1
  emit('page-size-change', localPageSize.value)
}

// Watch for external pagination changes
watch(() => props.pagination, (newPagination) => {
  if (newPagination && newPagination.current_page) {
    currentPage.value = newPagination.current_page
  }
}, { immediate: true })

// Watch for items changes to reset to page 1
watch(() => props.items, () => {
  if (currentPage.value > totalPages.value) {
    currentPage.value = 1
  }
})
</script>

<style scoped>
.enhanced-data-table {
  border-collapse: separate;
  border-spacing: 0;
}

thead th {
  position: sticky;
  top: 0;
  z-index: 10;
  background: linear-gradient(to right, #f9fafb, #f3f4f6);
}

tbody tr {
  transition: all 0.15s ease-in-out;
}

tbody tr:hover {
  background-color: #eff6ff;
}

tbody tr:active {
  background-color: #dbeafe;
}
</style>


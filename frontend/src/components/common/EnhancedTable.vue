<template>
  <div class="w-full">
    <!-- Table Container -->
    <div class="overflow-hidden rounded-2xl border border-gray-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm">
      <!-- Table Header (Optional title + actions) -->
      <div v-if="title || $slots.header" class="px-6 py-4 border-b border-gray-200 dark:border-slate-800">
        <div class="flex items-center justify-between">
          <div v-if="title" class="flex-1">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-slate-100">{{ title }}</h3>
            <p v-if="description" class="text-sm text-gray-500 dark:text-slate-400 mt-1">{{ description }}</p>
          </div>
          <div v-if="$slots.header">
            <slot name="header" />
          </div>
        </div>
      </div>

      <!-- Table Wrapper -->
      <div class="overflow-x-auto">
        <table class="w-full divide-y divide-gray-200 dark:divide-slate-800">
          <!-- Table Head -->
          <thead class="bg-gray-50 dark:bg-slate-900/50">
            <tr>
              <!-- Selection Checkbox Column -->
              <th v-if="selectable" class="w-12 px-6 py-3">
                <input
                  type="checkbox"
                  :checked="allSelected"
                  :indeterminate.prop="someSelected"
                  @change="toggleSelectAll"
                  class="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500 dark:border-slate-600 dark:bg-slate-800"
                />
              </th>

              <!-- Column Headers -->
              <th
                v-for="column in columns"
                :key="column.key"
                :class="[
                  'px-6 py-3 text-left text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wider',
                  column.sortable ? 'cursor-pointer select-none hover:text-gray-700 dark:hover:text-slate-300' : '',
                  column.align === 'center' ? 'text-center' : column.align === 'right' ? 'text-right' : 'text-left'
                ]"
                @click="column.sortable && handleSort(column.key)"
              >
                <div class="flex items-center gap-2" :class="column.align === 'center' ? 'justify-center' : column.align === 'right' ? 'justify-end' : ''">
                  <span>{{ column.label }}</span>
                  <span v-if="column.sortable" class="flex flex-col">
                    <svg class="w-3 h-3 transition-all" :class="sortKey === column.key && sortOrder === 'asc' ? 'text-primary-600' : 'text-gray-400'" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clip-rule="evenodd" />
                    </svg>
                    <svg class="w-3 h-3 -mt-1 transition-all" :class="sortKey === column.key && sortOrder === 'desc' ? 'text-primary-600' : 'text-gray-400'" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                  </span>
                </div>
              </th>

              <!-- Actions Column -->
              <th v-if="$slots.actions" class="px-6 py-3 text-right text-xs font-semibold text-gray-500 dark:text-slate-400 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>

          <!-- Table Body -->
          <tbody class="bg-white dark:bg-slate-900 divide-y divide-gray-200 dark:divide-slate-800">
            <!-- Loading State -->
            <tr v-if="loading">
              <td :colspan="totalColumns" class="px-6 py-12">
                <div class="flex flex-col items-center justify-center gap-3">
                  <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600"></div>
                  <p class="text-sm text-gray-500 dark:text-slate-400">{{ loadingText }}</p>
                </div>
              </td>
            </tr>

            <!-- Empty State -->
            <tr v-else-if="!data || data.length === 0">
              <td :colspan="totalColumns" class="px-6 py-12">
                <div class="flex flex-col items-center justify-center gap-3">
                  <div class="w-16 h-16 rounded-full bg-gray-100 dark:bg-slate-800 flex items-center justify-center">
                    <svg class="w-8 h-8 text-gray-400 dark:text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                    </svg>
                  </div>
                  <div class="text-center">
                    <p class="text-sm font-medium text-gray-900 dark:text-slate-100">{{ emptyText }}</p>
                    <p v-if="emptySubtext" class="text-xs text-gray-500 dark:text-slate-400 mt-1">{{ emptySubtext }}</p>
                  </div>
                </div>
              </td>
            </tr>

            <!-- Data Rows -->
            <tr
              v-else
              v-for="(row, index) in sortedData"
              :key="row.id || index"
              :class="[
                'transition-colors hover:bg-gray-50 dark:hover:bg-slate-800/50',
                striped && index % 2 === 1 ? 'bg-gray-50/50 dark:bg-slate-800/30' : '',
                row._highlighted ? 'bg-primary-50 dark:bg-primary-900/20' : '',
                clickableRows ? 'cursor-pointer' : ''
              ]"
              @click="handleRowClick(row)"
            >
              <!-- Selection Checkbox -->
              <td v-if="selectable" class="w-12 px-6 py-4">
                <input
                  type="checkbox"
                  :checked="selectedRows.includes(row)"
                  @click.stop
                  @change="toggleRowSelection(row)"
                  class="w-4 h-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500 dark:border-slate-600 dark:bg-slate-800"
                />
              </td>

              <!-- Data Cells -->
              <td
                v-for="column in columns"
                :key="column.key"
                :class="[
                  'px-6 py-4 whitespace-nowrap text-sm',
                  column.align === 'center' ? 'text-center' : column.align === 'right' ? 'text-right' : 'text-left',
                  column.truncate ? 'max-w-xs truncate' : '',
                  column.className || ''
                ]"
              >
                <!-- Custom Slot -->
                <slot v-if="$slots[`cell-${column.key}`]" :name="`cell-${column.key}`" :row="row" :value="getCellValue(row, column.key)" />
                
                <!-- Custom Formatter -->
                <template v-else-if="column.formatter">
                  {{ column.formatter(getCellValue(row, column.key), row) }}
                </template>

                <!-- Default Display -->
                <template v-else>
                  {{ getCellValue(row, column.key) }}
                </template>
              </td>

              <!-- Actions Column -->
              <td v-if="$slots.actions" class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <slot name="actions" :row="row" />
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Table Footer (Pagination) -->
      <div v-if="pagination" class="px-6 py-4 border-t border-gray-200 dark:border-slate-800 bg-gray-50 dark:bg-slate-900/50">
        <div class="flex items-center justify-between">
          <!-- Showing text -->
          <div class="text-sm text-gray-500 dark:text-slate-400">
            Showing <span class="font-medium">{{ startIndex + 1 }}</span> to <span class="font-medium">{{ endIndex }}</span> of <span class="font-medium">{{ totalItems }}</span> results
          </div>

          <!-- Pagination Controls -->
          <div class="flex items-center gap-2">
            <button
              @click="goToPage(currentPage - 1)"
              :disabled="currentPage === 1"
              class="px-3 py-2 text-sm font-medium rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 dark:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-800 disabled:hover:bg-transparent"
            >
              Previous
            </button>

            <div class="flex items-center gap-1">
              <button
                v-for="page in visiblePages"
                :key="page"
                @click="goToPage(page)"
                :class="[
                  'w-10 h-10 text-sm font-medium rounded-lg transition-all',
                  page === currentPage
                    ? 'bg-primary-600 text-white'
                    : 'text-gray-700 dark:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-800'
                ]"
              >
                {{ page }}
              </button>
            </div>

            <button
              @click="goToPage(currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="px-3 py-2 text-sm font-medium rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed text-gray-700 dark:text-slate-300 hover:bg-gray-100 dark:hover:bg-slate-800 disabled:hover:bg-transparent"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile Card View (Optional) -->
    <div v-if="mobileCards && isMobile" class="lg:hidden mt-4 space-y-4">
      <div
        v-for="(row, index) in sortedData"
        :key="row.id || index"
        class="bg-white dark:bg-slate-900 rounded-2xl border border-gray-200 dark:border-slate-800 p-4 shadow-sm hover:shadow-md transition-all"
      >
        <slot name="mobile-card" :row="row" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  // Data
  data: {
    type: Array,
    required: true
  },
  columns: {
    type: Array,
    required: true
    // Example: [{ key: 'name', label: 'Name', sortable: true, formatter: (val) => val }]
  },

  // Header
  title: {
    type: String,
    default: null
  },
  description: {
    type: String,
    default: null
  },

  // Sorting
  sortable: {
    type: Boolean,
    default: true
  },
  defaultSortKey: {
    type: String,
    default: null
  },
  defaultSortOrder: {
    type: String,
    default: 'asc',
    validator: (value) => ['asc', 'desc'].includes(value)
  },

  // Selection
  selectable: {
    type: Boolean,
    default: false
  },
  selectedRowsModel: {
    type: Array,
    default: () => []
  },

  // Styling
  striped: {
    type: Boolean,
    default: true
  },
  clickableRows: {
    type: Boolean,
    default: false
  },

  // States
  loading: {
    type: Boolean,
    default: false
  },
  loadingText: {
    type: String,
    default: 'Loading...'
  },
  emptyText: {
    type: String,
    default: 'No data found'
  },
  emptySubtext: {
    type: String,
    default: null
  },

  // Pagination
  pagination: {
    type: Boolean,
    default: false
  },
  perPage: {
    type: Number,
    default: 10
  },
  currentPageModel: {
    type: Number,
    default: 1
  },

  // Mobile
  mobileCards: {
    type: Boolean,
    default: false
  },
})

const emit = defineEmits(['row-click', 'sort-change', 'selection-change', 'page-change', 'update:selectedRowsModel', 'update:currentPageModel'])

// Sorting
const sortKey = ref(props.defaultSortKey)
const sortOrder = ref(props.defaultSortOrder)

// Selection
const selectedRows = ref([...props.selectedRowsModel])

// Pagination
const currentPage = ref(props.currentPageModel)

// Mobile detection
const isMobile = ref(window.innerWidth < 1024)

// Computed
const sortedData = computed(() => {
  if (!props.data) return []
  
  let data = [...props.data]
  
  // Apply sorting
  if (sortKey.value) {
    data.sort((a, b) => {
      const aVal = getCellValue(a, sortKey.value)
      const bVal = getCellValue(b, sortKey.value)
      
      if (aVal === bVal) return 0
      
      const comparison = aVal > bVal ? 1 : -1
      return sortOrder.value === 'asc' ? comparison : -comparison
    })
  }
  
  // Apply pagination
  if (props.pagination) {
    const start = (currentPage.value - 1) * props.perPage
    const end = start + props.perPage
    return data.slice(start, end)
  }
  
  return data
})

const totalColumns = computed(() => {
  let count = props.columns.length
  if (props.selectable) count++
  if (props.$slots && props.$slots.actions) count++
  return count
})

const allSelected = computed(() => {
  return selectedRows.value.length === props.data.length && props.data.length > 0
})

const someSelected = computed(() => {
  return selectedRows.value.length > 0 && selectedRows.value.length < props.data.length
})

const totalItems = computed(() => props.data?.length || 0)

const totalPages = computed(() => Math.ceil(totalItems.value / props.perPage))

const startIndex = computed(() => (currentPage.value - 1) * props.perPage)

const endIndex = computed(() => Math.min(startIndex.value + props.perPage, totalItems.value))

const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages.value, start + maxVisible - 1)
  
  if (end - start + 1 < maxVisible) {
    start = Math.max(1, end - maxVisible + 1)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// Methods
function getCellValue(row, key) {
  return key.split('.').reduce((obj, k) => obj?.[k], row)
}

function handleSort(key) {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
  
  emit('sort-change', { key: sortKey.value, order: sortOrder.value })
}

function toggleSelectAll() {
  if (allSelected.value) {
    selectedRows.value = []
  } else {
    selectedRows.value = [...props.data]
  }
  emit('update:selectedRowsModel', selectedRows.value)
  emit('selection-change', selectedRows.value)
}

function toggleRowSelection(row) {
  const index = selectedRows.value.indexOf(row)
  if (index > -1) {
    selectedRows.value.splice(index, 1)
  } else {
    selectedRows.value.push(row)
  }
  emit('update:selectedRowsModel', selectedRows.value)
  emit('selection-change', selectedRows.value)
}

function handleRowClick(row) {
  if (props.clickableRows) {
    emit('row-click', row)
  }
}

function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    emit('update:currentPageModel', page)
    emit('page-change', page)
  }
}

// Watch for external changes
watch(() => props.selectedRowsModel, (newVal) => {
  selectedRows.value = [...newVal]
})

watch(() => props.currentPageModel, (newVal) => {
  currentPage.value = newVal
})

// Mobile detection
window.addEventListener('resize', () => {
  isMobile.value = window.innerWidth < 1024
})
</script>

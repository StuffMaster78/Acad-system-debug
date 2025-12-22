<template>
  <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
    <!-- Loading State -->
    <div v-if="loading" class="flex items-center justify-center py-12">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!loading && items.length === 0" class="text-center py-12">
      <div class="text-4xl mb-4">{{ emptyIcon || '📋' }}</div>
      <p class="text-gray-600 text-lg">{{ emptyMessage || 'No data available' }}</p>
      <p v-if="emptyDescription" class="text-sm text-gray-400 mt-2">{{ emptyDescription }}</p>
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
                column.class || ''
              ]"
            >
              <div class="flex items-center gap-2">
                <span>{{ column.label }}</span>
                <button
                  v-if="column.sortable && sortable"
                  @click="handleSort(column.key)"
                  class="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"
                    />
                  </svg>
                </button>
              </div>
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr
            v-for="(item, rowIndex) in items"
            :key="getItemKey(item, rowIndex)"
            :class="[
              'transition-colors',
              rowClass ? rowClass(item, rowIndex) : 'hover:bg-gray-50',
              striped && rowIndex % 2 === 1 ? 'bg-gray-50/50' : ''
            ]"
          >
            <td
              v-for="(column, colIndex) in columns"
              :key="colIndex"
              :class="[
                'px-6 py-4 whitespace-nowrap text-sm',
                column.align === 'right' ? 'text-right' : 'text-left',
                column.cellClass || ''
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
                <span v-else>{{ formatValue(getNestedValue(item, column.key), column) }}</span>
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div
      v-if="pagination && pagination.total_pages > 1"
      class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex items-center justify-between"
    >
      <div class="text-sm text-gray-700">
        Showing {{ pagination.start_index || 1 }} to {{ pagination.end_index || items.length }} of
        {{ pagination.total_count || items.length }} results
      </div>
      <div class="flex items-center gap-2">
        <button 
          @click="$emit('page-change', pagination.current_page - 1)"
          :disabled="!pagination.has_previous"
          :class="[
            'px-3 py-2 text-sm font-medium rounded-lg transition-colors',
            pagination.has_previous
              ? 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
          ]"
        >
          Previous
        </button>
        <span class="px-3 py-2 text-sm text-gray-700">
          Page {{ pagination.current_page }} of {{ pagination.total_pages }}
        </span>
        <button 
          @click="$emit('page-change', pagination.current_page + 1)"
          :disabled="!pagination.has_next"
          :class="[
            'px-3 py-2 text-sm font-medium rounded-lg transition-colors',
            pagination.has_next
              ? 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
          ]"
        >
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

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
    default: false,
  },
  striped: {
    type: Boolean,
    default: true,
  },
  rowClass: {
    type: Function,
    default: null,
  },
  pagination: {
    type: Object,
    default: null,
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
  itemKey: {
    type: [String, Function],
    default: 'id',
  },
})

const emit = defineEmits(['page-change', 'sort'])

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
  emit('sort', key)
}
</script>

<style scoped>
/* Additional table styling */
table {
  border-collapse: separate;
  border-spacing: 0;
}

thead th {
  position: sticky;
  top: 0;
  z-index: 10;
}

tbody tr {
  transition: background-color 0.15s ease-in-out;
}

tbody tr:hover {
  background-color: #f9fafb;
}
</style>

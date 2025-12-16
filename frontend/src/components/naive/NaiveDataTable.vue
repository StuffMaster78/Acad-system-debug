<template>
  <NDataTable
    :columns="processedColumns"
    :data="items"
    :loading="loading"
    :pagination="paginationConfig"
    :bordered="bordered"
    :striped="striped"
    :single-line="singleLine"
    :single-column="singleColumn"
    :max-height="maxHeight"
    :scroll-x="scrollX"
    :row-class-name="rowClassName"
    :row-props="rowProps"
    :empty-description="emptyMessage"
    @update:sorter="handleSort"
    @update:page="handlePageChange"
    @update:page-size="handlePageSizeChange"
  >
    <!-- Custom cell slots -->
    <template v-for="(_, slot) in $slots" #[slot]="scope">
      <slot :name="slot" v-bind="scope" />
    </template>
  </NDataTable>
</template>

<script setup>
import { computed } from 'vue'
import { NDataTable } from 'naive-ui'

const props = defineProps({
  items: {
    type: Array,
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
  searchable: {
    type: Boolean,
    default: false,
  },
  sortable: {
    type: Boolean,
    default: true,
  },
  pagination: {
    type: [Boolean, Object],
    default: true,
  },
  pageSize: {
    type: Number,
    default: 10,
  },
  bordered: {
    type: Boolean,
    default: false,
  },
  striped: {
    type: Boolean,
    default: false,
  },
  singleLine: {
    type: Boolean,
    default: true,
  },
  singleColumn: {
    type: Boolean,
    default: false,
  },
  maxHeight: {
    type: [String, Number],
    default: undefined,
  },
  scrollX: {
    type: [String, Number],
    default: undefined,
  },
  emptyMessage: {
    type: String,
    default: 'No data available',
  },
  rowClassName: {
    type: [String, Function],
    default: undefined,
  },
  rowProps: {
    type: Function,
    default: undefined,
  },
})

const emit = defineEmits(['sort', 'page-change', 'page-size-change', 'row-click'])

// Process columns to match Naive UI format
const processedColumns = computed(() => {
  return props.columns.map((col) => {
    const naiveCol = {
      title: col.label || col.title,
      key: col.key,
      width: col.width,
      fixed: col.fixed,
      ellipsis: col.ellipsis !== false,
      align: col.align || 'left',
    }

    // Handle sorting
    if (props.sortable && col.sortable !== false) {
      naiveCol.sorter = col.sorter || true
    }

    // Handle render function
    if (col.render) {
      naiveCol.render = col.render
    }

    return naiveCol
  })
})

// Pagination configuration
const paginationConfig = computed(() => {
  if (props.pagination === false) return false

  if (typeof props.pagination === 'object') {
    return {
      pageSize: props.pageSize,
      ...props.pagination,
    }
  }

  return {
    pageSize: props.pageSize,
    showSizePicker: true,
    pageSizes: [10, 20, 50, 100],
    showQuickJumper: true,
  }
})

const handleSort = (sorter) => {
  emit('sort', sorter)
}

const handlePageChange = (page) => {
  emit('page-change', page)
}

const handlePageSizeChange = (pageSize) => {
  emit('page-size-change', pageSize)
}
</script>


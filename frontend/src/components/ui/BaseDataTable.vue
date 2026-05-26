<script setup lang="ts">
import { computed, ref } from "vue";
import { Search } from "@lucide/vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";

export interface DataTableColumn {
  key: string;
  label: string;
  align?: "left" | "right" | "center";
  sortable?: boolean;
}

const props = withDefaults(defineProps<{
  columns: DataTableColumn[];
  rows: Record<string, unknown>[];
  rowKey?: string;
  searchable?: boolean;
  loading?: boolean;
  emptyTitle?: string;
  emptyMessage?: string;
}>(), {
  rowKey: "id",
  searchable: true,
  loading: false,
  emptyTitle: "No records",
  emptyMessage: "Records will appear here when data is available.",
});

const query = ref("");
const sortKey = ref("");
const sortDirection = ref<"asc" | "desc">("asc");

const alignClasses = {
  left: "text-left",
  center: "text-center",
  right: "text-right",
};

const displayRows = computed(() => {
  const needle = query.value.trim().toLowerCase();
  const filtered = !needle
    ? props.rows
    : props.rows.filter((row) =>
      Object.values(row).some((value) =>
        String(value ?? "").toLowerCase().includes(needle),
      ),
    );

  if (!sortKey.value) return filtered;

  return [...filtered].sort((a, b) => {
    const left = String(a[sortKey.value] ?? "");
    const right = String(b[sortKey.value] ?? "");
    const result = left.localeCompare(right, undefined, { numeric: true });
    return sortDirection.value === "asc" ? result : -result;
  });
});

function rowIdentity(row: Record<string, unknown>, index: number) {
  return String(row[props.rowKey] ?? index);
}

function toggleSort(column: DataTableColumn) {
  if (!column.sortable) return;
  if (sortKey.value === column.key) {
    sortDirection.value = sortDirection.value === "asc" ? "desc" : "asc";
    return;
  }
  sortKey.value = column.key;
  sortDirection.value = "asc";
}
</script>

<template>
  <section class="rounded-md border border-slate-200 bg-white shadow-panel">
    <div
      v-if="searchable || $slots.toolbar"
      class="flex flex-col gap-3 border-b border-slate-200 px-4 py-4 sm:flex-row sm:items-center sm:justify-between"
    >
      <slot name="toolbar" />
      <label v-if="searchable" class="relative block min-w-64 sm:ml-auto">
        <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-graphite" />
        <input
          v-model="query"
          class="focus-ring h-10 w-full rounded-md border border-slate-200 bg-white pl-9 pr-3 text-sm"
          type="search"
          placeholder="Search table"
        >
      </label>
    </div>

    <div v-if="loading" class="p-6">
      <LoadingSpinner label="Loading records" />
    </div>

    <div v-else-if="displayRows.length" class="overflow-x-auto">
      <table class="min-w-full divide-y divide-slate-200 text-sm">
        <thead class="bg-slate-50 text-xs font-semibold uppercase text-graphite">
          <tr>
            <th
              v-for="column in columns"
              :key="column.key"
              class="px-4 py-3"
              :class="alignClasses[column.align ?? 'left']"
            >
              <button
                v-if="column.sortable"
                class="focus-ring inline-flex items-center gap-1 rounded text-xs font-semibold uppercase"
                type="button"
                @click="toggleSort(column)"
              >
                {{ column.label }}
                <span v-if="sortKey === column.key">{{ sortDirection === "asc" ? "↑" : "↓" }}</span>
              </button>
              <span v-else>{{ column.label }}</span>
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr
            v-for="(row, index) in displayRows"
            :key="rowIdentity(row, index)"
          >
            <td
              v-for="column in columns"
              :key="column.key"
              class="px-4 py-4"
              :class="alignClasses[column.align ?? 'left']"
            >
              <slot
                :name="`cell-${column.key}`"
                :row="row"
                :value="row[column.key]"
              >
                {{ row[column.key] }}
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="p-4">
      <EmptyState
        :icon="Search"
        :title="emptyTitle"
        :message="emptyMessage"
      />
    </div>
  </section>
</template>

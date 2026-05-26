<script setup lang="ts">
import { computed, onMounted } from "vue";
import {
  Activity,
  Download,
  Gauge,
  RefreshCw,
  Search,
  ShieldAlert,
  SlidersHorizontal,
} from "@lucide/vue";
import BaseDataTable, { type DataTableColumn } from "@/components/ui/BaseDataTable.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useAdminOpsStore } from "@/stores/adminOps";

const ops = useAdminOpsStore();

const metricToneClasses = {
  neutral: "border-slate-200 bg-white",
  good: "border-emerald-200 bg-emerald-50",
  warn: "border-amber-200 bg-amber-50",
  risk: "border-rose-200 bg-rose-50",
};

const performanceColumns: DataTableColumn[] = [
  { key: "endpoint", label: "Endpoint" },
  { key: "avg_response_time", label: "Avg ms", align: "right", sortable: true },
  { key: "avg_query_count", label: "Avg queries", align: "right", sortable: true },
  { key: "total_requests", label: "Requests", align: "right", sortable: true },
];

const compressionColumns: DataTableColumn[] = [
  { key: "endpoint", label: "Endpoint" },
  { key: "count", label: "Count", align: "right", sortable: true },
  { key: "total_saved", label: "Bytes saved", align: "right", sortable: true },
  { key: "compression_ratio", label: "Ratio", align: "right", sortable: true },
];

const performanceRows = computed(() => ops.endpointRows as Record<string, unknown>[]);
const compressionRows = computed(() => ops.compressionRows as Record<string, unknown>[]);

function resultRows(key: "orders" | "users" | "payments" | "messages") {
  const value = ops.searchResults[key];
  return Array.isArray(value) ? value.slice(0, 6) : [];
}

function signalText(value: unknown) {
  if (!value) return "No signals";
  if (Array.isArray(value)) return value.join(", ");
  return Object.entries(value as Record<string, unknown>)
    .map(([key, item]) => `${key}: ${String(item)}`)
    .join(", ");
}

function numberLabel(value: unknown) {
  return new Intl.NumberFormat(undefined, {
    maximumFractionDigits: 1,
  }).format(Number(value ?? 0));
}

function confidenceTone(value?: string) {
  if (value === "high") return "danger";
  if (value === "medium") return "warning";
  return "neutral";
}

onMounted(() => {
  ops.hydrate().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-8">
    <section class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase text-signal">Admin operations</p>
        <h1 class="mt-2 text-3xl font-semibold">Ops intelligence</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          Search across the platform, review duplicate-account risk, inspect rate-limit and performance hotspots, and generate exports.
        </p>
      </div>
      <button
        class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
        type="button"
        :disabled="ops.isLoading"
        @click="ops.hydrate"
      >
        <RefreshCw class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <p
      v-if="ops.error"
      class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {{ ops.error }} Preview mode will still show the workflow.
    </p>
    <p
      v-if="ops.notice"
      class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900"
    >
      {{ ops.notice }}
    </p>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div
        v-for="metric in ops.metrics"
        :key="metric.label"
        class="min-h-32 rounded-md border p-4 shadow-panel"
        :class="metricToneClasses[metric.tone]"
      >
        <p class="text-sm font-medium text-graphite">{{ metric.label }}</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ metric.value }}</p>
        <p class="mt-2 text-sm leading-5 text-graphite">{{ metric.detail }}</p>
      </div>
    </section>

    <section class="grid gap-6 xl:grid-cols-[minmax(0,1.25fr)_minmax(360px,0.85fr)]">
      <div class="space-y-6">
        <section class="rounded-md border border-slate-200 bg-white shadow-panel">
          <div class="border-b border-slate-200 px-4 py-4">
            <div class="flex items-center gap-2">
              <Search class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold">Unified search</h2>
            </div>
            <form class="mt-4 grid gap-3 lg:grid-cols-[1fr_280px_auto]" @submit.prevent="ops.runSearch">
              <input
                v-model="ops.searchQuery"
                class="focus-ring h-10 rounded-md border border-slate-200 px-3 text-sm"
                minlength="2"
                placeholder="Search users, orders, payments, messages"
                type="search"
              >
              <input
                v-model="ops.searchTypes"
                class="focus-ring h-10 rounded-md border border-slate-200 px-3 text-sm"
                type="text"
              >
              <button
                class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md bg-ink px-4 text-sm font-semibold text-white"
                type="submit"
                :disabled="ops.isSearching"
              >
                Search
              </button>
            </form>
          </div>

          <div class="grid gap-4 p-4 lg:grid-cols-2">
            <article
              v-for="kind in ['users', 'orders', 'payments', 'messages']"
              :key="kind"
              class="rounded-md border border-slate-200 p-4"
            >
              <div class="flex items-center justify-between">
                <h3 class="text-sm font-semibold capitalize text-ink">{{ kind }}</h3>
                <StatusPill :label="`${resultRows(kind as any).length}`" />
              </div>
              <div class="mt-3 space-y-2">
                <p v-if="!resultRows(kind as any).length" class="text-sm text-graphite">No matches.</p>
                <div
                  v-for="(item, index) in resultRows(kind as any)"
                  :key="index"
                  class="rounded-md bg-slate-50 p-3 text-sm"
                >
                  <p class="font-semibold text-ink">{{ item.title || item.full_name || item.username || item.email || item.id }}</p>
                  <p class="mt-1 text-xs text-graphite">
                    {{ item.email || item.status || item.snippet || item.amount || item.role || "Result" }}
                  </p>
                </div>
              </div>
            </article>
          </div>
        </section>

        <section class="rounded-md border border-slate-200 bg-white shadow-panel">
          <div class="flex min-h-16 items-center justify-between gap-3 border-b border-slate-200 px-4">
            <div class="flex items-center gap-2">
              <ShieldAlert class="h-5 w-5 text-signal" />
              <div>
                <h2 class="text-base font-semibold">Duplicate account detection</h2>
                <p class="text-sm text-graphite">Suspected matches grouped by detection signals.</p>
              </div>
            </div>
          </div>
          <div v-if="ops.isLoading" class="p-6">
            <LoadingSpinner label="Loading duplicates" />
          </div>
          <div v-else-if="ops.duplicates.length" class="divide-y divide-slate-100">
            <article
              v-for="group in ops.duplicates"
              :key="group.user_ids.join('-')"
              class="p-4"
            >
              <div class="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p class="font-semibold text-ink">Users {{ group.user_ids.join(", ") }}</p>
                  <p class="mt-1 text-sm text-graphite">{{ signalText(group.signals) }}</p>
                </div>
                <StatusPill :label="group.confidence" :tone="confidenceTone(group.confidence)" />
              </div>
              <div class="mt-3 grid gap-3 md:grid-cols-2">
                <div
                  v-for="user in group.users"
                  :key="user.id"
                  class="rounded-md border border-slate-200 p-3 text-sm"
                >
                  <p class="font-semibold text-ink">{{ user.username }}</p>
                  <p class="mt-1 text-xs text-graphite">{{ user.email }} · {{ user.role }}</p>
                  <p class="mt-1 text-xs text-graphite">{{ user.website?.name || "No website" }}</p>
                </div>
              </div>
            </article>
          </div>
          <div v-else class="p-4">
            <EmptyState
              :icon="ShieldAlert"
              title="No duplicate groups"
              message="Duplicate detection results will appear here."
            />
          </div>
        </section>
      </div>

      <aside class="space-y-6">
        <section class="rounded-md border border-slate-200 bg-white shadow-panel">
          <div class="border-b border-slate-200 px-4 py-4">
            <div class="flex items-center gap-2">
              <SlidersHorizontal class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold">Exports</h2>
            </div>
            <p class="mt-1 text-sm text-graphite">Download backend reports with role/date filters.</p>
          </div>
          <div class="space-y-3 p-4">
            <select
              v-model="ops.exportForm.kind"
              class="focus-ring h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
            >
              <option value="orders">Orders</option>
              <option value="payments">Payments</option>
              <option value="users">Users</option>
              <option value="financial-report">Financial report</option>
            </select>
            <select
              v-model="ops.exportForm.format"
              class="focus-ring h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
            >
              <option value="csv">CSV</option>
              <option value="xlsx">Excel</option>
            </select>
            <div class="grid gap-3 sm:grid-cols-2">
              <input v-model="ops.exportForm.date_from" class="focus-ring h-10 rounded-md border border-slate-200 px-3 text-sm" type="date">
              <input v-model="ops.exportForm.date_to" class="focus-ring h-10 rounded-md border border-slate-200 px-3 text-sm" type="date">
            </div>
            <div class="grid gap-3 sm:grid-cols-2">
              <input v-model="ops.exportForm.role" class="focus-ring h-10 rounded-md border border-slate-200 px-3 text-sm" placeholder="role">
              <input v-model="ops.exportForm.status" class="focus-ring h-10 rounded-md border border-slate-200 px-3 text-sm" placeholder="status">
            </div>
            <button
              class="focus-ring inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-ink px-3 text-sm font-semibold text-white"
              type="button"
              :disabled="ops.isMutating"
              @click="ops.downloadExport().catch(() => undefined)"
            >
              <Download class="h-4 w-4" />
              Download export
            </button>
          </div>
        </section>

        <section class="rounded-md border border-slate-200 bg-white shadow-panel">
          <div class="flex min-h-16 items-center justify-between gap-3 border-b border-slate-200 px-4">
            <div class="flex items-center gap-2">
              <Gauge class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold">Rate limits</h2>
            </div>
            <button
              class="focus-ring rounded-md border border-slate-200 px-3 py-2 text-xs font-semibold"
              type="button"
              :disabled="ops.isMutating"
              @click="ops.clearRateLimits().catch(() => undefined)"
            >
              Clear
            </button>
          </div>
          <div class="grid gap-4 p-4">
            <article class="rounded-md border border-slate-200 p-3">
              <p class="text-xs font-semibold uppercase text-graphite">Top endpoints</p>
              <p
                v-for="item in ops.topEndpoints"
                :key="item.endpoint"
                class="mt-2 flex justify-between gap-3 text-sm"
              >
                <span class="truncate text-graphite">{{ item.endpoint }}</span>
                <span class="font-semibold text-ink">{{ item.violations }}</span>
              </p>
            </article>
            <article class="rounded-md border border-slate-200 p-3">
              <p class="text-xs font-semibold uppercase text-graphite">Top users and IPs</p>
              <p
                v-for="item in ops.topUsers"
                :key="item.user_id"
                class="mt-2 flex justify-between gap-3 text-sm"
              >
                <span class="text-graphite">User {{ item.user_id }}</span>
                <span class="font-semibold text-ink">{{ item.violations }}</span>
              </p>
              <p
                v-for="item in ops.topIps"
                :key="item.ip"
                class="mt-2 flex justify-between gap-3 text-sm"
              >
                <span class="text-graphite">{{ item.ip }}</span>
                <span class="font-semibold text-ink">{{ item.violations }}</span>
              </p>
            </article>
          </div>
        </section>
      </aside>
    </section>

    <section class="grid gap-6 xl:grid-cols-2">
      <section>
        <div class="mb-3 flex items-center gap-2">
          <Activity class="h-5 w-5 text-signal" />
          <h2 class="text-base font-semibold">Performance hotspots</h2>
        </div>
        <BaseDataTable
          :columns="performanceColumns"
          :rows="performanceRows"
          empty-title="No performance metrics"
          empty-message="Performance middleware metrics will appear here."
        >
          <template #cell-avg_response_time="{ value }">{{ numberLabel(value) }}</template>
          <template #cell-avg_query_count="{ value }">{{ numberLabel(value) }}</template>
        </BaseDataTable>
      </section>
      <section>
        <div class="mb-3 flex items-center gap-2">
          <Download class="h-5 w-5 text-signal" />
          <h2 class="text-base font-semibold">Compression savings</h2>
        </div>
        <BaseDataTable
          :columns="compressionColumns"
          :rows="compressionRows"
          empty-title="No compression metrics"
          empty-message="Compression monitoring data will appear here."
        >
          <template #cell-total_saved="{ value }">{{ numberLabel(value) }}</template>
          <template #cell-compression_ratio="{ value }">{{ numberLabel(value) }}%</template>
        </BaseDataTable>
      </section>
    </section>
  </div>
</template>

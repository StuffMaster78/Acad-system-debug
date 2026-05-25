<script setup lang="ts">
import { onMounted } from "vue";
import {
  Archive,
  ClipboardList,
  Layers3,
  RefreshCw,
  Route,
  Search,
} from "@lucide/vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import {
  queueDefinitions,
  useOrderOpsStore,
} from "@/stores/orderOps";
import {
  useAdminWorkStore,
  workKindLabel,
  workTone,
} from "@/stores/adminWork";
import type { AdminWorkKind } from "@/types/adminWork";

const ops = useOrderOpsStore();
const work = useAdminWorkStore();

const toneClasses = {
  neutral: "border-slate-200 bg-white",
  good: "border-emerald-200 bg-emerald-50",
  warn: "border-amber-200 bg-amber-50",
  risk: "border-rose-200 bg-rose-50",
};

const workTabs: Array<{ key: AdminWorkKind | "all"; label: string }> = [
  { key: "all", label: "All work" },
  { key: "order", label: "Orders" },
  { key: "special_order", label: "Special" },
  { key: "class_order", label: "Classes" },
];

function formatDate(value: string | null) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatAmount(amount?: string, currency = "USD") {
  if (!amount) return "Not priced";
  const numeric = Number(amount);
  if (Number.isNaN(numeric)) return `${currency} ${amount}`;
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(numeric);
}

async function refreshAll() {
  await Promise.allSettled([
    work.refresh(),
    ops.refresh(),
  ]);
}

onMounted(() => {
  refreshAll().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-8">
    <section class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase text-signal">Admin</p>
        <h1 class="mt-2 text-3xl font-semibold">Work command center</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          A cross-site view of standard orders, special orders, class work,
          client context, writer assignments, payment state, and operational risk.
        </p>
      </div>
      <button
        class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
        type="button"
        @click="refreshAll"
      >
        <RefreshCw class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <p
      v-if="work.error || ops.error"
      class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {{ work.error || ops.error }} Preview mode will still show the layout.
    </p>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div
        v-for="metric in work.metrics"
        :key="metric.label"
        class="min-h-32 rounded-md border p-4 shadow-panel"
        :class="toneClasses[metric.tone]"
      >
        <p class="text-sm font-medium text-graphite">{{ metric.label }}</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ metric.value }}</p>
        <p class="mt-2 text-sm leading-5 text-graphite">{{ metric.detail }}</p>
      </div>
    </section>

    <section class="rounded-md border border-slate-200 bg-white shadow-panel">
      <div class="flex flex-col gap-4 border-b border-slate-200 px-4 py-4 xl:flex-row xl:items-center xl:justify-between">
        <div>
          <div class="flex items-center gap-2">
            <Layers3 class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold">All client-site work</h2>
          </div>
          <p class="mt-1 text-sm text-graphite">
            Normal orders, special orders, and class commitments with client and writer ownership.
          </p>
        </div>

        <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
          <div class="inline-flex rounded-md border border-slate-200 bg-slate-50 p-1">
            <button
              v-for="tab in workTabs"
              :key="tab.key"
              class="focus-ring min-h-9 rounded px-3 text-sm font-semibold"
              :class="work.activeKind === tab.key ? 'bg-white text-ink shadow-sm' : 'text-graphite'"
              type="button"
              @click="work.activeKind = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>
          <label class="relative block min-w-64">
            <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-graphite" />
            <input
              v-model="work.query"
              class="focus-ring h-10 w-full rounded-md border border-slate-200 bg-white pl-9 pr-3 text-sm"
              type="search"
              placeholder="Search site, client, writer, status"
            >
          </label>
        </div>
      </div>

      <div v-if="work.filteredItems.length" class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200 text-sm">
          <thead class="bg-slate-50 text-left text-xs font-semibold uppercase text-graphite">
            <tr>
              <th class="px-4 py-3">Work</th>
              <th class="px-4 py-3">Site / client</th>
              <th class="px-4 py-3">Assigned writer</th>
              <th class="px-4 py-3">Status</th>
              <th class="px-4 py-3">Deadline</th>
              <th class="px-4 py-3 text-right">Value</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="item in work.filteredItems" :key="`${item.kind}-${item.id}`">
              <td class="px-4 py-4">
                <div class="flex flex-wrap items-center gap-2">
                  <p class="font-semibold text-ink">{{ item.reference }}</p>
                  <StatusPill :label="workKindLabel(item.kind)" :tone="workTone(item)" />
                </div>
                <p class="mt-1 max-w-md font-medium text-ink">{{ item.title }}</p>
                <p v-if="item.subject" class="mt-1 text-xs text-graphite">
                  {{ item.subject }}
                </p>
              </td>
              <td class="px-4 py-4">
                <p class="font-medium text-ink">{{ item.website }}</p>
                <p class="mt-1 text-xs text-graphite">{{ item.client }}</p>
              </td>
              <td class="px-4 py-4 text-graphite">
                {{ item.assignedWriter }}
              </td>
              <td class="px-4 py-4">
                <StatusPill :label="item.status" :tone="workTone(item)" />
                <p v-if="item.paymentStatus" class="mt-2 text-xs text-graphite">
                  Payment: {{ item.paymentStatus }}
                </p>
              </td>
              <td class="px-4 py-4 text-graphite">
                {{ formatDate(item.deadline) }}
                <p v-if="item.notes" class="mt-1 max-w-xs text-xs leading-5 text-graphite">
                  {{ item.notes }}
                </p>
              </td>
              <td class="px-4 py-4 text-right font-semibold text-ink">
                {{ formatAmount(item.amount, item.currency) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-else class="p-4">
        <EmptyState
          :icon="ClipboardList"
          title="No work records found"
          message="Adjust the filter or refresh once the backend is connected."
        />
      </div>
    </section>

    <section class="space-y-4">
      <div>
        <h2 class="text-base font-semibold">Operations queues</h2>
        <p class="mt-1 text-sm text-graphite">
          Focused queues for staffing, deadlines, approvals, writer acknowledgement, and archive review.
        </p>
      </div>

      <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <button
          v-for="queue in queueDefinitions"
          :key="queue.key"
          class="focus-ring min-h-32 rounded-md border p-4 text-left shadow-panel"
          :class="[
            toneClasses[queue.tone],
            ops.activeQueue === queue.key ? 'ring-2 ring-signal ring-offset-2' : '',
          ]"
          type="button"
          @click="ops.fetchQueue(queue.key).catch(() => undefined)"
        >
          <p class="text-sm font-medium text-graphite">{{ queue.label }}</p>
          <p class="mt-3 text-3xl font-semibold text-ink">
            {{ ops.counts[queue.countKey] }}
          </p>
          <p class="mt-2 text-sm leading-5 text-graphite">
            {{ queue.description }}
          </p>
        </button>
      </div>

      <div class="rounded-md border border-slate-200 bg-white shadow-panel">
        <div class="flex min-h-16 items-center justify-between gap-3 border-b border-slate-200 px-4">
          <div>
            <h3 class="text-base font-semibold">{{ ops.activeDefinition.label }}</h3>
            <p class="text-sm text-graphite">{{ ops.activeDefinition.description }}</p>
          </div>
          <StatusPill :label="`${ops.rows.length} rows`" />
        </div>

        <div v-if="ops.rows.length" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50 text-left text-xs font-semibold uppercase text-graphite">
              <tr>
                <th class="px-4 py-3">Order</th>
                <th class="px-4 py-3">Status</th>
                <th class="px-4 py-3">Payment</th>
                <th class="px-4 py-3">Writer deadline</th>
                <th class="px-4 py-3">Client</th>
                <th class="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="order in ops.rows" :key="order.id">
                <td class="px-4 py-4">
                  <p class="font-semibold text-ink">#{{ order.id }} {{ order.topic }}</p>
                  <p class="mt-1 text-xs text-graphite">
                    Preferred writer: {{ order.preferred_writer_id || "None" }}
                  </p>
                </td>
                <td class="px-4 py-4">
                  <StatusPill :label="order.status" />
                </td>
                <td class="px-4 py-4 text-graphite">
                  {{ order.payment_status || "unknown" }}
                </td>
                <td class="px-4 py-4 text-graphite">
                  {{ formatDate(order.writer_deadline) }}
                </td>
                <td class="px-4 py-4 text-graphite">
                  {{ order.client_id || "External" }}
                </td>
                <td class="px-4 py-4">
                  <div class="flex justify-end gap-2">
                    <button
                      v-if="ops.activeQueue === 'pending_staffing'"
                      class="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200"
                      type="button"
                      title="Route to staffing"
                      @click="ops.routeToStaffing(order.id).catch(() => undefined)"
                    >
                      <Route class="h-4 w-4" />
                    </button>
                    <button
                      v-if="ops.activeQueue === 'eligible_for_archive'"
                      class="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200"
                      type="button"
                      title="Archive order"
                      @click="ops.archive(order.id).catch(() => undefined)"
                    >
                      <Archive class="h-4 w-4" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="p-4">
          <EmptyState
            :icon="ClipboardList"
            title="No queue rows loaded"
            message="Use refresh with a staff account connected to the backend, or switch queues to inspect the layout."
          />
        </div>
      </div>
    </section>
  </div>
</template>

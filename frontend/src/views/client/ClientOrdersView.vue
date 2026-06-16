<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { RouterLink } from "vue-router";
import {
  AlertCircle,
  CheckCircle2,
  ClipboardList,
  Clock3,
  Loader2,
  Plus,
  RefreshCw,
  Search,
  Zap,
} from "@lucide/vue";
import Pagination from "@/components/ui/Pagination.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useOrderStore } from "@/stores/orders";

const orders = useOrderStore();

type StatusTab = "all" | "active" | "pending" | "delivered" | "completed" | "cancelled";

const activeTab = ref<StatusTab>("all");
const searchQuery = ref("");

const tabDefs: Array<{ key: StatusTab; label: string; statuses?: string[] }> = [
  { key: "all", label: "All" },
  { key: "active", label: "Active", statuses: ["in_progress", "under_editing", "revision_requested"] },
  { key: "pending", label: "Pending", statuses: ["placed", "payment_pending", "assigned", "draft"] },
  { key: "delivered", label: "Delivered", statuses: ["awaiting_approval", "submitted"] },
  { key: "completed", label: "Completed", statuses: ["completed", "approved"] },
  { key: "cancelled", label: "Cancelled", statuses: ["cancelled", "archived"] },
];

const statusParam = computed(() => tabDefs.find((t) => t.key === activeTab.value)?.statuses?.join(","));

const filteredOrders = computed(() => {
  const q = searchQuery.value.trim().toLowerCase();
  if (!q) return orders.orders;
  return orders.orders.filter(
    (o) =>
      String(o.id).includes(q) ||
      (o.topic ?? "").toLowerCase().includes(q) ||
      (o.service_code ?? "").toLowerCase().includes(q),
  );
});

function statusTone(status: string): "success" | "warning" | "danger" | "neutral" {
  const s = status.toLowerCase();
  if (["completed", "approved"].includes(s)) return "success";
  if (["revision_requested", "awaiting_approval", "submitted"].includes(s)) return "warning";
  if (["cancelled", "archived"].includes(s)) return "danger";
  return "neutral";
}

function paymentTone(status?: string): "success" | "warning" | "danger" | "neutral" {
  if (!status) return "neutral";
  if (status === "paid") return "success";
  if (status === "pending") return "warning";
  if (status === "failed" || status === "refunded") return "danger";
  return "neutral";
}

function deadlineLabel(value?: string | null): string {
  if (!value) return "Not set";
  const h = (new Date(value).getTime() - Date.now()) / 3600000;
  if (h < 0) return `${Math.round(Math.abs(h))}h overdue`;
  if (h < 24) return `${Math.round(h)}h left`;
  const d = Math.round(h / 24);
  return `${d}d left`;
}

function deadlineTone(value?: string | null): "danger" | "warning" | "neutral" {
  if (!value) return "neutral";
  const h = (new Date(value).getTime() - Date.now()) / 3600000;
  if (h < 0) return "danger";
  if (h < 24) return "warning";
  return "neutral";
}

function money(amount?: string | number | null, currency = "USD"): string {
  if (amount === undefined || amount === null || amount === "") return `${currency} 0.00`;
  const n = Number(amount);
  if (Number.isNaN(n)) return `${currency} ${amount}`;
  return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(n);
}

// Stage track — 4 positions: placed → active → delivered → done
const STAGE_MAP: Record<string, number> = {
  placed: 0, payment_pending: 0, draft: 0,
  assigned: 1, in_progress: 1, under_editing: 1, revision_requested: 1,
  submitted: 2, awaiting_approval: 2,
  completed: 3, approved: 3,
};

function orderStage(status: string): number {
  return STAGE_MAP[status.toLowerCase()] ?? 0;
}

function accentBar(status: string): string {
  const s = status.toLowerCase();
  if (["in_progress", "under_editing", "assigned"].includes(s)) return "border-l-blue-500";
  if (["revision_requested", "awaiting_approval", "submitted"].includes(s)) return "border-l-amber-400";
  if (["completed", "approved"].includes(s)) return "border-l-emerald-500";
  if (["cancelled", "archived"].includes(s)) return "border-l-rose-400";
  return "border-l-slate-300";
}

async function switchTab(tab: StatusTab) {
  activeTab.value = tab;
  searchQuery.value = "";
  const statusDef = tabDefs.find((t) => t.key === tab);
  await orders.fetchOrders(1, statusDef?.statuses ? { status: statusDef.statuses.join(",") } : {});
}

function goToPage(page: number) {
  orders.fetchOrders(page, statusParam.value ? { status: statusParam.value } : {}).catch(() => undefined);
}

onMounted(() => {
  orders.fetchOrders(1).catch(() => undefined);
});
</script>

<template>
  <div class="space-y-5">

    <!-- Header -->
    <div class="flex items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-ink">My orders</h1>
        <p class="mt-1 text-sm text-graphite">Track active work, payments, delivery status, and revisions.</p>
      </div>
      <RouterLink
        class="focus-ring inline-flex h-9 items-center gap-2 rounded-lg bg-signal px-4 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-signal/90"
        to="/client/new-order"
      >
        <Plus class="h-4 w-4" /> New order
      </RouterLink>
    </div>

    <p v-if="orders.error" class="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
      {{ orders.error }}
    </p>

    <!-- Filter + search bar -->
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div class="inline-flex flex-wrap gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1">
        <button
          v-for="tab in tabDefs" :key="tab.key"
          class="focus-ring rounded-md px-3.5 py-1.5 text-xs font-semibold transition-all"
          :class="activeTab === tab.key ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
          type="button"
          @click="switchTab(tab.key)"
        >{{ tab.label }}</button>
      </div>
      <div class="flex items-center gap-2">
        <div class="relative">
          <Search class="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
          <input
            v-model="searchQuery"
            class="focus-ring h-9 w-52 rounded-lg border border-slate-200 bg-white pl-9 pr-3 text-sm placeholder:text-slate-400"
            type="search" placeholder="Search orders…"
          />
        </div>
        <button
          class="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-graphite hover:bg-slate-50 disabled:opacity-50"
          type="button" :disabled="orders.isLoading" title="Refresh"
          @click="orders.fetchOrders(orders.pagination.page, statusParam ? { status: statusParam } : {}).catch(() => undefined)"
        >
          <Loader2 v-if="orders.isLoading" class="h-4 w-4 animate-spin" />
          <RefreshCw v-else class="h-4 w-4" />
        </button>
      </div>
    </div>

    <!-- Order cards -->
    <div class="space-y-2">

      <!-- Skeleton -->
      <template v-if="orders.isLoading && !orders.orders.length">
        <div v-for="n in 4" :key="n" class="animate-pulse rounded-xl border border-slate-200 bg-white p-5">
          <div class="flex items-center justify-between gap-4">
            <div class="flex-1 space-y-2">
              <div class="h-4 w-3/5 rounded bg-slate-200" />
              <div class="h-3 w-2/5 rounded bg-slate-100" />
            </div>
            <div class="flex gap-2">
              <div class="h-5 w-20 rounded-full bg-slate-100" />
              <div class="h-5 w-14 rounded-full bg-slate-100" />
            </div>
          </div>
        </div>
      </template>

      <!-- Empty -->
      <div v-else-if="!filteredOrders.length" class="rounded-xl border border-slate-200 bg-white px-6 py-16 text-center">
        <ClipboardList class="mx-auto h-10 w-10 text-slate-200" />
        <p class="mt-3 text-sm font-semibold text-ink">
          {{ searchQuery ? 'No matching orders' : activeTab === 'all' ? 'No orders yet' : `No ${activeTab} orders` }}
        </p>
        <p class="mt-1 text-xs text-graphite">
          {{ searchQuery ? 'Try a different search term.' : activeTab === 'all' ? 'Place your first order to get started.' : 'No orders in this status group.' }}
        </p>
        <RouterLink
          v-if="!searchQuery && activeTab === 'all'"
          class="focus-ring mt-5 inline-flex h-9 items-center gap-2 rounded-lg bg-signal px-4 text-sm font-semibold text-white shadow-sm hover:bg-signal/90"
          to="/client/new-order"
        >
          <Plus class="h-4 w-4" /> Place your first order
        </RouterLink>
      </div>

      <!-- Cards -->
      <RouterLink
        v-else
        v-for="order in filteredOrders"
        :key="order.id"
        :to="`/client/orders/${order.id}`"
        class="group flex items-center gap-0 rounded-xl border border-slate-200 bg-white overflow-hidden transition-all hover:border-slate-300 hover:shadow-sm"
      >
        <!-- Accent bar -->
        <div class="w-1 self-stretch shrink-0 rounded-l-xl" :class="accentBar(order.status)" />

        <!-- Main content -->
        <div class="flex flex-1 min-w-0 items-center gap-4 px-5 py-4">

          <!-- Topic + meta -->
          <div class="min-w-0 flex-1">
            <div class="flex flex-wrap items-center gap-2">
              <span class="text-xs font-semibold text-slate-400">#{{ order.id }}</span>
              <p class="truncate text-sm font-semibold text-ink group-hover:text-signal transition-colors">
                {{ order.topic || 'Untitled order' }}
              </p>
              <span
                v-if="order.is_urgent"
                class="inline-flex items-center gap-0.5 rounded-full bg-rose-100 px-1.5 py-0.5 text-xs font-bold text-rose-700"
              >
                <Zap class="h-2.5 w-2.5" /> Urgent
              </span>
            </div>
            <p class="mt-1 text-xs text-graphite">
              {{ order.service_code || 'Academic paper' }}
              <span v-if="order.number_of_pages"> · {{ order.number_of_pages }} pages</span>
            </p>

            <!-- Stage track -->
            <div class="mt-2.5 flex items-center gap-1">
              <template v-for="(stage, idx) in ['Placed', 'Active', 'Delivered', 'Done']" :key="stage">
                <div
                  class="flex items-center justify-center rounded-full transition-colors"
                  :class="[
                    orderStage(order.status) >= idx
                      ? orderStage(order.status) === idx ? 'h-2 w-2 bg-signal ring-2 ring-signal/20' : 'h-1.5 w-1.5 bg-signal/40'
                      : 'h-1.5 w-1.5 bg-slate-200',
                  ]"
                />
                <div v-if="idx < 3" class="h-px w-4 flex-shrink-0" :class="orderStage(order.status) > idx ? 'bg-signal/40' : 'bg-slate-200'" />
              </template>
              <span class="ml-2 text-xs text-graphite">{{ ['Placed', 'Active', 'Delivered', 'Done'][orderStage(order.status)] }}</span>
            </div>
          </div>

          <!-- Pills -->
          <div class="hidden shrink-0 flex-col items-end gap-1.5 sm:flex">
            <StatusPill :label="order.status" :tone="statusTone(order.status)" />
            <StatusPill
              :label="order.payment_status || 'pending'"
              :tone="paymentTone(order.payment_status)"
            />
          </div>

          <!-- Deadline + price -->
          <div class="shrink-0 text-right">
            <div class="flex items-center justify-end gap-1">
              <component
                :is="deadlineTone(order.client_deadline) === 'danger' ? AlertCircle : deadlineTone(order.client_deadline) === 'warning' ? Clock3 : CheckCircle2"
                class="h-3.5 w-3.5"
                :class="{
                  'text-rose-500': deadlineTone(order.client_deadline) === 'danger',
                  'text-amber-500': deadlineTone(order.client_deadline) === 'warning',
                  'text-slate-300': deadlineTone(order.client_deadline) === 'neutral',
                }"
              />
              <span
                class="text-sm font-bold tabular-nums"
                :class="{
                  'text-rose-600': deadlineTone(order.client_deadline) === 'danger',
                  'text-amber-600': deadlineTone(order.client_deadline) === 'warning',
                  'text-graphite': deadlineTone(order.client_deadline) === 'neutral',
                }"
              >{{ deadlineLabel(order.client_deadline) }}</span>
            </div>
            <p class="mt-1 text-base font-extrabold text-ink tabular-nums">
              {{ money(order.total_price, order.currency) }}
            </p>
          </div>
        </div>
      </RouterLink>
    </div>

    <Pagination
      v-if="!searchQuery && orders.pagination.count > orders.pagination.pageSize"
      :page="orders.pagination.page"
      :page-size="orders.pagination.pageSize"
      :count="orders.pagination.count"
      @update:page="goToPage"
    />

  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { RouterLink } from "vue-router";
import {
  ClipboardList,
  Clock3,
  ExternalLink,
  Loader2,
  Plus,
  RefreshCw,
  Search,
  Zap,
} from "@lucide/vue";
import EmptyState from "@/components/ui/EmptyState.vue";
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
    <!-- Page header -->
    <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-2xl font-bold text-ink">My orders</h1>
        <p class="mt-1 text-sm text-graphite">
          Track active work, payments, delivery status, and revisions.
        </p>
      </div>
      <RouterLink
        class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-lg bg-signal px-5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-signal/90"
        to="/client/new-order"
      >
        <Plus class="h-4 w-4" />
        New order
      </RouterLink>
    </div>

    <p
      v-if="orders.error"
      class="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800"
    >
      {{ orders.error }}
    </p>

    <!-- Filters row -->
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div class="inline-flex flex-wrap gap-1 rounded-xl border border-slate-200 bg-slate-50 p-1">
        <button
          v-for="tab in tabDefs"
          :key="tab.key"
          class="focus-ring rounded-lg px-3.5 py-1.5 text-xs font-semibold transition-all"
          :class="activeTab === tab.key
            ? 'bg-white text-ink shadow-sm ring-1 ring-slate-200/80'
            : 'text-graphite hover:text-ink'"
          type="button"
          @click="switchTab(tab.key)"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="flex items-center gap-2">
        <div class="relative">
          <Search class="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
          <input
            v-model="searchQuery"
            class="focus-ring h-9 w-52 rounded-lg border border-slate-200 bg-white pl-9 pr-3 text-sm placeholder:text-slate-400"
            type="search"
            placeholder="Search orders…"
          />
        </div>
        <button
          class="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-graphite transition-colors hover:bg-slate-50 disabled:opacity-50"
          type="button"
          :disabled="orders.isLoading"
          title="Refresh"
          @click="orders.fetchOrders(orders.pagination.page, statusParam ? { status: statusParam } : {}).catch(() => undefined)"
        >
          <Loader2 v-if="orders.isLoading" class="h-4 w-4 animate-spin" />
          <RefreshCw v-else class="h-4 w-4" />
        </button>
      </div>
    </div>

    <div class="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-panel">
      <div v-if="orders.isLoading && !orders.orders.length" class="divide-y divide-slate-100">
        <div
          v-for="n in 5"
          :key="n"
          class="animate-pulse px-5 py-4"
          aria-hidden="true"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 space-y-2">
              <div class="h-4 w-2/3 rounded bg-slate-200" />
              <div class="h-3 w-1/3 rounded bg-slate-100" />
            </div>
            <div class="flex gap-2">
              <div class="h-6 w-16 rounded-full bg-slate-100" />
              <div class="h-6 w-16 rounded-full bg-slate-100" />
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="!filteredOrders.length" class="p-6">
        <EmptyState
          :icon="ClipboardList"
          :title="searchQuery ? 'No matching orders' : `No ${activeTab === 'all' ? '' : activeTab + ' '}orders`"
          :message="searchQuery
            ? 'Try a different search term or clear the filter.'
            : activeTab === 'all'
              ? 'Place your first order to get started.'
              : `No orders in this status group.`"
        >
          <template v-if="!searchQuery && activeTab === 'all'" #action>
            <RouterLink
              class="focus-ring inline-flex h-9 items-center gap-2 rounded-lg bg-signal px-4 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-signal/90"
              to="/client/new-order"
            >
              <Plus class="h-4 w-4" />
              Place your first order
            </RouterLink>
          </template>
        </EmptyState>
      </div>

      <div v-else class="overflow-x-auto">
      <table class="min-w-full divide-y divide-slate-200 text-sm">
        <thead class="bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-graphite">
          <tr>
            <th class="px-5 py-3">Order</th>
            <th class="px-5 py-3">Status</th>
            <th class="px-5 py-3">Payment</th>
            <th class="px-5 py-3">Deadline</th>
            <th class="px-5 py-3 text-right">Total</th>
            <th class="px-5 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr
            v-for="order in filteredOrders"
            :key="order.id"
            class="transition-colors hover:bg-slate-50"
          >
            <td class="px-5 py-4">
              <div class="flex items-center gap-2">
                <p class="font-semibold text-ink">#{{ order.id }} {{ order.topic }}</p>
                <span
                  v-if="order.is_urgent"
                  class="inline-flex items-center gap-0.5 rounded-full bg-red-100 px-1.5 py-0.5 text-xs font-semibold text-red-700"
                >
                  <Zap class="h-3 w-3" />
                  Urgent
                </span>
              </div>
              <p class="mt-0.5 text-xs text-graphite">
                {{ order.service_code || "Academic paper" }}
                <span v-if="order.number_of_pages"> · {{ order.number_of_pages }} pages</span>
              </p>
            </td>
            <td class="px-5 py-4">
              <StatusPill :label="order.status" :tone="statusTone(order.status)" />
            </td>
            <td class="px-5 py-4">
              <StatusPill
                :label="order.payment_status || 'pending'"
                :tone="paymentTone(order.payment_status)"
              />
            </td>
            <td class="px-5 py-4">
              <div class="flex items-center gap-1.5">
                <Clock3 class="h-3.5 w-3.5 shrink-0 text-slate-400" />
                <StatusPill
                  :label="deadlineLabel(order.client_deadline)"
                  :tone="deadlineTone(order.client_deadline)"
                />
              </div>
            </td>
            <td class="px-5 py-4 text-right font-semibold text-ink">
              {{ money(order.total_price, order.currency) }}
            </td>
            <td class="px-5 py-4 text-right">
              <RouterLink
                class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink hover:bg-slate-50"
                :to="`/client/orders/${order.id}`"
              >
                <ExternalLink class="h-3 w-3" />
                Open
              </RouterLink>
            </td>
          </tr>
        </tbody>
      </table>
      </div>

      <Pagination
        v-if="!searchQuery && orders.pagination.count > orders.pagination.pageSize"
        :page="orders.pagination.page"
        :page-size="orders.pagination.pageSize"
        :count="orders.pagination.count"
        @update:page="goToPage"
      />
    </div>
  </div>
</template>

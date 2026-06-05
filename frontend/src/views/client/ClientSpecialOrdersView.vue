<script setup lang="ts">
import { onMounted, ref, computed } from "vue";
import { useRouter } from "vue-router";
import { Plus, Sparkles, Zap } from "@lucide/vue";
import { useSpecialOrdersStore } from "@/stores/specialOrders";
import type { SpecialOrderStatus } from "@/types/specialOrders";

const store = useSpecialOrdersStore();
const router = useRouter();

onMounted(() => store.loadOrders());

const statusLabel: Partial<Record<SpecialOrderStatus, string>> = {
  inquiry: "Inquiry",
  quote_pending: "Awaiting Quote",
  quote_sent: "Quote Ready",
  quote_accepted: "Accepted",
  awaiting_payment: "Awaiting Payment",
  partially_funded: "Partially Funded",
  ready_for_staffing: "Ready for Staffing",
  assigned: "Assigned",
  on_hold: "On Hold",
  submitted: "Submitted",
  in_progress: "In Progress",
  ready_for_delivery: "Ready for Delivery",
  completed: "Completed",
  cancelled: "Cancelled",
  approved: "Approved",
  revision_requested: "Revision Requested",
  on_revision: "On Revision",
  refunded: "Refunded",
};

const statusClass: Partial<Record<SpecialOrderStatus, string>> = {
  inquiry: "bg-slate-100 text-graphite",
  quote_pending: "bg-amber-100 text-amber-700",
  quote_sent: "bg-blue-100 text-blue-700",
  quote_accepted: "bg-emerald-100 text-emerald-700",
  awaiting_payment: "bg-amber-100 text-amber-700",
  partially_funded: "bg-amber-100 text-amber-700",
  ready_for_staffing: "bg-blue-100 text-blue-700",
  assigned: "bg-blue-100 text-blue-700",
  on_hold: "bg-slate-100 text-graphite",
  submitted: "bg-purple-100 text-purple-700",
  in_progress: "bg-purple-100 text-purple-700",
  ready_for_delivery: "bg-blue-100 text-blue-700",
  completed: "bg-emerald-100 text-emerald-700",
  cancelled: "bg-slate-100 text-slate-400",
  approved: "bg-emerald-100 text-emerald-700",
  revision_requested: "bg-rose-100 text-rose-700",
  on_revision: "bg-amber-100 text-amber-700",
  refunded: "bg-slate-100 text-slate-400",
};

const active = computed(() =>
  store.orders.filter((o) => ["inquiry", "quote_pending", "quote_sent", "quote_accepted", "awaiting_payment", "partially_funded", "ready_for_staffing", "assigned", "in_progress", "ready_for_delivery", "revision_requested", "on_revision"].includes(o.status)),
);
const rest = computed(() =>
  store.orders.filter((o) => !["inquiry", "quote_pending", "quote_sent", "quote_accepted", "awaiting_payment", "partially_funded", "ready_for_staffing", "assigned", "in_progress", "ready_for_delivery", "revision_requested", "on_revision"].includes(o.status)),
);

function progress(total: number, done: number) {
  if (!total) return 0;
  return Math.round((done / total) * 100);
}
</script>

<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-4xl space-y-4">

      <!-- Header -->
      <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 class="text-xl font-bold text-ink">Special Orders</h1>
          <p class="text-sm text-graphite">Custom quote-based and milestone projects</p>
        </div>
        <div class="flex gap-2">
          <button
            class="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-ink hover:bg-slate-50 transition-colors"
            @click="router.push('/client/special-orders/express')"
          >
            <Zap class="size-4 text-amber-500" />
            Express Order
          </button>
          <button
            class="flex items-center gap-1.5 rounded-lg bg-berry px-4 py-2 text-sm font-medium text-white hover:bg-berry/90"
            @click="router.push('/client/special-orders/new')"
          >
            <Plus class="size-4" />
            Custom Quote
          </button>
        </div>
      </div>

      <div v-if="store.isLoading" class="py-16 text-center text-graphite animate-pulse">Loading…</div>

      <div
        v-else-if="!store.orders.length"
        class="rounded-lg border border-slate-200 bg-white p-16 text-center"
      >
        <Sparkles class="mx-auto mb-3 size-10 text-slate-300" />
        <p class="font-medium text-ink">No special orders yet</p>
        <p class="mt-1 text-sm text-graphite">Submit a request and we'll send you a custom quote.</p>
        <button
          class="mt-4 rounded-lg bg-berry px-4 py-2 text-sm font-medium text-white hover:bg-berry/90"
          @click="router.push('/client/special-orders/new')"
        >
          Create a Request
        </button>
      </div>

      <template v-else>
        <!-- Active -->
        <div v-if="active.length">
          <h2 class="mb-3 text-xs font-semibold uppercase tracking-wide text-graphite">Active</h2>
          <div class="space-y-3">
            <div
              v-for="order in active"
              :key="order.id"
              class="cursor-pointer rounded-lg border border-slate-200 bg-white p-5 hover:shadow-md transition-shadow"
              @click="router.push(`/client/special-orders/${order.id}`)"
            >
              <div class="flex items-start justify-between gap-4">
                <div class="min-w-0">
                  <div class="flex items-center gap-2">
                    <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="statusClass[order.status] ?? 'bg-slate-100 text-graphite'">
                      {{ statusLabel[order.status] ?? order.status.replace(/_/g, ' ') }}
                    </span>
                    <span class="text-xs font-mono text-graphite">{{ order.reference }}</span>
                  </div>
                  <h3 class="mt-1.5 font-semibold text-ink truncate">{{ order.title }}</h3>
                  <p class="mt-1 text-sm text-graphite line-clamp-2">{{ order.inquiry_details || order.description }}</p>
                </div>
                <div class="shrink-0 text-right">
                  <p v-if="order.quoted_price" class="font-semibold text-ink">${{ order.quoted_price }}</p>
                  <p v-else class="text-xs text-amber-600">Awaiting quote</p>
                </div>
              </div>

              <!-- Milestone progress (only if in progress) -->
              <div v-if="order.total_milestones > 0" class="mt-4">
                <div class="mb-1 flex justify-between text-xs text-graphite">
                  <span>{{ order.completed_milestones }} of {{ order.total_milestones }} milestones</span>
                  <span>{{ progress(order.total_milestones, order.completed_milestones) }}%</span>
                </div>
                <div class="h-1.5 overflow-hidden rounded-full bg-slate-100">
                  <div
                    class="h-full rounded-full bg-berry"
                    :style="{ width: `${progress(order.total_milestones, order.completed_milestones)}%` }"
                  />
                </div>
              </div>

              <div class="mt-3 text-xs text-graphite">
                <span v-if="order.duration_days">{{ order.duration_days }} day turnaround</span>
                <span v-if="order.writer_username" class="ml-3 text-emerald-700">{{ order.writer_username }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Past -->
        <div v-if="rest.length">
          <h2 class="mb-3 text-xs font-semibold uppercase tracking-wide text-graphite">Past</h2>
          <div class="space-y-2">
            <div
              v-for="order in rest"
              :key="order.id"
              class="flex cursor-pointer items-center gap-4 rounded-lg border border-slate-200 bg-white px-5 py-3 hover:shadow-md transition-shadow"
              @click="router.push(`/client/special-orders/${order.id}`)"
            >
              <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="statusClass[order.status] ?? 'bg-slate-100 text-graphite'">
                {{ statusLabel[order.status] ?? order.status.replace(/_/g, ' ') }}
              </span>
              <div class="min-w-0 flex-1">
                <p class="truncate font-medium text-ink">{{ order.title }}</p>
                <p class="text-xs text-graphite">{{ order.reference }}</p>
              </div>
              <p v-if="order.quoted_price" class="shrink-0 text-sm font-semibold text-ink">${{ order.quoted_price }}</p>
            </div>
          </div>
        </div>
      </template>

    </div>
  </div>
</template>

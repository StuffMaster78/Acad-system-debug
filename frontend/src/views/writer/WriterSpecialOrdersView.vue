<script setup lang="ts">
import { onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { Sparkles, Clock, CheckCircle, ChevronRight } from "@lucide/vue";
import { useSpecialOrdersStore } from "@/stores/specialOrders";
import type { SpecialOrderStatus } from "@/types/specialOrders";

const store = useSpecialOrdersStore();
const router = useRouter();

onMounted(() => store.loadOrders());

const statusLabel: Partial<Record<SpecialOrderStatus, string>> = {
  inquiry: "Inquiry",
  quote_pending: "Awaiting Quote",
  quote_sent: "Quote Sent",
  quote_accepted: "Quote Accepted",
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
  inquiry: "bg-slate-100 text-slate-600",
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
  store.orders.filter((o) =>
    ["assigned", "in_progress", "submitted", "ready_for_delivery", "revision_requested", "on_revision"].includes(o.status),
  ),
);
const past = computed(() =>
  store.orders.filter((o) => ["completed", "approved", "cancelled", "refunded"].includes(o.status)),
);

function progress(total: number, done: number) {
  if (!total) return 0;
  return Math.round((done / total) * 100);
}
</script>

<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-3xl space-y-4">

      <!-- Header -->
      <div>
        <h1 class="text-xl font-bold text-ink flex items-center gap-2">
          <Sparkles class="size-5 text-purple-500" />
          Special Orders
        </h1>
        <p class="text-sm text-graphite mt-0.5">Milestone-based projects you've been assigned to</p>
      </div>

      <div v-if="store.isLoading" class="py-16 text-center text-graphite animate-pulse">Loading…</div>

      <template v-else>
        <!-- Active -->
        <section v-if="active.length" class="space-y-3">
          <h2 class="text-xs font-semibold uppercase tracking-wider text-graphite flex items-center gap-1.5">
            <Clock class="size-3.5" /> Active
          </h2>
          <div
            v-for="order in active"
            :key="order.id"
            class="group flex cursor-pointer items-center gap-4 rounded-lg border border-slate-200 bg-white p-4 shadow-sm hover:border-purple-300 hover:shadow-md transition-all"
            @click="router.push(`/writer/special-orders/${order.id}`)"
          >
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <p class="font-semibold text-ink text-sm truncate">{{ order.title }}</p>
                <span :class="statusClass[order.status] ?? 'bg-slate-100 text-graphite'" class="text-xs px-2 py-0.5 rounded-full font-medium shrink-0">
                  {{ statusLabel[order.status] ?? order.status.replace(/_/g, ' ') }}
                </span>
              </div>
              <p class="text-xs text-graphite mt-0.5 truncate">{{ order.reference }}</p>

              <!-- Milestone progress bar -->
              <div v-if="order.total_milestones" class="mt-2 space-y-1">
                <div class="flex justify-between text-xs text-graphite">
                  <span>{{ order.completed_milestones }}/{{ order.total_milestones }} milestones</span>
                  <span>{{ progress(order.total_milestones, order.completed_milestones) }}%</span>
                </div>
                <div class="h-1.5 rounded-full bg-slate-100 overflow-hidden">
                  <div
                    class="h-full rounded-full bg-purple-500 transition-all"
                    :style="{ width: progress(order.total_milestones, order.completed_milestones) + '%' }"
                  />
                </div>
              </div>
            </div>

            <div class="flex flex-col items-end gap-1 shrink-0">
              <p v-if="order.writer_compensation?.type === 'fixed_amount'" class="text-sm font-semibold text-ink">
                {{ order.writer_compensation.currency }} {{ order.writer_compensation.amount }}
              </p>
              <p v-else-if="order.writer_compensation?.type === 'percentage'" class="text-sm font-semibold text-ink">
                {{ order.writer_compensation.percentage }}% share
              </p>
              <ChevronRight class="size-4 text-slate-300 group-hover:text-purple-400 transition-colors mt-1" />
            </div>
          </div>
        </section>

        <!-- Empty active -->
        <div
          v-if="!active.length && !store.isLoading"
          class="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center"
        >
          <Sparkles class="mx-auto mb-3 size-8 text-slate-300" />
          <p class="text-sm font-medium text-graphite">No active special orders</p>
          <p class="text-xs text-slate-400 mt-1">You'll be notified when you're assigned to a project</p>
        </div>

        <!-- Completed / Cancelled -->
        <section v-if="past.length" class="space-y-3">
          <h2 class="text-xs font-semibold uppercase tracking-wider text-graphite flex items-center gap-1.5">
            <CheckCircle class="size-3.5" /> Past
          </h2>
          <div
            v-for="order in past"
            :key="order.id"
            class="group flex cursor-pointer items-center gap-4 rounded-lg border border-slate-200 bg-white p-4 opacity-75 hover:opacity-100 hover:border-slate-300 transition-all"
            @click="router.push(`/writer/special-orders/${order.id}`)"
          >
            <div class="flex-1 min-w-0">
              <p class="font-medium text-ink text-sm truncate">{{ order.title }}</p>
              <p class="text-xs text-graphite mt-0.5">{{ order.reference }}</p>
            </div>
            <div class="flex items-center gap-3 shrink-0">
              <span :class="statusClass[order.status] ?? 'bg-slate-100 text-graphite'" class="text-xs px-2 py-0.5 rounded-full font-medium">
                {{ statusLabel[order.status] ?? order.status.replace(/_/g, ' ') }}
              </span>
              <ChevronRight class="size-4 text-slate-300 group-hover:text-slate-400 transition-colors" />
            </div>
          </div>
        </section>
      </template>
    </div>
  </div>
</template>

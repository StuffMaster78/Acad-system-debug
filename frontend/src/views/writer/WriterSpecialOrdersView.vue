<script setup lang="ts">
import { onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { Sparkles, Clock, CheckCircle, ChevronRight } from "@lucide/vue";
import { useSpecialOrdersStore } from "@/stores/specialOrders";
import type { SpecialOrderStatus } from "@/types/specialOrders";

const store = useSpecialOrdersStore();
const router = useRouter();

onMounted(() => store.loadOrders());

const statusLabel: Record<SpecialOrderStatus, string> = {
  draft: "Draft",
  pending_quote: "Awaiting Quote",
  quote_sent: "Quote Sent",
  quote_accepted: "Quote Accepted",
  quote_rejected: "Quote Rejected",
  in_progress: "In Progress",
  completed: "Completed",
  cancelled: "Cancelled",
};

const statusClass: Record<SpecialOrderStatus, string> = {
  draft: "bg-slate-100 text-slate-600",
  pending_quote: "bg-amber-100 text-amber-700",
  quote_sent: "bg-blue-100 text-blue-700",
  quote_accepted: "bg-emerald-100 text-emerald-700",
  quote_rejected: "bg-rose-100 text-rose-700",
  in_progress: "bg-purple-100 text-purple-700",
  completed: "bg-emerald-100 text-emerald-700",
  cancelled: "bg-slate-100 text-slate-400",
};

const active = computed(() =>
  store.orders.filter((o) =>
    ["quote_accepted", "in_progress"].includes(o.status),
  ),
);
const past = computed(() =>
  store.orders.filter((o) => ["completed", "cancelled"].includes(o.status)),
);

function progress(total: number, done: number) {
  if (!total) return 0;
  return Math.round((done / total) * 100);
}
</script>

<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-3xl space-y-6">

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
            class="group flex cursor-pointer items-center gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm hover:border-purple-300 hover:shadow-md transition-all"
            @click="router.push(`/writer/special-orders/${order.id}`)"
          >
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 flex-wrap">
                <p class="font-semibold text-ink text-sm truncate">{{ order.title }}</p>
                <span :class="statusClass[order.status]" class="text-xs px-2 py-0.5 rounded-full font-medium shrink-0">
                  {{ statusLabel[order.status] }}
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
              <p v-if="order.final_price || order.quoted_price" class="text-sm font-semibold text-ink">
                ${{ order.final_price ?? order.quoted_price }}
              </p>
              <p v-if="order.deadline" class="text-xs text-graphite">Due {{ order.deadline }}</p>
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
            class="group flex cursor-pointer items-center gap-4 rounded-xl border border-slate-200 bg-white p-4 opacity-75 hover:opacity-100 hover:border-slate-300 transition-all"
            @click="router.push(`/writer/special-orders/${order.id}`)"
          >
            <div class="flex-1 min-w-0">
              <p class="font-medium text-ink text-sm truncate">{{ order.title }}</p>
              <p class="text-xs text-graphite mt-0.5">{{ order.reference }}</p>
            </div>
            <div class="flex items-center gap-3 shrink-0">
              <span :class="statusClass[order.status]" class="text-xs px-2 py-0.5 rounded-full font-medium">
                {{ statusLabel[order.status] }}
              </span>
              <ChevronRight class="size-4 text-slate-300 group-hover:text-slate-400 transition-colors" />
            </div>
          </div>
        </section>
      </template>
    </div>
  </div>
</template>

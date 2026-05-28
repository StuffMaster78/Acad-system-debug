<script setup lang="ts">
import { onMounted } from "vue";
import {
  Clock3,
  CreditCard,
  FileWarning,
  LifeBuoy,
  RefreshCw,
  ShieldAlert,
} from "@lucide/vue";
import MetricTile from "@/components/ui/MetricTile.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useSupportWorkspaceStore } from "@/stores/supportWorkspace";

const support = useSupportWorkspaceStore();

function statusTone(status?: string | null): "danger" | "warning" | "success" | "neutral" {
  const s = (status ?? "").toLowerCase();
  if (s.includes("critical") || s.includes("escalated") || s.includes("breach")) return "danger";
  if (s.includes("open") || s.includes("progress") || s.includes("pending") || s.includes("high") || s.includes("warning")) return "warning";
  if (s.includes("closed") || s.includes("resolved") || s.includes("track")) return "success";
  return "neutral";
}

onMounted(() => {
  support.hydrate().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Support</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Rescue queue</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          Live overview of open tickets, SLA pressure, and order rescue status.
        </p>
      </div>
      <button
        class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
        type="button"
        :disabled="support.isLoading"
        @click="support.hydrate().catch(() => undefined)"
      >
        <RefreshCw class="h-4 w-4" :class="support.isLoading ? 'animate-spin' : ''" />
        Refresh
      </button>
    </section>

    <p v-if="support.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ support.error }}
    </p>
    <p v-if="support.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ support.notice }}
    </p>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <MetricTile v-for="metric in support.metrics" :key="metric.label" :metric="metric" />
    </section>

    <section class="grid gap-6 xl:grid-cols-[1fr_380px]">
      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <div class="flex items-center justify-between gap-3">
          <div>
            <h2 class="text-base font-semibold text-ink">Rescue summary</h2>
            <p class="mt-1 text-sm text-graphite">Orders and disputes requiring staff attention.</p>
          </div>
          <StatusPill
            :label="`${support.rescueCount} active`"
            :tone="support.rescueCount ? 'warning' : 'success'"
          />
        </div>

        <div class="mt-5 grid gap-3 sm:grid-cols-2">
          <div class="rounded-md border border-slate-200 p-4">
            <div class="flex items-center gap-2">
              <ShieldAlert class="h-4 w-4 text-signal" />
              <p class="text-sm font-semibold text-ink">Disputed orders</p>
            </div>
            <p class="mt-3 text-2xl font-semibold text-ink">{{ support.orders.disputed_orders?.count ?? 0 }}</p>
            <p class="mt-1 text-xs text-graphite">Orders in dispute needing staff context.</p>
          </div>
          <div class="rounded-md border border-slate-200 p-4">
            <div class="flex items-center gap-2">
              <CreditCard class="h-4 w-4 text-signal" />
              <p class="text-sm font-semibold text-ink">Payment issues</p>
            </div>
            <p class="mt-3 text-2xl font-semibold text-ink">{{ support.orders.payment_issue_orders?.count ?? 0 }}</p>
            <p class="mt-1 text-xs text-graphite">Failed, pending, or mismatched payment states.</p>
          </div>
          <div class="rounded-md border border-slate-200 p-4">
            <div class="flex items-center gap-2">
              <FileWarning class="h-4 w-4 text-signal" />
              <p class="text-sm font-semibold text-ink">Pending refunds</p>
            </div>
            <p class="mt-3 text-2xl font-semibold text-ink">{{ support.orders.pending_refunds?.count ?? 0 }}</p>
            <p class="mt-1 text-xs text-graphite">Refund requests waiting for review.</p>
          </div>
          <div class="rounded-md border border-slate-200 p-4">
            <div class="flex items-center gap-2">
              <LifeBuoy class="h-4 w-4 text-signal" />
              <p class="text-sm font-semibold text-ink">Ticketed orders</p>
            </div>
            <p class="mt-3 text-2xl font-semibold text-ink">{{ support.orders.orders_with_tickets?.count ?? 0 }}</p>
            <p class="mt-1 text-xs text-graphite">Orders with linked support conversations.</p>
          </div>
        </div>
      </div>

      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <div class="flex items-center gap-2">
          <Clock3 class="h-5 w-5 text-signal" />
          <h2 class="text-base font-semibold text-ink">SLA board</h2>
        </div>
        <div class="mt-4 grid grid-cols-2 gap-3">
          <div class="rounded-md border border-slate-200 p-3 text-center">
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite">On track</p>
            <p class="mt-2 text-2xl font-semibold text-ink">{{ support.sla.active_status?.on_track ?? 0 }}</p>
          </div>
          <div class="rounded-md border border-slate-200 p-3 text-center">
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Breached</p>
            <p class="mt-2 text-2xl font-semibold text-ink">{{ support.sla.active_status?.breached ?? 0 }}</p>
          </div>
        </div>

        <div v-if="support.sla.upcoming_deadlines?.length" class="mt-4 space-y-2">
          <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Upcoming deadlines</p>
          <div
            v-for="deadline in support.sla.upcoming_deadlines"
            :key="String(deadline.id ?? deadline.order_id)"
            class="flex items-center justify-between gap-3 rounded-md border border-slate-200 px-3 py-2 text-sm"
          >
            <span class="min-w-0 truncate text-graphite">Order #{{ deadline.order_id ?? deadline.order }}</span>
            <StatusPill
              :label="String(deadline.time_remaining_display ?? deadline.status ?? 'upcoming')"
              :tone="statusTone(String(deadline.status ?? 'warning'))"
            />
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

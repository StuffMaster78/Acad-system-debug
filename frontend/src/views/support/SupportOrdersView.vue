<script setup lang="ts">
import { onMounted } from "vue";
import { useRouter } from "vue-router";
const router = useRouter();
import type { Component } from "vue";
import {
  CreditCard,
  FileWarning,
  LifeBuoy,
  RefreshCw,
  ShieldAlert,
} from "@lucide/vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useSupportWorkspaceStore } from "@/stores/supportWorkspace";

const support = useSupportWorkspaceStore();

interface Bucket {
  key: string;
  label: string;
  icon: Component;
  count: number;
  detail: string;
  records: Array<Record<string, unknown>>;
}

const buckets = (): Bucket[] => [
  {
    key: "disputed",
    label: "Disputed orders",
    icon: ShieldAlert,
    count: support.orders.disputed_orders?.count ?? 0,
    detail: "Orders currently in dispute — need staff context or resolution.",
    records: support.orders.disputed_orders?.orders ?? [],
  },
  {
    key: "payment",
    label: "Payment issues",
    icon: CreditCard,
    count: support.orders.payment_issue_orders?.count ?? 0,
    detail: "Failed, pending, or mismatched payment states requiring review.",
    records: support.orders.payment_issue_orders?.orders ?? [],
  },
  {
    key: "refunds",
    label: "Pending refunds",
    icon: FileWarning,
    count: support.orders.pending_refunds?.count ?? 0,
    detail: "Refund requests awaiting staff action.",
    records: support.orders.pending_refunds?.refunds ?? [],
  },
  {
    key: "ticketed",
    label: "Ticketed orders",
    icon: LifeBuoy,
    count: support.orders.orders_with_tickets?.count ?? 0,
    detail: "Orders linked to open support tickets.",
    records: support.orders.orders_with_tickets?.orders ?? [],
  },
];

function recordLabel(record: Record<string, unknown>): string {
  return String(record.topic ?? record.title ?? record.order_topic ?? `Record #${record.id ?? "unknown"}`);
}

function recordStatus(record: Record<string, unknown>): string {
  return String(record.status ?? record.payment_status ?? "pending review");
}

onMounted(() => {
  if (!support.orders.summary) support.hydrate().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Support</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Order rescue</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Disputed orders, payment issues, pending refunds, and ticketed orders requiring staff attention.
        </p>
      </div>
      <button
        class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold disabled:opacity-60"
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

    <div class="space-y-8">
      <section
        v-for="bucket in buckets()"
        :key="bucket.key"
        class="rounded-lg border border-slate-200 bg-white"
      >
        <div class="flex items-center justify-between gap-4 border-b border-slate-200 px-5 py-4">
          <div class="flex items-center gap-3">
            <component :is="bucket.icon" class="h-5 w-5 text-signal" />
            <div>
              <h2 class="text-base font-semibold text-ink">{{ bucket.label }}</h2>
              <p class="mt-0.5 text-xs text-graphite">{{ bucket.detail }}</p>
            </div>
          </div>
          <StatusPill
            :label="`${bucket.count} ${bucket.count === 1 ? 'item' : 'items'}`"
            :tone="bucket.count ? 'warning' : 'success'"
          />
        </div>

        <div v-if="!bucket.records.length" class="px-5 py-8">
          <EmptyState
            :icon="bucket.icon"
            :title="`No ${bucket.label.toLowerCase()}`"
            message="Nothing requiring attention in this category."
          />
        </div>

        <div v-else class="divide-y divide-slate-100">
          <div
            v-for="record in bucket.records"
            :key="String(record.id ?? record.order_id)"
            class="flex cursor-pointer items-start justify-between gap-4 px-5 py-4 transition-colors hover:bg-slate-50"
            @click="router.push(`/support/orders/${record.order_id ?? record.id}`)"
          >
            <div class="min-w-0 flex-1">
              <p class="truncate font-semibold text-ink">{{ recordLabel(record) }}</p>
              <p class="mt-0.5 text-sm text-graphite">
                Order #{{ record.order_id ?? record.id ?? "unknown" }}
                · {{ recordStatus(record) }}
              </p>
              <p v-if="record.reason" class="mt-1 text-sm text-graphite">{{ record.reason }}</p>
              <p v-if="record.amount" class="mt-1 text-sm font-semibold text-ink">
                {{ record.currency ?? "USD" }} {{ record.amount }}
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<template>
  <div class="space-y-4">
    <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
      <h2 class="text-base font-semibold text-ink">Assignment</h2>
      <dl class="mt-4 grid gap-4 sm:grid-cols-2">
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Assigned writer</dt>
          <dd class="mt-1 font-mono text-sm text-ink">
            {{ lifecycle?.has_current_assignment ? maskedWriter(lifecycle.current_writer_id) : "Unassigned" }}
          </dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Assignment ID</dt>
          <dd class="mt-1 text-sm text-ink">{{ lifecycle?.current_assignment_id ?? "—" }}</dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Preferred writer</dt>
          <dd class="mt-1 font-mono text-sm text-ink">
            {{ order.preferred_writer ? maskedWriter(order.preferred_writer as number) : "None" }}
          </dd>
        </div>
        <div>
          <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Reassignment pending</dt>
          <dd class="mt-1 text-sm text-ink">{{ lifecycle?.has_pending_reassignment_request ? `#${lifecycle.pending_reassignment_request_id}` : "No" }}</dd>
        </div>
      </dl>
    </div>

    <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
      <h2 class="text-base font-semibold text-ink">Writer payout estimate</h2>
      <p class="mt-2 text-sm text-ink font-semibold">{{ money(order.writer_compensation, order.currency) }}</p>
      <p class="mt-1 text-xs text-graphite">
        <!-- TODO: wire bids/expressions of interest list via staffing API -->
        Bid history and capacity check require the staffing detail endpoint.
      </p>
    </div>

    <div class="rounded-lg border border-slate-100 bg-slate-50 p-4">
      <p class="text-xs text-graphite">
        Full staffing actions (reassign, override, capacity check) are available from the Admin Orders ops panel.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { OrderSummary, OrderLifecycle } from "@/types/orders";
import { maskedWriter } from "../types";

const props = defineProps<{
  orderId: string;
  order: OrderSummary;
  lifecycle: OrderLifecycle | null;
}>();

function money(v: string | number | null | undefined, currency = "USD"): string {
  if (v === null || v === undefined || v === "") return `${currency} 0.00`;
  return `${currency} ${v}`;
}
</script>

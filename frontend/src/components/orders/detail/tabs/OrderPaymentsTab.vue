<template>
  <div class="space-y-4">
    <!-- Client: limited payment view -->
    <template v-if="role === 'client'">
      <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <h2 class="text-base font-semibold text-ink">Payment summary</h2>
        <dl class="mt-4 grid gap-4 sm:grid-cols-2">
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Amount paid</dt>
            <dd class="mt-1 text-sm font-semibold text-ink">{{ money(order.amount_paid, order.currency) }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Balance due</dt>
            <dd class="mt-1 text-sm font-semibold text-ink">{{ money(order.remaining_balance, order.currency) }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Payment status</dt>
            <dd class="mt-1 text-sm text-ink capitalize">{{ order.payment_status ?? "—" }}</dd>
          </div>
          <div v-if="order.discount_code_used">
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Discount applied</dt>
            <dd class="mt-1 font-mono text-sm text-ink">{{ order.discount_code_used }}</dd>
          </div>
        </dl>
        <p class="mt-4 text-xs text-graphite">Invoice and receipt available from your billing page.</p>
      </div>
    </template>

    <!-- Support: limited view -->
    <template v-else-if="role === 'support'">
      <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <h2 class="text-base font-semibold text-ink">Payment overview</h2>
        <dl class="mt-4 grid gap-4 sm:grid-cols-2">
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Total</dt>
            <dd class="mt-1 text-sm font-semibold text-ink">{{ money(order.total_price, order.currency) }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Paid</dt>
            <dd class="mt-1 text-sm text-ink">{{ money(order.amount_paid, order.currency) }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Balance</dt>
            <dd class="mt-1 text-sm text-ink">{{ money(order.remaining_balance, order.currency) }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Status</dt>
            <dd class="mt-1 text-sm capitalize text-ink">{{ order.payment_status ?? "—" }}</dd>
          </div>
        </dl>
        <p class="mt-3 text-xs text-graphite">Full payment trail and gateway details available to admin only.</p>
      </div>
    </template>

    <!-- Admin/superadmin: full payment trail -->
    <template v-else>
      <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <h2 class="text-base font-semibold text-ink">Full payment trail</h2>
        <dl class="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Total amount</dt>
            <dd class="mt-1 text-sm font-semibold text-ink">{{ money(order.total_price, order.currency) }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Amount paid</dt>
            <dd class="mt-1 text-sm text-ink">{{ money(order.amount_paid, order.currency) }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Balance due</dt>
            <dd class="mt-1 text-sm text-ink">{{ money(order.remaining_balance, order.currency) }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Writer payout</dt>
            <dd class="mt-1 text-sm text-ink">{{ money(order.writer_compensation, order.currency) }}</dd>
          </div>
          <div>
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Payment status</dt>
            <dd class="mt-1 text-sm capitalize text-ink">{{ order.payment_status ?? "—" }}</dd>
          </div>
          <div v-if="order.discount_code_used">
            <dt class="text-xs font-semibold uppercase tracking-wide text-graphite">Discount</dt>
            <dd class="mt-1 font-mono text-sm text-ink">{{ order.discount_code_used }}</dd>
          </div>
        </dl>
        <p class="mt-4 border-t border-slate-100 pt-3 text-xs text-graphite">
          <!-- TODO: wire wallet_id, payment_intent_id, ledger journal entries via dedicated order payment API endpoint -->
          Wallet, gateway intent, ledger journal, and refund status require the order payment details endpoint (not yet wired).
        </p>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { UserRole } from "@/types/roles";
import type { OrderSummary } from "@/types/orders";

defineProps<{
  orderId: string;
  order: OrderSummary;
  role: UserRole;
}>();

function money(v: string | number | null | undefined, currency = "USD"): string {
  if (v === null || v === undefined || v === "") return `${currency} 0.00`;
  return `${currency} ${v}`;
}
</script>

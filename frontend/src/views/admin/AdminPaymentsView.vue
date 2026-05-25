<script setup lang="ts">
import { onMounted } from "vue";
import {
  CheckCircle2,
  CreditCard,
  RefreshCw,
  Search,
  Send,
  WalletCards,
  XCircle,
} from "@lucide/vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useAdminPaymentsStore } from "@/stores/adminPayments";

const payments = useAdminPaymentsStore();

const metricToneClasses = {
  neutral: "border-slate-200 bg-white",
  good: "border-emerald-200 bg-emerald-50",
  warn: "border-amber-200 bg-amber-50",
  risk: "border-rose-200 bg-rose-50",
};

const filterOptions = [
  { key: "all", label: "All" },
  { key: "client", label: "Client payments" },
  { key: "writer", label: "Writer payouts" },
  { key: "refund", label: "Refunds" },
] as const;

function formatDate(value?: string | null) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatAmount(value: string | number, currency = "USD") {
  const numeric = Number(value);
  if (Number.isNaN(numeric)) return String(value);
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(numeric);
}

function statusTone(status?: string | null) {
  const normalized = (status ?? "").toLowerCase();
  if (normalized.includes("failed") || normalized.includes("rejected") || normalized.includes("cancel")) {
    return "danger";
  }
  if (normalized.includes("pending") || normalized.includes("held") || normalized.includes("review")) {
    return "warning";
  }
  if (normalized.includes("complete") || normalized.includes("approved") || normalized.includes("released") || normalized.includes("posted") || normalized.includes("captured")) {
    return "success";
  }
  return "neutral";
}

onMounted(() => {
  payments.hydrate().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-8">
    <section class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase text-signal">Admin</p>
        <h1 class="mt-2 text-3xl font-semibold">Payments</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          Client payments, wallet balances, refund queues, and writer payout
          operations separated from the communications desk.
        </p>
      </div>
      <button
        class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
        type="button"
        @click="payments.hydrate"
      >
        <RefreshCw class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <p
      v-if="payments.error"
      class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {{ payments.error }} Preview mode will still show the layout.
    </p>

    <p
      v-if="payments.notice"
      class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900"
    >
      {{ payments.notice }}
    </p>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div
        v-for="metric in payments.metrics"
        :key="metric.label"
        class="min-h-32 rounded-md border p-4 shadow-panel"
        :class="metricToneClasses[metric.tone]"
      >
        <p class="text-sm font-medium text-graphite">{{ metric.label }}</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ metric.value }}</p>
        <p class="mt-2 text-sm leading-5 text-graphite">{{ metric.detail }}</p>
      </div>
    </section>

    <section class="grid gap-6 xl:grid-cols-[minmax(0,1.35fr)_minmax(360px,0.8fr)]">
      <div class="rounded-md border border-slate-200 bg-white shadow-panel">
        <div class="flex flex-col gap-4 border-b border-slate-200 px-4 py-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div class="flex items-center gap-2">
              <CreditCard class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold">Payment activity</h2>
            </div>
            <p class="mt-1 text-sm text-graphite">
              Client inflows, writer payout requests, and refund operations.
            </p>
          </div>

          <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
            <div class="inline-flex rounded-md border border-slate-200 bg-slate-50 p-1">
              <button
                v-for="option in filterOptions"
                :key="option.key"
                class="focus-ring min-h-9 rounded px-3 text-xs font-semibold"
                :class="payments.filter === option.key ? 'bg-white text-ink shadow-sm' : 'text-graphite'"
                type="button"
                @click="payments.filter = option.key"
              >
                {{ option.label }}
              </button>
            </div>
            <label class="relative block min-w-64">
              <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-graphite" />
              <input
                v-model="payments.query"
                class="focus-ring h-10 w-full rounded-md border border-slate-200 bg-white pl-9 pr-3 text-sm"
                type="search"
                placeholder="Search payments"
              >
            </label>
          </div>
        </div>

        <div v-if="payments.feed.length" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50 text-left text-xs font-semibold uppercase text-graphite">
              <tr>
                <th class="px-4 py-3">Record</th>
                <th class="px-4 py-3">Type</th>
                <th class="px-4 py-3">Amount</th>
                <th class="px-4 py-3">Status</th>
                <th class="px-4 py-3">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="item in payments.feed" :key="item.id">
                <td class="px-4 py-4">
                  <p class="font-semibold text-ink">{{ item.title }}</p>
                  <p class="mt-1 text-xs text-graphite">{{ item.subtitle }}</p>
                </td>
                <td class="px-4 py-4 capitalize text-graphite">{{ item.source }}</td>
                <td class="px-4 py-4 font-semibold text-ink">{{ formatAmount(item.amount) }}</td>
                <td class="px-4 py-4">
                  <StatusPill :label="item.status" :tone="statusTone(item.status)" />
                </td>
                <td class="px-4 py-4 text-graphite">{{ formatDate(item.date) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="p-4">
          <EmptyState
            :icon="CreditCard"
            title="No payment records"
            message="Payment records will appear here once wallet, refund, and payout endpoints respond."
          />
        </div>
      </div>

      <aside class="space-y-6">
        <section class="rounded-md border border-slate-200 bg-white shadow-panel">
          <div class="flex min-h-16 items-center justify-between gap-3 border-b border-slate-200 px-4">
            <div class="flex items-center gap-2">
              <WalletCards class="h-5 w-5 text-signal" />
              <div>
                <h2 class="text-base font-semibold">Writer payout ops</h2>
                <p class="text-sm text-graphite">Approve, process, or reject payout holds.</p>
              </div>
            </div>
          </div>

          <div v-if="payments.payouts.length" class="divide-y divide-slate-100">
            <article
              v-for="payout in payments.payouts"
              :key="payout.id"
              class="px-4 py-4"
            >
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="font-semibold text-ink">{{ payout.writer_email || `Writer #${payout.writer_id}` }}</p>
                  <p class="mt-1 text-sm text-graphite">{{ payout.reason || payout.reference || "Payout request" }}</p>
                </div>
                <p class="font-semibold text-ink">{{ formatAmount(payout.amount) }}</p>
              </div>
              <div class="mt-3 flex flex-wrap items-center gap-2">
                <StatusPill :label="payout.workflow_status || payout.status" :tone="statusTone(payout.workflow_status || payout.status)" />
                <span class="text-xs text-graphite">{{ formatDate(payout.created_at) }}</span>
              </div>
              <div class="mt-4 grid gap-2 sm:grid-cols-3">
                <button
                  class="focus-ring inline-flex h-9 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold"
                  type="button"
                  :disabled="payments.isMutating"
                  @click="payments.approvePayout(payout.id).catch(() => undefined)"
                >
                  <CheckCircle2 class="h-4 w-4" />
                  Approve
                </button>
                <button
                  class="focus-ring inline-flex h-9 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold"
                  type="button"
                  :disabled="payments.isMutating"
                  @click="payments.processPayout(payout.id).catch(() => undefined)"
                >
                  <Send class="h-4 w-4" />
                  Process
                </button>
                <button
                  class="focus-ring inline-flex h-9 items-center justify-center gap-2 rounded-md border border-rose-200 bg-white px-3 text-xs font-semibold text-rose-700"
                  type="button"
                  :disabled="payments.isMutating"
                  @click="payments.rejectPayout(payout.id).catch(() => undefined)"
                >
                  <XCircle class="h-4 w-4" />
                  Reject
                </button>
              </div>
            </article>
          </div>

          <div v-else class="p-4">
            <EmptyState
              :icon="WalletCards"
              title="No writer payout requests"
              message="Writer payout requests from wallet holds will appear here."
            />
          </div>
        </section>

        <section class="rounded-md border border-slate-200 bg-white shadow-panel">
          <div class="border-b border-slate-200 px-4 py-4">
            <div class="flex items-center gap-2">
              <WalletCards class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold">Wallet balances</h2>
            </div>
            <p class="mt-1 text-sm text-graphite">Client and writer wallet state from the canonical wallets app.</p>
          </div>

          <div v-if="payments.wallets.length" class="divide-y divide-slate-100">
            <article
              v-for="wallet in payments.wallets"
              :key="wallet.id"
              class="grid gap-2 px-4 py-4 sm:grid-cols-[1fr_auto]"
            >
              <div>
                <p class="font-semibold text-ink capitalize">{{ wallet.wallet_type }} wallet #{{ wallet.id }}</p>
                <p class="mt-1 text-xs text-graphite">
                  Owner #{{ wallet.owner_user_id || "n/a" }} · Site #{{ wallet.website_id || "n/a" }}
                </p>
              </div>
              <div class="sm:text-right">
                <p class="font-semibold text-ink">{{ formatAmount(wallet.available_balance || 0, wallet.currency || "USD") }}</p>
                <StatusPill :label="wallet.status || 'unknown'" :tone="statusTone(wallet.status)" />
              </div>
            </article>
          </div>

          <div v-else class="p-4">
            <EmptyState
              :icon="WalletCards"
              title="No wallets loaded"
              message="Admin wallet records will appear here when the backend is connected."
            />
          </div>
        </section>
      </aside>
    </section>
  </div>
</template>

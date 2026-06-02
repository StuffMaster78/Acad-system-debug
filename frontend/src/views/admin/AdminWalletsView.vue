<script setup lang="ts">
import { computed, onMounted } from "vue";
import {
  BadgeDollarSign,
  Banknote,
  CircleDollarSign,
  HandCoins,
  LockKeyhole,
  RefreshCw,
  Search,
  ShieldCheck,
  WalletCards,
  Wrench,
} from "@lucide/vue";
import BaseDataTable, { type DataTableColumn } from "@/components/ui/BaseDataTable.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useAdminWalletsStore } from "@/stores/adminWallets";
import { useWebsitesStore } from "@/stores/websites";

const wallets = useAdminWalletsStore();

const metricToneClasses = {
  neutral: "border-slate-200 bg-white",
  good: "border-emerald-200 bg-emerald-50",
  warn: "border-amber-200 bg-amber-50",
  risk: "border-rose-200 bg-rose-50",
};

const filterOptions = [
  { key: "all", label: "All" },
  { key: "client", label: "Clients" },
  { key: "writer", label: "Writers" },
  { key: "system", label: "System" },
  { key: "attention", label: "Needs attention" },
] as const;

const walletColumns: DataTableColumn[] = [
  { key: "id", label: "Wallet", sortable: true },
  { key: "wallet_type", label: "Type", sortable: true },
  { key: "owner_user_id", label: "Owner", sortable: true },
  { key: "available_balance", label: "Available", align: "right", sortable: true },
  { key: "pending_balance", label: "Pending", align: "right", sortable: true },
  { key: "status", label: "Status", sortable: true },
];

const entryColumns: DataTableColumn[] = [
  { key: "created_at", label: "Date", sortable: true },
  { key: "entry_type", label: "Entry", sortable: true },
  { key: "direction", label: "Direction", sortable: true },
  { key: "amount", label: "Amount", align: "right", sortable: true },
  { key: "reference", label: "Reference" },
  { key: "status", label: "Status", sortable: true },
];

const holdColumns: DataTableColumn[] = [
  { key: "id", label: "Hold", sortable: true },
  { key: "amount", label: "Amount", align: "right", sortable: true },
  { key: "reason", label: "Reason" },
  { key: "status", label: "Status", sortable: true },
  { key: "expires_at", label: "Expires", sortable: true },
];

const walletRows = computed(() => wallets.filteredWallets as unknown as Record<string, unknown>[]);
const entryRows = computed(() => wallets.entries as unknown as Record<string, unknown>[]);
const holdRows = computed(() => wallets.holds as unknown as Record<string, unknown>[]);

function formatDate(value?: string | null) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatAmount(value: string | number | undefined | null, currency = "USD") {
  const numeric = Number(value ?? 0);
  if (Number.isNaN(numeric)) return String(value ?? "0");
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(numeric);
}

function statusTone(status?: string | null) {
  const normalized = `${status ?? ""}`.toLowerCase();
  if (normalized.includes("suspend") || normalized.includes("lock") || normalized.includes("fail") || normalized.includes("capture")) {
    return "danger";
  }
  if (normalized.includes("pending") || normalized.includes("hold") || normalized.includes("active")) {
    return normalized.includes("active") ? "success" : "warning";
  }
  if (normalized.includes("complete") || normalized.includes("release") || normalized.includes("posted")) {
    return "success";
  }
  return "neutral";
}

function selectWallet(row: Record<string, unknown>) {
  const id = Number(row.id);
  if (!Number.isNaN(id)) wallets.loadWalletDetail(id).catch(() => undefined);
}

function selectHold(row: Record<string, unknown>) {
  const id = Number(row.id);
  if (!Number.isNaN(id)) wallets.selectedHoldId = id;
}

const websites = useWebsitesStore();
onMounted(() => {
  wallets.hydrate().catch(() => undefined);
  websites.ensure();
});
</script>

<template>
  <div class="space-y-8">
    <section class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase text-signal">Admin finance</p>
        <h1 class="mt-2 text-3xl font-semibold">Wallet control center</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          Inspect tenant-scoped wallets, audit ledger entries, manage holds, and run controlled balance adjustments.
        </p>
      </div>
      <button
        class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
        type="button"
        :disabled="wallets.isLoading"
        @click="wallets.hydrate"
      >
        <RefreshCw class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <p
      v-if="wallets.error"
      class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {{ wallets.error }} Preview mode will still show the wallet workflow.
    </p>

    <p
      v-if="wallets.notice"
      class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900"
    >
      {{ wallets.notice }}
    </p>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div
        v-for="metric in wallets.metrics"
        :key="metric.label"
        class="min-h-32 rounded-md border p-4"
        :class="metricToneClasses[metric.tone]"
      >
        <p class="text-sm font-medium text-graphite">{{ metric.label }}</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ metric.value }}</p>
        <p class="mt-2 text-sm leading-5 text-graphite">{{ metric.detail }}</p>
      </div>
    </section>

    <section class="grid gap-6 xl:grid-cols-[minmax(0,1.25fr)_minmax(360px,0.85fr)]">
      <div class="space-y-4">
        <section class="rounded-xl border border-slate-200 bg-white">
          <div class="flex items-center gap-2 border-b border-slate-200 px-5 py-4">
            <WalletCards class="h-5 w-5 text-signal" />
            <div>
              <h2 class="text-base font-semibold text-ink">Wallet registry</h2>
              <p class="text-xs text-graphite">Client, writer, and system wallets.</p>
            </div>
          </div>
          <div class="flex flex-wrap items-center gap-3 border-b border-slate-100 bg-slate-50 px-5 py-3">
            <div class="flex flex-wrap gap-1">
              <button
                v-for="option in filterOptions"
                :key="option.key"
                class="focus-ring h-8 rounded-lg px-3 text-xs font-semibold transition-colors"
                :class="wallets.filter === option.key ? 'bg-ink text-white shadow-sm' : 'bg-white border border-slate-200 text-graphite hover:border-slate-300 hover:text-ink'"
                type="button"
                @click="wallets.filter = option.key"
              >
                {{ option.label }}
              </button>
            </div>
            <label class="relative ml-auto block w-52">
              <Search class="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
              <input
                v-model="wallets.query"
                class="focus-ring h-8 w-full rounded-lg border border-slate-200 bg-white pl-8 pr-3 text-xs"
                type="search"
                placeholder="Search wallets…"
              />
            </label>
          </div>

          <div v-if="wallets.isLoading" class="p-6">
            <LoadingSpinner label="Loading wallets" />
          </div>
          <BaseDataTable
            v-else
            :columns="walletColumns"
            :rows="walletRows"
            :searchable="false"
            empty-title="No wallets found"
            empty-message="Wallets will appear here after the backend returns tenant-scoped data."
          >
            <template #cell-id="{ row }">
              <button
                class="focus-ring rounded text-left font-semibold text-signal"
                type="button"
                @click="selectWallet(row)"
              >
                #{{ row.id }}
              </button>
              <p class="mt-1 text-xs text-graphite">{{ websites.nameById(row.website_id as number | null) }}</p>
            </template>
            <template #cell-wallet_type="{ value }">
              <span class="capitalize">{{ value }}</span>
            </template>
            <template #cell-owner_user_id="{ value }">
              User #{{ value ?? "system" }}
            </template>
            <template #cell-available_balance="{ row, value }">
              <span class="font-semibold text-ink">{{ formatAmount(value as string | number, row.currency as string) }}</span>
            </template>
            <template #cell-pending_balance="{ row, value }">
              <span :class="Number(value ?? 0) > 0 ? 'font-semibold text-amber-700' : 'text-graphite'">
                {{ formatAmount(value as string | number, row.currency as string) }}
              </span>
            </template>
            <template #cell-status="{ row, value }">
              <StatusPill
                :label="`${value ?? (row.is_active ? 'active' : 'inactive')}`"
                :tone="statusTone(value as string)"
              />
            </template>
          </BaseDataTable>
        </section>

        <section class="rounded-md border border-slate-200 bg-white">
          <div class="flex min-h-16 items-center justify-between gap-3 border-b border-slate-200 px-4">
            <div class="flex items-center gap-2">
              <Banknote class="h-5 w-5 text-signal" />
              <div>
                <h2 class="text-base font-semibold">Ledger entries</h2>
                <p class="text-sm text-graphite">Credits, debits, references, and balance movements for the selected wallet.</p>
              </div>
            </div>
          </div>
          <BaseDataTable
            :columns="entryColumns"
            :rows="entryRows"
            :loading="wallets.isLoadingDetail"
            empty-title="No ledger entries"
            empty-message="Select a wallet or wait for the backend ledger endpoint to respond."
          >
            <template #cell-created_at="{ value }">{{ formatDate(value as string) }}</template>
            <template #cell-entry_type="{ value, row }">
              <p class="font-semibold text-ink">{{ value }}</p>
              <p class="mt-1 text-xs text-graphite">{{ row.description }}</p>
            </template>
            <template #cell-direction="{ value }">
              <span class="capitalize" :class="value === 'credit' ? 'text-emerald-700' : 'text-rose-700'">
                {{ value }}
              </span>
            </template>
            <template #cell-amount="{ row, value }">
              <span class="font-semibold text-ink">{{ formatAmount(value as string | number, wallets.selectedWallet?.currency) }}</span>
            </template>
            <template #cell-status="{ value }">
              <StatusPill :label="`${value ?? 'posted'}`" :tone="statusTone(value as string)" />
            </template>
          </BaseDataTable>
        </section>
      </div>

      <aside class="space-y-4">
        <section class="rounded-md border border-slate-200 bg-white">
          <div class="border-b border-slate-200 px-4 py-4">
            <div class="flex items-center gap-2">
              <CircleDollarSign class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold">Selected wallet</h2>
            </div>
            <p class="mt-1 text-sm text-graphite">Operational summary and guarded admin actions.</p>
          </div>

          <div v-if="wallets.selectedWallet" class="space-y-4 p-4">
            <div class="grid gap-3 sm:grid-cols-2">
              <div class="rounded-md border border-slate-200 bg-slate-50 p-3">
                <p class="text-xs font-semibold uppercase text-graphite">Wallet</p>
                <p class="mt-2 font-semibold text-ink">#{{ wallets.selectedWallet.id }}</p>
                <p class="mt-1 text-xs capitalize text-graphite">{{ wallets.selectedWallet.wallet_type }}</p>
              </div>
              <div class="rounded-md border border-slate-200 bg-slate-50 p-3">
                <p class="text-xs font-semibold uppercase text-graphite">Available</p>
                <p class="mt-2 font-semibold text-ink">
                  {{ formatAmount(wallets.selectedWallet.available_balance, wallets.selectedWallet.currency) }}
                </p>
                <p class="mt-1 text-xs text-graphite">Pending {{ formatAmount(wallets.selectedWallet.pending_balance, wallets.selectedWallet.currency) }}</p>
              </div>
            </div>

            <div class="grid gap-3 sm:grid-cols-2">
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Amount</span>
                <input
                  v-model.number="wallets.adjustmentForm.amount"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  min="0"
                  step="0.01"
                  type="number"
                >
              </label>
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Reference type</span>
                <input
                  v-model="wallets.adjustmentForm.reference_type"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  type="text"
                >
              </label>
            </div>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Description</span>
              <input
                v-model="wallets.adjustmentForm.description"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="text"
              >
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Reference</span>
              <input
                v-model="wallets.adjustmentForm.reference"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                placeholder="Order, payout, adjustment, or audit reference"
                type="text"
              >
            </label>

            <div class="grid gap-2 sm:grid-cols-2">
              <button
                class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md bg-emerald-700 px-3 text-sm font-semibold text-white disabled:opacity-60"
                type="button"
                :disabled="wallets.isMutating"
                @click="wallets.runWalletAction('fund').catch(() => undefined)"
              >
                <BadgeDollarSign class="h-4 w-4" />
                Credit
              </button>
              <button
                class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md bg-rose-700 px-3 text-sm font-semibold text-white disabled:opacity-60"
                type="button"
                :disabled="wallets.isMutating"
                @click="wallets.runWalletAction('debit').catch(() => undefined)"
              >
                <HandCoins class="h-4 w-4" />
                Debit
              </button>
              <button
                class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
                type="button"
                :disabled="wallets.isMutating"
                @click="wallets.runWalletAction('reconcile').catch(() => undefined)"
              >
                <ShieldCheck class="h-4 w-4" />
                Reconcile
              </button>
              <button
                class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
                type="button"
                :disabled="wallets.isMutating"
                @click="wallets.runWalletAction('repair').catch(() => undefined)"
              >
                <Wrench class="h-4 w-4" />
                Repair
              </button>
            </div>
          </div>

          <div v-else class="p-4">
            <EmptyState
              :icon="WalletCards"
              title="Select a wallet"
              message="Choose a wallet from the registry to inspect and operate on it."
            />
          </div>
        </section>

        <section class="rounded-md border border-slate-200 bg-white">
          <div class="border-b border-slate-200 px-4 py-4">
            <div class="flex items-center gap-2">
              <LockKeyhole class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold">Wallet holds</h2>
            </div>
            <p class="mt-1 text-sm text-graphite">Create, release, or capture funds under review.</p>
          </div>

          <div class="space-y-4 p-4">
            <div class="grid gap-3 sm:grid-cols-2">
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Hold amount</span>
                <input
                  v-model.number="wallets.holdForm.amount"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  min="0"
                  step="0.01"
                  type="number"
                >
              </label>
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Expires</span>
                <input
                  v-model="wallets.holdForm.expires_at"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  type="datetime-local"
                >
              </label>
            </div>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Reason</span>
              <input
                v-model="wallets.holdForm.reason"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="text"
              >
            </label>
            <div class="grid gap-3 sm:grid-cols-2">
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Reference type</span>
                <input
                  v-model="wallets.holdForm.reference_type"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  type="text"
                >
              </label>
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Reference</span>
                <input
                  v-model="wallets.holdForm.reference"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  type="text"
                >
              </label>
            </div>
            <button
              class="focus-ring inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-ink px-3 text-sm font-semibold text-white disabled:opacity-60"
              type="button"
              :disabled="wallets.isMutating || !wallets.selectedWallet"
              @click="wallets.runWalletAction('hold').catch(() => undefined)"
            >
              <LockKeyhole class="h-4 w-4" />
              Create hold
            </button>
          </div>

          <BaseDataTable
            :columns="holdColumns"
            :rows="holdRows"
            :searchable="false"
            :loading="wallets.isLoadingDetail"
            empty-title="No wallet holds"
            empty-message="Holds attached to the selected wallet will appear here."
          >
            <template #cell-id="{ row }">
              <button
                class="focus-ring rounded text-left font-semibold text-signal"
                type="button"
                @click="selectHold(row)"
              >
                #{{ row.id }}
              </button>
            </template>
            <template #cell-amount="{ value }">
              <span class="font-semibold text-ink">{{ formatAmount(value as string | number, wallets.selectedWallet?.currency) }}</span>
            </template>
            <template #cell-status="{ value }">
              <StatusPill :label="`${value ?? 'active'}`" :tone="statusTone(value as string)" />
            </template>
            <template #cell-expires_at="{ value }">{{ formatDate(value as string) }}</template>
          </BaseDataTable>

          <div class="grid gap-2 border-t border-slate-200 p-4 sm:grid-cols-2">
            <button
              class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
              type="button"
              :disabled="wallets.isMutating || !wallets.selectedHold"
              @click="wallets.releaseSelectedHold().catch(() => undefined)"
            >
              Release hold
            </button>
            <button
              class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-rose-200 bg-white px-3 text-sm font-semibold text-rose-700 disabled:opacity-60"
              type="button"
              :disabled="wallets.isMutating || !wallets.selectedHold"
              @click="wallets.captureSelectedHold().catch(() => undefined)"
            >
              Capture hold
            </button>
          </div>
        </section>
      </aside>
    </section>
  </div>
</template>

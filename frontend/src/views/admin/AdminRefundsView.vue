<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  AlertCircle,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  Clock3,
  ExternalLink,
  FileText,
  Loader2,
  Receipt,
  RefreshCw,
  RotateCcw,
  Search,
  X,
  XCircle,
} from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { adminPaymentsApi } from "@/api/adminPayments";
import type { RefundLogRecord, RefundReceiptRecord, RefundRecord } from "@/api/adminPayments";

// ── Tabs ─────────────────────────────────────────────────────────────────────

type Tab = "queue" | "logs" | "receipts";
const activeTab = ref<Tab>("queue");

// ── Refund Queue ─────────────────────────────────────────────────────────────

const refunds = ref<RefundRecord[]>([]);
const queueLoading = ref(false);
const queueFilter = ref<"all" | "pending" | "processed" | "rejected" | "cancelled">("all");
const queueSearch = ref("");

const expandedId = ref<number | null>(null);

const actioningId = ref<number | null>(null);
const cancelDialogId = ref<number | null>(null);
const cancelReason = ref("");
const actionError = ref<Record<number, string>>({});

async function loadQueue() {
  queueLoading.value = true;
  try {
    const params: Record<string, unknown> = {};
    if (queueFilter.value !== "all") params.status = queueFilter.value;
    const { data } = await adminPaymentsApi.refunds(params);
    refunds.value = Array.isArray(data) ? data : (data as { results: RefundRecord[] }).results ?? [];
  } catch { refunds.value = []; }
  finally { queueLoading.value = false; }
}

const filteredRefunds = computed(() => {
  if (!queueSearch.value.trim()) return refunds.value;
  const q = queueSearch.value.toLowerCase();
  return refunds.value.filter(
    (r) =>
      String(r.id).includes(q) ||
      String(r.order ?? "").includes(q) ||
      String(r.client ?? "").includes(q) ||
      (r.reason ?? "").toLowerCase().includes(q),
  );
});

async function process(r: RefundRecord) {
  actioningId.value = r.id;
  delete actionError.value[r.id];
  try {
    const { data } = await adminPaymentsApi.processRefund(r.id, "Processed by admin");
    const idx = refunds.value.findIndex((x) => x.id === r.id);
    if (idx !== -1) refunds.value[idx] = data;
  } catch {
    actionError.value[r.id] = "Failed to process refund.";
  } finally {
    actioningId.value = null;
  }
}

async function submitCancel() {
  if (!cancelDialogId.value) return;
  const id = cancelDialogId.value;
  actioningId.value = id;
  delete actionError.value[id];
  try {
    await adminPaymentsApi.cancelRefund(id, cancelReason.value || "Cancelled by admin");
    await loadQueue();
    cancelDialogId.value = null;
    cancelReason.value = "";
  } catch {
    actionError.value[id] = "Failed to cancel refund.";
  } finally {
    actioningId.value = null;
  }
}

async function retry(r: RefundRecord) {
  actioningId.value = r.id;
  delete actionError.value[r.id];
  try {
    const { data } = await adminPaymentsApi.retryRefund(r.id);
    const idx = refunds.value.findIndex((x) => x.id === r.id);
    if (idx !== -1) refunds.value[idx] = data;
  } catch {
    actionError.value[r.id] = "Failed to retry refund.";
  } finally {
    actioningId.value = null;
  }
}

// ── Summary metrics ───────────────────────────────────────────────────────────

const pendingCount = computed(() => refunds.value.filter((r) => r.status === "pending").length);
const processedCount = computed(() => refunds.value.filter((r) => r.status === "processed").length);
const rejectedCount = computed(() => refunds.value.filter((r) => r.status === "rejected").length);
const totalPending = computed(() => {
  return refunds.value
    .filter((r) => r.status === "pending")
    .reduce((sum, r) => sum + Number(r.total_amount ?? 0), 0)
    .toFixed(2);
});

// ── Refund Logs ───────────────────────────────────────────────────────────────

const logs = ref<RefundLogRecord[]>([]);
const logsLoading = ref(false);
const expandedLog = ref<number | null>(null);

async function loadLogs() {
  logsLoading.value = true;
  try {
    const { data } = await adminPaymentsApi.refundLogs();
    logs.value = Array.isArray(data) ? data : (data as { results: RefundLogRecord[] }).results ?? [];
  } catch { logs.value = []; }
  finally { logsLoading.value = false; }
}

// ── Receipts ──────────────────────────────────────────────────────────────────

const receipts = ref<RefundReceiptRecord[]>([]);
const receiptsLoading = ref(false);

async function loadReceipts() {
  receiptsLoading.value = true;
  try {
    const { data } = await adminPaymentsApi.refundReceipts();
    receipts.value = Array.isArray(data) ? data : (data as { results: RefundReceiptRecord[] }).results ?? [];
  } catch { receipts.value = []; }
  finally { receiptsLoading.value = false; }
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function statusTone(status: string): "success" | "warning" | "danger" | "neutral" {
  if (["processed", "completed"].includes(status)) return "success";
  if (["pending"].includes(status)) return "warning";
  if (["rejected", "cancelled", "failed"].includes(status)) return "danger";
  return "neutral";
}

function money(v: string | number | null | undefined): string {
  const n = Number(v ?? 0);
  return Number.isNaN(n) ? String(v ?? "—") : `$${n.toFixed(2)}`;
}

function fmt(v: string | null | undefined): string {
  if (!v) return "—";
  return new Date(v).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric", hour: "2-digit", minute: "2-digit" });
}

function logActionTone(action: string | null): string {
  if (!action) return "text-neutral-500";
  if (action.includes("cancel") || action.includes("reject")) return "text-berry-600";
  if (action.includes("process") || action.includes("complete")) return "text-signal-600";
  if (action.includes("retry")) return "text-amber-600";
  return "text-neutral-600";
}

// ── Init ─────────────────────────────────────────────────────────────────────

onMounted(() => {
  loadQueue();
  loadLogs();
  loadReceipts();
});
</script>

<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold text-neutral-900">Refund Management</h1>
        <p class="text-sm text-neutral-500 mt-0.5">Process, cancel, and audit client refund requests</p>
      </div>
      <button
        class="inline-flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg border border-neutral-200 hover:bg-neutral-50 transition-colors"
        @click="loadQueue(); loadLogs(); loadReceipts()"
      >
        <RefreshCw class="size-4" />
        Refresh
      </button>
    </div>

    <!-- Summary metrics -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div
        v-for="metric in [
          { label: 'Pending', value: pendingCount, sub: `$${totalPending} held`, tone: 'amber' },
          { label: 'Processed', value: processedCount, sub: 'this load', tone: 'signal' },
          { label: 'Rejected', value: rejectedCount, sub: 'needs retry', tone: 'berry' },
          { label: 'Total loaded', value: refunds.length, sub: 'all statuses', tone: 'neutral' },
        ]"
        :key="metric.label"
        class="rounded-xl border p-4"
        :class="{
          'border-amber-200 bg-amber-50': metric.tone === 'amber',
          'border-signal-200 bg-signal-50': metric.tone === 'signal',
          'border-berry-200 bg-berry-50': metric.tone === 'berry',
          'border-neutral-200 bg-white': metric.tone === 'neutral',
        }"
      >
        <p class="text-2xl font-bold"
          :class="{
            'text-amber-700': metric.tone === 'amber',
            'text-signal-700': metric.tone === 'signal',
            'text-berry-700': metric.tone === 'berry',
            'text-neutral-900': metric.tone === 'neutral',
          }"
        >{{ metric.value }}</p>
        <p class="text-xs font-medium mt-0.5 text-neutral-600">{{ metric.label }}</p>
        <p class="text-xs text-neutral-400">{{ metric.sub }}</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex border-b border-neutral-200 gap-6">
      <button
        v-for="tab in [
          { key: 'queue', label: 'Refund Queue', icon: RotateCcw },
          { key: 'logs', label: 'Audit Log', icon: FileText },
          { key: 'receipts', label: 'Receipts', icon: Receipt },
        ]"
        :key="tab.key"
        class="flex items-center gap-1.5 pb-3 text-sm font-medium border-b-2 transition-colors -mb-px"
        :class="activeTab === tab.key
          ? 'border-neutral-900 text-neutral-900'
          : 'border-transparent text-neutral-500 hover:text-neutral-700'"
        @click="activeTab = tab.key as Tab"
      >
        <component :is="tab.icon" class="size-4" />
        {{ tab.label }}
      </button>
    </div>

    <!-- ── QUEUE ──────────────────────────────────────────────────────────────── -->
    <template v-if="activeTab === 'queue'">
      <!-- Filters -->
      <div class="flex flex-wrap items-center gap-3">
        <!-- Status pills -->
        <div class="flex rounded-lg border border-neutral-200 overflow-hidden text-xs">
          <button
            v-for="f in (['all', 'pending', 'processed', 'rejected', 'cancelled'] as const)"
            :key="f"
            class="px-3 py-1.5 capitalize transition-colors border-r border-neutral-200 last:border-r-0"
            :class="queueFilter === f ? 'bg-neutral-900 text-white' : 'hover:bg-neutral-50 text-neutral-600'"
            @click="queueFilter = f; loadQueue()"
          >
            {{ f }}
          </button>
        </div>
        <!-- Search -->
        <div class="relative">
          <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 size-3.5 text-neutral-400" />
          <input
            v-model="queueSearch"
            type="text"
            placeholder="Search ID, order, client…"
            class="pl-8 pr-3 py-1.5 text-sm rounded-lg border border-neutral-200 focus:outline-none focus:ring-2 focus:ring-neutral-900 w-52"
          />
        </div>
      </div>

      <!-- Cancel dialog -->
      <div
        v-if="cancelDialogId !== null"
        class="rounded-xl border border-berry-200 bg-berry-50 p-4 space-y-3"
      >
        <div class="flex items-center justify-between">
          <p class="text-sm font-semibold text-berry-800">Cancel refund #{{ cancelDialogId }}</p>
          <button class="text-berry-400 hover:text-berry-600" @click="cancelDialogId = null; cancelReason = ''">
            <X class="size-4" />
          </button>
        </div>
        <input
          v-model="cancelReason"
          type="text"
          placeholder="Reason for cancellation (optional)"
          class="w-full text-sm px-3 py-2 rounded-lg border border-berry-200 bg-white focus:outline-none focus:ring-2 focus:ring-berry-400"
        />
        <div class="flex gap-2">
          <button
            class="text-sm px-3 py-1.5 rounded-lg bg-berry-600 text-white hover:bg-berry-700 disabled:opacity-50 transition-colors"
            :disabled="actioningId === cancelDialogId"
            @click="submitCancel"
          >
            <Loader2 v-if="actioningId === cancelDialogId" class="size-3.5 animate-spin inline mr-1" />
            Confirm cancel
          </button>
          <button
            class="text-sm px-3 py-1.5 rounded-lg border border-neutral-200 hover:bg-neutral-50 transition-colors"
            @click="cancelDialogId = null; cancelReason = ''"
          >
            Dismiss
          </button>
        </div>
      </div>

      <!-- Table -->
      <div class="bg-white rounded-lg border border-neutral-200 overflow-hidden">
        <div v-if="queueLoading" class="p-8 flex justify-center">
          <Loader2 class="size-7 text-neutral-300 animate-spin" />
        </div>
        <div v-else-if="filteredRefunds.length === 0" class="p-8 text-center text-sm text-neutral-400">
          No refunds match the current filter.
        </div>
        <div v-else class="divide-y divide-neutral-100">
          <div v-for="r in filteredRefunds" :key="r.id">
            <!-- Row -->
            <div
              class="flex items-center gap-4 px-4 py-3 hover:bg-neutral-50 transition-colors cursor-pointer"
              @click="expandedId = expandedId === r.id ? null : r.id"
            >
              <!-- Expand icon -->
              <component
                :is="expandedId === r.id ? ChevronDown : ChevronRight"
                class="size-4 text-neutral-400 shrink-0"
              />
              <!-- ID -->
              <span class="font-mono text-xs text-neutral-400 w-12 shrink-0">#{{ r.id }}</span>
              <!-- Status -->
              <StatusPill :label="r.status" :tone="statusTone(r.status)" />
              <!-- Amounts -->
              <div class="flex-1 min-w-0 grid grid-cols-3 gap-4 text-sm">
                <div>
                  <p class="text-xs text-neutral-400">Total</p>
                  <p class="font-semibold text-neutral-900">{{ money(r.total_amount) }}</p>
                </div>
                <div>
                  <p class="text-xs text-neutral-400">Wallet</p>
                  <p class="text-neutral-700">{{ money(r.wallet_amount) }}</p>
                </div>
                <div>
                  <p class="text-xs text-neutral-400">External</p>
                  <p class="text-neutral-700">{{ money(r.external_amount) }}</p>
                </div>
              </div>
              <!-- Order + created -->
              <div class="text-right text-xs text-neutral-500 shrink-0 space-y-0.5">
                <div v-if="r.order" class="flex items-center gap-1 justify-end">
                  <ExternalLink class="size-3" />
                  Order #{{ r.order }}
                </div>
                <div class="flex items-center gap-1 justify-end">
                  <Clock3 class="size-3" />
                  {{ fmt(r.created_at) }}
                </div>
              </div>
              <!-- Actions -->
              <div class="flex items-center gap-1.5 shrink-0" @click.stop>
                <button
                  v-if="r.status === 'pending'"
                  class="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-lg bg-signal-600 text-white hover:bg-signal-700 disabled:opacity-50 transition-colors"
                  :disabled="actioningId === r.id"
                  @click="process(r)"
                >
                  <Loader2 v-if="actioningId === r.id" class="size-3 animate-spin" />
                  <CheckCircle2 v-else class="size-3" />
                  Process
                </button>
                <button
                  v-if="r.status === 'pending'"
                  class="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-lg border border-berry-200 text-berry-700 hover:bg-berry-50 disabled:opacity-50 transition-colors"
                  :disabled="actioningId === r.id"
                  @click="cancelDialogId = r.id; cancelReason = ''"
                >
                  <XCircle class="size-3" />
                  Cancel
                </button>
                <button
                  v-if="r.status === 'rejected'"
                  class="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-lg border border-amber-200 text-amber-700 hover:bg-amber-50 disabled:opacity-50 transition-colors"
                  :disabled="actioningId === r.id"
                  @click="retry(r)"
                >
                  <Loader2 v-if="actioningId === r.id" class="size-3 animate-spin" />
                  <RotateCcw v-else class="size-3" />
                  Retry
                </button>
              </div>
            </div>

            <!-- Expanded details -->
            <div v-if="expandedId === r.id" class="px-14 pb-4 bg-neutral-50 border-t border-neutral-100">
              <p v-if="actionError[r.id]" class="text-xs text-berry-600 mb-2 flex items-center gap-1">
                <AlertCircle class="size-3.5" />{{ actionError[r.id] }}
              </p>
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
                <div>
                  <p class="text-neutral-400 font-medium uppercase tracking-wide">Type</p>
                  <p class="text-neutral-800 mt-0.5">{{ r.type ?? "—" }}</p>
                </div>
                <div>
                  <p class="text-neutral-400 font-medium uppercase tracking-wide">Method</p>
                  <p class="text-neutral-800 mt-0.5">{{ r.refund_method ?? "—" }}</p>
                </div>
                <div>
                  <p class="text-neutral-400 font-medium uppercase tracking-wide">Client</p>
                  <p class="text-neutral-800 mt-0.5">{{ r.client ?? "—" }}</p>
                </div>
                <div>
                  <p class="text-neutral-400 font-medium uppercase tracking-wide">Processed at</p>
                  <p class="text-neutral-800 mt-0.5">{{ fmt(r.processed_at) }}</p>
                </div>
                <div class="col-span-2">
                  <p class="text-neutral-400 font-medium uppercase tracking-wide">Reason</p>
                  <p class="text-neutral-800 mt-0.5">{{ r.reason ?? "—" }}</p>
                </div>
                <div v-if="r.error_message" class="col-span-2">
                  <p class="text-neutral-400 font-medium uppercase tracking-wide">Error</p>
                  <p class="text-berry-700 mt-0.5">{{ r.error_message }}</p>
                </div>
                <div v-if="r.refundable_amount" class="col-span-2">
                  <p class="text-neutral-400 font-medium uppercase tracking-wide">Refundable balance on payment</p>
                  <p class="text-neutral-800 mt-0.5">{{ money(r.refundable_amount) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ── AUDIT LOG ──────────────────────────────────────────────────────────── -->
    <template v-if="activeTab === 'logs'">
      <div class="bg-white rounded-lg border border-neutral-200 overflow-hidden">
        <div v-if="logsLoading" class="p-8 flex justify-center">
          <Loader2 class="size-7 text-neutral-300 animate-spin" />
        </div>
        <div v-else-if="logs.length === 0" class="p-8 text-center text-sm text-neutral-400">
          No refund audit logs found.
        </div>
        <div v-else class="divide-y divide-neutral-100">
          <div v-for="log in logs" :key="log.id">
            <div
              class="flex items-start gap-4 px-4 py-3 hover:bg-neutral-50 cursor-pointer transition-colors"
              @click="expandedLog = expandedLog === log.id ? null : log.id"
            >
              <component
                :is="expandedLog === log.id ? ChevronDown : ChevronRight"
                class="size-4 text-neutral-400 shrink-0 mt-0.5"
              />
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="font-mono text-xs text-neutral-400">#{{ log.id }}</span>
                  <span
                    class="text-xs font-medium capitalize"
                    :class="logActionTone(log.action)"
                  >{{ log.action ?? "unknown action" }}</span>
                  <StatusPill :label="log.status" :tone="statusTone(log.status)" />
                  <span class="text-xs text-neutral-500">{{ money(log.amount) }}</span>
                </div>
                <p class="text-xs text-neutral-400 mt-0.5">{{ fmt(log.created_at) }}</p>
              </div>
              <div class="text-xs text-neutral-400 shrink-0 text-right">
                <div v-if="log.refund">Refund #{{ log.refund }}</div>
                <div v-if="log.order">Order #{{ log.order }}</div>
              </div>
            </div>
            <!-- Expanded metadata -->
            <div v-if="expandedLog === log.id && log.metadata" class="px-12 pb-3 bg-neutral-50 border-t border-neutral-100">
              <pre class="text-xs text-neutral-600 overflow-x-auto whitespace-pre-wrap">{{ JSON.stringify(log.metadata, null, 2) }}</pre>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- ── RECEIPTS ────────────────────────────────────────────────────────────── -->
    <template v-if="activeTab === 'receipts'">
      <div v-if="receiptsLoading" class="p-8 flex justify-center">
        <Loader2 class="size-7 text-neutral-300 animate-spin" />
      </div>
      <div v-else-if="receipts.length === 0" class="p-8 text-center text-sm text-neutral-400">
        No refund receipts found.
      </div>
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div
          v-for="r in receipts"
          :key="r.id"
          class="bg-white rounded-lg border border-neutral-200 p-4 space-y-3"
        >
          <div class="flex items-start justify-between gap-2">
            <div>
              <p class="text-xs text-neutral-400 font-medium uppercase tracking-wide">Reference</p>
              <code class="text-sm font-mono font-semibold text-neutral-900 mt-0.5 block">{{ r.reference_code }}</code>
            </div>
            <Receipt class="size-5 text-neutral-300 shrink-0" />
          </div>
          <div class="grid grid-cols-2 gap-3 text-xs">
            <div>
              <p class="text-neutral-400">Amount</p>
              <p class="font-semibold text-neutral-900 mt-0.5">{{ money(r.amount) }}</p>
            </div>
            <div>
              <p class="text-neutral-400">Client</p>
              <p class="text-neutral-700 mt-0.5">{{ r.client ?? "—" }}</p>
            </div>
            <div>
              <p class="text-neutral-400">Refund</p>
              <p class="text-neutral-700 mt-0.5">#{{ r.refund ?? "—" }}</p>
            </div>
            <div>
              <p class="text-neutral-400">Processed by</p>
              <p class="text-neutral-700 mt-0.5">{{ r.processed_by ?? "—" }}</p>
            </div>
          </div>
          <div v-if="r.reason" class="text-xs text-neutral-500 border-t border-neutral-100 pt-2">
            {{ r.reason }}
          </div>
          <div class="text-xs text-neutral-400">
            <Clock3 class="size-3 inline mr-1" />
            {{ fmt(r.generated_at) }}
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

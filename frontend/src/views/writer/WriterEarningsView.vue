<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import {
  AlertTriangle,
  Banknote,
  CalendarClock,
  CheckCircle2,
  Clock3,
  CreditCard,
  Gift,
  Loader2,
  RefreshCw,
  Send,
  Star,
  TrendingDown,
  TrendingUp,
  X,
} from "@lucide/vue";
import { writerApi, type AdvanceRecord } from "@/api/writer";
import type { WriterEvent } from "@/types/writer";
import { finesApi, type FineRecord } from "@/api/fines";
import { tipsApi, type TipRecord } from "@/api/tips";
import MetricTile from "@/components/ui/MetricTile.vue";
import Pagination from "@/components/ui/Pagination.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useWriterWorkspaceStore } from "@/stores/writerWorkspace";

const workspace = useWriterWorkspaceStore();

// — Event display helpers ————————————————————————————————
const EVENT_TYPE_LABELS: Record<string, string> = {
  ORDER_COMPLETION:    "Order completion",
  REVISION_COMPLETION: "Revision completion",
  BONUS:               "Bonus",
  MILESTONE_BONUS:     "Milestone bonus",
  PERFORMANCE_BONUS:   "Performance bonus",
  RETENTION_BONUS:     "Retention bonus",
  TIP:                 "Client tip",
  FINE:                "Fine",
  REVERSAL:            "Reversal",
  ADVANCE:             "Advance",
  ADVANCE_RECOVERY:    "Advance recovery",
  ADJUSTMENT:          "Manual adjustment",
  DEDUCTION:           "Deduction",
};

function eventLabel(e: WriterEvent): string {
  return e.source_label ?? (e.event_type ? (EVENT_TYPE_LABELS[e.event_type] ?? e.event_type.replace(/_/g, " ")) : "Compensation event");
}

type EventFilter = "all" | "earnings" | "deductions";
const eventFilter = ref<EventFilter>("all");

const filteredEvents = computed(() => {
  if (eventFilter.value === "earnings")   return workspace.events.filter(e => e.is_positive !== false);
  if (eventFilter.value === "deductions") return workspace.events.filter(e => e.is_positive === false);
  return workspace.events;
});

// — Bonuses ——————————————————————————————————————————————
const bonuses = ref<WriterEvent[]>([]);
const bonusesLoading = ref(false);

async function fetchBonuses() {
  bonusesLoading.value = true;
  try {
    const { data } = await writerApi.bonuses({ limit: 10 });
    bonuses.value = Array.isArray(data) ? data : [];
  } catch {
    // non-critical
  } finally {
    bonusesLoading.value = false;
  }
}

// — Pending cycle change request ————————————————————————
interface PendingCycleChange { id: number; requested_cycle: string; status: string; reason: string; created_at: string }
const pendingCycleChange = ref<PendingCycleChange | null>(null);

async function fetchPendingCycleChange() {
  try {
    const { data } = await writerApi.pendingCycleChange();
    pendingCycleChange.value = data;
  } catch {
    pendingCycleChange.value = null; // 404 = no pending request
  }
}

// — Payout cycle ————————————————————————————————————————
interface PayoutHistoryRecord {
  id: number;
  total_amount: string;
  status: string;
  window_label: string;
  paid_at: string | null;
}

interface PayoutPreference {
  id: number;
  cycle_type: string;
  locked: boolean;
}

const payoutHistory = ref<PayoutHistoryRecord[]>([]);
const payoutHistoryLoading = ref(false);
const preference = ref<PayoutPreference | null>(null);
const preferenceLoading = ref(false);
const showCycleForm = ref(false);
const cycleFormMode = ref<"set" | "request">("set");
const selectedCycle = ref("BIWEEKLY");
const cycleReason = ref("");
const cycleSubmitting = ref(false);
const cycleError = ref("");
const cycleSuccess = ref("");

const cycleOptions = [
  { value: "BIWEEKLY", label: "Bi-weekly" },
  { value: "MONTHLY", label: "Monthly" },
];

async function fetchPayoutHistory() {
  payoutHistoryLoading.value = true;
  try {
    const { data } = await writerApi.payoutHistory();
    payoutHistory.value = Array.isArray(data) ? data : [];
  } catch {
    // non-critical
  } finally {
    payoutHistoryLoading.value = false;
  }
}

async function fetchPreference() {
  preferenceLoading.value = true;
  try {
    const { data } = await writerApi.payoutPreference();
    preference.value = data;
  } catch {
    // 404 = no preference set yet
    preference.value = null;
  } finally {
    preferenceLoading.value = false;
  }
}

function openCycleForm() {
  cycleError.value = "";
  cycleSuccess.value = "";
  cycleReason.value = "";
  selectedCycle.value = preference.value?.cycle_type ?? "BIWEEKLY";
  cycleFormMode.value = preference.value?.locked ? "request" : "set";
  showCycleForm.value = true;
}

async function submitCycleChange() {
  cycleError.value = "";
  cycleSuccess.value = "";
  cycleSubmitting.value = true;
  try {
    if (cycleFormMode.value === "set") {
      const { data } = await writerApi.setPayoutPreference(selectedCycle.value);
      preference.value = data;
      cycleSuccess.value = `Payment cycle set to ${data.cycle_type.toLowerCase()}.`;
    } else {
      if (!cycleReason.value.trim()) {
        cycleError.value = "Please provide a reason for the cycle change request.";
        return;
      }
      await writerApi.requestCycleChange(selectedCycle.value, cycleReason.value.trim());
      cycleSuccess.value = "Cycle change request submitted — an admin will review it.";
    }
    showCycleForm.value = false;
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    cycleError.value = detail ?? "Could not update cycle. Try again.";
  } finally {
    cycleSubmitting.value = false;
  }
}

function cycleTone(cycle: string | undefined) {
  if (cycle === "BIWEEKLY") return "bg-sky-100 text-sky-700";
  if (cycle === "MONTHLY") return "bg-violet-100 text-violet-700";
  return "bg-slate-100 text-graphite";
}

function cycleLabel(cycle: string | undefined) {
  if (cycle === "BIWEEKLY") return "Bi-weekly";
  if (cycle === "MONTHLY") return "Monthly";
  return cycle ?? "Not set";
}

// — end payout cycle ————————————————————————————————————

// — Advance payments ————————————————————————————————————
const advances = ref<AdvanceRecord[]>([]);
const advancesLoading = ref(false);
const showAdvanceForm = ref(false);
const advanceAmount = ref("");
const advanceReason = ref("");
const advanceSubmitting = ref(false);
const advanceError = ref("");
const advanceSuccess = ref("");

async function fetchAdvances() {
  advancesLoading.value = true;
  try {
    const { data } = await writerApi.advances();
    advances.value = Array.isArray(data) ? data : [];
  } catch {
    // non-critical
  } finally {
    advancesLoading.value = false;
  }
}

async function submitAdvance() {
  advanceError.value = "";
  advanceSuccess.value = "";
  const amt = Number(advanceAmount.value);
  if (!amt || amt <= 0) {
    advanceError.value = "Enter a valid amount.";
    return;
  }
  if (!advanceReason.value.trim()) {
    advanceError.value = "Please provide a reason for the advance.";
    return;
  }
  advanceSubmitting.value = true;
  try {
    const { data } = await writerApi.requestAdvance(advanceAmount.value, advanceReason.value.trim());
    advances.value = [data, ...advances.value];
    advanceSuccess.value = "Advance request submitted — an admin will review it shortly.";
    advanceAmount.value = "";
    advanceReason.value = "";
    showAdvanceForm.value = false;
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    advanceError.value = detail ?? "Advance request failed. Check the amount and try again.";
  } finally {
    advanceSubmitting.value = false;
  }
}

function advanceStatusTone(status: string): "success" | "warning" | "danger" | "neutral" {
  if (status === "APPROVED" || status === "RECOVERED") return "success";
  if (status === "PENDING" || status === "PARTIALLY_RECOVERED") return "warning";
  if (status === "REJECTED") return "danger";
  return "neutral";
}
// — end advance payments ————————————————————————————————

const showPayoutForm = ref(false);
const payoutForm = reactive({ amount: "", reason: "" });
const payoutError = ref("");

const tips = ref<TipRecord[]>([]);
const tipsLoading = ref(false);

const fines = ref<FineRecord[]>([]);
const finesLoading = ref(false);
const disputingFineId = ref<number | null>(null);
const disputeReason = ref("");
const disputeError = ref("");
const disputeSubmitting = ref(false);

async function fetchFines() {
  finesLoading.value = true;
  try {
    const { data } = await finesApi.list({ page_size: 20 });
    fines.value = Array.isArray(data) ? data : (data as { results: FineRecord[] }).results ?? [];
  } catch {
    // Non-critical
  } finally {
    finesLoading.value = false;
  }
}

function openDisputeForm(fineId: number) {
  disputingFineId.value = fineId;
  disputeReason.value = "";
  disputeError.value = "";
}

function closeDisputeForm() {
  disputingFineId.value = null;
  disputeReason.value = "";
  disputeError.value = "";
}

async function submitDispute(fineId: number) {
  disputeError.value = "";
  if (!disputeReason.value.trim()) {
    disputeError.value = "Please explain why you are disputing this fine.";
    return;
  }
  disputeSubmitting.value = true;
  try {
    const { data } = await finesApi.dispute(fineId, disputeReason.value.trim());
    const idx = fines.value.findIndex((f) => f.id === fineId);
    if (idx !== -1) fines.value[idx] = data;
    closeDisputeForm();
  } catch {
    disputeError.value = "Dispute submission failed. Try again shortly.";
  } finally {
    disputeSubmitting.value = false;
  }
}

function fineStatusTone(status: string): "success" | "warning" | "danger" | "neutral" {
  if (status === "waived") return "success";
  if (status === "disputed" || status === "escalated" || status === "appealed") return "warning";
  if (status === "issued") return "danger";
  return "neutral";
}

async function fetchReceivedTips() {
  tipsLoading.value = true;
  try {
    const { data } = await tipsApi.received({ page_size: 10 });
    tips.value = Array.isArray(data) ? data : (data as { results: TipRecord[] }).results ?? [];
  } catch {
    // Non-critical — don't surface error
  } finally {
    tipsLoading.value = false;
  }
}

function money(value: string | number | undefined | null): string {
  if (value === undefined || value === null || value === "") return "$0.00";
  const n = Number(value);
  if (Number.isNaN(n)) return String(value);
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(n);
}

function formatDate(value: string | undefined | null): string {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

function payoutStatusTone(status: string): "success" | "warning" | "danger" | "neutral" {
  if (status === "completed" || status === "approved") return "success";
  if (status === "pending" || status === "processing") return "warning";
  if (status === "rejected" || status === "failed") return "danger";
  return "neutral";
}

async function submitPayout() {
  payoutError.value = "";
  const amount = Number(payoutForm.amount);
  if (!amount || amount <= 0) {
    payoutError.value = "Enter a valid amount.";
    return;
  }
  try {
    await workspace.requestPayout({ amount: payoutForm.amount, reason: payoutForm.reason || undefined });
    payoutForm.amount = "";
    payoutForm.reason = "";
    showPayoutForm.value = false;
  } catch {
    payoutError.value = "Payout request failed. Check the amount and try again.";
  }
}

type SecondaryTab = "advances" | "bonuses" | "fines" | "tips";
const secondaryTab = ref<SecondaryTab>("advances");

onMounted(async () => {
  if (!workspace.balance) await workspace.hydrate();
  await Promise.all([
    workspace.fetchEvents(1),
    workspace.fetchPayoutRequests(),
    fetchReceivedTips(),
    fetchFines(),
    fetchPayoutHistory(),
    fetchPreference(),
    fetchAdvances(),
    fetchBonuses(),
    fetchPendingCycleChange(),
  ]);
});
</script>

<template>
  <div class="space-y-6">

    <!-- ── Page header ──────────────────────────────────────────────────── -->
    <div class="flex items-center justify-between gap-4">
      <div>
        <p class="text-xs font-semibold uppercase tracking-widest text-signal">Writer</p>
        <h1 class="mt-1 text-2xl font-bold text-ink">Earnings</h1>
      </div>
      <button
        class="focus-ring inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-graphite hover:text-ink disabled:opacity-50"
        type="button"
        :disabled="workspace.isLoading"
        @click="workspace.fetchEvents(workspace.eventsPagination.page).catch(() => undefined)"
      >
        <Loader2 v-if="workspace.isLoading" class="h-3.5 w-3.5 animate-spin" />
        <RefreshCw v-else class="h-3.5 w-3.5" />
        Refresh
      </button>
    </div>

    <!-- ── Alerts ────────────────────────────────────────────────────────── -->
    <div v-if="workspace.error" class="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">{{ workspace.error }}</div>
    <div v-if="workspace.notice" class="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">{{ workspace.notice }}</div>

    <!-- ── Balance hero ──────────────────────────────────────────────────── -->
    <section class="relative overflow-hidden rounded-2xl bg-slate-900 px-6 py-6 text-white">
      <!-- subtle grid -->
      <div class="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:32px_32px]" />
      <div class="relative">
        <div class="grid gap-6 sm:grid-cols-3">
          <!-- Pending -->
          <div>
            <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Pending balance</p>
            <p class="mt-2 text-3xl font-extrabold tabular-nums tracking-tight">
              <span v-if="workspace.isLoading" class="inline-block h-8 w-24 animate-pulse rounded bg-white/10" />
              <span v-else>{{ money(workspace.balance?.pending) }}</span>
            </p>
            <p class="mt-1 text-xs text-slate-500">Maturing — not yet disbursed</p>
          </div>
          <!-- Current window -->
          <div>
            <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">This window</p>
            <p class="mt-2 text-3xl font-extrabold tabular-nums tracking-tight">
              <span v-if="workspace.isLoading" class="inline-block h-8 w-20 animate-pulse rounded bg-white/10" />
              <span v-else>{{ money(workspace.currentWindow?.net) }}</span>
            </p>
            <p class="mt-1 text-xs text-slate-500">{{ workspace.currentWindow?.count ?? 0 }} events · {{ cycleLabel(preference?.cycle_type) }} cycle</p>
          </div>
          <!-- Lifetime -->
          <div class="sm:border-l sm:border-white/10 sm:pl-6">
            <p class="text-xs font-semibold uppercase tracking-widest text-slate-400">Lifetime earned</p>
            <p class="mt-2 text-3xl font-extrabold tabular-nums tracking-tight text-emerald-400">
              <span v-if="workspace.isLoading" class="inline-block h-8 w-24 animate-pulse rounded bg-white/10" />
              <span v-else>{{ money(workspace.balance?.lifetime) }}</span>
            </p>
            <p class="mt-1 text-xs text-slate-500">All-time compensation total</p>
          </div>
        </div>

        <!-- Payout CTA row -->
        <div class="mt-6 flex flex-wrap items-center gap-3 border-t border-white/10 pt-5">
          <button
            class="focus-ring inline-flex items-center gap-2 rounded-lg bg-white px-5 py-2.5 text-sm font-bold text-slate-900 hover:bg-slate-100 transition-colors disabled:opacity-50"
            type="button"
            :disabled="workspace.isMutating"
            @click="showPayoutForm = true"
          >
            <Send class="h-4 w-4" />
            Request payout
          </button>
          <div v-if="workspace.payoutRequests.length" class="flex flex-wrap gap-2">
            <span
              v-for="req in workspace.payoutRequests.slice(0, 2)"
              :key="req.id"
              class="inline-flex items-center gap-1.5 rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs font-semibold text-slate-200"
            >
              {{ money(req.amount) }}
              <span class="opacity-60">·</span>
              <span class="capitalize">{{ (req.workflow_status ?? req.status).toLowerCase() }}</span>
            </span>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Payout request modal ──────────────────────────────────────────── -->
    <Teleport to="body">
      <div
        v-if="showPayoutForm"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4"
        @click.self="showPayoutForm = false; payoutError = ''"
      >
        <div class="w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl space-y-5">
          <div class="flex items-center justify-between">
            <h2 class="text-base font-bold text-ink">Request payout</h2>
            <button class="text-graphite hover:text-ink" type="button" @click="showPayoutForm = false; payoutError = ''">
              <X class="h-5 w-5" />
            </button>
          </div>
          <label class="block">
            <span class="text-sm font-medium text-graphite">Amount</span>
            <input
              v-model="payoutForm.amount"
              class="focus-ring mt-1.5 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm"
              type="number" min="1" step="0.01" placeholder="0.00" autofocus
            />
          </label>
          <label class="block">
            <span class="text-sm font-medium text-graphite">Reason <span class="text-slate-400">(optional)</span></span>
            <input
              v-model="payoutForm.reason"
              class="focus-ring mt-1.5 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm"
              type="text" placeholder="e.g. Monthly payout"
            />
          </label>
          <p v-if="payoutError" class="text-xs text-berry">{{ payoutError }}</p>
          <div class="flex gap-2 pt-1">
            <button
              class="focus-ring inline-flex flex-1 items-center justify-center gap-2 rounded-lg bg-ink py-2.5 text-sm font-bold text-white disabled:opacity-60"
              type="button"
              :disabled="workspace.isMutating"
              @click="submitPayout"
            >
              <Loader2 v-if="workspace.isMutating" class="h-4 w-4 animate-spin" />
              <CheckCircle2 v-else class="h-4 w-4" />
              Submit
            </button>
            <button
              class="focus-ring rounded-lg border border-slate-200 px-4 py-2.5 text-sm font-semibold text-ink"
              type="button"
              @click="showPayoutForm = false; payoutError = ''"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ── Main grid: events + pay panel ────────────────────────────────── -->
    <div class="grid gap-5 lg:grid-cols-[1fr_300px]">

      <!-- Events panel -->
      <section class="rounded-xl border border-slate-200 bg-white">
        <div class="flex items-center justify-between gap-3 border-b border-slate-100 px-5 py-3.5">
          <div class="flex items-center gap-2">
            <TrendingUp class="h-4 w-4 text-signal" />
            <h2 class="text-sm font-semibold text-ink">Compensation events</h2>
          </div>
          <div class="flex items-center gap-0.5 rounded-lg border border-slate-200 bg-slate-50 p-0.5 text-xs font-semibold">
            <button
              v-for="tab in ([{ id: 'all', label: 'All' }, { id: 'earnings', label: 'Earnings' }, { id: 'deductions', label: 'Deductions' }] as const)"
              :key="tab.id"
              type="button"
              class="rounded-md px-2.5 py-1 transition-colors"
              :class="eventFilter === tab.id ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
              @click="eventFilter = tab.id"
            >{{ tab.label }}</button>
          </div>
        </div>

        <div v-if="workspace.isLoading" class="divide-y divide-slate-100">
          <div v-for="n in 6" :key="n" class="flex animate-pulse items-center gap-3 px-5 py-4">
            <div class="h-8 w-8 rounded-full bg-slate-100" />
            <div class="flex-1 space-y-1.5">
              <div class="h-3.5 w-2/5 rounded bg-slate-100" />
              <div class="h-3 w-1/4 rounded bg-slate-100" />
            </div>
            <div class="h-3.5 w-14 rounded bg-slate-100" />
          </div>
        </div>

        <div v-else-if="!filteredEvents.length" class="px-5 py-14 text-center">
          <Banknote class="mx-auto h-9 w-9 text-slate-200" />
          <p class="mt-3 text-sm font-medium text-ink">No events</p>
          <p class="mt-1 text-xs text-graphite">
            {{ eventFilter === 'all' ? 'Events appear as orders are completed.' : `No ${eventFilter} events on this page.` }}
          </p>
        </div>

        <div v-else class="divide-y divide-slate-100">
          <div
            v-for="event in filteredEvents"
            :key="String(event.id ?? event.created_at)"
            class="flex items-center gap-3 px-5 py-3.5"
          >
            <div
              class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full"
              :class="event.is_positive === false ? 'bg-rose-50' : 'bg-emerald-50'"
            >
              <TrendingDown v-if="event.is_positive === false" class="h-3.5 w-3.5 text-rose-500" />
              <TrendingUp v-else class="h-3.5 w-3.5 text-emerald-500" />
            </div>
            <div class="min-w-0 flex-1">
              <p class="truncate text-sm font-medium text-ink">{{ eventLabel(event) }}</p>
              <p class="mt-0.5 text-xs text-graphite">
                {{ formatDate(event.created_at) }}
                <template v-if="event.window_label">
                  <span class="mx-1 text-slate-300">·</span>{{ event.window_label }}
                </template>
              </p>
            </div>
            <StatusPill :label="event.status ?? 'recorded'" tone="neutral" />
            <p
              class="w-20 shrink-0 text-right text-sm font-semibold tabular-nums"
              :class="event.is_positive === false ? 'text-rose-600' : 'text-emerald-700'"
            >
              {{ event.is_positive === false ? '−' : '+' }}{{ money(event.amount) }}
            </p>
          </div>
        </div>

        <Pagination
          :page="workspace.eventsPagination.page"
          :page-size="workspace.eventsPagination.pageSize"
          :count="workspace.eventsPagination.count"
          @update:page="workspace.fetchEvents($event).catch(() => undefined)"
        />
      </section>

      <!-- Pay panel -->
      <aside class="space-y-4">

        <!-- Payment cycle -->
        <section class="rounded-xl border border-slate-200 bg-white">
          <div class="flex items-center justify-between gap-2 border-b border-slate-100 px-4 py-3">
            <div class="flex items-center gap-1.5">
              <CalendarClock class="h-4 w-4 text-signal" />
              <h2 class="text-sm font-semibold text-ink">Payment cycle</h2>
            </div>
            <button
              class="focus-ring text-xs font-semibold text-signal hover:underline underline-offset-2"
              type="button"
              @click="openCycleForm"
            >
              {{ preference?.locked ? 'Request change' : 'Set cycle' }}
            </button>
          </div>
          <div class="px-4 py-3 space-y-2.5">
            <div class="flex items-center gap-2">
              <span class="text-xs text-graphite">Cycle:</span>
              <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="cycleTone(preference?.cycle_type)">
                {{ preferenceLoading ? '…' : cycleLabel(preference?.cycle_type) }}
              </span>
              <span v-if="preference?.locked" class="text-xs text-slate-400">(locked)</span>
            </div>
            <div v-if="pendingCycleChange" class="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs">
              <p class="font-semibold text-amber-900">Change request pending</p>
              <p class="mt-0.5 text-amber-800">→ {{ cycleLabel(pendingCycleChange.requested_cycle) }} · {{ formatDate(pendingCycleChange.created_at) }}</p>
            </div>
            <p v-if="cycleSuccess" class="text-xs font-semibold text-signal">{{ cycleSuccess }}</p>
            <!-- Cycle form -->
            <div v-if="showCycleForm" class="space-y-2.5 rounded-lg border border-slate-200 bg-slate-50 p-3">
              <p class="text-xs font-semibold text-ink">{{ cycleFormMode === 'set' ? 'Set cycle' : 'Request change' }}</p>
              <div class="flex gap-1.5">
                <button
                  v-for="opt in cycleOptions" :key="opt.value" type="button"
                  class="focus-ring flex-1 rounded-lg border px-2 py-1.5 text-xs font-semibold transition-colors"
                  :class="selectedCycle === opt.value ? 'border-ink bg-ink text-white' : 'border-slate-200 bg-white text-graphite'"
                  @click="selectedCycle = opt.value"
                >{{ opt.label }}</button>
              </div>
              <textarea
                v-if="cycleFormMode === 'request'" v-model="cycleReason"
                class="focus-ring w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs"
                rows="2" placeholder="Reason for change…"
              />
              <p v-if="cycleError" class="text-xs text-berry">{{ cycleError }}</p>
              <div class="flex gap-2">
                <button
                  class="focus-ring inline-flex flex-1 items-center justify-center gap-1.5 rounded-lg bg-ink px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-60"
                  type="button" :disabled="cycleSubmitting" @click="submitCycleChange"
                >
                  <Loader2 v-if="cycleSubmitting" class="h-3 w-3 animate-spin" />
                  <CheckCircle2 v-else class="h-3 w-3" />
                  {{ cycleFormMode === 'set' ? 'Save' : 'Submit' }}
                </button>
                <button
                  class="focus-ring rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink"
                  type="button" @click="showCycleForm = false; cycleError = ''"
                >Cancel</button>
              </div>
            </div>
          </div>

          <!-- Payout history -->
          <div class="border-t border-slate-100">
            <p class="px-4 py-2.5 text-xs font-semibold uppercase tracking-wide text-slate-400">Payout history</p>
            <div v-if="payoutHistoryLoading" class="px-4 pb-4 text-center">
              <Loader2 class="mx-auto h-4 w-4 animate-spin text-slate-300" />
            </div>
            <div v-else-if="!payoutHistory.length" class="px-4 pb-4 text-center text-xs text-graphite">No settled payouts yet.</div>
            <div v-else class="divide-y divide-slate-100">
              <div v-for="p in payoutHistory" :key="p.id" class="flex items-center gap-2.5 px-4 py-2.5">
                <div class="min-w-0 flex-1">
                  <p class="text-xs font-semibold text-ink">{{ money(p.total_amount) }}</p>
                  <p class="truncate text-xs text-graphite">{{ p.window_label }}</p>
                  <p v-if="p.paid_at" class="text-xs text-slate-400">Paid {{ formatDate(p.paid_at) }}</p>
                </div>
                <StatusPill :label="p.status" :tone="payoutStatusTone(p.status)" />
              </div>
            </div>
          </div>
        </section>

        <!-- Payout requests list -->
        <section v-if="workspace.payoutRequests.length" class="rounded-xl border border-slate-200 bg-white">
          <div class="flex items-center gap-1.5 border-b border-slate-100 px-4 py-3">
            <Banknote class="h-4 w-4 text-signal" />
            <h2 class="text-sm font-semibold text-ink">Active requests</h2>
          </div>
          <div class="divide-y divide-slate-100">
            <div v-for="req in workspace.payoutRequests" :key="req.id" class="flex items-center gap-3 px-4 py-3">
              <div class="min-w-0 flex-1">
                <p class="text-sm font-semibold text-ink">{{ money(req.amount) }}</p>
                <p class="text-xs text-graphite">{{ formatDate(req.created_at) }}</p>
              </div>
              <StatusPill :label="req.workflow_status ?? req.status" :tone="payoutStatusTone(req.workflow_status ?? req.status)" />
            </div>
          </div>
        </section>

      </aside>
    </div>

    <!-- ── Secondary tabs: Advances | Bonuses | Fines | Tips ────────────── -->
    <section class="rounded-xl border border-slate-200 bg-white">
      <!-- Tab bar -->
      <div class="flex gap-0 border-b border-slate-100">
        <button
          v-for="tab in ([
            { id: 'advances', label: 'Advances',     icon: CreditCard },
            { id: 'bonuses',  label: 'Bonuses',      icon: Star },
            { id: 'fines',    label: 'Fines',        icon: AlertTriangle },
            { id: 'tips',     label: 'Tips received', icon: Gift },
          ] as const)"
          :key="tab.id"
          type="button"
          class="flex items-center gap-1.5 border-b-2 px-5 py-3 text-sm font-semibold transition-colors"
          :class="secondaryTab === tab.id
            ? 'border-ink text-ink'
            : 'border-transparent text-graphite hover:text-ink'"
          @click="secondaryTab = tab.id"
        >
          <component :is="tab.icon" class="h-4 w-4" />
          {{ tab.label }}
        </button>
      </div>

      <!-- Advances -->
      <div v-if="secondaryTab === 'advances'">
        <div class="flex items-center justify-between border-b border-slate-100 px-5 py-3">
          <p class="text-xs text-graphite">Request an advance against your pending earnings.</p>
          <button
            class="focus-ring inline-flex h-8 items-center gap-1.5 rounded-lg border border-slate-200 px-3 text-xs font-semibold text-ink"
            type="button"
            @click="showAdvanceForm = !showAdvanceForm; advanceError = ''"
          >
            <Send class="h-3.5 w-3.5" /> Request
          </button>
        </div>
        <p v-if="advanceSuccess" class="px-5 py-3 text-sm font-semibold text-signal">{{ advanceSuccess }}</p>
        <div v-if="showAdvanceForm" class="grid gap-4 border-b border-slate-100 p-5 sm:grid-cols-2">
          <label class="block">
            <span class="text-sm font-medium text-graphite">Amount</span>
            <input v-model="advanceAmount" class="focus-ring mt-1.5 h-10 w-full rounded-lg border border-slate-200 px-3 text-sm" type="number" min="1" step="0.01" placeholder="0.00" />
          </label>
          <label class="block sm:col-span-2">
            <span class="text-sm font-medium text-graphite">Reason</span>
            <textarea v-model="advanceReason" class="focus-ring mt-1.5 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" rows="2" placeholder="Why do you need this advance?" />
          </label>
          <p v-if="advanceError" class="text-xs text-berry sm:col-span-2">{{ advanceError }}</p>
          <div class="flex gap-2 sm:col-span-2">
            <button class="focus-ring inline-flex items-center gap-2 rounded-lg bg-ink px-4 py-2 text-sm font-semibold text-white disabled:opacity-60" type="button" :disabled="advanceSubmitting" @click="submitAdvance">
              <Loader2 v-if="advanceSubmitting" class="h-3.5 w-3.5 animate-spin" /><CheckCircle2 v-else class="h-3.5 w-3.5" /> Submit
            </button>
            <button class="focus-ring rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-ink" type="button" @click="showAdvanceForm = false; advanceError = ''">Cancel</button>
          </div>
        </div>
        <div v-if="advancesLoading && !advances.length" class="px-5 py-10 text-center"><Loader2 class="mx-auto h-5 w-5 animate-spin text-slate-300" /></div>
        <div v-else-if="!advances.length" class="px-5 py-10 text-center">
          <CreditCard class="mx-auto h-8 w-8 text-slate-200" />
          <p class="mt-2 text-sm text-graphite">No advance requests yet.</p>
        </div>
        <div v-else class="divide-y divide-slate-100">
          <div v-for="adv in advances" :key="adv.id" class="px-5 py-4">
            <div class="flex items-start gap-3">
              <div class="min-w-0 flex-1">
                <p class="text-sm font-semibold text-ink">{{ money(adv.requested_amount) }} requested</p>
                <p v-if="adv.approved_amount" class="mt-0.5 text-xs text-graphite">
                  {{ money(adv.approved_amount) }} approved
                  <span v-if="Number(adv.outstanding_balance) > 0"> · {{ money(adv.outstanding_balance) }} outstanding</span>
                </p>
                <p class="mt-0.5 truncate text-xs text-graphite">{{ adv.reason }}</p>
                <p class="mt-0.5 text-xs text-graphite">{{ formatDate(adv.created_at) }}</p>
              </div>
              <StatusPill :label="adv.status" :tone="advanceStatusTone(adv.status)" />
            </div>
            <p v-if="adv.admin_notes" class="mt-2 rounded-lg bg-slate-50 px-3 py-2 text-xs text-graphite">{{ adv.admin_notes }}</p>
          </div>
        </div>
      </div>

      <!-- Bonuses -->
      <div v-if="secondaryTab === 'bonuses'">
        <div v-if="bonusesLoading" class="px-5 py-10 text-center"><Loader2 class="mx-auto h-5 w-5 animate-spin text-slate-300" /></div>
        <div v-else-if="!bonuses.length" class="px-5 py-10 text-center">
          <Star class="mx-auto h-8 w-8 text-slate-200" />
          <p class="mt-2 text-sm text-graphite">No bonuses recorded yet.</p>
        </div>
        <div v-else class="divide-y divide-slate-100">
          <div v-for="bonus in bonuses" :key="String(bonus.id ?? bonus.created_at)" class="flex items-center gap-4 px-5 py-4">
            <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-amber-50">
              <Star class="h-3.5 w-3.5 text-amber-500" />
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-medium text-ink">{{ eventLabel(bonus) }}</p>
              <p class="mt-0.5 text-xs text-graphite">{{ formatDate(bonus.created_at) }}</p>
            </div>
            <p class="shrink-0 text-sm font-semibold text-emerald-700 tabular-nums">+{{ money(bonus.amount) }}</p>
          </div>
        </div>
      </div>

      <!-- Fines -->
      <div v-if="secondaryTab === 'fines'">
        <div v-if="finesLoading" class="px-5 py-10 text-center"><Loader2 class="mx-auto h-5 w-5 animate-spin text-slate-300" /></div>
        <div v-else-if="!fines.length" class="px-5 py-10 text-center">
          <AlertTriangle class="mx-auto h-8 w-8 text-slate-200" />
          <p class="mt-2 text-sm text-graphite">No fines on record.</p>
        </div>
        <div v-else class="divide-y divide-slate-100">
          <div v-for="fine in fines" :key="fine.id" class="px-5 py-4">
            <div class="flex items-start gap-4">
              <div class="min-w-0 flex-1">
                <p class="text-sm font-semibold text-ink">
                  {{ money(fine.amount) }}
                  <span v-if="fine.fine_type_name" class="ml-1 text-xs font-normal text-graphite">{{ fine.fine_type_name }}</span>
                </p>
                <p v-if="fine.order_topic" class="mt-0.5 truncate text-xs text-graphite">{{ fine.order_topic }}</p>
                <p class="mt-0.5 text-xs text-graphite">{{ formatDate(fine.imposed_at) }}</p>
              </div>
              <div class="flex shrink-0 flex-col items-end gap-1.5">
                <StatusPill :label="fine.status" :tone="fineStatusTone(fine.status)" />
                <button v-if="fine.can_dispute" class="focus-ring text-xs font-semibold text-signal hover:underline underline-offset-2" type="button" @click="openDisputeForm(fine.id)">Dispute</button>
              </div>
            </div>
            <div v-if="disputingFineId === fine.id" class="mt-3 space-y-3 rounded-lg border border-amber-200 bg-amber-50 p-4">
              <p class="text-xs font-semibold text-amber-900">Dispute this fine</p>
              <textarea v-model="disputeReason" class="focus-ring w-full rounded-lg border border-amber-200 bg-white px-3 py-2 text-sm" rows="3" placeholder="Explain why you believe this fine was issued in error…" />
              <p v-if="disputeError" class="text-xs text-berry">{{ disputeError }}</p>
              <div class="flex gap-2">
                <button class="focus-ring inline-flex items-center gap-1.5 rounded-lg bg-ink px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-60" type="button" :disabled="disputeSubmitting" @click="submitDispute(fine.id)">
                  <Loader2 v-if="disputeSubmitting" class="h-3 w-3 animate-spin" /><CheckCircle2 v-else class="h-3 w-3" /> Submit dispute
                </button>
                <button class="focus-ring rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink" type="button" @click="closeDisputeForm">Cancel</button>
              </div>
            </div>
            <div v-else-if="fine.appeal" class="mt-2 rounded-lg bg-slate-50 px-3 py-2">
              <p class="text-xs font-medium text-graphite">Dispute {{ fine.appeal.accepted === true ? 'accepted' : fine.appeal.accepted === false ? 'rejected' : 'under review' }}</p>
              <p v-if="fine.appeal.resolution_notes" class="mt-0.5 text-xs text-graphite">{{ fine.appeal.resolution_notes }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Tips -->
      <div v-if="secondaryTab === 'tips'">
        <div v-if="tipsLoading" class="px-5 py-10 text-center"><Loader2 class="mx-auto h-5 w-5 animate-spin text-slate-300" /></div>
        <div v-else-if="!tips.length" class="px-5 py-10 text-center">
          <Gift class="mx-auto h-8 w-8 text-slate-200" />
          <p class="mt-2 text-sm text-graphite">No tips yet.</p>
          <p class="mt-1 text-xs text-graphite">Tips appear here when clients send them after order completion.</p>
        </div>
        <div v-else class="divide-y divide-slate-100">
          <div v-for="tip in tips" :key="tip.id" class="flex items-center gap-4 px-5 py-4">
            <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-amber-50">
              <Gift class="h-3.5 w-3.5 text-amber-500" />
            </div>
            <div class="min-w-0 flex-1">
              <p class="text-sm font-semibold text-ink">{{ money((tip.writer_share_cents / 100).toFixed(2)) }} <span class="text-xs font-normal text-graphite">your share</span></p>
              <p v-if="tip.message" class="mt-0.5 truncate text-xs text-graphite">{{ tip.message }}</p>
              <p class="mt-0.5 text-xs text-graphite">{{ formatDate(tip.created_at) }}</p>
            </div>
            <StatusPill :label="tip.status" :tone="tip.status === 'settled' ? 'success' : 'neutral'" />
          </div>
        </div>
      </div>

    </section>

  </div>
</template>

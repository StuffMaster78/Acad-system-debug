<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import {
  AlertTriangle,
  Banknote,
  CheckCircle2,
  Clock3,
  Gift,
  Loader2,
  RefreshCw,
  Send,
  TrendingUp,
} from "@lucide/vue";
import { finesApi, type FineRecord } from "@/api/fines";
import { tipsApi, type TipRecord } from "@/api/tips";
import MetricTile from "@/components/ui/MetricTile.vue";
import Pagination from "@/components/ui/Pagination.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useWriterWorkspaceStore } from "@/stores/writerWorkspace";

const workspace = useWriterWorkspaceStore();

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

onMounted(async () => {
  if (!workspace.balance) await workspace.hydrate();
  await Promise.all([
    workspace.fetchEvents(1),
    workspace.fetchPayoutRequests(),
    fetchReceivedTips(),
    fetchFines(),
  ]);
});
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Writer</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Earnings</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Compensation balance, event history, and payout requests.
        </p>
      </div>
      <button
        class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-300 px-4 py-2.5 text-sm font-semibold text-ink disabled:opacity-60"
        type="button"
        :disabled="workspace.isLoading"
        @click="workspace.fetchEvents(workspace.eventsPagination.page).catch(() => undefined)"
      >
        <Loader2 v-if="workspace.isLoading" class="h-4 w-4 animate-spin" />
        <RefreshCw v-else class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <div v-if="workspace.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ workspace.error }}
    </div>
    <div v-if="workspace.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ workspace.notice }}
    </div>

    <section class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <MetricTile
        :metric="{
          label: 'Pending balance',
          value: money(workspace.balance?.pending),
          detail: 'Matured soon — not yet disbursed',
          tone: 'warn',
        }"
      />
      <MetricTile
        :metric="{
          label: 'Lifetime earned',
          value: money(workspace.balance?.lifetime),
          detail: 'All-time compensation total',
          tone: 'good',
        }"
      />
      <MetricTile
        :metric="{
          label: 'Current window',
          value: money(workspace.currentWindow?.net),
          detail: `${workspace.currentWindow?.count ?? 0} events this window`,
          tone: 'neutral',
        }"
      />
      <MetricTile
        :metric="{
          label: 'Completed orders',
          value: String(workspace.summary?.completed_orders ?? 0),
          detail: 'Backend compensation summary',
          tone: 'neutral',
        }"
      />
    </section>

    <div class="grid gap-6 lg:grid-cols-[1fr_360px]">
      <section class="rounded-lg border border-slate-200 bg-white shadow-panel">
        <div class="flex items-center justify-between gap-3 border-b border-slate-200 px-5 py-4">
          <div class="flex items-center gap-2">
            <TrendingUp class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold text-ink">Compensation events</h2>
          </div>
        </div>

        <div v-if="workspace.isLoading" class="space-y-px">
          <div
            v-for="n in 5"
            :key="n"
            class="animate-pulse px-5 py-4"
            aria-hidden="true"
          >
            <div class="flex items-center justify-between gap-4">
              <div class="flex-1 space-y-2">
                <div class="h-3.5 w-1/2 rounded bg-slate-200" />
                <div class="h-3 w-1/4 rounded bg-slate-100" />
              </div>
              <div class="h-3.5 w-16 rounded bg-slate-100" />
            </div>
          </div>
        </div>

        <div v-else-if="!workspace.events.length" class="px-5 py-12 text-center">
          <Banknote class="mx-auto h-8 w-8 text-slate-300" />
          <p class="mt-3 text-sm font-medium text-ink">No earnings events yet</p>
          <p class="mt-1 text-sm text-graphite">Events appear here as orders are completed and compensation is recorded.</p>
        </div>

        <div v-else class="divide-y divide-slate-100">
          <div
            v-for="event in workspace.events"
            :key="String(event.id ?? event.created_at)"
            class="flex items-center gap-4 px-5 py-4"
          >
            <div class="min-w-0 flex-1">
              <p class="truncate text-sm font-medium text-ink">
                {{ event.description ?? event.event_type ?? "Compensation event" }}
              </p>
              <p class="mt-0.5 text-xs text-graphite">{{ formatDate(event.created_at) }}</p>
            </div>
            <StatusPill :label="event.status ?? 'recorded'" tone="neutral" />
            <p class="shrink-0 text-sm font-semibold text-ink">
              {{ money(event.net_amount ?? event.amount) }}
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

      <aside class="space-y-6">
        <section class="rounded-lg border border-slate-200 bg-white shadow-panel">
          <div class="flex items-center justify-between gap-3 border-b border-slate-200 px-5 py-4">
            <div class="flex items-center gap-2">
              <Banknote class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold text-ink">Payout requests</h2>
            </div>
            <button
              class="focus-ring inline-flex h-8 items-center gap-1.5 rounded-md border border-slate-200 px-3 text-xs font-semibold text-ink"
              type="button"
              @click="showPayoutForm = !showPayoutForm"
            >
              <Send class="h-3.5 w-3.5" />
              Request
            </button>
          </div>

          <div v-if="showPayoutForm" class="border-b border-slate-200 p-5 space-y-4">
            <label class="block">
              <span class="text-sm font-medium text-graphite">Amount</span>
              <input
                v-model="payoutForm.amount"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="number"
                min="1"
                step="0.01"
                placeholder="0.00"
              />
            </label>
            <label class="block">
              <span class="text-sm font-medium text-graphite">Reason (optional)</span>
              <input
                v-model="payoutForm.reason"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="text"
                placeholder="e.g. Monthly payout"
              />
            </label>
            <p v-if="payoutError" class="text-xs text-berry">{{ payoutError }}</p>
            <div class="flex gap-2">
              <button
                class="focus-ring inline-flex items-center gap-2 rounded-md bg-ink px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
                type="button"
                :disabled="workspace.isMutating"
                @click="submitPayout"
              >
                <Loader2 v-if="workspace.isMutating" class="h-3.5 w-3.5 animate-spin" />
                <CheckCircle2 v-else class="h-3.5 w-3.5" />
                Submit
              </button>
              <button
                class="focus-ring rounded-md border border-slate-200 px-4 py-2 text-sm font-semibold text-ink"
                type="button"
                @click="showPayoutForm = false; payoutError = ''"
              >
                Cancel
              </button>
            </div>
          </div>

          <div v-if="!workspace.payoutRequests.length" class="px-5 py-8 text-center">
            <Clock3 class="mx-auto h-7 w-7 text-slate-300" />
            <p class="mt-3 text-sm text-graphite">No payout requests yet.</p>
          </div>

          <div v-else class="divide-y divide-slate-100">
            <div
              v-for="req in workspace.payoutRequests"
              :key="req.id"
              class="flex items-center gap-4 px-5 py-3"
            >
              <div class="min-w-0 flex-1">
                <p class="text-sm font-semibold text-ink">{{ money(req.amount) }}</p>
                <p class="mt-0.5 text-xs text-graphite">{{ formatDate(req.created_at) }}</p>
              </div>
              <StatusPill :label="req.workflow_status ?? req.status" :tone="payoutStatusTone(req.workflow_status ?? req.status)" />
            </div>
          </div>
        </section>

        <!-- Fines & disputes -->
        <section class="rounded-lg border border-slate-200 bg-white shadow-panel">
          <div class="flex items-center gap-2 border-b border-slate-200 px-5 py-4">
            <AlertTriangle class="h-5 w-5 text-berry" />
            <h2 class="text-base font-semibold text-ink">Fines</h2>
          </div>

          <div v-if="finesLoading" class="px-5 py-6 text-center">
            <Loader2 class="mx-auto h-5 w-5 animate-spin text-slate-400" />
          </div>
          <div v-else-if="!fines.length" class="px-5 py-8 text-center">
            <AlertTriangle class="mx-auto h-7 w-7 text-slate-300" />
            <p class="mt-3 text-sm text-graphite">No fines on record.</p>
          </div>
          <div v-else class="divide-y divide-slate-100">
            <div
              v-for="fine in fines"
              :key="fine.id"
              class="px-5 py-3"
            >
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
                  <button
                    v-if="fine.can_dispute"
                    class="focus-ring text-xs font-semibold text-signal underline-offset-2 hover:underline"
                    type="button"
                    @click="openDisputeForm(fine.id)"
                  >
                    Dispute
                  </button>
                </div>
              </div>

              <!-- Inline dispute form -->
              <div v-if="disputingFineId === fine.id" class="mt-3 space-y-3 rounded-md border border-amber-200 bg-amber-50 p-4">
                <p class="text-xs font-semibold text-amber-900">Dispute this fine</p>
                <textarea
                  v-model="disputeReason"
                  class="focus-ring w-full rounded-md border border-amber-200 bg-white px-3 py-2 text-sm"
                  rows="3"
                  placeholder="Explain why you believe this fine was issued in error…"
                />
                <p v-if="disputeError" class="text-xs text-berry">{{ disputeError }}</p>
                <div class="flex gap-2">
                  <button
                    class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-ink px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-60"
                    type="button"
                    :disabled="disputeSubmitting"
                    @click="submitDispute(fine.id)"
                  >
                    <Loader2 v-if="disputeSubmitting" class="h-3 w-3 animate-spin" />
                    <CheckCircle2 v-else class="h-3 w-3" />
                    Submit dispute
                  </button>
                  <button
                    class="focus-ring rounded-md border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink"
                    type="button"
                    @click="closeDisputeForm"
                  >
                    Cancel
                  </button>
                </div>
              </div>

              <!-- Existing appeal status -->
              <div v-else-if="fine.appeal" class="mt-2 rounded-md bg-slate-50 px-3 py-2">
                <p class="text-xs font-medium text-graphite">
                  Dispute {{ fine.appeal.accepted === true ? 'accepted' : fine.appeal.accepted === false ? 'rejected' : 'under review' }}
                </p>
                <p v-if="fine.appeal.resolution_notes" class="mt-0.5 text-xs text-graphite">{{ fine.appeal.resolution_notes }}</p>
              </div>
            </div>
          </div>
        </section>

        <!-- Received tips -->
        <section class="rounded-lg border border-slate-200 bg-white shadow-panel">
          <div class="flex items-center gap-2 border-b border-slate-200 px-5 py-4">
            <Gift class="h-5 w-5 text-amber-500" />
            <h2 class="text-base font-semibold text-ink">Tips received</h2>
          </div>

          <div v-if="tipsLoading" class="px-5 py-6 text-center">
            <Loader2 class="mx-auto h-5 w-5 animate-spin text-slate-400" />
          </div>
          <div v-else-if="!tips.length" class="px-5 py-8 text-center">
            <Gift class="mx-auto h-7 w-7 text-slate-300" />
            <p class="mt-3 text-sm text-graphite">No tips yet.</p>
            <p class="mt-1 text-xs text-graphite">Tips appear here when clients send them after order completion.</p>
          </div>
          <div v-else class="divide-y divide-slate-100">
            <div
              v-for="tip in tips"
              :key="tip.id"
              class="flex items-center gap-4 px-5 py-3"
            >
              <div class="min-w-0 flex-1">
                <p class="text-sm font-semibold text-ink">
                  {{ money((tip.writer_share_cents / 100).toFixed(2)) }}
                  <span class="ml-1 text-xs font-normal text-graphite">your share</span>
                </p>
                <p v-if="tip.message" class="mt-0.5 truncate text-xs text-graphite">{{ tip.message }}</p>
                <p class="mt-0.5 text-xs text-graphite">{{ formatDate(tip.created_at) }}</p>
              </div>
              <StatusPill :label="tip.status" :tone="tip.status === 'settled' ? 'success' : 'neutral'" />
            </div>
          </div>
        </section>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { AlertCircle, CheckCircle2, Clock, Search, ShieldAlert } from "@lucide/vue";
import { useDisputesStore } from "@/stores/disputes";
import type { Dispute, DisputeRemedy } from "@/types/disputes";

const disputes = useDisputesStore();
const expandedId = ref<number | null>(null);
const closeNote = ref<Record<number, string>>({});

onMounted(() => disputes.loadAll());

function toggle(id: number) {
  expandedId.value = expandedId.value === id ? null : id;
}

function statusColor(status: string) {
  const map: Record<string, string> = {
    open: "bg-rose-50 text-rose-700 border-rose-200",
    under_review: "bg-amber-50 text-amber-700 border-amber-200",
    resolved: "bg-emerald-50 text-emerald-700 border-emerald-200",
    closed: "bg-slate-100 text-graphite border-slate-200",
    withdrawn: "bg-slate-100 text-graphite border-slate-200",
  };
  return map[status] ?? "bg-slate-100 text-graphite border-slate-200";
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

function canResolve(d: Dispute) {
  return ["open", "under_review"].includes(d.status);
}

function isResolvePanelOpen(id: number) {
  return disputes.resolveForm.disputeId === id;
}

function verdictLabel(v: string | null | undefined) {
  if (v === "writer_wins") return "Writer wins";
  if (v === "client_wins") return "Client wins";
  return "";
}

function remedyLabel(r: string | null | undefined) {
  const map: Record<string, string> = {
    partial_refund: "Partial refund",
    full_refund: "Full refund",
    reassign: "Reassign writer",
    revision: "Request revision",
    cancel_refund: "Cancel + full refund",
  };
  return r ? (map[r] ?? r) : "";
}

const remedyOptions: { key: DisputeRemedy; label: string; description: string }[] = [
  { key: "partial_refund", label: "Partial refund", description: "Issue a partial refund to the client" },
  { key: "full_refund", label: "Full refund", description: "Issue a full refund of the order amount" },
  { key: "reassign", label: "Reassign writer", description: "Assign the order to a different writer" },
  { key: "revision", label: "Request revision", description: "Send the order back for a free revision" },
  { key: "cancel_refund", label: "Cancel + full refund", description: "Cancel the order and issue a full refund" },
];

const canConfirmResolve = () => {
  if (!disputes.resolveForm.verdict || !disputes.resolveForm.resolution.trim()) return false;
  if (disputes.resolveForm.verdict === "client_wins" && !disputes.resolveForm.remedy) return false;
  return true;
};

const statusOptions = [
  { key: "all", label: "All" },
  { key: "open", label: "Open" },
  { key: "under_review", label: "Under review" },
  { key: "resolved", label: "Resolved" },
  { key: "closed", label: "Closed" },
] as const;
</script>

<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-slate-200 pb-6">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Admin</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Disputes</h1>
        <p class="mt-2 text-sm text-graphite">Review, investigate, and resolve client disputes.</p>
      </div>
      <div class="flex items-center gap-3 text-sm">
        <div class="rounded-lg border border-rose-200 bg-rose-50 px-3 py-1.5 text-center">
          <p class="text-xs text-rose-700">Open</p>
          <p class="text-lg font-bold text-rose-800">{{ disputes.openCount }}</p>
        </div>
        <div class="rounded-lg border border-amber-200 bg-amber-50 px-3 py-1.5 text-center">
          <p class="text-xs text-amber-700">In review</p>
          <p class="text-lg font-bold text-amber-800">{{ disputes.underReviewCount }}</p>
        </div>
      </div>
    </div>

    <p v-if="disputes.notice" class="rounded-lg bg-emerald-50 border border-emerald-200 px-4 py-2 text-sm text-emerald-800">{{ disputes.notice }}</p>
    <p v-if="disputes.error" class="rounded-lg bg-rose-50 border border-rose-200 px-4 py-2 text-sm text-rose-800">{{ disputes.error }}</p>

    <!-- Filters -->
    <div class="flex items-center gap-3 flex-wrap">
      <div class="relative flex-1 max-w-xs">
        <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-graphite" />
        <input
          v-model="disputes.query"
          type="text"
          placeholder="Search disputes…"
          class="w-full rounded-lg border border-slate-200 py-2 pl-9 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-signal/30"
        />
      </div>
      <div class="flex items-center gap-1 rounded-lg border border-slate-200 p-1">
        <button
          v-for="opt in statusOptions"
          :key="opt.key"
          class="rounded-md px-3 py-1 text-xs font-medium transition-colors"
          :class="disputes.statusFilter === opt.key ? 'bg-ink text-white' : 'text-graphite hover:text-ink'"
          type="button"
          @click="disputes.statusFilter = opt.key"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <!-- Skeleton -->
    <div v-if="disputes.isLoading" class="space-y-3">
      <div v-for="i in 4" :key="i" class="h-20 rounded-xl bg-slate-100 animate-pulse" />
    </div>

    <!-- Empty -->
    <div
      v-else-if="!disputes.filteredAdmin.length"
      class="flex flex-col items-center gap-3 rounded-lg border border-slate-200 py-16 text-center"
    >
      <ShieldAlert class="h-8 w-8 text-graphite" />
      <p class="text-sm font-medium text-ink">No disputes found</p>
      <p class="text-xs text-graphite">Adjust your filters or search query.</p>
    </div>

    <!-- List -->
    <div v-else class="space-y-3">
      <div
        v-for="dispute in disputes.filteredAdmin"
        :key="dispute.id"
        class="rounded-lg border border-slate-200 bg-white overflow-hidden"
      >
        <!-- Row header -->
        <button
          class="w-full flex items-start gap-4 px-5 py-4 text-left hover:bg-slate-50 transition-colors"
          type="button"
          @click="toggle(dispute.id)"
        >
          <AlertCircle
            v-if="dispute.status === 'open'"
            class="h-5 w-5 text-rose-500 shrink-0 mt-0.5"
          />
          <Clock
            v-else-if="dispute.status === 'under_review'"
            class="h-5 w-5 text-amber-500 shrink-0 mt-0.5"
          />
          <CheckCircle2
            v-else
            class="h-5 w-5 text-emerald-500 shrink-0 mt-0.5"
          />

          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <p class="text-sm font-semibold text-ink">{{ dispute.order_topic }}</p>
              <span
                class="inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium capitalize"
                :class="statusColor(dispute.status)"
              >
                {{ dispute.status.replace("_", " ") }}
              </span>
              <span v-if="dispute.verdict" class="inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium bg-violet-50 text-violet-700 border-violet-200">
                {{ verdictLabel(dispute.verdict) }}
              </span>
            </div>
            <p class="text-xs text-graphite mt-0.5">
              Order #{{ dispute.order_id }} · Raised by {{ dispute.raised_by_username }} · {{ formatDate(dispute.created_at) }}
            </p>
          </div>
          <svg
            class="h-4 w-4 text-graphite shrink-0 mt-1 transition-transform"
            :class="expandedId === dispute.id ? 'rotate-180' : ''"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </button>

        <!-- Detail -->
        <div v-if="expandedId === dispute.id" class="border-t border-slate-100 px-5 py-4 space-y-4">
          <!-- Reason -->
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-1">Client reason</p>
            <p class="text-sm text-ink leading-relaxed bg-rose-50 border border-rose-100 rounded-lg px-3 py-2">{{ dispute.reason }}</p>
          </div>

          <!-- Admin notes -->
          <div v-if="dispute.admin_notes">
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-1">Admin notes</p>
            <p class="text-sm text-ink leading-relaxed">{{ dispute.admin_notes }}</p>
          </div>

          <!-- Resolution -->
          <div v-if="dispute.resolution">
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-1">Resolution</p>
            <p class="text-sm text-ink leading-relaxed bg-emerald-50 border border-emerald-100 rounded-lg px-3 py-2">{{ dispute.resolution }}</p>
            <div class="mt-1 flex items-center gap-3 flex-wrap text-xs text-graphite">
              <span v-if="dispute.remedy">Remedy: <span class="font-medium text-ink">{{ remedyLabel(dispute.remedy) }}</span></span>
              <span v-if="dispute.refund_amount">Refund: <span class="font-medium text-ink">${{ dispute.refund_amount }}</span></span>
              <span v-if="dispute.resolved_at">Resolved {{ formatDate(dispute.resolved_at) }}</span>
            </div>
          </div>

          <!-- Actions -->
          <div v-if="canResolve(dispute)" class="space-y-4 pt-2 border-t border-slate-100">

            <!-- Resolve panel (open) -->
            <div v-if="isResolvePanelOpen(dispute.id)" class="space-y-4 rounded-xl bg-slate-50 border border-slate-200 p-4">

              <!-- Step 1: Verdict -->
              <div>
                <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-2">Step 1 — Who wins?</p>
                <div class="flex gap-2">
                  <button
                    class="flex-1 rounded-lg border-2 px-4 py-2.5 text-sm font-semibold transition-colors"
                    :class="disputes.resolveForm.verdict === 'writer_wins'
                      ? 'border-emerald-500 bg-emerald-50 text-emerald-800'
                      : 'border-slate-200 bg-white text-graphite hover:border-emerald-300 hover:text-emerald-700'"
                    type="button"
                    @click="disputes.resolveForm.verdict = 'writer_wins'; disputes.resolveForm.remedy = null; disputes.resolveForm.refundAmount = ''"
                  >
                    Writer wins
                    <span class="block text-xs font-normal opacity-70">No action taken</span>
                  </button>
                  <button
                    class="flex-1 rounded-lg border-2 px-4 py-2.5 text-sm font-semibold transition-colors"
                    :class="disputes.resolveForm.verdict === 'client_wins'
                      ? 'border-rose-500 bg-rose-50 text-rose-800'
                      : 'border-slate-200 bg-white text-graphite hover:border-rose-300 hover:text-rose-700'"
                    type="button"
                    @click="disputes.resolveForm.verdict = 'client_wins'"
                  >
                    Client wins
                    <span class="block text-xs font-normal opacity-70">Select a remedy below</span>
                  </button>
                </div>
              </div>

              <!-- Step 2: Remedy (only when client wins) -->
              <div v-if="disputes.resolveForm.verdict === 'client_wins'">
                <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-2">Step 2 — Choose remedy</p>
                <div class="space-y-2">
                  <label
                    v-for="opt in remedyOptions"
                    :key="opt.key"
                    class="flex items-start gap-3 rounded-lg border-2 cursor-pointer px-3 py-2.5 transition-colors"
                    :class="disputes.resolveForm.remedy === opt.key
                      ? 'border-signal bg-signal/5'
                      : 'border-slate-200 bg-white hover:border-slate-300'"
                  >
                    <input
                      type="radio"
                      name="remedy"
                      :value="opt.key"
                      class="mt-0.5 accent-signal"
                      :checked="disputes.resolveForm.remedy === opt.key"
                      @change="disputes.resolveForm.remedy = opt.key"
                    />
                    <div class="min-w-0">
                      <p class="text-sm font-medium text-ink">{{ opt.label }}</p>
                      <p class="text-xs text-graphite">{{ opt.description }}</p>
                    </div>
                  </label>
                </div>

                <!-- Partial refund amount -->
                <div v-if="disputes.resolveForm.remedy === 'partial_refund'" class="mt-3">
                  <label class="block text-xs font-semibold uppercase tracking-wide text-graphite mb-1">Refund amount ($)</label>
                  <input
                    v-model="disputes.resolveForm.refundAmount"
                    type="number"
                    min="0"
                    step="0.01"
                    placeholder="0.00"
                    class="w-40 rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/30"
                  />
                </div>
              </div>

              <!-- Resolution note -->
              <div>
                <label class="block text-xs font-semibold uppercase tracking-wide text-graphite mb-1">Resolution note *</label>
                <textarea
                  v-model="disputes.resolveForm.resolution"
                  rows="3"
                  placeholder="Describe the outcome and reasoning for the decision…"
                  class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/30"
                />
              </div>

              <!-- Confirm row -->
              <div class="flex gap-2">
                <button
                  class="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50 transition-colors"
                  type="button"
                  :disabled="!canConfirmResolve() || disputes.isSaving"
                  @click="disputes.resolveDispute(dispute.id)"
                >
                  {{ disputes.isSaving ? "Resolving…" : "Confirm resolution" }}
                </button>
                <button
                  class="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-graphite hover:text-ink transition-colors"
                  type="button"
                  @click="disputes.resolveForm.disputeId = null"
                >
                  Cancel
                </button>
              </div>
            </div>

            <!-- Action buttons (resolve panel closed) -->
            <div v-else class="flex items-center gap-2 flex-wrap">
              <button
                class="rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-700 transition-colors"
                type="button"
                @click="disputes.openResolveForm(dispute.id)"
              >
                Resolve
              </button>
              <input
                v-model="closeNote[dispute.id]"
                type="text"
                placeholder="Close note (optional)"
                class="flex-1 min-w-0 max-w-xs rounded-lg border border-slate-200 px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-signal/30"
              />
              <button
                class="rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-medium text-graphite hover:text-ink transition-colors"
                type="button"
                :disabled="disputes.isSaving"
                @click="disputes.closeDispute(dispute.id, closeNote[dispute.id])"
              >
                Close without verdict
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

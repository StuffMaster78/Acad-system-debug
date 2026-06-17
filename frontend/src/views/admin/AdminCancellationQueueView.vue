<script setup lang="ts">
import { onMounted } from "vue";
import { Ban, Search, XCircle } from "@lucide/vue";
import { useCancellationQueueStore } from "@/stores/cancellationQueue";
import type { CancellationQueueItem } from "@/types/cancellation";

const store = useCancellationQueueStore();

onMounted(() => store.load());

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}

function formatDateTime(iso: string) {
  return new Date(iso).toLocaleString("en-US", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

function hoursUntil(deadline: string | null) {
  if (!deadline) return null;
  const diff = new Date(deadline).getTime() - Date.now();
  return Math.round(diff / (1000 * 60 * 60));
}

function deadlineColor(deadline: string | null) {
  const h = hoursUntil(deadline);
  if (h === null) return "text-graphite";
  if (h < 6) return "text-rose-600 font-semibold";
  if (h < 24) return "text-amber-600 font-semibold";
  return "text-graphite";
}

function isApprovePanelOpen(item: CancellationQueueItem) {
  return store.approveForm.reqId === item.id;
}

function isRejectPanelOpen(item: CancellationQueueItem) {
  return store.rejectForm.reqId === item.id;
}
</script>

<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-slate-200 pb-6">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Admin</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Cancellation Queue</h1>
        <p class="mt-2 text-sm text-graphite">Review and action pending client cancellation requests.</p>
      </div>
      <div class="rounded-lg border border-amber-200 bg-amber-50 px-4 py-2 text-center">
        <p class="text-xs text-amber-700">Pending</p>
        <p class="text-2xl font-bold text-amber-800">{{ store.queue.length }}</p>
      </div>
    </div>

    <p v-if="store.notice" class="rounded-lg bg-emerald-50 border border-emerald-200 px-4 py-2 text-sm text-emerald-800">{{ store.notice }}</p>
    <p v-if="store.error" class="rounded-lg bg-rose-50 border border-rose-200 px-4 py-2 text-sm text-rose-800">{{ store.error }}</p>

    <!-- Search -->
    <div class="relative max-w-xs">
      <Search class="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-graphite" />
      <input
        v-model="store.query"
        type="text"
        placeholder="Search requests…"
        class="w-full rounded-lg border border-slate-200 py-2 pl-9 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-signal/30"
      />
    </div>

    <!-- Skeleton -->
    <div v-if="store.isLoading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="h-24 rounded-xl bg-slate-100 animate-pulse" />
    </div>

    <!-- Empty -->
    <div
      v-else-if="!store.filtered.length"
      class="flex flex-col items-center gap-3 rounded-lg border border-slate-200 py-16 text-center"
    >
      <Ban class="h-8 w-8 text-graphite" />
      <p class="text-sm font-medium text-ink">No pending cancellation requests</p>
      <p class="text-xs text-graphite">All clear — nothing waiting for review.</p>
    </div>

    <!-- List -->
    <div v-else class="space-y-3">
      <div
        v-for="item in store.filtered"
        :key="item.id"
        class="rounded-lg border border-slate-200 bg-white overflow-hidden"
      >
        <!-- Summary row -->
        <div class="flex items-start gap-4 px-5 py-4">
          <XCircle class="h-5 w-5 text-amber-500 shrink-0 mt-0.5" />
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <p class="text-sm font-semibold text-ink">{{ item.order_topic }}</p>
              <span class="inline-flex items-center rounded-full border border-amber-200 bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-700">
                Pending cancellation
              </span>
            </div>
            <p class="text-xs text-graphite mt-0.5">
              Order #{{ item.order_id }}
              <template v-if="item.client_deadline">
                · Deadline:
                <span :class="deadlineColor(item.client_deadline)">
                  {{ formatDate(item.client_deadline) }}
                  <template v-if="hoursUntil(item.client_deadline) !== null && hoursUntil(item.client_deadline)! < 48">
                    ({{ hoursUntil(item.client_deadline) }}h)
                  </template>
                </span>
              </template>
              · Requested {{ formatDateTime(item.requested_at) }}
            </p>
          </div>
        </div>

        <!-- Detail -->
        <div class="border-t border-slate-100 px-5 py-4 space-y-4">
          <!-- Client reason -->
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-1">Client reason</p>
            <p class="text-sm text-ink leading-relaxed bg-amber-50 border border-amber-100 rounded-lg px-3 py-2">{{ item.reason }}</p>
          </div>

          <!-- Forfeiture breakdown -->
          <div class="flex items-center gap-6 flex-wrap text-sm">
            <div>
              <p class="text-xs text-graphite uppercase tracking-wide">Forfeiture</p>
              <p class="font-semibold text-ink">{{ item.forfeiture_pct }}% · ${{ item.forfeiture_amount }}</p>
            </div>
            <div>
              <p class="text-xs text-graphite uppercase tracking-wide">Refund to client</p>
              <p class="font-semibold text-emerald-700">${{ item.refund_amount }}</p>
            </div>
            <div>
              <p class="text-xs text-graphite uppercase tracking-wide">Was</p>
              <p class="font-medium text-ink capitalize">{{ item.pre_request_status.replace(/_/g, " ") }}</p>
            </div>
          </div>

          <!-- Approve panel -->
          <div v-if="isApprovePanelOpen(item)" class="rounded-xl bg-slate-50 border border-slate-200 p-4 space-y-4">
            <p class="text-sm font-semibold text-ink">Approve cancellation — Order #{{ item.order_id }}</p>

            <!-- Refund destination -->
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-2">Refund destination</p>
              <div class="flex gap-2">
                <button
                  class="flex-1 rounded-lg border-2 px-3 py-2 text-sm font-medium transition-colors"
                  :class="store.approveForm.refund_destination === 'wallet'
                    ? 'border-signal bg-signal/5 text-signal'
                    : 'border-slate-200 text-graphite hover:border-slate-300'"
                  type="button"
                  @click="store.approveForm.refund_destination = 'wallet'"
                >
                  Wallet credit
                </button>
                <button
                  class="flex-1 rounded-lg border-2 px-3 py-2 text-sm font-medium transition-colors"
                  :class="store.approveForm.refund_destination === 'external_gateway'
                    ? 'border-signal bg-signal/5 text-signal'
                    : 'border-slate-200 text-graphite hover:border-slate-300'"
                  type="button"
                  @click="store.approveForm.refund_destination = 'external_gateway'"
                >
                  Original payment method
                </button>
              </div>
            </div>

            <!-- Forfeiture override -->
            <div>
              <label class="block text-xs font-semibold uppercase tracking-wide text-graphite mb-1">
                Forfeiture % override
                <span class="normal-case font-normal text-graphite">(leave blank to keep {{ item.forfeiture_pct }}%)</span>
              </label>
              <input
                v-model="store.approveForm.forfeiture_pct_override"
                type="number"
                min="0"
                max="100"
                step="0.01"
                placeholder="e.g. 30"
                class="w-32 rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/30"
              />
            </div>

            <!-- Notes -->
            <div>
              <label class="block text-xs font-semibold uppercase tracking-wide text-graphite mb-1">Notes (optional)</label>
              <textarea
                v-model="store.approveForm.notes"
                rows="2"
                placeholder="Internal note on this approval…"
                class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/30"
              />
            </div>

            <div class="flex gap-2">
              <button
                class="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50 transition-colors"
                type="button"
                :disabled="store.isSaving"
                @click="store.approve()"
              >
                {{ store.isSaving ? "Approving…" : "Confirm approval" }}
              </button>
              <button
                class="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-graphite hover:text-ink transition-colors"
                type="button"
                @click="store.closeApprove()"
              >
                Cancel
              </button>
            </div>
          </div>

          <!-- Reject panel -->
          <div v-else-if="isRejectPanelOpen(item)" class="rounded-xl bg-slate-50 border border-slate-200 p-4 space-y-4">
            <p class="text-sm font-semibold text-ink">Reject cancellation — Order #{{ item.order_id }}</p>
            <p class="text-xs text-graphite">The order will revert to its previous status and the client will be notified.</p>

            <div>
              <label class="block text-xs font-semibold uppercase tracking-wide text-graphite mb-1">Reason for rejection (optional)</label>
              <textarea
                v-model="store.rejectForm.notes"
                rows="2"
                placeholder="Explain why this request was rejected…"
                class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/30"
              />
            </div>

            <div class="flex gap-2">
              <button
                class="rounded-lg bg-rose-600 px-4 py-2 text-sm font-semibold text-white hover:bg-rose-700 disabled:opacity-50 transition-colors"
                type="button"
                :disabled="store.isSaving"
                @click="store.reject()"
              >
                {{ store.isSaving ? "Rejecting…" : "Confirm rejection" }}
              </button>
              <button
                class="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-graphite hover:text-ink transition-colors"
                type="button"
                @click="store.closeReject()"
              >
                Cancel
              </button>
            </div>
          </div>

          <!-- Action buttons -->
          <div v-else class="flex items-center gap-2 flex-wrap">
            <button
              class="rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-700 transition-colors"
              type="button"
              @click="store.openApprove(item)"
            >
              Approve
            </button>
            <button
              class="rounded-lg border border-rose-200 bg-rose-50 px-3 py-1.5 text-xs font-semibold text-rose-700 hover:bg-rose-100 transition-colors"
              type="button"
              @click="store.openReject(item)"
            >
              Reject
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

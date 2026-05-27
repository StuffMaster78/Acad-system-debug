<script setup lang="ts">
import { onMounted, ref } from "vue";
import { AlertCircle, CheckCircle2, Clock, Search, ShieldAlert } from "@lucide/vue";
import { useDisputesStore } from "@/stores/disputes";
import type { Dispute } from "@/types/disputes";

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

const statusOptions = [
  { key: "all", label: "All" },
  { key: "open", label: "Open" },
  { key: "under_review", label: "Under review" },
  { key: "resolved", label: "Resolved" },
  { key: "closed", label: "Closed" },
] as const;
</script>

<template>
  <div class="space-y-6">
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
      class="flex flex-col items-center gap-3 rounded-xl border border-slate-200 py-16 text-center"
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
        class="rounded-xl border border-slate-200 bg-white shadow-panel overflow-hidden"
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
            <p v-if="dispute.resolved_at" class="text-xs text-graphite mt-1">Resolved {{ formatDate(dispute.resolved_at) }}</p>
          </div>

          <!-- Actions -->
          <div v-if="canResolve(dispute)" class="space-y-3 pt-2 border-t border-slate-100">
            <!-- Resolve form -->
            <div v-if="isResolvePanelOpen(dispute.id)" class="space-y-2">
              <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Resolution note *</p>
              <textarea
                v-model="disputes.resolveForm.resolution"
                rows="3"
                placeholder="Describe how the dispute is being resolved…"
                class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/30"
              />
              <div class="flex gap-2">
                <button
                  class="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-50 transition-colors"
                  type="button"
                  :disabled="!disputes.resolveForm.resolution || disputes.isSaving"
                  @click="disputes.resolveDispute(dispute.id)"
                >
                  {{ disputes.isSaving ? "Resolving…" : "Mark resolved" }}
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

            <!-- Close with note -->
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
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

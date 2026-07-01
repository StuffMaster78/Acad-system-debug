<script setup lang="ts">
import { onMounted, ref } from "vue";
import { AlertCircle, CheckCircle2, Clock, Plus, RotateCcw, ShieldAlert } from "@lucide/vue";
import { useDisputesStore } from "@/stores/disputes";

const disputes = useDisputesStore();
const expandedId = ref<number | null>(null);

onMounted(() => disputes.loadMine());

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

function statusIcon(status: string) {
  if (status === "resolved") return CheckCircle2;
  if (status === "under_review") return Clock;
  if (status === "open") return AlertCircle;
  return RotateCcw;
}

function statusLabel(status: string) {
  return status.replace("_", " ");
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" });
}


</script>

<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-slate-200 pb-6">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Client</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Disputes</h1>
        <p class="mt-2 text-sm text-graphite">Raise and track disputes on your orders.</p>
      </div>
      <button
        class="inline-flex items-center gap-1.5 rounded-lg bg-ink px-4 py-2.5 text-sm font-semibold text-white hover:bg-ink/90 transition-colors"
        type="button"
        @click="disputes.openRaiseModal()"
      >
        <Plus class="h-4 w-4" />
        Raise dispute
      </button>
    </div>

    <p v-if="disputes.notice" class="rounded-lg bg-emerald-50 border border-emerald-200 px-4 py-2 text-sm text-emerald-800">{{ disputes.notice }}</p>
    <p v-if="disputes.error" class="rounded-lg bg-rose-50 border border-rose-200 px-4 py-2 text-sm text-rose-800">{{ disputes.error }}</p>

    <!-- Skeleton -->
    <div v-if="disputes.isLoading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="h-20 rounded-xl bg-slate-100 animate-pulse" />
    </div>

    <!-- Empty -->
    <div
      v-else-if="!disputes.myList.length"
      class="flex flex-col items-center gap-3 rounded-lg border border-slate-200 py-16 text-center"
    >
      <ShieldAlert class="h-8 w-8 text-graphite" />
      <p class="text-sm font-medium text-ink">No disputes</p>
      <p class="text-xs text-graphite max-w-xs">If you have an issue with a delivered order, raise a dispute and our team will review it.</p>
      <button
        class="mt-2 inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-ink hover:bg-slate-50 transition-colors"
        type="button"
        @click="disputes.openRaiseModal()"
      >
        <Plus class="h-4 w-4" />
        Raise your first dispute
      </button>
    </div>

    <!-- Dispute list -->
    <div v-else class="space-y-3">
      <div
        v-for="dispute in disputes.myList"
        :key="dispute.id"
        class="rounded-lg border border-slate-200 bg-white overflow-hidden"
      >
        <!-- Row header -->
        <button
          class="w-full flex items-start gap-4 px-5 py-4 text-left hover:bg-slate-50 transition-colors"
          type="button"
          @click="toggle(dispute.id)"
        >
          <component
            :is="statusIcon(dispute.status)"
            class="h-5 w-5 shrink-0 mt-0.5"
            :class="{
              'text-rose-500': dispute.status === 'open',
              'text-amber-500': dispute.status === 'under_review',
              'text-emerald-500': dispute.status === 'resolved',
              'text-graphite': ['closed', 'withdrawn'].includes(dispute.status),
            }"
          />
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-2 flex-wrap">
              <p class="text-sm font-semibold text-ink truncate">{{ dispute.order_topic }}</p>
              <span
                class="inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium capitalize"
                :class="statusColor(dispute.status)"
              >
                {{ statusLabel(dispute.status) }}
              </span>
            </div>
            <p class="text-xs text-graphite mt-0.5">Order #{{ dispute.order_id }} · Raised {{ formatDate(dispute.created_at) }}</p>
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

        <!-- Expanded detail -->
        <div v-if="expandedId === dispute.id" class="border-t border-slate-100 px-5 py-4 space-y-4">
          <div>
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-1">Your reason</p>
            <p class="text-sm text-ink leading-relaxed">{{ dispute.reason }}</p>
          </div>

          <div v-if="dispute.admin_notes">
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-1">Admin notes</p>
            <p class="text-sm text-ink leading-relaxed bg-amber-50 border border-amber-100 rounded-lg px-3 py-2">{{ dispute.admin_notes }}</p>
          </div>

          <div v-if="dispute.resolution">
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite mb-1">Resolution</p>
            <p class="text-sm text-ink leading-relaxed bg-emerald-50 border border-emerald-100 rounded-lg px-3 py-2">{{ dispute.resolution }}</p>
            <p v-if="dispute.resolved_at" class="text-xs text-graphite mt-1">Resolved {{ formatDate(dispute.resolved_at) }}</p>
          </div>

        </div>
      </div>
    </div>

    <!-- Raise modal -->
    <Transition
      enter-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-100"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="disputes.showRaiseModal"
        class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4"
        @click.self="disputes.showRaiseModal = false"
      >
        <div class="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
          <h2 class="text-base font-bold text-ink mb-1">Raise a dispute</h2>
          <p class="text-xs text-graphite mb-4">Our support team will review your dispute within 24 hours.</p>

          <div class="space-y-4">
            <label class="block">
              <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Order ID *</span>
              <input
                v-model="disputes.raiseForm.orderId"
                type="text"
                placeholder="e.g. 5021"
                class="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/30"
              />
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase tracking-wide text-graphite">Reason *</span>
              <textarea
                v-model="disputes.raiseForm.reason"
                rows="4"
                placeholder="Describe the issue clearly — what was expected and what was delivered…"
                class="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-signal/30"
              />
            </label>
          </div>

          <p v-if="disputes.error" class="mt-2 text-xs text-rose-700">{{ disputes.error }}</p>

          <div class="mt-5 flex justify-end gap-2">
            <button
              class="rounded-lg px-4 py-2 text-sm font-medium text-graphite hover:text-ink transition-colors"
              type="button"
              @click="disputes.showRaiseModal = false"
            >
              Cancel
            </button>
            <button
              class="rounded-lg bg-rose-600 px-4 py-2 text-sm font-semibold text-white hover:bg-rose-700 transition-colors disabled:opacity-50"
              type="button"
              :disabled="!disputes.raiseForm.orderId || !disputes.raiseForm.reason || disputes.isSaving"
              @click="disputes.raiseDispute()"
            >
              {{ disputes.isSaving ? "Raising…" : "Raise dispute" }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { CheckCircle, XCircle, Clock, AlertCircle } from "@lucide/vue";
import { useSpecialOrdersStore } from "@/stores/specialOrders";
import type { MilestoneStatus, SpecialOrderStatus } from "@/types/specialOrders";

const route = useRoute();
const store = useSpecialOrdersStore();

onMounted(() => store.loadDetail(route.params.id as string));

const statusLabel: Record<SpecialOrderStatus, string> = {
  draft: "Draft",
  pending_quote: "Awaiting Quote",
  quote_sent: "Quote Ready",
  quote_accepted: "Quote Accepted",
  quote_rejected: "Quote Rejected",
  in_progress: "In Progress",
  completed: "Completed",
  cancelled: "Cancelled",
};

const statusClass: Record<SpecialOrderStatus, string> = {
  draft: "bg-slate-100 text-graphite",
  pending_quote: "bg-amber-100 text-amber-700",
  quote_sent: "bg-blue-100 text-blue-700",
  quote_accepted: "bg-emerald-100 text-emerald-700",
  quote_rejected: "bg-rose-100 text-rose-700",
  in_progress: "bg-purple-100 text-purple-700",
  completed: "bg-emerald-100 text-emerald-700",
  cancelled: "bg-slate-100 text-slate-400",
};

const milestoneStatusClass: Record<MilestoneStatus, string> = {
  pending: "bg-slate-100 text-graphite",
  in_progress: "bg-amber-100 text-amber-700",
  submitted: "bg-purple-100 text-purple-700",
  revision_requested: "bg-rose-100 text-rose-700",
  approved: "bg-emerald-100 text-emerald-700",
  cancelled: "bg-slate-100 text-slate-400",
};

const rejectReason = ref("");
const showRejectForm = ref(false);

async function handleAccept() {
  if (!store.detail || !store.latestQuote) return;
  await store.acceptQuote(store.detail.id, store.latestQuote.id);
}

async function handleReject() {
  if (!store.detail || !store.latestQuote) return;
  await store.rejectQuote(store.detail.id, store.latestQuote.id, rejectReason.value);
  showRejectForm.value = false;
}
</script>

<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-4xl space-y-6">

      <div v-if="store.isLoadingDetail" class="py-20 text-center text-graphite animate-pulse">Loading…</div>

      <template v-else-if="store.detail">
        <!-- Header -->
        <div class="rounded-xl border border-slate-200 bg-white p-6 shadow-panel">
          <div class="flex items-start justify-between gap-4">
            <div class="min-w-0">
              <div class="flex items-center gap-2">
                <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="statusClass[store.detail.status]">
                  {{ statusLabel[store.detail.status] }}
                </span>
                <span class="text-xs font-mono text-graphite">{{ store.detail.reference }}</span>
              </div>
              <h1 class="mt-2 text-xl font-bold text-ink">{{ store.detail.title }}</h1>
              <p class="mt-1 text-sm text-graphite">{{ store.detail.description }}</p>
            </div>
            <div class="shrink-0 text-right">
              <p v-if="store.detail.quoted_price" class="text-lg font-bold text-ink">${{ store.detail.quoted_price }}</p>
              <p v-else class="text-sm text-amber-600">Awaiting quote</p>
            </div>
          </div>
          <div class="mt-4 flex flex-wrap gap-4 text-xs text-graphite">
            <span v-if="store.detail.deadline" class="flex items-center gap-1">
              <Clock class="size-3.5" />
              Deadline: {{ store.detail.deadline }}
            </span>
            <span v-if="store.detail.writer_username" class="flex items-center gap-1 text-emerald-700">
              <CheckCircle class="size-3.5" />
              {{ store.detail.writer_username }}
            </span>
          </div>
        </div>

        <!-- Quote action banner -->
        <div v-if="store.canAcceptQuote && store.latestQuote" class="rounded-xl border border-blue-200 bg-blue-50 p-5 shadow-panel">
          <h3 class="font-semibold text-blue-900">Quote Ready for Review</h3>
          <p class="mt-1 text-sm text-blue-700">
            Total: <strong>${{ store.latestQuote.price }}</strong>
            <span v-if="store.latestQuote.valid_until"> · Valid until {{ store.latestQuote.valid_until }}</span>
          </p>
          <p v-if="store.latestQuote.notes" class="mt-2 text-sm text-blue-700">{{ store.latestQuote.notes }}</p>

          <!-- Milestone preview -->
          <div v-if="store.latestQuote.milestones_preview.length" class="mt-3 space-y-1">
            <p class="text-xs font-semibold text-blue-800 uppercase tracking-wide">Milestones</p>
            <div v-for="(m, i) in store.latestQuote.milestones_preview" :key="i" class="flex justify-between text-sm text-blue-700">
              <span>{{ m.label }}</span>
              <span class="font-medium">{{ m.due_date }} · ${{ m.price }}</span>
            </div>
          </div>

          <div class="mt-4 flex gap-3">
            <button
              class="flex items-center gap-1.5 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-60"
              :disabled="store.isSaving"
              @click="handleAccept"
            >
              <CheckCircle class="size-4" /> Accept Quote
            </button>
            <button
              class="flex items-center gap-1.5 rounded-lg border border-rose-200 bg-white px-4 py-2 text-sm text-rose-600 hover:bg-rose-50"
              @click="showRejectForm = !showRejectForm"
            >
              <XCircle class="size-4" /> Reject
            </button>
          </div>

          <!-- Reject form -->
          <div v-if="showRejectForm" class="mt-3 space-y-2">
            <textarea
              v-model="rejectReason"
              rows="2"
              placeholder="Reason for rejection (optional)…"
              class="w-full rounded-lg border border-rose-200 px-3 py-2 text-sm focus-ring resize-none"
            />
            <button
              class="rounded-lg bg-rose-600 px-4 py-1.5 text-sm font-medium text-white hover:bg-rose-700 disabled:opacity-60"
              :disabled="store.isSaving"
              @click="handleReject"
            >Confirm Rejection</button>
          </div>
        </div>

        <!-- Tabs -->
        <div class="flex gap-1 rounded-lg border border-slate-200 bg-white p-1 shadow-panel">
          <button
            v-for="tab in [{ key: 'milestones', label: 'Milestones' }, { key: 'quotes', label: 'Quote History' }]"
            :key="tab.key"
            class="flex-1 rounded-md py-1.5 text-sm font-medium transition-colors"
            :class="store.activeTab === tab.key ? 'bg-berry text-white shadow-sm' : 'text-graphite hover:text-ink'"
            @click="store.activeTab = tab.key as typeof store.activeTab"
          >{{ tab.label }}</button>
        </div>

        <!-- Milestones -->
        <div v-if="store.activeTab === 'milestones'" class="space-y-3">
          <div v-if="!store.detail.milestones.length" class="py-12 text-center text-graphite rounded-xl border border-slate-200 bg-white shadow-panel">
            <AlertCircle class="mx-auto mb-2 size-8 text-slate-300" />
            Milestones will appear here after you accept a quote.
          </div>
          <div
            v-for="m in store.detail.milestones"
            :key="m.id"
            class="rounded-xl border border-slate-200 bg-white p-5 shadow-panel"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="min-w-0">
                <div class="flex items-center gap-2">
                  <span class="text-xs font-mono text-graphite">#{{ m.sequence }}</span>
                  <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="milestoneStatusClass[m.status]">
                    {{ m.status.replace(/_/g, ' ') }}
                  </span>
                </div>
                <h3 class="mt-1 font-semibold text-ink">{{ m.label }}</h3>
                <p class="text-sm text-graphite">{{ m.description }}</p>
              </div>
              <div class="shrink-0 text-right text-sm">
                <p class="font-semibold text-ink">${{ m.price }}</p>
                <p class="text-xs text-graphite">Due {{ m.due_date }}</p>
              </div>
            </div>
            <div v-if="m.delivery_notes" class="mt-3 rounded-lg bg-slate-50 px-4 py-2 text-sm text-graphite">
              {{ m.delivery_notes }}
            </div>
          </div>
        </div>

        <!-- Quote history -->
        <div v-else-if="store.activeTab === 'quotes'" class="space-y-3">
          <div v-if="!store.detail.quotes.length" class="py-12 text-center text-graphite rounded-xl border border-slate-200 bg-white shadow-panel">
            No quotes yet.
          </div>
          <div
            v-for="q in store.detail.quotes"
            :key="q.id"
            class="rounded-xl border border-slate-200 bg-white p-5 shadow-panel"
          >
            <div class="flex items-center justify-between gap-4">
              <div>
                <p class="font-semibold text-ink">${{ q.price }}</p>
                <p class="text-xs text-graphite">Submitted {{ q.created_at.slice(0, 10) }} by {{ q.created_by }}</p>
              </div>
              <span class="rounded-full px-2 py-0.5 text-xs font-semibold capitalize"
                :class="{
                  'bg-emerald-100 text-emerald-700': q.status === 'accepted',
                  'bg-rose-100 text-rose-700': q.status === 'rejected',
                  'bg-blue-100 text-blue-700': q.status === 'sent',
                  'bg-slate-100 text-graphite': ['draft','superseded'].includes(q.status),
                }"
              >{{ q.status }}</span>
            </div>
            <p v-if="q.notes" class="mt-2 text-sm text-graphite">{{ q.notes }}</p>
            <p v-if="q.rejection_reason" class="mt-2 text-sm text-rose-600">Rejection reason: {{ q.rejection_reason }}</p>
          </div>
        </div>

      </template>
    </div>
  </div>
</template>

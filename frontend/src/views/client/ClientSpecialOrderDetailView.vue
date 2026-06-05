<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-4xl space-y-4">

      <div v-if="store.isLoadingDetail" class="py-24 text-center text-graphite animate-pulse">Loading…</div>

      <template v-else-if="store.detail">
        <!-- Back + header card -->
        <div>
          <button class="mb-3 inline-flex items-center gap-1.5 text-sm text-graphite hover:text-ink" @click="router.back()">
            <ArrowLeft class="size-3.5" /> Special Orders
          </button>
          <div class="rounded-lg border border-slate-200 bg-white p-6">
            <div class="flex items-start justify-between gap-4">
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="rounded-full px-2.5 py-0.5 text-xs font-semibold" :class="statusClass[store.detail.status] ?? 'bg-slate-100 text-graphite'">
                    {{ statusLabel[store.detail.status] ?? store.detail.status.replace(/_/g, ' ') }}
                  </span>
                  <span class="font-mono text-xs text-graphite">{{ store.detail.reference }}</span>
                </div>
                <h1 class="mt-2 text-xl font-bold text-ink">{{ store.detail.title }}</h1>
                <p class="mt-1 text-sm leading-5 text-graphite">{{ store.detail.inquiry_details || store.detail.description }}</p>
                <div class="mt-3 flex flex-wrap items-center gap-4 text-xs text-graphite">
                  <span v-if="store.detail.duration_days">{{ store.detail.duration_days }} day turnaround</span>
                  <span v-if="store.detail.writer_username" class="flex items-center gap-1.5 text-emerald-700">
                    <CheckCircle class="size-3.5" />
                    Expert assigned
                  </span>
                  <span v-else class="flex items-center gap-1.5 text-amber-600">
                    <AlertCircle class="size-3.5" />
                    Awaiting expert assignment
                  </span>
                </div>
              </div>
              <div class="shrink-0 text-right">
                <p v-if="store.detail.quoted_price" class="text-2xl font-bold text-ink">${{ store.detail.quoted_price }}</p>
                <p v-else class="mt-1 rounded-full bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-700">Awaiting quote</p>
                <p v-if="store.detail.quoted_price" class="mt-0.5 text-xs text-graphite">Quoted amount</p>
              </div>
            </div>

            <!-- Milestone progress bar (only when in_progress+) -->
            <div v-if="store.detail.total_milestones > 0" class="mt-5">
              <div class="mb-1.5 flex items-center justify-between text-xs">
                <span class="text-graphite">{{ store.detail.completed_milestones }} of {{ store.detail.total_milestones }} milestones complete</span>
                <span class="font-semibold text-ink">{{ milestonePct }}%</span>
              </div>
              <div class="h-2 overflow-hidden rounded-full bg-slate-100">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :class="milestonePct === 100 ? 'bg-emerald-500' : 'bg-berry'"
                  :style="{ width: `${milestonePct}%` }"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Quote accept/reject banner -->
        <div
          v-if="store.canAcceptQuote && store.latestQuote"
          class="rounded-xl border border-blue-200 bg-gradient-to-br from-blue-50 to-indigo-50 p-5"
        >
          <div class="flex items-start justify-between gap-4">
            <div>
              <p class="text-xs font-semibold uppercase tracking-wide text-blue-600">Quote ready for your review</p>
              <p class="mt-1 text-2xl font-bold text-blue-900">${{ store.latestQuote.price }}</p>
              <p v-if="store.latestQuote.valid_until" class="mt-0.5 text-xs text-blue-700">
                Valid until {{ fmtDate(store.latestQuote.valid_until) }}
              </p>
            </div>
            <div class="flex gap-2">
              <button
                class="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-60 transition-colors"
                :disabled="store.isSaving"
                @click="handleAccept"
              >
                <CheckCircle class="size-4" /> Accept Quote
              </button>
              <button
                class="inline-flex items-center gap-1.5 rounded-lg border border-rose-200 bg-white px-4 py-2 text-sm font-semibold text-rose-600 hover:bg-rose-50 transition-colors"
                @click="showRejectForm = !showRejectForm"
              >
                <XCircle class="size-4" /> Decline
              </button>
            </div>
          </div>

          <p v-if="store.latestQuote.notes" class="mt-3 text-sm text-blue-700">{{ store.latestQuote.notes }}</p>

          <!-- Milestone preview -->
          <div v-if="store.latestQuote.milestones_preview.length" class="mt-4 overflow-hidden rounded-lg border border-blue-200 bg-white/60">
            <div class="overflow-x-auto">
        <table class="min-w-full text-sm">
              <thead class="border-b border-blue-100 text-xs font-semibold text-blue-700">
                <tr>
                  <th class="px-4 py-2 text-left">Milestone</th>
                  <th class="px-4 py-2 text-left">Due</th>
                  <th class="px-4 py-2 text-right">Price</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-blue-50">
                <tr v-for="(m, i) in store.latestQuote.milestones_preview" :key="i">
                  <td class="px-4 py-2 font-medium text-ink">{{ m.label }}</td>
                  <td class="px-4 py-2 text-graphite">{{ fmtDate(m.due_date) }}</td>
                  <td class="px-4 py-2 text-right font-semibold text-ink">${{ m.price }}</td>
                </tr>
              </tbody>
            </table>
        </div>
          </div>

          <!-- Decline form -->
          <div v-if="showRejectForm" class="mt-4 space-y-2">
            <textarea
              v-model="rejectReason"
              rows="2"
              placeholder="Reason for declining (optional) — this helps us improve the quote…"
              class="w-full rounded-lg border border-rose-200 px-3 py-2 text-sm focus-ring resize-none"
            />
            <button
              class="rounded-lg bg-rose-600 px-4 py-1.5 text-sm font-semibold text-white hover:bg-rose-700 disabled:opacity-60"
              :disabled="store.isSaving"
              @click="handleReject"
            >
              Confirm Decline
            </button>
          </div>
        </div>

        <!-- Tabs -->
        <div class="flex gap-1 rounded-lg border border-slate-200 bg-white p-1">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="flex-1 rounded-md py-1.5 text-sm font-medium transition-colors"
            :class="activeTab === tab.key ? 'bg-berry text-white shadow-sm' : 'text-graphite hover:text-ink'"
            @click="activeTab = tab.key"
          >{{ tab.label }}</button>
        </div>

        <!-- Milestones tab -->
        <div v-if="activeTab === 'milestones'" class="space-y-3">
          <div v-if="!store.detail.milestones.length" class="rounded-xl border border-dashed border-slate-200 bg-white py-14 text-center">
            <Package class="mx-auto mb-3 size-8 text-slate-300" />
            <p class="text-sm text-graphite">Milestones will appear here once you accept a quote.</p>
          </div>
          <div
            v-for="m in store.detail.milestones"
            :key="m.id"
            class="rounded-lg border border-slate-200 bg-white p-5"
          >
            <div class="flex items-start justify-between gap-4">
              <div class="min-w-0">
                <div class="flex items-center gap-2">
                  <span class="font-mono text-xs text-graphite">#{{ m.sequence }}</span>
                  <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="milestoneStatusClass[m.status] ?? 'bg-slate-100 text-graphite'">
                    {{ m.status.replace(/_/g, " ") }}
                  </span>
                </div>
                <h3 class="mt-1.5 font-semibold text-ink">{{ m.label }}</h3>
                <p v-if="m.description" class="mt-0.5 text-sm text-graphite">{{ m.description }}</p>
              </div>
              <div class="shrink-0 text-right">
                <p v-if="m.price" class="font-bold text-ink">${{ m.price }}</p>
                <p v-if="m.due_date" class="mt-0.5 text-xs text-graphite">Due {{ fmtDate(m.due_date) }}</p>
              </div>
            </div>
            <div v-if="m.delivery_notes" class="mt-3 rounded-lg bg-slate-50 px-4 py-2.5 text-sm text-graphite">
              <span class="font-medium text-ink">Delivery notes:</span> {{ m.delivery_notes }}
            </div>

            <!-- Milestone delivery -->
            <div v-if="m.delivery_file_url && m.deliverable_status === 'approved'" class="mt-4 flex items-center gap-3">
              <a
                :href="m.delivery_file_url"
                target="_blank"
                rel="noreferrer"
                class="inline-flex items-center gap-1.5 rounded-md bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-700"
              >
                <Download class="size-3.5" /> Download delivery
              </a>
              <span v-if="m.delivered_at" class="text-xs text-graphite">
                Delivered {{ fmtDate(m.delivered_at) }}
              </span>
            </div>
            <div v-else-if="m.deliverable_status === 'uploaded'" class="mt-4 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-2.5 text-xs text-emerald-800">
              <p class="font-semibold">Work submitted — awaiting your approval</p>
              <p class="mt-0.5 opacity-80">Review the delivery notes above. Contact support if you have concerns or need a revision.</p>
            </div>
          </div>
        </div>

        <!-- Quote history tab -->
        <div v-else-if="activeTab === 'quotes'" class="space-y-3">
          <div v-if="!store.detail.quotes.length" class="rounded-xl border border-dashed border-slate-200 bg-white py-14 text-center text-sm text-graphite">
            No quotes yet. One will appear here once our team prepares your estimate.
          </div>
          <div
            v-for="q in store.detail.quotes"
            :key="q.id"
            class="rounded-lg border border-slate-200 bg-white p-5"
          >
            <div class="flex items-start justify-between gap-4">
              <div>
                <p class="text-xl font-bold text-ink">${{ q.price }}</p>
                <p class="mt-0.5 text-xs text-graphite">Submitted {{ fmtDateTime(q.created_at) }}</p>
                <p v-if="q.valid_until" class="text-xs text-graphite">Valid until {{ fmtDate(q.valid_until) }}</p>
              </div>
              <span
                class="rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize"
                :class="{
                  'bg-emerald-100 text-emerald-700': q.status === 'accepted',
                  'bg-rose-100 text-rose-700': q.status === 'rejected',
                  'bg-blue-100 text-blue-700': q.status === 'sent',
                  'bg-slate-100 text-graphite': ['draft', 'superseded'].includes(q.status),
                }"
              >{{ q.status }}</span>
            </div>
            <p v-if="q.notes" class="mt-3 text-sm text-graphite">{{ q.notes }}</p>
            <p v-if="q.rejection_reason" class="mt-2 text-sm text-rose-600">Your reason: {{ q.rejection_reason }}</p>

            <!-- Milestones breakdown -->
            <div v-if="q.milestones_preview.length" class="mt-4 space-y-1.5 border-t border-slate-100 pt-3">
              <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Milestone breakdown</p>
              <div v-for="(mp, i) in q.milestones_preview" :key="i" class="flex items-center justify-between text-sm">
                <span class="text-graphite">{{ mp.label }}</span>
                <span class="font-medium text-ink">${{ mp.price }} · {{ fmtDate(mp.due_date) }}</span>
              </div>
            </div>
          </div>
        </div>

      </template>

      <!-- Error state -->
      <div v-else class="py-20 text-center text-sm text-graphite">
        <p>Special order not found or failed to load.</p>
        <button class="mt-3 text-berry hover:underline" @click="router.back()">Go back</button>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { AlertCircle, ArrowLeft, CheckCircle, Download, Package, XCircle } from "@lucide/vue";
import { useSpecialOrdersStore } from "@/stores/specialOrders";
import type { MilestoneStatus, SpecialOrderStatus } from "@/types/specialOrders";

const route = useRoute();
const router = useRouter();
const store = useSpecialOrdersStore();

onMounted(() => store.loadDetail(route.params.id as string));

const tabs = [
  { key: "milestones", label: "Milestones" },
  { key: "quotes", label: "Quote History" },
];
const activeTab = ref("milestones");

const statusLabel: Partial<Record<SpecialOrderStatus, string>> = {
  inquiry: "Inquiry",
  quote_pending: "Awaiting Quote",
  quote_sent: "Quote Ready",
  quote_accepted: "Quote Accepted",
  awaiting_payment: "Awaiting Payment",
  partially_funded: "Partially Funded",
  ready_for_staffing: "Ready for Staffing",
  assigned: "Assigned",
  on_hold: "On Hold",
  submitted: "Submitted",
  in_progress: "In Progress",
  ready_for_delivery: "Ready for Delivery",
  completed: "Completed",
  cancelled: "Cancelled",
  approved: "Approved",
  revision_requested: "Revision Requested",
  on_revision: "On Revision",
  refunded: "Refunded",
};

const statusClass: Partial<Record<SpecialOrderStatus, string>> = {
  inquiry: "bg-slate-100 text-graphite",
  quote_pending: "bg-amber-100 text-amber-700",
  quote_sent: "bg-blue-100 text-blue-700",
  quote_accepted: "bg-emerald-100 text-emerald-700",
  awaiting_payment: "bg-amber-100 text-amber-700",
  partially_funded: "bg-amber-100 text-amber-700",
  ready_for_staffing: "bg-blue-100 text-blue-700",
  assigned: "bg-blue-100 text-blue-700",
  on_hold: "bg-slate-100 text-graphite",
  submitted: "bg-purple-100 text-purple-700",
  in_progress: "bg-purple-100 text-purple-700",
  ready_for_delivery: "bg-blue-100 text-blue-700",
  completed: "bg-emerald-100 text-emerald-700",
  cancelled: "bg-slate-100 text-slate-400",
  approved: "bg-emerald-100 text-emerald-700",
  revision_requested: "bg-rose-100 text-rose-700",
  on_revision: "bg-amber-100 text-amber-700",
  refunded: "bg-slate-100 text-slate-400",
};

const milestoneStatusClass: Partial<Record<MilestoneStatus, string>> = {
  pending: "bg-slate-100 text-graphite",
  partially_paid: "bg-amber-100 text-amber-700",
  paid: "bg-emerald-100 text-emerald-700",
  overdue: "bg-rose-100 text-rose-700",
  cancelled: "bg-slate-100 text-slate-400",
  refunded: "bg-slate-100 text-slate-400",
};

const milestonePct = computed(() => {
  const d = store.detail;
  if (!d || !d.total_milestones) return 0;
  return Math.round((d.completed_milestones / d.total_milestones) * 100);
});

const showRejectForm = ref(false);
const rejectReason = ref("");

async function handleAccept() {
  if (!store.detail || !store.latestQuote) return;
  await store.acceptQuote(store.detail.id, store.latestQuote.id);
}

async function handleReject() {
  if (!store.detail || !store.latestQuote) return;
  await store.rejectQuote(store.detail.id, store.latestQuote.id, rejectReason.value);
  showRejectForm.value = false;
  rejectReason.value = "";
}

function fmtDate(v: string | null): string {
  if (!v) return "Not set";
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric" }).format(new Date(v));
}

function fmtDateTime(v: string | null): string {
  if (!v) return "Not set";
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(v));
}
</script>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { Plus, Check, CheckCircle, Clock, UserCheck } from "@lucide/vue";
import { useSpecialOrdersStore } from "@/stores/specialOrders";
import type { MilestoneStatus, SpecialOrderStatus } from "@/types/specialOrders";

const route = useRoute();
const store = useSpecialOrdersStore();

onMounted(() => store.loadDetail(route.params.id as string));

const statusLabel: Record<SpecialOrderStatus, string> = {
  draft: "Draft",
  pending_quote: "Awaiting Quote",
  quote_sent: "Quote Sent",
  quote_accepted: "Quote Accepted",
  quote_rejected: "Rejected",
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

// Milestone approval
const approvingId = ref<number | null>(null);

async function handleApprove(milestoneId: number) {
  if (!store.detail) return;
  approvingId.value = milestoneId;
  try {
    await store.approveMilestone(store.detail.id, milestoneId);
  } finally {
    approvingId.value = null;
  }
}

// New milestone in quote form
function addMilestoneRow() {
  store.quoteForm.milestones.push({ label: "", due_date: "", price: "" });
}

function removeMilestoneRow(i: number) {
  store.quoteForm.milestones.splice(i, 1);
}

async function handleSubmitQuote() {
  if (!store.detail) return;
  await store.submitQuote(store.detail.id);
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
              <p v-else class="text-sm text-amber-600">No quote yet</p>
            </div>
          </div>
          <div class="mt-4 flex flex-wrap gap-4 text-xs text-graphite">
            <span v-if="store.detail.deadline" class="flex items-center gap-1">
              <Clock class="size-3.5" />
              Deadline: {{ store.detail.deadline }}
            </span>
            <span class="flex items-center gap-1">
              <UserCheck class="size-3.5" />
              Client: {{ store.detail.client_username }}
            </span>
            <span v-if="store.detail.writer_username" class="text-emerald-700">
              Writer: {{ store.detail.writer_username }}
            </span>
            <span v-else class="text-amber-600">Unassigned</span>
          </div>
        </div>

        <!-- Quote submission form -->
        <div
          v-if="['pending_quote', 'quote_rejected'].includes(store.detail.status)"
          class="rounded-xl border border-slate-200 bg-white shadow-panel"
        >
          <div class="flex items-center justify-between border-b border-slate-100 px-5 py-3">
            <h3 class="text-sm font-semibold text-ink">Submit a Quote</h3>
            <button
              class="flex items-center gap-1.5 rounded-lg bg-berry px-3 py-1.5 text-xs font-medium text-white hover:bg-berry/90"
              @click="store.showQuoteForm = !store.showQuoteForm"
            >
              <Plus class="size-3.5" />
              {{ store.showQuoteForm ? 'Cancel' : 'New Quote' }}
            </button>
          </div>

          <div v-if="store.showQuoteForm" class="p-5 space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-medium text-graphite mb-1">Total Price *</label>
                <input v-model="store.quoteForm.price" placeholder="e.g. 850.00" class="w-full rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring" />
              </div>
              <div>
                <label class="block text-xs font-medium text-graphite mb-1">Valid Until</label>
                <input v-model="store.quoteForm.valid_until" type="date" class="w-full rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring" />
              </div>
            </div>
            <div>
              <label class="block text-xs font-medium text-graphite mb-1">Notes</label>
              <textarea v-model="store.quoteForm.notes" rows="3" class="w-full rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring resize-none" />
            </div>

            <!-- Milestones in quote -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <label class="text-xs font-medium text-graphite">Milestones</label>
                <button class="text-xs text-berry hover:underline" @click="addMilestoneRow">+ Add milestone</button>
              </div>
              <div class="space-y-2">
                <div v-for="(m, i) in store.quoteForm.milestones" :key="i" class="flex gap-2 items-center">
                  <input v-model="m.label" placeholder="Label" class="flex-1 rounded border border-slate-200 px-2 py-1 text-sm focus-ring" />
                  <input v-model="m.due_date" type="date" class="w-36 rounded border border-slate-200 px-2 py-1 text-sm focus-ring" />
                  <input v-model="m.price" placeholder="Price" class="w-24 rounded border border-slate-200 px-2 py-1 text-sm focus-ring" />
                  <button class="text-rose-400 hover:text-rose-600 text-xs" @click="removeMilestoneRow(i)">✕</button>
                </div>
              </div>
            </div>

            <button
              class="flex items-center gap-1.5 rounded-lg bg-berry px-4 py-2 text-sm font-medium text-white hover:bg-berry/90 disabled:opacity-60"
              :disabled="store.isSaving || !store.quoteForm.price"
              @click="handleSubmitQuote"
            >
              <Check class="size-4" /> Send Quote to Client
            </button>
          </div>
        </div>

        <!-- Tabs -->
        <div class="flex gap-1 rounded-lg border border-slate-200 bg-white p-1 shadow-panel">
          <button
            v-for="tab in [{ key: 'milestones', label: 'Milestones' }, { key: 'quotes', label: 'Quotes' }, { key: 'access', label: 'Access Notes' }]"
            :key="tab.key"
            class="flex-1 rounded-md py-1.5 text-sm font-medium transition-colors"
            :class="store.activeTab === tab.key ? 'bg-berry text-white shadow-sm' : 'text-graphite hover:text-ink'"
            @click="store.activeTab = tab.key as typeof store.activeTab"
          >{{ tab.label }}</button>
        </div>

        <!-- Milestones tab -->
        <div v-if="store.activeTab === 'milestones'" class="space-y-3">
          <div v-if="!store.detail.milestones.length" class="py-12 text-center text-graphite rounded-xl border border-slate-200 bg-white shadow-panel">
            Milestones will appear after a quote is accepted.
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
              <span class="font-medium text-ink">Delivery notes:</span> {{ m.delivery_notes }}
            </div>

            <div v-if="m.status === 'submitted'" class="mt-4">
              <button
                class="flex items-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-sm text-emerald-700 hover:bg-emerald-100 disabled:opacity-60"
                :disabled="approvingId === m.id"
                @click="handleApprove(m.id)"
              >
                <CheckCircle class="size-4" /> Approve Milestone
              </button>
            </div>
          </div>
        </div>

        <!-- Quotes tab -->
        <div v-else-if="store.activeTab === 'quotes'" class="space-y-3">
          <div v-if="!store.detail.quotes.length" class="py-12 text-center text-graphite rounded-xl border border-slate-200 bg-white shadow-panel">
            No quotes submitted yet.
          </div>
          <div
            v-for="q in store.detail.quotes"
            :key="q.id"
            class="rounded-xl border border-slate-200 bg-white p-5 shadow-panel"
          >
            <div class="flex items-start justify-between gap-4">
              <div>
                <p class="text-lg font-bold text-ink">${{ q.price }}</p>
                <p class="text-xs text-graphite">By {{ q.created_by }} · {{ q.created_at.slice(0, 10) }}</p>
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
            <p v-if="q.rejection_reason" class="mt-2 text-sm text-rose-600">Rejection: {{ q.rejection_reason }}</p>
          </div>
        </div>

        <!-- Access tab -->
        <div v-else-if="store.activeTab === 'access'" class="rounded-xl border border-slate-200 bg-white p-6 shadow-panel">
          <h3 class="font-semibold text-ink">Sensitive Access Notes</h3>
          <div v-if="store.detail.sensitive_access" class="mt-4 space-y-3 text-sm">
            <div v-if="store.detail.sensitive_access.portal_url" class="flex gap-3">
              <span class="w-32 shrink-0 text-graphite">Portal URL</span>
              <span class="font-mono text-ink">{{ store.detail.sensitive_access.portal_url }}</span>
            </div>
            <div v-if="store.detail.sensitive_access.credentials_hint" class="flex gap-3">
              <span class="w-32 shrink-0 text-graphite">Credentials</span>
              <span class="text-ink">{{ store.detail.sensitive_access.credentials_hint }}</span>
            </div>
            <div v-if="store.detail.sensitive_access.notes" class="flex gap-3">
              <span class="w-32 shrink-0 text-graphite">Notes</span>
              <span class="text-ink">{{ store.detail.sensitive_access.notes }}</span>
            </div>
            <p v-if="!store.detail.sensitive_access.portal_url && !store.detail.sensitive_access.notes" class="text-graphite">
              No access information recorded.
            </p>
          </div>
          <p v-else class="mt-4 text-graphite">No access information.</p>
        </div>

      </template>
    </div>
  </div>
</template>

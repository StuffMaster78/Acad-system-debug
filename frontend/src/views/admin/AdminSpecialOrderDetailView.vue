<template>
  <div class="min-h-full bg-slate-50 p-6">
    <div class="mx-auto max-w-5xl space-y-4">

      <div v-if="store.isLoadingDetail" class="py-24 text-center text-graphite animate-pulse">Loading…</div>

      <template v-else-if="store.detail">
        <!-- Back + header -->
        <div>
          <button class="mb-3 inline-flex items-center gap-1.5 text-sm text-graphite hover:text-ink" @click="router.back()">
            <ArrowLeft class="size-3.5" /> Special Orders
          </button>
          <div class="rounded-lg border border-slate-200 bg-white p-6">
            <div class="flex flex-wrap items-start justify-between gap-4">
              <div class="min-w-0">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="rounded-full px-2.5 py-0.5 text-xs font-semibold" :class="statusClass[store.detail.status]">
                    {{ statusLabel[store.detail.status] }}
                  </span>
                  <span class="font-mono text-xs text-graphite">{{ store.detail.reference }}</span>
                </div>
                <h1 class="mt-2 text-xl font-bold text-ink">{{ store.detail.title }}</h1>
                <p class="mt-1 text-sm leading-5 text-graphite">{{ store.detail.description }}</p>
                <div class="mt-3 flex flex-wrap items-center gap-4 text-xs text-graphite">
                  <span v-if="store.detail.deadline" class="flex items-center gap-1.5">
                    <Clock class="size-3.5" />
                    Deadline: {{ fmtDate(store.detail.deadline) }}
                  </span>
                  <span class="flex items-center gap-1.5">
                    <UserCheck class="size-3.5" />
                    Client: <strong class="ml-0.5 text-ink">{{ store.detail.client_username }}</strong>
                  </span>
                  <span v-if="store.detail.writer_username" class="flex items-center gap-1.5 text-emerald-700">
                    <Check class="size-3.5" />
                    Writer: {{ store.detail.writer_username }}
                  </span>
                  <span v-else class="flex items-center gap-1.5 text-amber-600">
                    <AlertCircle class="size-3.5" />
                    No writer assigned
                  </span>
                  <span v-if="store.detail.attachments_count > 0" class="flex items-center gap-1.5">
                    <Paperclip class="size-3.5" />
                    {{ store.detail.attachments_count }} attachment{{ store.detail.attachments_count !== 1 ? 's' : '' }}
                  </span>
                </div>
              </div>
              <div class="shrink-0 text-right">
                <p v-if="store.detail.quoted_price" class="text-2xl font-bold text-ink">${{ store.detail.quoted_price }}</p>
                <p v-else class="rounded-full bg-amber-50 px-2.5 py-1 text-xs font-semibold text-amber-700">No quote yet</p>
                <p v-if="store.detail.payment_status" class="mt-0.5 text-xs capitalize text-graphite">{{ store.detail.payment_status }}</p>
              </div>
            </div>

            <!-- Milestone progress -->
            <div v-if="store.detail.total_milestones > 0" class="mt-5">
              <div class="mb-1.5 flex items-center justify-between text-xs">
                <span class="text-graphite">{{ store.detail.completed_milestones }}/{{ store.detail.total_milestones }} milestones</span>
                <span class="font-semibold text-ink">{{ milestonePct }}%</span>
              </div>
              <div class="h-2 overflow-hidden rounded-full bg-slate-100">
                <div
                  class="h-full rounded-full bg-berry transition-all duration-500"
                  :style="{ width: `${milestonePct}%` }"
                />
              </div>
            </div>

            <!-- Admin lifecycle actions -->
            <div class="mt-5 flex flex-wrap gap-2 border-t border-slate-100 pt-4">
              <button
                v-if="!store.detail.writer_username"
                class="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink hover:bg-slate-50 disabled:opacity-60"
                :disabled="store.isSaving"
                @click="showAssign = !showAssign"
              >
                <UserPlus class="size-3.5" />
                Assign Writer
              </button>
              <button
                v-if="['pending_quote', 'quote_rejected'].includes(store.detail.status)"
                class="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-ink hover:bg-slate-50"
                @click="store.showQuoteForm = !store.showQuoteForm"
              >
                <FileText class="size-3.5" />
                {{ store.showQuoteForm ? 'Cancel Quote' : 'Create Quote' }}
              </button>
              <button
                v-if="['in_progress'].includes(store.detail.status)"
                class="inline-flex items-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-700 hover:bg-emerald-100 disabled:opacity-60"
                :disabled="store.isSaving"
                @click="handleMarkComplete"
              >
                <CheckCircle class="size-3.5" />
                Mark Complete
              </button>
              <button
                v-if="!['completed', 'cancelled'].includes(store.detail.status)"
                class="inline-flex items-center gap-1.5 rounded-lg border border-rose-200 bg-rose-50 px-3 py-1.5 text-xs font-semibold text-rose-700 hover:bg-rose-100 disabled:opacity-60"
                :disabled="store.isSaving"
                @click="handleCancelOrder"
              >
                <XCircle class="size-3.5" />
                Cancel Order
              </button>
            </div>

            <!-- Assign writer form -->
            <div v-if="showAssign" class="mt-4 flex items-end gap-3 rounded-lg bg-slate-50 p-4">
              <div class="flex-1">
                <label class="block text-xs font-medium text-graphite mb-1">Writer ID</label>
                <input v-model="writerIdInput" type="number" placeholder="e.g. 42" class="w-full rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring" />
              </div>
              <button
                class="inline-flex items-center gap-1.5 rounded-lg bg-berry px-4 py-1.5 text-sm font-semibold text-white disabled:opacity-60"
                :disabled="store.isSaving || !writerIdInput"
                @click="confirmAssign"
              >
                <Check class="size-4" /> Assign
              </button>
              <button class="rounded-lg border border-slate-200 px-3 py-1.5 text-sm text-graphite hover:text-ink" @click="showAssign = false">Cancel</button>
            </div>
          </div>
        </div>

        <!-- Summary cards -->
        <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div class="rounded-lg border border-slate-200 bg-white p-4">
            <p class="text-xs text-graphite">Quoted price</p>
            <p class="mt-1 text-lg font-bold text-ink">{{ store.detail.quoted_price ? `$${store.detail.quoted_price}` : '—' }}</p>
          </div>
          <div class="rounded-lg border border-slate-200 bg-white p-4">
            <p class="text-xs text-graphite">Milestones</p>
            <p class="mt-1 text-lg font-bold text-ink">{{ store.detail.completed_milestones }}<span class="text-sm font-normal text-graphite">/{{ store.detail.total_milestones }}</span></p>
          </div>
          <div class="rounded-lg border border-slate-200 bg-white p-4">
            <p class="text-xs text-graphite">Payment</p>
            <p class="mt-1 text-sm font-semibold capitalize text-graphite">{{ store.detail.payment_status || '—' }}</p>
          </div>
          <div class="rounded-lg border border-slate-200 bg-white p-4">
            <p class="text-xs text-graphite">Quotes submitted</p>
            <p class="mt-1 text-lg font-bold text-ink">{{ store.detail.quotes.length }}</p>
          </div>
        </div>

        <!-- Quote creation form -->
        <div v-if="store.showQuoteForm" class="rounded-lg border border-slate-200 bg-white p-6 space-y-4">
          <h3 class="font-semibold text-ink">New Quote</h3>
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
            <label class="block text-xs font-medium text-graphite mb-1">Notes for client</label>
            <textarea v-model="(store.quoteForm.notes as string)" rows="3" class="w-full rounded-lg border border-slate-200 px-3 py-1.5 text-sm focus-ring resize-none" />
          </div>

          <!-- Milestones -->
          <div>
            <div class="mb-2 flex items-center justify-between">
              <label class="text-xs font-semibold text-graphite uppercase tracking-wide">Milestones</label>
              <button class="text-xs font-medium text-berry hover:underline" @click="addMilestone">+ Add milestone</button>
            </div>
            <div class="space-y-2">
              <div v-for="(m, i) in store.quoteForm.milestones" :key="i" class="flex items-center gap-2">
                <input v-model="m.label" placeholder="Milestone label" class="flex-1 rounded-lg border border-slate-200 px-2 py-1.5 text-sm focus-ring" />
                <input v-model="m.due_date" type="date" class="w-36 rounded-lg border border-slate-200 px-2 py-1.5 text-sm focus-ring" />
                <input v-model="m.price" placeholder="Price" class="w-24 rounded-lg border border-slate-200 px-2 py-1.5 text-sm focus-ring" />
                <button class="text-rose-400 hover:text-rose-600 text-sm" @click="removeMilestone(i)">✕</button>
              </div>
            </div>
          </div>

          <div class="flex gap-2 pt-1">
            <button
              class="inline-flex items-center gap-1.5 rounded-lg bg-berry px-5 py-2 text-sm font-semibold text-white hover:bg-berry/90 disabled:opacity-60"
              :disabled="store.isSaving || !store.quoteForm.price"
              @click="handleSubmitQuote"
            >
              <Check class="size-4" /> Send Quote to Client
            </button>
            <button class="rounded-lg border border-slate-200 px-4 py-2 text-sm text-graphite hover:text-ink" @click="store.showQuoteForm = false">
              Discard
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
          <div v-if="!store.detail.milestones.length" class="rounded-xl border border-dashed border-slate-200 bg-white py-14 text-center text-sm text-graphite">
            Milestones will appear after a quote is accepted by the client.
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
                  <span class="rounded-full px-2 py-0.5 text-xs font-semibold" :class="milestoneStatusClass[m.status]">
                    {{ m.status.replace(/_/g, " ") }}
                  </span>
                </div>
                <h3 class="mt-1.5 font-semibold text-ink">{{ m.label }}</h3>
                <p v-if="m.description" class="mt-0.5 text-sm text-graphite">{{ m.description }}</p>
                <p v-if="m.writer_username" class="mt-1 text-xs text-graphite">
                  Writer: <span class="font-medium text-ink">{{ m.writer_username }}</span>
                </p>
              </div>
              <div class="shrink-0 text-right">
                <p class="font-bold text-ink">${{ m.price }}</p>
                <p class="mt-0.5 text-xs text-graphite">Due {{ fmtDate(m.due_date) }}</p>
              </div>
            </div>

            <div v-if="m.delivery_notes" class="mt-3 rounded-lg bg-slate-50 px-4 py-2.5 text-sm text-graphite">
              <span class="font-medium text-ink">Delivery notes:</span> {{ m.delivery_notes }}
            </div>
            <div v-if="m.revision_notes" class="mt-2 rounded-lg border border-rose-100 bg-rose-50 px-4 py-2.5 text-sm text-rose-700">
              <span class="font-medium">Revision requested:</span> {{ m.revision_notes }}
            </div>

            <div v-if="m.status === 'submitted'" class="mt-4">
              <button
                class="inline-flex items-center gap-1.5 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-sm font-semibold text-emerald-700 hover:bg-emerald-100 disabled:opacity-60 transition-colors"
                :disabled="approvingId === m.id || store.isSaving"
                @click="handleApprove(m.id)"
              >
                <CheckCircle class="size-4" />
                {{ approvingId === m.id ? 'Approving…' : 'Approve Milestone' }}
              </button>
            </div>

            <div v-if="m.delivered_at || m.approved_at" class="mt-3 flex flex-wrap gap-4 border-t border-slate-100 pt-3 text-xs text-graphite">
              <span v-if="m.delivered_at">Delivered {{ fmtDateTime(m.delivered_at) }}</span>
              <span v-if="m.approved_at" class="text-emerald-700">Approved {{ fmtDateTime(m.approved_at) }}</span>
            </div>
          </div>
        </div>

        <!-- Quotes tab -->
        <div v-else-if="activeTab === 'quotes'" class="space-y-3">
          <div v-if="!store.detail.quotes.length" class="rounded-xl border border-dashed border-slate-200 bg-white py-14 text-center text-sm text-graphite">
            No quotes submitted yet.
          </div>
          <div
            v-for="q in store.detail.quotes"
            :key="q.id"
            class="rounded-lg border border-slate-200 bg-white p-5"
          >
            <div class="flex items-start justify-between gap-4">
              <div>
                <p class="text-xl font-bold text-ink">${{ q.price }}</p>
                <p class="mt-0.5 text-xs text-graphite">By {{ q.created_by }} · {{ fmtDateTime(q.created_at) }}</p>
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
            <p v-if="q.rejection_reason" class="mt-2 text-sm text-rose-600">Client reason: {{ q.rejection_reason }}</p>

            <div v-if="q.milestones_preview.length" class="mt-4 space-y-1.5 border-t border-slate-100 pt-3">
              <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Milestones</p>
              <div v-for="(mp, i) in q.milestones_preview" :key="i" class="flex items-center justify-between text-sm">
                <span class="text-graphite">{{ mp.label }}</span>
                <span class="font-medium text-ink">${{ mp.price }} · {{ fmtDate(mp.due_date) }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Access notes tab -->
        <div v-else-if="activeTab === 'access'" class="rounded-lg border border-slate-200 bg-white p-6">
          <div class="flex items-center gap-2 mb-4">
            <Lock class="size-4 text-graphite" />
            <h3 class="font-semibold text-ink">Sensitive Access Information</h3>
          </div>
          <div v-if="store.detail.sensitive_access" class="space-y-3 rounded-lg bg-slate-50 px-5 py-4 text-sm">
            <div v-if="store.detail.sensitive_access.portal_url" class="flex items-start gap-3">
              <span class="w-36 shrink-0 text-graphite">Portal URL</span>
              <span class="font-mono text-ink break-all">{{ store.detail.sensitive_access.portal_url }}</span>
            </div>
            <div v-if="store.detail.sensitive_access.credentials_hint" class="flex items-start gap-3">
              <span class="w-36 shrink-0 text-graphite">Credentials</span>
              <span class="text-ink">{{ store.detail.sensitive_access.credentials_hint }}</span>
            </div>
            <div v-if="store.detail.sensitive_access.notes" class="flex items-start gap-3">
              <span class="w-36 shrink-0 text-graphite">Notes</span>
              <span class="text-ink">{{ store.detail.sensitive_access.notes }}</span>
            </div>
            <p
              v-if="!store.detail.sensitive_access.portal_url && !store.detail.sensitive_access.credentials_hint && !store.detail.sensitive_access.notes"
              class="text-graphite"
            >
              No access information recorded for this order.
            </p>
          </div>
          <p v-else class="mt-2 text-sm text-graphite">No access information provided.</p>
        </div>

      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { AlertCircle, ArrowLeft, Check, CheckCircle, Clock, FileText, Lock, Paperclip, UserCheck, UserPlus, XCircle } from "@lucide/vue";
import { useSpecialOrdersStore } from "@/stores/specialOrders";
import { specialOrdersApi } from "@/api/specialOrders";
import { useAuthStore } from "@/stores/auth";
import type { MilestoneStatus, SpecialOrderStatus } from "@/types/specialOrders";

const route = useRoute();
const router = useRouter();
const store = useSpecialOrdersStore();
const auth = useAuthStore();

onMounted(() => store.loadDetail(route.params.id as string));

const tabs = [
  { key: "milestones", label: "Milestones" },
  { key: "quotes", label: "Quotes" },
  { key: "access", label: "Access Notes" },
];
const activeTab = ref("milestones");

const statusLabel: Record<SpecialOrderStatus, string> = {
  draft: "Draft",
  pending_quote: "Awaiting Quote",
  quote_sent: "Quote Sent",
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

const milestonePct = computed(() => {
  const d = store.detail;
  if (!d || !d.total_milestones) return 0;
  return Math.round((d.completed_milestones / d.total_milestones) * 100);
});

// Assign writer
const showAssign = ref(false);
const writerIdInput = ref<number | "">("");

async function confirmAssign() {
  if (!store.detail || !writerIdInput.value) return;
  if (!auth.isPreviewSession) {
    await specialOrdersApi.assignWriter(store.detail.id, Number(writerIdInput.value));
    await store.loadDetail(store.detail.id);
  }
  showAssign.value = false;
  writerIdInput.value = "";
}

// Quote
function addMilestone() {
  store.quoteForm.milestones.push({ label: "", due_date: "", price: "" });
}
function removeMilestone(i: number) {
  store.quoteForm.milestones.splice(i, 1);
}
async function handleSubmitQuote() {
  if (!store.detail) return;
  await store.submitQuote(store.detail.id);
}

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

function fmtDate(v: string): string {
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric" }).format(new Date(v));
}

function fmtDateTime(v: string): string {
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(v));
}

async function handleMarkComplete() {
  if (!store.detail) return;
  if (!confirm("Mark this special order as complete?")) return;
  try {
    await specialOrdersApi.complete(store.detail.id);
    await store.loadDetail(store.detail.id);
  } catch {
    // errors surfaced by the store
  }
}

async function handleCancelOrder() {
  const reason = prompt("Reason for cancellation (required):");
  if (!reason?.trim()) return;
  if (!store.detail) return;
  try {
    await specialOrdersApi.cancel(store.detail.id, reason.trim());
    await store.loadDetail(store.detail.id);
  } catch {
    // errors surfaced by the store
  }
}
</script>

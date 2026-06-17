<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { ArrowRight, CheckCircle, RotateCcw, ShieldAlert, XCircle } from "@lucide/vue";
import type { UserRole } from "@/types/roles";
import type { OrderLifecycle, RevisionRequest, RevisionRouteResponse } from "@/types/orders";
import { ordersApi } from "@/api/orders";
import { useOrderStore } from "@/stores/orders";

const props = defineProps<{
  orderId: string;
  lifecycle: OrderLifecycle | null;
  role: UserRole;
}>();

const emit = defineEmits<{ "go-to-adjustments": [] }>();

const orders = useOrderStore();
const revisions = ref<RevisionRequest[]>([]);
const loading = ref(false);
const actionBusy = ref<number | null>(null);
const routingResult = ref<RevisionRouteResponse | null>(null);
const submitError = ref("");

const clientForm = reactive({ reason: "", scope_summary: "", is_within_original_scope: true });
const writerNotesInput = reactive<Record<number, string>>({});

const STATUS_LABEL: Record<string, string> = {
  pending: "Awaiting Review",
  approved: "Approved",
  in_progress: "In Progress",
  submitted: "Work Submitted",
  accepted: "Accepted",
  rejected: "Rejected",
  cancelled: "Cancelled",
};

function statusClass(s: string): string {
  if (s === "accepted") return "bg-emerald-100 text-emerald-700";
  if (s === "approved" || s === "in_progress") return "bg-blue-100 text-blue-700";
  if (s === "submitted") return "bg-saffron/10 text-saffron";
  if (s === "pending") return "bg-amber-100 text-amber-700";
  if (s === "rejected" || s === "cancelled") return "bg-rose-100 text-rose-700";
  return "bg-slate-100 text-slate-600";
}

const canRequestRevision = computed(() =>
  props.role === "client" &&
  (props.lifecycle?.available_actions?.includes("request_revision") ?? false),
);

async function loadRevisions() {
  loading.value = true;
  try {
    const { data } = await ordersApi.revisions(props.orderId);
    revisions.value = Array.isArray(data) ? data : [];
  } catch {
    revisions.value = [];
  } finally {
    loading.value = false;
  }
}

async function submitRevision() {
  if (!clientForm.reason || !clientForm.scope_summary) return;
  submitError.value = "";
  routingResult.value = null;
  try {
    const { data } = await ordersApi.requestRevision(props.orderId, { ...clientForm });
    if ("routing" in data) {
      routingResult.value = data as RevisionRouteResponse;
      if ((data as RevisionRouteResponse).routing === "free_revision") {
        clientForm.reason = "";
        clientForm.scope_summary = "";
        await loadRevisions();
      }
    } else {
      clientForm.reason = "";
      clientForm.scope_summary = "";
      await loadRevisions();
    }
  } catch {
    submitError.value = "Failed to submit revision request. Please try again.";
  }
}

async function doAction(revId: number, action: "approve" | "reject" | "complete" | "accept") {
  actionBusy.value = revId;
  try {
    let updated: RevisionRequest;
    if (action === "approve") ({ data: updated } = await ordersApi.approveRevision(props.orderId, revId));
    else if (action === "reject") ({ data: updated } = await ordersApi.rejectRevision(props.orderId, revId));
    else if (action === "complete") ({ data: updated } = await ordersApi.completeRevision(props.orderId, revId, writerNotesInput[revId]));
    else ({ data: updated } = await ordersApi.acceptRevision(props.orderId, revId));
    revisions.value = revisions.value.map((r) => (r.id === revId ? updated : r));
  } catch {
    // silently ignore — user sees no change
  } finally {
    actionBusy.value = null;
  }
}

onMounted(loadRevisions);
</script>

<template>
  <div class="space-y-4">

    <!-- Paid adjustment routing notice -->
    <div
      v-if="routingResult?.routing === 'paid_adjustment'"
      class="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm"
    >
      <ShieldAlert class="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
      <div class="flex-1">
        <p class="font-semibold text-amber-900">Revision routed to paid scope change</p>
        <p class="mt-0.5 text-amber-800">{{ routingResult.message }}</p>
      </div>
      <button
        class="focus-ring shrink-0 inline-flex items-center gap-1 rounded-md border border-amber-300 bg-white px-2.5 py-1.5 text-xs font-semibold text-amber-900 hover:bg-amber-100"
        @click="emit('go-to-adjustments')"
      >
        View request <ArrowRight class="h-3 w-3" />
      </button>
    </div>

    <!-- Revision history -->
    <div class="rounded-lg border border-slate-200 bg-white">
      <div class="border-b border-slate-200 px-5 py-4">
        <h2 class="text-base font-semibold text-ink">Revision history</h2>
        <p class="mt-0.5 text-xs text-graphite">
          Window: {{ lifecycle?.revision_window_days ?? 0 }} days ·
          <span :class="lifecycle?.is_revision_window_open ? 'text-signal' : 'text-graphite'">
            {{ lifecycle?.is_revision_window_open ? 'Open' : 'Closed' }}
          </span>
        </p>
      </div>

      <div v-if="loading" class="px-5 py-6 text-sm text-graphite">Loading…</div>
      <div v-else-if="!revisions.length" class="px-5 py-8 text-center text-sm text-graphite">
        No revision requests on this order.
      </div>

      <div v-else class="divide-y divide-slate-100">
        <div v-for="rev in revisions" :key="rev.id" class="px-5 py-4 space-y-3">

          <!-- Header row -->
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="text-sm font-semibold text-ink">{{ rev.reason }}</p>
              <p class="mt-1 text-xs leading-5 text-graphite">{{ rev.scope_summary }}</p>
            </div>
            <span
              class="shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold"
              :class="statusClass(rev.status)"
            >{{ STATUS_LABEL[rev.status] ?? rev.status }}</span>
          </div>

          <!-- Meta row -->
          <div class="flex flex-wrap gap-x-3 gap-y-1 text-xs text-graphite">
            <span :class="rev.is_within_free_window ? 'text-signal' : 'text-amber-600'">
              {{ rev.is_within_free_window ? 'Free revision' : 'Outside free window' }}
            </span>
            <span>·</span>
            <span>Requested {{ new Date(rev.created_at).toLocaleDateString() }}</span>
            <template v-if="rev.approved_at">
              <span>·</span><span>Approved {{ new Date(rev.approved_at).toLocaleDateString() }}</span>
            </template>
            <template v-if="rev.submitted_at">
              <span>·</span><span>Submitted {{ new Date(rev.submitted_at).toLocaleDateString() }}</span>
            </template>
            <template v-if="rev.accepted_at">
              <span>·</span><span>Accepted {{ new Date(rev.accepted_at).toLocaleDateString() }}</span>
            </template>
          </div>

          <!-- Writer notes (if submitted) -->
          <p v-if="rev.writer_notes" class="rounded-md bg-slate-50 px-3 py-2 text-xs text-graphite">
            <span class="font-medium">Writer notes:</span> {{ rev.writer_notes }}
          </p>

          <!-- Admin actions: approve / reject -->
          <div
            v-if="(role === 'admin' || role === 'superadmin') && rev.status === 'pending'"
            class="flex gap-2"
          >
            <button
              class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-signal px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-60"
              :disabled="actionBusy === rev.id"
              @click="doAction(rev.id, 'approve')"
            >
              <CheckCircle class="h-3.5 w-3.5" />
              Approve
            </button>
            <button
              class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-rose-200 bg-rose-50 px-3 py-1.5 text-xs font-semibold text-berry disabled:opacity-60"
              :disabled="actionBusy === rev.id"
              @click="doAction(rev.id, 'reject')"
            >
              <XCircle class="h-3.5 w-3.5" />
              Reject
            </button>
          </div>

          <!-- Writer action: complete revision -->
          <div
            v-if="role === 'writer' && (rev.status === 'approved' || rev.status === 'in_progress')"
            class="space-y-2"
          >
            <textarea
              v-model="writerNotesInput[rev.id]"
              class="focus-ring w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
              placeholder="Optional notes for the client about what was changed…"
              rows="2"
            />
            <button
              class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-ink px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-60"
              :disabled="actionBusy === rev.id"
              @click="doAction(rev.id, 'complete')"
            >
              <CheckCircle class="h-3.5 w-3.5" />
              {{ actionBusy === rev.id ? 'Submitting…' : 'Mark revision complete' }}
            </button>
          </div>

          <!-- Client / Admin action: accept submitted revision -->
          <div v-if="rev.status === 'submitted' && (role === 'client' || role === 'admin' || role === 'superadmin')">
            <button
              class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-signal px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-60"
              :disabled="actionBusy === rev.id"
              @click="doAction(rev.id, 'accept')"
            >
              <CheckCircle class="h-3.5 w-3.5" />
              {{ actionBusy === rev.id ? 'Accepting…' : 'Accept revision' }}
            </button>
          </div>

        </div>
      </div>
    </div>

    <!-- Client: request revision form -->
    <form
      v-if="canRequestRevision"
      class="rounded-lg border border-slate-200 bg-white p-5"
      @submit.prevent="submitRevision"
    >
      <div class="flex items-center gap-2">
        <RotateCcw class="h-5 w-5 text-saffron" />
        <h2 class="text-base font-semibold text-ink">Request a revision</h2>
      </div>

      <div class="mt-4 space-y-4">
        <label class="block">
          <span class="text-sm font-medium text-graphite">Reason <span class="text-rose-400">*</span></span>
          <input
            v-model.trim="clientForm.reason"
            class="focus-ring mt-1.5 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
            placeholder="Briefly describe what needs to change"
            maxlength="2000"
          />
        </label>

        <label class="block">
          <span class="text-sm font-medium text-graphite">Detailed scope <span class="text-rose-400">*</span></span>
          <textarea
            v-model.trim="clientForm.scope_summary"
            class="focus-ring mt-1.5 min-h-24 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
            placeholder="Describe exactly what should be changed and how"
          />
        </label>

        <label class="flex cursor-pointer items-center gap-3 rounded-md border border-slate-200 px-3 py-2.5 text-sm">
          <input v-model="clientForm.is_within_original_scope" class="h-4 w-4 accent-signal" type="checkbox" />
          <span class="font-medium text-graphite">This change is within the original order scope</span>
        </label>

        <p v-if="!clientForm.is_within_original_scope" class="rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800">
          Out-of-scope changes will be routed to a paid adjustment rather than a free revision.
        </p>

        <p v-if="submitError" class="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-berry">
          {{ submitError }}
        </p>

        <button
          class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md bg-ink px-5 text-sm font-semibold text-white disabled:opacity-60"
          type="submit"
          :disabled="orders.isMutating || !clientForm.reason || !clientForm.scope_summary"
        >
          <RotateCcw class="h-4 w-4" />
          Submit revision request
        </button>
      </div>
    </form>

    <div
      v-else-if="role === 'client' && !lifecycle?.is_revision_window_open"
      class="rounded-lg border border-slate-100 bg-slate-50 p-4 text-sm text-graphite"
    >
      The revision window for this order has closed. Contact support if you need further changes.
    </div>
    <div
      v-else-if="role === 'client'"
      class="rounded-lg border border-slate-100 bg-slate-50 p-4 text-sm text-graphite"
    >
      Revision requests are not available for this order status.
    </div>

  </div>
</template>

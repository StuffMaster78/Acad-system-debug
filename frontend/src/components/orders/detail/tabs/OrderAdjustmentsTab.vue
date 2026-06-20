<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import {
  AlertTriangle,
  ArrowRight,
  CheckCircle,
  ChevronDown,
  ChevronUp,
  ChevronsRight,
  FileText,
  Loader2,
  Plus,
  RotateCcw,
  ShieldAlert,
  XCircle,
  Zap,
} from "@lucide/vue";
import type { UserRole } from "@/types/roles";
import type { OrderLifecycle, OrderSummary } from "@/types/orders";
import type {
  AdjustmentRequest,
  AdjustmentType,
  CreateExtraServicePayload,
  CreateScopeIncrementPayload,
  ScopeUnitType,
} from "@/types/adjustments";
import { adjustmentsApi } from "@/api/adjustments";
import { useUiStore } from "@/stores/ui";
import { isStaff, dateLabel } from "../types";

// ─── Props & emits ────────────────────────────────────────────────────────────

const props = defineProps<{
  orderId: string;
  order: OrderSummary | null;
  lifecycle: OrderLifecycle | null;
  role: UserRole;
}>();

const emit = defineEmits<{
  "go-to-payments": [];
  "go-to-timeline": [];
}>();

// ─── Shared state ─────────────────────────────────────────────────────────────

const ui = useUiStore();
const active = ref<AdjustmentRequest | null>(null);
const loading = ref(false);
const busy = ref(false);

// ─── Derived helpers ──────────────────────────────────────────────────────────

const canCreate = computed(
  () => props.role === "writer" || isStaff(props.role),
);
const canActAsClient = computed(() => props.role === "client");

// Statuses where the client still has a decision to make
const CLIENT_ACTIONABLE = new Set([
  "pending_client_response",
  "client_countered",
]);

const TERMINAL = new Set([
  "declined",
  "rejected_by_client",
  "rejected_by_staff",
  "cancelled",
  "expired",
  "reversed",
]);

const FUNDED = new Set(["funded", "counter_funded_final", "approved_by_staff"]);

function statusLabel(s: string): string {
  const MAP: Record<string, string> = {
    pending_client_response: "Awaiting client",
    client_countered: "Client countered",
    accepted: "Accepted",
    declined: "Declined",
    funding_pending: "Awaiting payment",
    funded: "Funded",
    counter_funded_final: "Counter funded",
    approved_by_staff: "Approved",
    rejected_by_client: "Rejected by client",
    rejected_by_staff: "Rejected by staff",
    cancelled: "Cancelled",
    expired: "Expired",
    reversed: "Reversed",
  };
  return MAP[s] ?? s;
}

function statusClass(s: string): string {
  if (["accepted", "funded", "counter_funded_final", "approved_by_staff"].includes(s))
    return "bg-emerald-100 text-emerald-700";
  if (["pending_client_response", "funding_pending"].includes(s))
    return "bg-amber-100 text-amber-700";
  if (s === "client_countered") return "bg-blue-100 text-blue-700";
  if (TERMINAL.has(s)) return "bg-rose-100 text-rose-700";
  return "bg-slate-100 text-slate-600";
}

function typeLabel(t: string | null): string {
  const MAP: Record<string, string> = {
    page_increase: "Additional pages",
    slide_increase: "Additional slides",
    diagram_increase: "Additional diagrams",
    design_concept_increase: "Additional design concepts",
    scope_expansion: "Scope expansion",
    extra_service: "Extra service",
    paid_revision: "Paid revision",
    deadline_decrease: "Deadline change",
    other: "Other",
  };
  return t ? (MAP[t] ?? t) : "Adjustment";
}

function proposalRoleLabel(role: string): string {
  const MAP: Record<string, string> = {
    system: "Platform quote",
    client: "Client counter",
    writer: "Writer proposal",
    staff: "Staff override",
  };
  return MAP[role] ?? role;
}

function fmt(val: string | null | undefined): string {
  if (!val) return "—";
  const n = Number(val);
  return isNaN(n) ? val : `$${n.toFixed(2)}`;
}

// ─── Load active adjustment ───────────────────────────────────────────────────

async function loadActive() {
  const id = props.lifecycle?.latest_adjustment_request_id;
  if (!id) return;
  loading.value = true;
  try {
    const { data } = await adjustmentsApi.getDetail(id);
    active.value = data;
  } catch {
    active.value = null;
  } finally {
    loading.value = false;
  }
}

onMounted(loadActive);

// ─── Create form (writer / staff) ─────────────────────────────────────────────

const showCreateForm = ref(false);

// Which kind to create: "scope" | "extra" | "deadline"
const createKind = ref<"scope" | "extra" | "deadline">("scope");

// — Deadline decrease (rush) form — client-initiated ——
const rushForm = reactive({
  new_deadline: "",
  reason: "I need this delivered sooner.",
});
const rushPreview = ref<{ surcharge: string; new_hours: number; original_hours: number } | null>(null);
const rushSubmitting = ref(false);
const rushError = ref("");
const rushSuccess = ref("");
const showRushForm = ref(false);

async function submitRushRequest() {
  rushError.value = "";
  rushSuccess.value = "";
  if (!rushForm.new_deadline) return;
  rushSubmitting.value = true;
  try {
    const { data } = await adjustmentsApi.createDeadlineDecrease(props.orderId, {
      new_deadline: new Date(rushForm.new_deadline).toISOString(),
      reason: rushForm.reason,
    });
    rushSuccess.value = data.message;
    rushPreview.value = null;
    rushForm.new_deadline = "";
    showRushForm.value = false;
    // Reload active adjustment — the rush request is now ACCEPTED/FUNDING_PENDING
    await loadActive();
    ui.toast("Rush request submitted — proceed to payment to confirm.", "success");
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    rushError.value = msg ?? "Could not submit rush request.";
  } finally {
    rushSubmitting.value = false;
  }
}

// — Deadline extension form ——
const deadlineForm = reactive({
  requested_deadline: "",
  reason: "",
  writer_justification: "",
});

async function submitDeadlineExtension() {
  if (!deadlineForm.requested_deadline || !deadlineForm.reason) return;
  busy.value = true;
  createError.value = "";
  try {
    await adjustmentsApi.createDeadlineExtension(props.orderId, {
      requested_deadline: new Date(deadlineForm.requested_deadline).toISOString(),
      reason: deadlineForm.reason,
      writer_justification: deadlineForm.writer_justification,
    });
    showCreateForm.value = false;
    deadlineForm.requested_deadline = "";
    deadlineForm.reason = "";
    deadlineForm.writer_justification = "";
    ui.toast("Deadline extension request submitted. The client will be notified.", "success");
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    createError.value = msg ?? "Failed to submit request. Please try again.";
  } finally {
    busy.value = false;
  }
}

const SCOPE_TYPES: { value: AdjustmentType; label: string; unit: ScopeUnitType }[] = [
  { value: "page_increase", label: "Additional pages", unit: "page" },
  { value: "slide_increase", label: "Additional slides", unit: "slide" },
  { value: "diagram_increase", label: "Additional diagrams", unit: "diagram" },
  { value: "design_concept_increase", label: "Additional design concepts", unit: "design_concept" },
  { value: "scope_expansion", label: "General scope expansion", unit: "other" },
];

const scopeForm = reactive({
  adjustment_type: "page_increase" as AdjustmentType,
  requested_quantity: "" as string | number,
  title: "",
  description: "",
  writer_justification: "",
});

const extraForm = reactive({
  extra_service_code: "",
  title: "",
  description: "",
  writer_justification: "",
});

const createError = ref("");

// Derive unit_type from chosen adjustment_type
const scopeUnitType = computed<ScopeUnitType>(() => {
  const found = SCOPE_TYPES.find((t) => t.value === scopeForm.adjustment_type);
  return found?.unit ?? "other";
});

// Current order quantity for the selected unit — shown as reference
const currentQuantity = computed<number | null>(() => {
  if (!props.order) return null;
  const t = scopeForm.adjustment_type;
  if (t === "slide_increase") return Number(props.order.number_of_slides ?? 0);
  if (t === "page_increase") return Number(props.order.number_of_pages ?? 0);
  return null;
});

async function submitScope() {
  const qty = Number(scopeForm.requested_quantity);
  if (!scopeForm.title || !qty) return;
  busy.value = true;
  createError.value = "";
  try {
    const payload: CreateScopeIncrementPayload = {
      adjustment_type: scopeForm.adjustment_type,
      unit_type: scopeUnitType.value,
      requested_quantity: qty,
      title: scopeForm.title,
      description: scopeForm.description,
      writer_justification: scopeForm.writer_justification,
    };
    const { data } = await adjustmentsApi.createScopeIncrement(props.orderId, payload);
    active.value = data;
    showCreateForm.value = false;
    scopeForm.title = "";
    scopeForm.description = "";
    scopeForm.writer_justification = "";
    scopeForm.requested_quantity = "";
    ui.toast("Scope change request submitted. The client will be notified.", "success");
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    createError.value = msg ?? "Failed to submit request. Please try again.";
  } finally {
    busy.value = false;
  }
}

async function submitExtra() {
  if (!extraForm.extra_service_code || !extraForm.title) return;
  busy.value = true;
  createError.value = "";
  try {
    const payload: CreateExtraServicePayload = {
      extra_service_code: extraForm.extra_service_code,
      title: extraForm.title,
      description: extraForm.description,
      writer_justification: extraForm.writer_justification,
    };
    const { data } = await adjustmentsApi.createExtraService(props.orderId, payload);
    active.value = data;
    showCreateForm.value = false;
    extraForm.extra_service_code = "";
    extraForm.title = "";
    extraForm.description = "";
    extraForm.writer_justification = "";
    ui.toast("Extra service request submitted. The client will be notified.", "success");
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    createError.value = msg ?? "Failed to submit request. Please try again.";
  } finally {
    busy.value = false;
  }
}

// ─── Client: accept original scope ────────────────────────────────────────────

async function acceptScope() {
  if (!active.value) return;
  busy.value = true;
  try {
    await adjustmentsApi.acceptScope(active.value.id);
    await loadActive();
    ui.toast("Scope request accepted. Proceeding to payment.", "success");
    emit("go-to-payments");
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    ui.toast(msg ?? "Could not accept request.", "error");
  } finally {
    busy.value = false;
  }
}

async function acceptExtraService() {
  if (!active.value) return;
  busy.value = true;
  try {
    await adjustmentsApi.acceptExtraService(active.value.id);
    await loadActive();
    ui.toast("Extra service accepted. Proceeding to payment.", "success");
    emit("go-to-payments");
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    ui.toast(msg ?? "Could not accept.", "error");
  } finally {
    busy.value = false;
  }
}

// ─── Client: counter ──────────────────────────────────────────────────────────

const showCounter = ref(false);
const counterForm = reactive({ countered_quantity: "" as string | number, note: "" });
const counterError = ref("");

async function submitCounter() {
  if (!active.value) return;
  const qty = Number(counterForm.countered_quantity);
  if (!qty) return;
  busy.value = true;
  counterError.value = "";
  try {
    await adjustmentsApi.counterScope(active.value.id, qty, counterForm.note);
    await loadActive();
    showCounter.value = false;
    counterForm.countered_quantity = "";
    counterForm.note = "";
    ui.toast("Counter submitted. The writer has been notified.", "success");
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    counterError.value = msg ?? "Could not submit counter.";
  } finally {
    busy.value = false;
  }
}

// ─── Client / staff: decline ──────────────────────────────────────────────────

const showDecline = ref(false);
const declineReason = ref("");
const declineError = ref("");

async function submitDecline() {
  if (!active.value || !declineReason.value.trim()) return;
  busy.value = true;
  declineError.value = "";
  try {
    await adjustmentsApi.decline(active.value.id, declineReason.value.trim());
    await loadActive();
    showDecline.value = false;
    declineReason.value = "";
    ui.toast("Adjustment request declined.", "success");
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    declineError.value = msg ?? "Could not decline.";
  } finally {
    busy.value = false;
  }
}

// ─── Writer: escalate ─────────────────────────────────────────────────────────

const showEscalate = ref(false);
const escalateReason = ref("");
const escalateError = ref("");

async function submitEscalate() {
  if (!active.value || !escalateReason.value.trim()) return;
  busy.value = true;
  escalateError.value = "";
  try {
    await adjustmentsApi.escalate(active.value.id, escalateReason.value.trim());
    await loadActive();
    showEscalate.value = false;
    escalateReason.value = "";
    ui.toast("Escalation submitted. Staff will review.", "success");
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    escalateError.value = msg ?? "Could not escalate.";
  } finally {
    busy.value = false;
  }
}

// ─── Staff: override ──────────────────────────────────────────────────────────

const showOverride = ref(false);
const overrideForm = reactive({ amount: "", notes: "" });
const overrideError = ref("");

async function submitOverride() {
  if (!active.value || !overrideForm.amount) return;
  busy.value = true;
  overrideError.value = "";
  try {
    await adjustmentsApi.staffOverride(active.value.id, overrideForm.amount, overrideForm.notes);
    await loadActive();
    showOverride.value = false;
    overrideForm.amount = "";
    overrideForm.notes = "";
    ui.toast("Override proposal sent to client.", "success");
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    overrideError.value = msg ?? "Could not apply override.";
  } finally {
    busy.value = false;
  }
}

// ─── Staff: resolve escalation ────────────────────────────────────────────────

const showResolve = ref(false);
const resolveForm = reactive({ resolution: "", note: "" });
const resolveError = ref("");

async function submitResolve() {
  if (!active.value || !resolveForm.resolution.trim()) return;
  busy.value = true;
  resolveError.value = "";
  try {
    await adjustmentsApi.resolveEscalation(active.value.id, resolveForm.resolution.trim(), resolveForm.note);
    await loadActive();
    showResolve.value = false;
    resolveForm.resolution = "";
    resolveForm.note = "";
    ui.toast("Escalation resolved.", "success");
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    resolveError.value = msg ?? "Could not resolve escalation.";
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <div class="space-y-4">

    <!-- ── Loading ──────────────────────────────────────────── -->
    <div v-if="loading" class="rounded-lg border border-slate-200 bg-white px-5 py-8 text-center text-sm text-graphite">
      Loading adjustment details…
    </div>

    <!-- ── Active adjustment card ────────────────────────────── -->
    <template v-else-if="active">

      <!-- Funding-pending banner (client) -->
      <div
        v-if="canActAsClient && active.status === 'funding_pending'"
        class="flex items-start gap-3 rounded-lg border border-amber-200 bg-amber-50 p-4"
      >
        <AlertTriangle class="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
        <div class="flex-1 text-sm">
          <p class="font-semibold text-amber-900">Payment required to proceed</p>
          <p class="mt-0.5 text-amber-800">
            The scope change has been accepted. Please complete payment to allow the writer to proceed.
          </p>
        </div>
        <button
          class="focus-ring inline-flex shrink-0 items-center gap-1.5 rounded-md bg-signal px-3 py-1.5 text-sm font-semibold text-white"
          @click="emit('go-to-payments')"
        >
          Pay now <ArrowRight class="h-3.5 w-3.5" />
        </button>
      </div>

      <!-- Escalation notice -->
      <div
        v-if="active.escalated_after_counter"
        class="flex items-start gap-3 rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm"
      >
        <ShieldAlert class="mt-0.5 h-5 w-5 shrink-0 text-berry" />
        <div>
          <p class="font-semibold text-berry">Escalation in progress</p>
          <p class="mt-0.5 text-rose-700">
            The writer has flagged an issue with this scope change. Staff is reviewing.
          </p>
        </div>
      </div>

      <!-- Main card -->
      <div class="rounded-lg border border-slate-200 bg-white">

        <!-- Header -->
        <div class="flex items-start justify-between gap-3 border-b border-slate-200 px-5 py-4">
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <FileText class="h-4 w-4 shrink-0 text-graphite" />
              <span class="text-base font-semibold text-ink">{{ active.title }}</span>
            </div>
            <p class="mt-1 text-xs text-graphite">
              {{ typeLabel(active.adjustment_type) }}
              · Requested {{ dateLabel(active.created_at) }}
            </p>
          </div>
          <span
            class="shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold"
            :class="statusClass(active.status)"
          >
            {{ statusLabel(active.status) }}
          </span>
        </div>

        <!-- Scope details -->
        <div class="border-b border-slate-100 px-5 py-4">
          <div class="grid grid-cols-2 gap-4 sm:grid-cols-4 text-sm">
            <div v-if="active.current_quantity !== null">
              <p class="text-xs font-medium text-graphite">Current</p>
              <p class="mt-0.5 font-semibold text-ink">
                {{ active.current_quantity }} {{ active.unit_type ?? "" }}
              </p>
            </div>
            <div v-if="active.requested_quantity !== null">
              <p class="text-xs font-medium text-graphite">Requested</p>
              <p class="mt-0.5 font-semibold text-ink">
                {{ active.requested_quantity }} {{ active.unit_type ?? "" }}
              </p>
            </div>
            <div v-if="active.countered_quantity !== null">
              <p class="text-xs font-medium text-graphite">Counter</p>
              <p class="mt-0.5 font-semibold text-ink">
                {{ active.countered_quantity }} {{ active.unit_type ?? "" }}
              </p>
            </div>
            <div v-if="active.request_total_amount">
              <p class="text-xs font-medium text-graphite">Quoted price</p>
              <p class="mt-0.5 font-semibold text-ink">{{ fmt(active.request_total_amount) }}</p>
            </div>
            <div v-if="active.counter_total_amount">
              <p class="text-xs font-medium text-graphite">Counter price</p>
              <p class="mt-0.5 font-semibold text-signal">{{ fmt(active.counter_total_amount) }}</p>
            </div>
          </div>

          <p v-if="active.description" class="mt-3 text-sm text-graphite">{{ active.description }}</p>
        </div>

        <!-- Proposal thread -->
        <div v-if="active.proposals.length" class="border-b border-slate-100 px-5 py-4">
          <p class="mb-3 text-xs font-medium text-graphite uppercase tracking-wide">Negotiation thread</p>
          <div class="space-y-3">
            <div
              v-for="p in active.proposals"
              :key="p.id"
              class="flex items-start gap-3 rounded-md border border-slate-100 bg-slate-50 px-3 py-2.5 text-sm"
            >
              <ChevronsRight class="mt-0.5 h-4 w-4 shrink-0 text-graphite" />
              <div class="min-w-0 flex-1">
                <div class="flex flex-wrap items-center justify-between gap-2">
                  <span class="font-medium text-ink">{{ proposalRoleLabel(p.proposal_role) }}</span>
                  <span class="text-xs text-graphite">{{ dateLabel(p.created_at) }}</span>
                </div>
                <p v-if="p.amount" class="mt-0.5 text-graphite">
                  Amount: <span class="font-semibold text-ink">{{ fmt(p.amount) }}</span>
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- ── Action panel ──────────────────────────────────── -->
        <div class="space-y-4 px-5 py-4">

          <!-- CLIENT: pending_client_response → accept / counter / decline -->
          <template v-if="canActAsClient && active.status === 'pending_client_response'">

            <!-- Accept scope increment -->
            <div v-if="active.adjustment_kind === 'scope_increment'" class="flex flex-wrap gap-2">
              <button
                class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-signal px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
                :disabled="busy"
                @click="acceptScope"
              >
                <CheckCircle class="h-4 w-4" />
                {{ busy ? "Processing…" : `Accept — ${fmt(active.request_total_amount)}` }}
              </button>
              <button
                class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-ink disabled:opacity-60"
                :disabled="busy"
                @click="showCounter = !showCounter"
              >
                <RotateCcw class="h-4 w-4" />
                Counter offer
                <component :is="showCounter ? ChevronUp : ChevronDown" class="h-3.5 w-3.5" />
              </button>
              <button
                class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-rose-200 bg-rose-50 px-4 py-2 text-sm font-semibold text-berry disabled:opacity-60"
                :disabled="busy"
                @click="showDecline = !showDecline"
              >
                <XCircle class="h-4 w-4" />
                Decline
              </button>
            </div>

            <!-- Accept extra service -->
            <div v-else class="flex flex-wrap gap-2">
              <button
                class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-signal px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
                :disabled="busy"
                @click="acceptExtraService"
              >
                <CheckCircle class="h-4 w-4" />
                {{ busy ? "Processing…" : `Accept extra service` }}
              </button>
              <button
                class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-rose-200 bg-rose-50 px-4 py-2 text-sm font-semibold text-berry disabled:opacity-60"
                :disabled="busy"
                @click="showDecline = !showDecline"
              >
                <XCircle class="h-4 w-4" />
                Decline
              </button>
            </div>

            <!-- Counter form (scope only) -->
            <Transition name="slide-down">
              <div v-if="showCounter && active.adjustment_kind === 'scope_increment'" class="rounded-md border border-blue-200 bg-blue-50 p-4 space-y-3">
                <p class="text-sm font-medium text-blue-900">
                  Propose a different quantity
                  <span v-if="active.current_quantity !== null" class="font-normal text-blue-700">
                    (must be &gt; {{ active.current_quantity }}, ≤ {{ active.requested_quantity }})
                  </span>
                </p>
                <div class="flex gap-3">
                  <input
                    v-model.number="counterForm.countered_quantity"
                    type="number"
                    min="1"
                    class="focus-ring w-24 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
                    placeholder="Qty"
                  />
                  <input
                    v-model.trim="counterForm.note"
                    class="focus-ring min-w-0 flex-1 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
                    placeholder="Optional note to the writer"
                  />
                </div>
                <p v-if="counterError" class="text-xs text-berry">{{ counterError }}</p>
                <button
                  class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-ink px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
                  :disabled="busy || !counterForm.countered_quantity"
                  @click="submitCounter"
                >
                  {{ busy ? "Submitting…" : "Submit counter" }}
                </button>
              </div>
            </Transition>

            <!-- Decline form -->
            <Transition name="slide-down">
              <div v-if="showDecline" class="rounded-md border border-rose-200 bg-rose-50 p-4 space-y-3">
                <p class="text-sm font-medium text-berry">Reason for declining</p>
                <textarea
                  v-model.trim="declineReason"
                  class="focus-ring w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
                  rows="2"
                  placeholder="Briefly explain why you're declining this request"
                />
                <p v-if="declineError" class="text-xs text-berry">{{ declineError }}</p>
                <button
                  class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-berry px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
                  :disabled="busy || !declineReason.trim()"
                  @click="submitDecline"
                >
                  {{ busy ? "Declining…" : "Confirm decline" }}
                </button>
              </div>
            </Transition>
          </template>

          <!-- CLIENT: client_countered → waiting note -->
          <div
            v-else-if="canActAsClient && active.status === 'client_countered'"
            class="rounded-md border border-blue-100 bg-blue-50 px-4 py-3 text-sm text-blue-800"
          >
            Your counter has been sent. Waiting for the writer to respond.
          </div>

          <!-- CLIENT: funding_pending → go to payments -->
          <div
            v-else-if="canActAsClient && active.status === 'funding_pending'"
            class="flex items-center justify-between gap-3 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm"
          >
            <span class="text-amber-900">Payment required: <strong>{{ fmt(active.counter_total_amount ?? active.request_total_amount) }}</strong></span>
            <button
              class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-signal px-3 py-1.5 text-sm font-semibold text-white"
              @click="emit('go-to-payments')"
            >
              Pay now <ArrowRight class="h-3.5 w-3.5" />
            </button>
          </div>

          <!-- WRITER: funded + escalation available -->
          <template v-if="role === 'writer' && FUNDED.has(active.status) && active.applied_at && !active.escalated_after_counter">
            <div class="rounded-md border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-graphite">
              <p>Scope change applied. If the adjusted scope is not workable, you can escalate to staff.</p>
              <button
                class="mt-2 focus-ring inline-flex items-center gap-1.5 rounded-md border border-saffron/40 bg-saffron/10 px-3 py-1.5 text-xs font-semibold text-saffron"
                @click="showEscalate = !showEscalate"
              >
                <AlertTriangle class="h-3.5 w-3.5" />
                Escalate issue
                <component :is="showEscalate ? ChevronUp : ChevronDown" class="h-3.5 w-3.5" />
              </button>
            </div>

            <Transition name="slide-down">
              <div v-if="showEscalate" class="rounded-md border border-amber-200 bg-amber-50 p-4 space-y-3">
                <p class="text-sm font-medium text-amber-900">Describe the issue</p>
                <textarea
                  v-model.trim="escalateReason"
                  class="focus-ring w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
                  rows="3"
                  placeholder="Explain why the scope change as applied is not workable"
                />
                <p v-if="escalateError" class="text-xs text-berry">{{ escalateError }}</p>
                <button
                  class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-saffron px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
                  :disabled="busy || !escalateReason.trim()"
                  @click="submitEscalate"
                >
                  {{ busy ? "Submitting…" : "Submit escalation" }}
                </button>
              </div>
            </Transition>
          </template>

          <!-- STAFF: override -->
          <template v-if="isStaff(role) && CLIENT_ACTIONABLE.has(active.status)">
            <button
              class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-graphite"
              @click="showOverride = !showOverride"
            >
              Override price
              <component :is="showOverride ? ChevronUp : ChevronDown" class="h-3.5 w-3.5" />
            </button>

            <Transition name="slide-down">
              <div v-if="showOverride" class="rounded-md border border-slate-200 bg-slate-50 p-4 space-y-3">
                <p class="text-sm font-medium text-ink">Set override amount</p>
                <div class="flex gap-3">
                  <input
                    v-model.trim="overrideForm.amount"
                    type="number"
                    step="0.01"
                    class="focus-ring w-32 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
                    placeholder="$0.00"
                  />
                  <input
                    v-model.trim="overrideForm.notes"
                    class="focus-ring min-w-0 flex-1 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
                    placeholder="Notes for the client"
                  />
                </div>
                <p v-if="overrideError" class="text-xs text-berry">{{ overrideError }}</p>
                <button
                  class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-ink px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
                  :disabled="busy || !overrideForm.amount"
                  @click="submitOverride"
                >
                  {{ busy ? "Applying…" : "Apply override" }}
                </button>
              </div>
            </Transition>
          </template>

          <!-- STAFF: resolve escalation -->
          <template v-if="isStaff(role) && active.escalated_after_counter">
            <button
              class="focus-ring inline-flex items-center gap-1.5 rounded-md border border-rose-200 bg-rose-50 px-3 py-1.5 text-xs font-semibold text-berry"
              @click="showResolve = !showResolve"
            >
              Resolve escalation
              <component :is="showResolve ? ChevronUp : ChevronDown" class="h-3.5 w-3.5" />
            </button>

            <Transition name="slide-down">
              <div v-if="showResolve" class="rounded-md border border-rose-200 bg-rose-50 p-4 space-y-3">
                <p class="text-sm font-medium text-berry">Resolution details</p>
                <input
                  v-model.trim="resolveForm.resolution"
                  class="focus-ring w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
                  placeholder="Resolution decision (e.g. reassign, adjust scope further)"
                />
                <textarea
                  v-model.trim="resolveForm.note"
                  class="focus-ring w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
                  rows="2"
                  placeholder="Additional notes"
                />
                <p v-if="resolveError" class="text-xs text-berry">{{ resolveError }}</p>
                <button
                  class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-ink px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
                  :disabled="busy || !resolveForm.resolution.trim()"
                  @click="submitResolve"
                >
                  {{ busy ? "Resolving…" : "Confirm resolution" }}
                </button>
              </div>
            </Transition>
          </template>

          <!-- Terminal state -->
          <p
            v-if="TERMINAL.has(active.status)"
            class="text-sm text-graphite"
          >
            This adjustment was <strong>{{ statusLabel(active.status).toLowerCase() }}</strong>
            on {{ active.declined_at ? dateLabel(active.declined_at) : dateLabel(active.updated_at) }}.
          </p>

        </div>
      </div>
    </template>

    <!-- ── No active adjustment ──────────────────────────────── -->
    <div
      v-else-if="!loading && !canCreate"
      class="rounded-lg border border-slate-100 bg-slate-50 px-5 py-8 text-center text-sm text-graphite"
    >
      No scope change requests on this order.
      <template v-if="role === 'client'">
        If you need additional work, contact your support team.
      </template>
    </div>

    <!-- ── Client: rush delivery request ──────────────────────── -->
    <div v-if="canActAsClient && order" class="rounded-lg border border-amber-200 bg-amber-50">
      <button
        class="flex w-full items-center justify-between px-5 py-4 text-left"
        @click="showRushForm = !showRushForm"
      >
        <div class="flex items-center gap-2">
          <Zap class="h-4 w-4 text-amber-600" />
          <span class="text-base font-semibold text-ink">Request rush delivery</span>
          <span class="text-xs text-amber-700">(additional charge may apply)</span>
        </div>
        <component :is="showRushForm ? ChevronUp : ChevronDown" class="h-4 w-4 text-graphite" />
      </button>

      <Transition name="slide-down">
        <div v-if="showRushForm" class="border-t border-amber-200 p-5 space-y-4">
          <p class="text-sm text-amber-900">
            Moving your deadline to an earlier date may incur a rush surcharge based on
            our pricing bands. The exact amount will be shown after you submit.
          </p>

          <label class="block">
            <span class="text-sm font-medium text-graphite">New deadline <span class="text-rose-400">*</span></span>
            <input
              v-model="rushForm.new_deadline"
              type="datetime-local"
              required
              class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
            />
          </label>

          <label class="block">
            <span class="text-sm font-medium text-graphite">Reason</span>
            <input
              v-model="rushForm.reason"
              type="text"
              class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
            />
          </label>

          <p v-if="rushError" class="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-berry">
            {{ rushError }}
          </p>
          <p v-if="rushSuccess" class="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-signal">
            {{ rushSuccess }}
          </p>

          <div class="flex gap-2">
            <button
              class="focus-ring inline-flex items-center gap-2 rounded-md bg-amber-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
              type="button"
              :disabled="rushSubmitting || !rushForm.new_deadline"
              @click="submitRushRequest"
            >
              <Loader2 v-if="rushSubmitting" class="h-4 w-4 animate-spin" />
              <Zap v-else class="h-4 w-4" />
              {{ rushSubmitting ? "Submitting…" : "Submit rush request" }}
            </button>
            <button
              class="focus-ring rounded-md border border-slate-200 px-4 py-2 text-sm font-semibold text-ink"
              type="button"
              @click="showRushForm = false; rushError = ''"
            >
              Cancel
            </button>
          </div>
        </div>
      </Transition>
    </div>

    <!-- ── Create form (writer / staff) ─────────────────────── -->
    <div v-if="canCreate" class="rounded-lg border border-slate-200 bg-white">
      <button
        class="flex w-full items-center justify-between px-5 py-4 text-left"
        @click="showCreateForm = !showCreateForm"
      >
        <div class="flex items-center gap-2">
          <Plus class="h-4 w-4 text-signal" />
          <span class="text-base font-semibold text-ink">Request scope change</span>
          <span v-if="active && !TERMINAL.has(active.status)" class="text-xs text-graphite">(another request is active)</span>
        </div>
        <component :is="showCreateForm ? ChevronUp : ChevronDown" class="h-4 w-4 text-graphite" />
      </button>

      <Transition name="slide-down">
        <div v-if="showCreateForm" class="border-t border-slate-200 p-5 space-y-5">

          <!-- Kind toggle -->
          <div class="flex flex-wrap gap-2">
            <button
              class="focus-ring rounded-md border px-3 py-1.5 text-sm font-medium transition-colors"
              :class="createKind === 'scope' ? 'border-signal bg-signal/10 text-signal' : 'border-slate-200 text-graphite'"
              @click="createKind = 'scope'"
            >
              Scope increment
            </button>
            <button
              class="focus-ring rounded-md border px-3 py-1.5 text-sm font-medium transition-colors"
              :class="createKind === 'extra' ? 'border-signal bg-signal/10 text-signal' : 'border-slate-200 text-graphite'"
              @click="createKind = 'extra'"
            >
              Extra service
            </button>
            <button
              v-if="role === 'writer'"
              class="focus-ring rounded-md border px-3 py-1.5 text-sm font-medium transition-colors"
              :class="createKind === 'deadline' ? 'border-signal bg-signal/10 text-signal' : 'border-slate-200 text-graphite'"
              @click="createKind = 'deadline'"
            >
              Deadline extension
            </button>
          </div>

          <!-- ── Scope increment form ── -->
          <form v-if="createKind === 'scope'" class="space-y-4" @submit.prevent="submitScope">

            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <label class="block">
                <span class="text-sm font-medium text-graphite">Adjustment type <span class="text-rose-400">*</span></span>
                <select
                  v-model="scopeForm.adjustment_type"
                  class="focus-ring mt-1.5 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                >
                  <option v-for="t in SCOPE_TYPES" :key="t.value" :value="t.value">
                    {{ t.label }}
                  </option>
                </select>
              </label>

              <label class="block">
                <span class="text-sm font-medium text-graphite">
                  Requested quantity <span class="text-rose-400">*</span>
                  <span v-if="currentQuantity !== null" class="ml-1 font-normal text-graphite/70">
                    (current: {{ currentQuantity }})
                  </span>
                </span>
                <input
                  v-model.number="scopeForm.requested_quantity"
                  type="number"
                  min="1"
                  class="focus-ring mt-1.5 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                  placeholder="Total quantity after change"
                />
              </label>
            </div>

            <label class="block">
              <span class="text-sm font-medium text-graphite">Title <span class="text-rose-400">*</span></span>
              <input
                v-model.trim="scopeForm.title"
                class="focus-ring mt-1.5 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                placeholder="e.g. Client requested 5 additional pages"
                maxlength="200"
              />
            </label>

            <label class="block">
              <span class="text-sm font-medium text-graphite">Description</span>
              <textarea
                v-model.trim="scopeForm.description"
                class="focus-ring mt-1.5 min-h-20 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                placeholder="Describe exactly what the additional scope covers"
              />
            </label>

            <label class="block">
              <span class="text-sm font-medium text-graphite">Justification (internal)</span>
              <textarea
                v-model.trim="scopeForm.writer_justification"
                class="focus-ring mt-1.5 min-h-16 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                placeholder="Internal note explaining why this change is out of scope"
              />
            </label>

            <p v-if="createError" class="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-berry">
              {{ createError }}
            </p>

            <button
              type="submit"
              class="focus-ring inline-flex h-10 items-center gap-2 rounded-md bg-ink px-5 text-sm font-semibold text-white disabled:opacity-60"
              :disabled="busy || !scopeForm.title || !scopeForm.requested_quantity"
            >
              <Plus class="h-4 w-4" />
              {{ busy ? "Submitting…" : "Submit scope request" }}
            </button>
          </form>

          <!-- ── Extra service form ── -->
          <form v-else-if="createKind === 'extra'" class="space-y-4" @submit.prevent="submitExtra">

            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <label class="block">
                <span class="text-sm font-medium text-graphite">Service code <span class="text-rose-400">*</span></span>
                <input
                  v-model.trim="extraForm.extra_service_code"
                  class="focus-ring mt-1.5 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                  placeholder="e.g. plagiarism_check, progressive_delivery"
                  maxlength="100"
                />
              </label>

              <label class="block">
                <span class="text-sm font-medium text-graphite">Title <span class="text-rose-400">*</span></span>
                <input
                  v-model.trim="extraForm.title"
                  class="focus-ring mt-1.5 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                  placeholder="Client-facing name for this service"
                  maxlength="200"
                />
              </label>
            </div>

            <label class="block">
              <span class="text-sm font-medium text-graphite">Description</span>
              <textarea
                v-model.trim="extraForm.description"
                class="focus-ring mt-1.5 min-h-20 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                placeholder="What does this extra service include?"
              />
            </label>

            <label class="block">
              <span class="text-sm font-medium text-graphite">Justification (internal)</span>
              <textarea
                v-model.trim="extraForm.writer_justification"
                class="focus-ring mt-1.5 min-h-16 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
                placeholder="Internal note"
              />
            </label>

            <p v-if="createError" class="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-berry">
              {{ createError }}
            </p>

            <button
              type="submit"
              class="focus-ring inline-flex h-10 items-center gap-2 rounded-md bg-ink px-5 text-sm font-semibold text-white disabled:opacity-60"
              :disabled="busy || !extraForm.extra_service_code || !extraForm.title"
            >
              <Plus class="h-4 w-4" />
              {{ busy ? "Submitting…" : "Submit extra service" }}
            </button>
          </form>

          <!-- ── Deadline extension form (writer only) ── -->
          <form v-else-if="createKind === 'deadline'" class="space-y-4" @submit.prevent="submitDeadlineExtension">
            <p class="text-sm text-graphite">
              Request more time to complete this order. The client will be notified and must approve.
            </p>

            <label class="block">
              <span class="text-sm font-medium text-graphite">New requested deadline <span class="text-rose-400">*</span></span>
              <input
                v-model="deadlineForm.requested_deadline"
                type="datetime-local"
                required
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
              />
            </label>

            <label class="block">
              <span class="text-sm font-medium text-graphite">Reason for extension <span class="text-rose-400">*</span></span>
              <textarea
                v-model="deadlineForm.reason"
                rows="3"
                required
                placeholder="Explain why you need more time (this will be shown to the client)."
                class="focus-ring mt-1 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
              />
            </label>

            <label class="block">
              <span class="text-sm font-medium text-graphite">Internal note <span class="text-slate-400">(optional)</span></span>
              <input
                v-model="deadlineForm.writer_justification"
                type="text"
                placeholder="Any extra context for the review team."
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
              />
            </label>

            <p v-if="createError" class="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-berry">
              {{ createError }}
            </p>

            <button
              class="focus-ring inline-flex items-center gap-2 rounded-md bg-signal px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
              type="submit"
              :disabled="busy || !deadlineForm.requested_deadline || !deadlineForm.reason"
            >
              <Loader2 v-if="busy" class="h-4 w-4 animate-spin" />
              <Plus v-else class="h-4 w-4" />
              {{ busy ? "Submitting…" : "Request deadline extension" }}
            </button>
          </form>

        </div>
      </Transition>
    </div>

    <!-- History note -->
    <p class="text-center text-xs text-graphite">
      Older scope change requests appear in the
      <button class="font-medium text-signal hover:underline" @click="$emit('go-to-timeline')">Timeline</button>.
    </p>

  </div>
</template>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.18s ease;
  overflow: hidden;
}
.slide-down-enter-from,
.slide-down-leave-to {
  max-height: 0;
  opacity: 0;
}
.slide-down-enter-to,
.slide-down-leave-from {
  max-height: 600px;
  opacity: 1;
}
</style>

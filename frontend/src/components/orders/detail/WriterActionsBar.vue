<script setup lang="ts">
import { computed, ref } from "vue";
import {
  AlertTriangle,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  ClipboardCheck,
  Files,
  ShieldAlert,
  XCircle,
} from "@lucide/vue";
import type { OrderLifecycle, OrderSummary } from "@/types/orders";
import { writerApi } from "@/api/writer";
import { ordersApi } from "@/api/orders";
import { useUiStore } from "@/stores/ui";
import { deadlineCountdown } from "./types";

// ─── Props & emits ────────────────────────────────────────────────────────────

const props = defineProps<{
  orderId: string;
  order: OrderSummary | null;
  lifecycle: OrderLifecycle | null;
}>();

const emit = defineEmits<{
  refresh: [];
  "go-to-files": [];
}>();

// ─── Shared ───────────────────────────────────────────────────────────────────

const ui = useUiStore();
const busy = ref<string | null>(null);
const feedback = ref<{ ok: boolean; msg: string } | null>(null);

// ─── Derived ──────────────────────────────────────────────────────────────────

const status = computed(() => props.order?.status ?? "");

const isPendingAcceptance = computed(() =>
  status.value === "pending_writer_acceptance",
);

const isActiveWork = computed(() =>
  ["in_progress", "revision_requested"].includes(status.value),
);

const writerDeadline = computed(() => props.order?.writer_deadline ?? null);
const compensation = computed(() => {
  const v = props.order?.writer_compensation;
  if (!v) return null;
  const n = Number(v);
  return isNaN(n) ? String(v) : `$${n.toFixed(2)}`;
});

// ─── Assignment acceptance ────────────────────────────────────────────────────

const showRejectForm = ref(false);
const rejectReason = ref("");
const rejectError = ref("");

async function acceptAssignment() {
  busy.value = "accept";
  feedback.value = null;
  try {
    await writerApi.acceptAssignment(props.orderId);
    ui.toast("Assignment accepted — order is now in progress.", "success");
    emit("refresh");
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    ui.toast(detail ?? "Could not accept assignment.", "error");
  } finally {
    busy.value = null;
  }
}

async function rejectAssignment() {
  if (!rejectReason.value.trim()) return;
  busy.value = "reject";
  rejectError.value = "";
  try {
    await writerApi.rejectAssignment(props.orderId, rejectReason.value.trim());
    ui.toast("Assignment declined. The order has been returned to the pool.", "success");
    emit("refresh");
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    rejectError.value = detail ?? "Could not decline assignment.";
  } finally {
    busy.value = null;
  }
}

// ─── Active-work actions ─────────────────────────────────────────────────────

const showDisputeForm = ref(false);
const disputeReason = ref("");
const disputeError = ref("");

async function openDispute() {
  if (!disputeReason.value.trim()) return;
  busy.value = "dispute";
  disputeError.value = "";
  try {
    await ordersApi.raiseDispute(props.orderId, disputeReason.value.trim());
    feedback.value = { ok: true, msg: "Dispute opened. Our support team has been notified." };
    showDisputeForm.value = false;
    disputeReason.value = "";
    emit("refresh");
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    disputeError.value = detail ?? "Could not open dispute.";
  } finally {
    busy.value = null;
  }
}
</script>

<template>
  <!-- Nothing to show for this writer in this state -->
  <template v-if="!isPendingAcceptance && !isActiveWork" />

  <!-- ── Assignment acceptance gate ─────────────────────────────────── -->
  <div
    v-else-if="isPendingAcceptance"
    class="overflow-hidden rounded-xl border-2 border-signal bg-white shadow-sm"
  >
    <!-- Accent header -->
    <div class="bg-signal px-5 py-3">
      <div class="flex items-center gap-2">
        <ClipboardCheck class="h-4 w-4 text-white" />
        <span class="text-sm font-semibold text-white">Direct assignment offer</span>
      </div>
    </div>

    <div class="px-5 py-4 space-y-4">
      <p class="text-sm text-graphite">
        You have been directly assigned to this order by our operations team.
        Please accept or decline before the order is reassigned.
      </p>

      <!-- Quick stats -->
      <div class="grid grid-cols-2 gap-3 sm:grid-cols-3">
        <div v-if="writerDeadline" class="rounded-md bg-slate-50 px-3 py-2.5">
          <p class="text-xs font-medium text-graphite">Your deadline</p>
          <p class="mt-0.5 text-sm font-semibold text-ink">{{ deadlineCountdown(writerDeadline) }}</p>
        </div>
        <div v-if="compensation" class="rounded-md bg-slate-50 px-3 py-2.5">
          <p class="text-xs font-medium text-graphite">Compensation</p>
          <p class="mt-0.5 text-sm font-semibold text-ink">{{ compensation }}</p>
        </div>
        <div v-if="order?.base_quantity" class="rounded-md bg-slate-50 px-3 py-2.5">
          <p class="text-xs font-medium text-graphite">Scope</p>
          <p class="mt-0.5 text-sm font-semibold text-ink">{{ order.base_quantity }} {{ order.unit_type ?? "pages" }}</p>
        </div>
      </div>

      <!-- Action buttons -->
      <div class="flex flex-wrap gap-3">
        <button
          class="focus-ring inline-flex h-10 items-center gap-2 rounded-md bg-signal px-5 text-sm font-semibold text-white disabled:opacity-60"
          :disabled="busy !== null"
          @click="acceptAssignment"
        >
          <CheckCircle2 class="h-4 w-4" />
          {{ busy === "accept" ? "Accepting…" : "Accept assignment" }}
        </button>
        <button
          class="focus-ring inline-flex h-10 items-center gap-2 rounded-md border border-slate-200 px-4 text-sm font-medium text-graphite hover:border-rose-200 hover:bg-rose-50 hover:text-berry disabled:opacity-60"
          :disabled="busy !== null"
          @click="showRejectForm = !showRejectForm"
        >
          <XCircle class="h-4 w-4" />
          Decline
          <component :is="showRejectForm ? ChevronUp : ChevronDown" class="h-3.5 w-3.5" />
        </button>
      </div>

      <!-- Reject form -->
      <Transition name="slide-down">
        <div v-if="showRejectForm" class="rounded-md border border-rose-200 bg-rose-50 p-4 space-y-3">
          <p class="text-sm font-medium text-berry">Reason for declining <span class="font-normal text-rose-600">(required)</span></p>
          <textarea
            v-model.trim="rejectReason"
            class="focus-ring w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm resize-none"
            rows="2"
            placeholder="Let us know why you can't take this order so we can reassign it quickly"
          />
          <p v-if="rejectError" class="text-xs text-berry">{{ rejectError }}</p>
          <div class="flex gap-2">
            <button
              class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-berry px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
              :disabled="busy !== null || !rejectReason.trim()"
              @click="rejectAssignment"
            >
              {{ busy === "reject" ? "Declining…" : "Confirm decline" }}
            </button>
            <button
              class="focus-ring inline-flex items-center rounded-md border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-graphite hover:bg-slate-50"
              @click="showRejectForm = false; rejectReason = ''; rejectError = ''"
            >
              Cancel
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </div>

  <!-- ── Active-work action bar ─────────────────────────────────────── -->
  <div
    v-else-if="isActiveWork"
    class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden"
  >
    <!-- Bar header -->
    <div class="flex items-center justify-between border-b border-slate-100 px-5 py-3">
      <div class="flex items-center gap-2">
        <Files class="h-4 w-4 text-signal" />
        <span class="text-sm font-semibold text-ink">Writer actions</span>
        <span
          class="rounded-full px-2 py-0.5 text-xs font-semibold"
          :class="status === 'revision_requested' ? 'bg-amber-100 text-amber-700' : 'bg-blue-100 text-blue-700'"
        >
          {{ status === "revision_requested" ? "Revision requested" : "In progress" }}
        </span>
      </div>
    </div>

    <!-- Feedback bar -->
    <div
      v-if="feedback"
      class="flex items-center gap-2 border-b px-5 py-2.5 text-sm font-medium"
      :class="feedback.ok ? 'border-emerald-200 bg-emerald-50 text-emerald-800' : 'border-rose-200 bg-rose-50 text-rose-800'"
    >
      <CheckCircle2 v-if="feedback.ok" class="h-4 w-4 shrink-0" />
      <AlertTriangle v-else class="h-4 w-4 shrink-0" />
      {{ feedback.msg }}
      <button class="ml-auto text-xs opacity-60 hover:opacity-100" @click="feedback = null">✕</button>
    </div>

    <div class="px-5 py-4 space-y-3">
      <!-- Action row -->
      <div class="flex flex-wrap gap-2">

        <!-- Primary: submit work via files tab -->
        <button
          class="focus-ring inline-flex items-center gap-1.5 rounded-lg border border-signal bg-signal px-3 py-1.5 text-xs font-semibold text-white hover:bg-signal/90"
          @click="emit('go-to-files')"
        >
          <Files class="h-3.5 w-3.5" />
          Upload &amp; submit work
        </button>

        <!-- Dispute -->
        <button
          class="focus-ring inline-flex items-center gap-1.5 rounded-lg border border-rose-300 bg-rose-50 px-3 py-1.5 text-xs font-semibold text-rose-800 hover:bg-rose-100"
          @click="showDisputeForm = !showDisputeForm"
        >
          <ShieldAlert class="h-3.5 w-3.5" />
          Open dispute
          <component :is="showDisputeForm ? ChevronUp : ChevronDown" class="h-3 w-3" />
        </button>

      </div>

      <!-- Dispute inline form -->
      <Transition name="slide-down">
        <div v-if="showDisputeForm" class="rounded-lg border border-rose-200 bg-rose-50 p-4 space-y-3">
          <p class="text-xs font-semibold text-ink">Describe the issue <span class="text-rose-500">*</span></p>
          <textarea
            v-model.trim="disputeReason"
            rows="3"
            class="focus-ring w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm resize-none"
            placeholder="Explain the problem clearly — this is recorded and visible to the support team and the client."
          />
          <p v-if="disputeError" class="text-xs text-berry">{{ disputeError }}</p>
          <div class="flex gap-2">
            <button
              class="focus-ring inline-flex items-center gap-1.5 rounded-md bg-berry px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-60"
              :disabled="busy !== null || !disputeReason.trim()"
              @click="openDispute"
            >
              {{ busy === "dispute" ? "Opening…" : "Open dispute" }}
            </button>
            <button
              class="focus-ring inline-flex items-center rounded-md border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-graphite hover:bg-slate-50"
              @click="showDisputeForm = false; disputeReason = ''; disputeError = ''"
            >
              Cancel
            </button>
          </div>
        </div>
      </Transition>

    </div>
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
  max-height: 400px;
  opacity: 1;
}
</style>

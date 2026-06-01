<template>
  <div class="space-y-4">

    <!-- Status banner -->
    <div
      class="flex items-center gap-3 rounded-xl border px-5 py-4"
      :class="banner.class"
    >
      <component :is="banner.icon" class="size-5 shrink-0" />
      <div class="min-w-0">
        <p class="font-semibold text-sm">{{ banner.title }}</p>
        <p class="text-xs mt-0.5 opacity-80">{{ banner.body }}</p>
      </div>
    </div>

    <!-- Return-to-writer feedback note (visible to writer when work was sent back) -->
    <div
      v-if="order.qa_returned_at && order.qa_review_note && role === 'writer'"
      class="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3"
    >
      <RotateCcw class="mt-0.5 size-4 shrink-0 text-amber-600" />
      <div class="min-w-0">
        <p class="text-sm font-semibold text-amber-900">Work returned by QA</p>
        <p class="mt-1 text-sm text-amber-800">{{ order.qa_review_note }}</p>
        <p class="mt-1 text-xs text-amber-700">Returned {{ new Date(order.qa_returned_at).toLocaleDateString() }}</p>
      </div>
    </div>

    <!-- QA approved note (visible to all when approved) -->
    <div
      v-if="order.qa_approved_at && order.qa_review_note"
      class="flex items-start gap-3 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3"
    >
      <CheckCircle2 class="mt-0.5 size-4 shrink-0 text-emerald-600" />
      <div class="min-w-0">
        <p class="text-sm font-semibold text-emerald-900">QA approved</p>
        <p v-if="order.qa_review_note" class="mt-1 text-sm text-emerald-800">{{ order.qa_review_note }}</p>
      </div>
    </div>

    <!-- QA steps timeline -->
    <div class="rounded-lg border border-slate-200 bg-white overflow-hidden">
      <div class="border-b border-slate-200 px-5 py-4">
        <h2 class="text-sm font-semibold text-ink">QA Pipeline</h2>
      </div>
      <ol class="divide-y divide-slate-100">
        <li
          v-for="step in steps"
          :key="step.key"
          class="flex items-center gap-4 px-5 py-3"
        >
          <span
            class="flex size-6 shrink-0 items-center justify-center rounded-full text-xs font-bold"
            :class="step.state === 'done'
              ? 'bg-emerald-100 text-emerald-700'
              : step.state === 'active'
                ? 'bg-amber-100 text-amber-700'
                : 'bg-slate-100 text-slate-400'"
          >
            <CheckCircle2 v-if="step.state === 'done'" class="size-4" />
            <Loader2 v-else-if="step.state === 'active'" class="size-4 animate-spin" />
            <span v-else>{{ step.num }}</span>
          </span>
          <div class="min-w-0 flex-1">
            <p class="text-sm font-medium text-ink">{{ step.label }}</p>
            <p v-if="step.note" class="text-xs text-graphite mt-0.5">{{ step.note }}</p>
          </div>
          <span
            class="shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold capitalize"
            :class="step.state === 'done'
              ? 'bg-emerald-100 text-emerald-700'
              : step.state === 'active'
                ? 'bg-amber-100 text-amber-700'
                : 'bg-slate-100 text-slate-400'"
          >
            {{ step.state === 'done' ? 'Done' : step.state === 'active' ? 'Active' : 'Pending' }}
          </span>
        </li>
      </ol>
    </div>

    <!-- Staff action panel (admin/editor only) -->
    <div v-if="canAct" class="rounded-lg border border-slate-200 bg-white p-5 space-y-4">
      <h2 class="text-sm font-semibold text-ink">QA Actions</h2>

      <!-- Return to writer — needs a notes field -->
      <div v-if="showReturnForm" class="space-y-3">
        <label class="block text-sm font-medium text-ink">
          Return notes <span class="text-rose-500">*</span>
        </label>
        <textarea
          v-model="returnNotes"
          rows="3"
          placeholder="Explain what needs to be corrected before resubmission…"
          class="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus-ring resize-none"
        />
        <div class="flex gap-2">
          <button
            class="flex-1 rounded-lg bg-amber-500 px-4 py-2 text-sm font-semibold text-white hover:bg-amber-600 disabled:opacity-60"
            :disabled="acting || !returnNotes.trim()"
            @click="doReturn"
          >
            <span v-if="acting">Returning…</span>
            <span v-else>Confirm Return to Writer</span>
          </button>
          <button
            class="rounded-lg border border-slate-200 px-4 py-2 text-sm text-graphite hover:text-ink"
            @click="showReturnForm = false"
          >
            Cancel
          </button>
        </div>
      </div>

      <div v-else class="flex flex-wrap gap-2">
        <!-- Submit for QA — available when order is in_progress/submitted -->
        <button
          v-if="canSubmitForQA"
          class="inline-flex items-center gap-1.5 rounded-lg bg-ink px-4 py-2 text-sm font-semibold text-white hover:bg-ink/90 disabled:opacity-60"
          :disabled="acting"
          @click="doSubmit"
        >
          <Send class="size-3.5" />
          Submit for QA
        </button>

        <!-- Approve — available when in qa_review -->
        <button
          v-if="canApprove"
          class="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-60"
          :disabled="acting"
          @click="doApprove"
        >
          <CheckCircle2 class="size-3.5" />
          Approve for Delivery
        </button>

        <!-- Return to writer — available when in qa_review -->
        <button
          v-if="canReturn"
          class="inline-flex items-center gap-1.5 rounded-lg border border-amber-300 bg-amber-50 px-4 py-2 text-sm font-semibold text-amber-800 hover:bg-amber-100 disabled:opacity-60"
          :disabled="acting"
          @click="showReturnForm = true"
        >
          <RotateCcw class="size-3.5" />
          Return to Writer
        </button>
      </div>

      <p v-if="actionError" class="rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
        {{ actionError }}
      </p>
      <p v-if="actionSuccess" class="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
        {{ actionSuccess }}
      </p>
    </div>

  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { CheckCircle2, Loader2, RotateCcw, Send } from "@lucide/vue";
import type { UserRole } from "@/types/roles";
import type { OrderSummary } from "@/types/orders";
import { ordersApi } from "@/api/orders";
import { useAuthStore } from "@/stores/auth";

const props = defineProps<{
  orderId: string;
  order: OrderSummary;
  role: UserRole;
}>();

const emit = defineEmits<{ (e: "refresh"): void }>();

const auth = useAuthStore();

const acting = ref(false);
const actionError = ref("");
const actionSuccess = ref("");
const showReturnForm = ref(false);
const returnNotes = ref("");

const STATUS = computed(() => props.order.status ?? "");

const isReviewer = computed(() => props.role === "admin" || props.role === "superadmin" || props.role === "editor");
const canAct = computed(() => isReviewer.value || props.role === "writer");
const canSubmitForQA = computed(() => STATUS.value === "in_progress" && (props.role === "writer" || isReviewer.value));
const canApprove = computed(() => STATUS.value === "qa_review" && isReviewer.value);
const canReturn = computed(() => STATUS.value === "qa_review" && isReviewer.value);

// ── Banner ────────────────────────────────────────────────────────────────────
const STATUS_BANNER: Record<string, { title: string; body: string; class: string; icon: unknown }> = {
  qa_review: { title: "In QA Review", body: "This order is being reviewed for quality and accuracy.", class: "border-amber-200 bg-amber-50 text-amber-900", icon: Loader2 },
  submitted: { title: "Submitted for Review", body: "Writer has submitted the work; awaiting QA assignment.", class: "border-blue-200 bg-blue-50 text-blue-900", icon: Send },
  completed: { title: "QA Approved", body: "This order passed QA and was delivered to the client.", class: "border-emerald-200 bg-emerald-50 text-emerald-900", icon: CheckCircle2 },
  under_editing:{ title: "Under Editing", body: "The work has been passed to an editor for final polish.", class: "border-cyan-200 bg-cyan-50 text-cyan-900", icon: Loader2 },
};

const banner = computed(() => {
  return STATUS_BANNER[STATUS.value] ?? {
    title: `Status: ${STATUS.value.replace(/_/g, " ")}`,
    body: "QA review has not started yet.",
    class: "border-slate-200 bg-slate-50 text-slate-700",
    icon: CheckCircle2,
  };
});

// ── Pipeline steps ────────────────────────────────────────────────────────────
type StepState = "done" | "active" | "pending";

interface Step {
  key: string;
  num: number;
  label: string;
  note?: string;
  state: StepState;
}

function stepState(doneStatuses: string[], activeStatuses: string[]): StepState {
  if (doneStatuses.includes(STATUS.value)) return "done";
  if (activeStatuses.includes(STATUS.value)) return "active";
  return "pending";
}

const steps = computed<Step[]>(() => [
  {
    key: "writing",
    num: 1,
    label: "Writing in progress",
    state: stepState(["submitted", "qa_review", "under_editing", "completed"], ["in_progress", "revision_requested"]),
  },
  {
    key: "submission",
    num: 2,
    label: "Submitted for QA",
    state: stepState(["qa_review", "under_editing", "completed"], ["submitted"]),
  },
  {
    key: "qa",
    num: 3,
    label: "QA Review",
    note: STATUS.value === "qa_review" ? "Reviewer is checking quality, citations, and rubric compliance." : undefined,
    state: stepState(["under_editing", "completed"], ["qa_review"]),
  },
  {
    key: "editing",
    num: 4,
    label: "Editing / final polish",
    state: stepState(["completed"], ["under_editing"]),
  },
  {
    key: "delivery",
    num: 5,
    label: "Delivered to client",
    state: stepState(["completed"], []),
  },
]);

// ── Actions ───────────────────────────────────────────────────────────────────
async function doSubmit() {
  acting.value = true;
  actionError.value = "";
  actionSuccess.value = "";
  try {
    if (auth.isPreviewSession) { actionSuccess.value = "Preview: submitted for QA."; return; }
    await ordersApi.qaSubmit(props.orderId);
    actionSuccess.value = "Order submitted for QA.";
    emit("refresh");
  } catch {
    actionError.value = "Failed to submit for QA. Please try again.";
  } finally {
    acting.value = false;
  }
}

async function doApprove() {
  acting.value = true;
  actionError.value = "";
  actionSuccess.value = "";
  try {
    if (auth.isPreviewSession) { actionSuccess.value = "Preview: approved."; return; }
    await ordersApi.qaApprove(props.orderId);
    actionSuccess.value = "Order approved and marked for delivery.";
    emit("refresh");
  } catch {
    actionError.value = "Failed to approve. Please try again.";
  } finally {
    acting.value = false;
  }
}

async function doReturn() {
  if (!returnNotes.value.trim()) return;
  acting.value = true;
  actionError.value = "";
  actionSuccess.value = "";
  try {
    if (auth.isPreviewSession) { actionSuccess.value = "Preview: returned to writer."; showReturnForm.value = false; return; }
    await ordersApi.qaReturn(props.orderId, returnNotes.value.trim());
    actionSuccess.value = "Order returned to writer with notes.";
    showReturnForm.value = false;
    returnNotes.value = "";
    emit("refresh");
  } catch {
    actionError.value = "Failed to return order. Please try again.";
  } finally {
    acting.value = false;
  }
}
</script>

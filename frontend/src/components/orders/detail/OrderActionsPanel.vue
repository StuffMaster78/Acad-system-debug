<template>
  <div class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">

    <!-- Panel header -->
    <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
      <div class="flex items-center gap-3">
        <Zap class="h-4 w-4 text-signal" />
        <h2 class="text-sm font-semibold text-ink">Staff Actions</h2>
        <span class="rounded-full px-2 py-0.5 text-xs font-semibold capitalize" :class="statusClass(order.status)">
          {{ humanStatus(order.status) }}
        </span>
        <span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold capitalize text-slate-600">
          {{ role }}
        </span>
      </div>
      <button
        class="inline-flex items-center gap-1 text-xs font-medium text-graphite hover:text-ink"
        @click="showGuide = !showGuide"
      >
        <BookOpen class="h-3.5 w-3.5" />
        {{ showGuide ? "Hide guide" : "State guide" }}
      </button>
    </div>

    <!-- Feedback bar -->
    <div v-if="feedback" :class="feedback.ok ? 'bg-emerald-50 border-emerald-200 text-emerald-800' : 'bg-rose-50 border-rose-200 text-rose-800'"
      class="border-b px-5 py-2.5 text-sm font-medium flex items-center gap-2">
      <CheckCircle2 v-if="feedback.ok" class="h-4 w-4 shrink-0" />
      <AlertCircle v-else class="h-4 w-4 shrink-0" />
      {{ feedback.msg }}
      <button class="ml-auto text-xs opacity-60 hover:opacity-100" @click="feedback = null">✕</button>
    </div>

    <!-- Primary actions -->
    <div class="px-5 py-4 space-y-3">

      <!-- No actions available message -->
      <p v-if="!availableActions.length && !canHold && !canReleaseHold && !canReassign"
        class="text-sm text-graphite py-2">
        No actions available in the current state.
      </p>

      <!-- Action button grid -->
      <div v-else class="flex flex-wrap gap-2">

        <!-- submit_for_qa -->
        <ActionButton
          v-if="has('submit_for_qa')"
          icon="send"
          label="Submit for QA"
          variant="primary"
          :loading="busy === 'submit_for_qa'"
          :pending="pendingConfirm === 'submit_for_qa'"
          @click="setPending('submit_for_qa')"
          @confirm="exec('submit_for_qa')"
          @cancel="pendingConfirm = null"
        />

        <!-- approve_delivery (qa_review → submitted) -->
        <ActionButton
          v-if="has('approve_delivery')"
          icon="check"
          label="Approve delivery"
          variant="primary"
          :loading="busy === 'approve_delivery'"
          :pending="pendingConfirm === 'approve_delivery'"
          @click="setPending('approve_delivery')"
          @confirm="exec('approve_delivery')"
          @cancel="pendingConfirm = null"
        />

        <!-- return_to_writer (qa_review → in_progress) -->
        <button
          v-if="has('return_to_writer')"
          class="focus-ring inline-flex items-center gap-1.5 rounded-lg border border-amber-300 bg-amber-50 px-3 py-1.5 text-xs font-semibold text-amber-800 hover:bg-amber-100"
          @click="openForm('return_to_writer')"
        >
          <RotateCcw class="h-3.5 w-3.5" /> Return to writer
        </button>

        <!-- approve_order (completed → approved) -->
        <ActionButton
          v-if="has('approve_order')"
          icon="check-circle"
          label="Approve order"
          variant="primary"
          :loading="busy === 'approve_order'"
          :pending="pendingConfirm === 'approve_order'"
          @click="setPending('approve_order')"
          @confirm="exec('approve_order')"
          @cancel="pendingConfirm = null"
        />

        <!-- place_on_hold -->
        <button
          v-if="canHold"
          class="focus-ring inline-flex items-center gap-1.5 rounded-lg border border-amber-300 bg-amber-50 px-3 py-1.5 text-xs font-semibold text-amber-800 hover:bg-amber-100"
          @click="openForm('hold')"
        >
          <PauseCircle class="h-3.5 w-3.5" /> Place on hold
        </button>

        <!-- release_hold -->
        <ActionButton
          v-if="canReleaseHold"
          icon="play"
          label="Release hold"
          variant="success"
          :loading="busy === 'release_hold'"
          :pending="pendingConfirm === 'release_hold'"
          @click="setPending('release_hold')"
          @confirm="exec('release_hold')"
          @cancel="pendingConfirm = null"
        />

        <!-- raise_dispute -->
        <button
          v-if="has('raise_dispute')"
          class="focus-ring inline-flex items-center gap-1.5 rounded-lg border border-rose-300 bg-rose-50 px-3 py-1.5 text-xs font-semibold text-rose-800 hover:bg-rose-100"
          @click="openForm('dispute')"
        >
          <AlertTriangle class="h-3.5 w-3.5" /> Open dispute
        </button>

        <!-- cancel_order -->
        <button
          v-if="has('cancel_order')"
          class="focus-ring inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-rose-50 hover:border-rose-300 hover:text-rose-700"
          @click="openForm('cancel')"
        >
          <XCircle class="h-3.5 w-3.5" /> Cancel order
        </button>

        <!-- archive_order -->
        <ActionButton
          v-if="has('archive_order')"
          icon="archive"
          label="Archive"
          variant="neutral"
          :loading="busy === 'archive_order'"
          :pending="pendingConfirm === 'archive_order'"
          @click="setPending('archive_order')"
          @confirm="exec('archive_order')"
          @cancel="pendingConfirm = null"
        />

        <!-- request_reassignment -->
        <button
          v-if="canReassign"
          class="focus-ring inline-flex items-center gap-1.5 rounded-lg border border-indigo-300 bg-indigo-50 px-3 py-1.5 text-xs font-semibold text-indigo-800 hover:bg-indigo-100"
          @click="openForm('reassign')"
        >
          <UserRoundCog class="h-3.5 w-3.5" /> Reassign writer
        </button>

        <!-- manual_mark_paid -->
        <button
          v-if="has('manual_mark_paid')"
          class="focus-ring inline-flex items-center gap-1.5 rounded-lg border border-emerald-300 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-800 hover:bg-emerald-100"
          @click="openForm('manual_mark_paid')"
        >
          <CircleDollarSign class="h-3.5 w-3.5" /> Verify payment
        </button>

      </div>

      <!-- Inline forms -->
      <Transition name="slide-down">
        <div v-if="activeForm" class="rounded-lg border border-slate-200 bg-slate-50 p-4 space-y-3">

          <!-- return_to_writer form -->
          <template v-if="activeForm === 'return_to_writer'">
            <p class="text-xs font-semibold text-ink">Return reason <span class="text-rose-500">*</span></p>
            <textarea v-model="formInput" rows="2"
              class="focus-ring w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm resize-none"
              placeholder="Explain what the writer must fix…" />
            <FormActions label="Return to writer" :loading="busy === 'return_to_writer'" :disabled="!formInput.trim()" @submit="exec('return_to_writer')" @cancel="closeForm" />
          </template>

          <!-- hold form -->
          <template v-if="activeForm === 'hold'">
            <p class="text-xs font-semibold text-ink">Hold reason <span class="text-rose-500">*</span></p>
            <textarea v-model="formInput" rows="2"
              class="focus-ring w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm resize-none"
              placeholder="Reason for placing this order on hold…" />
            <FormActions label="Place on hold" :loading="busy === 'hold'" :disabled="!formInput.trim()" @submit="exec('hold')" @cancel="closeForm" />
          </template>

          <!-- dispute form -->
          <template v-if="activeForm === 'dispute'">
            <p class="text-xs font-semibold text-ink">Dispute reason <span class="text-rose-500">*</span></p>
            <textarea v-model="formInput" rows="3"
              class="focus-ring w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm resize-none"
              placeholder="Describe the issue clearly. This is recorded and visible to all parties." />
            <FormActions label="Open dispute" :loading="busy === 'dispute'" :disabled="!formInput.trim()" variant="danger" @submit="exec('dispute')" @cancel="closeForm" />
          </template>

          <!-- cancel form -->
          <template v-if="activeForm === 'cancel'">
            <p class="text-xs font-semibold text-ink">Cancellation reason <span class="text-rose-500">*</span></p>
            <textarea v-model="formInput" rows="2"
              class="focus-ring w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm resize-none"
              placeholder="Why is this order being cancelled?" />
            <p class="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded px-2 py-1.5">
              Cancellation triggers a refund review. This action cannot be undone.
            </p>
            <FormActions label="Cancel order" :loading="busy === 'cancel'" :disabled="!formInput.trim()" variant="danger" @submit="exec('cancel')" @cancel="closeForm" />
          </template>

          <!-- reassign form -->
          <template v-if="activeForm === 'reassign'">
            <p class="text-xs font-semibold text-ink">Reassignment reason <span class="text-rose-500">*</span></p>
            <textarea v-model="formInput" rows="2"
              class="focus-ring w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm resize-none"
              placeholder="Why is the writer being reassigned?" />
            <p class="text-xs text-slate-500">The current writer will be released and the order returned to the pool for reassignment.</p>
            <FormActions label="Request reassignment" :loading="busy === 'reassign'" :disabled="!formInput.trim()" @submit="exec('reassign')" @cancel="closeForm" />
          </template>

          <!-- manual payment verification form -->
          <template v-if="activeForm === 'manual_mark_paid'">
            <div class="grid gap-3 sm:grid-cols-3">
              <label class="block">
                <span class="text-xs font-semibold text-ink">Amount <span class="text-rose-500">*</span></span>
                <input
                  v-model="paymentAmount"
                  class="focus-ring mt-1 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
                  type="number"
                  min="0"
                  step="0.01"
                  placeholder="0.00"
                />
              </label>
              <label class="block">
                <span class="text-xs font-semibold text-ink">Method</span>
                <input
                  v-model.trim="paymentMethod"
                  class="focus-ring mt-1 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
                  placeholder="M-Pesa, bank, Stripe..."
                />
              </label>
              <label class="block">
                <span class="text-xs font-semibold text-ink">Reference <span class="text-rose-500">*</span></span>
                <input
                  v-model.trim="paymentReference"
                  class="focus-ring mt-1 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
                  placeholder="Transaction ID"
                />
              </label>
            </div>
            <p class="text-xs font-semibold text-ink">Verification note</p>
            <textarea v-model="formInput" rows="2"
              class="focus-ring w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm resize-none"
              placeholder="Who verified this payment and where was it confirmed?" />
            <p class="text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 rounded px-2 py-1.5">
              This records a staff payment override for audit and can move the order into the paid flow.
            </p>
            <FormActions
              label="Verify payment"
              :loading="busy === 'manual_mark_paid'"
              :disabled="!canSubmitManualPayment"
              @submit="exec('manual_mark_paid')"
              @cancel="closeForm"
            />
          </template>

        </div>
      </Transition>

      <!-- Blocked actions (collapsible) -->
      <div v-if="blockedEntries.length">
        <button
          class="flex items-center gap-1.5 text-xs font-medium text-graphite hover:text-ink"
          @click="showBlocked = !showBlocked"
        >
          <ChevronRight class="h-3 w-3 transition-transform" :class="showBlocked ? 'rotate-90' : ''" />
          {{ blockedEntries.length }} action{{ blockedEntries.length > 1 ? 's' : '' }} currently blocked
        </button>
        <div v-if="showBlocked" class="mt-2 space-y-1.5">
          <div
            v-for="[action, reason] in blockedEntries"
            :key="action"
            class="flex items-start gap-2 rounded-md border border-slate-100 bg-slate-50 px-3 py-2"
          >
            <Lock class="mt-0.5 h-3.5 w-3.5 shrink-0 text-slate-400" />
            <div>
              <p class="text-xs font-semibold text-slate-600">{{ actionLabel(action) }}</p>
              <p class="text-xs text-graphite mt-0.5">{{ reason }}</p>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- State reference guide -->
    <Transition name="slide-down">
      <div v-if="showGuide" class="border-t border-slate-200">
        <div class="px-5 py-4">
          <h3 class="text-xs font-semibold uppercase tracking-wide text-graphite mb-3">Order state reference</h3>
          <div class="overflow-x-auto">
            <table class="w-full text-xs">
              <thead>
                <tr class="border-b border-slate-100">
                  <th class="pb-2 text-left font-semibold text-graphite pr-4 whitespace-nowrap">Status</th>
                  <th class="pb-2 text-left font-semibold text-graphite pr-4">Label</th>
                  <th class="pb-2 text-left font-semibold text-graphite pr-4">Client</th>
                  <th class="pb-2 text-left font-semibold text-graphite pr-4">Writer</th>
                  <th class="pb-2 text-left font-semibold text-graphite pr-4">Support</th>
                  <th class="pb-2 text-left font-semibold text-graphite pr-4">Editor</th>
                  <th class="pb-2 text-left font-semibold text-graphite">Admin / Superadmin</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-50">
                <tr
                  v-for="row in STATE_GUIDE"
                  :key="row.status"
                  :class="row.status === order.status ? 'bg-signal/5' : ''"
                >
                  <td class="py-2 pr-4">
                    <span class="rounded-full px-2 py-0.5 font-mono font-semibold whitespace-nowrap" :class="statusClass(row.status)">
                      {{ row.status }}
                    </span>
                  </td>
                  <td class="py-2 pr-4 text-graphite whitespace-nowrap">{{ row.label }}</td>
                  <td class="py-2 pr-4 text-graphite">{{ row.client || "—" }}</td>
                  <td class="py-2 pr-4 text-graphite">{{ row.writer || "—" }}</td>
                  <td class="py-2 pr-4 text-graphite">{{ row.support || "—" }}</td>
                  <td class="py-2 pr-4 text-graphite">{{ row.editor || "—" }}</td>
                  <td class="py-2 text-graphite">{{ row.admin }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p class="mt-3 text-xs text-slate-400">Row highlighted in blue = current order state.</p>
        </div>
      </div>
    </Transition>

  </div>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, ref } from "vue";
import {
  AlertCircle, AlertTriangle, Archive, BookOpen, CheckCircle2, ChevronRight, CircleDollarSign,
  Lock, PauseCircle, PlayCircle, RotateCcw, UserRoundCog, XCircle, Zap,
} from "@lucide/vue";
import type { OrderSummary, OrderLifecycle } from "@/types/orders";
import type { UserRole } from "@/types/roles";
import { ordersApi } from "@/api/orders";
import { orderOpsApi } from "@/api/orderOps";

const props = defineProps<{
  orderId: string;
  order: OrderSummary;
  lifecycle: OrderLifecycle | null;
  role: UserRole;
}>();

const emit = defineEmits<{
  (e: "refresh"): void;
}>();

// ── state ──────────────────────────────────────────────────────────────────
const busy = ref<string | null>(null);
const pendingConfirm = ref<string | null>(null);
const activeForm = ref<string | null>(null);
const formInput = ref("");
const paymentAmount = ref("");
const paymentReference = ref("");
const paymentMethod = ref("");
const feedback = ref<{ ok: boolean; msg: string } | null>(null);
const showBlocked = ref(false);
const showGuide = ref(false);

// ── computed ───────────────────────────────────────────────────────────────
const availableActions = computed(() => props.lifecycle?.available_actions ?? []);
const blockedEntries = computed(() => Object.entries(props.lifecycle?.blocked_actions ?? []));

const isTerminal = computed(() =>
  ["cancelled", "refunded", "archived"].includes(props.order.status)
);

const canHold = computed(() =>
  !isTerminal.value &&
  !props.lifecycle?.has_active_hold &&
  ["in_progress", "qa_review", "under_editing", "revision_requested", "submitted"].includes(props.order.status)
);

const canReleaseHold = computed(() =>
  !!props.lifecycle?.has_active_hold && !!props.lifecycle?.active_hold_id
);

const canReassign = computed(() =>
  !isTerminal.value &&
  !!props.lifecycle?.has_current_assignment &&
  !props.lifecycle?.has_pending_reassignment_request &&
  ["in_progress", "on_hold", "qa_review"].includes(props.order.status)
);

const canSubmitManualPayment = computed(() =>
  Number(paymentAmount.value) > 0 &&
  paymentReference.value.trim().length > 0 &&
  formInput.value.trim().length > 0
);

// ── helpers ────────────────────────────────────────────────────────────────
function has(action: string): boolean {
  return availableActions.value.includes(action);
}

function setPending(action: string) {
  pendingConfirm.value = action;
  activeForm.value = null;
}

function openForm(form: string) {
  activeForm.value = form;
  pendingConfirm.value = null;
  formInput.value = "";
  paymentAmount.value = "";
  paymentReference.value = "";
  paymentMethod.value = "";
  feedback.value = null;
}

function closeForm() {
  activeForm.value = null;
  formInput.value = "";
  paymentAmount.value = "";
  paymentReference.value = "";
  paymentMethod.value = "";
}

function ok(msg: string) {
  feedback.value = { ok: true, msg };
  pendingConfirm.value = null;
  activeForm.value = null;
  formInput.value = "";
  paymentAmount.value = "";
  paymentReference.value = "";
  paymentMethod.value = "";
  emit("refresh");
}

function fail(msg: string) {
  feedback.value = { ok: false, msg };
}

async function exec(action: string) {
  busy.value = action;
  feedback.value = null;
  try {
    switch (action) {
      case "submit_for_qa":
        await ordersApi.qaSubmit(props.orderId);
        ok("Order submitted for QA review.");
        break;
      case "approve_delivery":
        await ordersApi.qaApprove(props.orderId);
        ok("Delivery approved — order marked as submitted.");
        break;
      case "return_to_writer":
        await ordersApi.qaReturn(props.orderId, formInput.value);
        ok("Order returned to writer for revision.");
        break;
      case "approve_order":
        await ordersApi.approve(props.orderId, {});
        ok("Order approved successfully.");
        break;
      case "hold":
        await ordersApi.holdRequest(props.orderId, formInput.value);
        ok("Hold placed. Order is now paused.");
        break;
      case "release_hold": {
        const holdId = props.lifecycle?.active_hold_id;
        if (!holdId) { fail("No active hold found."); break; }
        await ordersApi.holdRelease(holdId);
        ok("Hold released. Order is resuming.");
        break;
      }
      case "dispute":
        await ordersApi.raiseDispute(props.orderId, formInput.value);
        ok("Dispute opened. All parties have been notified.");
        break;
      case "cancel":
        await ordersApi.cancel(props.orderId, { reason: formInput.value, refund_destination: "wallet" });
        ok("Order cancelled.");
        break;
      case "archive_order":
        await ordersApi.archive(props.orderId, {});
        ok("Order archived.");
        break;
      case "reassign":
        await ordersApi.reassignmentRequest(props.orderId, formInput.value);
        ok("Reassignment request submitted. Review in Staffing tab.");
        break;
      case "manual_mark_paid":
        await orderOpsApi.manualVerifyPayment(Number(props.orderId), {
          amount: paymentAmount.value,
          transaction_reference: paymentReference.value.trim(),
          verification_note: formInput.value.trim(),
          payment_method: paymentMethod.value.trim() || undefined,
        });
        ok("Payment verified. The order is ready to continue through the paid flow.");
        break;
    }
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: { detail?: string; message?: string } } })
      ?.response?.data;
    fail(detail?.detail ?? detail?.message ?? "Action failed. Please try again.");
  } finally {
    busy.value = null;
    if (pendingConfirm.value === action) pendingConfirm.value = null;
  }
}

function actionLabel(key: string): string {
  const map: Record<string, string> = {
    submit_for_qa: "Submit for QA",
    approve_delivery: "Approve delivery",
    return_to_writer: "Return to writer",
    approve_order: "Approve order",
    raise_dispute: "Open dispute",
    cancel_order: "Cancel order",
    archive_order: "Archive",
    request_revision: "Request revision",
    manual_mark_paid: "Verify payment",
    route_to_staffing: "Route to staffing",
    assign_writer: "Assign writer",
    release_to_pool: "Release to pool",
  };
  return map[key] ?? key.replace(/_/g, " ");
}

function humanStatus(s: string): string {
  const map: Record<string, string> = {
    created: "Created", unpaid: "Unpaid", pending_payment: "Payment processing",
    paid: "Paid", ready_for_staffing: "Ready for staffing", in_progress: "In progress",
    on_hold: "On hold", qa_review: "QA review", under_editing: "Under editing",
    submitted: "Submitted", completed: "Completed", revision_requested: "Revision",
    disputed: "Disputed", cancelled: "Cancelled", refunded: "Refunded", archived: "Archived",
  };
  return map[s] ?? s;
}

function statusClass(s: string): string {
  const map: Record<string, string> = {
    created: "bg-slate-100 text-slate-600",
    unpaid: "bg-amber-100 text-amber-700",
    pending_payment: "bg-amber-100 text-amber-700",
    paid: "bg-sky-100 text-sky-700",
    ready_for_staffing: "bg-indigo-100 text-indigo-700",
    in_progress: "bg-blue-100 text-blue-700",
    on_hold: "bg-amber-100 text-amber-700",
    qa_review: "bg-violet-100 text-violet-700",
    under_editing: "bg-violet-100 text-violet-700",
    submitted: "bg-teal-100 text-teal-700",
    completed: "bg-emerald-100 text-emerald-700",
    revision_requested: "bg-orange-100 text-orange-700",
    disputed: "bg-rose-100 text-rose-700",
    cancelled: "bg-slate-100 text-slate-500",
    refunded: "bg-emerald-100 text-emerald-600",
    archived: "bg-slate-100 text-slate-400",
  };
  return map[s] ?? "bg-slate-100 text-slate-600";
}

// ── sub-components ─────────────────────────────────────────────────────────

// Inline ActionButton — handles confirm state pattern
const ActionButton = defineComponent({
  props: {
    icon: String,
    label: String,
    variant: { type: String, default: "neutral" },
    loading: Boolean,
    pending: Boolean,
  },
  emits: ["click", "confirm", "cancel"],
  setup(props, { emit }) {
    const base = "focus-ring inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors disabled:opacity-60";
    const classes: Record<string, string> = {
      primary: "border border-signal bg-signal text-white hover:bg-signal/90",
      success: "border border-emerald-400 bg-emerald-50 text-emerald-800 hover:bg-emerald-100",
      neutral: "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50",
      danger: "border border-rose-300 bg-rose-50 text-rose-800 hover:bg-rose-100",
    };

    return () => {
      if (props.pending) {
        return h("span", { class: "inline-flex items-center gap-1 text-xs" }, [
          h("span", { class: "text-graphite" }, `Confirm ${props.label}?`),
          h("button", {
            class: `${base} ${classes[props.variant ?? "neutral"]}`,
            disabled: props.loading,
            onClick: () => emit("confirm"),
          }, props.loading ? "…" : "Yes, proceed"),
          h("button", {
            class: `${base} border border-slate-200 bg-white text-slate-600 hover:bg-slate-50`,
            onClick: () => emit("cancel"),
          }, "Cancel"),
        ]);
      }
      return h("button", {
        class: `${base} ${classes[props.variant ?? "neutral"]}`,
        disabled: props.loading,
        onClick: () => emit("click"),
      }, props.loading ? `${props.label}…` : props.label);
    };
  },
});

// Inline form action bar
const FormActions = defineComponent({
  props: {
    label: String,
    loading: Boolean,
    disabled: Boolean,
    variant: { type: String, default: "primary" },
  },
  emits: ["submit", "cancel"],
  setup(props, { emit }) {
    return () =>
      h("div", { class: "flex items-center gap-2" }, [
        h("button", {
          class: [
            "focus-ring inline-flex items-center rounded-lg px-3 py-1.5 text-xs font-semibold",
            props.variant === "danger"
              ? "border border-rose-400 bg-rose-600 text-white hover:bg-rose-700 disabled:opacity-60"
              : "border border-signal bg-signal text-white hover:bg-signal/90 disabled:opacity-60",
          ].join(" "),
          disabled: props.loading || props.disabled,
          onClick: () => emit("submit"),
        }, props.loading ? "Submitting…" : props.label),
        h("button", {
          class: "focus-ring inline-flex items-center rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-50",
          onClick: () => emit("cancel"),
        }, "Cancel"),
      ]);
  },
});

// ── state guide data ───────────────────────────────────────────────────────
const STATE_GUIDE = [
  {
    status: "created",
    label: "Pending payment",
    client: "Pay, Cancel",
    writer: "—",
    support: "Cancel",
    editor: "—",
    admin: "Verify payment, Cancel, Hold if allowed",
  },
  {
    status: "unpaid",
    label: "Unpaid",
    client: "Pay, Cancel",
    writer: "—",
    support: "Cancel",
    editor: "—",
    admin: "Verify payment, Cancel, Hold if allowed",
  },
  {
    status: "pending_payment",
    label: "Payment processing",
    client: "—",
    writer: "—",
    support: "Cancel",
    editor: "—",
    admin: "Verify payment, Cancel, Hold if allowed",
  },
  {
    status: "paid",
    label: "Paid",
    client: "—",
    writer: "—",
    support: "—",
    editor: "—",
    admin: "Route to staffing, Hold, Cancel",
  },
  {
    status: "ready_for_staffing",
    label: "Ready for staffing",
    client: "—",
    writer: "—",
    support: "—",
    editor: "—",
    admin: "Assign writer, Release to pool, Hold, Cancel",
  },
  {
    status: "in_progress",
    label: "In progress",
    client: "Open dispute, Cancel",
    writer: "Submit for QA, Open dispute",
    support: "Hold, Open dispute, Cancel",
    editor: "—",
    admin: "Submit for QA, Hold, Open dispute, Cancel, Reassign",
  },
  {
    status: "on_hold",
    label: "On hold",
    client: "—",
    writer: "—",
    support: "Release hold",
    editor: "—",
    admin: "Release hold, Cancel",
  },
  {
    status: "qa_review",
    label: "QA review",
    client: "—",
    writer: "—",
    support: "Hold",
    editor: "Approve delivery, Return to writer",
    admin: "Approve delivery, Return to writer, Hold, Reassign",
  },
  {
    status: "under_editing",
    label: "Under editing",
    client: "—",
    writer: "—",
    support: "Hold",
    editor: "—",
    admin: "Hold, Cancel",
  },
  {
    status: "submitted",
    label: "Submitted",
    client: "Approve order, Request revision, Open dispute",
    writer: "—",
    support: "Open dispute",
    editor: "—",
    admin: "Approve order, Request revision, Open dispute",
  },
  {
    status: "completed",
    label: "Completed",
    client: "Request revision (if window open)",
    writer: "—",
    support: "—",
    editor: "—",
    admin: "Archive, Request revision (if window open)",
  },
  {
    status: "revision_requested",
    label: "Revision in progress",
    client: "Open dispute",
    writer: "Submit for QA, Open dispute",
    support: "Hold, Open dispute",
    editor: "Approve delivery, Return to writer",
    admin: "Submit for QA, Hold, Open dispute, Reassign",
  },
  {
    status: "disputed",
    label: "Dispute open",
    client: "—",
    writer: "—",
    support: "Escalate, Resolve, Close dispute",
    editor: "—",
    admin: "Escalate, Resolve, Close dispute",
  },
  {
    status: "cancelled",
    label: "Cancelled",
    client: "—",
    writer: "—",
    support: "—",
    editor: "—",
    admin: "—",
  },
  {
    status: "refunded",
    label: "Refunded",
    client: "—",
    writer: "—",
    support: "—",
    editor: "—",
    admin: "Archive",
  },
  {
    status: "archived",
    label: "Archived (read-only)",
    client: "—",
    writer: "—",
    support: "—",
    editor: "—",
    admin: "—",
  },
];
</script>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.18s ease;
  overflow: hidden;
}
.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  max-height: 0;
}
.slide-down-enter-to,
.slide-down-leave-from {
  opacity: 1;
  max-height: 600px;
}
</style>

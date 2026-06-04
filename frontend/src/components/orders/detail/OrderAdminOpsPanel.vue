<script setup lang="ts">
import { ref, computed } from "vue";
import { Archive, CheckCircle2, Flag, RotateCcw, Send, ThumbsUp, XCircle } from "@lucide/vue";
import { useOrderOpsStore } from "@/stores/orderOps";
import { useOrderStore } from "@/stores/orders";
import { ordersApi } from "@/api/orders";
import type { UserRole } from "@/types/roles";

const props = defineProps<{
  orderId: number;
  role: UserRole;
}>();

const ops = useOrderOpsStore();
const orders = useOrderStore();

const writerId = ref("");
const note = ref("");
const disputeReason = ref("");
const isPanelMutating = ref(false);
const actionError = ref("");
const actionNotice = ref("");

const canAct = computed(
  () => props.role === "admin" || props.role === "superadmin",
);
const needsNote = computed(() => note.value.trim().length >= 10);
const availableActions = computed(() => {
  if (Number(orders.selectedLifecycle?.order_id) !== Number(props.orderId)) {
    return [];
  }
  return orders.selectedLifecycle?.available_actions ?? [];
});

function hasAction(action: string) {
  return availableActions.value.includes(action);
}

const hasAnyAction = computed(() =>
  [
    "route_to_staffing",
    "assign_writer",
    "release_to_pool",
    "submit_for_qa",
    "approve_delivery",
    "return_to_writer",
    "approve_order",
    "request_revision",
    "raise_dispute",
    "cancel_order",
    "archive_order",
  ].some(hasAction),
);

async function run(action: () => Promise<unknown>) {
  isPanelMutating.value = true;
  actionError.value = "";
  actionNotice.value = "";
  try {
    await action();
    await orders.fetchOrder(props.orderId);
    note.value = "";
    writerId.value = "";
    disputeReason.value = "";
    actionNotice.value = "Order action completed.";
  }
  catch {
    actionError.value = "Unable to complete this action for the current order status.";
  } finally {
    isPanelMutating.value = false;
  }
}

function revisionPayload() {
  return {
    reason: "Staff revision request",
    scope_summary: note.value.trim(),
    is_within_original_scope: true,
  };
}

async function submitForQA() {
  await ordersApi.qaSubmit(props.orderId);
}
</script>

<template>
  <div v-if="canAct" class="rounded-lg border border-slate-200 bg-slate-50 p-4">
    <div class="mb-3 flex items-center gap-2">
      <Send class="h-3.5 w-3.5 text-signal" />
      <h3 class="text-sm font-semibold text-ink">Order flow controls</h3>
    </div>

    <div v-if="ops.notice" class="mb-3 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-900">
      {{ ops.notice }}
    </div>
    <div v-if="actionNotice" class="mb-3 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-900">
      {{ actionNotice }}
    </div>
    <div v-if="ops.error" class="mb-3 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-900">
      {{ ops.error }}
    </div>
    <div v-if="actionError || orders.error" class="mb-3 rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-900">
      {{ actionError || orders.error }}
    </div>

    <div class="grid gap-3 sm:grid-cols-2">
      <div>
        <label class="block text-xs font-medium text-graphite mb-1">Writer ID (for direct assign)</label>
        <input
          v-model.trim="writerId"
          inputmode="numeric"
          placeholder="e.g. 42"
          class="focus-ring h-9 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
        />
      </div>
      <div>
        <label class="block text-xs font-medium text-graphite mb-1">Operational note (≥10 chars for actions that need one)</label>
        <input
          v-model.trim="note"
          placeholder="Required for return / revision / cancel"
          class="focus-ring h-9 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
        />
      </div>
      <div v-if="hasAction('raise_dispute')" class="sm:col-span-2">
        <label class="block text-xs font-medium text-graphite mb-1">Dispute reason</label>
        <input
          v-model.trim="disputeReason"
          placeholder="Required when opening a dispute"
          class="focus-ring h-9 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
        />
      </div>
    </div>

    <div v-if="hasAnyAction" class="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-6">
      <button
        v-if="hasAction('route_to_staffing')"
        class="focus-ring inline-flex h-9 items-center justify-center gap-1 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold disabled:opacity-50"
        :disabled="isPanelMutating || ops.isMutating"
        @click="run(() => ops.routeToStaffing(orderId))"
      ><Send class="size-3.5" /> Route</button>

      <button
        v-if="hasAction('assign_writer')"
        class="focus-ring inline-flex h-9 items-center justify-center gap-1 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold disabled:opacity-50"
        :disabled="isPanelMutating || ops.isMutating || !Number(writerId)"
        @click="run(() => ops.assignDirect(orderId, Number(writerId), note))"
      >Assign writer</button>

      <button
        v-if="hasAction('release_to_pool')"
        class="focus-ring inline-flex h-9 items-center justify-center gap-1 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold disabled:opacity-50"
        :disabled="isPanelMutating || ops.isMutating"
        @click="run(() => ops.releaseToPool(orderId, note))"
      >Release to pool</button>

      <button
        v-if="hasAction('submit_for_qa')"
        class="focus-ring inline-flex h-9 items-center justify-center gap-1 rounded-md border border-blue-200 bg-white px-3 text-xs font-semibold text-blue-800 disabled:opacity-50"
        :disabled="isPanelMutating"
        @click="run(submitForQA)"
      ><Send class="size-3.5" /> Submit QA</button>

      <button
        v-if="hasAction('approve_delivery')"
        class="focus-ring inline-flex h-9 items-center justify-center gap-1 rounded-md border border-emerald-200 bg-white px-3 text-xs font-semibold text-emerald-800 disabled:opacity-50"
        :disabled="isPanelMutating || ops.isMutating"
        @click="run(() => ops.approveForDelivery(orderId, note))"
      ><CheckCircle2 class="size-3.5" /> Approve delivery</button>

      <button
        v-if="hasAction('return_to_writer')"
        class="focus-ring inline-flex h-9 items-center justify-center gap-1 rounded-md border border-amber-200 bg-white px-3 text-xs font-semibold text-amber-900 disabled:opacity-50"
        :disabled="isPanelMutating || ops.isMutating || !needsNote"
        @click="run(() => ops.returnToWriter(orderId, note))"
      ><RotateCcw class="size-3.5" /> Return</button>

      <button
        v-if="hasAction('approve_order')"
        class="focus-ring inline-flex h-9 items-center justify-center gap-1 rounded-md border border-emerald-200 bg-white px-3 text-xs font-semibold text-emerald-800 disabled:opacity-50"
        :disabled="isPanelMutating || orders.isMutating"
        @click="run(() => orders.approveOrder(orderId))"
      ><ThumbsUp class="size-3.5" /> Accept</button>

      <button
        v-if="hasAction('request_revision')"
        class="focus-ring inline-flex h-9 items-center justify-center gap-1 rounded-md border border-saffron/40 bg-white px-3 text-xs font-semibold text-amber-800 disabled:opacity-50"
        :disabled="isPanelMutating || orders.isMutating || !needsNote"
        @click="run(() => orders.requestRevision(orderId, revisionPayload()))"
      ><RotateCcw class="size-3.5" /> Revision</button>

      <button
        v-if="hasAction('raise_dispute')"
        class="focus-ring inline-flex h-9 items-center justify-center gap-1 rounded-md border border-amber-200 bg-white px-3 text-xs font-semibold text-amber-900 disabled:opacity-50"
        :disabled="isPanelMutating || orders.isMutating || disputeReason.trim().length < 10"
        @click="run(() => orders.raiseDispute(orderId, disputeReason.trim()))"
      ><Flag class="size-3.5" /> Dispute</button>

      <button
        v-if="hasAction('cancel_order')"
        class="focus-ring inline-flex h-9 items-center justify-center gap-1 rounded-md border border-rose-200 bg-white px-3 text-xs font-semibold text-rose-800 disabled:opacity-50"
        :disabled="isPanelMutating || ops.isMutating || !needsNote"
        @click="run(() => ops.cancel(orderId, note))"
      ><XCircle class="size-3.5" /> Cancel</button>

      <button
        v-if="hasAction('archive_order')"
        class="focus-ring inline-flex h-9 items-center justify-center gap-1 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold text-slate-700 disabled:opacity-50"
        :disabled="isPanelMutating || ops.isMutating"
        @click="run(() => ops.archive(orderId))"
      ><Archive class="size-3.5" /> Archive</button>
    </div>
    <p v-else class="mt-3 rounded-md border border-slate-200 bg-white px-3 py-2 text-xs text-graphite">
      No direct staff action is available for this order status.
    </p>
  </div>
</template>

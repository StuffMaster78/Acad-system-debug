<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import {
  Archive,
  CheckCircle2,
  CircleDollarSign,
  ClipboardList,
  Layers3,
  RefreshCw,
  Route,
  Search,
  Send,
  XCircle,
} from "@lucide/vue";
import BaseModal from "@/components/ui/BaseModal.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import SavedViewPresets from "@/components/admin/SavedViewPresets.vue";
import {
  adminWorkApi,
  type AdminWorkDetailBundle,
  type ClassOrderDetailRecord,
  type SpecialOrderDetailRecord,
} from "@/api/adminWork";
import {
  queueDefinitions,
  useOrderOpsStore,
} from "@/stores/orderOps";
import {
  useAdminWorkStore,
  workKindLabel,
  workTone,
} from "@/stores/adminWork";
import { useOrderStore } from "@/stores/orders";
import { useWebsitesStore } from "@/stores/websites";
import type { AdminWorkItem } from "@/types/adminWork";
import type { AdminWorkKind } from "@/types/adminWork";
import type { OrderOpsRow } from "@/types/orderOps";

const ops = useOrderOpsStore();
const work = useAdminWorkStore();
const orderDetails = useOrderStore();
const router = useRouter();
const route = useRoute();

const toneClasses = {
  neutral: "border-slate-200 bg-white",
  good: "border-emerald-200 bg-emerald-50",
  warn: "border-amber-200 bg-amber-50",
  risk: "border-rose-200 bg-rose-50",
};

const workTabs: Array<{ key: AdminWorkKind | "all"; label: string }> = [
  { key: "all", label: "All work" },
  { key: "order", label: "Orders" },
  { key: "special_order", label: "Special" },
  { key: "class_order", label: "Classes" },
];

const orderControl = reactive({
  selectedId: 0,
  writerId: "",
  note: "Operational update from the order command center.",
});
type QuickAction =
  | "route_to_staffing"
  | "manual_mark_paid"
  | "assign_writer"
  | "release_to_pool"
  | "approve_delivery"
  | "return_to_writer"
  | "request_revision"
  | "cancel_order"
  | "archive_order";

const actionDialog = reactive({
  open: false,
  action: null as QuickAction | null,
  order: null as OrderOpsRow | null,
  note: "",
  writerId: "",
  amount: "",
  transactionReference: "",
  paymentMethod: "",
});
const detailOpen = ref(false);
const detailContext = ref<AdminWorkItem | OrderOpsRow | null>(null);
const detailBundle = ref<AdminWorkDetailBundle>({});
const detailLoading = ref(false);
const detailNote = ref("Operational action from order detail drawer.");

function isWorkItem(context: AdminWorkItem | OrderOpsRow): context is AdminWorkItem {
  return "reference" in context;
}

const selectedQueueOrder = computed<OrderOpsRow | undefined>(() =>
  ops.rows.find((row) => row.id === orderControl.selectedId) ?? ops.rows[0],
);
const detailOrderId = computed(() => detailContext.value?.id ?? orderDetails.selectedOrder?.id ?? 0);
const detailTitle = computed(() => {
  if (!detailContext.value) return "Order detail";
  if (isWorkItem(detailContext.value)) return `${detailContext.value.reference} · ${detailContext.value.title}`;
  return `#${detailContext.value.id} ${detailContext.value.topic}`;
});
const detailStatus = computed(() => {
  if (orderDetails.selectedOrder?.id === detailOrderId.value) return orderDetails.selectedOrder.status;
  return detailContext.value && "status" in detailContext.value ? detailContext.value.status : "unknown";
});
const detailPaymentStatus = computed(() => {
  if (orderDetails.selectedOrder?.id === detailOrderId.value) return orderDetails.selectedOrder.payment_status;
  if (!detailContext.value) return undefined;
  return isWorkItem(detailContext.value) ? detailContext.value.paymentStatus : detailContext.value.payment_status;
});
const detailAmount = computed(() => {
  if (orderDetails.selectedOrder?.id === detailOrderId.value) return orderDetails.selectedOrder.total_price;
  if (!detailContext.value) return undefined;
  return isWorkItem(detailContext.value) ? detailContext.value.amount : detailContext.value.total_price;
});
const detailCurrency = computed(() => {
  if (orderDetails.selectedOrder?.id === detailOrderId.value) return orderDetails.selectedOrder.currency;
  return detailContext.value && "currency" in detailContext.value ? detailContext.value.currency : "USD";
});
const specialDetail = computed(() =>
  detailContext.value && isWorkItem(detailContext.value) && detailContext.value.kind === "special_order"
    ? detailBundle.value.detail as SpecialOrderDetailRecord | undefined
    : undefined,
);
const classDetail = computed(() =>
  detailContext.value && isWorkItem(detailContext.value) && detailContext.value.kind === "class_order"
    ? detailBundle.value.detail as ClassOrderDetailRecord | undefined
    : undefined,
);

function formatDate(value: string | null) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatAmount(amount?: string | number | null, currency = "USD") {
  if (!amount) return "Not priced";
  const numeric = Number(amount);
  if (Number.isNaN(numeric)) return `${currency} ${amount}`;
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(numeric);
}

async function refreshAll() {
  await Promise.allSettled([
    work.refresh(),
    ops.refresh(),
  ]);
  orderControl.selectedId = ops.rows[0]?.id ?? 0;
}

function selectQueueOrder(order: OrderOpsRow) {
  orderControl.selectedId = order.id;
}

function orderStatus(order?: Pick<OrderOpsRow, "status">) {
  return String(order?.status ?? "").toLowerCase();
}

function orderPaymentStatus(order?: Pick<OrderOpsRow, "payment_status">) {
  return String(order?.payment_status ?? "").toLowerCase();
}

function isPaidForStaffing(order?: Pick<OrderOpsRow, "status" | "payment_status">) {
  const paymentStatus = orderPaymentStatus(order);
  return ["paid", "fully_paid"].includes(paymentStatus) || (!paymentStatus && orderStatus(order) === "paid");
}

function orderOutstandingAmount(order?: Pick<OrderOpsRow, "total_price" | "amount_paid">) {
  const total = Number(order?.total_price ?? 0);
  const paid = Number(order?.amount_paid ?? 0);
  const due = Math.max(0, total - paid);
  return Number.isFinite(due) ? due.toFixed(2) : "";
}

function actionAllowed(order: OrderOpsRow | undefined, action: string, fallback: () => boolean) {
  if (order?.available_actions) return order.available_actions.includes(action);
  return fallback();
}

function canManualMarkPaid(order?: OrderOpsRow) {
  return !isPaidForStaffing(order) && actionAllowed(order, "manual_mark_paid", () => [
    "created",
    "unpaid",
    "pending_payment",
    "paid",
  ].includes(orderStatus(order)) || ["unpaid", "pending", "partially_paid"].includes(orderPaymentStatus(order)));
}

function canRouteToStaffing(order?: OrderOpsRow) {
  return isPaidForStaffing(order) && actionAllowed(order, "route_to_staffing", () => orderStatus(order) === "paid");
}

function canAssignWriter(order?: OrderOpsRow) {
  return isPaidForStaffing(order) && actionAllowed(order, "assign_writer", () => ["ready_for_staffing", "paid", "preferred_writer_pending"].includes(orderStatus(order)));
}

function canReleaseToPool(order?: OrderOpsRow) {
  return isPaidForStaffing(order) && actionAllowed(order, "release_to_pool", () => ["ready_for_staffing", "preferred_writer_pending", "assigned"].includes(orderStatus(order)));
}

function canApproveDelivery(order?: OrderOpsRow) {
  return actionAllowed(order, "approve_delivery", () => ["qa_review", "submitted", "awaiting_approval", "delivered"].includes(orderStatus(order)));
}

function canReturnToWriter(order?: OrderOpsRow) {
  return actionAllowed(order, "return_to_writer", () => ["qa_review", "submitted", "awaiting_approval"].includes(orderStatus(order)));
}

function canRequestRevision(order?: OrderOpsRow) {
  return actionAllowed(order, "request_revision", () => ["submitted", "completed", "awaiting_approval"].includes(orderStatus(order)));
}

function canCancelOrder(order?: OrderOpsRow) {
  return actionAllowed(order, "cancel_order", () => [
    "created",
    "unpaid",
    "pending_payment",
    "paid",
    "ready_for_staffing",
    "in_progress",
    "on_hold",
    "qa_review",
    "submitted",
    "disputed",
  ].includes(orderStatus(order)));
}

function canArchiveOrder(order?: OrderOpsRow) {
  return actionAllowed(order, "archive_order", () => orderStatus(order) === "completed");
}

function orderControlDisabled(requireNote = false, actionAllowed = true) {
  return !selectedQueueOrder.value || !actionAllowed || ops.isMutating || (requireNote && orderControl.note.trim().length < 10);
}

const actionCopy: Record<QuickAction, {
  title: string;
  description: string;
  confirm: string;
  tone: "neutral" | "success" | "warning" | "danger";
  requiresNote?: boolean;
  requiresWriter?: boolean;
}> = {
  route_to_staffing: {
    title: "Route order to staffing",
    description: "Move this paid order into the staffing queue so an eligible writer can be assigned.",
    confirm: "Route to staffing",
    tone: "neutral",
  },
  manual_mark_paid: {
    title: "Verify payment manually",
    description: "Apply a verified payment that did not reflect automatically. A transaction reference and audit note are required.",
    confirm: "Verify payment",
    tone: "success",
    requiresNote: true,
  },
  assign_writer: {
    title: "Assign writer",
    description: "Assign this order directly to a writer. The writer will see their writer-safe deadline and instructions.",
    confirm: "Assign writer",
    tone: "neutral",
    requiresWriter: true,
  },
  release_to_pool: {
    title: "Release order to pool",
    description: "Clear the preferred/direct assignment path and return this order to the writer pool.",
    confirm: "Release to pool",
    tone: "warning",
  },
  approve_delivery: {
    title: "Approve delivery",
    description: "Approve the submitted work for delivery. The client-facing order state will advance.",
    confirm: "Approve delivery",
    tone: "success",
  },
  return_to_writer: {
    title: "Return to writer",
    description: "Send this back to the writer with clear correction instructions. The writer needs this note to act.",
    confirm: "Return to writer",
    tone: "warning",
    requiresNote: true,
  },
  request_revision: {
    title: "Request revision",
    description: "Open a revision request with instructions. This should match the allowed revision state for the order.",
    confirm: "Request revision",
    tone: "warning",
    requiresNote: true,
  },
  cancel_order: {
    title: "Cancel order",
    description: "Cancel this order and send it into the refund/review path where applicable. This needs a clear reason.",
    confirm: "Cancel order",
    tone: "danger",
    requiresNote: true,
  },
  archive_order: {
    title: "Archive order",
    description: "Hide this completed order from active operations queues while preserving history and audit records.",
    confirm: "Archive order",
    tone: "neutral",
  },
};

const currentActionCopy = computed(() =>
  actionDialog.action ? actionCopy[actionDialog.action] : null,
);

const actionDialogCanSubmit = computed(() => {
  const copy = currentActionCopy.value;
  if (!copy || !actionDialog.order || ops.isMutating) return false;
  if (actionDialog.action === "manual_mark_paid") {
    return Number(actionDialog.amount) > 0
      && actionDialog.transactionReference.trim().length >= 4
      && actionDialog.note.trim().length >= 10;
  }
  if (["route_to_staffing", "assign_writer", "release_to_pool"].includes(actionDialog.action ?? "") && !isPaidForStaffing(actionDialog.order)) return false;
  if (copy.requiresNote && actionDialog.note.trim().length < 10) return false;
  if (copy.requiresWriter && !Number(actionDialog.writerId)) return false;
  return true;
});

function openActionDialog(action: QuickAction, order?: OrderOpsRow) {
  const targetOrder = order ?? selectedQueueOrder.value;
  if (!targetOrder) return;
  actionDialog.open = true;
  actionDialog.action = action;
  actionDialog.order = targetOrder;
  actionDialog.note = orderControl.note;
  actionDialog.writerId = orderControl.writerId;
  actionDialog.amount = action === "manual_mark_paid" ? orderOutstandingAmount(targetOrder) : "";
  actionDialog.transactionReference = "";
  actionDialog.paymentMethod = "";
}

function closeActionDialog() {
  actionDialog.open = false;
  actionDialog.action = null;
  actionDialog.order = null;
  actionDialog.note = "";
  actionDialog.writerId = "";
  actionDialog.amount = "";
  actionDialog.transactionReference = "";
  actionDialog.paymentMethod = "";
}

async function confirmActionDialog() {
  if (!actionDialog.action || !actionDialog.order || !actionDialogCanSubmit.value) return;
  const orderId = actionDialog.order.id;
  const note = actionDialog.note.trim();
  switch (actionDialog.action) {
    case "route_to_staffing":
      await ops.routeToStaffing(orderId);
      break;
    case "manual_mark_paid":
      await ops.manualVerifyPayment(orderId, {
        amount: actionDialog.amount,
        transaction_reference: actionDialog.transactionReference.trim(),
        verification_note: note,
        payment_method: actionDialog.paymentMethod.trim(),
      });
      break;
    case "assign_writer":
      await ops.assignDirect(orderId, Number(actionDialog.writerId), note);
      break;
    case "release_to_pool":
      await ops.releaseToPool(orderId, note);
      break;
    case "approve_delivery":
      await ops.approveForDelivery(orderId, note);
      break;
    case "return_to_writer":
      await ops.returnToWriter(orderId, note);
      break;
    case "request_revision":
      await ops.requestRevision(orderId, note);
      break;
    case "cancel_order":
      await ops.cancel(orderId, note);
      break;
    case "archive_order":
      await ops.archive(orderId);
      break;
  }
  closeActionDialog();
}

function openOrderDetail(context: AdminWorkItem | OrderOpsRow) {
  // Navigate to the dedicated full-page detail view instead of opening a modal.
  const prefix = route.path.startsWith("/superadmin") ? "/superadmin" : "/admin";
  const kind = isWorkItem(context) ? context.kind : "order";
  if (kind === "special_order") {
    router.push(`${prefix}/special-orders/${context.id}`);
  } else if (kind === "class_order") {
    router.push(`${prefix}/classes/${context.id}`);
  } else {
    router.push(`${prefix}/orders/${context.id}`);
  }
}

async function approveDetailOrder() {
  if (!detailOrderId.value) return;
  await ops.approveForDelivery(Number(detailOrderId.value), detailNote.value).catch(() => undefined);
  if (orderDetails.selectedOrder?.id === detailOrderId.value) {
    await orderDetails.fetchOrder(detailOrderId.value).catch(() => undefined);
  }
}

async function returnDetailOrder() {
  if (!detailOrderId.value || detailNote.value.trim().length < 10) return;
  await ops.returnToWriter(Number(detailOrderId.value), detailNote.value).catch(() => undefined);
  if (orderDetails.selectedOrder?.id === detailOrderId.value) {
    await orderDetails.fetchOrder(detailOrderId.value).catch(() => undefined);
  }
}

function normalizeMaybeResults(value: unknown): Array<Record<string, unknown>> {
  if (Array.isArray(value)) return value.filter((item): item is Record<string, unknown> => typeof item === "object" && item !== null);
  if (value && typeof value === "object" && Array.isArray((value as { results?: unknown[] }).results)) {
    return (value as { results: unknown[] }).results.filter((item): item is Record<string, unknown> => typeof item === "object" && item !== null);
  }
  return [];
}

function valueOf(record: Record<string, unknown> | undefined, keys: string[], fallback = "Not set") {
  if (!record) return fallback;
  for (const key of keys) {
    const value = record[key];
    if (value !== undefined && value !== null && value !== "") return String(value);
  }
  return fallback;
}

function firstRecordLabel(record: Record<string, unknown>) {
  return valueOf(record, ["title", "name", "label", "status", "event_type", "task_type", "id"], "Record");
}

const websites = useWebsitesStore();
onMounted(() => {
  refreshAll().catch(() => undefined);
  websites.ensure();
});
</script>

<template>
  <div class="space-y-8">
    <section class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase text-signal">Admin</p>
        <h1 class="mt-2 text-3xl font-semibold">Work command center</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          A cross-site view of standard orders, special orders, class work,
          client context, writer assignments, payment state, and operational risk.
        </p>
      </div>
      <button
        class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
        type="button"
        @click="refreshAll"
      >
        <RefreshCw class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <p
      v-if="work.error || ops.error"
      class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {{ work.error || ops.error }} Preview mode will still show the layout.
    </p>
    <p
      v-if="ops.notice"
      class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900"
    >
      {{ ops.notice }}
    </p>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div
        v-for="metric in work.metrics"
        :key="metric.label"
        class="min-h-32 rounded-md border p-4"
        :class="toneClasses[metric.tone]"
      >
        <p class="text-sm font-medium text-graphite">{{ metric.label }}</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ metric.value }}</p>
        <p class="mt-2 text-sm leading-5 text-graphite">{{ metric.detail }}</p>
      </div>
    </section>

    <section class="rounded-xl border border-slate-200 bg-white">
      <div class="flex items-center gap-2 border-b border-slate-200 px-5 py-4">
        <Layers3 class="h-5 w-5 text-signal" />
        <div>
          <h2 class="text-base font-semibold text-ink">All client-site work</h2>
          <p class="text-xs text-graphite">Normal orders, special orders, and class commitments.</p>
        </div>
      </div>
      <div class="flex flex-wrap items-center gap-2 border-b border-slate-100 bg-slate-50 px-5 py-2">
        <SavedViewPresets
          view-type="orders"
          :current-filters="{ query: work.query, kind: work.activeKind }"
          @load="(f) => { work.query = String(f.query ?? ''); if (f.kind) work.activeKind = f.kind as (typeof work.activeKind); }"
        />
      </div>
      <div class="flex flex-wrap items-center gap-3 border-b border-slate-100 bg-slate-50 px-5 py-3">
        <div class="flex flex-wrap gap-1">
          <button
            v-for="tab in workTabs"
            :key="tab.key"
            class="focus-ring h-8 rounded-lg px-3 text-xs font-semibold transition-colors"
            :class="work.activeKind === tab.key ? 'bg-ink text-white shadow-sm' : 'bg-white border border-slate-200 text-graphite hover:border-slate-300 hover:text-ink'"
            type="button"
            @click="work.activeKind = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>
        <label class="relative ml-auto block w-52">
          <Search class="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
          <input
            v-model="work.query"
            class="focus-ring h-8 w-full rounded-lg border border-slate-200 bg-white pl-8 pr-3 text-xs"
            type="search"
            placeholder="Search orders…"
          />
        </label>
      </div>

      <div v-if="work.filteredItems.length">
        <!-- Mobile cards -->
        <div class="divide-y divide-slate-100 sm:hidden">
          <button
            v-for="item in work.filteredItems"
            :key="`${item.kind}-${item.id}`"
            class="w-full px-4 py-3 text-left hover:bg-slate-50"
            type="button"
            @click="openOrderDetail(item)"
          >
            <div class="flex items-start justify-between gap-2">
              <div class="min-w-0 flex-1">
                <div class="flex flex-wrap items-center gap-1.5">
                  <span class="font-semibold text-ink">{{ item.reference }}</span>
                  <StatusPill :label="workKindLabel(item.kind)" :tone="workTone(item)" />
                </div>
                <p class="mt-0.5 truncate text-sm font-medium text-ink">{{ item.title }}</p>
              </div>
              <StatusPill :label="item.status" :tone="workTone(item)" class="shrink-0" />
            </div>
            <div class="mt-2 flex flex-wrap gap-3 text-xs text-graphite">
              <span>{{ item.website }} · {{ item.client }}</span>
              <span v-if="item.assignedWriter">{{ item.assignedWriter }}</span>
              <span>{{ formatDate(item.deadline) }}</span>
              <span class="font-semibold text-ink">{{ formatAmount(item.amount, item.currency) }}</span>
            </div>
          </button>
        </div>

        <!-- Desktop table -->
        <div class="hidden overflow-x-auto sm:block">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50 text-left text-xs font-semibold uppercase text-graphite">
              <tr>
                <th class="px-3 py-2">Work</th>
                <th class="px-3 py-2">Site / client</th>
                <th class="px-3 py-2">Assigned writer</th>
                <th class="px-3 py-2">Status</th>
                <th class="px-3 py-2">Deadline</th>
                <th class="px-3 py-2 text-right">Value</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr
                v-for="item in work.filteredItems"
                :key="`${item.kind}-${item.id}`"
                class="cursor-pointer hover:bg-slate-50"
                @click="openOrderDetail(item)"
              >
                <td class="px-3 py-2.5">
                  <div class="flex flex-wrap items-center gap-2">
                    <p class="font-semibold text-ink">{{ item.reference }}</p>
                    <StatusPill :label="workKindLabel(item.kind)" :tone="workTone(item)" />
                  </div>
                  <p class="mt-1 max-w-md font-medium text-ink">{{ item.title }}</p>
                  <p v-if="item.subject" class="mt-1 text-xs text-graphite">{{ item.subject }}</p>
                </td>
                <td class="px-3 py-2.5">
                  <p class="font-medium text-ink">{{ item.website }}</p>
                  <p class="mt-1 text-xs text-graphite">{{ item.client }}</p>
                </td>
                <td class="px-3 py-2.5 text-graphite">{{ item.assignedWriter }}</td>
                <td class="px-3 py-2.5">
                  <StatusPill :label="item.status" :tone="workTone(item)" />
                  <p v-if="item.paymentStatus" class="mt-2 text-xs text-graphite">Payment: {{ item.paymentStatus }}</p>
                </td>
                <td class="px-3 py-2.5 text-graphite">
                  {{ formatDate(item.deadline) }}
                  <p v-if="item.notes" class="mt-1 max-w-xs text-xs leading-5 text-graphite">{{ item.notes }}</p>
                </td>
                <td class="px-3 py-2.5 text-right font-semibold text-ink">{{ formatAmount(item.amount, item.currency) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div v-else class="p-4">
        <EmptyState
          :icon="ClipboardList"
          title="No work records found"
          message="Adjust the filter or refresh once the backend is connected."
        />
      </div>
    </section>

    <section class="space-y-4">
      <div>
        <h2 class="text-base font-semibold">Operations queues</h2>
        <p class="mt-1 text-sm text-graphite">
          Focused queues for staffing, deadlines, approvals, writer acknowledgement, and archive review.
        </p>
      </div>

      <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <button
          v-for="queue in queueDefinitions"
          :key="queue.key"
          class="focus-ring min-h-32 rounded-md border p-4 text-left"
          :class="[
            toneClasses[queue.tone],
            ops.activeQueue === queue.key ? 'ring-2 ring-signal ring-offset-2' : '',
          ]"
          type="button"
          @click="ops.fetchQueue(queue.key).catch(() => undefined)"
        >
          <p class="text-sm font-medium text-graphite">{{ queue.label }}</p>
          <p class="mt-3 text-3xl font-semibold text-ink">
            {{ ops.counts[queue.countKey] }}
          </p>
          <p class="mt-2 text-sm leading-5 text-graphite">
            {{ queue.description }}
          </p>
        </button>
      </div>

      <div class="rounded-md border border-slate-200 bg-white">
        <div class="flex min-h-16 items-center justify-between gap-3 border-b border-slate-200 px-4">
          <div>
            <h3 class="text-base font-semibold">{{ ops.activeDefinition.label }}</h3>
            <p class="text-sm text-graphite">{{ ops.activeDefinition.description }}</p>
          </div>
          <StatusPill :label="`${ops.rows.length} rows`" />
        </div>

        <div class="grid gap-4 border-b border-slate-200 bg-slate-50 px-4 py-4 xl:grid-cols-[minmax(0,1fr)_360px]">
          <div>
            <div class="flex items-center gap-2">
              <Send class="h-4 w-4 text-signal" />
              <h4 class="text-sm font-semibold text-ink">Order flow controls</h4>
            </div>
            <p class="mt-1 text-sm text-graphite">
              Select a queue row, then route, assign, approve, return, revise, cancel, or archive from one control surface.
            </p>
            <div class="mt-3 grid gap-3 sm:grid-cols-2">
              <label class="block text-sm font-medium text-ink">
                Selected order
                <select
                  v-model.number="orderControl.selectedId"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
                >
                  <option
                    v-for="row in ops.rows"
                    :key="row.id"
                    :value="row.id"
                  >
                    #{{ row.id }} · {{ row.topic }}
                  </option>
                </select>
              </label>
              <label class="block text-sm font-medium text-ink">
                Writer ID
                <input
                  v-model.trim="orderControl.writerId"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
                  inputmode="numeric"
                  placeholder="For direct assignment"
                >
              </label>
            </div>
            <label class="mt-3 block text-sm font-medium text-ink">
              Operational note
              <textarea
                v-model.trim="orderControl.note"
                class="focus-ring mt-1 min-h-20 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
              />
            </label>
          </div>

          <div class="grid content-start gap-2 sm:grid-cols-2 xl:grid-cols-1">
            <button
              v-if="canManualMarkPaid(selectedQueueOrder)"
              class="focus-ring h-10 rounded-md border border-emerald-200 bg-white px-3 text-sm font-semibold text-emerald-800 disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled(true, canManualMarkPaid(selectedQueueOrder))"
              @click="openActionDialog('manual_mark_paid')"
            >
              Verify payment
            </button>
            <button
              v-if="canRouteToStaffing(selectedQueueOrder)"
              class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled(false, canRouteToStaffing(selectedQueueOrder))"
              @click="openActionDialog('route_to_staffing')"
            >
              Route to staffing
            </button>
            <button
              v-if="canAssignWriter(selectedQueueOrder)"
              class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled(false, canAssignWriter(selectedQueueOrder)) || !Number(orderControl.writerId)"
              @click="openActionDialog('assign_writer')"
            >
              Assign writer
            </button>
            <button
              v-if="canReleaseToPool(selectedQueueOrder)"
              class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled(false, canReleaseToPool(selectedQueueOrder))"
              @click="openActionDialog('release_to_pool')"
            >
              Release to pool
            </button>
            <button
              v-if="canApproveDelivery(selectedQueueOrder)"
              class="focus-ring h-10 rounded-md border border-emerald-200 bg-white px-3 text-sm font-semibold text-emerald-800 disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled(false, canApproveDelivery(selectedQueueOrder))"
              @click="openActionDialog('approve_delivery')"
            >
              Approve delivery
            </button>
            <button
              v-if="canReturnToWriter(selectedQueueOrder)"
              class="focus-ring h-10 rounded-md border border-amber-200 bg-white px-3 text-sm font-semibold text-amber-900 disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled(true, canReturnToWriter(selectedQueueOrder))"
              @click="openActionDialog('return_to_writer')"
            >
              Return to writer
            </button>
            <button
              v-if="canRequestRevision(selectedQueueOrder)"
              class="focus-ring h-10 rounded-md border border-amber-200 bg-white px-3 text-sm font-semibold text-amber-900 disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled(true, canRequestRevision(selectedQueueOrder))"
              @click="openActionDialog('request_revision')"
            >
              Request revision
            </button>
            <button
              v-if="canCancelOrder(selectedQueueOrder)"
              class="focus-ring h-10 rounded-md border border-rose-200 bg-white px-3 text-sm font-semibold text-rose-700 disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled(true, canCancelOrder(selectedQueueOrder))"
              @click="openActionDialog('cancel_order')"
            >
              Cancel order
            </button>
            <button
              v-if="canArchiveOrder(selectedQueueOrder)"
              class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled(false, canArchiveOrder(selectedQueueOrder))"
              @click="openActionDialog('archive_order')"
            >
              Archive order
            </button>
            <p
              v-if="selectedQueueOrder && !canManualMarkPaid(selectedQueueOrder) && !canRouteToStaffing(selectedQueueOrder) && !canAssignWriter(selectedQueueOrder) && !canReleaseToPool(selectedQueueOrder) && !canApproveDelivery(selectedQueueOrder) && !canReturnToWriter(selectedQueueOrder) && !canRequestRevision(selectedQueueOrder) && !canCancelOrder(selectedQueueOrder) && !canArchiveOrder(selectedQueueOrder)"
              class="rounded-md border border-slate-200 bg-white px-3 py-2 text-xs text-graphite"
            >
              No direct staff action is available for this status.
            </p>
          </div>
        </div>

        <div v-if="ops.rows.length">
          <!-- Mobile cards -->
          <div class="divide-y divide-slate-100 sm:hidden">
            <div
              v-for="order in ops.rows"
              :key="order.id"
              class="px-4 py-3"
              :class="order.id === selectedQueueOrder?.id ? 'bg-slate-50' : ''"
            >
              <button class="w-full text-left" type="button" @click="selectQueueOrder(order)">
                <div class="flex items-start justify-between gap-2">
                  <p class="truncate font-semibold text-ink">#{{ order.id }} {{ order.topic }}</p>
                  <StatusPill :label="order.status" class="shrink-0" />
                </div>
                <div class="mt-1.5 flex flex-wrap gap-3 text-xs text-graphite">
                  <span>{{ order.payment_status || "unknown" }}</span>
                  <span>{{ formatDate(order.writer_deadline) }}</span>
                  <span>Client: {{ order.client_id || "External" }}</span>
                </div>
              </button>
              <div class="mt-2 flex gap-2">
                <button class="focus-ring flex-1 rounded-md border border-slate-200 py-1.5 text-xs font-semibold text-signal" type="button" @click="openOrderDetail(order)">Inspect</button>
                <button v-if="canRouteToStaffing(order)" class="focus-ring rounded-md border border-slate-200 px-3 py-1.5 text-xs" type="button" title="Route to staffing" @click="openActionDialog('route_to_staffing', order)"><Route class="h-4 w-4" /></button>
                <button v-if="canManualMarkPaid(order)" class="focus-ring rounded-md border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs text-emerald-700" type="button" title="Verify payment" @click="openActionDialog('manual_mark_paid', order)"><CircleDollarSign class="h-4 w-4" /></button>
                <button v-if="canReleaseToPool(order)" class="focus-ring rounded-md border border-slate-200 px-3 py-1.5 text-xs" type="button" title="Release to pool" @click="openActionDialog('release_to_pool', order)"><Layers3 class="h-4 w-4" /></button>
                <button v-if="canApproveDelivery(order)" class="focus-ring rounded-md border border-emerald-200 bg-emerald-50 px-3 py-1.5 text-xs text-emerald-700" type="button" title="Approve delivery" @click="openActionDialog('approve_delivery', order)"><CheckCircle2 class="h-4 w-4" /></button>
                <button v-if="canReturnToWriter(order)" class="focus-ring rounded-md border border-amber-200 bg-amber-50 px-3 py-1.5 text-xs text-amber-700" type="button" title="Return to writer" @click="openActionDialog('return_to_writer', order)"><RefreshCw class="h-4 w-4" /></button>
                <button v-if="canRequestRevision(order)" class="focus-ring rounded-md border border-amber-200 bg-white px-3 py-1.5 text-xs text-amber-700" type="button" title="Request revision" @click="openActionDialog('request_revision', order)"><Send class="h-4 w-4" /></button>
                <button v-if="canCancelOrder(order)" class="focus-ring rounded-md border border-rose-200 bg-rose-50 px-3 py-1.5 text-xs text-rose-700" type="button" title="Cancel order" @click="openActionDialog('cancel_order', order)"><XCircle class="h-4 w-4" /></button>
                <button v-if="canArchiveOrder(order)" class="focus-ring rounded-md border border-slate-200 px-3 py-1.5 text-xs" type="button" title="Archive" @click="openActionDialog('archive_order', order)"><Archive class="h-4 w-4" /></button>
              </div>
            </div>
          </div>

          <!-- Desktop table -->
          <div class="hidden overflow-x-auto sm:block">
            <table class="min-w-full divide-y divide-slate-200 text-sm">
              <thead class="bg-slate-50 text-left text-xs font-semibold uppercase text-graphite">
                <tr>
                  <th class="px-3 py-2">Order</th>
                  <th class="px-3 py-2">Status</th>
                  <th class="px-3 py-2">Payment</th>
                  <th class="px-3 py-2">Writer deadline</th>
                  <th class="px-3 py-2">Client</th>
                  <th class="px-3 py-2 text-right">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr
                  v-for="order in ops.rows"
                  :key="order.id"
                  class="cursor-pointer"
                  :class="order.id === selectedQueueOrder?.id ? 'bg-slate-50' : ''"
                  @click="selectQueueOrder(order)"
                >
                  <td class="px-3 py-2.5">
                    <p class="font-semibold text-ink">#{{ order.id }} {{ order.topic }}</p>
                    <p class="mt-1 text-xs text-graphite">Preferred writer: {{ order.preferred_writer_id || "None" }}</p>
                  </td>
                  <td class="px-3 py-2.5"><StatusPill :label="order.status" /></td>
                  <td class="px-3 py-2.5 text-graphite">{{ order.payment_status || "unknown" }}</td>
                  <td class="px-3 py-2.5 text-graphite">{{ formatDate(order.writer_deadline) }}</td>
                  <td class="px-3 py-2.5 text-graphite">{{ order.client_id || "External" }}</td>
                  <td class="px-3 py-2.5">
                    <div class="flex justify-end gap-2">
                      <button class="focus-ring inline-flex h-9 items-center justify-center rounded-md border border-slate-200 px-3 text-xs font-semibold text-signal" type="button" @click.stop="openOrderDetail(order)">Inspect</button>
                      <button v-if="canRouteToStaffing(order)" class="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200" type="button" title="Route to staffing" @click.stop="openActionDialog('route_to_staffing', order)"><Route class="h-4 w-4" /></button>
                      <button v-if="canManualMarkPaid(order)" class="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-md border border-emerald-200 bg-emerald-50 text-emerald-700" type="button" title="Verify payment" @click.stop="openActionDialog('manual_mark_paid', order)"><CircleDollarSign class="h-4 w-4" /></button>
                      <button v-if="canReleaseToPool(order)" class="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200" type="button" title="Release to pool" @click.stop="openActionDialog('release_to_pool', order)"><Layers3 class="h-4 w-4" /></button>
                      <button v-if="canApproveDelivery(order)" class="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-md border border-emerald-200 bg-emerald-50 text-emerald-700" type="button" title="Approve delivery" @click.stop="openActionDialog('approve_delivery', order)"><CheckCircle2 class="h-4 w-4" /></button>
                      <button v-if="canReturnToWriter(order)" class="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-md border border-amber-200 bg-amber-50 text-amber-700" type="button" title="Return to writer" @click.stop="openActionDialog('return_to_writer', order)"><RefreshCw class="h-4 w-4" /></button>
                      <button v-if="canRequestRevision(order)" class="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-md border border-amber-200 bg-white text-amber-700" type="button" title="Request revision" @click.stop="openActionDialog('request_revision', order)"><Send class="h-4 w-4" /></button>
                      <button v-if="canCancelOrder(order)" class="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-md border border-rose-200 bg-rose-50 text-rose-700" type="button" title="Cancel order" @click.stop="openActionDialog('cancel_order', order)"><XCircle class="h-4 w-4" /></button>
                      <button v-if="canArchiveOrder(order)" class="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200" type="button" title="Archive order" @click.stop="openActionDialog('archive_order', order)"><Archive class="h-4 w-4" /></button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-else class="p-4">
          <EmptyState
            :icon="ClipboardList"
            title="No queue rows loaded"
            message="Use refresh with a staff account connected to the backend, or switch queues to inspect the layout."
          />
        </div>
      </div>
    </section>

    <BaseModal
      :open="actionDialog.open"
      :title="currentActionCopy?.title ?? 'Confirm action'"
      :description="currentActionCopy?.description"
      size="md"
      @close="closeActionDialog"
    >
      <div v-if="actionDialog.order && currentActionCopy" class="space-y-4">
        <div
          class="rounded-lg border px-4 py-3"
          :class="{
            'border-slate-200 bg-slate-50': currentActionCopy.tone === 'neutral',
            'border-emerald-200 bg-emerald-50': currentActionCopy.tone === 'success',
            'border-amber-200 bg-amber-50': currentActionCopy.tone === 'warning',
            'border-rose-200 bg-rose-50': currentActionCopy.tone === 'danger',
          }"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="font-semibold text-ink">#{{ actionDialog.order.id }} {{ actionDialog.order.topic }}</p>
              <p class="mt-1 text-xs text-graphite">
                Client {{ actionDialog.order.client_id || "External" }} · Preferred writer {{ actionDialog.order.preferred_writer_id || "None" }}
              </p>
            </div>
            <StatusPill :label="actionDialog.order.status" />
          </div>
          <div class="mt-3 grid gap-2 text-xs text-graphite sm:grid-cols-3">
            <span>Payment: {{ actionDialog.order.payment_status || "unknown" }}</span>
            <span>Writer due: {{ formatDate(actionDialog.order.writer_deadline) }}</span>
            <span>{{ formatAmount(actionDialog.order.total_price, "USD") }}</span>
          </div>
        </div>

        <label v-if="currentActionCopy.requiresWriter" class="block text-sm font-medium text-ink">
          Writer ID <span class="text-rose-500">*</span>
          <input
            v-model.trim="actionDialog.writerId"
            class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
            inputmode="numeric"
            placeholder="Enter writer ID"
          >
        </label>

        <div v-if="actionDialog.action === 'manual_mark_paid'" class="grid gap-3 sm:grid-cols-2">
          <label class="block text-sm font-medium text-ink">
            Amount <span class="text-rose-500">*</span>
            <input
              v-model.trim="actionDialog.amount"
              class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
              inputmode="decimal"
              placeholder="0.00"
            >
          </label>
          <label class="block text-sm font-medium text-ink">
            Transaction reference <span class="text-rose-500">*</span>
            <input
              v-model.trim="actionDialog.transactionReference"
              class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
              placeholder="Gateway, bank, wallet, or receipt reference"
            >
          </label>
          <label class="block text-sm font-medium text-ink sm:col-span-2">
            Payment method
            <input
              v-model.trim="actionDialog.paymentMethod"
              class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
              placeholder="Stripe, bank transfer, M-Pesa, wallet, etc."
            >
          </label>
        </div>

        <label class="block text-sm font-medium text-ink">
          Operational note
          <span v-if="currentActionCopy.requiresNote" class="text-rose-500">*</span>
          <textarea
            v-model.trim="actionDialog.note"
            class="focus-ring mt-1 min-h-24 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
            :placeholder="currentActionCopy.requiresNote ? 'Add a clear reason or instruction for this action...' : 'Optional internal note for this action...'"
          />
          <span v-if="currentActionCopy.requiresNote" class="mt-1 block text-xs text-graphite">
            Minimum 10 characters. This gives the next user enough context.
          </span>
        </label>

        <div v-if="currentActionCopy.tone === 'danger'" class="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-800">
          This action can affect billing, refunds, staff queues, and user notifications. Confirm only after reviewing the order state.
        </div>
      </div>

      <template #footer>
        <div class="flex flex-wrap justify-end gap-2">
          <button
            class="focus-ring h-10 rounded-md border border-slate-200 px-4 text-sm font-semibold text-graphite hover:text-ink"
            type="button"
            @click="closeActionDialog"
          >
            Cancel
          </button>
          <button
            class="focus-ring h-10 rounded-md px-4 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
            :class="{
              'bg-ink hover:bg-slate-800': currentActionCopy?.tone === 'neutral',
              'bg-emerald-600 hover:bg-emerald-700': currentActionCopy?.tone === 'success',
              'bg-amber-600 hover:bg-amber-700': currentActionCopy?.tone === 'warning',
              'bg-rose-600 hover:bg-rose-700': currentActionCopy?.tone === 'danger',
            }"
            type="button"
            :disabled="!actionDialogCanSubmit"
            @click="confirmActionDialog"
          >
            {{ ops.isMutating ? "Working..." : currentActionCopy?.confirm }}
          </button>
        </div>
      </template>
    </BaseModal>

  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import {
  Archive,
  CheckCircle2,
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

function actionAllowed(order: OrderOpsRow | undefined, action: string, fallback: () => boolean) {
  if (order?.available_actions) return order.available_actions.includes(action);
  return fallback();
}

function canRouteToStaffing(order?: OrderOpsRow) {
  return actionAllowed(order, "route_to_staffing", () => ["paid", "unpaid", "pending_payment"].includes(orderStatus(order)));
}

function canAssignWriter(order?: OrderOpsRow) {
  return actionAllowed(order, "assign_writer", () => ["ready_for_staffing", "paid", "preferred_writer_pending"].includes(orderStatus(order)));
}

function canReleaseToPool(order?: OrderOpsRow) {
  return actionAllowed(order, "release_to_pool", () => ["ready_for_staffing", "preferred_writer_pending", "assigned"].includes(orderStatus(order)));
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
          @load="(f) => { work.query = String(f.query ?? ''); if (f.kind) work.activeKind = String(f.kind); }"
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
              v-if="canRouteToStaffing(selectedQueueOrder)"
              class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled(false, canRouteToStaffing(selectedQueueOrder))"
              @click="selectedQueueOrder && ops.routeToStaffing(selectedQueueOrder.id).catch(() => undefined)"
            >
              Route to staffing
            </button>
            <button
              v-if="canAssignWriter(selectedQueueOrder)"
              class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled(false, canAssignWriter(selectedQueueOrder)) || !Number(orderControl.writerId)"
              @click="selectedQueueOrder && ops.assignDirect(selectedQueueOrder.id, Number(orderControl.writerId), orderControl.note).catch(() => undefined)"
            >
              Assign writer
            </button>
            <button
              v-if="canReleaseToPool(selectedQueueOrder)"
              class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled(false, canReleaseToPool(selectedQueueOrder))"
              @click="selectedQueueOrder && ops.releaseToPool(selectedQueueOrder.id, orderControl.note).catch(() => undefined)"
            >
              Release to pool
            </button>
            <button
              v-if="canApproveDelivery(selectedQueueOrder)"
              class="focus-ring h-10 rounded-md border border-emerald-200 bg-white px-3 text-sm font-semibold text-emerald-800 disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled(false, canApproveDelivery(selectedQueueOrder))"
              @click="selectedQueueOrder && ops.approveForDelivery(selectedQueueOrder.id, orderControl.note).catch(() => undefined)"
            >
              Approve delivery
            </button>
            <button
              v-if="canReturnToWriter(selectedQueueOrder)"
              class="focus-ring h-10 rounded-md border border-amber-200 bg-white px-3 text-sm font-semibold text-amber-900 disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled(true, canReturnToWriter(selectedQueueOrder))"
              @click="selectedQueueOrder && ops.returnToWriter(selectedQueueOrder.id, orderControl.note).catch(() => undefined)"
            >
              Return to writer
            </button>
            <button
              v-if="canRequestRevision(selectedQueueOrder)"
              class="focus-ring h-10 rounded-md border border-amber-200 bg-white px-3 text-sm font-semibold text-amber-900 disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled(true, canRequestRevision(selectedQueueOrder))"
              @click="selectedQueueOrder && ops.requestRevision(selectedQueueOrder.id, orderControl.note).catch(() => undefined)"
            >
              Request revision
            </button>
            <button
              v-if="canCancelOrder(selectedQueueOrder)"
              class="focus-ring h-10 rounded-md border border-rose-200 bg-white px-3 text-sm font-semibold text-rose-700 disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled(true, canCancelOrder(selectedQueueOrder))"
              @click="selectedQueueOrder && ops.cancel(selectedQueueOrder.id, orderControl.note).catch(() => undefined)"
            >
              Cancel order
            </button>
            <button
              v-if="canArchiveOrder(selectedQueueOrder)"
              class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled(false, canArchiveOrder(selectedQueueOrder))"
              @click="selectedQueueOrder && ops.archive(selectedQueueOrder.id).catch(() => undefined)"
            >
              Archive order
            </button>
            <p
              v-if="selectedQueueOrder && !canRouteToStaffing(selectedQueueOrder) && !canAssignWriter(selectedQueueOrder) && !canReleaseToPool(selectedQueueOrder) && !canApproveDelivery(selectedQueueOrder) && !canReturnToWriter(selectedQueueOrder) && !canRequestRevision(selectedQueueOrder) && !canCancelOrder(selectedQueueOrder) && !canArchiveOrder(selectedQueueOrder)"
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
                <button v-if="canRouteToStaffing(order)" class="focus-ring rounded-md border border-slate-200 px-3 py-1.5 text-xs" type="button" title="Route to staffing" @click="ops.routeToStaffing(order.id).catch(() => undefined)"><Route class="h-4 w-4" /></button>
                <button v-if="canArchiveOrder(order)" class="focus-ring rounded-md border border-slate-200 px-3 py-1.5 text-xs" type="button" title="Archive" @click="ops.archive(order.id).catch(() => undefined)"><Archive class="h-4 w-4" /></button>
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
                      <button v-if="canRouteToStaffing(order)" class="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200" type="button" title="Route to staffing" @click="ops.routeToStaffing(order.id).catch(() => undefined)"><Route class="h-4 w-4" /></button>
                      <button v-if="canArchiveOrder(order)" class="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200" type="button" title="Archive order" @click="ops.archive(order.id).catch(() => undefined)"><Archive class="h-4 w-4" /></button>
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

  </div>
</template>

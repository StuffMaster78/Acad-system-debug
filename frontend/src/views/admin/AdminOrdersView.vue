<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
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

function orderControlDisabled(requireNote = false) {
  return !selectedQueueOrder.value || ops.isMutating || (requireNote && orderControl.note.trim().length < 10);
}

async function openOrderDetail(context: AdminWorkItem | OrderOpsRow) {
  detailContext.value = context;
  detailOpen.value = true;
  detailBundle.value = {};
  if (!isWorkItem(context) || context.kind === "order") {
    await orderDetails.fetchOrder(context.id).catch(() => undefined);
    return;
  }

  detailLoading.value = true;
  try {
    if (context.kind === "special_order") {
      const [detailRes, deliverablesRes, checkpointsRes] = await Promise.allSettled([
        adminWorkApi.specialOrder(context.id),
        adminWorkApi.specialDeliverables(context.id),
        adminWorkApi.specialDeliveryCheckpoints(context.id),
      ]);
      detailBundle.value = {
        detail: detailRes.status === "fulfilled" ? detailRes.value.data : undefined,
        tasks: checkpointsRes.status === "fulfilled" ? normalizeMaybeResults(checkpointsRes.value.data) : [],
        portalWorkLogs: deliverablesRes.status === "fulfilled" ? normalizeMaybeResults(deliverablesRes.value.data) : [],
      };
    } else if (context.kind === "class_order") {
      const [
        detailRes,
        tasksRes,
        milestonesRes,
        assignmentsRes,
        timelineRes,
        accessLogsRes,
        portalLogsRes,
        compensationRes,
      ] = await Promise.allSettled([
        adminWorkApi.classOrder(context.id),
        adminWorkApi.classTasks(context.id),
        adminWorkApi.classPaymentMilestones(context.id),
        adminWorkApi.classAssignments(context.id),
        adminWorkApi.classTimeline(context.id),
        adminWorkApi.classAccessLogs(context.id),
        adminWorkApi.classPortalWorkLogs(context.id),
        adminWorkApi.classWriterCompensation(context.id),
      ]);
      detailBundle.value = {
        detail: detailRes.status === "fulfilled" ? detailRes.value.data : undefined,
        tasks: tasksRes.status === "fulfilled" ? normalizeMaybeResults(tasksRes.value.data) : [],
        milestones: milestonesRes.status === "fulfilled" ? normalizeMaybeResults(milestonesRes.value.data) : [],
        assignments: assignmentsRes.status === "fulfilled" ? normalizeMaybeResults(assignmentsRes.value.data) : [],
        timeline: timelineRes.status === "fulfilled" ? normalizeMaybeResults(timelineRes.value.data) : [],
        accessLogs: accessLogsRes.status === "fulfilled" ? normalizeMaybeResults(accessLogsRes.value.data) : [],
        portalWorkLogs: portalLogsRes.status === "fulfilled" ? normalizeMaybeResults(portalLogsRes.value.data) : [],
        writerCompensation: compensationRes.status === "fulfilled" ? normalizeMaybeResults(compensationRes.value.data) : [],
      };
    }
  } finally {
    detailLoading.value = false;
  }
}

function closeOrderDetail() {
  detailOpen.value = false;
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

    <section class="rounded-md border border-slate-200 bg-white">
      <div class="flex flex-col gap-4 border-b border-slate-200 px-4 py-4 xl:flex-row xl:items-center xl:justify-between">
        <div>
          <div class="flex items-center gap-2">
            <Layers3 class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold">All client-site work</h2>
          </div>
          <p class="mt-1 text-sm text-graphite">
            Normal orders, special orders, and class commitments with client and writer ownership.
          </p>
        </div>

        <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
          <div class="inline-flex rounded-md border border-slate-200 bg-slate-50 p-1">
            <button
              v-for="tab in workTabs"
              :key="tab.key"
              class="focus-ring min-h-9 rounded px-3 text-sm font-semibold"
              :class="work.activeKind === tab.key ? 'bg-white text-ink shadow-sm' : 'text-graphite'"
              type="button"
              @click="work.activeKind = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>
          <label class="relative block min-w-64">
            <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-graphite" />
            <input
              v-model="work.query"
              class="focus-ring h-10 w-full rounded-md border border-slate-200 bg-white pl-9 pr-3 text-sm"
              type="search"
              placeholder="Search site, client, writer, status"
            >
          </label>
        </div>
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
              class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled()"
              @click="selectedQueueOrder && ops.routeToStaffing(selectedQueueOrder.id).catch(() => undefined)"
            >
              Route to staffing
            </button>
            <button
              class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled() || !Number(orderControl.writerId)"
              @click="selectedQueueOrder && ops.assignDirect(selectedQueueOrder.id, Number(orderControl.writerId), orderControl.note).catch(() => undefined)"
            >
              Assign writer
            </button>
            <button
              class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled()"
              @click="selectedQueueOrder && ops.releaseToPool(selectedQueueOrder.id, orderControl.note).catch(() => undefined)"
            >
              Release to pool
            </button>
            <button
              class="focus-ring h-10 rounded-md border border-emerald-200 bg-white px-3 text-sm font-semibold text-emerald-800 disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled()"
              @click="selectedQueueOrder && ops.approveForDelivery(selectedQueueOrder.id, orderControl.note).catch(() => undefined)"
            >
              Approve delivery
            </button>
            <button
              class="focus-ring h-10 rounded-md border border-amber-200 bg-white px-3 text-sm font-semibold text-amber-900 disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled(true)"
              @click="selectedQueueOrder && ops.returnToWriter(selectedQueueOrder.id, orderControl.note).catch(() => undefined)"
            >
              Return to writer
            </button>
            <button
              class="focus-ring h-10 rounded-md border border-amber-200 bg-white px-3 text-sm font-semibold text-amber-900 disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled(true)"
              @click="selectedQueueOrder && ops.requestRevision(selectedQueueOrder.id, orderControl.note).catch(() => undefined)"
            >
              Request revision
            </button>
            <button
              class="focus-ring h-10 rounded-md border border-rose-200 bg-white px-3 text-sm font-semibold text-rose-700 disabled:opacity-60"
              type="button"
              :disabled="orderControlDisabled(true)"
              @click="selectedQueueOrder && ops.cancel(selectedQueueOrder.id, orderControl.note).catch(() => undefined)"
            >
              Cancel order
            </button>
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
                <button v-if="ops.activeQueue === 'pending_staffing'" class="focus-ring rounded-md border border-slate-200 px-3 py-1.5 text-xs" type="button" title="Route to staffing" @click="ops.routeToStaffing(order.id).catch(() => undefined)"><Route class="h-4 w-4" /></button>
                <button v-if="ops.activeQueue === 'eligible_for_archive'" class="focus-ring rounded-md border border-slate-200 px-3 py-1.5 text-xs" type="button" title="Archive" @click="ops.archive(order.id).catch(() => undefined)"><Archive class="h-4 w-4" /></button>
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
                      <button v-if="ops.activeQueue === 'pending_staffing'" class="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200" type="button" title="Route to staffing" @click="ops.routeToStaffing(order.id).catch(() => undefined)"><Route class="h-4 w-4" /></button>
                      <button v-if="ops.activeQueue === 'eligible_for_archive'" class="focus-ring inline-flex h-9 w-9 items-center justify-center rounded-md border border-slate-200" type="button" title="Archive order" @click="ops.archive(order.id).catch(() => undefined)"><Archive class="h-4 w-4" /></button>
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
      :open="detailOpen"
      :title="detailTitle"
      description="Operational context, lifecycle state, assignment/payment signals, and controlled actions."
      size="full"
      @close="closeOrderDetail"
    >
      <div class="space-y-4">
        <div v-if="orderDetails.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
          {{ orderDetails.error }}
        </div>
        <div v-if="ops.notice || orderDetails.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
          {{ ops.notice || orderDetails.notice }}
        </div>

        <section class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          <div class="rounded-md border border-slate-200 p-4">
            <p class="text-xs font-semibold uppercase text-graphite">Status</p>
            <div class="mt-3 flex flex-wrap gap-2">
              <StatusPill :label="detailStatus" :tone="workTone({ status: detailStatus, assignedWriter: 'Assigned', deadline: null, isPaused: false } as AdminWorkItem)" />
              <StatusPill :label="detailPaymentStatus || 'payment unknown'" />
            </div>
          </div>
          <div class="rounded-md border border-slate-200 p-4">
            <p class="text-xs font-semibold uppercase text-graphite">Value</p>
            <p class="mt-3 text-2xl font-semibold text-ink">{{ formatAmount(detailAmount, detailCurrency) }}</p>
          </div>
          <div class="rounded-md border border-slate-200 p-4">
            <p class="text-xs font-semibold uppercase text-graphite">Writer deadline</p>
            <p class="mt-3 font-semibold text-ink">
              {{ formatDate(orderDetails.selectedOrder?.writer_deadline ?? ('writer_deadline' in (detailContext || {}) ? (detailContext as OrderOpsRow).writer_deadline : null)) }}
            </p>
          </div>
          <div class="rounded-md border border-slate-200 p-4">
            <p class="text-xs font-semibold uppercase text-graphite">Client deadline</p>
            <p class="mt-3 font-semibold text-ink">
              {{ formatDate(orderDetails.selectedOrder?.client_deadline ?? ('client_deadline' in (detailContext || {}) ? (detailContext as OrderOpsRow).client_deadline : null)) }}
            </p>
          </div>
        </section>

        <p v-if="detailLoading" class="rounded-md border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-graphite">
          Loading deeper backend detail...
        </p>

        <section
          v-if="!detailContext || !isWorkItem(detailContext) || detailContext.kind === 'order'"
          class="space-y-4"
        >
          <div class="grid gap-4 xl:grid-cols-3">
            <section class="rounded-md border border-slate-200 p-4">
              <h3 class="text-sm font-semibold uppercase text-graphite">Core identity</h3>
              <dl class="mt-3 space-y-2 text-sm">
                <div class="flex justify-between gap-3"><dt class="text-graphite">Order ID</dt><dd class="font-semibold text-ink">#{{ detailOrderId }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Tenant website</dt><dd class="font-semibold text-ink">{{ websites.nameById(orderDetails.selectedLifecycle?.website_id) }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Client</dt><dd class="font-semibold text-ink">{{ orderDetails.selectedOrder?.client_username || orderDetails.selectedOrder?.client_email || orderDetails.selectedLifecycle?.client_id || 'Not loaded' }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Service type</dt><dd class="font-semibold text-ink">{{ orderDetails.selectedOrder?.service_code || orderDetails.selectedOrder?.service_family || 'Not loaded' }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Subject</dt><dd class="font-semibold text-ink">{{ orderDetails.selectedOrder?.subject || ('subject' in (detailContext || {}) ? (detailContext as AdminWorkItem).subject : '') || 'Not loaded' }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Urgency</dt><dd class="font-semibold text-ink">{{ orderDetails.selectedOrder?.is_urgent ? 'Urgent' : 'Standard' }}</dd></div>
              </dl>
            </section>

            <section class="rounded-md border border-slate-200 p-4">
              <h3 class="text-sm font-semibold uppercase text-graphite">Instructions</h3>
              <dl class="mt-3 space-y-2 text-sm">
                <div class="flex justify-between gap-3"><dt class="text-graphite">Topic</dt><dd class="font-semibold text-ink">{{ orderDetails.selectedOrder?.topic || detailTitle }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Pages</dt><dd class="font-semibold text-ink">{{ orderDetails.selectedOrder?.number_of_pages ?? 'Not loaded' }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Slides</dt><dd class="font-semibold text-ink">{{ orderDetails.selectedOrder?.number_of_slides ?? '0' }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Sources</dt><dd class="font-semibold text-ink">{{ orderDetails.selectedOrder?.number_of_refereces ?? 'Not loaded' }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Spacing</dt><dd class="font-semibold text-ink">{{ orderDetails.selectedOrder?.spacing || 'Not loaded' }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Citation/style</dt><dd class="font-semibold text-ink">{{ orderDetails.selectedOrder?.formatting_style || 'Not loaded' }}</dd></div>
              </dl>
            </section>

            <section class="rounded-md border border-slate-200 p-4">
              <h3 class="text-sm font-semibold uppercase text-graphite">Pricing and payment</h3>
              <dl class="mt-3 space-y-2 text-sm">
                <div class="flex justify-between gap-3"><dt class="text-graphite">Total</dt><dd class="font-semibold text-ink">{{ formatAmount(orderDetails.selectedOrder?.total_price ?? detailAmount, detailCurrency) }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Paid</dt><dd class="font-semibold text-ink">{{ formatAmount(orderDetails.selectedOrder?.amount_paid, detailCurrency) }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Balance</dt><dd class="font-semibold text-ink">{{ formatAmount(orderDetails.selectedOrder?.remaining_balance, detailCurrency) }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Writer estimate</dt><dd class="font-semibold text-ink">{{ formatAmount(orderDetails.selectedOrder?.writer_compensation, detailCurrency) }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Discount</dt><dd class="font-semibold text-ink">{{ orderDetails.selectedOrder?.discount_code_used || 'None' }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Payment</dt><dd class="font-semibold text-ink">{{ detailPaymentStatus || 'Not loaded' }}</dd></div>
              </dl>
            </section>
          </div>

          <div class="grid gap-4 xl:grid-cols-3">
            <section class="rounded-md border border-slate-200 p-4">
              <h3 class="text-sm font-semibold uppercase text-graphite">Staffing</h3>
              <dl class="mt-3 space-y-2 text-sm">
                <div class="flex justify-between gap-3"><dt class="text-graphite">Assigned writer</dt><dd class="font-semibold text-ink">{{ orderDetails.selectedOrder?.writer_username || orderDetails.selectedLifecycle?.current_writer_id || 'Unassigned' }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Preferred writer</dt><dd class="font-semibold text-ink">{{ orderDetails.selectedOrder?.preferred_writer || ('preferred_writer_id' in (detailContext || {}) ? (detailContext as OrderOpsRow).preferred_writer_id : '') || 'None' }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Pool state</dt><dd class="font-semibold text-ink">{{ ('preferred_writer_status' in (detailContext || {}) ? (detailContext as OrderOpsRow).preferred_writer_status : '') || detailStatus }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Reassignment</dt><dd class="font-semibold text-ink">{{ orderDetails.selectedLifecycle?.has_pending_reassignment_request ? `#${orderDetails.selectedLifecycle.pending_reassignment_request_id}` : 'None pending' }}</dd></div>
              </dl>
            </section>

            <section class="rounded-md border border-slate-200 p-4">
              <h3 class="text-sm font-semibold uppercase text-graphite">Timeline</h3>
              <dl class="mt-3 space-y-2 text-sm">
                <div class="flex justify-between gap-3"><dt class="text-graphite">Placed</dt><dd class="font-semibold text-ink">{{ formatDate(orderDetails.selectedOrder?.created_at || ('createdAt' in (detailContext || {}) ? (detailContext as AdminWorkItem).createdAt : null)) }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Updated</dt><dd class="font-semibold text-ink">{{ formatDate(orderDetails.selectedOrder?.updated_at || null) }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Draft due</dt><dd class="font-semibold text-ink">{{ formatDate(orderDetails.selectedOrder?.writer_deadline || null) }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Final deadline</dt><dd class="font-semibold text-ink">{{ formatDate(orderDetails.selectedOrder?.client_deadline || null) }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Revision window</dt><dd class="font-semibold text-ink">{{ orderDetails.selectedLifecycle?.revision_window_days ?? 0 }} days</dd></div>
              </dl>
            </section>

            <section class="rounded-md border border-slate-200 p-4">
              <h3 class="text-sm font-semibold uppercase text-graphite">Risk and audit</h3>
              <dl class="mt-3 space-y-2 text-sm">
                <div class="flex justify-between gap-3"><dt class="text-graphite">Hold</dt><dd class="font-semibold text-ink">{{ orderDetails.selectedLifecycle?.has_active_hold ? `Hold #${orderDetails.selectedLifecycle.active_hold_id}` : 'No active hold' }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Dispute</dt><dd class="font-semibold text-ink">{{ orderDetails.selectedLifecycle?.has_active_dispute ? `Dispute #${orderDetails.selectedLifecycle.active_dispute_id}` : 'No active dispute' }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Revision</dt><dd class="font-semibold text-ink">{{ orderDetails.selectedLifecycle?.latest_revision_status || 'None' }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Flags</dt><dd class="font-semibold text-ink">{{ orderDetails.selectedOrder?.flags?.length ? orderDetails.selectedOrder.flags.join(', ') : 'None loaded' }}</dd></div>
              </dl>
            </section>
          </div>
        </section>

        <section v-else-if="detailContext.kind === 'special_order'" class="space-y-4">
          <div class="grid gap-4 xl:grid-cols-3">
            <section class="rounded-md border border-slate-200 p-4">
              <h3 class="text-sm font-semibold uppercase text-graphite">Special order identity</h3>
              <dl class="mt-3 space-y-2 text-sm">
                <div class="flex justify-between gap-3"><dt class="text-graphite">Special order ID</dt><dd class="font-semibold text-ink">SPO-{{ detailOrderId }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Client</dt><dd class="font-semibold text-ink">{{ specialDetail?.client_name || detailContext.client }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Tenant website</dt><dd class="font-semibold text-ink">{{ detailContext.website }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Pricing mode</dt><dd class="font-semibold text-ink">{{ specialDetail?.pricing_mode || detailContext.paymentStatus || 'Not loaded' }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Priority</dt><dd class="font-semibold text-ink">{{ specialDetail?.priority || detailContext.priority || 'normal' }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Writer/team</dt><dd class="font-semibold text-ink">{{ specialDetail?.writer_name || detailContext.assignedWriter }}</dd></div>
              </dl>
            </section>
            <section class="rounded-md border border-slate-200 p-4">
              <h3 class="text-sm font-semibold uppercase text-graphite">Request details</h3>
              <p class="mt-3 whitespace-pre-wrap text-sm leading-6 text-graphite">{{ specialDetail?.inquiry_details || detailContext.notes || 'No request detail loaded.' }}</p>
              <dl class="mt-3 space-y-2 text-sm">
                <div class="flex justify-between gap-3"><dt class="text-graphite">Custom service</dt><dd class="font-semibold text-ink">{{ specialDetail?.predefined_config_name || detailContext.subject || 'Custom' }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Duration</dt><dd class="font-semibold text-ink">{{ specialDetail?.duration_days || 'Not set' }} day(s)</dd></div>
              </dl>
            </section>
            <section class="rounded-md border border-slate-200 p-4">
              <h3 class="text-sm font-semibold uppercase text-graphite">Pricing and ledger</h3>
              <dl class="mt-3 space-y-2 text-sm">
                <div class="flex justify-between gap-3"><dt class="text-graphite">Client budget</dt><dd class="font-semibold text-ink">{{ formatAmount(specialDetail?.budget ?? detailContext.amount, specialDetail?.currency || detailContext.currency) }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Accepted quote</dt><dd class="font-semibold text-ink">{{ specialDetail?.accepted_quote ? `Quote #${specialDetail.accepted_quote}` : 'Not accepted' }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Converted order</dt><dd class="font-semibold text-ink">{{ specialDetail?.converted_order ? `ORD-${specialDetail.converted_order}` : 'Not converted' }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Writer pay rule</dt><dd class="font-semibold text-ink">{{ specialDetail?.writer_pay_rule || 'Not loaded' }}</dd></div>
              </dl>
            </section>
          </div>
          <div class="grid gap-4 xl:grid-cols-3">
            <section class="rounded-md border border-slate-200 p-4">
              <h3 class="text-sm font-semibold uppercase text-graphite">Milestones and deliverables</h3>
              <div class="mt-3 space-y-2">
                <p v-if="!detailBundle.portalWorkLogs?.length" class="text-sm text-graphite">No deliverables loaded yet.</p>
                <article v-for="record in detailBundle.portalWorkLogs" :key="String(record.id)" class="rounded-md border border-slate-200 p-3 text-sm">
                  <p class="font-semibold text-ink">{{ firstRecordLabel(record) }}</p>
                  <p class="mt-1 text-xs text-graphite">{{ valueOf(record, ['status', 'delivery_status', 'approval_status']) }}</p>
                </article>
              </div>
            </section>
            <section class="rounded-md border border-slate-200 p-4">
              <h3 class="text-sm font-semibold uppercase text-graphite">Sensitive access</h3>
              <p class="mt-3 text-sm leading-6 text-graphite">
                Backend exposes vaults, access grants, access logs, external links, and 2FA requests. Detail reveal should remain admin-only and audited.
              </p>
            </section>
            <section class="rounded-md border border-slate-200 p-4">
              <h3 class="text-sm font-semibold uppercase text-graphite">Audit and compliance</h3>
              <dl class="mt-3 space-y-2 text-sm">
                <div class="flex justify-between gap-3"><dt class="text-graphite">Assigned</dt><dd class="font-semibold text-ink">{{ formatDate(specialDetail?.assigned_at || null) }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Started</dt><dd class="font-semibold text-ink">{{ formatDate(specialDetail?.started_at || null) }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Completed</dt><dd class="font-semibold text-ink">{{ formatDate(specialDetail?.completed_at || null) }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Cancelled</dt><dd class="font-semibold text-ink">{{ formatDate(specialDetail?.cancelled_at || null) }}</dd></div>
              </dl>
            </section>
          </div>
        </section>

        <section v-else-if="detailContext.kind === 'class_order'" class="space-y-4">
          <div class="grid gap-4 xl:grid-cols-3">
            <section class="rounded-md border border-slate-200 p-4">
              <h3 class="text-sm font-semibold uppercase text-graphite">Class identity</h3>
              <dl class="mt-3 space-y-2 text-sm">
                <div class="flex justify-between gap-3"><dt class="text-graphite">Class ID</dt><dd class="font-semibold text-ink">CLS-{{ detailOrderId }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Client</dt><dd class="font-semibold text-ink">{{ classDetail?.client_name || detailContext.client }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Institution</dt><dd class="font-semibold text-ink">{{ classDetail?.institution_name || detailContext.website }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Course</dt><dd class="font-semibold text-ink">{{ classDetail?.class_name || detailContext.title }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Course code</dt><dd class="font-semibold text-ink">{{ classDetail?.class_code || 'Not set' }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Subject</dt><dd class="font-semibold text-ink">{{ classDetail?.class_subject || detailContext.subject || 'Not set' }}</dd></div>
              </dl>
            </section>
            <section class="rounded-md border border-slate-200 p-4">
              <h3 class="text-sm font-semibold uppercase text-graphite">Portal access</h3>
              <p class="mt-3 text-sm leading-6 text-graphite">
                Backend exposes access details, grants, logs, 2FA windows, and 2FA requests. Credentials should stay hidden until a staff user explicitly reveals them.
              </p>
              <p class="mt-3 text-xs font-semibold text-graphite">{{ detailBundle.accessLogs?.length ?? 0 }} access log record(s) loaded.</p>
            </section>
            <section class="rounded-md border border-slate-200 p-4">
              <h3 class="text-sm font-semibold uppercase text-graphite">Pricing and billing</h3>
              <dl class="mt-3 space-y-2 text-sm">
                <div class="flex justify-between gap-3"><dt class="text-graphite">Quoted</dt><dd class="font-semibold text-ink">{{ formatAmount(classDetail?.quoted_amount, classDetail?.currency || detailContext.currency) }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Accepted</dt><dd class="font-semibold text-ink">{{ formatAmount(classDetail?.accepted_amount, classDetail?.currency || detailContext.currency) }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Paid</dt><dd class="font-semibold text-ink">{{ formatAmount(classDetail?.paid_amount, classDetail?.currency || detailContext.currency) }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Balance</dt><dd class="font-semibold text-ink">{{ formatAmount(classDetail?.balance_amount, classDetail?.currency || detailContext.currency) }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Milestones</dt><dd class="font-semibold text-ink">{{ detailBundle.milestones?.length ?? 0 }}</dd></div>
              </dl>
            </section>
          </div>

          <div class="grid gap-4 xl:grid-cols-3">
            <section class="rounded-md border border-slate-200 p-4">
              <h3 class="text-sm font-semibold uppercase text-graphite">Scope of work</h3>
              <p class="mt-3 whitespace-pre-wrap text-sm leading-6 text-graphite">{{ classDetail?.initial_client_notes || classDetail?.writer_visible_notes || 'No class scope notes loaded.' }}</p>
              <p class="mt-3 text-xs text-graphite">Complexity: {{ classDetail?.complexity_level || 'Not set' }}</p>
            </section>
            <section class="rounded-md border border-slate-200 p-4">
              <h3 class="text-sm font-semibold uppercase text-graphite">Task board</h3>
              <div class="mt-3 space-y-2">
                <p v-if="!detailBundle.tasks?.length" class="text-sm text-graphite">No class tasks loaded yet.</p>
                <article v-for="record in detailBundle.tasks" :key="String(record.id)" class="rounded-md border border-slate-200 p-3 text-sm">
                  <p class="font-semibold text-ink">{{ firstRecordLabel(record) }}</p>
                  <p class="mt-1 text-xs text-graphite">{{ valueOf(record, ['status', 'task_type', 'due_at', 'due_date']) }}</p>
                </article>
              </div>
            </section>
            <section class="rounded-md border border-slate-200 p-4">
              <h3 class="text-sm font-semibold uppercase text-graphite">Risk controls</h3>
              <dl class="mt-3 space-y-2 text-sm">
                <div class="flex justify-between gap-3"><dt class="text-graphite">Work paused</dt><dd class="font-semibold text-ink">{{ classDetail?.is_work_paused ? 'Yes' : 'No' }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Pause reason</dt><dd class="font-semibold text-ink">{{ classDetail?.pause_reason || 'None' }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Portal logs</dt><dd class="font-semibold text-ink">{{ detailBundle.portalWorkLogs?.length ?? 0 }}</dd></div>
                <div class="flex justify-between gap-3"><dt class="text-graphite">Timeline events</dt><dd class="font-semibold text-ink">{{ detailBundle.timeline?.length ?? 0 }}</dd></div>
              </dl>
            </section>
          </div>
        </section>

        <section class="grid gap-4 xl:grid-cols-[1fr_360px]">
          <div class="rounded-md border border-slate-200 p-4">
            <h3 class="text-base font-semibold text-ink">Lifecycle and context</h3>
            <div class="mt-4 grid gap-3 md:grid-cols-2">
              <div class="rounded-md border border-slate-200 p-3">
                <p class="text-xs text-graphite">Current assignment</p>
                <p class="mt-1 font-semibold text-ink">
                  {{ orderDetails.selectedLifecycle?.has_current_assignment ? `Writer #${orderDetails.selectedLifecycle.current_writer_id}` : "No active assignment" }}
                </p>
              </div>
              <div class="rounded-md border border-slate-200 p-3">
                <p class="text-xs text-graphite">Reassignment</p>
                <p class="mt-1 font-semibold text-ink">
                  {{ orderDetails.selectedLifecycle?.has_pending_reassignment_request ? `Request #${orderDetails.selectedLifecycle.pending_reassignment_request_id}` : "None pending" }}
                </p>
              </div>
              <div class="rounded-md border border-slate-200 p-3">
                <p class="text-xs text-graphite">Hold</p>
                <p class="mt-1 font-semibold text-ink">
                  {{ orderDetails.selectedLifecycle?.has_active_hold ? `Hold #${orderDetails.selectedLifecycle.active_hold_id}` : "No active hold" }}
                </p>
              </div>
              <div class="rounded-md border border-slate-200 p-3">
                <p class="text-xs text-graphite">Dispute</p>
                <p class="mt-1 font-semibold text-ink">
                  {{ orderDetails.selectedLifecycle?.has_active_dispute ? `Dispute #${orderDetails.selectedLifecycle.active_dispute_id}` : "No active dispute" }}
                </p>
              </div>
              <div class="rounded-md border border-slate-200 p-3">
                <p class="text-xs text-graphite">Revision state</p>
                <p class="mt-1 font-semibold text-ink">
                  {{ orderDetails.selectedLifecycle?.latest_revision_status || "No revision request" }}
                </p>
              </div>
              <div class="rounded-md border border-slate-200 p-3">
                <p class="text-xs text-graphite">Adjustment state</p>
                <p class="mt-1 font-semibold text-ink">
                  {{ orderDetails.selectedLifecycle?.latest_adjustment_status || "No adjustment request" }}
                </p>
              </div>
            </div>

            <div class="mt-4 rounded-md border border-slate-200 p-3">
              <p class="text-xs font-semibold uppercase text-graphite">Instructions</p>
              <p class="mt-2 whitespace-pre-wrap text-sm leading-6 text-graphite">
                {{ orderDetails.selectedOrder?.order_instructions || orderDetails.selectedOrder?.instructions || ('notes' in (detailContext || {}) ? (detailContext as AdminWorkItem).notes : '') || "No instructions loaded for this record yet." }}
              </p>
            </div>
          </div>

          <aside class="rounded-md border border-slate-200 p-4">
            <h3 class="text-base font-semibold text-ink">Detail actions</h3>
            <label class="mt-4 block text-sm font-medium text-ink">
              Audit note
              <textarea
                v-model.trim="detailNote"
                class="focus-ring mt-2 min-h-24 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
              />
            </label>
            <div class="mt-4 grid gap-2">
              <button
                class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
                type="button"
                :disabled="ops.isMutating"
                @click="ops.routeToStaffing(Number(detailOrderId)).catch(() => undefined)"
              >
                <Route class="h-4 w-4" />
                Route to staffing
              </button>
              <button
                class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-emerald-200 bg-white px-3 text-sm font-semibold text-emerald-800 disabled:opacity-60"
                type="button"
                :disabled="ops.isMutating"
                @click="approveDetailOrder"
              >
                <CheckCircle2 class="h-4 w-4" />
                Approve delivery
              </button>
              <button
                class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-amber-200 bg-white px-3 text-sm font-semibold text-amber-900 disabled:opacity-60"
                type="button"
                :disabled="ops.isMutating || detailNote.length < 10"
                @click="returnDetailOrder"
              >
                <Send class="h-4 w-4" />
                Return to writer
              </button>
              <button
                class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-rose-200 bg-white px-3 text-sm font-semibold text-rose-700 disabled:opacity-60"
                type="button"
                :disabled="ops.isMutating || detailNote.length < 10"
                @click="ops.cancel(Number(detailOrderId), detailNote).catch(() => undefined)"
              >
                <XCircle class="h-4 w-4" />
                Cancel order
              </button>
              <button
                class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
                type="button"
                :disabled="ops.isMutating"
                @click="ops.archive(Number(detailOrderId)).catch(() => undefined)"
              >
                <Archive class="h-4 w-4" />
                Archive
              </button>
            </div>
          </aside>
        </section>
      </div>
    </BaseModal>
  </div>
</template>

import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { orderOpsApi } from "@/api/orderOps";
import { useAuthStore } from "@/stores/auth";
import type {
  OrderOpsCounts,
  OrderOpsQueueDefinition,
  OrderOpsQueueKey,
  OrderOpsRow,
} from "@/types/orderOps";

export const queueDefinitions: OrderOpsQueueDefinition[] = [
  {
    key: "late",
    countKey: "late_orders",
    label: "Late",
    description: "In-progress orders past writer deadline.",
    tone: "risk",
  },
  {
    key: "critical",
    countKey: "critical_orders",
    label: "Critical",
    description: "Urgent in-progress orders needing attention.",
    tone: "risk",
  },
  {
    key: "pending_staffing",
    countKey: "pending_staffing",
    label: "Pending staffing",
    description: "Paid orders ready for writer assignment.",
    tone: "warn",
  },
  {
    key: "awaiting_approval",
    countKey: "awaiting_approval",
    label: "Awaiting approval",
    description: "Submitted orders awaiting client or staff approval.",
    tone: "warn",
  },
  {
    key: "awaiting_acknowledgement",
    countKey: "awaiting_acknowledgement",
    label: "Writer acknowledgement",
    description: "Assigned orders not acknowledged by writers.",
    tone: "neutral",
  },
  {
    key: "preferred_writer_pending",
    countKey: "preferred_writer_pending",
    label: "Preferred writer",
    description: "Invitations waiting on preferred writers.",
    tone: "neutral",
  },
  {
    key: "eligible_for_archive",
    countKey: "eligible_for_archive",
    label: "Archive-ready",
    description: "Completed orders visible for archival review.",
    tone: "good",
  },
];

const emptyCounts: OrderOpsCounts = {
  late_orders: 0,
  critical_orders: 0,
  awaiting_approval: 0,
  awaiting_acknowledgement: 0,
  pending_staffing: 0,
  preferred_writer_pending: 0,
  eligible_for_archive: 0,
};

const previewRowsByQueue: Record<OrderOpsQueueKey, OrderOpsRow[]> = {
  late: [
    {
      id: 1049,
      topic: "Nursing care plan revision",
      status: "in_progress",
      payment_status: "paid",
      total_price: "148.00",
      amount_paid: "148.00",
      client_deadline: new Date(Date.now() + 1000 * 60 * 60 * 10).toISOString(),
      writer_deadline: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
      preferred_writer_status: "none",
      client_id: 29,
      preferred_writer_id: null,
    },
  ],
  critical: [
    {
      id: 1042,
      topic: "Healthcare policy brief",
      status: "in_progress",
      payment_status: "paid",
      total_price: "186.00",
      amount_paid: "186.00",
      client_deadline: new Date(Date.now() + 1000 * 60 * 60 * 18).toISOString(),
      writer_deadline: new Date(Date.now() + 1000 * 60 * 60 * 12).toISOString(),
      preferred_writer_status: "none",
      client_id: 18,
      preferred_writer_id: null,
    },
  ],
  awaiting_approval: [
    {
      id: 1038,
      topic: "Sociology literature review",
      status: "submitted",
      payment_status: "paid",
      total_price: "210.00",
      amount_paid: "210.00",
      client_deadline: new Date(Date.now() + 1000 * 60 * 60 * 36).toISOString(),
      writer_deadline: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString(),
      preferred_writer_status: "none",
      client_id: 34,
      preferred_writer_id: null,
    },
  ],
  awaiting_acknowledgement: [
    {
      id: 1044,
      topic: "Finance case memo",
      status: "assigned",
      payment_status: "paid",
      total_price: "122.00",
      amount_paid: "122.00",
      client_deadline: new Date(Date.now() + 1000 * 60 * 60 * 28).toISOString(),
      writer_deadline: new Date(Date.now() + 1000 * 60 * 60 * 20).toISOString(),
      preferred_writer_status: "none",
      client_id: 41,
      preferred_writer_id: null,
    },
  ],
  pending_staffing: [
    {
      id: 1048,
      topic: "Machine learning report",
      status: "paid",
      payment_status: "paid",
      total_price: "242.00",
      amount_paid: "242.00",
      client_deadline: new Date(Date.now() + 1000 * 60 * 60 * 44).toISOString(),
      writer_deadline: null,
      preferred_writer_status: "none",
      client_id: 22,
      preferred_writer_id: null,
    },
  ],
  preferred_writer_pending: [
    {
      id: 1051,
      topic: "Macroeconomics problem set",
      status: "preferred_writer_pending",
      payment_status: "paid",
      total_price: "96.00",
      amount_paid: "96.00",
      client_deadline: new Date(Date.now() + 1000 * 60 * 60 * 30).toISOString(),
      writer_deadline: null,
      preferred_writer_status: "invited",
      client_id: 27,
      preferred_writer_id: 2,
    },
  ],
  eligible_for_archive: [
    {
      id: 1026,
      topic: "Marketing plan edit",
      status: "completed",
      payment_status: "paid",
      total_price: "74.00",
      amount_paid: "74.00",
      client_deadline: new Date(Date.now() - 1000 * 60 * 60 * 36).toISOString(),
      writer_deadline: new Date(Date.now() - 1000 * 60 * 60 * 42).toISOString(),
      preferred_writer_status: "none",
      client_id: 12,
      preferred_writer_id: null,
    },
  ],
};

function previewCounts(): OrderOpsCounts {
  return {
    late_orders: previewRowsByQueue.late.length,
    critical_orders: previewRowsByQueue.critical.length,
    awaiting_approval: previewRowsByQueue.awaiting_approval.length,
    awaiting_acknowledgement: previewRowsByQueue.awaiting_acknowledgement.length,
    pending_staffing: previewRowsByQueue.pending_staffing.length,
    preferred_writer_pending: previewRowsByQueue.preferred_writer_pending.length,
    eligible_for_archive: previewRowsByQueue.eligible_for_archive.length,
  };
}

export const useOrderOpsStore = defineStore("order-ops", () => {
  const counts = ref<OrderOpsCounts>({ ...emptyCounts });
  const activeQueue = ref<OrderOpsQueueKey>("pending_staffing");
  const rows = ref<OrderOpsRow[]>([]);
  const isLoading = ref(false);
  const isMutating = ref(false);
  const error = ref("");
  const notice = ref("");

  const activeDefinition = computed(
    () =>
      queueDefinitions.find((queue) => queue.key === activeQueue.value) ??
      queueDefinitions[0],
  );

  async function fetchSummary() {
    const auth = useAuthStore();
    if (auth.isPreviewSession) {
      counts.value = previewCounts();
      return counts.value;
    }

    const { data } = await orderOpsApi.summary();
    counts.value = data;
    return data;
  }

  async function fetchQueue(queueKey = activeQueue.value) {
    const auth = useAuthStore();
    activeQueue.value = queueKey;
    isLoading.value = true;
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        rows.value = previewRowsByQueue[queueKey];
        return {
          queue_key: queueKey,
          count: rows.value.length,
          results: rows.value,
        };
      }

      const { data } = await orderOpsApi.queue(queueKey);
      rows.value = data.results ?? [];
      return data;
    } catch (caught) {
      error.value = "Unable to load the operations queue.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  async function refresh() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        counts.value = previewCounts();
        rows.value = previewRowsByQueue[activeQueue.value];
        return;
      }

      await fetchSummary();
      await fetchQueue(activeQueue.value);
    } catch (caught) {
      error.value =
        "Order operations are unavailable for this account or backend session.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  async function routeToStaffing(orderId: number) {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        rows.value = rows.value.map((row) =>
          row.id === orderId ? { ...row, status: "ready_for_staffing" } : row,
        );
        notice.value = "Preview order routed to staffing.";
        return;
      }
    await orderOpsApi.routeToStaffing(orderId);
    await refresh();
      notice.value = "Order routed to staffing.";
    } finally {
      isMutating.value = false;
    }
  }

  async function manualVerifyPayment(orderId: number, payload: {
    amount: string;
    transaction_reference: string;
    verification_note: string;
    payment_method?: string;
  }) {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        rows.value = rows.value.map((row) =>
          row.id === orderId
            ? { ...row, payment_status: "fully_paid", status: "ready_for_staffing", amount_paid: row.total_price }
            : row,
        );
        notice.value = "Preview payment verified.";
        return;
      }
      await orderOpsApi.manualVerifyPayment(orderId, payload);
      notice.value = "Payment verification applied.";
      await refresh();
    } finally {
      isMutating.value = false;
    }
  }

  async function assignDirect(orderId: number, writerId: number, note = "") {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        rows.value = rows.value.map((row) =>
          row.id === orderId ? { ...row, status: "assigned", preferred_writer_id: writerId } : row,
        );
        notice.value = `Preview assigned order #${orderId} to writer #${writerId}.`;
        return;
      }
      await orderOpsApi.assignDirect(orderId, writerId, note);
      notice.value = "Order assigned.";
      await refresh();
    } finally {
      isMutating.value = false;
    }
  }

  async function releaseToPool(orderId: number, reason = "") {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        rows.value = rows.value.map((row) =>
          row.id === orderId ? { ...row, status: "staffing", preferred_writer_id: null } : row,
        );
        notice.value = "Preview order released to pool.";
        return;
      }
      await orderOpsApi.releaseToPool(orderId, reason);
      notice.value = "Order released to pool.";
      await refresh();
    } finally {
      isMutating.value = false;
    }
  }

  async function approveForDelivery(orderId: number, notes = "") {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        rows.value = rows.value.map((row) =>
          row.id === orderId ? { ...row, status: "approved_for_delivery" } : row,
        );
        notice.value = "Preview order approved for delivery.";
        return;
      }
      await orderOpsApi.approveForDelivery(orderId, notes);
      notice.value = "Order approved for delivery.";
      await refresh();
    } finally {
      isMutating.value = false;
    }
  }

  async function returnToWriter(orderId: number, notes: string) {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        rows.value = rows.value.map((row) =>
          row.id === orderId ? { ...row, status: "returned_to_writer" } : row,
        );
        notice.value = "Preview order returned to writer.";
        return;
      }
      await orderOpsApi.returnToWriter(orderId, notes);
      notice.value = "Order returned to writer.";
      await refresh();
    } finally {
      isMutating.value = false;
    }
  }

  async function requestRevision(orderId: number, instructions: string) {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        rows.value = rows.value.map((row) =>
          row.id === orderId ? { ...row, status: "revision_requested" } : row,
        );
        notice.value = "Preview revision requested.";
        return;
      }
      await orderOpsApi.requestRevision(orderId, instructions);
      notice.value = "Revision requested.";
      await refresh();
    } finally {
      isMutating.value = false;
    }
  }

  async function cancel(orderId: number, reason: string) {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        rows.value = rows.value.map((row) =>
          row.id === orderId ? { ...row, status: "cancelled" } : row,
        );
        notice.value = "Preview order cancelled.";
        return;
      }
      await orderOpsApi.cancel(orderId, reason);
      notice.value = "Order cancelled.";
      await refresh();
    } finally {
      isMutating.value = false;
    }
  }

  async function archive(orderId: number) {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        rows.value = rows.value.filter((row) => row.id !== orderId);
        notice.value = "Preview order archived.";
        return;
      }
    await orderOpsApi.archive(orderId);
    await refresh();
      notice.value = "Order archived.";
    } finally {
      isMutating.value = false;
    }
  }

  return {
    counts,
    activeQueue,
    rows,
    isLoading,
    isMutating,
    error,
    notice,
    activeDefinition,
    fetchSummary,
    fetchQueue,
    refresh,
    routeToStaffing,
    manualVerifyPayment,
    assignDirect,
    releaseToPool,
    approveForDelivery,
    returnToWriter,
    requestRevision,
    cancel,
    archive,
  };
});

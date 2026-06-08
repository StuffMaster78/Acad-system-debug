import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { ordersApi } from "@/api/orders";
import { pricingApi } from "@/api/pricing";
import { useAuthStore } from "@/stores/auth";
import type {
  CreateOrderPayload,
  DesignQuotePayload,
  DiagramQuotePayload,
  OrderLifecycle,
  OrderSummary,
  PaperQuotePayload,
  PaperQuoteUpdateResponse,
  RevisionRequestPayload,
  CancelOrderPayload,
} from "@/types/orders";

function previewOrder(id: number | string): OrderSummary {
  return {
    id: Number(id),
    topic: "Literature review on ethical AI in academic writing",
    status: "in_progress",
    payment_status: "paid",
    total_price: "148.00",
    amount_paid: "148.00",
    remaining_balance: "0.00",
    currency: "USD",
    service_code: "paper",
    service_family: "academic_writing",
    client_deadline: new Date(Date.now() + 1000 * 60 * 60 * 36).toISOString(),
    writer_deadline: new Date(Date.now() + 1000 * 60 * 60 * 24).toISOString(),
    order_instructions:
      "Use APA 7, focus on peer-reviewed sources, and include a concise methodology section.",
  };
}

function previewLifecycle(id: number | string): OrderLifecycle {
  return {
    order_id: Number(id),
    order_status: "in_progress",
    website_id: 1,
    client_id: 0,
    current_assignment_id: 42,
    current_writer_id: 108,
    current_writer_registration_id: "WR-0108",
    has_current_assignment: true,
    active_hold_id: null,
    has_active_hold: false,
    pending_reassignment_request_id: null,
    has_pending_reassignment_request: false,
    active_dispute_id: null,
    has_active_dispute: false,
    latest_adjustment_request_id: null,
    latest_adjustment_status: null,
    latest_revision_request_id: null,
    latest_revision_status: null,
    is_revision_window_open: false,
    revision_window_days: 7,
    available_actions: ["submit_for_qa", "raise_dispute", "cancel_order"],
  };
}

export const useOrderStore = defineStore("orders", () => {
  const orders = ref<OrderSummary[]>([]);
  const selectedOrder = ref<OrderSummary | null>(null);
  const selectedLifecycle = ref<OrderLifecycle | null>(null);
  const latestQuote = ref<PaperQuoteUpdateResponse | null>(null);
  const isLoading = ref(false);
  const isCreating = ref(false);
  const isMutating = ref(false);
  const error = ref("");
  const notice = ref("");
  const pagination = ref({ page: 1, pageSize: 20, count: 0 });

  const openOrders = computed(() =>
    orders.value.filter((order) => !["completed", "archived", "cancelled"].includes(order.status)),
  );

  async function fetchOrders(page = 1, params?: Record<string, unknown>) {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        orders.value = [previewOrder(1), previewOrder(2), previewOrder(3)].map((order, index) => ({
          ...order,
          id: index + 1,
          topic: [
            "Literature review on ethical AI in academic writing",
            "Business report on subscription retention",
            "Reflective essay on clinical leadership",
          ][index],
          status: ["in_progress", "awaiting_approval", "draft"][index],
        }));
        pagination.value = { page: 1, pageSize: 20, count: 3 };
        return;
      }
      const { data } = await ordersApi.list({
        page,
        page_size: pagination.value.pageSize,
        ...params,
      });
      if (Array.isArray(data)) {
        orders.value = data;
      } else {
        orders.value = Array.isArray(data.results) ? data.results : [];
        pagination.value = { ...pagination.value, page, count: data.count ?? 0 };
      }
    } catch (caught) {
      error.value = "Unable to load orders.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  async function fetchOrder(id: number | string) {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        selectedOrder.value = previewOrder(id);
        selectedLifecycle.value = previewLifecycle(id);
        return;
      }
      const [orderRes, lifecycleRes] = await Promise.allSettled([
        ordersApi.get(id),
        ordersApi.lifecycle(id),
      ]);

      if (orderRes.status === "fulfilled") {
        selectedOrder.value = orderRes.value.data;
      } else {
        const fallback = orders.value.find((order) => String(order.id) === String(id));
        selectedOrder.value = fallback ?? null;
      }

      if (lifecycleRes.status === "fulfilled") {
        selectedLifecycle.value = lifecycleRes.value.data;
      } else {
        selectedLifecycle.value = null;
      }

      if (orderRes.status === "rejected") {
        error.value = "Unable to load full order details.";
      }
    } finally {
      isLoading.value = false;
    }
  }

  function mergeSelectedStatus(status?: string) {
    if (!status || !selectedOrder.value) return;
    selectedOrder.value = { ...selectedOrder.value, status };
    orders.value = orders.value.map((order) =>
      order.id === selectedOrder.value?.id ? { ...order, status } : order,
    );
    if (selectedLifecycle.value) {
      selectedLifecycle.value = { ...selectedLifecycle.value, order_status: status };
    }
  }

  async function approveOrder(id: number | string) {
    const auth = useAuthStore();
    isMutating.value = true;
    error.value = "";
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        mergeSelectedStatus("completed");
        if (selectedOrder.value) {
          selectedOrder.value = {
            ...selectedOrder.value,
            status: "completed",
            payment_status: "paid",
          };
        }
        notice.value = "Preview order approved.";
        return {
          message: notice.value,
          order_id: Number(id),
          status: "completed",
        };
      }
      const { data } = await ordersApi.approve(id, {});
      mergeSelectedStatus(data.status);
      notice.value = data.message ?? "Order approved.";
      return data;
    } catch (caught) {
      error.value = "Unable to approve this order.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function requestRevision(id: number | string, payload: RevisionRequestPayload) {
    const auth = useAuthStore();
    isMutating.value = true;
    error.value = "";
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        if (selectedLifecycle.value) {
          selectedLifecycle.value = {
            ...selectedLifecycle.value,
            latest_revision_request_id: Date.now(),
            latest_revision_status: payload.is_within_original_scope
              ? "free_revision_requested"
              : "paid_adjustment_review",
            is_revision_window_open: true,
          };
        }
        mergeSelectedStatus("revision_requested");
        notice.value = payload.is_within_original_scope
          ? "Preview free revision request submitted."
          : "Preview paid adjustment review submitted.";
        return {
          message: notice.value,
          order_id: Number(id),
          status: selectedOrder.value?.status,
        };
      }
      const { data } = await ordersApi.requestRevision(id, payload);
      notice.value = ("message" in data ? data.message : null) ?? "Revision request submitted.";
      await fetchOrder(id);
      return data;
    } catch (caught) {
      error.value = "Unable to request a revision.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function cancelOrder(id: number | string, payload: CancelOrderPayload) {
    const auth = useAuthStore();
    isMutating.value = true;
    error.value = "";
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        mergeSelectedStatus("cancelled");
        notice.value = `Preview order cancelled with ${payload.refund_destination} refund.`;
        return {
          detail: notice.value,
          order_id: Number(id),
          status: "cancelled",
          refund_destination: payload.refund_destination,
        };
      }
      const { data } = await ordersApi.cancel(id, payload);
      mergeSelectedStatus(data.status);
      notice.value = data.detail ?? data.message ?? "Order cancelled.";
      return data;
    } catch (caught) {
      error.value = "Unable to cancel this order.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function raiseDispute(id: number | string, reason: string) {
    const auth = useAuthStore();
    isMutating.value = true;
    error.value = "";
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        if (selectedLifecycle.value) {
          selectedLifecycle.value = {
            ...selectedLifecycle.value,
            has_active_dispute: true,
            active_dispute_id: Date.now(),
          };
        }
        notice.value = "Preview dispute raised.";
        return;
      }
      const { data } = await ordersApi.raiseDispute(id, reason);
      await fetchOrder(id);
      notice.value = (data as { message?: string }).message ?? "Dispute raised.";
      return data;
    } catch (caught) {
      error.value = "Unable to raise dispute.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function pricePaperOrder(payload: PaperQuotePayload) {
    isLoading.value = true;
    error.value = "";
    try {
      const start = await pricingApi.startPaperQuote(payload);
      const update = await pricingApi.updatePaperQuote(start.data.session_id, payload);
      latestQuote.value = update.data;
      return update.data;
    } catch (caught) {
      error.value = "Unable to calculate pricing.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  async function createPaperOrder(payload: PaperQuotePayload, order: Omit<CreateOrderPayload, "pricing_snapshot_id">) {
    isCreating.value = true;
    error.value = "";
    try {
      const quote = latestQuote.value ?? (await pricePaperOrder(payload));
      const snapshot = await pricingApi.createSnapshot(quote.session_id);
      const created = await ordersApi.create({
        ...order,
        pricing_snapshot_id: snapshot.data.snapshot_id,
      });
    orders.value = [created.data.order, ...orders.value];
      return created.data;
    } catch (caught) {
      error.value = "Unable to create order.";
      throw caught;
    } finally {
      isCreating.value = false;
    }
  }

  async function priceDesignOrder(payload: DesignQuotePayload) {
    isLoading.value = true;
    error.value = "";
    try {
      const start = await pricingApi.startDesignQuote(payload);
      const update = await pricingApi.updateDesignQuote(start.data.session_id, payload);
      latestQuote.value = update.data;
      return update.data;
    } catch (caught) {
      error.value = "Unable to calculate pricing.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  async function priceDiagramOrder(payload: DiagramQuotePayload) {
    isLoading.value = true;
    error.value = "";
    try {
      const start = await pricingApi.startDiagramQuote(payload);
      const update = await pricingApi.updateDiagramQuote(start.data.session_id, payload);
      latestQuote.value = update.data;
      return update.data;
    } catch (caught) {
      error.value = "Unable to calculate pricing.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  async function priceComboOrder(paperPayload: PaperQuotePayload, secondPayload: DesignQuotePayload | DiagramQuotePayload, secondType: "design" | "diagram") {
    isLoading.value = true;
    error.value = "";
    try {
      // Start both quotes
      const [paperStart, secondStart] = await Promise.all([
        pricingApi.startPaperQuote(paperPayload),
        secondType === "design"
          ? pricingApi.startDesignQuote(secondPayload as DesignQuotePayload)
          : pricingApi.startDiagramQuote(secondPayload as DiagramQuotePayload),
      ]);
      // Update both to set calculated_price (required by composite validator)
      await Promise.all([
        pricingApi.updatePaperQuote(paperStart.data.session_id, paperPayload),
        secondType === "design"
          ? pricingApi.updateDesignQuote(secondStart.data.session_id, secondPayload as DesignQuotePayload)
          : pricingApi.updateDiagramQuote(secondStart.data.session_id, secondPayload as DiagramQuotePayload),
      ]);
      const composite = await pricingApi.createCompositeQuote([
        paperStart.data.session_id,
        secondStart.data.session_id,
      ]);
      latestQuote.value = {
        session_id: composite.data.session_id,
        calculated_price: composite.data.total,
        currency: composite.data.currency,
        total: composite.data.total,
      } as PaperQuoteUpdateResponse;
      return composite.data;
    } catch (caught) {
      error.value = "Unable to calculate pricing.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  async function createDesignOrder(payload: DesignQuotePayload, order: Omit<CreateOrderPayload, "pricing_snapshot_id">) {
    isCreating.value = true;
    error.value = "";
    try {
      const quote = await priceDesignOrder(payload);
      const snapshot = await pricingApi.createSnapshot(quote.session_id);
      const created = await ordersApi.create({ ...order, pricing_snapshot_id: snapshot.data.snapshot_id });
      orders.value = [created.data.order, ...orders.value];
      return created.data;
    } catch (caught) {
      error.value = "Unable to create order.";
      throw caught;
    } finally {
      isCreating.value = false;
    }
  }

  async function createDiagramOrder(payload: DiagramQuotePayload, order: Omit<CreateOrderPayload, "pricing_snapshot_id">) {
    isCreating.value = true;
    error.value = "";
    try {
      const quote = await priceDiagramOrder(payload);
      const snapshot = await pricingApi.createSnapshot(quote.session_id);
      const created = await ordersApi.create({ ...order, pricing_snapshot_id: snapshot.data.snapshot_id });
      orders.value = [created.data.order, ...orders.value];
      return created.data;
    } catch (caught) {
      error.value = "Unable to create order.";
      throw caught;
    } finally {
      isCreating.value = false;
    }
  }

  async function createComboOrder(
    paperPayload: PaperQuotePayload,
    secondPayload: DesignQuotePayload | DiagramQuotePayload,
    secondType: "design" | "diagram",
    order: Omit<CreateOrderPayload, "pricing_snapshot_id">,
    comboTotal: number,
  ) {
    isCreating.value = true;
    error.value = "";
    try {
      // For combo, price the paper component and use its snapshot; pass total override
      const paperQuote = await pricePaperOrder(paperPayload);
      const snapshot = await pricingApi.createSnapshot(paperQuote.session_id);
      const created = await ordersApi.create({
        ...order,
        pricing_snapshot_id: snapshot.data.snapshot_id,
        total_price_override: comboTotal,
      } as CreateOrderPayload & { total_price_override: number });
      orders.value = [created.data.order, ...orders.value];
      return created.data;
    } catch (caught) {
      error.value = "Unable to create order.";
      throw caught;
    } finally {
      isCreating.value = false;
    }
  }

  return {
    orders,
    selectedOrder,
    selectedLifecycle,
    latestQuote,
    isLoading,
    isCreating,
    isMutating,
    error,
    notice,
    pagination,
    openOrders,
    fetchOrders,
    fetchOrder,
    approveOrder,
    requestRevision,
    cancelOrder,
    raiseDispute,
    pricePaperOrder,
    priceDesignOrder,
    priceDiagramOrder,
    priceComboOrder,
    createPaperOrder,
    createDesignOrder,
    createDiagramOrder,
    createComboOrder,
  };
});

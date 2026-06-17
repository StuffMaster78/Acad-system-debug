import { computed, ref } from "vue";
import { defineStore } from "pinia";
import { cancellationRequestsApi } from "@/api/cancellationRequests";
import { useAuthStore } from "@/stores/auth";
import type { CancellationQueueItem } from "@/types/cancellation";

const PREVIEW: CancellationQueueItem[] = [
  {
    id: 1,
    order_id: 4201,
    order_topic: "Qualitative research paper on urban housing policy",
    order_status: "pending_cancellation",
    client_id: 55,
    client_deadline: new Date(Date.now() + 1000 * 60 * 60 * 12).toISOString().slice(0, 10),
    reason: "The writer has not started yet and I need to cancel due to a schedule change.",
    pre_request_status: "in_progress",
    forfeiture_pct: "20.00",
    forfeiture_amount: "8.40",
    refund_amount: "33.60",
    requested_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
  },
  {
    id: 2,
    order_id: 4118,
    order_topic: "Business case analysis — SaaS market entry",
    order_status: "pending_cancellation",
    client_id: 67,
    client_deadline: new Date(Date.now() + 1000 * 60 * 60 * 4).toISOString().slice(0, 10),
    reason: "I found another service that fits my budget better.",
    pre_request_status: "in_progress",
    forfeiture_pct: "50.00",
    forfeiture_amount: "31.25",
    refund_amount: "31.25",
    requested_at: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
  },
];

export const useCancellationQueueStore = defineStore("cancellationQueue", () => {
  const queue = ref<CancellationQueueItem[]>([]);
  const isLoading = ref(false);
  const isSaving = ref(false);
  const error = ref("");
  const notice = ref("");
  const query = ref("");

  const approveForm = ref<{
    reqId: number | null;
    orderId: number | null;
    refund_destination: "wallet" | "external_gateway";
    forfeiture_pct_override: string;
    notes: string;
  }>({ reqId: null, orderId: null, refund_destination: "wallet", forfeiture_pct_override: "", notes: "" });

  const rejectForm = ref<{ reqId: number | null; orderId: number | null; notes: string }>({
    reqId: null,
    orderId: null,
    notes: "",
  });

  const filtered = computed(() => {
    const needle = query.value.trim().toLowerCase();
    if (!needle) return queue.value;
    return queue.value.filter((r) =>
      [r.order_topic, String(r.order_id), r.reason].some((v) => v.toLowerCase().includes(needle)),
    );
  });

  async function load() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        queue.value = PREVIEW;
        return;
      }
      const { data } = await cancellationRequestsApi.listPending();
      queue.value = Array.isArray(data) ? data : (data as any).results ?? [];
    } catch {
      error.value = "Unable to load cancellation requests.";
    } finally {
      isLoading.value = false;
    }
  }

  function openApprove(item: CancellationQueueItem) {
    approveForm.value = {
      reqId: item.id,
      orderId: item.order_id,
      refund_destination: "wallet",
      forfeiture_pct_override: "",
      notes: "",
    };
    error.value = "";
  }

  function openReject(item: CancellationQueueItem) {
    rejectForm.value = { reqId: item.id, orderId: item.order_id, notes: "" };
    error.value = "";
  }

  function closeApprove() {
    approveForm.value = { reqId: null, orderId: null, refund_destination: "wallet", forfeiture_pct_override: "", notes: "" };
  }

  function closeReject() {
    rejectForm.value = { reqId: null, orderId: null, notes: "" };
  }

  async function approve() {
    const auth = useAuthStore();
    const { reqId, orderId, refund_destination, forfeiture_pct_override, notes } = approveForm.value;
    if (!reqId || !orderId) return;

    isSaving.value = true;
    error.value = "";
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        queue.value = queue.value.filter((r) => r.id !== reqId);
        closeApprove();
        notice.value = "Preview: cancellation approved.";
        return;
      }
      await cancellationRequestsApi.approve(orderId, reqId, {
        refund_destination,
        ...(forfeiture_pct_override ? { forfeiture_pct_override } : {}),
        ...(notes ? { notes } : {}),
      });
      queue.value = queue.value.filter((r) => r.id !== reqId);
      closeApprove();
      notice.value = "Cancellation approved and order cancelled.";
    } catch {
      error.value = "Unable to approve cancellation request.";
    } finally {
      isSaving.value = false;
    }
  }

  async function reject() {
    const auth = useAuthStore();
    const { reqId, orderId, notes } = rejectForm.value;
    if (!reqId || !orderId) return;

    isSaving.value = true;
    error.value = "";
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        queue.value = queue.value.filter((r) => r.id !== reqId);
        closeReject();
        notice.value = "Preview: cancellation rejected.";
        return;
      }
      await cancellationRequestsApi.reject(orderId, reqId, notes);
      queue.value = queue.value.filter((r) => r.id !== reqId);
      closeReject();
      notice.value = "Cancellation request rejected. Order status reverted.";
    } catch {
      error.value = "Unable to reject cancellation request.";
    } finally {
      isSaving.value = false;
    }
  }

  return {
    queue,
    filtered,
    isLoading,
    isSaving,
    error,
    notice,
    query,
    approveForm,
    rejectForm,
    load,
    openApprove,
    openReject,
    closeApprove,
    closeReject,
    approve,
    reject,
  };
});

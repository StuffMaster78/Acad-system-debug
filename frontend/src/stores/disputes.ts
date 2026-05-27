import { computed, reactive, ref } from "vue";
import { defineStore } from "pinia";
import { disputesApi } from "@/api/disputes";
import { useAuthStore } from "@/stores/auth";
import type { Dispute, DisputeRemedy, DisputeStatus, DisputeVerdict, ResolveDisputePayload } from "@/types/disputes";

function normalizeList<T>(data: T[] | { results: T[]; count?: number }): T[] {
  return Array.isArray(data) ? data : data.results;
}

const PREVIEW_DISPUTES: Dispute[] = [
  {
    id: 101,
    order_id: 5021,
    order_topic: "Healthcare policy brief — Q2 edition",
    raised_by: 42,
    raised_by_username: "client.preview",
    status: "open",
    reason: "The delivered document does not address section 3 of the brief. The writer ignored the methodology requirements.",
    resolution: null,
    admin_notes: null,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 14).toISOString(),
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 14).toISOString(),
    resolved_at: null,
  },
  {
    id: 102,
    order_id: 4908,
    order_topic: "Business analytics report — subscription retention",
    raised_by: 42,
    raised_by_username: "client.preview",
    status: "under_review",
    reason: "Delivered file has significant formatting issues and references that were not requested.",
    assigned_admin: 11,
    assigned_admin_username: "admin.preview",
    admin_notes: "Reviewing the delivered file against the original brief.",
    resolution: null,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    resolved_at: null,
  },
  {
    id: 88,
    order_id: 4610,
    order_topic: "Reflective essay on clinical leadership",
    raised_by: 42,
    raised_by_username: "client.preview",
    status: "resolved",
    reason: "Content was below expected academic standard.",
    resolution: "Order was sent for a free revision. Writer completed the revision and client confirmed satisfaction.",
    admin_notes: "Revision completed within 6 hours. Marked resolved.",
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 72 * 5).toISOString(),
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 72 * 4).toISOString(),
    resolved_at: new Date(Date.now() - 1000 * 60 * 60 * 72 * 4).toISOString(),
  },
];

const PREVIEW_ADMIN_DISPUTES: Dispute[] = [
  ...PREVIEW_DISPUTES,
  {
    id: 95,
    order_id: 4780,
    order_topic: "Literature review on ethical AI",
    raised_by: 67,
    raised_by_username: "client.delta",
    status: "open",
    reason: "Sources are not peer-reviewed as required. The paper uses blog posts instead of academic journals.",
    resolution: null,
    admin_notes: null,
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString(),
    updated_at: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString(),
    resolved_at: null,
  },
];

export const useDisputesStore = defineStore("disputes", () => {
  const myList = ref<Dispute[]>([]);
  const adminList = ref<Dispute[]>([]);
  const isLoading = ref(false);
  const isSaving = ref(false);
  const error = ref("");
  const notice = ref("");
  const statusFilter = ref<"all" | DisputeStatus>("all");
  const query = ref("");

  const raiseForm = reactive({ orderId: "" as number | string, reason: "" });
  const resolveForm = reactive({
    disputeId: null as number | null,
    verdict: null as DisputeVerdict | null,
    remedy: null as DisputeRemedy | null,
    refundAmount: "",
    resolution: "",
  });
  const showRaiseModal = ref(false);

  const filteredAdmin = computed(() => {
    const needle = query.value.trim().toLowerCase();
    return adminList.value.filter((d) => {
      if (statusFilter.value !== "all" && d.status !== statusFilter.value) return false;
      if (!needle) return true;
      return [d.order_topic, d.raised_by_username, String(d.order_id)]
        .some((v) => v.toLowerCase().includes(needle));
    });
  });

  const openCount = computed(() => adminList.value.filter((d) => d.status === "open").length);
  const underReviewCount = computed(() => adminList.value.filter((d) => d.status === "under_review").length);

  async function loadMine() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        myList.value = PREVIEW_DISPUTES;
        return;
      }
      const { data } = await disputesApi.mine();
      myList.value = normalizeList(data);
    } catch {
      error.value = "Unable to load your disputes.";
    } finally {
      isLoading.value = false;
    }
  }

  async function loadAll() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        adminList.value = PREVIEW_ADMIN_DISPUTES;
        return;
      }
      const { data } = await disputesApi.list();
      adminList.value = normalizeList(data);
    } catch {
      error.value = "Unable to load disputes.";
    } finally {
      isLoading.value = false;
    }
  }

  async function raiseDispute() {
    const auth = useAuthStore();
    if (!raiseForm.orderId || !raiseForm.reason.trim()) {
      error.value = "Order ID and reason are required.";
      return;
    }
    isSaving.value = true;
    error.value = "";
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        const newDispute: Dispute = {
          id: Date.now(),
          order_id: Number(raiseForm.orderId),
          order_topic: `Order #${raiseForm.orderId}`,
          raised_by: 42,
          raised_by_username: "client.preview",
          status: "open",
          reason: raiseForm.reason,
          resolution: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          resolved_at: null,
        };
        myList.value = [newDispute, ...myList.value];
        raiseForm.orderId = "";
        raiseForm.reason = "";
        showRaiseModal.value = false;
        notice.value = "Preview dispute raised.";
        return newDispute;
      }
      const { data } = await disputesApi.raise(raiseForm.orderId, raiseForm.reason);
      myList.value = [data, ...myList.value];
      raiseForm.orderId = "";
      raiseForm.reason = "";
      showRaiseModal.value = false;
      notice.value = "Dispute raised. Our team will review it shortly.";
      return data;
    } catch {
      error.value = "Unable to raise dispute. Check the order ID and try again.";
    } finally {
      isSaving.value = false;
    }
  }

  async function resolveDispute(disputeId: number) {
    const auth = useAuthStore();
    if (!resolveForm.verdict) {
      error.value = "Select a verdict before resolving.";
      return;
    }
    if (!resolveForm.resolution.trim()) {
      error.value = "Resolution note is required.";
      return;
    }
    if (resolveForm.verdict === "client_wins" && !resolveForm.remedy) {
      error.value = "Select a remedy when the client wins.";
      return;
    }

    const payload: ResolveDisputePayload = {
      verdict: resolveForm.verdict,
      resolution: resolveForm.resolution,
      ...(resolveForm.remedy && { remedy: resolveForm.remedy }),
      ...(resolveForm.remedy === "partial_refund" && resolveForm.refundAmount && {
        refund_amount: resolveForm.refundAmount,
      }),
    };

    isSaving.value = true;
    error.value = "";
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        const patch = (d: Dispute) =>
          d.id === disputeId
            ? {
                ...d,
                status: "resolved" as DisputeStatus,
                verdict: resolveForm.verdict,
                remedy: resolveForm.remedy,
                refund_amount: resolveForm.remedy === "partial_refund" ? resolveForm.refundAmount : null,
                resolution: resolveForm.resolution,
                resolved_at: new Date().toISOString(),
              }
            : d;
        adminList.value = adminList.value.map(patch);
        myList.value = myList.value.map(patch);
        resolveForm.disputeId = null;
        resolveForm.verdict = null;
        resolveForm.remedy = null;
        resolveForm.refundAmount = "";
        resolveForm.resolution = "";
        notice.value = "Preview dispute resolved.";
        return;
      }
      await disputesApi.resolve(disputeId, payload);
      await loadAll();
      resolveForm.disputeId = null;
      resolveForm.verdict = null;
      resolveForm.remedy = null;
      resolveForm.refundAmount = "";
      resolveForm.resolution = "";
      notice.value = "Dispute resolved.";
    } catch {
      error.value = "Unable to resolve dispute.";
    } finally {
      isSaving.value = false;
    }
  }

  async function closeDispute(disputeId: number, notes?: string) {
    const auth = useAuthStore();
    isSaving.value = true;
    error.value = "";
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        const patch = (d: Dispute) =>
          d.id === disputeId ? { ...d, status: "closed" as DisputeStatus, admin_notes: notes ?? d.admin_notes } : d;
        adminList.value = adminList.value.map(patch);
        notice.value = "Preview dispute closed.";
        return;
      }
      await disputesApi.close(disputeId, notes);
      await loadAll();
      notice.value = "Dispute closed.";
    } catch {
      error.value = "Unable to close dispute.";
    } finally {
      isSaving.value = false;
    }
  }

  async function withdrawDispute(disputeId: number) {
    const auth = useAuthStore();
    isSaving.value = true;
    error.value = "";
    notice.value = "";
    try {
      if (auth.isPreviewSession) {
        myList.value = myList.value.map((d) =>
          d.id === disputeId ? { ...d, status: "withdrawn" as DisputeStatus } : d,
        );
        notice.value = "Preview dispute withdrawn.";
        return;
      }
      await disputesApi.withdraw(disputeId);
      myList.value = myList.value.map((d) =>
        d.id === disputeId ? { ...d, status: "withdrawn" } : d,
      );
      notice.value = "Dispute withdrawn.";
    } catch {
      error.value = "Unable to withdraw dispute.";
    } finally {
      isSaving.value = false;
    }
  }

  function openRaiseModal(orderId?: number | string) {
    raiseForm.orderId = orderId ?? "";
    raiseForm.reason = "";
    error.value = "";
    showRaiseModal.value = true;
  }

  function openResolveForm(disputeId: number) {
    resolveForm.disputeId = disputeId;
    resolveForm.verdict = null;
    resolveForm.remedy = null;
    resolveForm.refundAmount = "";
    resolveForm.resolution = "";
    error.value = "";
  }

  return {
    myList,
    adminList,
    isLoading,
    isSaving,
    error,
    notice,
    statusFilter,
    query,
    raiseForm,
    resolveForm,
    showRaiseModal,
    filteredAdmin,
    openCount,
    underReviewCount,
    loadMine,
    loadAll,
    raiseDispute,
    resolveDispute,
    closeDispute,
    withdrawDispute,
    openRaiseModal,
    openResolveForm,
  };
});

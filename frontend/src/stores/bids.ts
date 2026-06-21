import { ref, computed } from "vue";
import { defineStore } from "pinia";
import { bidsApi } from "@/api/bids";
import { useAuthStore } from "@/stores/auth";
import type { Bid, SubmitBidPayload } from "@/types/bids";

function normalizeList<T>(data: T[] | { results: T[] }): T[] {
  return Array.isArray(data) ? data : data.results;
}

const PREVIEW_BIDS: Bid[] = [
  {
    id: 1,
    order_id: 101,
    order_topic: "Analysis of Financial Markets",
    writer_id: 5,
    writer_username: "writer.pro",
    writer_rating: 4.8,
    price: "45.00",
    currency: "USD",
    delivery_hours: 24,
    pitch: "I have 5 years of experience in financial analysis and have completed over 200 similar papers.",
    status: "pending",
    created_at: "2026-05-26T10:00:00Z",
    responded_at: null,
    rejection_reason: null,
  },
  {
    id: 2,
    order_id: 102,
    order_topic: "Climate Change Policy Essay",
    writer_id: 5,
    writer_username: "writer.pro",
    writer_rating: 4.8,
    price: "35.00",
    currency: "USD",
    delivery_hours: 12,
    pitch: "Environmental policy is my specialty. I can deliver a well-researched essay on time.",
    status: "accepted",
    created_at: "2026-05-25T14:00:00Z",
    responded_at: "2026-05-25T16:00:00Z",
    rejection_reason: null,
  },
];

// Preview bids for admin order view
const PREVIEW_ORDER_BIDS: Record<string, Bid[]> = {
  "101": [
    {
      id: 1,
      order_id: 101,
      order_topic: "Analysis of Financial Markets",
      writer_id: 5,
      writer_username: "writer.pro",
      writer_rating: 4.8,
      price: "45.00",
      currency: "USD",
      delivery_hours: 24,
      pitch: "I have 5 years of experience in financial analysis and have completed over 200 similar papers. Guaranteed on-time delivery.",
      status: "pending",
      created_at: "2026-05-26T10:00:00Z",
      responded_at: null,
      rejection_reason: null,
    },
    {
      id: 2,
      order_id: 101,
      order_topic: "Analysis of Financial Markets",
      writer_id: 8,
      writer_username: "finance.expert",
      writer_rating: 4.6,
      price: "52.00",
      currency: "USD",
      delivery_hours: 18,
      pitch: "CFA charterholder with deep expertise in capital markets. This is my bread and butter.",
      status: "pending",
      created_at: "2026-05-26T11:30:00Z",
      responded_at: null,
      rejection_reason: null,
    },
    {
      id: 3,
      order_id: 101,
      order_topic: "Analysis of Financial Markets",
      writer_id: 12,
      writer_username: "quick.writer",
      writer_rating: 4.2,
      price: "38.00",
      currency: "USD",
      delivery_hours: 36,
      pitch: "Can handle this efficiently. Strong economics background.",
      status: "pending",
      created_at: "2026-05-26T13:00:00Z",
      responded_at: null,
      rejection_reason: null,
    },
  ],
};

export const useBidsStore = defineStore("bids", () => {
  const myBids = ref<Bid[]>([]);
  const orderBids = ref<Bid[]>([]);
  const allBids = ref<Bid[]>([]);
  const isLoading = ref(false);
  const isLoadingOrderBids = ref(false);
  const isSaving = ref(false);
  const error = ref<string | null>(null);
  const notice = ref<string | null>(null);

  // Per-order bid form state
  const bidFormOrderId = ref<number | null>(null);
  const bidForm = ref<SubmitBidPayload>({ price: "", delivery_hours: 24, pitch: "" });

  const pendingBids = computed(() => myBids.value.filter((b) => b.status === "pending"));
  const acceptedBids = computed(() => myBids.value.filter((b) => b.status === "accepted"));
  const pendingOrderBids = computed(() => orderBids.value.filter((b) => b.status === "pending"));

  function openBidForm(orderId: number) {
    bidFormOrderId.value = orderId;
    bidForm.value = { price: "", delivery_hours: 24, pitch: "" };
    error.value = null;
  }

  function closeBidForm() {
    bidFormOrderId.value = null;
  }

  async function submitBid() {
    const auth = useAuthStore();
    if (!bidFormOrderId.value || isSaving.value) return;
    isSaving.value = true;
    error.value = null;
    try {
      if (auth.isPreviewSession) {
        notice.value = "Bid submitted (preview).";
        closeBidForm();
        return;
      }
      await bidsApi.submit(bidFormOrderId.value, bidForm.value);
      notice.value = "Bid submitted successfully.";
      closeBidForm();
      await loadMyBids();
    } catch {
      error.value = "Failed to submit bid.";
    } finally {
      isSaving.value = false;
    }
  }

  async function loadMyBids() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = null;
    try {
      if (auth.isPreviewSession) {
        myBids.value = PREVIEW_BIDS;
        return;
      }
      const res = await bidsApi.listMine();
      myBids.value = normalizeList(res.data);
    } catch {
      error.value = "Failed to load bids.";
    } finally {
      isLoading.value = false;
    }
  }

  async function loadOrderBids(orderId: number | string) {
    const auth = useAuthStore();
    isLoadingOrderBids.value = true;
    orderBids.value = [];
    error.value = null;
    try {
      if (auth.isPreviewSession) {
        orderBids.value = PREVIEW_ORDER_BIDS[String(orderId)] ?? [];
        return;
      }
      const res = await bidsApi.listForOrder(orderId);
      orderBids.value = res.data.bids ?? [];
    } catch {
      error.value = "Failed to load bids for this order.";
    } finally {
      isLoadingOrderBids.value = false;
    }
  }

  async function loadAllBids(params?: Record<string, unknown>) {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = null;
    try {
      if (auth.isPreviewSession) {
        allBids.value = [...PREVIEW_BIDS, ...Object.values(PREVIEW_ORDER_BIDS).flat()];
        return;
      }
      const res = await bidsApi.listAll(params);
      allBids.value = normalizeList(res.data as Bid[] | { results: Bid[] });
    } catch {
      error.value = "Failed to load bids.";
    } finally {
      isLoading.value = false;
    }
  }

  async function acceptBid(orderId: number | string, bidId: number | string) {
    const auth = useAuthStore();
    if (isSaving.value) return;
    isSaving.value = true;
    notice.value = null;
    try {
      if (auth.isPreviewSession) {
        const bid = orderBids.value.find((b) => b.id === Number(bidId));
        if (bid) {
          bid.status = "accepted";
          bid.responded_at = new Date().toISOString();
        }
        orderBids.value
          .filter((b) => b.id !== Number(bidId) && b.status === "pending")
          .forEach((b) => { b.status = "rejected"; });
        notice.value = "Bid accepted. Writer assigned.";
        return;
      }
      await bidsApi.accept(orderId, bidId);
      notice.value = "Bid accepted. Writer assigned.";
      await loadOrderBids(orderId);
    } catch {
      error.value = "Failed to accept bid.";
    } finally {
      isSaving.value = false;
    }
  }

  async function rejectBid(orderId: number | string, bidId: number | string, reason?: string) {
    const auth = useAuthStore();
    if (isSaving.value) return;
    isSaving.value = true;
    try {
      if (auth.isPreviewSession) {
        const bid = orderBids.value.find((b) => b.id === Number(bidId));
        if (bid) { bid.status = "rejected"; bid.rejection_reason = reason ?? null; }
        return;
      }
      await bidsApi.reject(orderId, bidId, reason);
      await loadOrderBids(orderId);
    } catch {
      error.value = "Failed to reject bid.";
    } finally {
      isSaving.value = false;
    }
  }

  async function withdrawBid(bidId: number | string) {
    const auth = useAuthStore();
    if (isSaving.value) return;
    isSaving.value = true;
    try {
      if (auth.isPreviewSession) {
        const bid = myBids.value.find((b) => b.id === Number(bidId));
        if (bid) bid.status = "withdrawn";
        return;
      }
      await bidsApi.withdraw(bidId);
      await loadMyBids();
    } catch {
      error.value = "Failed to withdraw bid.";
    } finally {
      isSaving.value = false;
    }
  }

  function clearNotice() { notice.value = null; }

  return {
    myBids,
    orderBids,
    allBids,
    isLoading,
    isLoadingOrderBids,
    isSaving,
    error,
    notice,
    bidFormOrderId,
    bidForm,
    pendingBids,
    acceptedBids,
    pendingOrderBids,
    openBidForm,
    closeBidForm,
    submitBid,
    loadMyBids,
    loadOrderBids,
    loadAllBids,
    acceptBid,
    rejectBid,
    withdrawBid,
    clearNotice,
  };
});

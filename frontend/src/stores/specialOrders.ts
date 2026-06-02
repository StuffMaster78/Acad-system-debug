import { ref, computed } from "vue";
import { defineStore } from "pinia";
import { specialOrdersApi } from "@/api/specialOrders";
import { useAuthStore } from "@/stores/auth";
import type {
  SpecialOrder,
  SpecialOrderDetail,
  SpecialOrderMilestone,
  Quote,
  SubmitQuotePayload,
  DeliverMilestonePayload,
} from "@/types/specialOrders";

function normalizeList<T>(data: T[] | { results: T[] }): T[] {
  return Array.isArray(data) ? data : data.results;
}

const PREVIEW_ORDERS: SpecialOrder[] = [
  {
    id: 1,
    reference: "SPO-001",
    title: "Dissertation Chapter Editing + Formatting",
    description: "Full dissertation — 6 chapters, APA 7th, formatting + editing + plagiarism check.",
    status: "in_progress",
    client_id: 10,
    client_username: "john.doe",
    assigned_writer_id: 5,
    writer_username: "writer.pro",
    total_milestones: 4,
    completed_milestones: 2,
    quoted_price: "850.00",
    final_price: null,
    currency: "USD",
    payment_status: "partial",
    deadline: "2026-06-30",
    created_at: "2026-04-01T10:00:00Z",
    updated_at: "2026-04-20T14:00:00Z",
    attachments_count: 3,
  },
  {
    id: 2,
    reference: "SPO-002",
    title: "Grant Proposal Writing",
    description: "Full grant proposal for STEM research funding — 15 pages.",
    status: "quote_sent",
    client_id: 11,
    client_username: "jane.smith",
    assigned_writer_id: null,
    writer_username: null,
    total_milestones: 0,
    completed_milestones: 0,
    quoted_price: null,
    final_price: null,
    currency: "USD",
    payment_status: "pending",
    deadline: "2026-07-15",
    created_at: "2026-05-01T09:00:00Z",
    updated_at: "2026-05-10T11:00:00Z",
    attachments_count: 1,
  },
];

const PREVIEW_DETAIL: SpecialOrderDetail = {
  ...PREVIEW_ORDERS[0],
  milestones: [
    {
      id: 1,
      special_order_id: 1,
      sequence: 1,
      label: "Chapters 1–2 Edit",
      description: "Editing and formatting of chapters 1 and 2.",
      price: "200.00",
      currency: "USD",
      due_date: "2026-05-01",
      status: "approved",
      writer_id: 5,
      writer_username: "writer.pro",
      delivery_file_url: "https://example.com/files/ch1-2.docx",
      delivery_notes: "Chapters 1 and 2 edited and formatted.",
      revision_notes: null,
      delivered_at: "2026-04-28T16:00:00Z",
      approved_at: "2026-04-30T09:00:00Z",
    },
    {
      id: 2,
      special_order_id: 1,
      sequence: 2,
      label: "Chapters 3–4 Edit",
      description: "Editing and formatting of chapters 3 and 4.",
      price: "200.00",
      currency: "USD",
      due_date: "2026-05-20",
      status: "approved",
      writer_id: 5,
      writer_username: "writer.pro",
      delivery_file_url: "https://example.com/files/ch3-4.docx",
      delivery_notes: "All feedback addressed.",
      revision_notes: null,
      delivered_at: "2026-05-18T14:00:00Z",
      approved_at: "2026-05-20T10:00:00Z",
    },
    {
      id: 3,
      special_order_id: 1,
      sequence: 3,
      label: "Chapters 5–6 Edit",
      description: "Editing and formatting of chapters 5 and 6.",
      price: "250.00",
      currency: "USD",
      due_date: "2026-06-10",
      status: "in_progress",
      writer_id: 5,
      writer_username: "writer.pro",
      delivery_file_url: null,
      delivery_notes: null,
      revision_notes: null,
      delivered_at: null,
      approved_at: null,
    },
    {
      id: 4,
      special_order_id: 1,
      sequence: 4,
      label: "Final Plagiarism Check & Compilation",
      description: "Turnitin check and full document compilation.",
      price: "200.00",
      currency: "USD",
      due_date: "2026-06-25",
      status: "pending",
      writer_id: null,
      writer_username: null,
      delivery_file_url: null,
      delivery_notes: null,
      revision_notes: null,
      delivered_at: null,
      approved_at: null,
    },
  ],
  quotes: [
    {
      id: 1,
      special_order_id: 1,
      status: "accepted",
      price: "850.00",
      currency: "USD",
      valid_until: "2026-04-10",
      notes: "Price covers full dissertation editing, formatting, and plagiarism check.",
      milestones_preview: [
        { label: "Chapters 1–2 Edit", due_date: "2026-05-01", price: "200.00" },
        { label: "Chapters 3–4 Edit", due_date: "2026-05-20", price: "200.00" },
        { label: "Chapters 5–6 Edit", due_date: "2026-06-10", price: "250.00" },
        { label: "Final Compilation", due_date: "2026-06-25", price: "200.00" },
      ],
      created_by: "admin.user",
      created_at: "2026-04-03T12:00:00Z",
      responded_at: "2026-04-05T09:00:00Z",
      rejection_reason: null,
    },
  ],
  sensitive_access: {
    portal_url: null,
    credentials_hint: null,
    notes: "Client sends files via email. No LMS access required.",
  },
  latest_quote: null,
};
PREVIEW_DETAIL.latest_quote = PREVIEW_DETAIL.quotes[0];

export const useSpecialOrdersStore = defineStore("specialOrders", () => {
  const orders = ref<SpecialOrder[]>([]);
  const detail = ref<SpecialOrderDetail | null>(null);
  const isLoading = ref(false);
  const isLoadingDetail = ref(false);
  const isSaving = ref(false);
  const error = ref<string | null>(null);
  const activeTab = ref<"milestones" | "quotes" | "access">("milestones");

  // Quote submission form
  const showQuoteForm = ref(false);
  const quoteForm = ref<SubmitQuotePayload>({
    price: "",
    valid_until: "",
    notes: "",
    milestones: [],
  });

  const pendingMilestones = computed(() =>
    (detail.value?.milestones ?? []).filter((m) =>
      ["pending", "in_progress", "submitted", "revision_requested"].includes(m.status),
    ),
  );
  const completedMilestones = computed(() =>
    (detail.value?.milestones ?? []).filter((m) =>
      ["approved", "cancelled"].includes(m.status),
    ),
  );
  const latestQuote = computed<Quote | null>(() => detail.value?.latest_quote ?? null);
  const canAcceptQuote = computed(
    () => latestQuote.value?.status === "sent",
  );

  async function loadOrders(params?: Record<string, unknown>) {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = null;
    try {
      if (auth.isPreviewSession) {
        orders.value = PREVIEW_ORDERS;
        return;
      }
      const res = await specialOrdersApi.list(params);
      orders.value = normalizeList(res.data);
    } catch {
      error.value = "Failed to load special orders.";
    } finally {
      isLoading.value = false;
    }
  }

  async function loadDetail(id: number | string) {
    const auth = useAuthStore();
    isLoadingDetail.value = true;
    detail.value = null;
    error.value = null;
    try {
      if (auth.isPreviewSession) {
        detail.value = PREVIEW_DETAIL;
        return;
      }
      const res = await specialOrdersApi.get(id);
      const data = res.data;
      // Ensure required array/count fields always exist
      detail.value = {
        ...data,
        milestones: data.milestones ?? [],
        quotes: data.quotes ?? [],
        total_milestones: data.total_milestones ?? 0,
        completed_milestones: data.completed_milestones ?? 0,
        attachments_count: data.attachments_count ?? 0,
      };
    } catch {
      error.value = "Failed to load special order detail.";
    } finally {
      isLoadingDetail.value = false;
    }
  }

  async function submitQuote(orderId: number | string) {
    const auth = useAuthStore();
    isSaving.value = true;
    try {
      if (auth.isPreviewSession) {
        showQuoteForm.value = false;
        return;
      }
      const res = await specialOrdersApi.quotes.submit(orderId, quoteForm.value);
      if (detail.value) {
        detail.value.quotes.push(res.data);
        detail.value.latest_quote = res.data;
        detail.value.status = "quote_sent";
      }
      showQuoteForm.value = false;
    } finally {
      isSaving.value = false;
    }
  }

  async function acceptQuote(orderId: number | string, quoteId: number | string) {
    const auth = useAuthStore();
    isSaving.value = true;
    try {
      if (auth.isPreviewSession) {
        if (detail.value?.latest_quote) detail.value.latest_quote.status = "accepted";
        if (detail.value) detail.value.status = "quote_accepted";
        return;
      }
      await specialOrdersApi.quotes.accept(orderId, quoteId);
      await loadDetail(orderId);
    } finally {
      isSaving.value = false;
    }
  }

  async function rejectQuote(orderId: number | string, quoteId: number | string, reason: string) {
    const auth = useAuthStore();
    isSaving.value = true;
    try {
      if (auth.isPreviewSession) {
        if (detail.value?.latest_quote) detail.value.latest_quote.status = "rejected";
        if (detail.value) detail.value.status = "quote_rejected";
        return;
      }
      await specialOrdersApi.quotes.reject(orderId, quoteId, reason);
      await loadDetail(orderId);
    } finally {
      isSaving.value = false;
    }
  }

  async function deliverMilestone(
    orderId: number | string,
    milestoneId: number | string,
    payload: DeliverMilestonePayload,
  ) {
    const auth = useAuthStore();
    isSaving.value = true;
    try {
      if (auth.isPreviewSession) {
        if (detail.value) {
          const m = detail.value.milestones.find((m) => m.id === Number(milestoneId));
          if (m) { m.status = "submitted"; m.delivered_at = new Date().toISOString(); }
        }
        return;
      }
      const res = await specialOrdersApi.milestones.deliver(orderId, milestoneId, payload);
      if (detail.value) {
        const idx = detail.value.milestones.findIndex((m) => m.id === Number(milestoneId));
        if (idx !== -1) detail.value.milestones[idx] = res.data;
      }
    } finally {
      isSaving.value = false;
    }
  }

  async function approveMilestone(orderId: number | string, milestoneId: number | string) {
    const auth = useAuthStore();
    isSaving.value = true;
    try {
      if (auth.isPreviewSession) {
        if (detail.value) {
          const m = detail.value.milestones.find((m) => m.id === Number(milestoneId));
          if (m) { m.status = "approved"; m.approved_at = new Date().toISOString(); }
          const done = detail.value.milestones.filter((m) => m.status === "approved").length;
          detail.value.completed_milestones = done;
        }
        return;
      }
      await specialOrdersApi.milestones.approve(orderId, milestoneId);
      await loadDetail(orderId);
    } finally {
      isSaving.value = false;
    }
  }

  function resetQuoteForm() {
    quoteForm.value = { price: "", valid_until: "", notes: "", milestones: [] };
    showQuoteForm.value = false;
  }

  function reset() {
    orders.value = [];
    detail.value = null;
    error.value = null;
    activeTab.value = "milestones";
    resetQuoteForm();
  }

  return {
    orders,
    detail,
    isLoading,
    isLoadingDetail,
    isSaving,
    error,
    activeTab,
    showQuoteForm,
    quoteForm,
    pendingMilestones,
    completedMilestones,
    latestQuote,
    canAcceptQuote,
    loadOrders,
    loadDetail,
    submitQuote,
    acceptQuote,
    rejectQuote,
    deliverMilestone,
    approveMilestone,
    resetQuoteForm,
    reset,
  };
});

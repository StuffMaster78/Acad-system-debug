import { computed, ref } from "vue";
import { defineStore } from "pinia";
import {
  adminPaymentsApi,
  type AdminWalletRecord,
  type RefundRecord,
  type WalletEntryRecord,
  type WriterPayoutRequestRecord,
} from "@/api/adminPayments";
import { useAuthStore } from "@/stores/auth";
import type { AdminPaymentFeedItem, AdminPaymentMetric } from "@/types/adminPayments";

type ListResponse<T> = T[] | { results: T[] };
type PaymentFilter = "all" | "client" | "writer" | "refund";

function normalizeList<T>(data: ListResponse<T>): T[] {
  return Array.isArray(data) ? data : data.results;
}

function numeric(value: string | number | undefined | null) {
  if (value === undefined || value === null || value === "") return 0;
  const parsed = Number(value);
  return Number.isNaN(parsed) ? 0 : parsed;
}

function money(value: string | number | undefined | null, currency = "USD") {
  const amount = numeric(value);
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(amount);
}

function previewWallets(): AdminWalletRecord[] {
  const now = Date.now();
  return [
    {
      id: 31,
      owner_user_id: 101,
      website_id: 1,
      wallet_type: "client",
      currency: "USD",
      status: "active",
      available_balance: "148.00",
      pending_balance: "0.00",
      total_credited: "3100.00",
      total_debited: "2952.00",
      last_activity_at: new Date(now - 1000 * 60 * 22).toISOString(),
    },
    {
      id: 42,
      owner_user_id: 1,
      website_id: 1,
      wallet_type: "writer",
      currency: "USD",
      status: "active",
      available_balance: "420.00",
      pending_balance: "186.00",
      total_credited: "5240.00",
      total_debited: "4634.00",
      last_activity_at: new Date(now - 1000 * 60 * 65).toISOString(),
    },
    {
      id: 43,
      owner_user_id: 2,
      website_id: 2,
      wallet_type: "writer",
      currency: "USD",
      status: "active",
      available_balance: "186.00",
      pending_balance: "0.00",
      total_credited: "1980.00",
      total_debited: "1794.00",
      last_activity_at: new Date(now - 1000 * 60 * 60 * 4).toISOString(),
    },
  ];
}

function previewEntries(): WalletEntryRecord[] {
  const now = Date.now();
  return [
    {
      id: 901,
      wallet_id: 31,
      website_id: 1,
      entry_type: "client_payment",
      direction: "credit",
      status: "completed",
      amount: "240.00",
      reference: "ORD-1042",
      reference_type: "order_payment",
      description: "Client payment for healthcare policy brief",
      created_at: new Date(now - 1000 * 60 * 38).toISOString(),
    },
    {
      id: 902,
      wallet_id: 31,
      website_id: 2,
      entry_type: "client_payment",
      direction: "credit",
      status: "completed",
      amount: "580.00",
      reference: "CLS-15",
      reference_type: "class_payment",
      description: "Client class milestone payment",
      created_at: new Date(now - 1000 * 60 * 60 * 9).toISOString(),
    },
    {
      id: 903,
      wallet_id: 42,
      website_id: 1,
      entry_type: "writer_earning",
      direction: "credit",
      status: "posted",
      amount: "120.00",
      reference: "ORD-1042",
      reference_type: "writer_earning",
      description: "Writer earning posted after order approval",
      created_at: new Date(now - 1000 * 60 * 60 * 3).toISOString(),
    },
  ];
}

function previewPayouts(): WriterPayoutRequestRecord[] {
  const now = Date.now();
  return [
    {
      id: 12,
      wallet_id: 42,
      writer_id: 1,
      writer_email: "amina.writer@preview.local",
      amount: "420.00",
      status: "held",
      workflow_status: "pending_review",
      reason: "Weekly payout request",
      reference: "PAY-12",
      reference_type: "writer_payout",
      created_at: new Date(now - 1000 * 60 * 42).toISOString(),
    },
    {
      id: 13,
      wallet_id: 43,
      writer_id: 2,
      writer_email: "jon.writer@preview.local",
      amount: "186.00",
      status: "released",
      workflow_status: "approved",
      reason: "Completed order earnings",
      reference: "PAY-13",
      reference_type: "writer_payout",
      created_at: new Date(now - 1000 * 60 * 60 * 5).toISOString(),
      released_at: new Date(now - 1000 * 60 * 60 * 2).toISOString(),
    },
  ];
}

function previewRefunds(): RefundRecord[] {
  const now = Date.now();
  return [
    {
      id: 71,
      order: "ORD-1038",
      client: "caleb@example.com",
      amount: "90.00",
      wallet_amount: "90.00",
      external_amount: "0.00",
      status: "pending",
      refund_method: "wallet",
      reason: "Client cancellation within grace period",
      created_at: new Date(now - 1000 * 60 * 60 * 7).toISOString(),
    },
  ];
}

export const useAdminPaymentsStore = defineStore("admin-payments", () => {
  const wallets = ref<AdminWalletRecord[]>([]);
  const walletEntries = ref<WalletEntryRecord[]>([]);
  const payouts = ref<WriterPayoutRequestRecord[]>([]);
  const refunds = ref<RefundRecord[]>([]);
  const query = ref("");
  const filter = ref<PaymentFilter>("all");
  const isLoading = ref(false);
  const isMutating = ref(false);
  const error = ref("");
  const notice = ref("");

  const clientPayments = computed(() =>
    walletEntries.value.filter((entry) => {
      const text = `${entry.entry_type ?? ""} ${entry.reference_type ?? ""} ${entry.description ?? ""}`.toLowerCase();
      return entry.direction === "credit" && (text.includes("client") || text.includes("order_payment") || text.includes("class_payment"));
    }),
  );

  const feed = computed<AdminPaymentFeedItem[]>(() => {
    const items: AdminPaymentFeedItem[] = [
      ...clientPayments.value.map((entry) => ({
        id: `entry-${entry.id}`,
        source: "client" as const,
        title: entry.reference || `Wallet entry #${entry.id}`,
        subtitle: entry.description || entry.reference_type || "Client payment",
        amount: entry.amount,
        status: entry.status || "posted",
        date: entry.created_at,
      })),
      ...payouts.value.map((payout) => ({
        id: `payout-${payout.id}`,
        source: "writer" as const,
        title: payout.writer_email || `Writer #${payout.writer_id ?? payout.id}`,
        subtitle: payout.reason || payout.reference || "Writer payout request",
        amount: payout.amount,
        status: payout.workflow_status || payout.status,
        date: payout.created_at,
      })),
      ...refunds.value.map((refund) => ({
        id: `refund-${refund.id}`,
        source: "refund" as const,
        title: `Refund #${refund.id}`,
        subtitle: refund.reason || String(refund.order || "Refund request"),
        amount: refund.amount ?? refund.wallet_amount ?? refund.external_amount ?? 0,
        status: refund.status,
        date: refund.created_at,
      })),
    ].sort((a, b) => new Date(b.date || 0).getTime() - new Date(a.date || 0).getTime());

    const needle = query.value.trim().toLowerCase();
    return items.filter((item) => {
      const typeMatches = filter.value === "all" || item.source === filter.value;
      const textMatches =
        !needle ||
        [item.title, item.subtitle, item.status, item.source].some((value) =>
          value.toLowerCase().includes(needle),
        );
      return typeMatches && textMatches;
    });
  });

  const metrics = computed<AdminPaymentMetric[]>(() => {
    const clientTotal = clientPayments.value.reduce((sum, entry) => sum + numeric(entry.amount), 0);
    const pendingPayouts = payouts.value.filter((payout) => {
      const status = `${payout.status} ${payout.workflow_status ?? ""}`.toLowerCase();
      return status.includes("pending") || status.includes("held") || status.includes("review");
    });
    const pendingPayoutTotal = pendingPayouts.reduce((sum, payout) => sum + numeric(payout.amount), 0);
    const clientWalletTotal = wallets.value
      .filter((wallet) => wallet.wallet_type === "client")
      .reduce((sum, wallet) => sum + numeric(wallet.available_balance), 0);
    const refundCount = refunds.value.filter((refund) => refund.status !== "processed").length;

    return [
      {
        label: "Client payments",
        value: money(clientTotal),
        detail: `${clientPayments.value.length} incoming wallet/order entries in scope.`,
        tone: "good",
      },
      {
        label: "Writer payout queue",
        value: money(pendingPayoutTotal),
        detail: `${pendingPayouts.length} requests pending review or processing.`,
        tone: pendingPayouts.length ? "warn" : "good",
      },
      {
        label: "Client wallet balance",
        value: money(clientWalletTotal),
        detail: "Available client wallet funds visible to admin.",
        tone: "neutral",
      },
      {
        label: "Refunds",
        value: refundCount,
        detail: "Refund requests not yet fully processed.",
        tone: refundCount ? "risk" : "neutral",
      },
    ];
  });

  async function hydrate() {
    const auth = useAuthStore();
    isLoading.value = true;
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        wallets.value = previewWallets();
        walletEntries.value = previewEntries();
        payouts.value = previewPayouts();
        refunds.value = previewRefunds();
        return;
      }

      const [walletRes, payoutRes, refundRes] = await Promise.allSettled([
        adminPaymentsApi.wallets({ page_size: 50 }),
        adminPaymentsApi.payoutRequests(),
        adminPaymentsApi.refunds(),
      ]);

      if (walletRes.status === "fulfilled") wallets.value = normalizeList(walletRes.value.data);
      if (payoutRes.status === "fulfilled") payouts.value = normalizeList(payoutRes.value.data);
      if (refundRes.status === "fulfilled") refunds.value = normalizeList(refundRes.value.data);

      const entryResponses = await Promise.allSettled(
        wallets.value.slice(0, 12).map((wallet) =>
          adminPaymentsApi.walletEntries(wallet.id, { page_size: 25 }),
        ),
      );
      walletEntries.value = entryResponses.flatMap((response) =>
        response.status === "fulfilled" ? normalizeList(response.value.data) : [],
      );
    } catch (caught) {
      error.value = "Unable to load admin payment operations.";
      throw caught;
    } finally {
      isLoading.value = false;
    }
  }

  async function approvePayout(payoutId: number) {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        payouts.value = payouts.value.map((payout) =>
          payout.id === payoutId
            ? { ...payout, workflow_status: "approved", status: "released" }
            : payout,
        );
        notice.value = "Preview payout approved.";
        return;
      }
      await adminPaymentsApi.approvePayout(payoutId, "Approved from admin payments.");
      notice.value = "Payout approved.";
      await hydrate();
    } finally {
      isMutating.value = false;
    }
  }

  async function processPayout(payoutId: number) {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        payouts.value = payouts.value.map((payout) =>
          payout.id === payoutId
            ? { ...payout, workflow_status: "processed", status: "captured", captured_at: new Date().toISOString() }
            : payout,
        );
        notice.value = "Preview payout processed.";
        return;
      }
      await adminPaymentsApi.processPayout(payoutId, `ADMIN-${payoutId}`);
      notice.value = "Payout marked processed.";
      await hydrate();
    } finally {
      isMutating.value = false;
    }
  }

  async function rejectPayout(payoutId: number) {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";
    try {
      if (auth.isPreviewSession) {
        payouts.value = payouts.value.map((payout) =>
          payout.id === payoutId
            ? { ...payout, workflow_status: "rejected", status: "rejected" }
            : payout,
        );
        notice.value = "Preview payout rejected.";
        return;
      }
      await adminPaymentsApi.rejectPayout(payoutId, "Rejected from admin payments.");
      notice.value = "Payout rejected.";
      await hydrate();
    } finally {
      isMutating.value = false;
    }
  }

  return {
    wallets,
    walletEntries,
    payouts,
    refunds,
    clientPayments,
    feed,
    metrics,
    query,
    filter,
    isLoading,
    isMutating,
    error,
    notice,
    hydrate,
    approvePayout,
    processPayout,
    rejectPayout,
  };
});

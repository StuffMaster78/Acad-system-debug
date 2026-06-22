import { computed, ref } from "vue";
import { defineStore } from "pinia";
import {
  adminPaymentsApi,
  type AdminWalletRecord,
  type FinancialOverviewResponse,
  type FinanceDashboardResponse,
  type RefundRecord,
  type QueueResponse,
  type WalletEntryRecord,
  type ReceiptRecord,
  type WriterPaymentRecord,
  type WriterPayoutRequestRecord,
} from "@/api/adminPayments";
import { useAuthStore } from "@/stores/auth";
import { usePortalContextStore } from "@/stores/portalContext";
import type {
  AdminPaymentFeedItem,
  AdminPaymentMetric,
  FinanceOpsItem,
  FinanceOpsSummary,
} from "@/types/adminPayments";

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

function pickNumber(record: Record<string, unknown>, keys: string[]) {
  for (const key of keys) {
    const value = record[key];
    if (value !== undefined && value !== null && value !== "") return numeric(value as string | number);
  }
  return 0;
}

function pickString(record: Record<string, unknown>, keys: string[], fallback = "") {
  for (const key of keys) {
    const value = record[key];
    if (value !== undefined && value !== null && value !== "") return String(value);
  }
  return fallback;
}

function asRecords(value: unknown): Array<Record<string, unknown>> {
  return Array.isArray(value) ? value.filter((item): item is Record<string, unknown> => typeof item === "object" && item !== null) : [];
}

function recordsFromQueue(data: QueueResponse, keys: string[]) {
  for (const key of keys) {
    const records = asRecords(data[key]);
    if (records.length) return records;
  }
  return asRecords(data.results);
}

function resolvedWebsiteParams(extra: Record<string, unknown> = {}) {
  const portalCtx = usePortalContextStore();
  return portalCtx.website?.id ? { ...extra, website_id: portalCtx.website.id } : extra;
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
      order_payment: null,
      payment_refund: null,
      order: 1038,
      client: 5,
      website: null,
      type: null,
      wallet_amount: "90.00",
      external_amount: "0.00",
      refund_method: "wallet",
      reason: "Client cancellation within grace period",
      processed_by: null,
      processed_at: null,
      status: "pending",
      metadata: null,
      error_message: null,
      total_amount: "90.00",
      refundable_amount: "90.00",
      created_at: new Date(now - 1000 * 60 * 60 * 7).toISOString(),
      updated_at: new Date(now - 1000 * 60 * 60 * 7).toISOString(),
    },
  ];
}

export const useAdminPaymentsStore = defineStore("admin-payments", () => {
  const wallets = ref<AdminWalletRecord[]>([]);
  const walletEntries = ref<WalletEntryRecord[]>([]);
  const receipts = ref<ReceiptRecord[]>([]);
  const receiptsLoading = ref(false);
  const payouts = ref<WriterPayoutRequestRecord[]>([]);
  const refunds = ref<RefundRecord[]>([]);
  const financialOverview = ref<FinancialOverviewResponse>({});
  const writerPayments = ref<WriterPaymentRecord[]>([]);
  const refundDashboard = ref<FinanceDashboardResponse>({});
  const disputeDashboard = ref<FinanceDashboardResponse>({});
  const tipDashboard = ref<FinanceDashboardResponse>({});
  const pendingRefundQueue = ref<FinanceOpsItem[]>([]);
  const disputeQueue = ref<FinanceOpsItem[]>([]);
  const paymentMilestones = ref<FinanceOpsItem[]>([]);
  const pendingDeposits = ref<FinanceOpsItem[]>([]);
  const tipQueue = ref<FinanceOpsItem[]>([]);
  const opsFilter = ref<"all" | FinanceOpsItem["source"]>("all");
  const cycleFilter = ref<"all" | "BIWEEKLY" | "MONTHLY">("all");
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
        website_id: entry.website_id ?? null,
      })),
      ...payouts.value.map((payout) => ({
        id: `payout-${payout.id}`,
        source: "writer" as const,
        title: payout.writer_email || `Writer #${payout.writer_id ?? payout.id}`,
        subtitle: payout.reason || payout.reference || "Writer payout request",
        amount: payout.amount,
        status: payout.workflow_status || payout.status,
        date: payout.created_at,
        website_id: payout.website_id ?? null,
      })),
      ...refunds.value.map((refund) => ({
        id: `refund-${refund.id}`,
        source: "refund" as const,
        title: `Refund #${refund.id}`,
        subtitle: refund.reason || String(refund.order || "Refund request"),
        amount: refund.total_amount ?? refund.wallet_amount ?? refund.external_amount ?? 0,
        status: refund.status,
        date: refund.created_at,
        website_id: refund.website ?? null,
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

  const platformMetrics = computed<AdminPaymentMetric[]>(() => {
    const summary = financialOverview.value.summary;
    if (!summary) return metrics.value;

    return [
      {
        label: "Gross revenue",
        value: money(summary.total_revenue),
        detail: `Orders ${money(summary.revenue_breakdown?.orders)} · special ${money(summary.revenue_breakdown?.special_orders)} · classes ${money(summary.revenue_breakdown?.classes)}.`,
        tone: "good",
      },
      {
        label: "Writer expenses",
        value: money(summary.total_expenses),
        detail: `Payouts ${money(summary.expenses_breakdown?.writer_payments)} · tips ${money(summary.expenses_breakdown?.tips)}.`,
        tone: "warn",
      },
      {
        label: "Net revenue",
        value: money(summary.net_revenue),
        detail: `${Number(summary.profit_margin ?? 0).toFixed(1)}% platform margin.`,
        tone: numeric(summary.net_revenue) >= 0 ? "good" : "risk",
      },
      {
        label: "Payout records",
        value: String(writerPayments.value.length),
        detail: "Historical writer payment rows from finance overview.",
        tone: "neutral",
      },
    ];
  });

  const financeOpsItems = computed(() => {
    const items = [
      ...pendingRefundQueue.value,
      ...disputeQueue.value,
      ...paymentMilestones.value,
      ...pendingDeposits.value,
      ...tipQueue.value,
    ].sort((a, b) => new Date(b.date || 0).getTime() - new Date(a.date || 0).getTime());

    return items.filter((item) => opsFilter.value === "all" || item.source === opsFilter.value);
  });

  const financeOpsMetrics = computed<FinanceOpsSummary[]>(() => {
    const refundSummary = refundDashboard.value.summary ?? {};
    const disputeSummary = disputeDashboard.value.summary ?? {};
    const tipSummary = tipDashboard.value.summary ?? {};
    return [
      {
        label: "Pending refunds",
        value: refundSummary.pending_refunds ?? pendingRefundQueue.value.length,
        detail: `${money(refundSummary.pending_amount as number | string | undefined)} pending refund exposure.`,
        tone: pendingRefundQueue.value.length ? "risk" : "neutral",
      },
      {
        label: "Open disputes",
        value: disputeSummary.pending_disputes ?? disputeQueue.value.length,
        detail: `${disputeSummary.awaiting_response ?? 0} awaiting response.`,
        tone: disputeQueue.value.length ? "warn" : "neutral",
      },
      {
        label: "Class funding",
        value: pendingDeposits.value.length + paymentMilestones.value.length,
        detail: "Pending deposits and unpaid class milestones.",
        tone: pendingDeposits.value.length || paymentMilestones.value.length ? "warn" : "good",
      },
      {
        label: "Tips volume",
        value: money(tipSummary.total_tip_amount as number | string | undefined),
        detail: `${tipSummary.total_tips ?? tipQueue.value.length} tip records visible.`,
        tone: "good",
      },
    ];
  });

  const filteredWriterPayments = computed(() => {
    if (cycleFilter.value === "all") return writerPayments.value;
    return writerPayments.value.filter(
      (p) => (p.type ?? "").toUpperCase() === cycleFilter.value,
    );
  });

  const cycleBreakdown = computed(() => {
    const groups: Record<string, { count: number; total: number; writerTotal: number; margin: number }> = {};
    for (const p of writerPayments.value) {
      const key = (p.type ?? "Manual").toUpperCase();
      if (!groups[key]) groups[key] = { count: 0, total: 0, writerTotal: 0, margin: 0 };
      groups[key].count += 1;
      groups[key].total += numeric(p.client_total ?? p.total_amount ?? p.amount);
      groups[key].writerTotal += numeric(p.total_earnings ?? p.total_amount ?? p.amount);
      groups[key].margin += numeric(p.platform_margin);
    }
    return Object.entries(groups).map(([cycle, stats]) => ({ cycle, ...stats }));
  });

  function normalizeRefundOps(record: Record<string, unknown>): FinanceOpsItem {
    return {
      id: record.id as number | string,
      source: "refund",
      title: `Refund #${record.id}`,
      subtitle: pickString(record, ["reason", "client", "order", "order_payment_id"], "Refund request"),
      amount: pickNumber(record, ["amount", "wallet_amount", "external_amount", "total_amount"]),
      status: pickString(record, ["status"], "pending"),
      date: pickString(record, ["created_at", "processed_at"], ""),
      meta: record,
    };
  }

  function normalizeDisputeOps(record: Record<string, unknown>): FinanceOpsItem {
    return {
      id: record.id as number | string,
      source: "dispute",
      title: pickString(record, ["order_topic", "topic"], `Dispute #${record.id}`),
      subtitle: pickString(record, ["raised_by", "client", "order_id"], "Order dispute"),
      status: pickString(record, ["status", "dispute_status"], "open"),
      date: pickString(record, ["created_at", "updated_at"], ""),
      meta: record,
    };
  }

  function normalizeMilestoneOps(record: Record<string, unknown>): FinanceOpsItem {
    return {
      id: record.id as number | string,
      source: "milestone",
      title: pickString(record, ["title", "label", "class_order", "order_title"], `Milestone #${record.id}`),
      subtitle: pickString(record, ["client_email", "client", "description"], "Class payment milestone"),
      amount: pickNumber(record, ["amount", "due_amount", "balance_amount"]),
      status: pickString(record, ["status"], "unpaid"),
      date: pickString(record, ["due_at", "created_at"], ""),
      meta: record,
    };
  }

  function normalizeDepositOps(record: Record<string, unknown>): FinanceOpsItem {
    return {
      id: record.id as number | string,
      source: "deposit",
      title: pickString(record, ["topic", "title", "class_name"], `Class order #${record.id}`),
      subtitle: pickString(record, ["client_email", "client", "status"], "Pending class funding"),
      amount: pickNumber(record, ["balance_amount", "amount_due", "final_amount"]),
      status: pickString(record, ["status"], "pending_payment"),
      date: pickString(record, ["created_at", "updated_at"], ""),
      meta: record,
    };
  }

  function normalizeTipOps(record: Record<string, unknown>): FinanceOpsItem {
    return {
      id: record.id as number | string,
      source: "tip",
      title: pickString(record, ["writer_email", "receiver_email", "writer", "receiver"], `Tip #${record.id}`),
      subtitle: pickString(record, ["client_email", "sender_email", "tip_type", "payment_status"], "Tip record"),
      amount: pickNumber(record, ["tip_amount", "amount", "writer_earning"]),
      status: pickString(record, ["payment_status", "status"], "pending"),
      date: pickString(record, ["sent_at", "created_at"], ""),
      meta: record,
    };
  }

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

      const scopedParams = resolvedWebsiteParams();
      const [walletRes, payoutRes, refundRes] = await Promise.allSettled([
        adminPaymentsApi.wallets(resolvedWebsiteParams({ page_size: 50 })),
        adminPaymentsApi.payoutRequests(scopedParams),
        adminPaymentsApi.refunds(scopedParams),
      ]);

      if (walletRes.status === "fulfilled") wallets.value = normalizeList(walletRes.value.data);
      if (payoutRes.status === "fulfilled") payouts.value = normalizeList(payoutRes.value.data);
      if (refundRes.status === "fulfilled") refunds.value = normalizeList(refundRes.value.data);

      const entryResponses = await Promise.allSettled(
        wallets.value.slice(0, 12).map((wallet) =>
          adminPaymentsApi.walletEntries(wallet.id, resolvedWebsiteParams({ page_size: 25 })),
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

  async function hydratePlatformFinance() {
    const auth = useAuthStore();
    await hydrate();

    if (auth.isPreviewSession) {
      financialOverview.value = {
        summary: {
          total_revenue: 1243700,
          revenue_breakdown: { orders: 982400, special_orders: 141800, classes: 119500 },
          total_expenses: 462900,
          expenses_breakdown: { writer_payments: 438200, tips: 24700 },
          net_revenue: 780800,
          profit_margin: 62.8,
        },
        period_breakdown: [
          {
            period: "2026-05",
            month: "May 2026",
            revenue: { orders: 184200, special_orders: 20800, classes: 14200, total: 219200 },
            expenses: { writer_payments: 78100, total: 78100 },
            net_revenue: 141100,
          },
          {
            period: "2026-04",
            month: "April 2026",
            revenue: { orders: 164900, special_orders: 17600, classes: 10900, total: 193400 },
            expenses: { writer_payments: 70400, total: 70400 },
            net_revenue: 123000,
          },
        ],
      };
      writerPayments.value = [
        {
          id: 501,
          payment_id: "payout-501",
          writer_email: "amina.writer@preview.local",
          writer: { name: "Amina K.", email: "amina.writer@preview.local", registration_id: "WR-0041" },
          website: "NurseMyGrade",
          type: "BIWEEKLY",
          amount: 1240,
          total_earnings: 1275,
          tips: 35,
          fines: 0,
          status: "paid",
          paid_at: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
          date: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
          number_of_orders: 8,
          order_count: 8,
          client_total: 2840,
          platform_margin: 1600,
          reference: "payout-501",
          batch_reference: "batch-71",
        },
        {
          id: 502,
          payment_id: "payout-502",
          writer_email: "jon.writer@preview.local",
          writer: { name: "Jon M.", email: "jon.writer@preview.local", registration_id: "WR-0055" },
          website: "EssayManiacs",
          type: "MONTHLY",
          amount: 860,
          total_earnings: 820,
          tips: 0,
          fines: 40,
          status: "paid",
          paid_at: new Date(Date.now() - 1000 * 60 * 60 * 28).toISOString(),
          date: new Date(Date.now() - 1000 * 60 * 60 * 28).toISOString(),
          number_of_orders: 5,
          order_count: 5,
          client_total: 1930,
          platform_margin: 1070,
          reference: "payout-502",
          batch_reference: "batch-70",
        },
        {
          id: 503,
          payment_id: "payout-503",
          writer_email: "priya.writer@preview.local",
          writer: { name: "Priya S.", email: "priya.writer@preview.local", registration_id: "WR-0062" },
          website: "NurseMyGrade",
          type: "BIWEEKLY",
          amount: 720,
          total_earnings: 720,
          tips: 0,
          fines: 0,
          status: "paid",
          paid_at: new Date(Date.now() - 1000 * 60 * 60 * 36).toISOString(),
          date: new Date(Date.now() - 1000 * 60 * 60 * 36).toISOString(),
          number_of_orders: 4,
          order_count: 4,
          client_total: 1540,
          platform_margin: 820,
          reference: "payout-503",
          batch_reference: "batch-71",
        },
      ];
      refundDashboard.value = {
        summary: { pending_refunds: 1, pending_amount: 90, processed_recent: 7, processed_amount: 840 },
      };
      disputeDashboard.value = {
        summary: { pending_disputes: 2, awaiting_response: 1, resolved_recent: 6 },
      };
      tipDashboard.value = {
        summary: { total_tips: 42, total_tip_amount: 24700, total_writer_earnings: 19800, total_platform_profit: 4900 },
      };
      pendingRefundQueue.value = previewRefunds().map((refund) => normalizeRefundOps(refund as unknown as Record<string, unknown>));
      disputeQueue.value = [
        {
          id: 801,
          source: "dispute",
          title: "Healthcare policy brief dispute",
          subtitle: "Raised by caleb@example.com",
          status: "open",
          date: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(),
        },
        {
          id: 802,
          source: "dispute",
          title: "Class weekly quiz dispute",
          subtitle: "Awaiting writer response",
          status: "open",
          date: new Date(Date.now() - 1000 * 60 * 60 * 11).toISOString(),
        },
      ];
      paymentMilestones.value = [
        {
          id: 901,
          source: "milestone",
          title: "Nursing class milestone 2",
          subtitle: "Due this week",
          amount: 320,
          status: "due",
          date: new Date(Date.now() + 1000 * 60 * 60 * 24 * 2).toISOString(),
        },
      ];
      pendingDeposits.value = [
        {
          id: 902,
          source: "deposit",
          title: "Statistics class bundle",
          subtitle: "Partial funding still required",
          amount: 480,
          status: "partially_paid",
          date: new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(),
        },
      ];
      tipQueue.value = [
        {
          id: 1001,
          source: "tip",
          title: "amina.writer@preview.local",
          subtitle: "Client tip posted",
          amount: 35,
          status: "completed",
          date: new Date(Date.now() - 1000 * 60 * 28).toISOString(),
        },
      ];
      return;
    }

    const [
      overviewRes,
      writerPaymentsRes,
      refundDashRes,
      pendingRefundsRes,
      disputeDashRes,
      pendingDisputesRes,
      milestonesRes,
      depositsRes,
      tipDashRes,
      tipsRes,
    ] = await Promise.allSettled([
      adminPaymentsApi.financialOverview(resolvedWebsiteParams()),
      adminPaymentsApi.allWriterPayments(resolvedWebsiteParams({ page_size: 100 })),
      adminPaymentsApi.refundDashboard(resolvedWebsiteParams()),
      adminPaymentsApi.pendingRefunds(resolvedWebsiteParams()),
      adminPaymentsApi.disputeDashboard(resolvedWebsiteParams()),
      adminPaymentsApi.pendingDisputes(resolvedWebsiteParams()),
      adminPaymentsApi.classPaymentMilestones(resolvedWebsiteParams()),
      adminPaymentsApi.pendingClassDeposits(resolvedWebsiteParams()),
      adminPaymentsApi.tipDashboard(resolvedWebsiteParams()),
      adminPaymentsApi.tipList(resolvedWebsiteParams()),
    ]);
    if (overviewRes.status === "fulfilled") financialOverview.value = overviewRes.value.data;
    if (writerPaymentsRes.status === "fulfilled") {
      const data = writerPaymentsRes.value.data;
      writerPayments.value = Array.isArray(data) ? data : data.payments ?? data.results ?? [];
    }
    if (refundDashRes.status === "fulfilled") refundDashboard.value = refundDashRes.value.data;
    if (pendingRefundsRes.status === "fulfilled") {
      pendingRefundQueue.value = recordsFromQueue(pendingRefundsRes.value.data, ["refunds"]).map(normalizeRefundOps);
    }
    if (disputeDashRes.status === "fulfilled") disputeDashboard.value = disputeDashRes.value.data;
    if (pendingDisputesRes.status === "fulfilled") {
      disputeQueue.value = recordsFromQueue(pendingDisputesRes.value.data, ["disputes"]).map(normalizeDisputeOps);
    }
    if (milestonesRes.status === "fulfilled") {
      paymentMilestones.value = recordsFromQueue(milestonesRes.value.data, ["payment_milestones"]).map(normalizeMilestoneOps);
    }
    if (depositsRes.status === "fulfilled") {
      pendingDeposits.value = recordsFromQueue(depositsRes.value.data, ["class_orders"]).map(normalizeDepositOps);
    }
    if (tipDashRes.status === "fulfilled") tipDashboard.value = tipDashRes.value.data;
    if (tipsRes.status === "fulfilled") {
      tipQueue.value = recordsFromQueue(tipsRes.value.data, ["results"]).map(normalizeTipOps);
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

  function patchFinanceOpsItem(itemId: number | string, source: FinanceOpsItem["source"], status: string) {
    const patch = (item: FinanceOpsItem) =>
      item.id === itemId && item.source === source ? { ...item, status } : item;

    pendingRefundQueue.value = pendingRefundQueue.value.map(patch);
    disputeQueue.value = disputeQueue.value.map(patch);
    paymentMilestones.value = paymentMilestones.value.map(patch);
    pendingDeposits.value = pendingDeposits.value.map(patch);
    tipQueue.value = tipQueue.value.map(patch);
  }

  async function applyFinanceControl(item: FinanceOpsItem, action: string, note: string) {
    const auth = useAuthStore();
    isMutating.value = true;
    notice.value = "";
    error.value = "";

    try {
      if (auth.isPreviewSession) {
        patchFinanceOpsItem(item.id, item.source, action);
        notice.value = `Preview finance action applied: ${action}.`;
        return;
      }

      if (item.source === "refund" && action === "process_refund") {
        await adminPaymentsApi.processRefund(item.id, note);
      } else if (item.source === "refund" && action === "cancel_refund") {
        await adminPaymentsApi.cancelRefund(item.id, note);
      } else if (item.source === "dispute" && action === "resolve_dispute") {
        await adminPaymentsApi.resolveDispute(item.id, note);
      } else if (item.source === "dispute" && action === "close_dispute") {
        await adminPaymentsApi.closeDispute(item.id, note);
      } else {
        patchFinanceOpsItem(item.id, item.source, action);
      }

      notice.value = "Finance control applied.";
      await hydratePlatformFinance();
    } catch (caught) {
      error.value = "Unable to apply finance control.";
      throw caught;
    } finally {
      isMutating.value = false;
    }
  }

  async function fetchReceipts() {
    receiptsLoading.value = true;
    try {
      const { data } = await adminPaymentsApi.receipts({ page_size: 50 });
      receipts.value = Array.isArray(data) ? data : (data as { results: ReceiptRecord[] }).results ?? [];
    } catch {
      // non-critical
    } finally {
      receiptsLoading.value = false;
    }
  }

  return {
    wallets,
    walletEntries,
    receipts,
    receiptsLoading,
    payouts,
    refunds,
    financialOverview,
    writerPayments,
    refundDashboard,
    disputeDashboard,
    tipDashboard,
    pendingRefundQueue,
    disputeQueue,
    paymentMilestones,
    pendingDeposits,
    tipQueue,
    clientPayments,
    feed,
    metrics,
    platformMetrics,
    financeOpsItems,
    financeOpsMetrics,
    opsFilter,
    cycleFilter,
    filteredWriterPayments,
    cycleBreakdown,
    query,
    filter,
    isLoading,
    isMutating,
    error,
    notice,
    hydrate,
    hydratePlatformFinance,
    approvePayout,
    processPayout,
    rejectPayout,
    applyFinanceControl,
    fetchReceipts,
  };
});

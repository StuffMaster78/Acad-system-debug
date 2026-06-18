<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import AppChart from "@/components/ui/AppChart.vue";
import { analyticsChartsApi, type ChartData } from "@/api/analyticsCharts";
import type { EChartsOption } from "echarts";
import {
  AlertTriangle,
  CheckCircle2,
  CircleDollarSign,
  CreditCard,
  Landmark,
  RefreshCw,
  Scale,
  Search,
  Send,
  TrendingUp,
  WalletCards,
  XCircle,
} from "@lucide/vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import MetricTile from "@/components/ui/MetricTile.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useAdminPaymentsStore } from "@/stores/adminPayments";
import { useWebsitesStore } from "@/stores/websites";

const finance = useAdminPaymentsStore();
const websitesStore = useWebsitesStore();

const activityWebsite = ref<number | "">("");
const websiteFilteredFeed = computed(() => {
  if (!activityWebsite.value) return finance.feed;
  return finance.feed.filter((item) => item.website_id === activityWebsite.value);
});

onMounted(() => websitesStore.ensure());

const filterOptions = [
  { key: "all", label: "All" },
  { key: "client", label: "Client payments" },
  { key: "writer", label: "Writer payouts" },
  { key: "refund", label: "Refunds" },
] as const;

const opsFilterOptions = [
  { key: "all", label: "All ops" },
  { key: "refund", label: "Refunds" },
  { key: "dispute", label: "Disputes" },
  { key: "milestone", label: "Milestones" },
  { key: "deposit", label: "Deposits" },
  { key: "tip", label: "Tips" },
] as const;

const revenueRows = computed(() => finance.financialOverview.period_breakdown ?? []);
const financeControl = reactive({
  itemKey: "",
  action: "process_refund",
  note: "Finance control action from superadmin finance operations.",
});

const selectedFinanceItem = computed(() => {
  const [source, id] = financeControl.itemKey.split(":");
  return finance.financeOpsItems.find((item) => `${item.source}` === source && `${item.id}` === id) ?? finance.financeOpsItems[0];
});

const financeActions = computed(() => {
  if (selectedFinanceItem.value?.source === "refund") {
    return [
      { key: "process_refund", label: "Process refund" },
      { key: "cancel_refund", label: "Cancel refund" },
    ];
  }
  if (selectedFinanceItem.value?.source === "dispute") {
    return [
      { key: "resolve_dispute", label: "Resolve dispute" },
      { key: "close_dispute", label: "Close dispute" },
    ];
  }
  return [
    { key: "mark_reviewed", label: "Mark reviewed" },
    { key: "escalate", label: "Escalate" },
  ];
});

function numeric(value: unknown) {
  const parsed = Number(value ?? 0);
  return Number.isFinite(parsed) ? parsed : 0;
}

function formatDate(value?: string | null) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function formatAmount(value: unknown, currency = "USD") {
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(numeric(value));
}

function statusTone(status?: string | null) {
  const normalized = (status ?? "").toLowerCase();
  if (normalized.includes("failed") || normalized.includes("rejected") || normalized.includes("cancel")) return "danger";
  if (normalized.includes("pending") || normalized.includes("held") || normalized.includes("review")) return "warning";
  if (normalized.includes("complete") || normalized.includes("approved") || normalized.includes("released") || normalized.includes("posted") || normalized.includes("captured") || normalized.includes("paid")) return "success";
  return "neutral";
}

function sourceLabel(source: string) {
  if (source === "milestone") return "Payment milestone";
  if (source === "deposit") return "Class deposit";
  return source;
}

// ── Charts ────────────────────────────────────────────────────────────────────
const websiteChart = ref<ChartData | null>(null);
const chartsLoading = ref(false);

const revenueTrendOption = computed<EChartsOption>(() => {
  const rows = revenueRows.value;
  if (!rows.length) return {};
  return {
    tooltip: { trigger: "axis", confine: true },
    legend: { data: ["Revenue", "Expenses", "Net"], bottom: 8, type: "scroll" },
    grid: { left: 12, right: 12, top: 24, bottom: 60, containLabel: true },
    xAxis: { type: "category", data: rows.map((r) => r.month || r.period || ""), axisLabel: { rotate: 30, fontSize: 10, hideOverlap: true } },
    yAxis: { type: "value", axisLabel: { formatter: (v: number) => `$${(v / 1000).toFixed(0)}k` } },
    series: [
      { name: "Revenue", type: "line", data: rows.map((r) => Number(r.revenue?.total ?? 0)), smooth: true, itemStyle: { color: "#7c3aed" }, lineStyle: { color: "#7c3aed", width: 2 }, areaStyle: { color: "rgba(124,58,237,0.07)" } },
      { name: "Expenses", type: "line", data: rows.map((r) => Number(r.expenses?.total ?? 0)), smooth: true, itemStyle: { color: "#f59e0b" }, lineStyle: { color: "#f59e0b" } },
      { name: "Net", type: "bar", data: rows.map((r) => Number(r.net_revenue ?? 0)), itemStyle: { color: "#10b981" } },
    ],
  };
});

const websiteChartOption = computed<EChartsOption>(() => {
  if (!websiteChart.value) return {};
  const d = websiteChart.value;
  return {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, confine: true },
    grid: { left: 12, right: 32, top: 10, bottom: 12, containLabel: true },
    xAxis: { type: "value", axisLabel: { formatter: (v: number) => `$${(v / 1000).toFixed(0)}k` } },
    yAxis: { type: "category", data: [...d.labels].reverse(), axisLabel: { fontSize: 11, width: 120, overflow: "truncate" } },
    series: [{ name: "Revenue", type: "bar", data: [...d.series[0].data].reverse(), itemStyle: { color: "#7c3aed" }, barMaxWidth: 32 }],
  };
});

onMounted(() => {
  finance.hydratePlatformFinance().then(() => {
    const first = finance.financeOpsItems[0];
    if (first) financeControl.itemKey = `${first.source}:${first.id}`;
  }).catch(() => undefined);

  chartsLoading.value = true;
  analyticsChartsApi.revenueByWebsite({ months: 12, top: 8 })
    .then((r) => { websiteChart.value = r.data; })
    .catch(() => undefined)
    .finally(() => { chartsLoading.value = false; });
});
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Superadmin finance</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Platform payments</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          Cross-tenant revenue, expenses, net margin, refunds, wallet balances, and writer payout operations.
        </p>
      </div>

      <button
        class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
        type="button"
        :disabled="finance.isLoading"
        @click="finance.hydratePlatformFinance().catch(() => undefined)"
      >
        <RefreshCw class="h-4 w-4" :class="finance.isLoading ? 'animate-spin' : ''" />
        Refresh
      </button>
    </section>

    <p v-if="finance.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ finance.error }}
    </p>
    <p v-if="finance.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ finance.notice }}
    </p>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <MetricTile
        v-for="metric in finance.platformMetrics"
        :key="metric.label"
        :metric="{ ...metric, value: String(metric.value) }"
      />
    </section>

    <section class="space-y-4">
      <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricTile
          v-for="metric in finance.financeOpsMetrics"
          :key="metric.label"
          :metric="{ ...metric, value: String(metric.value) }"
        />
      </div>

      <div class="rounded-lg border border-slate-200 bg-white">
        <div class="flex flex-col gap-4 border-b border-slate-200 px-4 py-4 xl:flex-row xl:items-center xl:justify-between">
          <div>
            <div class="flex items-center gap-2">
              <Landmark class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold text-ink">Finance operations</h2>
            </div>
            <p class="mt-1 text-sm text-graphite">
              Refunds, disputes, class funding, payment milestones, and tip records that need operational visibility.
            </p>
          </div>

          <div class="inline-flex max-w-full overflow-x-auto rounded-md border border-slate-200 bg-slate-50 p-1">
            <button
              v-for="option in opsFilterOptions"
              :key="option.key"
              class="focus-ring min-h-9 whitespace-nowrap rounded px-3 text-xs font-semibold"
              :class="finance.opsFilter === option.key ? 'bg-white text-ink shadow-sm' : 'text-graphite'"
              type="button"
              @click="finance.opsFilter = option.key"
            >
              {{ option.label }}
            </button>
          </div>
        </div>

        <div v-if="finance.financeOpsItems.length" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50 text-left text-xs font-semibold uppercase text-graphite">
              <tr>
                <th class="px-3 py-2">Work item</th>
                <th class="px-3 py-2">Source</th>
                <th class="px-3 py-2">Website</th>
                <th class="px-3 py-2">Amount</th>
                <th class="px-3 py-2">Status</th>
                <th class="px-3 py-2">Updated</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="item in finance.financeOpsItems" :key="`${item.source}-${item.id}`">
                <td class="px-3 py-2.5">
                  <div class="flex items-start gap-3">
                    <span class="mt-0.5 inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-slate-100 text-signal">
                      <AlertTriangle v-if="item.source === 'refund'" class="h-4 w-4" />
                      <Scale v-else-if="item.source === 'dispute'" class="h-4 w-4" />
                      <CircleDollarSign v-else class="h-4 w-4" />
                    </span>
                    <span>
                      <span class="block font-semibold text-ink">{{ item.title }}</span>
                      <span class="mt-1 block text-xs text-graphite">{{ item.subtitle }}</span>
                    </span>
                  </div>
                </td>
                <td class="px-3 py-2.5 capitalize text-graphite">{{ sourceLabel(item.source) }}</td>
                <td class="px-3 py-2.5">
                  <span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
                    {{ websitesStore.nameById(item.meta?.website as number | undefined ?? item.meta?.website_id as number | undefined) }}
                  </span>
                </td>
                <td class="px-3 py-2.5 font-semibold text-ink">{{ item.amount === undefined ? "Not set" : formatAmount(item.amount) }}</td>
                <td class="px-3 py-2.5">
                  <StatusPill :label="item.status" :tone="statusTone(item.status)" />
                </td>
                <td class="px-3 py-2.5 text-graphite">{{ formatDate(item.date) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="p-4">
          <EmptyState
            :icon="Landmark"
            title="No finance operations"
            message="Refund, dispute, class funding, and tip records will appear here when the backend returns them."
          />
        </div>
      </div>

      <section class="rounded-lg border border-slate-200 bg-white p-4">
        <div class="flex items-center gap-2">
          <CircleDollarSign class="h-5 w-5 text-signal" />
          <h2 class="text-base font-semibold text-ink">Financial controls</h2>
        </div>
        <p class="mt-1 text-sm text-graphite">
          Apply controlled actions to refund and dispute records while leaving class funding and tip items reviewable.
        </p>
        <div class="mt-4 grid gap-3 lg:grid-cols-[minmax(0,1fr)_220px_160px]">
          <label class="block text-sm font-medium text-ink">
            Work item
            <select
              v-model="financeControl.itemKey"
              class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
            >
              <option
                v-for="item in finance.financeOpsItems"
                :key="`${item.source}:${item.id}`"
                :value="`${item.source}:${item.id}`"
              >
                {{ sourceLabel(item.source) }} · {{ item.title }}
              </option>
            </select>
          </label>
          <label class="block text-sm font-medium text-ink">
            Action
            <select
              v-model="financeControl.action"
              class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
            >
              <option v-for="action in financeActions" :key="action.key" :value="action.key">
                {{ action.label }}
              </option>
            </select>
          </label>
          <button
            class="focus-ring self-end rounded-md bg-ink px-4 py-3 text-sm font-semibold text-white disabled:opacity-60"
            type="button"
            :disabled="finance.isMutating || !selectedFinanceItem || financeControl.note.length < 10"
            @click="selectedFinanceItem && finance.applyFinanceControl(selectedFinanceItem, financeControl.action, financeControl.note).catch(() => undefined)"
          >
            Apply
          </button>
        </div>
        <label class="mt-3 block text-sm font-medium text-ink">
          Audit note
          <textarea
            v-model.trim="financeControl.note"
            class="focus-ring mt-1 min-h-20 w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm"
          />
        </label>
      </section>
    </section>

    <section class="grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(380px,0.85fr)]">
      <div class="rounded-xl border border-slate-200 bg-white">
        <!-- Header -->
        <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
          <div class="flex items-center gap-2">
            <CreditCard class="h-5 w-5 text-signal" />
            <div>
              <h2 class="text-base font-semibold text-ink">Payment activity</h2>
              <p class="text-xs text-graphite">Client inflows, writer payouts, and refunds.</p>
            </div>
          </div>
        </div>
        <!-- Filters row -->
        <div class="flex flex-wrap items-center gap-3 border-b border-slate-100 bg-slate-50 px-5 py-3">
          <div class="flex flex-wrap gap-1">
            <button
              v-for="option in filterOptions"
              :key="option.key"
              class="focus-ring h-8 rounded-lg px-3 text-xs font-semibold transition-colors"
              :class="finance.filter === option.key
                ? 'bg-ink text-white shadow-sm'
                : 'bg-white border border-slate-200 text-graphite hover:border-slate-300 hover:text-ink'"
              type="button"
              @click="finance.filter = option.key"
            >
              {{ option.label }}
            </button>
          </div>
          <select v-model="activityWebsite" class="focus-ring h-8 rounded-lg border border-slate-200 bg-white px-2 text-xs">
            <option value="">All websites</option>
            <option v-for="ws in websitesStore.list" :key="ws.id" :value="ws.id">{{ ws.name || ws.domain }}</option>
          </select>
          <label class="relative ml-auto block w-52">
            <Search class="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
            <input
              v-model="finance.query"
              class="focus-ring h-8 w-full rounded-lg border border-slate-200 bg-white pl-8 pr-3 text-xs"
              type="search"
              placeholder="Search payments…"
            />
          </label>
        </div>

        <div v-if="websiteFilteredFeed.length" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50 text-left text-xs font-semibold uppercase text-graphite">
              <tr>
                <th class="px-3 py-2">Record</th>
                <th class="px-3 py-2">Type</th>
                <th class="px-3 py-2">Website</th>
                <th class="px-3 py-2">Amount</th>
                <th class="px-3 py-2">Status</th>
                <th class="px-3 py-2">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="item in websiteFilteredFeed" :key="item.id">
                <td class="px-3 py-2.5">
                  <p class="font-semibold text-ink">{{ item.title }}</p>
                  <p class="mt-1 text-xs text-graphite">{{ item.subtitle }}</p>
                </td>
                <td class="px-3 py-2.5 capitalize text-graphite">{{ item.source }}</td>
                <td class="px-3 py-2.5">
                  <span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
                    {{ websitesStore.nameById(item.website_id) }}
                  </span>
                </td>
                <td class="px-3 py-2.5 font-semibold text-ink">{{ formatAmount(item.amount) }}</td>
                <td class="px-3 py-2.5">
                  <StatusPill :label="item.status" :tone="statusTone(item.status)" />
                </td>
                <td class="px-3 py-2.5 text-graphite">{{ formatDate(item.date) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="p-4">
          <EmptyState
            :icon="CreditCard"
            title="No payment records"
            message="Payment records will appear here once wallet, refund, and payout endpoints respond."
          />
        </div>
      </div>

      <aside class="space-y-4">
        <section class="rounded-lg border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2">
            <TrendingUp class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold text-ink">Revenue breakdown</h2>
          </div>
          <div class="mt-4 space-y-3">
            <div class="flex items-center justify-between text-sm">
              <span class="text-graphite">Orders</span>
              <span class="font-semibold text-ink">{{ formatAmount(finance.financialOverview.summary?.revenue_breakdown?.orders) }}</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-graphite">Special orders</span>
              <span class="font-semibold text-ink">{{ formatAmount(finance.financialOverview.summary?.revenue_breakdown?.special_orders) }}</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-graphite">Classes</span>
              <span class="font-semibold text-ink">{{ formatAmount(finance.financialOverview.summary?.revenue_breakdown?.classes) }}</span>
            </div>
            <div class="flex items-center justify-between border-t border-slate-200 pt-3 text-sm">
              <span class="font-semibold text-ink">Net revenue</span>
              <span class="font-semibold text-ink">{{ formatAmount(finance.financialOverview.summary?.net_revenue) }}</span>
            </div>
          </div>
        </section>

        <section class="rounded-lg border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2">
            <WalletCards class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold text-ink">Writer payout ops</h2>
          </div>
          <div v-if="finance.payouts.length" class="mt-4 space-y-4">
            <article
              v-for="payout in finance.payouts"
              :key="payout.id"
              class="rounded-md border border-slate-200 p-3"
            >
              <div class="flex items-start justify-between gap-3">
                <div>
                  <p class="font-semibold text-ink">{{ payout.writer_email || `Writer #${payout.writer_id}` }}</p>
                  <p class="mt-1 text-sm text-graphite">{{ payout.reason || payout.reference || "Payout request" }}</p>
                  <span v-if="payout.website_id" class="mt-1 inline-block rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
                    {{ websitesStore.nameById(payout.website_id) }}
                  </span>
                </div>
                <p class="font-semibold text-ink">{{ formatAmount(payout.amount) }}</p>
              </div>
              <div class="mt-3 flex flex-wrap items-center gap-2">
                <StatusPill :label="payout.workflow_status || payout.status" :tone="statusTone(payout.workflow_status || payout.status)" />
                <span class="text-xs text-graphite">{{ formatDate(payout.created_at) }}</span>
              </div>
              <div class="mt-4 grid gap-2 sm:grid-cols-3">
                <button
                  class="focus-ring inline-flex h-9 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold disabled:opacity-60"
                  type="button"
                  :disabled="finance.isMutating"
                  @click="finance.approvePayout(payout.id).catch(() => undefined)"
                >
                  <CheckCircle2 class="h-4 w-4" />
                  Approve
                </button>
                <button
                  class="focus-ring inline-flex h-9 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold disabled:opacity-60"
                  type="button"
                  :disabled="finance.isMutating"
                  @click="finance.processPayout(payout.id).catch(() => undefined)"
                >
                  <Send class="h-4 w-4" />
                  Process
                </button>
                <button
                  class="focus-ring inline-flex h-9 items-center justify-center gap-2 rounded-md border border-rose-200 bg-white px-3 text-xs font-semibold text-rose-700 disabled:opacity-60"
                  type="button"
                  :disabled="finance.isMutating"
                  @click="finance.rejectPayout(payout.id).catch(() => undefined)"
                >
                  <XCircle class="h-4 w-4" />
                  Reject
                </button>
              </div>
            </article>
          </div>
          <EmptyState
            v-else
            :icon="WalletCards"
            title="No payout requests"
            message="Writer payout requests will appear here."
          />
        </section>
      </aside>
    </section>

    <section class="grid gap-6 xl:grid-cols-[1fr_1fr]">
      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <h2 class="text-lg font-semibold text-ink">Monthly finance trend</h2>
        <AppChart
          v-if="revenueRows.length"
          :option="revenueTrendOption"
          height="280px"
          class="mt-4"
        />
        <div v-else class="mt-4 overflow-hidden rounded-md border border-slate-200">
          <div class="grid grid-cols-[1fr_auto_auto_auto] gap-3 bg-slate-50 px-4 py-3 text-xs font-semibold uppercase text-graphite">
            <span>Period</span><span>Revenue</span><span>Expenses</span><span class="text-right">Net</span>
          </div>
          <div
            v-for="row in revenueRows"
            :key="row.period || row.month"
            class="grid grid-cols-[1fr_auto_auto_auto] gap-3 border-t border-slate-100 px-4 py-3 text-sm"
          >
            <span class="font-semibold text-ink">{{ row.month || row.period }}</span>
            <span class="text-graphite">{{ formatAmount(row.revenue?.total) }}</span>
            <span class="text-graphite">{{ formatAmount(row.expenses?.total) }}</span>
            <span class="text-right font-semibold text-ink">{{ formatAmount(row.net_revenue) }}</span>
          </div>
        </div>
      </div>

      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <h2 class="text-lg font-semibold text-ink">Writer payment history</h2>
          <div class="inline-flex rounded-md border border-slate-200 bg-slate-50 p-1">
            <button
              v-for="opt in [{ key: 'all', label: 'All' }, { key: 'BIWEEKLY', label: 'Bi-weekly' }, { key: 'MONTHLY', label: 'Monthly' }]"
              :key="opt.key"
              class="focus-ring min-h-8 rounded px-3 text-xs font-semibold"
              :class="finance.cycleFilter === opt.key ? 'bg-white text-ink shadow-sm' : 'text-graphite'"
              type="button"
              @click="finance.cycleFilter = opt.key as 'all' | 'BIWEEKLY' | 'MONTHLY'"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>

        <!-- Cycle summary tiles -->
        <div v-if="finance.cycleBreakdown.length" class="mt-4 grid gap-3 sm:grid-cols-3">
          <div
            v-for="row in finance.cycleBreakdown"
            :key="row.cycle"
            class="rounded-md border border-slate-200 bg-slate-50 p-3 text-center"
          >
            <p class="text-xs font-semibold uppercase tracking-wide text-graphite">{{ row.cycle === "BIWEEKLY" ? "Bi-weekly" : row.cycle === "MONTHLY" ? "Monthly" : row.cycle }}</p>
            <p class="mt-1 text-lg font-semibold text-ink">{{ formatAmount(row.writerTotal) }}</p>
            <p class="text-xs text-graphite">{{ row.count }} payout(s) · {{ formatAmount(row.margin) }} margin</p>
          </div>
        </div>

        <div class="mt-4 space-y-3">
          <article
            v-for="payment in finance.filteredWriterPayments"
            :key="payment.id || `${payment.writer_email}-${payment.paid_at}`"
            class="rounded-md border border-slate-200 p-4"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <div class="flex items-center gap-2">
                  <p class="font-semibold text-ink">
                    {{ payment.writer?.name || payment.writer_email || payment.writer_username || `Writer #${payment.writer_id}` }}
                  </p>
                  <span
                    v-if="payment.type"
                    class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold"
                    :class="payment.type === 'BIWEEKLY' ? 'bg-sky-100 text-sky-700' : payment.type === 'MONTHLY' ? 'bg-violet-100 text-violet-700' : 'bg-slate-100 text-graphite'"
                  >
                    {{ payment.type === "BIWEEKLY" ? "Bi-weekly" : payment.type === "MONTHLY" ? "Monthly" : payment.type }}
                  </span>
                </div>
                <p class="mt-1 text-sm text-graphite">
                  {{ payment.website || websitesStore.nameById(payment.website_id) }}
                  · {{ payment.number_of_orders ?? payment.order_count ?? 0 }} order(s)
                  <span v-if="Number(payment.tips) > 0"> · {{ formatAmount(payment.tips) }} tips</span>
                  <span v-if="Number(payment.fines) > 0"> · {{ formatAmount(payment.fines) }} fines</span>
                </p>
              </div>
              <div class="text-right">
                <p class="font-semibold text-ink">{{ formatAmount(payment.total_earnings ?? payment.total_amount ?? payment.amount) }}</p>
                <StatusPill :label="payment.status || 'paid'" :tone="statusTone(payment.status || 'paid')" />
              </div>
            </div>
            <p class="mt-2 text-xs text-graphite">
              Client {{ formatAmount(payment.client_total) }} · Margin {{ formatAmount(payment.platform_margin) }} · {{ formatDate(payment.date ?? payment.paid_at) }}
            </p>
          </article>
          <EmptyState
            v-if="!finance.filteredWriterPayments.length"
            :icon="WalletCards"
            title="No writer payments"
            message="Historical writer payment records will appear here."
          />
        </div>
      </div>
    </section>

    <!-- Revenue by website (cross-tenant) -->
    <section v-if="websiteChart || chartsLoading" class="rounded-xl border border-slate-200 bg-white p-5">
      <h2 class="text-base font-semibold text-ink">Revenue by website — last 12 months</h2>
      <AppChart
        v-if="websiteChart"
        :option="websiteChartOption"
        :loading="chartsLoading"
        height="320px"
        class="mt-4"
      />
      <div v-else-if="chartsLoading" class="mt-4 h-72 animate-pulse rounded-lg bg-slate-100" />
    </section>

  </div>
</template>

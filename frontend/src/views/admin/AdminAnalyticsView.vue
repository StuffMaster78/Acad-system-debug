<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { BarChart3, Download, RefreshCw, ShieldAlert, TrendingUp, Users } from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import AppChart from "@/components/ui/AppChart.vue";
import { useAdminAnalyticsStore } from "@/stores/adminAnalytics";
import { analyticsChartsApi, type ChartData } from "@/api/analyticsCharts";
import type { EChartsOption } from "echarts";

const analytics = useAdminAnalyticsStore();

function money(value: number | string | undefined | null) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(Number(value ?? 0));
}

function percent(value: number | string | undefined | null) {
  return `${Number(value ?? 0).toFixed(1)}%`;
}

function numberLabel(value: number | string | undefined | null) {
  return new Intl.NumberFormat("en-US").format(Number(value ?? 0));
}

const revenueBarMax = computed(() => {
  const vals = analytics.clients.map((c) => Number(c.total_spend ?? 0));
  return Math.max(...vals, 1);
});

const writerEarningsMax = computed(() => {
  const vals = analytics.writers.map((w) => Number(w.total_earnings ?? 0));
  return Math.max(...vals, 1);
});

function barWidth(value: number | string | undefined | null, max: number) {
  const n = Number(value ?? 0);
  return `${Math.max((n / max) * 100, 2).toFixed(1)}%`;
}

function exportCSV() {
  const rows = [
    ["Client", "Period start", "Period end", "Total spend", "Orders", "On-time %", "Revision %", "Avg writer rating"],
    ...analytics.clients.map((c) => [
      c.client_name ?? c.client_email ?? String(c.client ?? ""),
      c.period_start,
      c.period_end,
      Number(c.total_spend ?? 0).toFixed(2),
      String(c.total_orders ?? 0),
      Number(c.on_time_delivery_rate ?? 0).toFixed(1),
      Number(c.revision_rate ?? 0).toFixed(1),
      Number(c.average_writer_rating ?? 0).toFixed(1),
    ]),
  ];
  const csv = rows.map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(",")).join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `client-analytics-${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

// ── Charts ───────────────────────────────────────────────────────────────────

const revenueChart = ref<ChartData | null>(null);
const ordersChart = ref<ChartData | null>(null);
const clientsChart = ref<ChartData | null>(null);
const chartsLoading = ref(false);

function buildRevenueOption(d: ChartData): EChartsOption {
  return {
    tooltip: { trigger: "axis" },
    legend: { data: d.series.map((s) => s.name), bottom: 0 },
    grid: { left: 60, right: 60, top: 20, bottom: 40 },
    xAxis: { type: "category", data: d.labels, axisLabel: { rotate: 30, fontSize: 10 } },
    yAxis: [
      { type: "value", name: "$", axisLabel: { formatter: (v: number) => `$${(v / 1000).toFixed(0)}k` } },
      { type: "value", name: "Orders", splitLine: { show: false } },
    ],
    series: d.series.map((s) => ({
      name: s.name,
      type: s.type,
      data: s.data,
      yAxisIndex: s.yAxisIndex ?? 0,
      smooth: true,
      itemStyle: s.type === "bar" ? { color: "#e2e8f0" } : { color: "#7c3aed" },
      lineStyle: { color: "#7c3aed", width: 2 },
      areaStyle: s.type === "line" ? { color: "rgba(124,58,237,0.08)" } : undefined,
    })),
  };
}

function buildOrdersOption(d: ChartData): EChartsOption {
  const palette = ["#94a3b8","#3b82f6","#f59e0b","#10b981","#6366f1","#ef4444"];
  return {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { data: d.series.map((s) => s.name), bottom: 0, type: "scroll" },
    grid: { left: 50, right: 20, top: 20, bottom: 50 },
    xAxis: { type: "category", data: d.labels, axisLabel: { rotate: 30, fontSize: 10 } },
    yAxis: { type: "value" },
    series: d.series.map((s, i) => ({
      name: s.name,
      type: "bar",
      stack: "orders",
      data: s.data,
      itemStyle: { color: palette[i % palette.length] },
    })),
  };
}

function buildClientsOption(d: ChartData): EChartsOption {
  return {
    tooltip: { trigger: "axis" },
    legend: { data: d.series.map((s) => s.name), bottom: 0 },
    grid: { left: 50, right: 20, top: 20, bottom: 40 },
    xAxis: { type: "category", data: d.labels, axisLabel: { rotate: 30, fontSize: 10 } },
    yAxis: { type: "value" },
    series: d.series.map((s, i) => ({
      name: s.name,
      type: s.type,
      data: s.data,
      smooth: true,
      itemStyle: { color: i === 0 ? "#0ea5e9" : "#7c3aed" },
      lineStyle: { color: "#7c3aed", width: 2 },
      areaStyle: s.type === "line" ? { color: "rgba(124,58,237,0.06)" } : undefined,
    })),
  };
}

async function loadCharts() {
  chartsLoading.value = true;
  try {
    const [rev, ord, cli] = await Promise.all([
      analyticsChartsApi.revenue({ months: 12 }),
      analyticsChartsApi.orders({ months: 12 }),
      analyticsChartsApi.clients({ months: 12 }),
    ]);
    revenueChart.value = rev.data;
    ordersChart.value = ord.data;
    clientsChart.value = cli.data;
  } catch { /* non-fatal */ }
  finally { chartsLoading.value = false; }
}

function changeLabel(pct: number | null | undefined): string {
  if (pct == null) return "—";
  const sign = pct >= 0 ? "+" : "";
  return `${sign}${pct.toFixed(1)}%`;
}
function changeTone(pct: number | null | undefined): string {
  if (pct == null) return "text-graphite";
  return pct >= 0 ? "text-emerald-600" : "text-rose-600";
}

onMounted(() => {
  analytics.hydrate().catch(() => undefined);
  loadCharts();
});
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Admin</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Analytics</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          Operational signals across clients, writers, and class cohorts.
        </p>
      </div>
      <div class="flex flex-wrap gap-2">
        <button
          class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-300 px-4 text-sm font-semibold text-ink disabled:cursor-not-allowed disabled:opacity-60"
          type="button"
          :disabled="analytics.isLoading"
          @click="analytics.hydrate()"
        >
          <RefreshCw class="h-4 w-4" />
          Refresh
        </button>
        <button
          class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-300 px-4 text-sm font-semibold text-ink"
          type="button"
          :disabled="!analytics.clients.length"
          @click="exportCSV"
        >
          <Download class="h-4 w-4" />
          Export CSV
        </button>
        <button
          class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md bg-ink px-4 text-sm font-semibold text-white"
          type="button"
          @click="analytics.markReviewed()"
        >
          Review
        </button>
      </div>
    </section>

    <div v-if="analytics.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ analytics.error }}
    </div>
    <div v-if="analytics.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ analytics.notice }}
    </div>

    <!-- ── Trend charts ────────────────────────────────────────────────────── -->
    <section class="grid gap-6 xl:grid-cols-3">

      <!-- Revenue trend -->
      <div class="rounded-xl border border-slate-200 bg-white p-5 col-span-2">
        <div class="mb-4 flex items-center justify-between">
          <div>
            <h2 class="text-base font-semibold text-ink">Revenue trend</h2>
            <p
              v-if="revenueChart?.summary?.change_pct != null"
              class="mt-0.5 text-xs"
              :class="changeTone(revenueChart.summary.change_pct)"
            >
              {{ revenueChart.summary.current?.label }}
              &nbsp;{{ changeLabel(revenueChart.summary.change_pct) }} vs {{ revenueChart.summary.previous?.label }}
            </p>
          </div>
          <TrendingUp class="size-4 text-graphite" />
        </div>
        <AppChart
          v-if="revenueChart"
          :option="buildRevenueOption(revenueChart)"
          :loading="chartsLoading"
          height="260px"
        />
        <div v-else-if="chartsLoading" class="h-64 animate-pulse rounded-lg bg-slate-100" />
      </div>

      <!-- Client growth -->
      <div class="rounded-xl border border-slate-200 bg-white p-5">
        <div class="mb-4 flex items-center justify-between">
          <div>
            <h2 class="text-base font-semibold text-ink">Client growth</h2>
            <p
              v-if="clientsChart?.summary?.change_pct != null"
              class="mt-0.5 text-xs"
              :class="changeTone(clientsChart.summary.change_pct)"
            >
              New this month {{ changeLabel(clientsChart.summary.change_pct) }}
            </p>
          </div>
          <Users class="size-4 text-graphite" />
        </div>
        <AppChart
          v-if="clientsChart"
          :option="buildClientsOption(clientsChart)"
          :loading="chartsLoading"
          height="260px"
        />
        <div v-else-if="chartsLoading" class="h-64 animate-pulse rounded-lg bg-slate-100" />
      </div>

    </section>

    <!-- Orders by status stacked bar -->
    <section class="rounded-xl border border-slate-200 bg-white p-5">
      <div class="mb-4 flex items-center justify-between">
        <div>
          <h2 class="text-base font-semibold text-ink">Orders by status</h2>
          <p
            v-if="ordersChart?.summary?.change_pct != null"
            class="mt-0.5 text-xs"
            :class="changeTone(ordersChart.summary.change_pct)"
          >
            {{ ordersChart.summary.current?.label }} — {{ ordersChart.summary.current?.value.toLocaleString() }} orders
            &nbsp;{{ changeLabel(ordersChart.summary.change_pct) }}
          </p>
        </div>
        <BarChart3 class="size-4 text-graphite" />
      </div>
      <AppChart
        v-if="ordersChart"
        :option="buildOrdersOption(ordersChart)"
        :loading="chartsLoading"
        height="280px"
      />
      <div v-else-if="chartsLoading" class="h-64 animate-pulse rounded-lg bg-slate-100" />
    </section>

    <section class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <div class="rounded-md border border-slate-200 bg-white p-4">
        <p class="text-sm font-medium text-graphite">Revenue observed</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ money(analytics.totalRevenue) }}</p>
        <p class="mt-2 text-sm text-graphite">From client analytics</p>
      </div>
      <div class="rounded-md border border-slate-200 bg-white p-4">
        <p class="text-sm font-medium text-graphite">Orders observed</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ numberLabel(analytics.totalOrders) }}</p>
        <p class="mt-2 text-sm text-graphite">Across sampled clients</p>
      </div>
      <div class="rounded-md border border-emerald-200 bg-emerald-50 p-4">
        <p class="text-sm font-medium text-emerald-900">On-time delivery</p>
        <p class="mt-3 text-3xl font-semibold text-emerald-950">{{ percent(analytics.averageOnTimeRate) }}</p>
        <p class="mt-2 text-sm text-emerald-900">Average client rate</p>
      </div>
      <div class="rounded-md border border-amber-200 bg-amber-50 p-4">
        <p class="text-sm font-medium text-amber-900">Writer risk</p>
        <p class="mt-3 text-3xl font-semibold text-amber-950">{{ analytics.riskWriters.length }}</p>
        <p class="mt-2 text-sm text-amber-900">Revision/rejection watchlist</p>
      </div>
    </section>

    <section class="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <div class="flex items-center justify-between gap-3">
          <div>
            <h2 class="text-lg font-semibold text-ink">Client performance</h2>
            <p class="mt-1 text-sm text-graphite">Spend, delivery, and revision behavior by client period.</p>
          </div>
          <BarChart3 class="h-5 w-5 text-signal" />
        </div>

        <div class="mt-5 overflow-hidden rounded-md border border-slate-200">
          <div class="grid grid-cols-[1fr_120px_100px_100px_100px] gap-3 bg-slate-50 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
            <span>Client</span>
            <span>Spend</span>
            <span>Orders</span>
            <span>On-time</span>
            <span>Revision</span>
          </div>
          <div v-if="analytics.isLoading" class="px-4 py-6 text-sm text-graphite">Loading analytics...</div>
          <div v-else-if="!analytics.clients.length" class="px-4 py-6 text-sm text-graphite">No client analytics loaded.</div>
          <div
            v-for="client in analytics.clients"
            v-else
            :key="client.id"
            class="grid grid-cols-[1fr_120px_100px_100px_100px] items-center gap-3 border-t border-slate-100 px-4 py-3 text-sm"
          >
            <div>
              <p class="font-semibold text-ink">{{ client.client_name || client.client_email || `Client #${client.client}` }}</p>
              <p class="mt-1 text-xs text-graphite">{{ client.period_start }} to {{ client.period_end }}</p>
            </div>
            <span class="font-semibold text-ink">{{ money(client.total_spend) }}</span>
            <span class="text-graphite">{{ numberLabel(client.total_orders) }}</span>
            <span class="text-graphite">{{ percent(client.on_time_delivery_rate) }}</span>
            <span class="text-graphite">{{ percent(client.revision_rate) }}</span>
          </div>
        </div>
      </div>

      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <div class="flex items-center justify-between gap-3">
          <div>
            <h2 class="text-lg font-semibold text-ink">Writer quality</h2>
            <p class="mt-1 text-sm text-graphite">Quality score, approvals, revisions, and earnings signals.</p>
          </div>
          <ShieldAlert class="h-5 w-5 text-saffron" />
        </div>

        <div class="mt-5 space-y-3">
          <p v-if="!analytics.writers.length" class="text-sm text-graphite">No writer analytics loaded.</p>
          <article
            v-for="writer in analytics.writers"
            :key="writer.id"
            class="rounded-md border border-slate-200 p-4"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="text-sm font-semibold text-ink">{{ writer.writer_name || writer.writer_email || `Writer #${writer.writer}` }}</p>
                <p class="mt-1 text-xs text-graphite">{{ money(writer.total_earnings) }} earned · {{ numberLabel(writer.total_orders_completed) }} completed</p>
              </div>
              <StatusPill
                :label="`Q ${numberLabel(writer.quality_score)}`"
                :tone="Number(writer.quality_score) >= 85 ? 'success' : 'warning'"
              />
            </div>
            <div class="mt-4 grid grid-cols-3 gap-3 text-sm">
              <div>
                <p class="text-xs text-graphite">Approval</p>
                <p class="font-semibold text-ink">{{ percent(writer.approval_rate) }}</p>
              </div>
              <div>
                <p class="text-xs text-graphite">Revision</p>
                <p class="font-semibold text-ink">{{ percent(writer.revision_rate) }}</p>
              </div>
              <div>
                <p class="text-xs text-graphite">Hourly</p>
                <p class="font-semibold text-ink">{{ money(writer.effective_hourly_rate) }}</p>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- Revenue trend bars -->
    <section class="grid gap-6 xl:grid-cols-2">
      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <div class="flex items-center gap-2 mb-4">
          <TrendingUp class="h-5 w-5 text-signal" />
          <h2 class="text-lg font-semibold text-ink">Revenue by client</h2>
        </div>
        <div v-if="!analytics.clients.length" class="text-sm text-graphite py-6 text-center">No client data loaded.</div>
        <div v-else class="space-y-3">
          <div
            v-for="client in analytics.clients"
            :key="client.id"
            class="space-y-1"
          >
            <div class="flex justify-between text-xs">
              <span class="font-medium text-ink truncate max-w-[60%]">{{ client.client_name ?? client.client_email ?? `Client #${client.client}` }}</span>
              <span class="text-graphite shrink-0">{{ money(client.total_spend) }}</span>
            </div>
            <div class="h-2 rounded-full bg-slate-100">
              <div
                class="h-2 rounded-full bg-signal transition-all"
                :style="{ width: barWidth(client.total_spend, revenueBarMax) }"
              />
            </div>
            <p class="text-xs text-graphite">{{ client.total_orders }} orders · {{ percent(client.on_time_delivery_rate) }} on-time</p>
          </div>
        </div>
      </div>

      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <div class="flex items-center gap-2 mb-4">
          <BarChart3 class="h-5 w-5 text-signal" />
          <h2 class="text-lg font-semibold text-ink">Earnings by writer</h2>
        </div>
        <div v-if="!analytics.writers.length" class="text-sm text-graphite py-6 text-center">No writer data loaded.</div>
        <div v-else class="space-y-3">
          <div
            v-for="writer in analytics.writers"
            :key="writer.id"
            class="space-y-1"
          >
            <div class="flex justify-between text-xs">
              <span class="font-medium text-ink truncate max-w-[60%]">{{ writer.writer_name ?? writer.writer_email ?? `Writer #${writer.writer}` }}</span>
              <span class="text-graphite shrink-0">{{ money(writer.total_earnings) }}</span>
            </div>
            <div class="h-2 rounded-full bg-slate-100">
              <div
                class="h-2 rounded-full transition-all"
                :class="Number(writer.quality_score) >= 85 ? 'bg-emerald-500' : 'bg-amber-400'"
                :style="{ width: barWidth(writer.total_earnings, writerEarningsMax) }"
              />
            </div>
            <p class="text-xs text-graphite">Quality {{ writer.quality_score }} · {{ writer.total_orders_completed }} completed</p>
          </div>
        </div>
      </div>
    </section>

    <section class="rounded-lg border border-slate-200 bg-white p-5">
      <div class="flex items-center gap-2">
        <Users class="h-5 w-5 text-signal" />
        <h2 class="text-lg font-semibold text-ink">Class cohorts</h2>
      </div>
      <div class="mt-5 grid gap-4 lg:grid-cols-2">
        <article
          v-for="cohort in analytics.classes"
          :key="cohort.id"
          class="rounded-md border border-slate-200 p-4"
        >
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-sm font-semibold text-ink">{{ cohort.class_name }}</p>
              <p class="mt-1 text-xs text-graphite">{{ cohort.class_id || "No class id" }} · {{ cohort.reports_count ?? 0 }} reports</p>
            </div>
            <StatusPill :label="`${percent(cohort.completion_rate)} complete`" />
          </div>
          <div class="mt-4 grid grid-cols-4 gap-3 text-sm">
            <div>
              <p class="text-xs text-graphite">Students</p>
              <p class="font-semibold text-ink">{{ cohort.active_students }}/{{ cohort.total_students }}</p>
            </div>
            <div>
              <p class="text-xs text-graphite">Orders</p>
              <p class="font-semibold text-ink">{{ cohort.completed_orders }}/{{ cohort.total_orders }}</p>
            </div>
            <div>
              <p class="text-xs text-graphite">On-time</p>
              <p class="font-semibold text-ink">{{ percent(cohort.on_time_submission_rate) }}</p>
            </div>
            <div>
              <p class="text-xs text-graphite">Grade</p>
              <p class="font-semibold text-ink">{{ numberLabel(cohort.average_grade) }}</p>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

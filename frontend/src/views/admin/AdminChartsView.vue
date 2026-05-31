<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { BarChart3, TrendingUp, Users, Globe, RefreshCw } from "@lucide/vue";
import AppChart from "@/components/ui/AppChart.vue";
import { analyticsChartsApi, type ChartData } from "@/api/analyticsCharts";
import { useAuthStore } from "@/stores/auth";
import type { EChartsOption } from "echarts";

const auth = useAuthStore();
const isSuperAdmin = computed(() => auth.role === "superadmin");

const revenue   = ref<ChartData | null>(null);
const orders    = ref<ChartData | null>(null);
const clients   = ref<ChartData | null>(null);
const byWebsite = ref<ChartData | null>(null);
const loading   = ref(false);
const period    = ref<"month" | "quarter">("month");
const months    = ref(12);

// ── ECharts options ───────────────────────────────────────────────────────────

function revenueOption(d: ChartData): EChartsOption {
  return {
    tooltip: { trigger: "axis" },
    legend: { data: d.series.map((s) => s.name), bottom: 0 },
    grid: { left: 64, right: 56, top: 16, bottom: 44 },
    xAxis: { type: "category", data: d.labels, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: [
      { type: "value", axisLabel: { formatter: (v: number) => `$${(v / 1000).toFixed(0)}k` } },
      { type: "value", splitLine: { show: false } },
    ],
    series: d.series.map((s) => ({
      name: s.name, type: s.type, data: s.data,
      yAxisIndex: s.yAxisIndex ?? 0, smooth: true,
      itemStyle: { color: s.type === "bar" ? "#cbd5e1" : "#7c3aed" },
      lineStyle: { color: "#7c3aed", width: 2 },
      areaStyle: s.type === "line" ? { color: "rgba(124,58,237,0.08)" } : undefined,
    })),
  };
}

function ordersOption(d: ChartData): EChartsOption {
  const palette = ["#94a3b8", "#3b82f6", "#f59e0b", "#10b981", "#6366f1", "#ef4444"];
  return {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    legend: { data: d.series.map((s) => s.name), bottom: 0, type: "scroll" },
    grid: { left: 48, right: 16, top: 16, bottom: 52 },
    xAxis: { type: "category", data: d.labels, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: "value" },
    series: d.series.map((s, i) => ({
      name: s.name, type: "bar", stack: "orders", data: s.data,
      itemStyle: { color: palette[i % palette.length] },
    })),
  };
}

function clientsOption(d: ChartData): EChartsOption {
  return {
    tooltip: { trigger: "axis" },
    legend: { data: d.series.map((s) => s.name), bottom: 0 },
    grid: { left: 48, right: 16, top: 16, bottom: 44 },
    xAxis: { type: "category", data: d.labels, axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: "value" },
    series: d.series.map((s, i) => ({
      name: s.name, type: s.type, data: s.data, smooth: true,
      itemStyle: { color: i === 0 ? "#0ea5e9" : "#7c3aed" },
      lineStyle: { color: "#7c3aed", width: 2 },
      areaStyle: s.type === "line" ? { color: "rgba(124,58,237,0.06)" } : undefined,
    })),
  };
}

function websiteOption(d: ChartData): EChartsOption {
  return {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    grid: { left: 140, right: 40, top: 16, bottom: 24 },
    xAxis: { type: "value", axisLabel: { formatter: (v: number) => `$${(v / 1000).toFixed(0)}k` } },
    yAxis: { type: "category", data: [...d.labels].reverse(), axisLabel: { fontSize: 11 } },
    series: [{ name: "Revenue", type: "bar", data: [...d.series[0].data].reverse(), itemStyle: { color: "#7c3aed" } }],
  };
}

// ── summary helper ────────────────────────────────────────────────────────────

function changeBadge(pct?: number | null) {
  if (pct == null) return null;
  return { label: `${pct >= 0 ? "+" : ""}${pct.toFixed(1)}%`, positive: pct >= 0 };
}

// ── data loading ──────────────────────────────────────────────────────────────

async function load() {
  loading.value = true;
  try {
    const params = { months: months.value, period: period.value };
    const calls: Promise<void>[] = [
      analyticsChartsApi.revenue(params).then((r) => { revenue.value = r.data; }),
      analyticsChartsApi.orders(params).then((r) => { orders.value = r.data; }),
      analyticsChartsApi.clients(params).then((r) => { clients.value = r.data; }),
    ];
    if (isSuperAdmin.value) {
      calls.push(
        analyticsChartsApi.revenueByWebsite({ months: months.value, top: 10 })
          .then((r) => { byWebsite.value = r.data; }),
      );
    }
    await Promise.all(calls);
  } catch { /* non-fatal */ }
  finally { loading.value = false; }
}

onMounted(load);
</script>

<template>
  <div class="space-y-6 p-6">

    <!-- Header + controls -->
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div>
        <h1 class="text-xl font-bold text-ink">Charts</h1>
        <p class="mt-0.5 text-sm text-graphite">Revenue, orders, and client growth over time</p>
      </div>
      <div class="flex items-center gap-2">
        <div class="flex rounded-lg border border-slate-200 overflow-hidden text-sm">
          <button
            v-for="p in [{ key: 'month', label: 'Monthly' }, { key: 'quarter', label: 'Quarterly' }]"
            :key="p.key"
            class="px-3 py-1.5 transition-colors"
            :class="period === p.key ? 'bg-ink text-white' : 'bg-white text-graphite hover:bg-slate-50'"
            @click="period = p.key as 'month' | 'quarter'; load()"
          >{{ p.label }}</button>
        </div>
        <select
          v-model="months"
          class="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm text-ink"
          @change="load()"
        >
          <option :value="6">6 months</option>
          <option :value="12">12 months</option>
          <option :value="24">24 months</option>
        </select>
        <button
          class="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm text-graphite hover:bg-slate-50"
          :disabled="loading"
          @click="load()"
        >
          <RefreshCw class="size-3.5" :class="{ 'animate-spin': loading }" />
        </button>
      </div>
    </div>

    <!-- Revenue + Clients -->
    <div class="grid gap-6 xl:grid-cols-[2fr_1fr]">

      <div class="rounded-xl border border-slate-200 bg-white p-5">
        <div class="flex items-center justify-between mb-1">
          <h2 class="text-sm font-semibold text-ink flex items-center gap-2">
            <TrendingUp class="size-4 text-berry" /> Revenue trend
          </h2>
          <template v-if="revenue?.summary?.change_pct != null">
            <span
              class="rounded-full px-2 py-0.5 text-xs font-semibold"
              :class="revenue.summary.change_pct >= 0 ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-600'"
            >
              {{ revenue.summary.change_pct >= 0 ? '+' : '' }}{{ revenue.summary.change_pct.toFixed(1) }}%
            </span>
          </template>
        </div>
        <p v-if="revenue?.summary?.current" class="text-xs text-graphite mb-3">
          {{ revenue.summary.current.label }}: ${{ revenue.summary.current.value.toLocaleString() }}
        </p>
        <AppChart v-if="revenue" :option="revenueOption(revenue)" :loading="loading" height="280px" />
        <div v-else-if="loading" class="h-72 animate-pulse rounded-lg bg-slate-100 mt-2" />
      </div>

      <div class="rounded-xl border border-slate-200 bg-white p-5">
        <div class="flex items-center justify-between mb-1">
          <h2 class="text-sm font-semibold text-ink flex items-center gap-2">
            <Users class="size-4 text-sky-500" /> Client growth
          </h2>
          <template v-if="clients?.summary?.change_pct != null">
            <span
              class="rounded-full px-2 py-0.5 text-xs font-semibold"
              :class="clients.summary.change_pct >= 0 ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-600'"
            >
              {{ clients.summary.change_pct >= 0 ? '+' : '' }}{{ clients.summary.change_pct.toFixed(1) }}%
            </span>
          </template>
        </div>
        <p v-if="clients?.summary?.current" class="text-xs text-graphite mb-3">
          {{ clients.summary.current.value }} new this {{ period }}
        </p>
        <AppChart v-if="clients" :option="clientsOption(clients)" :loading="loading" height="280px" />
        <div v-else-if="loading" class="h-72 animate-pulse rounded-lg bg-slate-100 mt-2" />
      </div>

    </div>

    <!-- Orders by status -->
    <div class="rounded-xl border border-slate-200 bg-white p-5">
      <div class="flex items-center justify-between mb-1">
        <h2 class="text-sm font-semibold text-ink flex items-center gap-2">
          <BarChart3 class="size-4 text-indigo-500" /> Orders by status
        </h2>
        <span v-if="orders?.summary?.current" class="text-xs text-graphite">
          {{ orders.summary.current.label }} — {{ orders.summary.current.value.toLocaleString() }} orders
        </span>
      </div>
      <AppChart v-if="orders" :option="ordersOption(orders)" :loading="loading" height="300px" class="mt-2" />
      <div v-else-if="loading" class="h-72 animate-pulse rounded-lg bg-slate-100 mt-2" />
    </div>

    <!-- Revenue by website (superadmin only) -->
    <div v-if="isSuperAdmin" class="rounded-xl border border-slate-200 bg-white p-5">
      <h2 class="text-sm font-semibold text-ink flex items-center gap-2 mb-4">
        <Globe class="size-4 text-violet-500" /> Revenue by website — top 10
      </h2>
      <AppChart v-if="byWebsite" :option="websiteOption(byWebsite)" :loading="loading" height="320px" />
      <div v-else-if="loading" class="h-72 animate-pulse rounded-lg bg-slate-100" />
    </div>

  </div>
</template>

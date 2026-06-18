<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { CheckCircle2, Clock, RefreshCw, Star, TrendingUp, XCircle } from "@lucide/vue";
import AppChart from "@/components/ui/AppChart.vue";
import { analyticsChartsApi, type ChartData } from "@/api/analyticsCharts";
import { api, apiPath } from "@/api/client";
import { useWriterWorkspaceStore } from "@/stores/writerWorkspace";
import type { EChartsOption } from "echarts";

const writerWs = useWriterWorkspaceStore();
const earnings = ref<ChartData | null>(null);
const loading = ref(false);
const months = ref(12);

interface WriterPerf {
  total_orders: number;
  completed_orders: number;
  late_deliveries: number;
  on_time_deliveries: number;
  average_rating: number | null;
  total_ratings: number;
  revision_count: number;
  cancelled_orders: number;
}
const perf = ref<WriterPerf | null>(null);

const earningsOption = computed<EChartsOption>(() => {
  const d = earnings.value;
  if (!d) return {};
  return {
    tooltip: { trigger: "axis", confine: true },
    legend: { data: d.series.map((s) => s.name), bottom: 8, type: "scroll" },
    grid: { left: 12, right: 12, top: 24, bottom: 60, containLabel: true },
    xAxis: { type: "category", data: d.labels, axisLabel: { rotate: 30, fontSize: 11, hideOverlap: true } },
    yAxis: [
      { type: "value", axisLabel: { formatter: (v: number) => `$${v.toFixed(0)}` } },
      { type: "value", splitLine: { show: false } },
    ],
    series: d.series.map((s, i) => ({
      name: s.name, type: s.type, data: s.data,
      yAxisIndex: s.yAxisIndex ?? 0, smooth: true,
      itemStyle: { color: i === 0 ? "#10b981" : "#94a3b8" },
      lineStyle: { color: "#94a3b8" },
    })),
  };
});

const onTimeRate = computed(() => {
  if (!perf.value || !perf.value.completed_orders) return null;
  return Math.round((perf.value.on_time_deliveries / perf.value.completed_orders) * 100);
});

const completionRate = computed(() => {
  if (!perf.value || !perf.value.total_orders) return null;
  return Math.round((perf.value.completed_orders / perf.value.total_orders) * 100);
});

const summaryStats = computed(() => [
  { label: "Completed orders", value: writerWs.summary?.completed_orders ?? "—" },
  { label: "Pending payout", value: writerWs.balance?.pending != null ? `$${Number(writerWs.balance.pending).toFixed(2)}` : "—" },
  { label: "Current window", value: writerWs.currentWindow?.net != null ? `$${Number(writerWs.currentWindow.net).toFixed(2)}` : "—" },
]);

async function load() {
  loading.value = true;
  try {
    const [earningsRes, perfRes] = await Promise.allSettled([
      analyticsChartsApi.writerEarnings({ months: months.value }),
      api.get<WriterPerf>(apiPath("/writer-management/me/performance/")),
    ]);
    if (earningsRes.status === "fulfilled") earnings.value = earningsRes.value.data;
    if (perfRes.status === "fulfilled") perf.value = perfRes.value.data;
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  if (!writerWs.summary) writerWs.hydrate().catch(() => undefined);
  load();
});
</script>

<template>
  <div class="space-y-6 p-6">

    <div class="flex flex-wrap items-center justify-between gap-4">
      <div>
        <h1 class="text-xl font-bold text-ink">Performance</h1>
        <p class="mt-0.5 text-sm text-graphite">Your earnings trend and delivery stats</p>
      </div>
      <div class="flex items-center gap-2">
        <select
          v-model="months"
          class="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm text-ink"
          @change="load()"
        >
          <option :value="6">6 months</option>
          <option :value="12">12 months</option>
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

    <!-- Earnings summary tiles -->
    <div class="grid grid-cols-3 gap-4">
      <div
        v-for="stat in summaryStats"
        :key="stat.label"
        class="rounded-xl border border-slate-200 bg-white p-4"
      >
        <p class="text-xs font-medium uppercase tracking-wide text-graphite">{{ stat.label }}</p>
        <p class="mt-1.5 text-2xl font-bold text-ink">{{ stat.value }}</p>
      </div>
    </div>

    <!-- Performance stat cards -->
    <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
      <!-- Rating -->
      <div class="rounded-xl border border-slate-200 bg-white p-4">
        <p class="text-xs font-medium uppercase tracking-wide text-graphite">Avg rating</p>
        <div class="mt-2 flex items-end gap-2">
          <p class="text-2xl font-bold text-ink">
            {{ perf?.average_rating != null ? perf.average_rating.toFixed(1) : "—" }}
          </p>
          <div v-if="perf?.average_rating != null" class="mb-0.5 flex gap-0.5">
            <Star
              v-for="n in 5"
              :key="n"
              class="h-3.5 w-3.5"
              :class="n <= Math.round(perf.average_rating) ? 'text-amber-400' : 'text-slate-200'"
              fill="currentColor"
            />
          </div>
        </div>
        <p class="mt-1 text-xs text-graphite">{{ perf?.total_ratings ?? 0 }} rating{{ perf?.total_ratings !== 1 ? 's' : '' }}</p>
      </div>

      <!-- On-time rate -->
      <div class="rounded-xl border border-slate-200 bg-white p-4">
        <p class="text-xs font-medium uppercase tracking-wide text-graphite">On-time rate</p>
        <div class="mt-2 flex items-center gap-2">
          <Clock class="h-5 w-5 shrink-0" :class="(onTimeRate ?? 0) >= 90 ? 'text-emerald-500' : (onTimeRate ?? 0) >= 70 ? 'text-amber-500' : 'text-red-400'" />
          <p class="text-2xl font-bold text-ink">
            {{ onTimeRate != null ? `${onTimeRate}%` : "—" }}
          </p>
        </div>
        <p class="mt-1 text-xs text-graphite">
          {{ perf?.on_time_deliveries ?? 0 }} / {{ perf?.completed_orders ?? 0 }} deliveries
        </p>
      </div>

      <!-- Completion rate -->
      <div class="rounded-xl border border-slate-200 bg-white p-4">
        <p class="text-xs font-medium uppercase tracking-wide text-graphite">Completion rate</p>
        <div class="mt-2 flex items-center gap-2">
          <CheckCircle2 class="h-5 w-5 shrink-0" :class="(completionRate ?? 0) >= 90 ? 'text-emerald-500' : (completionRate ?? 0) >= 70 ? 'text-amber-500' : 'text-red-400'" />
          <p class="text-2xl font-bold text-ink">
            {{ completionRate != null ? `${completionRate}%` : "—" }}
          </p>
        </div>
        <p class="mt-1 text-xs text-graphite">
          {{ perf?.completed_orders ?? 0 }} of {{ perf?.total_orders ?? 0 }} orders
        </p>
      </div>

      <!-- Revisions -->
      <div class="rounded-xl border border-slate-200 bg-white p-4">
        <p class="text-xs font-medium uppercase tracking-wide text-graphite">Revisions</p>
        <div class="mt-2 flex items-center gap-2">
          <XCircle class="h-5 w-5 shrink-0 text-slate-400" />
          <p class="text-2xl font-bold text-ink">{{ perf?.revision_count ?? "—" }}</p>
        </div>
        <p class="mt-1 text-xs text-graphite">Total revision requests</p>
      </div>
    </div>

    <!-- Earnings chart -->
    <div class="rounded-xl border border-slate-200 bg-white p-5">
      <div class="flex items-center justify-between mb-1">
        <h2 class="text-sm font-semibold text-ink flex items-center gap-2">
          <TrendingUp class="size-4 text-emerald-500" /> Monthly earnings
        </h2>
        <template v-if="earnings?.summary?.change_pct != null">
          <span
            class="rounded-full px-2 py-0.5 text-xs font-semibold"
            :class="earnings.summary.change_pct >= 0 ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-600'"
          >
            {{ earnings.summary.change_pct >= 0 ? '+' : '' }}{{ earnings.summary.change_pct.toFixed(1) }}%
          </span>
        </template>
      </div>
      <AppChart v-if="earnings" :option="earningsOption" :loading="loading" height="300px" class="mt-2" />
      <div v-else-if="loading" class="h-72 animate-pulse rounded-lg bg-slate-100 mt-2" />
      <p v-else class="mt-6 text-center text-sm text-graphite">No earnings data yet.</p>
    </div>

  </div>
</template>

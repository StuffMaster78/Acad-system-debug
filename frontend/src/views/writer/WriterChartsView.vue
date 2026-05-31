<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { TrendingUp, RefreshCw } from "@lucide/vue";
import AppChart from "@/components/ui/AppChart.vue";
import { analyticsChartsApi, type ChartData } from "@/api/analyticsCharts";
import { useWriterWorkspaceStore } from "@/stores/writerWorkspace";
import type { EChartsOption } from "echarts";

const writerWs = useWriterWorkspaceStore();
const earnings = ref<ChartData | null>(null);
const loading  = ref(false);
const months   = ref(12);

const earningsOption = computed<EChartsOption>(() => {
  const d = earnings.value;
  if (!d) return {};
  return {
    tooltip: { trigger: "axis" },
    legend: { data: d.series.map((s) => s.name), bottom: 0 },
    grid: { left: 64, right: 48, top: 16, bottom: 44 },
    xAxis: { type: "category", data: d.labels, axisLabel: { rotate: 30, fontSize: 11 } },
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

const summaryStats = computed(() => [
  { label: "Completed orders", value: writerWs.summary?.completed_orders ?? "—" },
  { label: "Pending payout", value: writerWs.balance?.pending != null ? `$${Number(writerWs.balance.pending).toFixed(2)}` : "—" },
  { label: "Current window", value: writerWs.currentWindow?.net != null ? `$${Number(writerWs.currentWindow.net).toFixed(2)}` : "—" },
]);

async function load() {
  loading.value = true;
  try {
    const r = await analyticsChartsApi.writerEarnings({ months: months.value });
    earnings.value = r.data;
  } catch { /* non-fatal */ }
  finally { loading.value = false; }
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
        <h1 class="text-xl font-bold text-ink">Charts</h1>
        <p class="mt-0.5 text-sm text-graphite">Your earnings trend over time</p>
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

    <!-- Summary tiles -->
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

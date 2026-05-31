<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { use } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { LineChart } from "echarts/charts";
import { GridComponent, TooltipComponent } from "echarts/components";
import VChart from "vue-echarts";
import { analyticsChartsApi } from "@/api/analyticsCharts";
import type { EChartsOption } from "echarts";

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent]);

const props = defineProps<{ role: "admin" | "superadmin" }>();

const totalRevenue = ref<number | null>(null);
const totalOrders  = ref<number | null>(null);
const sparkData    = ref<number[]>([]);
const sparkLabels  = ref<string[]>([]);

const option = computed<EChartsOption>(() => ({
  backgroundColor: "transparent",
  grid: { left: 0, right: 0, top: 4, bottom: 0, containLabel: false },
  xAxis: { type: "category", data: sparkLabels.value, show: false },
  yAxis: { type: "value", show: false },
  tooltip: {
    trigger: "axis",
    backgroundColor: "#18181b",
    borderColor: "#3f3f46",
    textStyle: { color: "#e4e4e7", fontSize: 11 },
    formatter: (p: unknown) => {
      const params = p as Array<{ name: string; value: number }>;
      return `${params[0]?.name}<br/><b>$${Number(params[0]?.value ?? 0).toLocaleString()}</b>`;
    },
  },
  series: [{
    type: "line",
    data: sparkData.value,
    smooth: true,
    symbol: "none",
    lineStyle: { color: "#a78bfa", width: 1.5 },
    areaStyle: { color: { type: "linear", x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: "rgba(167,139,250,0.25)" }, { offset: 1, color: "rgba(167,139,250,0)" }] } },
  }],
}));

function money(v: number) {
  if (v >= 1000) return `$${(v / 1000).toFixed(1)}k`;
  return `$${v.toFixed(0)}`;
}

onMounted(async () => {
  try {
    const { data } = await analyticsChartsApi.daily({ days: 14 });
    sparkData.value   = data.series[0]?.data ?? [];
    sparkLabels.value = data.labels;
    totalRevenue.value = data.summary.total_revenue;
    totalOrders.value  = data.summary.total_orders;
  } catch { /* non-fatal */ }
});
</script>

<template>
  <div class="mx-2 mb-2 rounded-lg border border-slate-700 bg-slate-700/40 p-3">
    <!-- Stat row -->
    <div class="mb-2.5 flex items-center justify-between gap-2">
      <div>
        <p class="text-[9px] font-semibold uppercase tracking-widest text-zinc-600">14d revenue</p>
        <p class="mt-0.5 text-[15px] font-bold leading-none text-zinc-100">
          {{ totalRevenue != null ? money(totalRevenue) : '—' }}
        </p>
      </div>
      <div class="text-right">
        <p class="text-[9px] font-semibold uppercase tracking-widest text-zinc-600">Orders</p>
        <p class="mt-0.5 text-[15px] font-bold leading-none text-zinc-100">
          {{ totalOrders != null ? totalOrders.toLocaleString() : '—' }}
        </p>
      </div>
    </div>

    <!-- Sparkline -->
    <VChart
      v-if="sparkData.length"
      :option="option"
      :style="{ height: '52px', width: '100%' }"
      autoresize
    />
    <div v-else class="h-[52px] animate-pulse rounded bg-white/[0.04]" />
  </div>
</template>

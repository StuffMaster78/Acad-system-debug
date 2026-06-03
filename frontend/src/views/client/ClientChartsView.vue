<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { ArrowRight, RefreshCw, TrendingUp } from "@lucide/vue";
import { useRouter } from "vue-router";
import AppChart from "@/components/ui/AppChart.vue";
import { analyticsChartsApi, type ChartData } from "@/api/analyticsCharts";
import { api, apiPath } from "@/api/client";
import { useOrderStore } from "@/stores/orders";
import { useWalletStore } from "@/stores/wallets";
import type { EChartsOption } from "echarts";

const router = useRouter();
const orderStore = useOrderStore();
const walletStore = useWalletStore();
const spending = ref<ChartData | null>(null);
const loading = ref(false);
const months = ref(12);

interface OrderSummary {
  total_spend: number;
  total_orders: number;
  avg_order_value: number;
  recent_orders: { id: number; topic: string; amount: number; currency: string; status: string; created_at: string | null }[];
}
const summary = ref<OrderSummary | null>(null);

const spendingOption = computed<EChartsOption>(() => {
  const d = spending.value;
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
      itemStyle: { color: i === 0 ? "#6366f1" : "#cbd5e1" },
      lineStyle: { color: "#cbd5e1" },
      areaStyle: s.type === "bar" ? undefined : { color: "rgba(99,102,241,0.06)" },
    })),
  };
});

const orderStatusOption = computed<EChartsOption>(() => {
  const statuses = ["pending", "in_progress", "completed", "cancelled"];
  const data = statuses.map((s) => ({
    name: s.replace(/_/g, " "),
    value: orderStore.orders.filter((o) => o.status === s).length,
  })).filter((d) => d.value > 0);
  if (!data.length) return {};
  return {
    tooltip: { trigger: "item" },
    legend: { bottom: 0 },
    series: [{
      name: "Orders", type: "pie", radius: ["45%", "75%"], data,
      label: { formatter: "{b}: {c}" },
      itemStyle: { borderRadius: 4 },
    }],
  };
});

const lifetimeTiles = computed(() => [
  {
    label: "Total spent",
    value: summary.value != null ? `$${summary.value.total_spend.toFixed(2)}` : "—",
  },
  {
    label: "Orders placed",
    value: summary.value != null ? summary.value.total_orders : "—",
  },
  {
    label: "Avg order value",
    value: summary.value != null ? `$${summary.value.avg_order_value.toFixed(2)}` : "—",
  },
  {
    label: "Wallet balance",
    value: `${walletStore.currency} ${walletStore.availableBalance.toFixed(2)}`,
  },
]);

function fmtDate(iso: string | null) {
  if (!iso) return "";
  return new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" }).format(new Date(iso));
}

function statusClass(s: string) {
  if (s === "completed") return "bg-emerald-50 text-emerald-700";
  if (s === "cancelled" || s === "refunded") return "bg-red-50 text-red-600";
  if (s === "in_progress" || s === "qa_review") return "bg-blue-50 text-blue-700";
  return "bg-slate-100 text-slate-600";
}

async function load() {
  loading.value = true;
  try {
    const [spendRes, sumRes] = await Promise.allSettled([
      analyticsChartsApi.clientSpending({ months: months.value }),
      api.get<OrderSummary>(apiPath("/analytics/charts/client-summary/")),
    ]);
    if (spendRes.status === "fulfilled") spending.value = spendRes.value.data;
    if (sumRes.status === "fulfilled") summary.value = sumRes.value.data;
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  if (!orderStore.orders.length) orderStore.fetchOrders().catch(() => undefined);
  if (!walletStore.wallet) walletStore.fetchWallet().catch(() => undefined);
  load();
});
</script>

<template>
  <div class="space-y-6 p-6">

    <div class="flex flex-wrap items-center justify-between gap-4">
      <div>
        <h1 class="text-xl font-bold text-ink">Spending Analytics</h1>
        <p class="mt-0.5 text-sm text-graphite">Your order history and spending breakdown</p>
      </div>
      <div class="flex items-center gap-2">
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

    <!-- Lifetime summary tiles -->
    <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
      <div
        v-for="tile in lifetimeTiles"
        :key="tile.label"
        class="rounded-xl border border-slate-200 bg-white p-4"
      >
        <p class="text-xs font-medium uppercase tracking-wide text-graphite">{{ tile.label }}</p>
        <p class="mt-1.5 text-2xl font-bold text-ink">{{ tile.value }}</p>
      </div>
    </div>

    <div class="grid gap-6 xl:grid-cols-[1.5fr_1fr]">

      <!-- Spending trend -->
      <div class="rounded-xl border border-slate-200 bg-white p-5">
        <div class="flex items-center justify-between mb-1">
          <h2 class="text-sm font-semibold text-ink flex items-center gap-2">
            <TrendingUp class="size-4 text-indigo-500" /> Monthly spend
          </h2>
          <template v-if="spending?.summary?.change_pct != null">
            <span
              class="rounded-full px-2 py-0.5 text-xs font-semibold"
              :class="spending.summary.change_pct >= 0 ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-600'"
            >
              {{ spending.summary.change_pct >= 0 ? '+' : '' }}{{ spending.summary.change_pct.toFixed(1) }}%
            </span>
          </template>
        </div>
        <AppChart v-if="spending" :option="spendingOption" :loading="loading" height="260px" class="mt-2" />
        <div v-else-if="loading" class="h-64 animate-pulse rounded-lg bg-slate-100 mt-2" />
        <p v-else class="mt-6 text-center text-sm text-graphite">No spending data yet.</p>
      </div>

      <!-- Order status donut -->
      <div class="rounded-xl border border-slate-200 bg-white p-5">
        <h2 class="text-sm font-semibold text-ink mb-4">Orders by status</h2>
        <AppChart
          v-if="orderStore.orders.length"
          :option="orderStatusOption"
          height="260px"
        />
        <p v-else class="mt-6 text-center text-sm text-graphite">No orders yet.</p>
      </div>

    </div>

    <!-- Recent orders -->
    <div class="rounded-xl border border-slate-200 bg-white p-5">
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-sm font-semibold text-ink">Recent paid orders</h2>
        <button
          class="flex items-center gap-1 text-xs text-indigo-600 hover:underline"
          @click="router.push({ name: 'client-orders' })"
        >
          View all <ArrowRight class="h-3 w-3" />
        </button>
      </div>
      <div v-if="summary?.recent_orders?.length" class="divide-y divide-slate-100">
        <div
          v-for="order in summary.recent_orders"
          :key="order.id"
          class="flex items-center justify-between py-3 text-sm"
        >
          <div class="min-w-0 flex-1">
            <p class="truncate font-medium text-ink">{{ order.topic || `Order #${order.id}` }}</p>
            <p class="text-xs text-graphite">{{ fmtDate(order.created_at) }}</p>
          </div>
          <div class="ml-4 flex items-center gap-3 shrink-0">
            <span
              class="rounded-full px-2 py-0.5 text-xs font-medium capitalize"
              :class="statusClass(order.status)"
            >
              {{ order.status.replace(/_/g, " ") }}
            </span>
            <span class="font-semibold text-ink">${{ order.amount.toFixed(2) }}</span>
          </div>
        </div>
      </div>
      <div v-else-if="loading" class="space-y-3">
        <div v-for="n in 3" :key="n" class="h-10 animate-pulse rounded-lg bg-slate-100" />
      </div>
      <p v-else class="text-center text-sm text-graphite py-4">No paid orders yet.</p>
    </div>

  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { Headphones, ShieldAlert } from "@lucide/vue";
import AppChart from "@/components/ui/AppChart.vue";
import { useSupportWorkspaceStore } from "@/stores/supportWorkspace";
import type { EChartsOption } from "echarts";

const support = useSupportWorkspaceStore();

const statusBreakdown = computed(() => {
  const tickets = support.tickets;
  const statuses = ["open", "in_progress", "resolved", "closed"];
  return statuses.map((s) => ({
    name: s.replace(/_/g, " "),
    value: tickets.filter((t) => t.status === s || (!statuses.slice(0, 2).includes(s) && t.status === s)).length,
  })).filter((d) => d.value > 0);
});

const priorityBreakdown = computed(() => {
  const tickets = support.tickets;
  return ["critical", "high", "medium", "low"].map((p) => ({
    name: p,
    value: tickets.filter((t) => t.priority === p).length,
  })).filter((d) => d.value > 0);
});

const queueBreakdown = computed(() => {
  const q = support.queue;
  return [
    { name: "Unassigned", value: q.counts?.unassigned ?? support.tickets.filter((t) => !t.assigned_to && !t.assigned_to_name).length },
    { name: "Assigned to me", value: q.counts?.my_assigned ?? support.tickets.filter((t) => t.assigned_to || t.assigned_to_name).length },
    { name: "High priority", value: q.counts?.high_priority ?? support.tickets.filter((t) => ["high", "critical"].includes(t.priority)).length },
    { name: "Overdue", value: q.counts?.overdue ?? 0 },
    { name: "Escalated", value: support.tickets.filter((t) => t.is_escalated).length },
  ].filter((d) => d.value > 0);
});

const statusChartOption = computed<EChartsOption>(() => {
  if (!statusBreakdown.value.length) return {};
  return {
    tooltip: { trigger: "item", confine: true, formatter: "{b}: {c} ({d}%)" },
    legend: { bottom: 8, type: "scroll" },
    series: [{
      name: "Tickets", type: "pie", radius: ["45%", "72%"],
      center: ["50%", "44%"],
      data: statusBreakdown.value,
      label: { show: false },
      labelLine: { show: false },
      emphasis: { label: { show: true, fontWeight: "bold", fontSize: 12, formatter: "{b}: {c}" } },
      itemStyle: { borderRadius: 4 },
    }],
  };
});

const priorityChartOption = computed<EChartsOption>(() => {
  if (!priorityBreakdown.value.length) return {};
  const palette = ["#ef4444", "#f97316", "#f59e0b", "#94a3b8"];
  return {
    tooltip: { trigger: "item", confine: true, formatter: "{b}: {c} ({d}%)" },
    legend: { bottom: 8, type: "scroll" },
    series: [{
      name: "Priority", type: "pie", radius: ["45%", "72%"],
      center: ["50%", "44%"],
      data: priorityBreakdown.value.map((d, i) => ({ ...d, itemStyle: { color: palette[i] } })),
      label: { show: false },
      labelLine: { show: false },
      emphasis: { label: { show: true, fontWeight: "bold", fontSize: 12, formatter: "{b}: {c}" } },
      itemStyle: { borderRadius: 4 },
    }],
  };
});

const queueChartOption = computed<EChartsOption>(() => {
  if (!queueBreakdown.value.length) return {};
  return {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, confine: true },
    grid: { left: 12, right: 24, top: 10, bottom: 12, containLabel: true },
    xAxis: { type: "value", minInterval: 1 },
    yAxis: { type: "category", data: queueBreakdown.value.map((d) => d.name), axisLabel: { fontSize: 11, width: 110, overflow: "truncate" } },
    series: [{ name: "Tickets", type: "bar", data: queueBreakdown.value.map((d) => d.value), itemStyle: { color: "#6366f1" }, barMaxWidth: 28 }],
  };
});

const summaryStats = computed(() => support.metrics.slice(0, 4));

onMounted(() => {
  if (!support.tickets.length) support.hydrate().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-6 p-6">

    <div>
      <h1 class="text-xl font-bold text-ink">Charts</h1>
      <p class="mt-0.5 text-sm text-graphite">Ticket queue, priority, and status breakdown</p>
    </div>

    <!-- Summary tiles -->
    <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
      <div
        v-for="stat in summaryStats"
        :key="stat.label"
        class="rounded-xl border border-slate-200 bg-white p-4"
      >
        <p class="text-xs font-medium uppercase tracking-wide text-graphite">{{ stat.label }}</p>
        <p class="mt-1.5 text-2xl font-bold text-ink">{{ stat.value }}</p>
        <p v-if="stat.detail" class="mt-0.5 text-xs text-graphite truncate">{{ stat.detail }}</p>
      </div>
    </div>

    <!-- Status + Priority donuts -->
    <div class="grid gap-6 xl:grid-cols-2">
      <div class="rounded-xl border border-slate-200 bg-white p-5">
        <h2 class="text-sm font-semibold text-ink flex items-center gap-2 mb-4">
          <Headphones class="size-4 text-indigo-500" /> Tickets by status
        </h2>
        <AppChart v-if="statusBreakdown.length" :option="statusChartOption" height="240px" />
        <p v-else class="mt-4 text-center text-sm text-graphite">No ticket data yet.</p>
      </div>

      <div class="rounded-xl border border-slate-200 bg-white p-5">
        <h2 class="text-sm font-semibold text-ink flex items-center gap-2 mb-4">
          <ShieldAlert class="size-4 text-amber-500" /> Tickets by priority
        </h2>
        <AppChart v-if="priorityBreakdown.length" :option="priorityChartOption" height="240px" />
        <p v-else class="mt-4 text-center text-sm text-graphite">No ticket data yet.</p>
      </div>
    </div>

    <!-- Queue breakdown bar -->
    <div class="rounded-xl border border-slate-200 bg-white p-5">
      <h2 class="text-sm font-semibold text-ink mb-4">Queue breakdown</h2>
      <AppChart v-if="queueBreakdown.length" :option="queueChartOption" height="200px" />
      <p v-else class="mt-4 text-center text-sm text-graphite">No queue data yet.</p>
    </div>

  </div>
</template>

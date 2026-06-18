<script setup lang="ts">
import { computed, onMounted } from "vue";
import { BarChart3, RefreshCw } from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import AppChart from "@/components/ui/AppChart.vue";
import { useEditorWorkspaceStore } from "@/stores/editorWorkspace";
import type { EChartsOption } from "echarts";

const workspace = useEditorWorkspaceStore();

const statusBreakdown = computed(() => Object.entries(workspace.analytics.status_breakdown ?? {}));
const assignmentBreakdown = computed(() => Object.entries(workspace.analytics.assignment_breakdown ?? {}));
const weeklyTasks = computed(() => [...(workspace.analytics.weekly_tasks ?? [])].reverse());
const recentReviews = computed(() => workspace.activity.recent_reviews ?? []);

const maxWeeklyCount = computed(() => Math.max(...(workspace.analytics.weekly_tasks ?? []).map((w) => w.count), 1));

function reviewTone(isApproved?: boolean): "success" | "danger" | "neutral" {
  if (isApproved === true) return "success";
  if (isApproved === false) return "danger";
  return "neutral";
}

function formatDate(value?: string | null): string {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric" }).format(new Date(value));
}

const weeklyChartOption = computed<EChartsOption>(() => {
  const weeks = weeklyTasks.value;
  if (!weeks.length) return {};
  return {
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, confine: true },
    grid: { left: 12, right: 24, top: 10, bottom: 12, containLabel: true },
    xAxis: { type: "value", minInterval: 1 },
    yAxis: { type: "category", data: weeks.map((w) => w.week ?? ""), axisLabel: { fontSize: 11, width: 90, overflow: "truncate" } },
    series: [{ name: "Tasks", type: "bar", data: weeks.map((w) => w.count), itemStyle: { color: "#0ea5e9" }, barMaxWidth: 28 }],
  };
});

const statusChartOption = computed<EChartsOption>(() => {
  const entries = statusBreakdown.value;
  if (!entries.length) return {};
  return {
    tooltip: { trigger: "item", confine: true, formatter: "{b}: {c} ({d}%)" },
    legend: { bottom: 8, type: "scroll" },
    series: [{
      name: "Tasks",
      type: "pie",
      radius: ["40%", "70%"],
      center: ["50%", "44%"],
      data: entries.map(([name, value]) => ({ name, value })),
      label: { show: false },
      labelLine: { show: false },
      emphasis: { label: { show: true, fontWeight: "bold", fontSize: 12, formatter: "{b}: {c}" } },
    }],
  };
});

onMounted(async () => {
  if (!workspace.tasks.length) await workspace.hydrate();
});
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Editor workspace</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Analytics</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Task breakdown, assignment mix, weekly output, and recent review submissions.
        </p>
      </div>
      <button
        class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold disabled:opacity-60"
        type="button"
        :disabled="workspace.isLoading"
        @click="workspace.hydrate()"
      >
        <RefreshCw class="h-4 w-4" :class="workspace.isLoading ? 'animate-spin' : ''" />
        Refresh
      </button>
    </section>

    <div v-if="workspace.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ workspace.error }}
    </div>

    <section class="grid gap-4 sm:grid-cols-3">
      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <p class="text-sm font-medium text-graphite">Total tasks tracked</p>
        <p class="mt-2 text-3xl font-semibold text-ink">{{ workspace.analytics.total_tasks ?? 0 }}</p>
      </div>
      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <p class="text-sm font-medium text-graphite">Overdue tasks</p>
        <p class="mt-2 text-3xl font-semibold" :class="(workspace.analytics.overdue_tasks_count ?? 0) > 0 ? 'text-rose-600' : 'text-ink'">
          {{ workspace.analytics.overdue_tasks_count ?? 0 }}
        </p>
      </div>
      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <p class="text-sm font-medium text-graphite">Urgent tasks</p>
        <p class="mt-2 text-3xl font-semibold" :class="(workspace.analytics.urgent_tasks_count ?? 0) > 0 ? 'text-amber-600' : 'text-ink'">
          {{ workspace.analytics.urgent_tasks_count ?? 0 }}
        </p>
      </div>
    </section>

    <section class="grid gap-6 lg:grid-cols-2">
      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <h2 class="text-base font-semibold text-ink">Status breakdown</h2>
        <AppChart
          v-if="statusBreakdown.length"
          :option="statusChartOption"
          height="200px"
          class="mt-2"
        />
        <p v-else class="mt-4 text-sm text-graphite">No status data available.</p>
      </div>

      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <h2 class="text-base font-semibold text-ink">Assignment mix</h2>
        <div class="mt-4 space-y-2">
          <div
            v-for="([kind, count]) in assignmentBreakdown"
            :key="kind"
            class="flex items-center justify-between gap-3"
          >
            <span class="text-sm capitalize text-graphite">{{ kind }}</span>
            <div class="flex items-center gap-3">
              <div class="h-2 w-24 overflow-hidden rounded-full bg-slate-100">
                <div
                  class="h-full rounded-full bg-signal/70"
                  :style="{ width: `${Math.min(((count as number) / (workspace.analytics.total_tasks ?? 1)) * 100, 100)}%` }"
                />
              </div>
              <span class="w-8 text-right text-sm font-semibold text-ink">{{ count }}</span>
            </div>
          </div>
          <p v-if="!assignmentBreakdown.length" class="text-sm text-graphite">No assignment data available.</p>
        </div>
      </div>
    </section>

    <section class="grid gap-6 lg:grid-cols-[1fr_380px]">
      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <div class="flex items-center gap-2">
          <BarChart3 class="h-5 w-5 text-signal" />
          <h2 class="text-base font-semibold text-ink">Weekly output</h2>
        </div>

        <AppChart
          v-if="weeklyTasks.length"
          :option="weeklyChartOption"
          height="220px"
          class="mt-4"
        />
        <p v-else class="mt-5 text-sm text-graphite">No weekly data available.</p>
      </div>

      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <h2 class="text-base font-semibold text-ink">Recent reviews</h2>
        <div class="mt-4 divide-y divide-slate-100">
          <div
            v-for="review in recentReviews"
            :key="String(review.id)"
            class="py-3"
          >
            <div class="flex items-start justify-between gap-2">
              <p class="min-w-0 truncate text-sm font-semibold text-ink">
                {{ review.order_topic ?? `Order #${review.order_id}` }}
              </p>
              <span class="shrink-0 text-sm font-semibold text-ink">{{ review.quality_score ?? "—" }}</span>
            </div>
            <div class="mt-1.5 flex items-center gap-2">
              <StatusPill
                :label="review.is_approved ? 'Approved' : 'Not approved'"
                :tone="reviewTone(review.is_approved)"
              />
              <span class="text-xs text-graphite">{{ formatDate(review.submitted_at) }}</span>
            </div>
          </div>
          <p v-if="!recentReviews.length" class="py-4 text-sm text-graphite">No recent review submissions.</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { RefreshCw, Timer } from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useEditorWorkspaceStore } from "@/stores/editorWorkspace";

const workspace = useEditorWorkspaceStore();

onMounted(async () => {
  if (!workspace.tasks.length) await workspace.hydrate();
});
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Editor workspace</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Workload</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Capacity, deadline pressure, time estimates, and task recommendations.
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

    <section class="grid gap-4 md:grid-cols-3">
      <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <p class="text-sm font-medium text-graphite">Capacity used</p>
        <p class="mt-2 text-3xl font-semibold text-ink">{{ Math.round(workspace.capacity) }}%</p>
        <p class="mt-1 text-xs text-graphite">
          {{ workspace.workload.current_workload?.active_tasks_count ?? 0 }} of
          {{ workspace.workload.current_workload?.max_concurrent_tasks ?? 0 }} max tasks
        </p>
        <div class="mt-3 h-2 w-full overflow-hidden rounded-full bg-slate-100">
          <div
            class="h-full rounded-full transition-all"
            :class="workspace.capacity >= 90 ? 'bg-rose-500' : workspace.capacity >= 70 ? 'bg-amber-400' : 'bg-emerald-500'"
            :style="{ width: `${Math.min(workspace.capacity, 100)}%` }"
          />
        </div>
      </div>

      <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <p class="text-sm font-medium text-graphite">Available slots</p>
        <p class="mt-2 text-3xl font-semibold text-ink">{{ workspace.workload.current_workload?.available_slots ?? 0 }}</p>
        <StatusPill
          class="mt-2"
          :label="workspace.workload.current_workload?.is_at_capacity ? 'At capacity' : 'Can take work'"
          :tone="workspace.workload.current_workload?.is_at_capacity ? 'danger' : 'success'"
        />
      </div>

      <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <p class="text-sm font-medium text-graphite">Avg hours / task</p>
        <p class="mt-2 text-3xl font-semibold text-ink">{{ workspace.workload.time_estimates?.average_hours_per_task ?? 0 }}</p>
        <p class="mt-1 text-xs text-graphite">
          Est. {{ workspace.workload.time_estimates?.estimated_hours_until_all_deadlines ?? 0 }} h until all deadlines
        </p>
      </div>
    </section>

    <section class="grid gap-6 lg:grid-cols-2">
      <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <div class="flex items-center gap-2">
          <Timer class="h-5 w-5 text-signal" />
          <h2 class="text-lg font-semibold text-ink">Deadline analysis</h2>
        </div>
        <div class="mt-5 space-y-3">
          <div class="flex items-center justify-between rounded-md border border-slate-200 px-4 py-3">
            <span class="text-sm text-graphite">Overdue tasks</span>
            <span
              class="text-lg font-semibold"
              :class="(workspace.workload.deadline_analysis?.overdue_tasks ?? 0) > 0 ? 'text-rose-600' : 'text-ink'"
            >
              {{ workspace.workload.deadline_analysis?.overdue_tasks ?? 0 }}
            </span>
          </div>
          <div class="flex items-center justify-between rounded-md border border-slate-200 px-4 py-3">
            <span class="text-sm text-graphite">Urgent (within 24 h)</span>
            <span
              class="text-lg font-semibold"
              :class="(workspace.workload.deadline_analysis?.urgent_tasks ?? 0) > 0 ? 'text-amber-600' : 'text-ink'"
            >
              {{ workspace.workload.deadline_analysis?.urgent_tasks ?? 0 }}
            </span>
          </div>
          <div class="flex items-center justify-between rounded-md border border-slate-200 px-4 py-3">
            <span class="text-sm text-graphite">Total with deadlines</span>
            <span class="text-lg font-semibold text-ink">
              {{ workspace.workload.deadline_analysis?.total_with_deadlines ?? 0 }}
            </span>
          </div>
        </div>
      </div>

      <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <h2 class="text-lg font-semibold text-ink">Recommendations</h2>
        <div class="mt-5 space-y-3">
          <div class="flex items-center justify-between rounded-md border border-slate-200 px-4 py-3">
            <div>
              <p class="text-sm font-medium text-ink">Claim more work</p>
              <p class="mt-0.5 text-xs text-graphite">Based on available capacity</p>
            </div>
            <StatusPill
              :label="workspace.workload.recommendations?.should_claim_more ? 'Yes' : 'No'"
              :tone="workspace.workload.recommendations?.should_claim_more ? 'success' : 'neutral'"
            />
          </div>
          <div class="flex items-center justify-between rounded-md border border-slate-200 px-4 py-3">
            <div>
              <p class="text-sm font-medium text-ink">Focus on urgent first</p>
              <p class="mt-0.5 text-xs text-graphite">Prioritise tasks approaching deadline</p>
            </div>
            <StatusPill
              :label="workspace.workload.recommendations?.should_focus_on_urgent ? 'Yes' : 'No'"
              :tone="workspace.workload.recommendations?.should_focus_on_urgent ? 'warning' : 'neutral'"
            />
          </div>
          <div class="flex items-center justify-between rounded-md border border-slate-200 px-4 py-3">
            <div>
              <p class="text-sm font-medium text-ink">Recommended max orders</p>
              <p class="mt-0.5 text-xs text-graphite">Concurrent task ceiling</p>
            </div>
            <span class="text-lg font-semibold text-ink">
              {{ workspace.workload.recommendations?.recommended_max_orders ?? "—" }}
            </span>
          </div>
        </div>

        <div class="mt-5 border-t border-slate-200 pt-4">
          <h3 class="text-sm font-semibold text-ink">Performance benchmarks</h3>
          <div class="mt-3 space-y-2">
            <div class="flex items-center justify-between text-sm">
              <span class="text-graphite">On-time completion rate</span>
              <span class="font-semibold text-ink">{{ workspace.performance.on_time_completion_rate ?? 0 }}%</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-graphite">Revision rate</span>
              <span class="font-semibold text-ink">{{ workspace.performance.revision_rate ?? 0 }}%</span>
            </div>
            <div class="flex items-center justify-between text-sm">
              <span class="text-graphite">Total reviews</span>
              <span class="font-semibold text-ink">{{ workspace.performance.total_reviews ?? 0 }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

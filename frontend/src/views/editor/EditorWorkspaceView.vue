<script setup lang="ts">
import { onMounted } from "vue";
import { Clock3, RefreshCw } from "@lucide/vue";
import MetricTile from "@/components/ui/MetricTile.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useEditorWorkspaceStore } from "@/stores/editorWorkspace";

const workspace = useEditorWorkspaceStore();

const activityRows = () => workspace.activity.activity_logs ?? [];
const recentReviews = () => workspace.activity.recent_reviews ?? [];

function dateLabel(value: string | null | undefined): string {
  if (!value) return "No deadline";
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

onMounted(async () => {
  await workspace.hydrate();
});
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Editor workspace</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">
          {{ workspace.profile?.name ?? "Quality desk" }}
        </h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          QA queue, review decisions, workload, and editor performance brought forward from the backend.
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-2">
        <StatusPill
          :label="workspace.profile?.can_self_assign === false ? 'Manual assignment only' : 'Can self-assign'"
          :tone="workspace.profile?.can_self_assign === false ? 'warning' : 'success'"
        />
        <StatusPill
          :label="workspace.workload.current_workload?.is_at_capacity ? 'At capacity' : 'Capacity available'"
          :tone="workspace.workload.current_workload?.is_at_capacity ? 'danger' : 'neutral'"
        />
        <button
          class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold disabled:opacity-60"
          type="button"
          :disabled="workspace.isLoading"
          @click="workspace.hydrate()"
        >
          <RefreshCw class="h-4 w-4" :class="workspace.isLoading ? 'animate-spin' : ''" />
          Refresh
        </button>
      </div>
    </section>

    <div v-if="workspace.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ workspace.error }}
    </div>
    <div v-if="workspace.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ workspace.notice }}
    </div>

    <section class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <MetricTile v-for="metric in workspace.metrics" :key="metric.label" :metric="metric" />
    </section>

    <section class="grid gap-6 xl:grid-cols-3">
      <div class="rounded-lg border border-slate-200 bg-white p-5 xl:col-span-2">
        <div class="flex items-center gap-2">
          <Clock3 class="h-5 w-5 text-signal" />
          <h2 class="text-lg font-semibold text-ink">Workload snapshot</h2>
        </div>
        <div class="mt-5 grid gap-4 md:grid-cols-3">
          <div class="rounded-md border border-slate-200 p-4">
            <p class="text-sm font-medium text-graphite">Available slots</p>
            <p class="mt-2 text-2xl font-semibold text-ink">{{ workspace.workload.current_workload?.available_slots ?? 0 }}</p>
          </div>
          <div class="rounded-md border border-slate-200 p-4">
            <p class="text-sm font-medium text-graphite">Avg hours / task</p>
            <p class="mt-2 text-2xl font-semibold text-ink">{{ workspace.workload.time_estimates?.average_hours_per_task ?? 0 }}</p>
          </div>
          <div class="rounded-md border border-slate-200 p-4">
            <p class="text-sm font-medium text-graphite">On-time rate</p>
            <p class="mt-2 text-2xl font-semibold text-ink">{{ workspace.performance.on_time_completion_rate ?? 0 }}%</p>
          </div>
        </div>

        <div class="mt-5 grid gap-4 md:grid-cols-2">
          <div class="rounded-md border border-slate-200 p-4">
            <h3 class="text-sm font-semibold text-ink">Deadline analysis</h3>
            <div class="mt-3 space-y-2 text-sm">
              <div class="flex items-center justify-between">
                <span class="text-graphite">Overdue</span>
                <span class="font-semibold text-danger">{{ workspace.workload.deadline_analysis?.overdue_tasks ?? 0 }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-graphite">Urgent (&lt; 24 h)</span>
                <span class="font-semibold text-ink">{{ workspace.workload.deadline_analysis?.urgent_tasks ?? 0 }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-graphite">Total with deadlines</span>
                <span class="font-semibold text-ink">{{ workspace.workload.deadline_analysis?.total_with_deadlines ?? 0 }}</span>
              </div>
            </div>
          </div>
          <div class="rounded-md border border-slate-200 p-4">
            <h3 class="text-sm font-semibold text-ink">Recommendations</h3>
            <div class="mt-3 space-y-2 text-sm">
              <div class="flex items-center justify-between">
                <span class="text-graphite">Claim more work</span>
                <StatusPill
                  :label="workspace.workload.recommendations?.should_claim_more ? 'Yes' : 'No'"
                  :tone="workspace.workload.recommendations?.should_claim_more ? 'success' : 'neutral'"
                />
              </div>
              <div class="flex items-center justify-between">
                <span class="text-graphite">Focus on urgent</span>
                <StatusPill
                  :label="workspace.workload.recommendations?.should_focus_on_urgent ? 'Yes' : 'No'"
                  :tone="workspace.workload.recommendations?.should_focus_on_urgent ? 'warning' : 'neutral'"
                />
              </div>
              <div class="flex items-center justify-between">
                <span class="text-graphite">Recommended max</span>
                <span class="font-semibold text-ink">{{ workspace.workload.recommendations?.recommended_max_orders ?? '—' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="rounded-lg border border-slate-200 bg-white p-5">
        <h2 class="text-lg font-semibold text-ink">Recent activity</h2>
        <div class="mt-4 space-y-3">
          <div
            v-for="event in activityRows()"
            :key="String(event.id)"
            class="rounded-md border border-slate-200 p-3"
          >
            <p class="text-sm font-semibold text-ink">{{ event.action ?? event.action_type }}</p>
            <p class="mt-1 text-xs text-graphite">
              {{ event.order_topic ?? `Order #${event.order_id ?? "unknown"}` }}
            </p>
            <p class="mt-2 text-xs text-slate-500">{{ dateLabel(event.timestamp) }}</p>
          </div>
          <div v-if="!activityRows().length" class="rounded-md border border-slate-200 bg-slate-50 px-4 py-6 text-sm text-graphite">
            No recent editor activity.
          </div>
        </div>

        <div class="mt-5 border-t border-slate-200 pt-4">
          <h3 class="text-sm font-semibold text-ink">Recent reviews</h3>
          <div class="mt-3 space-y-2">
            <div
              v-for="review in recentReviews()"
              :key="String(review.id)"
              class="flex items-center justify-between gap-3 text-sm"
            >
              <span class="min-w-0 truncate text-graphite">{{ review.order_topic ?? `Order #${review.order_id}` }}</span>
              <span class="font-semibold text-ink">{{ review.quality_score ?? "—" }}</span>
            </div>
            <p v-if="!recentReviews().length" class="text-sm text-graphite">No recent review submissions.</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

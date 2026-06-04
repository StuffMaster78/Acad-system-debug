<template>
  <div class="space-y-6 px-4 py-6">
    <!-- Header -->
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-xl font-bold text-ink">Trust Center</h1>
        <p class="mt-0.5 text-sm text-graphite">
          Security posture, sensitive event trends, and risk signals for this website.
        </p>
      </div>
      <div class="flex items-center gap-2">
        <select
          v-model="windowDays"
          class="focus-ring h-9 rounded-md border border-slate-200 bg-white px-3 text-sm"
          @change="refresh"
        >
          <option :value="7">Last 7 days</option>
          <option :value="30">Last 30 days</option>
          <option :value="90">Last 90 days</option>
        </select>
        <button
          class="focus-ring inline-flex h-9 items-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold"
          @click="refresh"
        >
          <RefreshCw class="h-4 w-4" /> Refresh
        </button>
      </div>
    </div>

    <div v-if="store.isSummaryLoading" class="grid grid-cols-2 gap-4 sm:grid-cols-4">
      <div v-for="n in 4" :key="n" class="h-24 animate-pulse rounded-xl bg-slate-100" />
    </div>

    <template v-else-if="store.summary">
      <!-- KPI strip -->
      <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div class="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <p class="text-xs font-semibold uppercase text-graphite">Total events</p>
          <p class="mt-2 text-3xl font-bold text-ink">{{ store.summary.total_events.toLocaleString() }}</p>
          <p class="mt-0.5 text-xs text-graphite">Last {{ windowDays }} days</p>
        </div>
        <div class="rounded-xl border border-amber-200 bg-amber-50 p-4 shadow-sm">
          <p class="text-xs font-semibold uppercase text-amber-700">Sensitive events</p>
          <p class="mt-2 text-3xl font-bold text-amber-800">{{ store.summary.sensitive_events.toLocaleString() }}</p>
          <p class="mt-0.5 text-xs text-amber-600">{{ sensitiveRate }}% of total</p>
        </div>
        <div class="rounded-xl border border-red-200 bg-red-50 p-4 shadow-sm">
          <p class="text-xs font-semibold uppercase text-red-700">Warnings</p>
          <p class="mt-2 text-3xl font-bold text-red-800">{{ (store.summary.by_severity.warning ?? 0).toLocaleString() }}</p>
        </div>
        <div class="rounded-xl border border-red-300 bg-red-100 p-4 shadow-sm">
          <p class="text-xs font-semibold uppercase text-red-800">Critical</p>
          <p class="mt-2 text-3xl font-bold text-red-900">{{ (store.summary.by_severity.critical ?? 0).toLocaleString() }}</p>
        </div>
      </div>

      <!-- Two-column layout -->
      <div class="grid gap-5 lg:grid-cols-2">

        <!-- Sensitivity breakdown -->
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 class="text-sm font-semibold text-ink">Sensitive event types</h2>
          <div class="mt-4 space-y-2">
            <div
              v-for="(count, level) in store.summary.by_sensitivity_level"
              :key="level"
              class="flex items-center justify-between rounded-lg border border-slate-100 px-3 py-2 text-sm"
            >
              <div class="flex items-center gap-2">
                <Shield class="h-3.5 w-3.5 text-amber-500" />
                <span class="text-ink capitalize">{{ String(level).replace(/_/g, " ") }}</span>
              </div>
              <span class="font-semibold text-graphite">{{ count }}</span>
            </div>
            <p v-if="!Object.keys(store.summary.by_sensitivity_level).length" class="text-sm text-graphite">
              No sensitive events in this window.
            </p>
          </div>
        </div>

        <!-- Top actions -->
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h2 class="text-sm font-semibold text-ink">Top audit actions</h2>
          <div class="mt-4 space-y-2">
            <div
              v-for="item in store.summary.top_actions.slice(0, 10)"
              :key="item.action"
              class="flex items-center gap-3"
            >
              <div class="min-w-0 flex-1">
                <p class="truncate font-mono text-xs text-ink">{{ humanAction(item.action) }}</p>
                <div class="mt-0.5 h-1.5 w-full rounded-full bg-slate-100">
                  <div
                    class="h-1.5 rounded-full bg-signal"
                    :style="{ width: `${Math.min(100, (item.count / maxActionCount) * 100)}%` }"
                  />
                </div>
              </div>
              <span class="shrink-0 text-xs font-semibold text-graphite">{{ item.count }}</span>
            </div>
          </div>
        </div>

        <!-- Recent critical / warning events -->
        <div class="rounded-xl border border-slate-200 bg-white p-5 shadow-sm lg:col-span-2">
          <div class="flex items-center justify-between">
            <h2 class="text-sm font-semibold text-ink">Recent warnings &amp; critical events</h2>
            <RouterLink
              :to="auditRoute"
              class="text-xs font-semibold text-signal hover:underline"
            >
              View full log →
            </RouterLink>
          </div>
          <div class="mt-4 divide-y divide-slate-100 overflow-x-auto">
            <div
              v-for="ev in store.summary.recent_critical"
              :key="ev.id"
              class="flex items-start gap-4 py-2.5"
            >
              <span
                class="mt-0.5 shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold capitalize"
                :class="ev.severity === 'critical' ? 'bg-red-100 text-red-700' : 'bg-amber-50 text-amber-700'"
              >{{ ev.severity }}</span>
              <div class="min-w-0 flex-1">
                <p class="truncate text-sm font-medium text-ink">{{ humanAction(ev.action) }}</p>
                <p class="mt-0.5 text-xs text-graphite">
                  <span v-if="ev.object_type">{{ ev.object_type }} #{{ ev.object_id }}</span>
                  <span v-if="ev.actor_id"> · Actor #{{ ev.actor_id }}</span>
                </p>
              </div>
              <p class="shrink-0 text-right text-xs text-graphite whitespace-nowrap">{{ fmtDate(ev.occurred_at) }}</p>
            </div>
            <p v-if="!store.summary.recent_critical.length" class="py-4 text-center text-sm text-graphite">
              No warnings or critical events in this window.
            </p>
          </div>
        </div>
      </div>
    </template>

    <p v-else class="text-sm text-graphite">Could not load trust center data.</p>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { RefreshCw, Shield } from "@lucide/vue";
import { useAuditLogStore, humanAction } from "@/stores/auditLog";
import { usePortalContextStore } from "@/stores/portalContext";

const store = useAuditLogStore();
const portalCtx = usePortalContextStore();
const windowDays = ref(30);

const auditRoute = computed(() =>
  portalCtx.surface === "staff" ? "/admin/audit" : "/superadmin/audit"
);

const sensitiveRate = computed(() => {
  if (!store.summary || !store.summary.total_events) return "0";
  return ((store.summary.sensitive_events / store.summary.total_events) * 100).toFixed(1);
});

const maxActionCount = computed(() => {
  if (!store.summary?.top_actions.length) return 1;
  return store.summary.top_actions[0].count;
});

function fmtDate(d: string) {
  return new Intl.DateTimeFormat("en", { dateStyle: "short", timeStyle: "short" }).format(new Date(d));
}

async function refresh() {
  await store.loadSummary(windowDays.value);
}

onMounted(refresh);
</script>

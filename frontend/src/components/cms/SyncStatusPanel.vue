<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { CheckCircle2, AlertTriangle, Clock, RefreshCw, XCircle } from "@lucide/vue";
import { api, apiPath } from "@/api/client";

interface SyncEntry {
  status: "success" | "partial" | "failed" | "skipped";
  rows_processed: number;
  ran_at: string;
  error_message: string | null;
  duration_seconds: number | null;
}

interface SyncStatus {
  gsc: SyncEntry | null;
  ga4: SyncEntry | null;
  freshness: SyncEntry | null;
  snapshot: SyncEntry | null;
  attribution: SyncEntry | null;
  embeddings: SyncEntry | null;
  recent_failures: Array<{ task: string; ran_at: string; error_message: string }>;
}

const data = ref<SyncStatus | null>(null);
const loading = ref(false);
const error = ref("");

const TASK_LABELS: Record<string, string> = {
  gsc: "GSC ingestion",
  ga4: "GA4 ingestion",
  freshness: "Freshness scanner",
  snapshot: "Performance snapshots",
  attribution: "Conversion attribution",
  embeddings: "Embedding generation",
};

const TASKS = ["gsc", "ga4", "freshness", "snapshot", "attribution", "embeddings"] as const;

const rows = computed(() =>
  TASKS.map((key) => ({
    key,
    label: TASK_LABELS[key],
    entry: data.value?.[key] ?? null,
  }))
);

function fmt(iso: string) {
  const d = new Date(iso);
  const now = Date.now();
  const diff = now - d.getTime();
  if (diff < 60_000) return "just now";
  if (diff < 3_600_000) return `${Math.floor(diff / 60_000)}m ago`;
  if (diff < 86_400_000) return `${Math.floor(diff / 3_600_000)}h ago`;
  return d.toLocaleDateString("en", { month: "short", day: "numeric" });
}

function statusIcon(entry: SyncEntry | null) {
  if (!entry) return Clock;
  if (entry.status === "success") return CheckCircle2;
  if (entry.status === "failed") return XCircle;
  return AlertTriangle;
}

function statusColor(entry: SyncEntry | null) {
  if (!entry) return "text-slate-400";
  if (entry.status === "success") return "text-emerald-500";
  if (entry.status === "failed") return "text-rose-500";
  return "text-amber-400";
}

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const { data: d } = await api.get<SyncStatus>(
      apiPath("/cms-api/intelligence/sync-status/")
    );
    data.value = d;
  } catch {
    error.value = "Could not load sync status.";
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <div class="space-y-4">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-base font-semibold text-ink">Intelligence sync status</h2>
        <p class="mt-0.5 text-xs text-graphite">Last run time for each nightly data ingestion task</p>
      </div>
      <button
        class="inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-medium text-graphite hover:text-ink transition-colors"
        :disabled="loading"
        @click="load"
      >
        <RefreshCw class="size-3" :class="{ 'animate-spin': loading }" />
        Refresh
      </button>
    </div>

    <p v-if="error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-2.5 text-xs text-amber-900">
      {{ error }}
    </p>

    <!-- Task table -->
    <div class="overflow-hidden rounded-xl border border-slate-200 bg-white">
      <table class="min-w-full text-sm">
        <thead>
          <tr class="border-b border-slate-100 bg-slate-50">
            <th class="px-4 py-2.5 text-left text-xs font-semibold uppercase tracking-wide text-graphite">Task</th>
            <th class="px-4 py-2.5 text-left text-xs font-semibold uppercase tracking-wide text-graphite">Status</th>
            <th class="px-4 py-2.5 text-left text-xs font-semibold uppercase tracking-wide text-graphite">Last run</th>
            <th class="px-4 py-2.5 text-right text-xs font-semibold uppercase tracking-wide text-graphite">Rows</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr
            v-for="row in rows"
            :key="row.key"
            class="transition-colors hover:bg-slate-50"
          >
            <td class="px-4 py-3 font-medium text-ink">{{ row.label }}</td>
            <td class="px-4 py-3">
              <div v-if="loading && !data" class="h-4 w-20 animate-pulse rounded bg-slate-100" />
              <div v-else class="flex items-center gap-1.5">
                <component
                  :is="statusIcon(row.entry)"
                  class="size-3.5"
                  :class="statusColor(row.entry)"
                />
                <span :class="statusColor(row.entry)" class="text-xs font-medium capitalize">
                  {{ row.entry?.status ?? "never run" }}
                </span>
              </div>
            </td>
            <td class="px-4 py-3 text-xs text-graphite">
              <span v-if="row.entry">{{ fmt(row.entry.ran_at) }}</span>
              <span v-else class="text-slate-300">—</span>
            </td>
            <td class="px-4 py-3 text-right font-mono text-xs text-graphite">
              <span v-if="row.entry">{{ row.entry.rows_processed.toLocaleString() }}</span>
              <span v-else class="text-slate-300">—</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Recent failures -->
    <div v-if="data?.recent_failures?.length" class="rounded-xl border border-rose-200 bg-rose-50 p-4">
      <p class="mb-2.5 text-xs font-semibold text-rose-800">Recent failures (last 7 days)</p>
      <ul class="space-y-1.5">
        <li
          v-for="f in data.recent_failures"
          :key="f.ran_at + f.task"
          class="flex items-start gap-2 text-xs text-rose-700"
        >
          <XCircle class="mt-0.5 size-3.5 shrink-0 text-rose-500" />
          <span>
            <span class="font-semibold">{{ TASK_LABELS[f.task] ?? f.task }}</span>
            — {{ fmt(f.ran_at) }}
            <span v-if="f.error_message" class="ml-1 font-mono text-rose-600">{{ f.error_message }}</span>
          </span>
        </li>
      </ul>
    </div>

    <p v-else-if="data && !data.recent_failures?.length" class="text-center text-xs text-graphite py-2">
      No failures in the last 7 days.
    </p>

  </div>
</template>

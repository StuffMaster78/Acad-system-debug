<template>
  <div class="space-y-6 px-4 py-6">

    <!-- Header -->
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-xl font-bold text-ink">Event System</h1>
        <p class="mt-0.5 text-sm text-graphite">
          Outbox health, delivery failures, and event replay.
        </p>
      </div>
      <button
        class="focus-ring inline-flex h-9 items-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold"
        :disabled="loading"
        @click="refresh"
      >
        <RefreshCw class="h-4 w-4" :class="{ 'animate-spin': loading }" />
        Refresh
      </button>
    </div>

    <!-- Error banner -->
    <div v-if="error" class="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
      {{ error }}
    </div>

    <!-- Metrics strip -->
    <div v-if="metricsLoading" class="grid grid-cols-2 gap-4 sm:grid-cols-4 lg:grid-cols-7">
      <div v-for="n in 7" :key="n" class="h-20 animate-pulse rounded-xl bg-slate-100" />
    </div>

    <div v-else-if="metrics" class="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:grid-cols-7">
      <div class="rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
        <p class="text-xs font-semibold uppercase text-graphite">Total</p>
        <p class="mt-1 text-2xl font-bold text-ink">{{ metrics.total_events.toLocaleString() }}</p>
      </div>
      <div class="rounded-xl border border-emerald-200 bg-emerald-50 p-3 shadow-sm">
        <p class="text-xs font-semibold uppercase text-emerald-700">Processed</p>
        <p class="mt-1 text-2xl font-bold text-emerald-800">{{ metrics.processed.toLocaleString() }}</p>
      </div>
      <div class="rounded-xl border border-amber-200 bg-amber-50 p-3 shadow-sm">
        <p class="text-xs font-semibold uppercase text-amber-700">Pending</p>
        <p class="mt-1 text-2xl font-bold text-amber-800">{{ pendingCount.toLocaleString() }}</p>
      </div>
      <div class="rounded-xl border border-red-200 bg-red-50 p-3 shadow-sm">
        <p class="text-xs font-semibold uppercase text-red-700">Failed</p>
        <p class="mt-1 text-2xl font-bold text-red-800">{{ metrics.failed.toLocaleString() }}</p>
      </div>
      <div class="rounded-xl border border-red-300 bg-red-100 p-3 shadow-sm">
        <p class="text-xs font-semibold uppercase text-red-800">Dead Letter</p>
        <p class="mt-1 text-2xl font-bold text-red-900">{{ metrics.dead_letter.toLocaleString() }}</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
        <p class="text-xs font-semibold uppercase text-graphite">Success rate</p>
        <p class="mt-1 text-2xl font-bold text-ink">{{ pct(metrics.processing_rate) }}%</p>
      </div>
      <div class="rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
        <p class="text-xs font-semibold uppercase text-graphite">Failure rate</p>
        <p class="mt-1 text-2xl font-bold" :class="metrics.failure_rate > 0.05 ? 'text-red-700' : 'text-ink'">
          {{ pct(metrics.failure_rate) }}%
        </p>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap items-center gap-2">
      <select
        v-model="filterStatus"
        class="focus-ring h-9 rounded-md border border-slate-200 bg-white px-3 text-sm"
      >
        <option value="">All statuses</option>
        <option value="pending">Pending</option>
        <option value="processing">Processing</option>
        <option value="processed">Processed</option>
        <option value="failed">Failed</option>
        <option value="ignored">Ignored</option>
        <option value="dead_letter">Dead Letter</option>
      </select>
      <input
        v-model="filterDomain"
        placeholder="Filter by domain…"
        class="focus-ring h-9 rounded-md border border-slate-200 bg-white px-3 text-sm"
      />
      <input
        v-model="filterType"
        placeholder="Filter by event type…"
        class="focus-ring h-9 rounded-md border border-slate-200 bg-white px-3 text-sm"
      />
      <span class="ml-auto text-xs text-graphite">{{ filtered.length }} event{{ filtered.length !== 1 ? 's' : '' }}</span>
    </div>

    <!-- Event table -->
    <div v-if="loading" class="space-y-2">
      <div v-for="n in 8" :key="n" class="h-12 animate-pulse rounded-lg bg-slate-100" />
    </div>

    <div v-else-if="filtered.length === 0" class="rounded-xl border border-slate-200 bg-white py-16 text-center">
      <Inbox class="mx-auto h-8 w-8 text-slate-300" />
      <p class="mt-2 text-sm text-graphite">No events match these filters.</p>
    </div>

    <div v-else class="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <table class="w-full text-sm">
        <thead class="border-b border-slate-100 bg-slate-50">
          <tr>
            <th class="px-4 py-2.5 text-left text-xs font-semibold uppercase text-graphite">Status</th>
            <th class="px-4 py-2.5 text-left text-xs font-semibold uppercase text-graphite">Domain</th>
            <th class="px-4 py-2.5 text-left text-xs font-semibold uppercase text-graphite">Event type</th>
            <th class="px-4 py-2.5 text-left text-xs font-semibold uppercase text-graphite">Attempts</th>
            <th class="px-4 py-2.5 text-left text-xs font-semibold uppercase text-graphite">Created</th>
            <th class="px-4 py-2.5 text-left text-xs font-semibold uppercase text-graphite">Last error</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <template v-for="ev in filtered" :key="ev.id">
            <tr
              class="cursor-pointer transition-colors hover:bg-slate-50"
              :class="{ 'bg-blue-50 hover:bg-blue-50': selectedId === ev.id }"
              @click="toggleDetail(ev.id)"
            >
              <td class="px-4 py-3">
                <span :class="statusBadge(ev.status)" class="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-semibold">
                  {{ ev.status.replace('_', ' ') }}
                </span>
              </td>
              <td class="px-4 py-3 font-mono text-xs text-graphite">{{ ev.domain }}</td>
              <td class="px-4 py-3 font-mono text-xs text-ink">{{ ev.event_type }}</td>
              <td class="px-4 py-3 text-center text-xs">
                <span :class="ev.attempts >= ev.max_attempts ? 'text-red-700 font-semibold' : 'text-graphite'">
                  {{ ev.attempts }}/{{ ev.max_attempts }}
                </span>
              </td>
              <td class="px-4 py-3 text-xs text-graphite whitespace-nowrap">{{ fmtDate(ev.created_at) }}</td>
              <td class="max-w-xs truncate px-4 py-3 text-xs text-red-600">{{ ev.last_error ?? '—' }}</td>
            </tr>

            <!-- Expanded detail panel -->
            <tr v-if="selectedId === ev.id" class="bg-blue-50">
              <td colspan="6" class="px-4 pb-5 pt-2">
                <div v-if="detailLoading" class="h-24 animate-pulse rounded-lg bg-slate-200" />
                <div v-else-if="detail" class="grid gap-4 lg:grid-cols-2">

                  <!-- Left: payload + actions -->
                  <div class="space-y-3">
                    <div class="flex items-center gap-3">
                      <p class="text-xs font-semibold uppercase text-graphite">Event ID</p>
                      <code class="rounded bg-slate-100 px-1.5 py-0.5 text-xs text-ink">{{ ev.id }}</code>
                    </div>
                    <div v-if="ev.correlation_id" class="flex items-center gap-3">
                      <p class="text-xs font-semibold uppercase text-graphite">Correlation</p>
                      <code class="rounded bg-slate-100 px-1.5 py-0.5 text-xs text-ink">{{ ev.correlation_id }}</code>
                    </div>

                    <div>
                      <p class="mb-1 text-xs font-semibold uppercase text-graphite">Payload</p>
                      <pre class="max-h-48 overflow-auto rounded-lg bg-slate-900 p-3 text-xs text-emerald-300">{{ JSON.stringify(detail.event.payload, null, 2) }}</pre>
                    </div>

                    <div v-if="ev.last_error" class="rounded-lg border border-red-200 bg-red-50 p-3">
                      <p class="mb-1 text-xs font-semibold text-red-700">Last error</p>
                      <p class="text-xs text-red-600">{{ ev.last_error }}</p>
                    </div>

                    <!-- Actions -->
                    <div class="flex gap-2 pt-1">
                      <button
                        v-if="ev.status === 'failed' || ev.status === 'dead_letter'"
                        class="focus-ring inline-flex h-8 items-center gap-1.5 rounded-md bg-amber-500 px-3 text-xs font-semibold text-white hover:bg-amber-600 disabled:opacity-50"
                        :disabled="replaying"
                        @click.stop="replayEvent(ev.id)"
                      >
                        <RotateCcw class="h-3.5 w-3.5" :class="{ 'animate-spin': replaying }" />
                        Replay
                      </button>
                      <button
                        class="focus-ring inline-flex h-8 items-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold text-ink hover:bg-slate-50"
                        @click.stop="loadCorrelation(ev.correlation_id)"
                        :disabled="!ev.correlation_id"
                      >
                        <GitBranch class="h-3.5 w-3.5" />
                        Correlation chain
                      </button>
                    </div>

                    <p v-if="replayMsg" class="text-xs" :class="replayMsg.startsWith('Error') ? 'text-red-600' : 'text-emerald-600'">
                      {{ replayMsg }}
                    </p>
                  </div>

                  <!-- Right: timeline + failures -->
                  <div class="space-y-3">
                    <!-- Timeline -->
                    <div v-if="detail.timeline.length">
                      <p class="mb-2 text-xs font-semibold uppercase text-graphite">Timeline</p>
                      <ol class="relative space-y-2 border-l border-slate-200 pl-4">
                        <li v-for="(t, i) in detail.timeline" :key="i" class="relative">
                          <span class="absolute -left-[18px] mt-0.5 h-2.5 w-2.5 rounded-full border-2 border-white"
                            :class="t.event_status === 'processed' ? 'bg-emerald-500' : t.event_status === 'failed' ? 'bg-red-500' : 'bg-slate-400'" />
                          <p class="text-xs font-medium text-ink">{{ t.stage }}</p>
                          <p class="text-xs text-graphite">
                            {{ t.event_status }}
                            <span v-if="t.duration_ms"> · {{ t.duration_ms }}ms</span>
                            · {{ fmtDate(t.created_at) }}
                          </p>
                        </li>
                      </ol>
                    </div>
                    <p v-else class="text-xs text-graphite">No timeline entries.</p>

                    <!-- Failures -->
                    <div v-if="failures.length">
                      <p class="mb-2 text-xs font-semibold uppercase text-graphite">Failure history</p>
                      <div v-for="(f, i) in failures" :key="i" class="mb-1.5 rounded-lg border border-red-100 bg-red-50 p-2.5">
                        <p class="text-xs font-medium text-red-700">Attempt {{ f.attempts }} · {{ fmtDate(f.updated_at ?? '') }}</p>
                        <p class="mt-0.5 text-xs text-red-600">{{ f.last_error ?? 'No error message' }}</p>
                      </div>
                    </div>

                    <!-- Correlation chain -->
                    <div v-if="correlationTimeline.length">
                      <p class="mb-2 text-xs font-semibold uppercase text-graphite">
                        Correlation chain ({{ correlationTimeline.length }})
                      </p>
                      <ol class="relative space-y-2 border-l border-purple-200 pl-4">
                        <li v-for="(t, i) in correlationTimeline" :key="i" class="relative">
                          <span class="absolute -left-[18px] mt-0.5 h-2.5 w-2.5 rounded-full border-2 border-white bg-purple-400" />
                          <p class="text-xs font-medium text-ink">{{ t.stage }}</p>
                          <p class="text-xs text-graphite">{{ t.event_status }} · {{ fmtDate(t.created_at) }}</p>
                        </li>
                      </ol>
                    </div>
                  </div>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { RefreshCw, RotateCcw, GitBranch, Inbox } from "@lucide/vue";
import {
  eventSystemApi,
  type OutboxEvent,
  type EventMetrics,
  type EventDetail,
  type EventFailure,
  type EventTimelineEntry,
} from "@/api/eventSystem";

const error = ref("");

// ── State ────────────────────────────────────────────────────────────────────
const events = ref<OutboxEvent[]>([]);
const metrics = ref<EventMetrics | null>(null);
const loading = ref(false);
const metricsLoading = ref(false);

const filterStatus = ref("");
const filterDomain = ref("");
const filterType = ref("");

const selectedId = ref<string | null>(null);
const detail = ref<EventDetail | null>(null);
const failures = ref<EventFailure[]>([]);
const correlationTimeline = ref<EventTimelineEntry[]>([]);
const detailLoading = ref(false);
const replaying = ref(false);
const replayMsg = ref("");

// ── Computed ─────────────────────────────────────────────────────────────────
const pendingCount = computed(() => {
  if (!metrics.value) return 0;
  const m = metrics.value;
  return Math.max(0, m.total_events - m.processed - m.failed - m.dead_letter - m.ignored);
});

const filtered = computed(() => {
  let list = events.value;
  if (filterStatus.value) list = list.filter((e) => e.status === filterStatus.value);
  if (filterDomain.value) list = list.filter((e) => e.domain.includes(filterDomain.value));
  if (filterType.value) list = list.filter((e) => e.event_type.includes(filterType.value));
  return list;
});

// ── Data loading ──────────────────────────────────────────────────────────────
async function loadMetrics() {
  metricsLoading.value = true;
  try {
    const res = await eventSystemApi.metrics();
    metrics.value = res.data;
  } catch {
    // metrics are optional — fail silently
  } finally {
    metricsLoading.value = false;
  }
}

async function loadEvents() {
  loading.value = true;
  try {
    const res = await eventSystemApi.list();
    events.value = res.data;
  } catch {
    error.value = "Failed to load events.";
  } finally {
    loading.value = false;
  }
}

async function refresh() {
  selectedId.value = null;
  error.value = "";
  await Promise.all([loadMetrics(), loadEvents()]);
}

// ── Detail panel ──────────────────────────────────────────────────────────────
async function toggleDetail(id: string) {
  if (selectedId.value === id) {
    selectedId.value = null;
    detail.value = null;
    failures.value = [];
    correlationTimeline.value = [];
    replayMsg.value = "";
    return;
  }
  selectedId.value = id;
  detail.value = null;
  failures.value = [];
  correlationTimeline.value = [];
  replayMsg.value = "";
  detailLoading.value = true;
  try {
    const [detailRes, failRes] = await Promise.all([
      eventSystemApi.detail(id),
      eventSystemApi.failures(id),
    ]);
    detail.value = detailRes.data;
    failures.value = failRes.data;
  } catch {
    error.value = "Failed to load event detail.";
  } finally {
    detailLoading.value = false;
  }
}

async function loadCorrelation(correlationId: string | null) {
  if (!correlationId) return;
  try {
    const res = await eventSystemApi.timeline({ correlation_id: correlationId });
    correlationTimeline.value = res.data;
  } catch {
    error.value = "Failed to load correlation chain.";
  }
}

async function replayEvent(id: string) {
  replaying.value = true;
  replayMsg.value = "";
  try {
    await eventSystemApi.replay(id);
    replayMsg.value = "Replayed — event re-queued.";
    await loadEvents();
  } catch {
    replayMsg.value = "Error: replay failed.";
  } finally {
    replaying.value = false;
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function statusBadge(status: string): string {
  const map: Record<string, string> = {
    pending:     "bg-slate-100 text-slate-700",
    processing:  "bg-blue-100 text-blue-700",
    processed:   "bg-emerald-100 text-emerald-700",
    failed:      "bg-red-100 text-red-700",
    ignored:     "bg-slate-100 text-slate-500",
    dead_letter: "bg-red-200 text-red-900",
  };
  return map[status] ?? "bg-slate-100 text-slate-700";
}

function pct(rate: number): string {
  return (rate * 100).toFixed(1);
}

function fmtDate(iso: string): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleString(undefined, {
    month: "short", day: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

onMounted(refresh);
</script>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import {
  ChevronDown,
  ChevronRight,
  Loader2,
  RefreshCw,
  Search,
  ShieldAlert,
} from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { auditLogsApi, type AuditEvent, type AuditEventFilters } from "@/api/auditLogs";

const events = ref<AuditEvent[]>([]);
const loading = ref(false);
const loadingMore = ref(false);
const error = ref("");
const nextCursor = ref<string | null>(null);
const expandedId = ref<string | null>(null);

const filters = ref<AuditEventFilters>({
  search: "",
  severity: "",
  status: "",
  service_name: "",
  occurred_after: "",
  occurred_before: "",
  page_size: 50,
});

const SEVERITIES = ["", "info", "warning", "error", "critical"];
const STATUSES = ["", "pending", "processed", "failed", "dead_letter"];

async function fetchEvents(reset = true) {
  if (reset) {
    loading.value = true;
    events.value = [];
    nextCursor.value = null;
    error.value = "";
  } else {
    loadingMore.value = true;
  }

  try {
    const params: AuditEventFilters = { ...filters.value };
    if (!params.search) delete params.search;
    if (!params.severity) delete params.severity;
    if (!params.status) delete params.status;
    if (!params.service_name) delete params.service_name;
    if (!params.occurred_after) delete params.occurred_after;
    if (!params.occurred_before) delete params.occurred_before;

    const { data } = reset
      ? await auditLogsApi.events(params)
      : await auditLogsApi.eventsFromUrl(nextCursor.value!);

    if (reset) {
      events.value = data.results;
    } else {
      events.value.push(...data.results);
    }
    nextCursor.value = data.next;
  } catch (err: unknown) {
    const detail = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    error.value = detail ?? "Could not load audit events.";
  } finally {
    loading.value = false;
    loadingMore.value = false;
  }
}

function toggleExpand(id: string) {
  expandedId.value = expandedId.value === id ? null : id;
}

function severityTone(severity: string): "success" | "warning" | "danger" | "neutral" {
  switch (severity?.toLowerCase()) {
    case "critical": return "danger";
    case "error": return "danger";
    case "warning": return "warning";
    case "info": return "neutral";
    default: return "neutral";
  }
}

function statusTone(status: string): "success" | "warning" | "danger" | "neutral" {
  switch (status?.toLowerCase()) {
    case "processed": return "success";
    case "failed":
    case "dead_letter": return "danger";
    case "pending": return "warning";
    default: return "neutral";
  }
}

function formatTs(value: string) {
  return new Intl.DateTimeFormat("en", {
    dateStyle: "short",
    timeStyle: "medium",
  }).format(new Date(value));
}

let debounceTimer: ReturnType<typeof setTimeout>;
watch(
  () => filters.value.search,
  () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => fetchEvents(), 400);
  },
);

onMounted(() => fetchEvents());
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Superadmin</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Audit Log</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Platform-wide security and operational audit trail. All events, actor IDs, and processing status.
        </p>
      </div>
      <button
        class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold disabled:opacity-60"
        type="button"
        :disabled="loading"
        @click="fetchEvents()"
      >
        <Loader2 v-if="loading" class="h-4 w-4 animate-spin" />
        <RefreshCw v-else class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <!-- Filters -->
    <section class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <label class="relative col-span-full xl:col-span-2">
        <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-graphite" />
        <input
          v-model="filters.search"
          type="search"
          class="focus-ring h-10 w-full rounded-md border border-slate-200 bg-white pl-9 pr-3 text-sm"
          placeholder="Search action, object type, correlation ID…"
        />
      </label>

      <select
        v-model="filters.severity"
        class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm"
        @change="fetchEvents()"
      >
        <option value="">All severities</option>
        <option v-for="s in SEVERITIES.slice(1)" :key="s" :value="s">{{ s.charAt(0).toUpperCase() + s.slice(1) }}</option>
      </select>

      <select
        v-model="filters.status"
        class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm"
        @change="fetchEvents()"
      >
        <option value="">All statuses</option>
        <option v-for="s in STATUSES.slice(1)" :key="s" :value="s">{{ s.replace(/_/g, " ").charAt(0).toUpperCase() + s.replace(/_/g, " ").slice(1) }}</option>
      </select>

      <label class="block">
        <input
          v-model="filters.service_name"
          type="text"
          class="focus-ring h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
          placeholder="Filter by service"
          @change="fetchEvents()"
        />
      </label>

      <label class="block">
        <span class="text-xs font-semibold text-graphite">From</span>
        <input
          v-model="filters.occurred_after"
          type="datetime-local"
          class="focus-ring mt-0.5 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
          @change="fetchEvents()"
        />
      </label>

      <label class="block">
        <span class="text-xs font-semibold text-graphite">To</span>
        <input
          v-model="filters.occurred_before"
          type="datetime-local"
          class="focus-ring mt-0.5 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
          @change="fetchEvents()"
        />
      </label>
    </section>

    <p v-if="error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ error }}
    </p>

    <!-- Events table -->
    <div class="rounded-lg border border-slate-200 bg-white shadow-panel">
      <div v-if="loading" class="space-y-px">
        <div
          v-for="n in 8"
          :key="n"
          class="animate-pulse border-b border-slate-100 px-5 py-3.5"
        >
          <div class="flex gap-4">
            <div class="h-3 w-32 rounded bg-slate-200" />
            <div class="h-3 w-48 rounded bg-slate-100" />
            <div class="h-3 w-24 rounded bg-slate-100" />
          </div>
        </div>
      </div>

      <EmptyState
        v-else-if="!events.length"
        :icon="ShieldAlert"
        title="No audit events"
        message="No events match the current filters."
      />

      <div v-else>
        <div class="grid grid-cols-[auto_1fr_auto_auto_auto] gap-0 divide-y divide-slate-100 overflow-x-auto">
          <!-- Header -->
          <div class="col-span-full grid grid-cols-[auto_1fr_auto_auto_auto] border-b border-slate-200 bg-slate-50 px-5 py-3 text-xs font-semibold uppercase tracking-wide text-graphite">
            <span class="w-6" />
            <span>Action / Object</span>
            <span class="px-4">Severity</span>
            <span class="px-4">Status</span>
            <span class="pl-4 text-right">Occurred</span>
          </div>

          <template v-for="ev in events" :key="ev.id">
            <!-- Row -->
            <button
              class="focus-ring col-span-full grid w-full grid-cols-[auto_1fr_auto_auto_auto] items-center gap-0 px-5 py-3.5 text-left transition-colors hover:bg-slate-50"
              type="button"
              @click="toggleExpand(ev.id)"
            >
              <span class="mr-2 shrink-0">
                <ChevronDown v-if="expandedId === ev.id" class="h-3.5 w-3.5 text-graphite" />
                <ChevronRight v-else class="h-3.5 w-3.5 text-graphite" />
              </span>
              <span class="min-w-0">
                <p class="truncate font-mono text-xs font-semibold text-ink">{{ ev.action }}</p>
                <p class="mt-0.5 truncate text-xs text-graphite">
                  <span v-if="ev.object_type">{{ ev.object_type }}</span>
                  <span v-if="ev.object_id"> #{{ ev.object_id }}</span>
                  <span v-if="ev.actor_id"> · actor {{ ev.actor_id }}</span>
                  <span v-if="ev.service_name"> · {{ ev.service_name }}</span>
                </p>
              </span>
              <span class="px-4">
                <StatusPill :label="ev.severity || 'info'" :tone="severityTone(ev.severity)" />
              </span>
              <span class="px-4">
                <StatusPill :label="ev.status" :tone="statusTone(ev.status)" />
              </span>
              <span class="pl-4 text-right font-mono text-xs text-graphite">{{ formatTs(ev.occurred_at) }}</span>
            </button>

            <!-- Expanded detail -->
            <div
              v-if="expandedId === ev.id"
              class="col-span-full border-t border-dashed border-slate-200 bg-slate-50 px-8 py-4"
            >
              <div class="grid gap-y-2 gap-x-6 text-xs sm:grid-cols-2 lg:grid-cols-3">
                <div v-if="ev.correlation_id">
                  <p class="font-semibold uppercase text-graphite">Correlation ID</p>
                  <p class="mt-0.5 font-mono text-ink break-all">{{ ev.correlation_id }}</p>
                </div>
                <div v-if="ev.span_id">
                  <p class="font-semibold uppercase text-graphite">Span ID</p>
                  <p class="mt-0.5 font-mono text-ink break-all">{{ ev.span_id }}</p>
                </div>
                <div v-if="ev.processed_at">
                  <p class="font-semibold uppercase text-graphite">Processed at</p>
                  <p class="mt-0.5 text-ink">{{ formatTs(ev.processed_at) }}</p>
                </div>
                <div>
                  <p class="font-semibold uppercase text-graphite">Processing attempts</p>
                  <p class="mt-0.5 text-ink">{{ ev.processing_attempts }}</p>
                </div>
                <div v-if="ev.is_sensitive">
                  <p class="font-semibold uppercase text-graphite">Sensitivity</p>
                  <p class="mt-0.5 text-ink">{{ ev.sensitivity_level ?? "sensitive" }}</p>
                </div>
                <div v-if="ev.ip_address">
                  <p class="font-semibold uppercase text-graphite">IP Address</p>
                  <p class="mt-0.5 font-mono text-ink">{{ ev.ip_address }}</p>
                </div>
                <div v-if="ev.user_agent">
                  <p class="font-semibold uppercase text-graphite">User Agent</p>
                  <p class="mt-0.5 text-ink break-all">{{ ev.user_agent }}</p>
                </div>
                <div v-if="ev.last_error">
                  <p class="font-semibold uppercase text-graphite">Last Error</p>
                  <p class="mt-0.5 text-berry break-all">{{ ev.last_error }}</p>
                </div>
              </div>
              <div v-if="ev.metadata && Object.keys(ev.metadata).length" class="mt-4">
                <p class="text-xs font-semibold uppercase text-graphite">Metadata</p>
                <pre class="mt-1 max-h-48 overflow-auto rounded-md bg-slate-800 p-3 text-xs text-slate-100">{{ JSON.stringify(ev.metadata, null, 2) }}</pre>
              </div>
            </div>
          </template>
        </div>

        <!-- Load more -->
        <div v-if="nextCursor" class="border-t border-slate-100 px-5 py-4 text-center">
          <button
            class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-200 px-4 py-2 text-sm font-semibold text-ink hover:bg-slate-50 disabled:opacity-60"
            type="button"
            :disabled="loadingMore"
            @click="fetchEvents(false)"
          >
            <Loader2 v-if="loadingMore" class="h-4 w-4 animate-spin" />
            Load more events
          </button>
        </div>

        <div class="border-t border-slate-100 px-5 py-3 text-right text-xs text-slate-400">
          {{ events.length }} events loaded
        </div>
      </div>
    </div>
  </div>
</template>

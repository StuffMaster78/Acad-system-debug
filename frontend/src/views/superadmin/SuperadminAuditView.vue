<script setup lang="ts">
import { onMounted, watch } from "vue";
import { ChevronDown, ChevronRight, Download, Loader2, RefreshCw, Search, Shield } from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import { useAuditLogStore, humanAction, sensitiveActionBadge } from "@/stores/auditLog";

const store = useAuditLogStore();

const SEVERITIES = ["info", "warning", "critical", "error"];
const SERVICES   = ["auth", "orders", "payments", "wallets", "disputes", "staffing", "config"];

const expandedId = ref<string | null>(null);

function toggleExpand(id: string) {
  expandedId.value = expandedId.value === id ? null : id;
}

function severityTone(s: string): "success" | "warning" | "danger" | "neutral" {
  return s === "critical" || s === "error" ? "danger" : s === "warning" ? "warning" : "neutral";
}
function statusTone(s: string): "success" | "warning" | "danger" | "neutral" {
  return s === "processed" ? "success" : s === "failed" ? "danger" : s === "pending" ? "warning" : "neutral";
}
function fmtTs(v: string) {
  return new Intl.DateTimeFormat("en", { dateStyle: "short", timeStyle: "medium" }).format(new Date(v));
}
function rowClass(ev: { severity: string; is_sensitive: boolean }) {
  if (ev.severity === "critical") return "bg-red-50/60";
  if (ev.severity === "warning" || ev.is_sensitive) return "bg-amber-50/40";
  return "";
}

let debounce: ReturnType<typeof setTimeout>;
watch(() => store.filters.search, () => {
  clearTimeout(debounce);
  debounce = setTimeout(() => store.load(), 400);
});

function applyFilter() { store.load(); }

function downloadExport() {
  window.open(store.exportUrl(), "_blank");
}

import { ref } from "vue";

onMounted(() => store.load());
</script>

<template>
  <div class="space-y-4">
    <!-- Header -->
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Superadmin</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Audit Log</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Platform-wide security and operational audit trail. Sensitive events are highlighted.
        </p>
      </div>
      <div class="flex items-center gap-2">
        <button
          class="focus-ring inline-flex h-9 items-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold"
          type="button"
          @click="downloadExport"
        >
          <Download class="h-4 w-4" /> Export CSV
        </button>
        <button
          class="focus-ring inline-flex h-9 items-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
          type="button"
          :disabled="store.isLoading"
          @click="store.load()"
        >
          <Loader2 v-if="store.isLoading" class="h-4 w-4 animate-spin" />
          <RefreshCw v-else class="h-4 w-4" />
          Refresh
        </button>
      </div>
    </section>

    <!-- Filters -->
    <section class="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
      <label class="relative col-span-full xl:col-span-2">
        <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-graphite" />
        <input v-model="store.filters.search" type="search"
          class="focus-ring h-10 w-full rounded-md border border-slate-200 bg-white pl-9 pr-3 text-sm"
          placeholder="Search action, object, correlation ID…" />
      </label>
      <select v-model="store.filters.severity" class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm" @change="applyFilter">
        <option value="">All severities</option>
        <option v-for="s in SEVERITIES" :key="s" :value="s">{{ s.charAt(0).toUpperCase() + s.slice(1) }}</option>
      </select>
      <select v-model="store.filters.service_name" class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm" @change="applyFilter">
        <option value="">All services</option>
        <option v-for="s in SERVICES" :key="s" :value="s">{{ s }}</option>
      </select>
      <select v-model="(store.filters as any).is_sensitive" class="focus-ring h-10 rounded-md border border-slate-200 bg-white px-3 text-sm" @change="applyFilter">
        <option :value="undefined">All events</option>
        <option :value="true">Sensitive only</option>
        <option :value="false">Non-sensitive only</option>
      </select>
      <label class="block">
        <span class="text-xs font-semibold text-graphite">From</span>
        <input v-model="store.filters.occurred_after" type="datetime-local"
          class="focus-ring mt-0.5 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm" @change="applyFilter" />
      </label>
      <label class="block">
        <span class="text-xs font-semibold text-graphite">To</span>
        <input v-model="store.filters.occurred_before" type="datetime-local"
          class="focus-ring mt-0.5 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm" @change="applyFilter" />
      </label>
    </section>

    <p v-if="store.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">{{ store.error }}</p>

    <!-- Events table -->
    <div class="rounded-lg border border-slate-200 bg-white">
      <div v-if="store.isLoading && !store.events.length" class="space-y-px">
        <div v-for="n in 8" :key="n" class="animate-pulse border-b border-slate-100 px-5 py-3">
          <div class="flex gap-4">
            <div class="h-3 w-32 rounded bg-slate-200" />
            <div class="h-3 w-48 rounded bg-slate-100" />
            <div class="h-3 w-24 rounded bg-slate-100" />
          </div>
        </div>
      </div>

      <EmptyState v-else-if="!store.events.length" :icon="Shield" title="No audit events" message="No events match the current filters." />

      <div v-else>
        <div class="divide-y divide-slate-100 overflow-x-auto">
          <!-- Header -->
          <div class="grid grid-cols-[auto_1fr_auto_auto_auto_auto] border-b border-slate-200 bg-slate-50 px-5 py-3 text-xs font-semibold uppercase tracking-wide text-graphite">
            <span class="w-6 mr-2" />
            <span>Action / Actor / Object</span>
            <span class="px-3">Badge</span>
            <span class="px-3">Severity</span>
            <span class="px-3">Status</span>
            <span class="pl-3 text-right">Occurred</span>
          </div>

          <template v-for="ev in store.events" :key="ev.id">
            <button
              class="grid w-full grid-cols-[auto_1fr_auto_auto_auto_auto] items-center gap-0 px-5 py-3 text-left transition-colors hover:bg-slate-50"
              :class="rowClass(ev)"
              type="button"
              @click="toggleExpand(ev.id)"
            >
              <span class="mr-2 shrink-0">
                <ChevronDown v-if="expandedId === ev.id" class="h-3.5 w-3.5 text-graphite" />
                <ChevronRight v-else class="h-3.5 w-3.5 text-graphite" />
              </span>
              <span class="min-w-0">
                <p class="truncate font-mono text-xs font-semibold text-ink">{{ humanAction(ev.action) }}</p>
                <p class="mt-0.5 truncate text-xs text-graphite">
                  <span class="font-medium">{{ store.actorName(ev.actor_id) }}</span>
                  <span v-if="ev.object_type"> · {{ ev.object_type }}</span>
                  <span v-if="ev.object_id"> #{{ ev.object_id }}</span>
                  <span v-if="ev.service_name" class="ml-1 rounded bg-slate-100 px-1 py-0.5 font-mono text-[10px]">{{ ev.service_name }}</span>
                </p>
              </span>
              <span class="px-3">
                <span
                  v-if="sensitiveActionBadge(ev.action)"
                  class="inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-[10px] font-semibold"
                  :class="sensitiveActionBadge(ev.action)!.color"
                >
                  <Shield class="h-2.5 w-2.5" />
                  {{ sensitiveActionBadge(ev.action)!.label }}
                </span>
              </span>
              <span class="px-3"><StatusPill :label="ev.severity || 'info'" :tone="severityTone(ev.severity)" /></span>
              <span class="px-3"><StatusPill :label="ev.status" :tone="statusTone(ev.status)" /></span>
              <span class="pl-3 text-right font-mono text-xs text-graphite whitespace-nowrap">{{ fmtTs(ev.occurred_at) }}</span>
            </button>

            <!-- Expanded detail -->
            <div v-if="expandedId === ev.id" class="border-t border-dashed border-slate-200 bg-slate-50 px-8 py-4">
              <div class="grid gap-y-3 gap-x-6 text-xs sm:grid-cols-2 lg:grid-cols-4">
                <div>
                  <p class="font-semibold uppercase text-graphite">Actor</p>
                  <p class="mt-0.5 text-ink">{{ store.actorName(ev.actor_id) }}
                    <span v-if="ev.actor_id" class="ml-1 text-graphite">(#{{ ev.actor_id }})</span>
                  </p>
                  <p v-if="ev.metadata?.actor_role" class="text-graphite capitalize">{{ ev.metadata.actor_role }}</p>
                </div>
                <div v-if="ev.correlation_id">
                  <p class="font-semibold uppercase text-graphite">Correlation ID</p>
                  <p class="mt-0.5 font-mono text-ink break-all text-[10px]">{{ ev.correlation_id }}</p>
                </div>
                <div v-if="ev.ip_address">
                  <p class="font-semibold uppercase text-graphite">IP Address</p>
                  <p class="mt-0.5 font-mono text-ink">{{ ev.ip_address }}</p>
                </div>
                <div v-if="ev.is_sensitive">
                  <p class="font-semibold uppercase text-graphite">Sensitivity</p>
                  <p class="mt-0.5 text-ink">{{ ev.sensitivity_level ?? "sensitive" }}</p>
                </div>
                <div v-if="ev.processed_at">
                  <p class="font-semibold uppercase text-graphite">Processed</p>
                  <p class="mt-0.5 text-ink">{{ fmtTs(ev.processed_at) }}</p>
                </div>
                <div v-if="ev.last_error">
                  <p class="font-semibold uppercase text-graphite">Last Error</p>
                  <p class="mt-0.5 text-red-700 break-all">{{ ev.last_error }}</p>
                </div>
              </div>

              <!-- Before / After diff -->
              <div v-if="ev.metadata?.before || ev.metadata?.after" class="mt-4 grid gap-3 sm:grid-cols-2">
                <div v-if="ev.metadata.before">
                  <p class="text-xs font-semibold uppercase text-graphite">Before</p>
                  <pre class="mt-1 max-h-32 overflow-auto rounded-md border border-red-100 bg-red-50 p-2 text-xs text-red-900">{{ JSON.stringify(ev.metadata.before, null, 2) }}</pre>
                </div>
                <div v-if="ev.metadata.after">
                  <p class="text-xs font-semibold uppercase text-graphite">After</p>
                  <pre class="mt-1 max-h-32 overflow-auto rounded-md border border-emerald-100 bg-emerald-50 p-2 text-xs text-emerald-900">{{ JSON.stringify(ev.metadata.after, null, 2) }}</pre>
                </div>
              </div>

              <!-- Metadata -->
              <div v-if="ev.metadata && Object.keys(ev.metadata).filter(k => !['before','after','actor_role','actor_display'].includes(k)).length" class="mt-3">
                <p class="text-xs font-semibold uppercase text-graphite">Metadata</p>
                <pre class="mt-1 max-h-40 overflow-auto rounded-md bg-slate-800 p-3 text-xs text-slate-100">{{ JSON.stringify(
                  Object.fromEntries(Object.entries(ev.metadata).filter(([k]) => !['before','after'].includes(k))),
                  null, 2) }}</pre>
              </div>
            </div>
          </template>
        </div>

        <!-- Load more -->
        <div v-if="store.hasMore" class="border-t border-slate-100 px-5 py-4 text-center">
          <button
            class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-200 px-4 py-2 text-sm font-semibold text-ink hover:bg-slate-50 disabled:opacity-60"
            type="button" :disabled="store.isLoading"
            @click="store.loadMore()"
          >
            <Loader2 v-if="store.isLoading" class="h-4 w-4 animate-spin" />
            Load more events
          </button>
        </div>
        <div class="border-t border-slate-100 px-5 py-3 text-right text-xs text-slate-400">
          {{ store.events.length }} events loaded
        </div>
      </div>
    </div>
  </div>
</template>

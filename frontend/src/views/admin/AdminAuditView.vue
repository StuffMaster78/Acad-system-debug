<template>
  <div class="space-y-4 px-4 py-6">
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-xl font-bold text-ink">Audit Log</h1>
        <p class="mt-0.5 text-sm text-graphite">Security and operational events for this website.</p>
      </div>
      <div class="flex items-center gap-2">
        <button
          class="focus-ring inline-flex h-9 items-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold"
          @click="store.exportUrl() && window.open(store.exportUrl(), '_blank')"
        >
          <Download class="h-4 w-4" /> Export
        </button>
        <button
          class="focus-ring inline-flex h-9 items-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
          :disabled="store.isLoading"
          @click="store.load()"
        >
          <Loader2 v-if="store.isLoading" class="h-4 w-4 animate-spin" />
          <RefreshCw v-else class="h-4 w-4" />
          Refresh
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap items-center gap-2 rounded-lg border border-slate-200 bg-white p-3">
      <div class="relative">
        <Search class="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-graphite" />
        <input v-model="store.filters.search" type="search"
          class="focus-ring h-8 w-52 rounded-md border border-slate-200 pl-8 pr-2 text-sm"
          placeholder="Search…" />
      </div>
      <select v-model="store.filters.severity" class="focus-ring h-8 rounded-md border border-slate-200 px-2 text-sm" @change="store.load()">
        <option value="">All severities</option>
        <option value="info">Info</option>
        <option value="warning">Warning</option>
        <option value="critical">Critical</option>
      </select>
      <select v-model="store.filters.service_name" class="focus-ring h-8 rounded-md border border-slate-200 px-2 text-sm" @change="store.load()">
        <option value="">All services</option>
        <option v-for="s in SERVICES" :key="s" :value="s">{{ s }}</option>
      </select>
      <select v-model="(store.filters as any).is_sensitive" class="focus-ring h-8 rounded-md border border-slate-200 px-2 text-sm" @change="store.load()">
        <option :value="undefined">All events</option>
        <option :value="true">Sensitive only</option>
      </select>
    </div>

    <p v-if="store.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">{{ store.error }}</p>

    <!-- Table -->
    <div class="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
      <table class="min-w-full text-sm">
        <thead class="border-b border-slate-100 bg-slate-50">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-semibold uppercase text-graphite w-8" />
            <th class="px-4 py-3 text-left text-xs font-semibold uppercase text-graphite">Event</th>
            <th class="px-3 py-3 text-left text-xs font-semibold uppercase text-graphite">Severity</th>
            <th class="px-3 py-3 text-left text-xs font-semibold uppercase text-graphite">Service</th>
            <th class="px-3 py-3 text-right text-xs font-semibold uppercase text-graphite">Occurred</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-if="store.isLoading && !store.events.length">
            <td colspan="5" class="px-4 py-8 text-center text-sm text-graphite">Loading…</td>
          </tr>
          <tr v-else-if="!store.events.length">
            <td colspan="5" class="px-4 py-8 text-center text-sm text-graphite">No events found.</td>
          </tr>
          <template v-for="ev in store.events" :key="ev.id">
            <tr
              class="cursor-pointer transition-colors hover:bg-slate-50"
              :class="ev.severity === 'critical' ? 'bg-red-50/40' : ev.is_sensitive ? 'bg-amber-50/30' : ''"
              @click="toggle(ev.id)"
            >
              <td class="px-4 py-3 text-graphite">
                <ChevronDown v-if="expanded === ev.id" class="h-3.5 w-3.5" />
                <ChevronRight v-else class="h-3.5 w-3.5" />
              </td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <Shield v-if="ev.is_sensitive" class="h-3.5 w-3.5 shrink-0 text-amber-500" />
                  <div>
                    <p class="font-medium text-ink">{{ humanAction(ev.action) }}</p>
                    <p class="text-xs text-graphite">
                      {{ store.actorName(ev.actor_id) }}
                      <span v-if="ev.object_type"> · {{ ev.object_type }} #{{ ev.object_id }}</span>
                    </p>
                  </div>
                </div>
              </td>
              <td class="px-3 py-3">
                <span class="rounded-full px-2 py-0.5 text-xs font-semibold capitalize"
                  :class="severityClass(ev.severity)">{{ ev.severity }}</span>
              </td>
              <td class="px-3 py-3 text-xs text-graphite">{{ ev.service_name ?? "—" }}</td>
              <td class="px-3 py-3 text-right text-xs text-graphite whitespace-nowrap">{{ fmtDate(ev.occurred_at) }}</td>
            </tr>
            <tr v-if="expanded === ev.id">
              <td colspan="5" class="border-t border-dashed border-slate-200 bg-slate-50 px-8 py-4">
                <div class="grid gap-3 text-xs sm:grid-cols-3">
                  <div>
                    <p class="font-semibold uppercase text-graphite">Actor</p>
                    <p class="mt-0.5 text-ink">{{ store.actorName(ev.actor_id) }}
                      <span v-if="ev.metadata?.actor_role" class="ml-1 text-graphite capitalize">({{ ev.metadata.actor_role }})</span>
                    </p>
                  </div>
                  <div v-if="ev.sensitivity_level">
                    <p class="font-semibold uppercase text-graphite">Sensitivity</p>
                    <p class="mt-0.5 text-ink">{{ ev.sensitivity_level }}</p>
                  </div>
                  <div v-if="ev.correlation_id">
                    <p class="font-semibold uppercase text-graphite">Correlation</p>
                    <p class="mt-0.5 font-mono text-[10px] text-ink break-all">{{ ev.correlation_id }}</p>
                  </div>
                </div>
                <div v-if="ev.metadata?.before || ev.metadata?.after" class="mt-3 grid gap-3 sm:grid-cols-2">
                  <div v-if="ev.metadata.before">
                    <p class="text-xs font-semibold uppercase text-graphite">Before</p>
                    <pre class="mt-1 rounded border border-red-100 bg-red-50 p-2 text-xs text-red-900">{{ JSON.stringify(ev.metadata.before, null, 2) }}</pre>
                  </div>
                  <div v-if="ev.metadata.after">
                    <p class="text-xs font-semibold uppercase text-graphite">After</p>
                    <pre class="mt-1 rounded border border-emerald-100 bg-emerald-50 p-2 text-xs text-emerald-900">{{ JSON.stringify(ev.metadata.after, null, 2) }}</pre>
                  </div>
                </div>
                <div v-if="ev.metadata && Object.keys(ev.metadata).filter(k => !['before','after','actor_role','actor_display'].includes(k)).length" class="mt-3">
                  <p class="text-xs font-semibold uppercase text-graphite">Metadata</p>
                  <pre class="mt-1 rounded bg-slate-800 p-2 text-xs text-slate-100">{{ JSON.stringify(
                    Object.fromEntries(Object.entries(ev.metadata).filter(([k]) => !['before','after'].includes(k))),
                    null, 2) }}</pre>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <div v-if="store.hasMore" class="text-center">
      <button
        class="focus-ring rounded-md border border-slate-200 bg-white px-4 py-2 text-sm font-semibold disabled:opacity-60"
        :disabled="store.isLoading"
        @click="store.loadMore()"
      >Load more</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ChevronDown, ChevronRight, Download, Loader2, RefreshCw, Search, Shield } from "@lucide/vue";
import { useAuditLogStore, humanAction } from "@/stores/auditLog";

const store = useAuditLogStore();
const expanded = ref<string | null>(null);
const SERVICES = ["auth", "orders", "payments", "wallets", "disputes", "staffing", "config"];

function toggle(id: string) { expanded.value = expanded.value === id ? null : id; }

function fmtDate(d: string) {
  return new Intl.DateTimeFormat("en", { dateStyle: "short", timeStyle: "short" }).format(new Date(d));
}

function severityClass(s: string) {
  return { critical: "bg-red-100 text-red-700", warning: "bg-amber-50 text-amber-700", info: "bg-slate-100 text-slate-600" }[s] ?? "bg-slate-100";
}

onMounted(() => store.load());
</script>

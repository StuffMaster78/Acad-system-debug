<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { RefreshCw, Shield } from "@lucide/vue";
import { filesApi, type AuditAccessLogEntry, type AuditDownloadLogEntry } from "@/api/files";

// ── Tabs ───────────────────────────────────────────────────────────────────
type TabId = "access" | "download";
const activeTab = ref<TabId>("access");

// ── Access log ─────────────────────────────────────────────────────────────
const accessLog = ref<AuditAccessLogEntry[]>([]);
const accessLoading = ref(false);
const accessError = ref("");
const accessSearch = ref("");

const filteredAccessLog = computed(() => {
  const q = accessSearch.value.toLowerCase().trim();
  if (!q) return accessLog.value;
  return accessLog.value.filter(
    (e) =>
      e.file_name.toLowerCase().includes(q) ||
      (e.user_email ?? "").toLowerCase().includes(q),
  );
});

async function loadAccessLog() {
  accessLoading.value = true;
  accessError.value = "";
  try {
    const { data } = await filesApi.auditAccessLog();
    accessLog.value = data;
  } catch {
    accessError.value = "Failed to load access log.";
  } finally {
    accessLoading.value = false;
  }
}

// ── Download log ───────────────────────────────────────────────────────────
const downloadLog = ref<AuditDownloadLogEntry[]>([]);
const downloadLoading = ref(false);
const downloadError = ref("");
const downloadSearch = ref("");

const filteredDownloadLog = computed(() => {
  const q = downloadSearch.value.toLowerCase().trim();
  if (!q) return downloadLog.value;
  return downloadLog.value.filter(
    (e) =>
      e.file_name.toLowerCase().includes(q) ||
      (e.downloaded_by_email ?? "").toLowerCase().includes(q),
  );
});

async function loadDownloadLog() {
  downloadLoading.value = true;
  downloadError.value = "";
  try {
    const { data } = await filesApi.auditDownloadLog();
    downloadLog.value = data;
  } catch {
    downloadError.value = "Failed to load download log.";
  } finally {
    downloadLoading.value = false;
  }
}

// ── Helpers ────────────────────────────────────────────────────────────────
function fmtDate(iso: string) {
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(iso));
}

function bytesLabel(bytes: number) {
  if (!bytes) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1048576).toFixed(1)} MB`;
}

function truncate(str: string, max = 60) {
  return str.length > max ? str.slice(0, max) + "…" : str;
}

function switchTab(tab: TabId) {
  activeTab.value = tab;
  if (tab === "access" && !accessLog.value.length && !accessLoading.value) loadAccessLog();
  if (tab === "download" && !downloadLog.value.length && !downloadLoading.value) loadDownloadLog();
}

onMounted(() => {
  loadAccessLog();
});
</script>

<template>
  <div class="space-y-4">
    <!-- Page header -->
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <div class="flex items-center gap-2">
          <Shield class="h-5 w-5 text-signal" />
          <p class="text-sm font-semibold uppercase tracking-wide text-signal">Admin</p>
        </div>
        <h1 class="mt-2 text-3xl font-semibold text-ink">File Audit Trail</h1>
        <p class="mt-2 max-w-2xl text-sm leading-6 text-graphite">
          Immutable audit records for file access and download activity across all orders.
          Capped at 500 most recent entries per log.
        </p>
      </div>
    </section>

    <!-- Tab switcher -->
    <div class="flex gap-1 rounded-lg border border-slate-200 bg-slate-50 p-1 w-fit">
      <button
        class="rounded-md px-4 py-2 text-sm font-semibold transition-colors focus-ring"
        :class="activeTab === 'access' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
        @click="switchTab('access')">
        Access Log
      </button>
      <button
        class="rounded-md px-4 py-2 text-sm font-semibold transition-colors focus-ring"
        :class="activeTab === 'download' ? 'bg-white text-ink shadow-sm' : 'text-graphite hover:text-ink'"
        @click="switchTab('download')">
        Download Log
      </button>
    </div>

    <!-- ── ACCESS LOG TAB ─────────────────────────────────────────────── -->
    <div v-if="activeTab === 'access'" class="space-y-3">
      <div class="flex flex-wrap items-center gap-3">
        <input
          v-model="accessSearch"
          type="search"
          placeholder="Search by file name or user email…"
          class="focus-ring h-9 w-72 rounded-md border border-slate-200 px-3 text-sm" />
        <button
          class="focus-ring inline-flex h-9 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-semibold text-graphite hover:text-ink disabled:opacity-50"
          :disabled="accessLoading"
          @click="loadAccessLog">
          <RefreshCw class="h-4 w-4" :class="accessLoading ? 'animate-spin' : ''" />
          Refresh
        </button>
        <span class="text-xs text-graphite">{{ filteredAccessLog.length }} entries</span>
      </div>

      <div v-if="accessError" class="rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
        {{ accessError }}
      </div>

      <div class="overflow-x-auto rounded-xl border border-slate-200 bg-white">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-slate-100 bg-slate-50 text-left">
              <th class="px-4 py-3 text-xs font-semibold text-graphite uppercase tracking-wide">Timestamp</th>
              <th class="px-4 py-3 text-xs font-semibold text-graphite uppercase tracking-wide">File Name</th>
              <th class="px-4 py-3 text-xs font-semibold text-graphite uppercase tracking-wide">Access Type</th>
              <th class="px-4 py-3 text-xs font-semibold text-graphite uppercase tracking-wide">User Email</th>
              <th class="px-4 py-3 text-xs font-semibold text-graphite uppercase tracking-wide">IP Address</th>
              <th class="px-4 py-3 text-xs font-semibold text-graphite uppercase tracking-wide">Success</th>
              <th class="px-4 py-3 text-xs font-semibold text-graphite uppercase tracking-wide">Bytes</th>
            </tr>
          </thead>
          <tbody>
            <!-- Loading skeleton -->
            <template v-if="accessLoading && !accessLog.length">
              <tr v-for="n in 8" :key="n" class="border-b border-slate-50">
                <td v-for="c in 7" :key="c" class="px-4 py-3">
                  <div class="h-3 animate-pulse rounded bg-slate-100" :style="{ width: `${50 + Math.random() * 40}%` }" />
                </td>
              </tr>
            </template>
            <!-- Empty state -->
            <tr v-else-if="!filteredAccessLog.length">
              <td colspan="7" class="px-4 py-10 text-center text-sm text-graphite">No access log entries found.</td>
            </tr>
            <!-- Rows -->
            <tr
              v-for="entry in filteredAccessLog"
              :key="entry.id"
              class="border-b border-slate-50 transition-colors hover:bg-slate-50/60"
              :class="!entry.success ? 'bg-rose-50 hover:bg-rose-50' : ''">
              <td class="px-4 py-3 text-xs text-graphite whitespace-nowrap">{{ fmtDate(entry.created_at) }}</td>
              <td class="px-4 py-3 text-xs font-medium text-ink max-w-[180px] truncate" :title="entry.file_name">{{ entry.file_name }}</td>
              <td class="px-4 py-3 text-xs text-graphite">
                <span class="rounded px-1.5 py-0.5 text-[10px] font-semibold bg-slate-100 text-slate-700 uppercase">
                  {{ entry.access_type }}
                </span>
              </td>
              <td class="px-4 py-3 text-xs text-graphite">{{ entry.user_email ?? "—" }}</td>
              <td class="px-4 py-3 text-xs text-graphite font-mono">{{ entry.ip_address ?? "—" }}</td>
              <td class="px-4 py-3 text-xs">
                <span v-if="entry.success" class="font-semibold text-emerald-600">&#x2713;</span>
                <span v-else class="font-semibold text-rose-600" :title="entry.error_detail">&#x2717;</span>
              </td>
              <td class="px-4 py-3 text-xs text-graphite">{{ bytesLabel(entry.bytes_transferred) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ── DOWNLOAD LOG TAB ────────────────────────────────────────────── -->
    <div v-if="activeTab === 'download'" class="space-y-3">
      <div class="flex flex-wrap items-center gap-3">
        <input
          v-model="downloadSearch"
          type="search"
          placeholder="Search by file name or user email…"
          class="focus-ring h-9 w-72 rounded-md border border-slate-200 px-3 text-sm" />
        <button
          class="focus-ring inline-flex h-9 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm font-semibold text-graphite hover:text-ink disabled:opacity-50"
          :disabled="downloadLoading"
          @click="loadDownloadLog">
          <RefreshCw class="h-4 w-4" :class="downloadLoading ? 'animate-spin' : ''" />
          Refresh
        </button>
        <span class="text-xs text-graphite">{{ filteredDownloadLog.length }} entries</span>
      </div>

      <div v-if="downloadError" class="rounded-md border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
        {{ downloadError }}
      </div>

      <div class="overflow-x-auto rounded-xl border border-slate-200 bg-white">
        <table class="w-full text-sm">
          <thead>
            <tr class="border-b border-slate-100 bg-slate-50 text-left">
              <th class="px-4 py-3 text-xs font-semibold text-graphite uppercase tracking-wide">Timestamp</th>
              <th class="px-4 py-3 text-xs font-semibold text-graphite uppercase tracking-wide">File Name</th>
              <th class="px-4 py-3 text-xs font-semibold text-graphite uppercase tracking-wide">Downloaded By</th>
              <th class="px-4 py-3 text-xs font-semibold text-graphite uppercase tracking-wide">IP Address</th>
              <th class="px-4 py-3 text-xs font-semibold text-graphite uppercase tracking-wide">User Agent</th>
            </tr>
          </thead>
          <tbody>
            <!-- Loading skeleton -->
            <template v-if="downloadLoading && !downloadLog.length">
              <tr v-for="n in 8" :key="n" class="border-b border-slate-50">
                <td v-for="c in 5" :key="c" class="px-4 py-3">
                  <div class="h-3 animate-pulse rounded bg-slate-100" :style="{ width: `${50 + Math.random() * 40}%` }" />
                </td>
              </tr>
            </template>
            <!-- Empty state -->
            <tr v-else-if="!filteredDownloadLog.length">
              <td colspan="5" class="px-4 py-10 text-center text-sm text-graphite">No download log entries found.</td>
            </tr>
            <!-- Rows -->
            <tr
              v-for="entry in filteredDownloadLog"
              :key="entry.id"
              class="border-b border-slate-50 transition-colors hover:bg-slate-50/60">
              <td class="px-4 py-3 text-xs text-graphite whitespace-nowrap">{{ fmtDate(entry.downloaded_at) }}</td>
              <td class="px-4 py-3 text-xs font-medium text-ink max-w-[180px] truncate" :title="entry.file_name">{{ entry.file_name }}</td>
              <td class="px-4 py-3 text-xs text-graphite">{{ entry.downloaded_by_email ?? "—" }}</td>
              <td class="px-4 py-3 text-xs text-graphite font-mono">{{ entry.ip_address ?? "—" }}</td>
              <td class="px-4 py-3 text-xs text-graphite max-w-[220px] truncate" :title="entry.user_agent">{{ truncate(entry.user_agent) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

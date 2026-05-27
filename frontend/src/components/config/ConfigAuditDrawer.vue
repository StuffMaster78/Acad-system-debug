<script setup lang="ts">
import { X, ArrowRight, Clock } from "@lucide/vue";
import { useAdminMasterConfigStore } from "@/stores/adminMasterConfig";

const config = useAdminMasterConfigStore();

function formatValue(v: unknown): string {
  if (v === null || v === undefined) return "—";
  if (typeof v === "boolean") return v ? "Enabled" : "Disabled";
  return String(v);
}

function relativeTime(iso: string) {
  const diff = Date.now() - new Date(iso).getTime();
  const min = Math.floor(diff / 60000);
  if (min < 1) return "just now";
  if (min < 60) return `${min}m ago`;
  const hr = Math.floor(min / 60);
  if (hr < 24) return `${hr}h ago`;
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(iso));
}
</script>

<template>
  <aside
    class="flex w-80 shrink-0 flex-col border-l border-slate-200 bg-white shadow-panel overflow-hidden"
  >
    <!-- Header -->
    <div class="flex items-center justify-between border-b border-slate-100 px-4 py-3">
      <div>
        <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Audit History</p>
        <p class="text-sm font-medium text-ink">
          {{ config.auditSection?.split(":")?.[1]?.replace(/-/g, " ") ?? "Section" }}
        </p>
      </div>
      <button
        class="rounded p-1 text-graphite hover:bg-slate-100 hover:text-ink transition-colors"
        @click="config.closeAudit()"
      >
        <X class="size-4" />
      </button>
    </div>

    <!-- Loading -->
    <div v-if="config.isLoadingAudit" class="flex flex-1 items-center justify-center">
      <div class="size-5 animate-spin rounded-full border-2 border-slate-200 border-t-berry" />
    </div>

    <!-- Empty -->
    <div v-else-if="!config.auditEntries.length" class="flex flex-1 flex-col items-center justify-center gap-2 text-graphite">
      <Clock class="size-8 opacity-30" />
      <p class="text-sm">No audit entries yet.</p>
    </div>

    <!-- Entries -->
    <div v-else class="flex-1 overflow-y-auto divide-y divide-slate-50">
      <div
        v-for="entry in config.auditEntries"
        :key="entry.id"
        class="px-4 py-3"
      >
        <div class="flex items-start justify-between gap-2 mb-1">
          <span class="text-xs font-medium text-ink leading-snug">{{ entry.label }}</span>
          <span class="text-[10px] text-graphite shrink-0">{{ relativeTime(entry.changedAt) }}</span>
        </div>

        <!-- Diff -->
        <div class="flex items-center gap-1.5 text-xs">
          <code class="rounded bg-rose-50 px-1.5 py-0.5 text-rose-700 line-through">{{ formatValue(entry.oldValue) }}</code>
          <ArrowRight class="size-3 text-graphite shrink-0" />
          <code class="rounded bg-emerald-50 px-1.5 py-0.5 text-emerald-700">{{ formatValue(entry.newValue) }}</code>
        </div>

        <div class="mt-1.5 flex items-center gap-2 text-[11px] text-graphite">
          <span>{{ entry.changedBy }}</span>
          <span v-if="entry.website" class="rounded bg-slate-100 px-1.5 py-0.5">{{ entry.website }}</span>
          <span v-else class="rounded bg-slate-100 px-1.5 py-0.5">Global</span>
        </div>
      </div>
    </div>
  </aside>
</template>

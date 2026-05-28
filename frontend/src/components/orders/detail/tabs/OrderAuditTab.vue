<template>
  <div class="space-y-4">
    <div class="rounded-lg border border-slate-200 bg-white shadow-panel">
      <div class="border-b border-slate-200 px-5 py-4">
        <h2 class="text-base font-semibold text-ink">Audit log</h2>
        <p class="mt-0.5 text-xs text-graphite">Status changes, file access, payment changes, staff overrides, and sensitive access events.</p>
      </div>
      <div v-if="loading" class="px-5 py-6 text-sm text-graphite">Loading…</div>
      <div v-else-if="!entries.length" class="px-5 py-8 text-center text-sm text-graphite">No audit entries found.</div>
      <div v-else class="divide-y divide-slate-100">
        <div v-for="entry in entries" :key="entry.id" class="px-5 py-3">
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0">
              <p class="text-sm font-medium text-ink">{{ entry.action }}</p>
              <p class="mt-0.5 text-xs text-graphite">
                {{ entry.actor_id ? `Actor #${entry.actor_id}` : "System" }}
                <span v-if="entry.service_name"> · {{ entry.service_name }}</span>
                <span v-if="entry.severity !== 'info'"> · {{ entry.severity }}</span>
              </p>
            </div>
            <span class="shrink-0 text-xs text-graphite whitespace-nowrap">{{ fmtDate(entry.occurred_at) }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="rounded-lg border border-dashed border-slate-200 bg-slate-50 p-4 text-xs text-graphite">
      <!-- TODO: wire to audit_logging API filtered by order — /api/v1/audit-logs/?object_id={orderId}&content_type=order -->
      Full audit log wiring requires order-scoped audit query endpoint.
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { auditLogsApi, type AuditEvent } from "@/api/auditLogs";

const props = defineProps<{ orderId: string }>();

const entries = ref<AuditEvent[]>([]);
const loading = ref(false);

function fmtDate(v: string): string {
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(v));
}

onMounted(async () => {
  loading.value = true;
  try {
    const { data } = await auditLogsApi.events({ object_type: "order", action: props.orderId });
    entries.value = data.results ?? [];
  } catch {
    entries.value = [];
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="space-y-4">
    <div class="rounded-lg border border-slate-200 bg-white overflow-hidden">
      <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
        <div>
          <h2 class="text-sm font-semibold text-ink">Audit Log</h2>
          <p class="mt-0.5 text-xs text-graphite">Status changes, payments, file access, and staff actions for this order.</p>
        </div>
        <button
          class="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-graphite hover:text-ink disabled:opacity-50"
          :disabled="loading"
          @click="load"
        >
          <RefreshCw class="size-3.5" :class="loading ? 'animate-spin' : ''" />
          Refresh
        </button>
      </div>

      <div v-if="loading" class="space-y-px">
        <div v-for="n in 4" :key="n" class="animate-pulse px-5 py-3">
          <div class="h-3 w-48 rounded bg-slate-200" />
          <div class="mt-2 h-3 w-32 rounded bg-slate-100" />
        </div>
      </div>

      <div v-else-if="!entries.length" class="px-5 py-12 text-center">
        <ClipboardList class="mx-auto mb-2 size-7 text-slate-300" />
        <p class="text-sm text-graphite">No audit entries found for this order.</p>
      </div>

      <div v-else class="divide-y divide-slate-100">
        <div v-for="entry in entries" :key="entry.id" class="flex items-start gap-4 px-5 py-3">
          <!-- Severity dot -->
          <span
            class="mt-1 size-2 shrink-0 rounded-full"
            :class="severityClass(entry.severity)"
          />
          <div class="min-w-0 flex-1">
            <p class="text-sm font-medium text-ink">{{ humanAction(entry.action) }}</p>
            <p class="mt-0.5 text-xs text-graphite">
              <span v-if="entry.actor_id">Actor #{{ entry.actor_id }}</span>
              <span v-else>System</span>
              <span v-if="entry.service_name"> · {{ entry.service_name }}</span>
            </p>
          </div>
          <div class="shrink-0 text-right">
            <p class="text-xs text-graphite whitespace-nowrap">{{ fmtDate(entry.occurred_at) }}</p>
            <span
              v-if="entry.severity !== 'info'"
              class="text-xs font-semibold capitalize"
              :class="severityTextClass(entry.severity)"
            >
              {{ entry.severity }}
            </span>
          </div>
        </div>
      </div>

      <!-- Cursor pagination -->
      <div v-if="nextUrl || prevUrl" class="flex items-center justify-between border-t border-slate-100 px-5 py-3">
        <button
          class="text-xs font-semibold text-graphite hover:text-ink disabled:opacity-40"
          :disabled="!prevUrl"
          @click="loadFrom(prevUrl!)"
        >
          ← Previous
        </button>
        <button
          class="text-xs font-semibold text-graphite hover:text-ink disabled:opacity-40"
          :disabled="!nextUrl"
          @click="loadFrom(nextUrl!)"
        >
          Next →
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ClipboardList, RefreshCw } from "@lucide/vue";
import { auditLogsApi, type AuditEvent } from "@/api/auditLogs";
import { useAuthStore } from "@/stores/auth";

const props = defineProps<{ orderId: string }>();

const auth = useAuthStore();
const entries = ref<AuditEvent[]>([]);
const loading = ref(false);
const nextUrl = ref<string | null>(null);
const prevUrl = ref<string | null>(null);

function fmtDate(v: string): string {
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(v));
}

function humanAction(action: string): string {
  return action.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function severityClass(s: string): string {
  const map: Record<string, string> = { critical: "bg-rose-500", warning: "bg-amber-400", error: "bg-rose-400" };
  return map[s] ?? "bg-slate-300";
}

function severityTextClass(s: string): string {
  const map: Record<string, string> = { critical: "text-rose-600", warning: "text-amber-600", error: "text-rose-500" };
  return map[s] ?? "text-graphite";
}

function previewAuditEvent(partial: Partial<AuditEvent> & Pick<AuditEvent, "id" | "occurred_at" | "action">): AuditEvent {
  return {
    website: null,
    actor_id: null,
    actor_role: null,
    actor_display: null,
    object_type: "order",
    object_id: props.orderId,
    object_label: `Order ${props.orderId}`,
    portal_surface: "staff",
    request_path: null,
    http_method: null,
    session_id: null,
    status: "processed",
    processed_at: null,
    processing_attempts: 1,
    correlation_id: null,
    span_id: null,
    severity: "info",
    is_sensitive: false,
    sensitivity_level: null,
    service_name: null,
    before_state: null,
    after_state: null,
    metadata: null,
    ...partial,
  };
}

async function load() {
  loading.value = true;
  try {
    if (auth.isPreviewSession) {
      const now = Date.now();
      entries.value = [
        previewAuditEvent({ id: "1", occurred_at: new Date(now - 1000 * 60 * 5).toISOString(), actor_id: "88", actor_role: "support", actor_display: "Support #88", action: "order_status_changed", service_name: "order_transition_service" }),
        previewAuditEvent({ id: "2", occurred_at: new Date(now - 1000 * 60 * 30).toISOString(), action: "payment_confirmed", service_name: "billing_service" }),
        previewAuditEvent({ id: "3", occurred_at: new Date(now - 1000 * 60 * 90).toISOString(), actor_id: "12", actor_role: "admin", actor_display: "Admin #12", action: "writer_assigned", service_name: "staffing_service" }),
        previewAuditEvent({ id: "4", occurred_at: new Date(now - 1000 * 60 * 120).toISOString(), actor_id: "12", actor_role: "admin", actor_display: "Admin #12", action: "file_access", severity: "warning", is_sensitive: true, sensitivity_level: "medium", service_name: "files_service" }),
      ];
      nextUrl.value = null;
      prevUrl.value = null;
      return;
    }
    const { data } = await auditLogsApi.events({ object_type: "order", object_id: props.orderId, page_size: 25 });
    entries.value = data.results ?? [];
    nextUrl.value = data.next ?? null;
    prevUrl.value = data.previous ?? null;
  } catch {
    entries.value = [];
  } finally {
    loading.value = false;
  }
}

async function loadFrom(url: string) {
  loading.value = true;
  try {
    const { data } = await auditLogsApi.eventsFromUrl(url);
    entries.value = data.results ?? [];
    nextUrl.value = data.next ?? null;
    prevUrl.value = data.previous ?? null;
  } catch {
    // keep current page on error
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

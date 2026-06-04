import { ref, computed } from "vue";
import { defineStore } from "pinia";
import {
  auditLogsApi,
  type AuditEvent,
  type AuditEventFilters,
  type AuditSensitiveSummary,
} from "@/api/auditLogs";
import { api, apiPath } from "@/api/client";

// ---------------------------------------------------------------------------
// Actor name cache — resolve actor_id → display name on demand
// ---------------------------------------------------------------------------
const actorCache = new Map<string, string>();

async function resolveActorName(actorId: string): Promise<string> {
  if (actorCache.has(actorId)) return actorCache.get(actorId)!;
  try {
    const { data } = await api.get<{ id: number; full_name?: string; username?: string; email?: string }>(
      apiPath(`/users/users/${actorId}/`)
    );
    const name = data.full_name || data.username || data.email || `#${actorId}`;
    actorCache.set(actorId, name);
    return name;
  } catch {
    const fallback = `#${actorId}`;
    actorCache.set(actorId, fallback);
    return fallback;
  }
}

// ---------------------------------------------------------------------------
// Sensitive action classification for badge display
// ---------------------------------------------------------------------------
export const SENSITIVE_ACTION_LABELS: Record<string, { label: string; color: string }> = {
  "auth.role_changed":         { label: "Role change", color: "text-amber-700 bg-amber-50 border-amber-200" },
  "auth.user_suspended":       { label: "Suspension", color: "text-red-700 bg-red-50 border-red-200" },
  "order.cancelled":           { label: "Cancelled", color: "text-orange-700 bg-orange-50 border-orange-200" },
  "order.refunded":            { label: "Refunded", color: "text-violet-700 bg-violet-50 border-violet-200" },
  "order.disputed":            { label: "Disputed", color: "text-red-700 bg-red-50 border-red-200" },
  "order.dispute_resolved":    { label: "Dispute resolved", color: "text-emerald-700 bg-emerald-50 border-emerald-200" },
  "payment.refund_issued":     { label: "Refund", color: "text-violet-700 bg-violet-50 border-violet-200" },
  "payment.initiated":         { label: "Payment", color: "text-blue-700 bg-blue-50 border-blue-200" },
  "config.branding_updated":   { label: "Config change", color: "text-amber-700 bg-amber-50 border-amber-200" },
  "config.writer_level_changed": { label: "Pay rate change", color: "text-amber-700 bg-amber-50 border-amber-200" },
  "wallet.payout":             { label: "Payout", color: "text-teal-700 bg-teal-50 border-teal-200" },
};

export function sensitiveActionBadge(action: string) {
  return SENSITIVE_ACTION_LABELS[action] ?? null;
}

// ---------------------------------------------------------------------------
// Human-readable action labels
// ---------------------------------------------------------------------------
export function humanAction(action: string): string {
  const map: Record<string, string> = {
    "auth.login": "User logged in",
    "auth.logout": "User logged out",
    "auth.role_changed": "User role changed",
    "auth.user_suspended": "User suspended",
    "order.created": "Order created",
    "order.cancelled": "Order cancelled",
    "order.completed": "Order completed",
    "order.disputed": "Dispute opened",
    "order.dispute_resolved": "Dispute resolved",
    "order.revision_requested": "Revision requested",
    "order.refunded": "Order refunded",
    "order.writer_assigned": "Writer assigned",
    "payment.initiated": "Payment initiated",
    "payment.refund_issued": "Refund issued",
    "wallet.funding": "Wallet top-up",
    "wallet.payout": "Writer payout",
    "wallet.order_refund": "Refund to wallet",
    "config.branding_updated": "Branding/disclosure updated",
    "config.portal_definition_changed": "Portal config changed",
    "config.writer_level_changed": "Writer pay rate changed",
  };
  return map[action] ?? action.replace(/\./g, " › ").replace(/_/g, " ");
}

// ---------------------------------------------------------------------------
// Store
// ---------------------------------------------------------------------------
export const useAuditLogStore = defineStore("auditLog", () => {
  const events = ref<AuditEvent[]>([]);
  const actorNames = ref<Record<string, string>>({});
  const summary = ref<AuditSensitiveSummary | null>(null);
  const isLoading = ref(false);
  const isSummaryLoading = ref(false);
  const error = ref("");
  const nextCursor = ref<string | null>(null);
  const filters = ref<AuditEventFilters>({
    search: "", severity: "", status: "", service_name: "",
    action: "", actor_id: "", object_type: "", is_sensitive: undefined,
    occurred_after: "", occurred_before: "", page_size: 50,
  });

  const hasMore = computed(() => !!nextCursor.value);

  function _clean(f: AuditEventFilters): AuditEventFilters {
    return Object.fromEntries(
      Object.entries(f).filter(([, v]) => v !== "" && v !== undefined)
    ) as AuditEventFilters;
  }

  async function load(reset = true) {
    if (reset) {
      events.value = [];
      nextCursor.value = null;
    }
    isLoading.value = true;
    error.value = "";
    try {
      const { data } = reset
        ? await auditLogsApi.events(_clean(filters.value))
        : await auditLogsApi.eventsFromUrl(nextCursor.value!);
      const incoming = data.results;
      events.value = reset ? incoming : [...events.value, ...incoming];
      nextCursor.value = data.next;
      // Resolve actor names in background
      const unresolvedIds = [...new Set(incoming.map((e) => e.actor_id).filter(Boolean) as string[])]
        .filter((id) => !actorNames.value[id]);
      for (const id of unresolvedIds) {
        resolveActorName(id).then((name) => { actorNames.value[id] = name; });
      }
    } catch {
      error.value = "Failed to load audit events.";
    } finally {
      isLoading.value = false;
    }
  }

  async function loadMore() {
    if (!nextCursor.value) return;
    await load(false);
  }

  async function loadSummary(days = 30, websiteId?: number) {
    isSummaryLoading.value = true;
    try {
      const { data } = await auditLogsApi.sensitiveSummary({ days, website: websiteId });
      summary.value = data;
    } catch {
      summary.value = null;
    } finally {
      isSummaryLoading.value = false;
    }
  }

  function actorName(actorId: string | null): string {
    if (!actorId) return "System";
    return actorNames.value[actorId] ?? `Actor #${actorId}`;
  }

  function exportUrl(): string {
    return auditLogsApi.exportUrl(_clean(filters.value));
  }

  function resetFilters() {
    filters.value = {
      search: "", severity: "", status: "", service_name: "",
      action: "", actor_id: "", object_type: "", is_sensitive: undefined,
      occurred_after: "", occurred_before: "", page_size: 50,
    };
  }

  return {
    events, actorNames, summary, isLoading, isSummaryLoading, error,
    nextCursor, filters, hasMore,
    load, loadMore, loadSummary, actorName, exportUrl, resetFilters,
  };
});

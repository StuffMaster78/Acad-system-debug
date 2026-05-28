<script setup lang="ts">
import { onMounted } from "vue";
import { CheckCircle2, RefreshCw, ShieldAlert } from "@lucide/vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useSupportWorkspaceStore } from "@/stores/supportWorkspace";

const support = useSupportWorkspaceStore();

function statusTone(status?: string | null): "danger" | "warning" | "success" | "neutral" {
  const s = (status ?? "").toLowerCase();
  if (s.includes("breach") || s.includes("critical")) return "danger";
  if (s.includes("open") || s.includes("pending")) return "warning";
  if (s.includes("resolved") || s.includes("closed")) return "success";
  return "neutral";
}

function formatDate(value?: string | null) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

onMounted(() => {
  if (!support.escalations.length) support.hydrate().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-4">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Support</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Escalations</h1>
        <p class="mt-2 max-w-2xl text-sm text-graphite">
          Communication threads escalated for staff resolution. Resolve once the underlying issue is addressed.
        </p>
      </div>
      <button
        class="focus-ring inline-flex items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold disabled:opacity-60"
        type="button"
        :disabled="support.isLoading"
        @click="support.hydrate().catch(() => undefined)"
      >
        <RefreshCw class="h-4 w-4" :class="support.isLoading ? 'animate-spin' : ''" />
        Refresh
      </button>
    </section>

    <p v-if="support.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ support.error }}
    </p>
    <p v-if="support.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ support.notice }}
    </p>

    <div v-if="!support.escalations.length && !support.isLoading" class="rounded-lg border border-slate-200 bg-white px-6 py-12">
      <EmptyState
        :icon="ShieldAlert"
        title="No escalations"
        message="Escalated communication threads appear here when staff action is required."
      />
    </div>

    <div v-else class="space-y-4">
      <article
        v-for="escalation in support.escalations"
        :key="escalation.id"
        class="rounded-lg border border-slate-200 bg-white p-5"
      >
        <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div class="min-w-0 flex-1">
            <div class="flex flex-wrap items-center gap-2">
              <h2 class="font-semibold text-ink">Thread #{{ escalation.thread }}</h2>
              <StatusPill :label="escalation.status" :tone="statusTone(escalation.status)" />
            </div>
            <p class="mt-2 text-sm leading-6 text-graphite">{{ escalation.reason }}</p>
            <p class="mt-1.5 text-xs text-graphite">
              Escalated by {{ escalation.escalated_by_display || "staff" }}
              · {{ formatDate(escalation.escalated_at) }}
              <template v-if="escalation.resolved_at">
                · Resolved {{ formatDate(escalation.resolved_at) }}
              </template>
            </p>
            <p v-if="escalation.resolution_note" class="mt-2 rounded-md bg-slate-50 px-3 py-2 text-sm text-graphite">
              {{ escalation.resolution_note }}
            </p>
          </div>
          <button
            class="focus-ring inline-flex shrink-0 items-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2 text-sm font-semibold disabled:opacity-60"
            type="button"
            :disabled="support.isMutating || escalation.status === 'resolved'"
            @click="support.resolveEscalation(escalation.id).catch(() => undefined)"
          >
            <CheckCircle2 class="h-4 w-4" />
            {{ escalation.status === "resolved" ? "Resolved" : "Resolve" }}
          </button>
        </div>
      </article>
    </div>
  </div>
</template>

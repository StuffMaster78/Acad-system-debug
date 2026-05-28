<script setup lang="ts">
import { onMounted } from "vue";
import { Activity, RefreshCw, Search } from "@lucide/vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import LoadingSpinner from "@/components/ui/LoadingSpinner.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useActivityStore } from "@/stores/activity";
import type { UserRole } from "@/types/roles";

defineProps<{
  role: UserRole;
}>();

const activity = useActivityStore();

const severityOptions = ["all", "info", "success", "warning", "critical"] as const;

function formatDate(value: string) {
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function severityTone(value: string) {
  if (value === "critical") return "danger";
  if (value === "warning") return "warning";
  if (value === "success") return "success";
  return "neutral";
}

onMounted(() => {
  activity.hydrate().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-8">
    <section class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase text-signal">{{ role }} activity</p>
        <h1 class="mt-2 text-3xl font-semibold">Activity</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          Shared order timelines and personal platform activity scoped to what this role can see.
        </p>
      </div>
      <button
        class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
        type="button"
        :disabled="activity.isLoading"
        @click="activity.hydrate"
      >
        <RefreshCw class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <p
      v-if="activity.error"
      class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {{ activity.error }} Preview mode will still show the activity pattern.
    </p>

    <section class="rounded-md border border-slate-200 bg-white">
      <div class="flex flex-col gap-3 border-b border-slate-200 px-4 py-4 lg:flex-row lg:items-center lg:justify-between">
        <div class="flex items-center gap-2">
          <Activity class="h-5 w-5 text-signal" />
          <div>
            <h2 class="text-base font-semibold">Feed</h2>
            <p class="text-sm text-graphite">Order events, messages, files, payments, and system notices.</p>
          </div>
        </div>
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
          <div class="inline-flex rounded-md border border-slate-200 bg-slate-50 p-1">
            <button
              v-for="option in severityOptions"
              :key="option"
              class="focus-ring min-h-9 rounded px-3 text-xs font-semibold capitalize"
              :class="activity.severity === option ? 'bg-white text-ink shadow-sm' : 'text-graphite'"
              type="button"
              @click="activity.severity = option"
            >
              {{ option }}
            </button>
          </div>
          <label class="relative block min-w-64">
            <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-graphite" />
            <input
              v-model="activity.query"
              class="focus-ring h-10 w-full rounded-md border border-slate-200 bg-white pl-9 pr-3 text-sm"
              type="search"
              placeholder="Search activity"
            >
          </label>
        </div>
      </div>

      <div v-if="activity.isLoading" class="p-6">
        <LoadingSpinner label="Loading activity" />
      </div>

      <div v-else-if="activity.filteredEvents.length" class="divide-y divide-slate-100">
        <article
          v-for="event in activity.filteredEvents"
          :key="event.id"
          class="grid gap-3 px-4 py-4 md:grid-cols-[1fr_auto]"
        >
          <div>
            <div class="flex flex-wrap items-center gap-2">
              <StatusPill :label="event.severity" :tone="severityTone(event.severity)" />
              <span class="text-xs font-semibold uppercase text-graphite">{{ event.verb }}</span>
            </div>
            <h3 class="mt-3 text-base font-semibold text-ink">
              {{ event.card?.title || event.title || event.verb }}
            </h3>
            <p class="mt-1 text-sm leading-6 text-graphite">
              {{ event.card?.summary || event.summary }}
            </p>
            <div class="mt-3 flex flex-wrap gap-2 text-xs text-graphite">
              <span v-if="event.card?.actor">Actor: {{ event.card.actor.label }}</span>
              <span v-if="event.card?.target">Target: {{ event.card.target.label }}</span>
              <span v-if="event.card?.subject">Subject: {{ event.card.subject.label }}</span>
            </div>
          </div>
          <div class="text-sm text-graphite md:text-right">
            {{ formatDate(event.occurred_at) }}
          </div>
        </article>
      </div>

      <div v-else class="p-4">
        <EmptyState
          :icon="Activity"
          title="No activity yet"
          message="Activity will appear here once events are emitted by orders, files, messages, and payments."
        />
      </div>
    </section>
  </div>
</template>

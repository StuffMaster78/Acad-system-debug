<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { Activity } from "@lucide/vue";
import { useActivityStore } from "@/stores/activity";
import type { UserRole } from "@/types/roles";

const props = defineProps<{
  role: UserRole;
}>();

const activity = useActivityStore();
const open = ref(false);

const recentEvents = computed(() => activity.events.slice(0, 5));
const visibleCount = computed(() => Math.min(activity.events.length, 9));
const hasUrgentActivity = computed(() =>
  activity.events.some((event) => event.severity === "critical" || event.severity === "warning"),
);

function formatDate(value?: string) {
  if (!value) return "Now";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function severityClass(severity: string) {
  if (severity === "critical") return "bg-rose-600";
  if (severity === "warning") return "bg-amber-500";
  if (severity === "success") return "bg-emerald-600";
  return "bg-signal";
}

onMounted(() => {
  if (!activity.events.length && !activity.isLoading) {
    activity.hydrate().catch(() => undefined);
  }
});
</script>

<template>
  <div class="relative">
    <button
      class="focus-ring relative inline-flex h-10 w-10 items-center justify-center rounded-md border border-slate-200 bg-white text-graphite hover:bg-slate-50 hover:text-ink"
      type="button"
      title="Activity"
      aria-label="Activity"
      @click="open = !open"
    >
      <Activity class="h-5 w-5" />
      <span
        v-if="visibleCount"
        class="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full px-1 text-xs font-semibold text-white"
        :class="hasUrgentActivity ? 'bg-amber-500' : 'bg-signal'"
      >
        {{ visibleCount }}
      </span>
    </button>

    <section
      v-if="open"
      class="absolute right-0 top-12 z-30 w-80 rounded-md border border-slate-200 bg-white shadow-panel"
    >
      <div class="flex items-center justify-between gap-3 border-b border-slate-200 px-4 py-3">
        <p class="text-sm font-semibold text-ink">Activity</p>
        <RouterLink
          class="focus-ring rounded text-xs font-semibold text-signal"
          :to="`/${props.role}/activity`"
          @click="open = false"
        >
          View all
        </RouterLink>
      </div>

      <div v-if="recentEvents.length" class="max-h-96 divide-y divide-slate-100 overflow-y-auto">
        <RouterLink
          v-for="event in recentEvents"
          :key="event.id"
          class="block px-4 py-3 hover:bg-slate-50"
          :to="`/${props.role}/activity`"
          @click="open = false"
        >
          <div class="flex items-start gap-3">
            <span
              class="mt-1 h-2.5 w-2.5 shrink-0 rounded-full"
              :class="severityClass(event.severity)"
            />
            <div class="min-w-0">
              <p class="truncate text-sm font-semibold text-ink">
                {{ event.card?.title || event.title || event.verb }}
              </p>
              <p class="mt-1 line-clamp-2 text-sm leading-5 text-graphite">
                {{ event.card?.summary || event.summary }}
              </p>
              <p class="mt-2 text-xs text-graphite">{{ formatDate(event.occurred_at) }}</p>
            </div>
          </div>
        </RouterLink>
      </div>
      <p v-else class="px-4 py-6 text-center text-sm text-graphite">No activity yet.</p>
    </section>
  </div>
</template>

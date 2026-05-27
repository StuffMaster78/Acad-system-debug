<script setup lang="ts">
import { onMounted, ref } from "vue";
import {
  AlertTriangle,
  CheckCircle2,
  Circle,
  Info,
  RefreshCw,
  XCircle,
} from "@lucide/vue";
import { activityApi } from "@/api/activity";
import type { ActivityEvent } from "@/types/activity";

const props = defineProps<{
  orderId: string | number;
}>();

const events = ref<ActivityEvent[]>([]);
const isLoading = ref(false);
const error = ref("");

function severityIcon(severity: string) {
  if (severity === "success") return CheckCircle2;
  if (severity === "warning") return AlertTriangle;
  if (severity === "critical") return XCircle;
  return Info;
}

function severityColor(severity: string): string {
  if (severity === "success") return "text-emerald-500 bg-emerald-50 border-emerald-200";
  if (severity === "warning") return "text-saffron bg-amber-50 border-amber-200";
  if (severity === "critical") return "text-berry bg-rose-50 border-rose-200";
  return "text-signal bg-blue-50 border-blue-200";
}

function lineColor(severity: string): string {
  if (severity === "success") return "bg-emerald-200";
  if (severity === "warning") return "bg-amber-200";
  if (severity === "critical") return "bg-rose-200";
  return "bg-slate-200";
}

function formatDate(value?: string): string {
  if (!value) return "";
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

async function load() {
  isLoading.value = true;
  error.value = "";
  try {
    const { data } = await activityApi.feed({
      target_id: props.orderId,
      target_type: "order",
      page_size: 30,
      ordering: "occurred_at",
    });
    const raw = data as ActivityEvent[] | { results?: ActivityEvent[] };
    events.value = Array.isArray(raw) ? raw : (raw.results ?? []);
  } catch {
    error.value = "Could not load order history.";
  } finally {
    isLoading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <section class="rounded-lg border border-slate-200 bg-white shadow-panel">
    <div class="flex items-center justify-between gap-3 border-b border-slate-200 px-5 py-4">
      <div>
        <h2 class="text-base font-semibold text-ink">Order history</h2>
        <p class="mt-0.5 text-xs text-graphite">Chronological timeline of events on this order.</p>
      </div>
      <button
        class="focus-ring inline-flex h-8 items-center gap-1.5 rounded-md border border-slate-200 px-3 text-xs font-semibold text-graphite hover:bg-slate-50 disabled:opacity-60"
        type="button"
        :disabled="isLoading"
        @click="load"
      >
        <RefreshCw class="h-3.5 w-3.5" :class="isLoading ? 'animate-spin' : ''" />
        Refresh
      </button>
    </div>

    <div class="px-5 py-5">
      <div v-if="isLoading && !events.length" class="space-y-4">
        <div
          v-for="n in 4"
          :key="n"
          class="flex gap-4"
          aria-hidden="true"
        >
          <div class="flex flex-col items-center gap-1">
            <div class="h-7 w-7 animate-pulse rounded-full border border-slate-200 bg-slate-100" />
            <div class="w-px flex-1 animate-pulse bg-slate-100" style="min-height: 32px" />
          </div>
          <div class="flex-1 space-y-2 pb-4">
            <div class="h-4 w-1/2 animate-pulse rounded bg-slate-200" />
            <div class="h-3 w-3/4 animate-pulse rounded bg-slate-100" />
            <div class="h-3 w-1/4 animate-pulse rounded bg-slate-100" />
          </div>
        </div>
      </div>

      <div v-else-if="error" class="rounded-md border border-amber-200 bg-amber-50 px-3 py-3 text-sm text-amber-900">
        {{ error }}
      </div>

      <div v-else-if="!events.length" class="py-6 text-center">
        <Circle class="mx-auto h-7 w-7 text-slate-300" />
        <p class="mt-3 text-sm font-medium text-ink">No history yet</p>
        <p class="mt-1 text-xs text-graphite">Events will appear here as the order progresses.</p>
      </div>

      <ol v-else class="space-y-0">
        <li
          v-for="(event, index) in events"
          :key="event.id"
          class="flex gap-4"
        >
          <div class="flex flex-col items-center">
            <div
              class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full border"
              :class="severityColor(event.severity)"
            >
              <component :is="severityIcon(event.severity)" class="h-3.5 w-3.5" />
            </div>
            <div
              v-if="index < events.length - 1"
              class="w-px flex-1 mt-1"
              :class="lineColor(event.severity)"
              style="min-height: 20px"
            />
          </div>

          <div class="min-w-0 flex-1 pb-5">
            <div class="flex flex-wrap items-baseline gap-x-2 gap-y-0.5">
              <p class="text-sm font-semibold text-ink">
                {{ event.card?.title || event.title }}
              </p>
              <span class="text-xs text-slate-400">{{ formatDate(event.occurred_at) }}</span>
            </div>
            <p v-if="event.card?.summary || event.summary" class="mt-1 text-xs leading-5 text-graphite">
              {{ event.card?.summary || event.summary }}
            </p>
            <div
              v-if="event.card?.actor || event.card?.target"
              class="mt-1.5 flex flex-wrap gap-x-3 gap-y-0.5 text-xs text-slate-400"
            >
              <span v-if="event.card?.actor">{{ event.card.actor.label }}</span>
              <span v-if="event.card?.actor && event.card?.target">·</span>
              <span v-if="event.card?.target">{{ event.card.target.label }}</span>
            </div>
          </div>
        </li>
      </ol>
    </div>
  </section>
</template>

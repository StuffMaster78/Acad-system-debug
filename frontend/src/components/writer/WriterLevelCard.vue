<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ArrowRight, CheckCircle2, Star, TrendingUp, XCircle } from "@lucide/vue";
import { writerApi } from "@/api/writer";
import type { WriterLevelProgress } from "@/api/writer";

const data = ref<WriterLevelProgress | null>(null);
const loading = ref(true);

onMounted(async () => {
  try {
    const { data: d } = await writerApi.myLevel();
    data.value = d;
  } catch {
    // non-critical — silently hide
  } finally {
    loading.value = false;
  }
});

// ── helpers ──────────────────────────────────────────────────────────────────

function fmtPct(val: string | null | undefined): string {
  if (!val) return "—";
  return `${parseFloat(val).toFixed(1)}%`;
}

function fmtRating(val: string | null | undefined): string {
  if (!val) return "—";
  return parseFloat(val).toFixed(2);
}

function numVal(s: string | null | undefined): number {
  return s ? parseFloat(s) : 0;
}

// For each metric: does the writer currently pass the criterion?
function passesCompletion(p: WriterLevelProgress): boolean | null {
  if (!p.performance.completion_rate || !p.criteria.min_completion_rate) return null;
  return numVal(p.performance.completion_rate) >= numVal(p.criteria.min_completion_rate);
}

function passesRevision(p: WriterLevelProgress): boolean | null {
  if (!p.performance.revision_rate || !p.criteria.max_revision_rate) return null;
  return numVal(p.performance.revision_rate) <= numVal(p.criteria.max_revision_rate);
}

function passesLateness(p: WriterLevelProgress): boolean | null {
  if (!p.performance.on_time_rate || !p.criteria.max_lateness_rate) return null;
  const lateness = 100 - numVal(p.performance.on_time_rate);
  return lateness <= numVal(p.criteria.max_lateness_rate);
}

function passesOrders(p: WriterLevelProgress): boolean | null {
  if (!p.criteria.min_orders_completed) return null;
  return p.performance.completed_orders >= p.criteria.min_orders_completed;
}

// Progress bar width (0–100) clamped
function barWidth(current: string | null, target: string | null, invert = false): number {
  if (!current || !target) return 0;
  const c = numVal(current);
  const t = numVal(target);
  if (!t) return 100;
  const pct = invert ? (1 - c / t) * 100 : (c / t) * 100;
  return Math.min(Math.max(pct, 0), 100);
}

// For next-level criteria comparison
function meetsNextCriteria(
  metric: "completion" | "revision" | "lateness" | "orders",
  p: WriterLevelProgress,
): boolean {
  if (!p.next) return false;
  const c = p.next.criteria;
  const perf = p.performance;
  if (metric === "completion") return c.min_completion_rate
    ? numVal(perf.completion_rate) >= numVal(c.min_completion_rate) : true;
  if (metric === "revision") return c.max_revision_rate
    ? numVal(perf.revision_rate ?? "0") <= numVal(c.max_revision_rate) : true;
  if (metric === "lateness") return c.max_lateness_rate
    ? (100 - numVal(perf.on_time_rate ?? "100")) <= numVal(c.max_lateness_rate) : true;
  if (metric === "orders") return c.min_orders_completed
    ? perf.completed_orders >= c.min_orders_completed : true;
  return false;
}
</script>

<template>
  <div v-if="!loading && data" class="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">

    <!-- Header -->
    <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
      <div class="flex items-center gap-3">
        <div class="flex h-9 w-9 items-center justify-center rounded-full bg-signal/10">
          <Star class="h-4 w-4 text-signal fill-signal/40" />
        </div>
        <div>
          <p class="text-sm font-semibold text-ink">
            {{ data.current?.name ?? "Unranked" }}
          </p>
          <p class="text-xs text-graphite">Your writer level</p>
        </div>
      </div>
      <div v-if="data.next" class="hidden sm:flex items-center gap-1.5 text-xs text-graphite">
        <TrendingUp class="h-3.5 w-3.5 text-signal" />
        Next: <span class="font-semibold text-ink">{{ data.next.name }}</span>
      </div>
    </div>

    <!-- Description -->
    <p
      v-if="data.current?.description"
      class="border-b border-slate-100 px-5 py-3 text-xs text-graphite"
    >
      {{ data.current.description }}
    </p>

    <!-- Performance metrics vs. current criteria -->
    <div class="px-5 py-4 space-y-3">
      <p class="text-xs font-semibold uppercase tracking-wide text-graphite">Your performance</p>

      <!-- Completed orders -->
      <div class="space-y-1">
        <div class="flex items-center justify-between text-xs">
          <span class="text-graphite">Orders completed</span>
          <div class="flex items-center gap-1.5">
            <span class="font-semibold text-ink">{{ data.performance.completed_orders }}</span>
            <span v-if="data.criteria.min_orders_completed" class="text-graphite">
              / {{ data.criteria.min_orders_completed }} min
            </span>
            <CheckCircle2
              v-if="passesOrders(data) === true"
              class="h-3.5 w-3.5 text-emerald-500"
            />
          </div>
        </div>
        <div class="h-1.5 overflow-hidden rounded-full bg-slate-100">
          <div
            class="h-full rounded-full bg-signal transition-all"
            :style="{ width: `${Math.min((data.performance.completed_orders / (data.criteria.min_orders_completed || 1)) * 100, 100)}%` }"
          />
        </div>
      </div>

      <!-- Average rating -->
      <div v-if="data.performance.average_rating" class="flex items-center justify-between text-xs">
        <span class="text-graphite">Average rating</span>
        <div class="flex items-center gap-1.5">
          <Star class="h-3 w-3 text-amber-400 fill-amber-400" />
          <span class="font-semibold text-ink">{{ fmtRating(data.performance.average_rating) }}</span>
          <span class="text-graphite">/ 5.00</span>
        </div>
      </div>

      <!-- Completion rate -->
      <div v-if="data.performance.completion_rate !== null" class="space-y-1">
        <div class="flex items-center justify-between text-xs">
          <span class="text-graphite">Completion rate</span>
          <div class="flex items-center gap-1.5">
            <span class="font-semibold text-ink">{{ fmtPct(data.performance.completion_rate) }}</span>
            <span v-if="data.criteria.min_completion_rate" class="text-graphite">
              (min {{ fmtPct(data.criteria.min_completion_rate) }})
            </span>
            <CheckCircle2 v-if="passesCompletion(data) === true" class="h-3.5 w-3.5 text-emerald-500" />
            <XCircle v-else-if="passesCompletion(data) === false" class="h-3.5 w-3.5 text-berry" />
          </div>
        </div>
        <div class="h-1.5 overflow-hidden rounded-full bg-slate-100">
          <div
            class="h-full rounded-full transition-all"
            :class="passesCompletion(data) === false ? 'bg-berry' : 'bg-emerald-500'"
            :style="{ width: `${barWidth(data.performance.completion_rate, data.criteria.min_completion_rate)}%` }"
          />
        </div>
      </div>

      <!-- On-time rate -->
      <div v-if="data.performance.on_time_rate !== null" class="flex items-center justify-between text-xs">
        <span class="text-graphite">On-time delivery</span>
        <div class="flex items-center gap-1.5">
          <span class="font-semibold text-ink">{{ fmtPct(data.performance.on_time_rate) }}</span>
          <CheckCircle2 v-if="passesLateness(data) === true" class="h-3.5 w-3.5 text-emerald-500" />
          <XCircle v-else-if="passesLateness(data) === false" class="h-3.5 w-3.5 text-berry" />
        </div>
      </div>

      <!-- Revision rate -->
      <div v-if="data.performance.revision_rate !== null" class="flex items-center justify-between text-xs">
        <span class="text-graphite">Revision rate</span>
        <div class="flex items-center gap-1.5">
          <span class="font-semibold text-ink">{{ fmtPct(data.performance.revision_rate) }}</span>
          <span v-if="data.criteria.max_revision_rate" class="text-graphite">
            (max {{ fmtPct(data.criteria.max_revision_rate) }})
          </span>
          <CheckCircle2 v-if="passesRevision(data) === true" class="h-3.5 w-3.5 text-emerald-500" />
          <XCircle v-else-if="passesRevision(data) === false" class="h-3.5 w-3.5 text-berry" />
        </div>
      </div>
    </div>

    <!-- Next level requirements -->
    <div v-if="data.next" class="border-t border-slate-200 px-5 py-4 space-y-3 bg-slate-50">
      <div class="flex items-center gap-2">
        <ArrowRight class="h-3.5 w-3.5 text-signal" />
        <p class="text-xs font-semibold text-ink">To reach {{ data.next.name }}</p>
      </div>

      <div class="grid grid-cols-2 gap-2 text-xs">
        <div
          v-if="data.next.criteria.min_orders_completed"
          class="flex items-center gap-1.5 rounded-md border px-2.5 py-1.5"
          :class="meetsNextCriteria('orders', data) ? 'border-emerald-200 bg-emerald-50 text-emerald-800' : 'border-slate-200 bg-white text-graphite'"
        >
          <CheckCircle2 v-if="meetsNextCriteria('orders', data)" class="h-3 w-3 text-emerald-500 shrink-0" />
          <span v-else class="h-3 w-3 shrink-0 rounded-full border border-slate-300" />
          {{ data.next.criteria.min_orders_completed }}+ orders
        </div>

        <div
          v-if="data.next.criteria.min_completion_rate"
          class="flex items-center gap-1.5 rounded-md border px-2.5 py-1.5"
          :class="meetsNextCriteria('completion', data) ? 'border-emerald-200 bg-emerald-50 text-emerald-800' : 'border-slate-200 bg-white text-graphite'"
        >
          <CheckCircle2 v-if="meetsNextCriteria('completion', data)" class="h-3 w-3 text-emerald-500 shrink-0" />
          <span v-else class="h-3 w-3 shrink-0 rounded-full border border-slate-300" />
          {{ fmtPct(data.next.criteria.min_completion_rate) }} completion
        </div>

        <div
          v-if="data.next.criteria.max_revision_rate"
          class="flex items-center gap-1.5 rounded-md border px-2.5 py-1.5"
          :class="meetsNextCriteria('revision', data) ? 'border-emerald-200 bg-emerald-50 text-emerald-800' : 'border-slate-200 bg-white text-graphite'"
        >
          <CheckCircle2 v-if="meetsNextCriteria('revision', data)" class="h-3 w-3 text-emerald-500 shrink-0" />
          <span v-else class="h-3 w-3 shrink-0 rounded-full border border-slate-300" />
          ≤{{ fmtPct(data.next.criteria.max_revision_rate) }} revisions
        </div>

        <div
          v-if="data.next.criteria.max_lateness_rate"
          class="flex items-center gap-1.5 rounded-md border px-2.5 py-1.5"
          :class="meetsNextCriteria('lateness', data) ? 'border-emerald-200 bg-emerald-50 text-emerald-800' : 'border-slate-200 bg-white text-graphite'"
        >
          <CheckCircle2 v-if="meetsNextCriteria('lateness', data)" class="h-3 w-3 text-emerald-500 shrink-0" />
          <span v-else class="h-3 w-3 shrink-0 rounded-full border border-slate-300" />
          ≤{{ fmtPct(data.next.criteria.max_lateness_rate) }} late
        </div>
      </div>
    </div>

    <!-- Top level — no next -->
    <div
      v-else-if="data.current"
      class="border-t border-slate-100 px-5 py-3 bg-emerald-50 text-xs font-medium text-emerald-800"
    >
      You're at the highest writer level. Keep it up!
    </div>

  </div>
</template>

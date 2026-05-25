<script setup lang="ts">
import { onMounted } from "vue";
import { BarChart3, RefreshCw, ShieldAlert, Users } from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useAdminAnalyticsStore } from "@/stores/adminAnalytics";

const analytics = useAdminAnalyticsStore();

function money(value: number | string | undefined | null) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(Number(value ?? 0));
}

function percent(value: number | string | undefined | null) {
  return `${Number(value ?? 0).toFixed(1)}%`;
}

function numberLabel(value: number | string | undefined | null) {
  return new Intl.NumberFormat("en-US").format(Number(value ?? 0));
}

onMounted(() => {
  analytics.hydrate().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Admin</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Analytics</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          Operational signals across clients, writers, and class cohorts.
        </p>
      </div>
      <div class="flex flex-wrap gap-2">
        <button
          class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-300 px-4 text-sm font-semibold text-ink disabled:cursor-not-allowed disabled:opacity-60"
          type="button"
          :disabled="analytics.isLoading"
          @click="analytics.hydrate()"
        >
          <RefreshCw class="h-4 w-4" />
          Refresh
        </button>
        <button
          class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md bg-ink px-4 text-sm font-semibold text-white"
          type="button"
          @click="analytics.markReviewed()"
        >
          Review
        </button>
      </div>
    </section>

    <div v-if="analytics.error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
      {{ analytics.error }}
    </div>
    <div v-if="analytics.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900">
      {{ analytics.notice }}
    </div>

    <section class="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      <div class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
        <p class="text-sm font-medium text-graphite">Revenue observed</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ money(analytics.totalRevenue) }}</p>
        <p class="mt-2 text-sm text-graphite">From client analytics</p>
      </div>
      <div class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
        <p class="text-sm font-medium text-graphite">Orders observed</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ numberLabel(analytics.totalOrders) }}</p>
        <p class="mt-2 text-sm text-graphite">Across sampled clients</p>
      </div>
      <div class="rounded-md border border-emerald-200 bg-emerald-50 p-4 shadow-panel">
        <p class="text-sm font-medium text-emerald-900">On-time delivery</p>
        <p class="mt-3 text-3xl font-semibold text-emerald-950">{{ percent(analytics.averageOnTimeRate) }}</p>
        <p class="mt-2 text-sm text-emerald-900">Average client rate</p>
      </div>
      <div class="rounded-md border border-amber-200 bg-amber-50 p-4 shadow-panel">
        <p class="text-sm font-medium text-amber-900">Writer risk</p>
        <p class="mt-3 text-3xl font-semibold text-amber-950">{{ analytics.riskWriters.length }}</p>
        <p class="mt-2 text-sm text-amber-900">Revision/rejection watchlist</p>
      </div>
    </section>

    <section class="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
      <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <div class="flex items-center justify-between gap-3">
          <div>
            <h2 class="text-lg font-semibold text-ink">Client performance</h2>
            <p class="mt-1 text-sm text-graphite">Spend, delivery, and revision behavior by client period.</p>
          </div>
          <BarChart3 class="h-5 w-5 text-signal" />
        </div>

        <div class="mt-5 overflow-hidden rounded-md border border-slate-200">
          <div class="grid grid-cols-[1fr_120px_100px_100px_100px] gap-3 bg-slate-50 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
            <span>Client</span>
            <span>Spend</span>
            <span>Orders</span>
            <span>On-time</span>
            <span>Revision</span>
          </div>
          <div v-if="analytics.isLoading" class="px-4 py-6 text-sm text-graphite">Loading analytics...</div>
          <div v-else-if="!analytics.clients.length" class="px-4 py-6 text-sm text-graphite">No client analytics loaded.</div>
          <div
            v-for="client in analytics.clients"
            v-else
            :key="client.id"
            class="grid grid-cols-[1fr_120px_100px_100px_100px] items-center gap-3 border-t border-slate-100 px-4 py-3 text-sm"
          >
            <div>
              <p class="font-semibold text-ink">{{ client.client_name || client.client_email || `Client #${client.client}` }}</p>
              <p class="mt-1 text-xs text-graphite">{{ client.period_start }} to {{ client.period_end }}</p>
            </div>
            <span class="font-semibold text-ink">{{ money(client.total_spend) }}</span>
            <span class="text-graphite">{{ numberLabel(client.total_orders) }}</span>
            <span class="text-graphite">{{ percent(client.on_time_delivery_rate) }}</span>
            <span class="text-graphite">{{ percent(client.revision_rate) }}</span>
          </div>
        </div>
      </div>

      <div class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
        <div class="flex items-center justify-between gap-3">
          <div>
            <h2 class="text-lg font-semibold text-ink">Writer quality</h2>
            <p class="mt-1 text-sm text-graphite">Quality score, approvals, revisions, and earnings signals.</p>
          </div>
          <ShieldAlert class="h-5 w-5 text-saffron" />
        </div>

        <div class="mt-5 space-y-3">
          <p v-if="!analytics.writers.length" class="text-sm text-graphite">No writer analytics loaded.</p>
          <article
            v-for="writer in analytics.writers"
            :key="writer.id"
            class="rounded-md border border-slate-200 p-4"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="text-sm font-semibold text-ink">{{ writer.writer_name || writer.writer_email || `Writer #${writer.writer}` }}</p>
                <p class="mt-1 text-xs text-graphite">{{ money(writer.total_earnings) }} earned · {{ numberLabel(writer.total_orders_completed) }} completed</p>
              </div>
              <StatusPill
                :label="`Q ${numberLabel(writer.quality_score)}`"
                :tone="Number(writer.quality_score) >= 85 ? 'success' : 'warning'"
              />
            </div>
            <div class="mt-4 grid grid-cols-3 gap-3 text-sm">
              <div>
                <p class="text-xs text-graphite">Approval</p>
                <p class="font-semibold text-ink">{{ percent(writer.approval_rate) }}</p>
              </div>
              <div>
                <p class="text-xs text-graphite">Revision</p>
                <p class="font-semibold text-ink">{{ percent(writer.revision_rate) }}</p>
              </div>
              <div>
                <p class="text-xs text-graphite">Hourly</p>
                <p class="font-semibold text-ink">{{ money(writer.effective_hourly_rate) }}</p>
              </div>
            </div>
          </article>
        </div>
      </div>
    </section>

    <section class="rounded-lg border border-slate-200 bg-white p-5 shadow-panel">
      <div class="flex items-center gap-2">
        <Users class="h-5 w-5 text-signal" />
        <h2 class="text-lg font-semibold text-ink">Class cohorts</h2>
      </div>
      <div class="mt-5 grid gap-4 lg:grid-cols-2">
        <article
          v-for="cohort in analytics.classes"
          :key="cohort.id"
          class="rounded-md border border-slate-200 p-4"
        >
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-sm font-semibold text-ink">{{ cohort.class_name }}</p>
              <p class="mt-1 text-xs text-graphite">{{ cohort.class_id || "No class id" }} · {{ cohort.reports_count ?? 0 }} reports</p>
            </div>
            <StatusPill :label="`${percent(cohort.completion_rate)} complete`" />
          </div>
          <div class="mt-4 grid grid-cols-4 gap-3 text-sm">
            <div>
              <p class="text-xs text-graphite">Students</p>
              <p class="font-semibold text-ink">{{ cohort.active_students }}/{{ cohort.total_students }}</p>
            </div>
            <div>
              <p class="text-xs text-graphite">Orders</p>
              <p class="font-semibold text-ink">{{ cohort.completed_orders }}/{{ cohort.total_orders }}</p>
            </div>
            <div>
              <p class="text-xs text-graphite">On-time</p>
              <p class="font-semibold text-ink">{{ percent(cohort.on_time_submission_rate) }}</p>
            </div>
            <div>
              <p class="text-xs text-graphite">Grade</p>
              <p class="font-semibold text-ink">{{ numberLabel(cohort.average_grade) }}</p>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { ArrowRight, Clock3 } from "@lucide/vue";
import { dashboards } from "@/config/dashboard";
import MetricTile from "@/components/ui/MetricTile.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import type { UserRole } from "@/types/roles";

const props = defineProps<{
  role: UserRole;
}>();

const dashboard = computed(() => dashboards[props.role]);
</script>

<template>
  <div class="space-y-6">
    <section class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase text-signal">{{ role }}</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">{{ dashboard.title }}</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          {{ dashboard.subtitle }}
        </p>
      </div>
      <button
        class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md bg-ink px-4 text-sm font-semibold text-white"
        type="button"
      >
        {{ dashboard.primaryAction }}
        <ArrowRight class="h-4 w-4" />
      </button>
    </section>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <MetricTile
        v-for="metric in dashboard.metrics"
        :key="metric.label"
        :metric="metric"
      />
    </section>

    <section class="grid gap-5 xl:grid-cols-[minmax(0,1.5fr)_minmax(320px,0.8fr)]">
      <div class="rounded-md border border-slate-200 bg-white shadow-panel">
        <div class="flex min-h-14 items-center justify-between border-b border-slate-200 px-4">
          <h2 class="text-base font-semibold">Priority work</h2>
          <Clock3 class="h-4 w-4 text-slate-400" />
        </div>
        <div class="divide-y divide-slate-100">
          <article
            v-for="item in dashboard.work"
            :key="item.title"
            class="grid gap-3 px-4 py-4 sm:grid-cols-[minmax(0,1fr)_auto]"
          >
            <div>
              <h3 class="text-sm font-semibold text-ink">{{ item.title }}</h3>
              <p class="mt-1 text-sm text-graphite">{{ item.meta }}</p>
            </div>
            <StatusPill :label="item.status" />
          </article>
        </div>
      </div>

      <div class="rounded-md border border-slate-200 bg-white shadow-panel">
        <div class="flex min-h-14 items-center border-b border-slate-200 px-4">
          <h2 class="text-base font-semibold">Next surfaces</h2>
        </div>
        <div class="space-y-3 p-4">
          <div
            v-for="panel in dashboard.panels"
            :key="panel"
            class="rounded-md border border-slate-200 bg-slate-50 p-3"
          >
            <p class="text-sm font-semibold">{{ panel }}</p>
            <p class="mt-1 text-sm text-graphite">
              Backend endpoint mapping and detailed table/form states come next.
            </p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

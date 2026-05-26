<script setup lang="ts">
import { onMounted } from "vue";
import { useRouter } from "vue-router";
import { ArrowRight, Clock3 } from "@lucide/vue";
import MetricTile from "@/components/ui/MetricTile.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { dashboards } from "@/config/dashboard";
import { navigationByRole } from "@/config/navigation";
import { useDashboardData } from "@/composables/useDashboardData";
import type { UserRole } from "@/types/roles";

const props = defineProps<{ role: UserRole }>();

const router = useRouter();
const dashboard = dashboards[props.role];
const navItems = navigationByRole[props.role];
const { isLoading, error, metrics, workItems, primaryActionTo, load } = useDashboardData(props.role);

onMounted(() => {
  load().catch(() => undefined);
});
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
        @click="router.push(primaryActionTo)"
      >
        {{ dashboard.primaryAction }}
        <ArrowRight class="h-4 w-4" />
      </button>
    </section>

    <p
      v-if="error"
      class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {{ error }} Some metrics may show defaults until the backend is reachable.
    </p>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <template v-if="isLoading">
        <div
          v-for="n in 4"
          :key="n"
          class="min-h-32 animate-pulse rounded-md border border-slate-200 bg-white p-4 shadow-panel"
          aria-hidden="true"
        >
          <div class="h-3 w-24 rounded bg-slate-200" />
          <div class="mt-4 h-7 w-20 rounded bg-slate-100" />
          <div class="mt-3 h-3 w-36 rounded bg-slate-100" />
        </div>
      </template>
      <template v-else>
        <MetricTile
          v-for="metric in metrics"
          :key="metric.label"
          :metric="metric"
        />
      </template>
    </section>

    <section class="grid gap-5 xl:grid-cols-[minmax(0,1.5fr)_minmax(320px,0.8fr)]">
      <div class="rounded-md border border-slate-200 bg-white shadow-panel">
        <div class="flex min-h-14 items-center justify-between border-b border-slate-200 px-4">
          <h2 class="text-base font-semibold">Priority work</h2>
          <Clock3 class="h-4 w-4 text-slate-400" />
        </div>
        <div v-if="isLoading" class="animate-pulse divide-y divide-slate-100" aria-hidden="true">
          <div v-for="n in 3" :key="n" class="px-4 py-4">
            <div class="h-4 w-3/4 rounded bg-slate-100" />
            <div class="mt-2 h-4 w-1/2 rounded bg-slate-100" />
          </div>
        </div>
        <div v-else-if="workItems.length" class="divide-y divide-slate-100">
          <article
            v-for="item in workItems"
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
        <div v-else class="px-4 py-6 text-sm text-graphite">
          No active work to display.
        </div>
      </div>

      <div class="rounded-md border border-slate-200 bg-white shadow-panel">
        <div class="flex min-h-14 items-center border-b border-slate-200 px-4">
          <h2 class="text-base font-semibold">Quick navigation</h2>
        </div>
        <div class="space-y-1 p-3">
          <RouterLink
            v-for="item in navItems.slice(0, 6)"
            :key="item.to"
            :to="item.to"
            class="focus-ring flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium text-graphite hover:bg-slate-50 hover:text-ink"
          >
            <component :is="item.icon" class="h-4 w-4 shrink-0" aria-hidden="true" />
            <span>{{ item.label }}</span>
            <ArrowRight class="ml-auto h-3.5 w-3.5 text-slate-300" />
          </RouterLink>
        </div>
      </div>
    </section>
  </div>
</template>

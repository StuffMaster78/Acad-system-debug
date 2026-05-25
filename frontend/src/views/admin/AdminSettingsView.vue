<script setup lang="ts">
import { onMounted } from "vue";
import {
  Bell,
  CreditCard,
  Percent,
  RefreshCw,
  Settings,
  ShieldAlert,
  SlidersHorizontal,
  UserCog,
} from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useAdminSettingsStore } from "@/stores/adminSettings";

const settings = useAdminSettingsStore();

const metricToneClasses = {
  neutral: "border-slate-200 bg-white",
  good: "border-emerald-200 bg-emerald-50",
  warn: "border-amber-200 bg-amber-50",
  risk: "border-rose-200 bg-rose-50",
};

const icons = {
  pricing: CreditCard,
  writer: UserCog,
  discount: Percent,
  notifications: Bell,
};

function nameFor(item: Record<string, unknown>) {
  return String(item.name ?? item.title ?? item.code ?? `Config #${item.id ?? "new"}`);
}

function statusFor(item: Record<string, unknown>) {
  if (item.is_active === false) return "inactive";
  return "active";
}

onMounted(() => {
  settings.hydrate().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-8">
    <section class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase text-signal">Admin</p>
        <h1 class="mt-2 text-3xl font-semibold">Settings & configuration</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          Platform controls for pricing, writer rules, discounts, notification profiles,
          order dropdown defaults, screened words, and configuration health.
        </p>
      </div>
      <button
        class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
        type="button"
        @click="settings.hydrate"
      >
        <RefreshCw class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <p
      v-if="settings.error"
      class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {{ settings.error }} Preview mode will still show the layout.
    </p>

    <p
      v-if="settings.notice"
      class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900"
    >
      {{ settings.notice }}
    </p>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div
        v-for="metric in settings.metrics"
        :key="metric.label"
        class="min-h-32 rounded-md border p-4 shadow-panel"
        :class="metricToneClasses[metric.tone]"
      >
        <p class="text-sm font-medium text-graphite">{{ metric.label }}</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ metric.value }}</p>
        <p class="mt-2 text-sm leading-5 text-graphite">{{ metric.detail }}</p>
      </div>
    </section>

    <section class="grid gap-6 xl:grid-cols-[minmax(0,1.3fr)_minmax(360px,0.8fr)]">
      <div class="grid gap-4 md:grid-cols-2">
        <section
          v-for="group in settings.groups"
          :key="group.key"
          class="rounded-md border border-slate-200 bg-white p-4 shadow-panel"
        >
          <div class="flex items-start gap-3">
            <div class="flex h-10 w-10 items-center justify-center rounded-md bg-mist text-signal">
              <component :is="icons[group.key as keyof typeof icons]" class="h-5 w-5" />
            </div>
            <div>
              <h2 class="text-base font-semibold">{{ group.label }}</h2>
              <p class="mt-1 text-sm leading-5 text-graphite">{{ group.description }}</p>
            </div>
          </div>

          <div class="mt-4 space-y-2">
            <article
              v-for="item in group.items.slice(0, 4)"
              :key="`${group.key}-${item.id ?? nameFor(item)}`"
              class="flex items-center justify-between gap-3 rounded-md border border-slate-200 p-3"
            >
              <div>
                <p class="text-sm font-semibold text-ink">{{ nameFor(item) }}</p>
                <p class="mt-1 text-xs text-graphite">{{ item.website ?? "Global" }}</p>
              </div>
              <StatusPill
                :label="statusFor(item)"
                :tone="statusFor(item) === 'active' ? 'success' : 'neutral'"
              />
            </article>
            <p v-if="!group.items.length" class="rounded-md border border-slate-200 p-3 text-sm text-graphite">
              No configs loaded yet.
            </p>
          </div>
        </section>
      </div>

      <aside class="space-y-6">
        <section class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
          <div class="flex items-center gap-2">
            <SlidersHorizontal class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold">Order configuration</h2>
          </div>
          <dl class="mt-4 grid grid-cols-2 gap-3 text-sm">
            <div class="rounded-md border border-slate-200 p-3">
              <dt class="text-graphite">Total</dt>
              <dd class="mt-1 text-xl font-semibold text-ink">{{ settings.orderConfigUsage.total_configs }}</dd>
            </div>
            <div class="rounded-md border border-slate-200 p-3">
              <dt class="text-graphite">Unused</dt>
              <dd class="mt-1 text-xl font-semibold text-ink">{{ settings.orderConfigUsage.unused_configs }}</dd>
            </div>
          </dl>
          <button
            class="focus-ring mt-4 inline-flex h-10 w-full items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold"
            type="button"
            :disabled="settings.isMutating"
            @click="settings.checkDefaults().catch(() => undefined)"
          >
            <Settings class="h-4 w-4" />
            Check defaults
          </button>
        </section>

        <section class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
          <div class="flex items-center gap-2">
            <ShieldAlert class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold">Screening health</h2>
          </div>
          <div class="mt-4 space-y-3 text-sm">
            <div class="rounded-md border border-slate-200 p-3">
              <p class="font-semibold text-ink">{{ settings.screenedWordStats.total_screened_words }} screened words</p>
              <p class="mt-1 text-graphite">{{ settings.screenedWordStats.total_flagged_messages }} total flagged messages</p>
            </div>
            <div class="rounded-md border border-slate-200 p-3">
              <p class="font-semibold text-ink">{{ settings.screenedWordStats.flagged_last_7_days }} recent flags</p>
              <p class="mt-1 text-graphite">Moderation pressure in the last 7 days.</p>
            </div>
          </div>
        </section>

        <section class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
          <h2 class="text-base font-semibold">Default sets</h2>
          <div class="mt-3 flex flex-wrap gap-2">
            <StatusPill
              v-for="set in settings.defaultSets"
              :key="set"
              :label="set"
            />
          </div>
        </section>
      </aside>
    </section>
  </div>
</template>

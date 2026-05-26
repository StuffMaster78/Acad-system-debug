<script setup lang="ts">
import { onMounted } from "vue";
import {
  Bell,
  CalendarDays,
  CreditCard,
  DatabaseZap,
  History,
  Percent,
  RefreshCw,
  Settings,
  ShieldAlert,
  SlidersHorizontal,
  UserCog,
} from "@lucide/vue";
import BaseDataTable, { type DataTableColumn } from "@/components/ui/BaseDataTable.vue";
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

const configColumns: DataTableColumn[] = [
  { key: "name", label: "Config", sortable: true },
  { key: "website", label: "Website", sortable: true },
  { key: "status", label: "Status" },
  { key: "updated", label: "Updated", sortable: true },
];

const activityColumns: DataTableColumn[] = [
  { key: "action", label: "Action", sortable: true },
  { key: "admin", label: "Admin", sortable: true },
  { key: "timestamp", label: "Time", sortable: true },
];

function nameFor(item: Record<string, unknown>) {
  return String(item.name ?? item.title ?? item.code ?? `Config #${item.id ?? "new"}`);
}

function statusFor(item: Record<string, unknown>) {
  if (item.is_active === false) return "inactive";
  return "active";
}

function formatDate(value?: string | null) {
  if (!value) return "Not set";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function healthStatus() {
  return String(settings.systemHealth.status ?? "unknown");
}

function configRows() {
  return settings.filteredSelectedItems.map((item) => ({
    id: item.id ?? nameFor(item),
    name: nameFor(item),
    website: item.website ?? "Global",
    status: statusFor(item),
    updated: formatDate(String(item.updated_at ?? item.created_at ?? "")),
  }));
}

function activityRows() {
  return settings.activityLogs.map((log) => ({
    id: log.id,
    action: log.action,
    admin: log.admin_username || log.admin || "System",
    timestamp: formatDate(log.timestamp),
  }));
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
      <div class="space-y-6">
        <section class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
          <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <div class="flex items-center gap-2">
                <DatabaseZap class="h-5 w-5 text-signal" />
                <h2 class="text-base font-semibold">Configuration workbench</h2>
              </div>
              <p class="mt-1 max-w-2xl text-sm leading-6 text-graphite">
                Browse pricing, writer, discount, and notification records from the backend configuration APIs.
              </p>
            </div>
            <label class="block min-w-72">
              <span class="text-xs font-semibold uppercase text-graphite">Search configs</span>
              <input
                v-model="settings.query"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="search"
                placeholder="Search name, website, code"
              >
            </label>
          </div>

          <div class="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <button
              v-for="group in settings.groups"
              :key="group.key"
              class="focus-ring rounded-md border p-3 text-left"
              :class="settings.selectedGroupKey === group.key ? 'border-signal bg-mist' : 'border-slate-200 bg-white'"
              type="button"
              @click="settings.selectedGroupKey = group.key"
            >
              <div class="flex items-center gap-2">
                <component :is="icons[group.key]" class="h-4 w-4 text-signal" />
                <span class="text-sm font-semibold text-ink">{{ group.label }}</span>
              </div>
              <p class="mt-2 text-2xl font-semibold text-ink">{{ group.count }}</p>
              <p class="mt-1 text-xs leading-5 text-graphite">{{ group.description }}</p>
            </button>
          </div>

          <BaseDataTable
            class="mt-4 shadow-none"
            :columns="configColumns"
            :rows="configRows()"
            :searchable="false"
            :loading="settings.isLoading"
            empty-title="No configs loaded"
            empty-message="This group has no records yet or the backend endpoint is unavailable."
          >
            <template #cell-status="{ value }">
              <StatusPill
                :label="String(value)"
                :tone="String(value) === 'active' ? 'success' : 'neutral'"
              />
            </template>
          </BaseDataTable>
        </section>

        <section class="grid gap-6 xl:grid-cols-2">
          <section class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
            <div class="flex items-center gap-2">
              <ShieldAlert class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold">Screened words</h2>
            </div>
            <p class="mt-1 text-sm leading-6 text-graphite">
              Add moderation terms in bulk. Separate words with commas or new lines.
            </p>
            <textarea
              v-model="settings.screenedWordDraft"
              class="focus-ring mt-4 min-h-28 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
            />
            <button
              class="focus-ring mt-3 inline-flex h-10 items-center justify-center rounded-md bg-ink px-4 text-sm font-semibold text-white"
              type="button"
              :disabled="settings.isMutating"
              @click="settings.bulkCreateScreenedWords().catch(() => undefined)"
            >
              Add screened words
            </button>
            <div class="mt-4 flex flex-wrap gap-2">
              <StatusPill
                v-for="word in settings.screenedWords.slice(0, 12)"
                :key="word.id ?? word.word"
                :label="word.word"
                tone="warning"
              />
            </div>
          </section>

          <section class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
            <div class="flex items-center gap-2">
              <CalendarDays class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold">Holiday rules</h2>
            </div>
            <div class="mt-4 grid gap-3 sm:grid-cols-2">
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Name</span>
                <input
                  v-model="settings.specialDayForm.name"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  type="text"
                >
              </label>
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Date</span>
                <input
                  v-model="settings.specialDayForm.date"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  type="date"
                >
              </label>
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Type</span>
                <select
                  v-model="settings.specialDayForm.event_type"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                >
                  <option value="holiday">Holiday</option>
                  <option value="special_day">Special day</option>
                  <option value="seasonal">Seasonal</option>
                  <option value="cultural">Cultural</option>
                </select>
              </label>
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Priority</span>
                <select
                  v-model="settings.specialDayForm.priority"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </label>
            </div>
            <div class="mt-3 flex flex-wrap gap-3">
              <label class="flex min-h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm">
                <input v-model="settings.specialDayForm.is_annual" type="checkbox">
                Annual
              </label>
              <label class="flex min-h-10 items-center gap-2 rounded-md border border-slate-200 px-3 text-sm">
                <input v-model="settings.specialDayForm.is_international" type="checkbox">
                International
              </label>
            </div>
            <button
              class="focus-ring mt-3 inline-flex h-10 items-center justify-center rounded-md bg-ink px-4 text-sm font-semibold text-white"
              type="button"
              :disabled="settings.isMutating"
              @click="settings.createSpecialDay().catch(() => undefined)"
            >
              Create special day
            </button>
          </section>
        </section>
      </div>

      <aside class="space-y-6">
        <section class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
          <div class="flex items-center justify-between gap-3">
            <div class="flex items-center gap-2">
              <DatabaseZap class="h-5 w-5 text-signal" />
              <h2 class="text-base font-semibold">System health</h2>
            </div>
            <StatusPill
              :label="healthStatus()"
              :tone="healthStatus() === 'healthy' ? 'success' : settings.systemAlerts.length ? 'danger' : 'warning'"
            />
          </div>
          <div class="mt-4 space-y-3 text-sm">
            <div
              v-for="alert in settings.systemAlerts.slice(0, 4)"
              :key="String(typeof alert === 'string' ? alert : alert.message ?? alert.type ?? JSON.stringify(alert))"
              class="rounded-md border border-rose-200 bg-rose-50 p-3 text-rose-900"
            >
              {{ typeof alert === "string" ? alert : alert.message ?? alert.type ?? JSON.stringify(alert) }}
            </div>
            <p v-if="!settings.systemAlerts.length" class="rounded-md border border-emerald-200 bg-emerald-50 p-3 text-emerald-900">
              No active system alerts.
            </p>
          </div>
        </section>

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
          <div class="mt-4 grid gap-2">
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Website ID</span>
              <input
                v-model.number="settings.defaultPopulationForm.website_id"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="number"
                min="1"
              >
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Default set</span>
              <select
                v-model="settings.defaultPopulationForm.default_set"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
              >
                <option value="">Backend default</option>
                <option
                  v-for="set in settings.defaultSets"
                  :key="set"
                  :value="set"
                >
                  {{ set }}
                </option>
              </select>
            </label>
            <button
              class="focus-ring inline-flex h-10 w-full items-center justify-center gap-2 rounded-md bg-ink px-3 text-sm font-semibold text-white"
              type="button"
              :disabled="settings.isMutating"
              @click="settings.populateDefaults().catch(() => undefined)"
            >
              Populate defaults
            </button>
          </div>
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

        <section class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
          <div class="flex items-center gap-2">
            <History class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold">Recent admin activity</h2>
          </div>
          <BaseDataTable
            class="mt-4 shadow-none"
            :columns="activityColumns"
            :rows="activityRows()"
            :searchable="false"
            :loading="settings.isLoading"
            empty-title="No activity logs"
            empty-message="Admin activity will appear here after backend data loads."
          />
        </section>
      </aside>
    </section>
  </div>
</template>

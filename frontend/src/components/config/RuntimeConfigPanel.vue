<script setup lang="ts">
import { computed, ref } from "vue";
import { RotateCcw, Save, RefreshCw } from "@lucide/vue";
import { useRuntimeConfigStore } from "@/stores/runtimeConfig";
import type { RegistryEntry } from "@/stores/runtimeConfig";

const store = useRuntimeConfigStore();

const DOMAIN_LABELS: Record<string, string> = {
  system: "System",
  auth: "Authentication",
  notifications: "Notifications",
  payments: "Payments",
  orders: "Orders",
  writer: "Writer",
  wallet: "Wallet",
  files: "Files",
  referrals: "Referrals",
  security: "Security",
  feature: "Feature Flags",
  cache: "Cache",
  observability: "Observability",
};

// Pending edits: key → new value
const edits = ref<Record<string, unknown>>({});
const savingKey = ref<string | null>(null);

function isDirty(key: string) {
  return key in edits.value;
}

function getEditValue(key: string): unknown {
  return key in edits.value ? edits.value[key] : store.getValue(key);
}

function setEdit(key: string, value: unknown) {
  const current = store.getValue(key);
  if (value === current) {
    delete edits.value[key];
  } else {
    edits.value[key] = value;
  }
}

async function saveKey(key: string) {
  if (!isDirty(key)) return;
  savingKey.value = key;
  await store.save(key, edits.value[key]);
  delete edits.value[key];
  savingKey.value = null;
}

async function resetKey(key: string) {
  savingKey.value = key;
  await store.reset(key);
  delete edits.value[key];
  savingKey.value = null;
}

function typeLabel(entry: RegistryEntry): string {
  if (entry.config_type === "bool") return "toggle";
  if (entry.config_type === "int") return "int";
  return entry.config_type;
}

function shortKey(key: string): string {
  const parts = key.split(".");
  return parts.slice(1).join(".");
}

const activeDomain = ref<string>(store.domains[0] ?? "system");
const activeEntries = computed(() => store.byDomain[activeDomain.value] ?? []);
const dirtyCount = computed(() => Object.keys(edits.value).length);
</script>

<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-lg font-semibold text-ink">Runtime Controls</h2>
        <p class="mt-0.5 text-sm text-graphite">
          Live platform switches — changes take effect immediately without a restart (unless marked).
        </p>
      </div>
      <button
        class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-graphite hover:bg-slate-50 disabled:opacity-50"
        :disabled="store.isLoading"
        @click="store.load()"
      >
        <RefreshCw class="h-3.5 w-3.5" :class="store.isLoading ? 'animate-spin' : ''" />
        Refresh
      </button>
    </div>

    <!-- Notice / error -->
    <p v-if="store.error" class="rounded-md border border-rose-200 bg-rose-50 px-4 py-2.5 text-sm text-rose-800">
      {{ store.error }}
    </p>
    <p v-if="store.notice" class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-2.5 text-sm text-emerald-800">
      {{ store.notice }}
    </p>

    <div v-if="store.isLoading" class="py-16 text-center text-sm text-graphite animate-pulse">
      Loading runtime config…
    </div>

    <div v-else class="grid gap-4 lg:grid-cols-[200px_1fr]">
      <!-- Domain sidebar -->
      <nav class="flex flex-row flex-wrap gap-1 lg:flex-col">
        <button
          v-for="domain in store.domains"
          :key="domain"
          class="flex items-center justify-between rounded-lg px-3 py-2 text-left text-sm font-medium transition-colors"
          :class="activeDomain === domain
            ? 'bg-ink text-white'
            : 'text-graphite hover:bg-slate-100 hover:text-ink'"
          @click="activeDomain = domain"
        >
          <span>{{ DOMAIN_LABELS[domain] ?? domain }}</span>
          <span
            v-if="store.byDomain[domain]?.some(e => store.overriddenKeys.has(e.key))"
            class="ml-2 h-1.5 w-1.5 shrink-0 rounded-full"
            :class="activeDomain === domain ? 'bg-white' : 'bg-signal'"
          />
        </button>
      </nav>

      <!-- Config table -->
      <div class="rounded-xl border border-slate-200 bg-white">
        <div class="border-b border-slate-200 px-5 py-3">
          <p class="text-sm font-semibold text-ink">{{ DOMAIN_LABELS[activeDomain] ?? activeDomain }}</p>
          <p class="text-xs text-graphite">{{ activeEntries.length }} settings</p>
        </div>

        <div class="divide-y divide-slate-100">
          <div
            v-for="entry in activeEntries"
            :key="entry.key"
            class="flex items-start gap-4 px-5 py-4"
            :class="isDirty(entry.key) ? 'bg-amber-50/40' : ''"
          >
            <!-- Description -->
            <div class="min-w-0 flex-1">
              <div class="flex flex-wrap items-center gap-2">
                <p class="font-mono text-xs font-semibold text-ink">{{ shortKey(entry.key) }}</p>
                <span
                  v-if="store.overriddenKeys.has(entry.key)"
                  class="rounded-full bg-emerald-100 px-1.5 py-0.5 text-[10px] font-semibold text-emerald-700"
                >overridden</span>
                <span
                  v-if="entry.requires_restart"
                  class="rounded-full bg-amber-100 px-1.5 py-0.5 text-[10px] font-semibold text-amber-700"
                >restart required</span>
                <span
                  v-if="!entry.is_runtime_editable"
                  class="rounded-full bg-slate-100 px-1.5 py-0.5 text-[10px] font-semibold text-slate-500"
                >read-only</span>
              </div>
              <p class="mt-0.5 text-xs text-graphite">{{ entry.description }}</p>
              <p class="mt-0.5 font-mono text-[10px] text-slate-400">default: {{ String(entry.default) }}</p>
            </div>

            <!-- Control -->
            <div class="flex shrink-0 items-center gap-2">
              <!-- Boolean toggle -->
              <template v-if="entry.config_type === 'bool'">
                <button
                  class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-signal"
                  :class="getEditValue(entry.key) ? 'bg-signal' : 'bg-slate-300'"
                  :disabled="!entry.is_runtime_editable || store.isSaving"
                  role="switch"
                  :aria-checked="Boolean(getEditValue(entry.key))"
                  @click="entry.is_runtime_editable && setEdit(entry.key, !getEditValue(entry.key))"
                >
                  <span
                    class="pointer-events-none inline-block h-5 w-5 translate-x-0 rounded-full bg-white shadow ring-0 transition-transform"
                    :class="getEditValue(entry.key) ? 'translate-x-5' : 'translate-x-0'"
                  />
                </button>
              </template>

              <!-- Integer / float input -->
              <template v-else-if="entry.config_type === 'int' || entry.config_type === 'float'">
                <input
                  class="focus-ring h-8 w-24 rounded-md border border-slate-200 px-2 text-right text-sm"
                  :class="isDirty(entry.key) ? 'border-amber-300 bg-amber-50' : ''"
                  :type="entry.config_type === 'int' ? 'number' : 'text'"
                  :step="entry.config_type === 'int' ? '1' : 'any'"
                  :disabled="!entry.is_runtime_editable || store.isSaving"
                  :value="getEditValue(entry.key)"
                  @input="setEdit(entry.key, entry.config_type === 'int' ? parseInt(($event.target as HTMLInputElement).value) : parseFloat(($event.target as HTMLInputElement).value))"
                />
              </template>

              <!-- String input -->
              <template v-else>
                <input
                  class="focus-ring h-8 w-40 rounded-md border border-slate-200 px-2 text-sm"
                  :class="isDirty(entry.key) ? 'border-amber-300 bg-amber-50' : ''"
                  type="text"
                  :disabled="!entry.is_runtime_editable || store.isSaving"
                  :value="String(getEditValue(entry.key) ?? '')"
                  @input="setEdit(entry.key, ($event.target as HTMLInputElement).value)"
                />
              </template>

              <!-- Save button (shown when dirty) -->
              <button
                v-if="isDirty(entry.key)"
                class="focus-ring inline-flex h-8 items-center gap-1 rounded-md bg-ink px-2.5 text-xs font-semibold text-white hover:bg-slate-800 disabled:opacity-50"
                :disabled="store.isSaving"
                @click="saveKey(entry.key)"
              >
                <Save class="h-3 w-3" />
                Save
              </button>

              <!-- Reset button (shown when overridden and not dirty) -->
              <button
                v-else-if="store.overriddenKeys.has(entry.key)"
                class="focus-ring inline-flex h-8 items-center gap-1 rounded-md border border-slate-200 px-2 text-xs text-graphite hover:bg-slate-50 disabled:opacity-50"
                :disabled="store.isSaving"
                title="Reset to default"
                @click="resetKey(entry.key)"
              >
                <RotateCcw class="h-3 w-3" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Unsaved changes footer -->
    <div v-if="dirtyCount > 0" class="rounded-xl border border-amber-200 bg-amber-50 px-5 py-3 text-sm text-amber-800">
      {{ dirtyCount }} unsaved change{{ dirtyCount !== 1 ? 's' : '' }} — click Save on each field to apply.
    </div>
  </div>
</template>

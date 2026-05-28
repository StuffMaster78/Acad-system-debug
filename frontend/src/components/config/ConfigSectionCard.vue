<script setup lang="ts">
import { computed, ref } from "vue";
import { Check, Clock, History, RotateCcw, TriangleAlert } from "@lucide/vue";
import ConfigSettingRow from "./ConfigSettingRow.vue";
import { getSettingsForSection, scopeAllows } from "@/config/configDefinitions";
import { useAdminMasterConfigStore } from "@/stores/adminMasterConfig";
import { useAuthStore } from "@/stores/auth";
import type { ConfigSectionMeta } from "@/types/config";

const props = defineProps<{
  domain: string;
  section: ConfigSectionMeta;
}>();

const config = useAdminMasterConfigStore();
const auth = useAuthStore();

const definitions = computed(() => getSettingsForSection(props.domain, props.section.key));
const isDirty = computed(() => config.isSectionDirty(props.domain, props.section.key));
const isSaving = computed(() => config.savingSection === `${props.domain}:${props.section.key}`);
const isReadonly = computed(() => !scopeAllows(auth.role ?? "support", props.section.requiredScope));

const scopeColors: Record<string, string> = {
  superadmin: "bg-rose-50 text-rose-700",
  admin:      "bg-amber-50 text-amber-700",
  editor:     "bg-sky-50 text-sky-700",
  support:    "bg-slate-100 text-graphite",
};

const scopeLabel: Record<string, string> = {
  superadmin: "Superadmin only",
  admin:      "Admin",
  editor:     "Editor",
  support:    "Support",
};

const showResetConfirm = ref(false);

function getDisplayValue(key: string): unknown {
  const dirty = config.getDirtyValue(props.domain, props.section.key, key);
  return dirty !== undefined ? dirty : config.getEffectiveValue(key) ?? getSettingsForSection(props.domain, props.section.key).find((d) => d.key === key)?.defaultValue;
}

function handleChange(key: string, value: unknown) {
  config.markDirty(props.domain, props.section.key, key, value);
}

function handleSave() {
  config.saveSection(props.domain, props.section.key);
}

function handleDiscard() {
  config.discardSection(props.domain, props.section.key);
}

function handleReset() {
  config.resetSection(props.domain, props.section.key);
  showResetConfirm.value = false;
}

function openAudit() {
  config.openAudit(props.domain, props.section.key);
}

function relativeTime(iso: string | null) {
  if (!iso) return null;
  const diff = Date.now() - new Date(iso).getTime();
  const min = Math.floor(diff / 60000);
  if (min < 1) return "just now";
  if (min < 60) return `${min}m ago`;
  const hr = Math.floor(min / 60);
  return hr < 24 ? `${hr}h ago` : `${Math.floor(hr / 24)}d ago`;
}

// Last changed for section = most recent across all its settings
const lastChanged = computed(() => {
  let latest: { by: string; at: string } | null = null;
  for (const def of definitions.value) {
    const v = config.configValues[def.key];
    if (v?.lastChangedAt && (!latest || v.lastChangedAt > latest.at)) {
      latest = { by: v.lastChangedBy ?? "Admin", at: v.lastChangedAt };
    }
  }
  return latest;
});
</script>

<template>
  <div
    class="overflow-hidden rounded-lg border transition-all"
    :class="isDirty ? 'border-amber-300' : 'border-slate-200 bg-white'"
  >
    <!-- Card header -->
    <div
      class="flex items-center justify-between gap-3 border-b px-5 py-3"
      :class="isDirty ? 'border-amber-200 bg-amber-50' : 'border-slate-100 bg-white'"
    >
      <div class="flex items-center gap-2 min-w-0">
        <h3 class="font-semibold text-ink text-sm truncate">{{ section.label }}</h3>

        <span v-if="isDirty" class="flex items-center gap-1 text-[10px] font-semibold text-amber-700 bg-amber-100 border border-amber-200 rounded px-1.5 py-0.5">
          <TriangleAlert class="size-3" /> Unsaved
        </span>

        <span
          class="rounded px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide"
          :class="scopeColors[section.requiredScope]"
        >{{ scopeLabel[section.requiredScope] }}</span>

        <span v-if="section.pendingBackend" class="rounded border border-slate-200 bg-slate-100 px-1.5 py-0.5 text-[10px] font-medium text-graphite">
          Pending backend
        </span>

        <span v-if="isReadonly" class="rounded border border-slate-200 bg-slate-50 px-1.5 py-0.5 text-[10px] text-graphite">
          Read-only
        </span>
      </div>

      <div class="flex items-center gap-1.5 shrink-0">
        <!-- Last changed -->
        <span v-if="lastChanged" class="hidden lg:flex items-center gap-1 text-[11px] text-graphite">
          <Clock class="size-3" />
          {{ lastChanged.by }} · {{ relativeTime(lastChanged.at) }}
        </span>

        <!-- Audit -->
        <button
          class="flex items-center gap-1 rounded px-2 py-1 text-xs text-graphite hover:bg-slate-100 hover:text-ink transition-colors"
          title="View audit history"
          @click="openAudit"
        >
          <History class="size-3.5" />
          <span class="hidden sm:inline">Audit</span>
        </button>

        <!-- Reset -->
        <div class="relative">
          <button
            v-if="!showResetConfirm"
            class="flex items-center gap-1 rounded px-2 py-1 text-xs text-graphite hover:bg-slate-100 hover:text-ink transition-colors"
            title="Reset to defaults"
            :disabled="isReadonly"
            @click="showResetConfirm = true"
          >
            <RotateCcw class="size-3.5" />
            <span class="hidden sm:inline">Reset</span>
          </button>
          <div v-else class="flex items-center gap-1">
            <span class="text-xs text-amber-700">Reset to defaults?</span>
            <button class="rounded bg-amber-600 px-2 py-1 text-xs text-white hover:bg-amber-700" @click="handleReset">Yes</button>
            <button class="rounded border border-slate-200 px-2 py-1 text-xs text-graphite hover:text-ink" @click="showResetConfirm = false">No</button>
          </div>
        </div>

        <!-- Discard / Save -->
        <template v-if="isDirty && !isReadonly">
          <button
            class="rounded border border-slate-200 px-2 py-1 text-xs text-graphite hover:text-ink transition-colors"
            @click="handleDiscard"
          >Discard</button>
          <button
            class="flex items-center gap-1 rounded bg-berry px-3 py-1 text-xs font-semibold text-white hover:bg-berry/90 disabled:opacity-60 transition-colors"
            :disabled="isSaving"
            @click="handleSave"
          >
            <Check class="size-3" />
            {{ isSaving ? "Saving…" : "Save" }}
          </button>
        </template>
      </div>
    </div>

    <!-- Settings rows -->
    <div class="divide-y divide-slate-50 p-4 space-y-2">
      <p v-if="definitions.length === 0 && !section.pendingBackend" class="py-4 text-center text-sm text-graphite">
        No settings defined for this section yet.
      </p>

      <div v-if="section.pendingBackend && definitions.length === 0" class="rounded-lg border border-dashed border-slate-200 bg-slate-50 px-4 py-6 text-center text-sm text-graphite">
        Settings for this section are being added as the backend endpoint is implemented.
      </div>

      <ConfigSettingRow
        v-for="def in definitions"
        :key="def.key"
        :definition="def"
        :model-value="getDisplayValue(def.key)"
        :saved-value="config.getEffectiveValue(def.key) ?? def.defaultValue"
        :last-changed-by="config.configValues[def.key]?.lastChangedBy ?? null"
        :last-changed-at="config.configValues[def.key]?.lastChangedAt ?? null"
        :is-overridden="config.isWebsiteOverridden(def.key)"
        :readonly="isReadonly || Boolean(def.pendingBackend)"
        :website-mode="config.selectedWebsite !== null"
        @update:model-value="handleChange(def.key, $event)"
      />
    </div>
  </div>
</template>

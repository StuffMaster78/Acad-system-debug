<script setup lang="ts">
import { ref, computed } from "vue";
import {
  ClipboardList,
  Cpu,
  CreditCard,
  DollarSign,
  FileText,
  Megaphone,
  MessageSquare,
  PenTool,
  ShieldCheck,
  Tag,
  TriangleAlert,
} from "@lucide/vue";
import { useAdminMasterConfigStore } from "@/stores/adminMasterConfig";
import { scopeAllows } from "@/config/configDefinitions";
import { useAuthStore } from "@/stores/auth";
import type { ConfigDomainMeta } from "@/types/config";

const config = useAdminMasterConfigStore();
const auth = useAuthStore();

const ICON_MAP: Record<string, unknown> = {
  ClipboardList,
  DollarSign,
  Tag,
  Megaphone,
  PenTool,
  CreditCard,
  MessageSquare,
  FileText,
  ShieldCheck,
  Cpu,
};

// Track which domains are expanded in the sidebar
const expanded = ref<Record<string, boolean>>({ [config.activeDomain]: true });

function toggleDomain(key: string) {
  expanded.value[key] = !expanded.value[key];
}

function selectSection(domain: string, section: string) {
  config.navigate(domain, section);
  expanded.value[domain] = true;
}

function isActive(domain: string, section: string) {
  return config.activeDomain === domain && config.activeSection === section;
}

function isDomainDirty(domain: ConfigDomainMeta) {
  return domain.sections.some((s) => config.isSectionDirty(domain.key, s.key));
}

function isSectionVisible(domain: ConfigDomainMeta, sectionKey: string) {
  const section = domain.sections.find((s) => s.key === sectionKey);
  if (!section) return false;
  return scopeAllows(auth.role ?? "support", section.requiredScope);
}
</script>

<template>
  <aside class="flex w-56 shrink-0 flex-col border-r border-slate-200 bg-white shadow-panel overflow-y-auto">

    <div class="p-2 space-y-0.5">
      <template v-for="domain in config.visibleDomains" :key="domain.key">
        <!-- Domain header -->
        <button
          class="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-xs font-semibold uppercase tracking-wide transition-colors"
          :class="config.activeDomain === domain.key
            ? 'bg-berry/10 text-berry'
            : 'text-graphite hover:bg-slate-100 hover:text-ink'"
          @click="toggleDomain(domain.key)"
        >
          <component :is="ICON_MAP[domain.iconName]" class="size-3.5 shrink-0" />
          <span class="flex-1 text-left truncate">{{ domain.label }}</span>
          <!-- Dirty dot -->
          <span v-if="isDomainDirty(domain)" class="size-1.5 shrink-0 rounded-full bg-amber-500" title="Unsaved changes" />
          <!-- Chevron -->
          <span class="text-[10px] text-graphite transition-transform" :class="expanded[domain.key] ? 'rotate-0' : '-rotate-90'">▾</span>
        </button>

        <!-- Sections -->
        <div v-if="expanded[domain.key]" class="ml-2 space-y-0.5">
          <template v-for="section in domain.sections" :key="section.key">
            <button
              v-if="isSectionVisible(domain, section.key)"
              class="flex w-full items-center gap-1.5 rounded-lg py-1.5 pl-4 pr-2 text-sm transition-colors"
              :class="isActive(domain.key, section.key)
                ? 'bg-berry/10 font-medium text-berry'
                : 'text-graphite hover:bg-slate-100 hover:text-ink'"
              @click="selectSection(domain.key, section.key)"
            >
              <span class="flex-1 text-left truncate">{{ section.label }}</span>
              <!-- Section dirty dot -->
              <span
                v-if="config.isSectionDirty(domain.key, section.key)"
                class="size-1.5 shrink-0 rounded-full bg-amber-500"
                title="Unsaved changes"
              />
              <!-- Pending badge -->
              <span
                v-else-if="section.pendingBackend"
                class="shrink-0 rounded bg-slate-100 px-1 py-0.5 text-[9px] text-graphite"
              >WIP</span>
              <!-- CRUD badge -->
              <span
                v-else-if="section.isCrud"
                class="shrink-0 rounded bg-slate-100 px-1 py-0.5 text-[9px] text-graphite"
              >CRUD</span>
            </button>
          </template>
        </div>
      </template>
    </div>

    <!-- Unsaved warning at bottom -->
    <div
      v-if="config.totalDirtyCount > 0"
      class="mt-auto border-t border-amber-200 bg-amber-50 px-4 py-2 text-xs text-amber-700 flex items-center gap-1.5"
    >
      <TriangleAlert class="size-3 shrink-0" />
      {{ config.totalDirtyCount }} section{{ config.totalDirtyCount !== 1 ? "s" : "" }} unsaved
    </div>
  </aside>
</template>

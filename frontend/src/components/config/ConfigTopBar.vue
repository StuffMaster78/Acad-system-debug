<script setup lang="ts">
import { ref, computed } from "vue";
import {
  ChevronDown,
  Download,
  Globe,
  History,
  RotateCcw,
  Save,
  Search,
  TriangleAlert,
  X,
} from "@lucide/vue";
import { useAdminMasterConfigStore } from "@/stores/adminMasterConfig";

const config = useAdminMasterConfigStore();

const showWebsiteMenu = ref(false);
const showActionsMenu = ref(false);

const envBadge = computed(() => {
  const hostname = typeof window !== "undefined" ? window.location.hostname : "";
  if (hostname.includes("localhost") || hostname.includes("127.0")) return { label: "local", cls: "bg-slate-100 text-graphite" };
  if (hostname.includes("staging") || hostname.includes("test")) return { label: "staging", cls: "bg-amber-100 text-amber-800" };
  return { label: "production", cls: "bg-emerald-100 text-emerald-800 font-semibold" };
});

function selectWebsite(ws: string | null) {
  config.selectedWebsite = ws;
  showWebsiteMenu.value = false;
  config.loadConfigValues();
}
</script>

<template>
  <div class="flex h-12 shrink-0 items-center gap-3 border-b border-slate-200 bg-white px-4 shadow-sm z-10">

    <!-- Website selector -->
    <div class="relative">
      <button
        class="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-ink hover:border-slate-300 transition-colors"
        @click="showWebsiteMenu = !showWebsiteMenu"
      >
        <Globe class="size-3.5 text-graphite" />
        {{ config.selectedWebsite ?? "Global" }}
        <ChevronDown class="size-3.5 text-graphite" />
      </button>

      <div
        v-if="showWebsiteMenu"
        class="absolute top-full left-0 z-50 mt-1 min-w-40 rounded-lg border border-slate-200 bg-white py-1 shadow-lg"
      >
        <button
          class="flex w-full items-center gap-2 px-3 py-1.5 text-sm hover:bg-slate-50 text-left"
          :class="config.selectedWebsite === null ? 'font-semibold text-berry' : 'text-ink'"
          @click="selectWebsite(null)"
        >
          <Globe class="size-3.5 text-graphite" />
          Global (default)
        </button>
        <div class="my-1 border-t border-slate-100" />
        <button
          v-for="ws in config.websites"
          :key="ws"
          class="flex w-full items-center gap-2 px-3 py-1.5 text-sm hover:bg-slate-50 text-left"
          :class="config.selectedWebsite === ws ? 'font-semibold text-berry' : 'text-ink'"
          @click="selectWebsite(ws)"
        >
          {{ ws }}
        </button>
      </div>
    </div>

    <!-- Search -->
    <div class="relative flex-1 max-w-sm">
      <Search class="absolute left-2.5 top-1/2 -translate-y-1/2 size-3.5 text-graphite pointer-events-none" />
      <input
        v-model="config.searchQuery"
        placeholder="Search settings…"
        class="w-full rounded-lg border border-slate-200 bg-white py-1.5 pl-8 pr-8 text-sm focus-ring"
      />
      <button
        v-if="config.searchQuery"
        class="absolute right-2.5 top-1/2 -translate-y-1/2 text-graphite hover:text-ink"
        @click="config.searchQuery = ''"
      >
        <X class="size-3.5" />
      </button>
    </div>

    <!-- Environment badge -->
    <span class="hidden sm:inline-flex rounded-full px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide" :class="envBadge.cls">
      {{ envBadge.label }}
    </span>

    <!-- Unsaved changes warning -->
    <div
      v-if="config.totalDirtyCount > 0"
      class="flex items-center gap-1.5 rounded-lg border border-amber-200 bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700"
    >
      <TriangleAlert class="size-3.5 shrink-0" />
      {{ config.totalDirtyCount }} section{{ config.totalDirtyCount !== 1 ? "s" : "" }} unsaved
    </div>

    <div class="ml-auto flex items-center gap-1.5">
      <!-- Actions dropdown -->
      <div class="relative">
        <button
          class="flex items-center gap-1 rounded-lg border border-slate-200 px-2.5 py-1.5 text-sm text-graphite hover:bg-slate-50 hover:text-ink transition-colors"
          @click="showActionsMenu = !showActionsMenu"
        >
          Actions <ChevronDown class="size-3.5" />
        </button>
        <div
          v-if="showActionsMenu"
          class="absolute right-0 top-full z-50 mt-1 min-w-44 rounded-lg border border-slate-200 bg-white py-1 shadow-lg"
          @click="showActionsMenu = false"
        >
          <button
            class="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-ink hover:bg-slate-50"
            @click="config.exportConfig()"
          >
            <Download class="size-3.5 text-graphite" />
            Export config
          </button>
          <button
            class="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-ink hover:bg-slate-50"
            @click="config.openAudit(config.activeDomain, config.activeSection)"
          >
            <History class="size-3.5 text-graphite" />
            View audit log
          </button>
          <div class="my-1 border-t border-slate-100" />
          <button
            class="flex w-full items-center gap-2 px-3 py-1.5 text-sm text-rose-600 hover:bg-rose-50"
            @click="config.resetSection(config.activeDomain, config.activeSection)"
          >
            <RotateCcw class="size-3.5" />
            Reset current section
          </button>
        </div>
      </div>

      <!-- Save all -->
      <button
        class="flex items-center gap-1.5 rounded-lg bg-berry px-3 py-1.5 text-sm font-semibold text-white hover:bg-berry/90 disabled:opacity-50 transition-colors"
        :disabled="config.totalDirtyCount === 0"
        @click="config.saveAll()"
      >
        <Save class="size-3.5" />
        Save all{{ config.totalDirtyCount > 0 ? ` (${config.totalDirtyCount})` : "" }}
      </button>
    </div>
  </div>

  <!-- Search results overlay -->
  <div
    v-if="config.isSearching"
    class="absolute inset-x-0 top-12 z-40 bg-white border-b border-slate-200 shadow-lg max-h-96 overflow-y-auto"
  >
    <div v-if="!config.searchResults.length" class="px-6 py-8 text-center text-sm text-graphite">
      No settings match "{{ config.searchQuery }}"
    </div>
    <div v-else class="divide-y divide-slate-50">
      <button
        v-for="result in config.searchResults.slice(0, 20)"
        :key="result.key"
        class="flex w-full items-center gap-3 px-6 py-3 text-left hover:bg-slate-50 transition-colors"
        @click="config.navigate(result.domain, result.section); config.searchQuery = ''"
      >
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-ink truncate">{{ result.label }}</p>
          <p class="text-xs text-graphite truncate">{{ result.domain.replace(/-/g, " ") }} → {{ result.section.replace(/-/g, " ") }}</p>
        </div>
        <code class="shrink-0 rounded bg-slate-100 px-1.5 py-0.5 text-[10px] text-graphite">{{ result.key }}</code>
      </button>
    </div>
  </div>
</template>

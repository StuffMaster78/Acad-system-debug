<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { AlertTriangle, CheckCircle2, ExternalLink, RefreshCw } from "@lucide/vue";
import { adminPublishingApi, type ContentHealthItem, type ContentHealthFlag, type ContentHealthReport } from "@/api/adminPublishing";

const report = ref<ContentHealthReport | null>(null);
const isLoading = ref(false);
const error = ref("");

const FLAG_LABELS: Record<ContentHealthFlag, string> = {
  missing_meta: "No meta description",
  missing_author: "No author",
  stale: "Stale (90+ days)",
  no_cta: "No CTA",
  no_service_route: "No service link",
  no_citations: "Missing citations",
};

const FLAG_SEVERITY: Record<ContentHealthFlag, "high" | "medium" | "low"> = {
  missing_author: "high",
  no_service_route: "high",
  missing_meta: "high",
  no_cta: "medium",
  stale: "medium",
  no_citations: "low",
};

const activeFilter = ref<ContentHealthFlag | "all">("all");

const filteredItems = computed<ContentHealthItem[]>(() => {
  if (!report.value) return [];
  const items = report.value.items.filter((i) => !i.is_healthy);
  if (activeFilter.value === "all") return items;
  return items.filter((i) => i.flags.includes(activeFilter.value as ContentHealthFlag));
});

const summaryStats = computed(() => {
  const s = report.value?.summary;
  if (!s) return [];
  return [
    { flag: "missing_meta" as ContentHealthFlag,    count: s.missing_meta,      label: "No meta" },
    { flag: "missing_author" as ContentHealthFlag,  count: s.missing_author,    label: "No author" },
    { flag: "stale" as ContentHealthFlag,           count: s.stale,             label: "Stale" },
    { flag: "no_cta" as ContentHealthFlag,          count: s.no_cta,            label: "No CTA" },
    { flag: "no_service_route" as ContentHealthFlag,count: s.no_service_route,  label: "No service link" },
    { flag: "no_citations" as ContentHealthFlag,    count: s.no_citations,      label: "No citations" },
  ].filter((s) => s.count > 0);
});

function typeTag(type: ContentHealthItem["type"]) {
  if (type === "blog") return "bg-blue-100 text-blue-700";
  if (type === "service") return "bg-purple-100 text-purple-700";
  return "bg-slate-100 text-graphite";
}

function typeLabel(type: ContentHealthItem["type"]) {
  if (type === "blog") return "Blog";
  if (type === "service") return "Service";
  return "SEO";
}

function severityClass(flag: ContentHealthFlag) {
  const s = FLAG_SEVERITY[flag];
  if (s === "high") return "bg-rose-100 text-rose-700";
  if (s === "medium") return "bg-amber-100 text-amber-700";
  return "bg-slate-100 text-graphite";
}

async function load() {
  isLoading.value = true;
  error.value = "";
  try {
    const { data } = await adminPublishingApi.contentHealth();
    report.value = data;
  } catch {
    error.value = "Could not load content health data.";
  } finally {
    isLoading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <div class="space-y-5">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h2 class="text-base font-semibold text-ink">Content Health</h2>
        <p class="mt-0.5 text-xs text-graphite">Editorial completeness across all published pages</p>
      </div>
      <button
        class="inline-flex items-center gap-1.5 rounded-md border border-slate-200 px-3 py-1.5 text-xs font-medium text-graphite hover:text-ink transition-colors"
        :disabled="isLoading"
        @click="load"
      >
        <RefreshCw class="size-3" :class="{ 'animate-spin': isLoading }" />
        Refresh
      </button>
    </div>

    <!-- Error -->
    <p v-if="error" class="rounded-md border border-amber-200 bg-amber-50 px-4 py-2.5 text-xs text-amber-900">
      {{ error }}
    </p>

    <!-- Loading skeleton -->
    <div v-else-if="isLoading && !report" class="space-y-3">
      <div v-for="i in 4" :key="i" class="h-14 animate-pulse rounded-lg bg-slate-100" />
    </div>

    <template v-else-if="report">

      <!-- Summary bar -->
      <div class="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        <div
          v-for="stat in summaryStats"
          :key="stat.flag"
          class="cursor-pointer rounded-xl border px-3 py-2.5 transition-colors"
          :class="activeFilter === stat.flag
            ? 'border-ink bg-ink text-white'
            : 'border-slate-200 bg-white hover:border-slate-300'"
          @click="activeFilter = activeFilter === stat.flag ? 'all' : stat.flag"
        >
          <p class="text-lg font-extrabold" :class="activeFilter === stat.flag ? 'text-white' : 'text-ink'">
            {{ stat.count }}
          </p>
          <p class="text-xs" :class="activeFilter === stat.flag ? 'text-white/80' : 'text-graphite'">
            {{ stat.label }}
          </p>
        </div>

        <!-- Healthy count -->
        <div class="rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2.5">
          <p class="text-lg font-extrabold text-emerald-700">{{ report.summary.healthy }}</p>
          <p class="text-xs text-emerald-600">Healthy</p>
        </div>
      </div>

      <!-- All healthy state -->
      <div
        v-if="report.summary.total > 0 && report.summary.healthy === report.summary.total"
        class="flex items-center gap-3 rounded-xl border border-emerald-200 bg-emerald-50 px-5 py-4"
      >
        <CheckCircle2 class="size-5 shrink-0 text-emerald-600" />
        <div>
          <p class="text-sm font-semibold text-emerald-800">All {{ report.summary.total }} pages are healthy</p>
          <p class="text-xs text-emerald-600">No editorial issues found</p>
        </div>
      </div>

      <!-- Issue list -->
      <div v-else-if="filteredItems.length" class="divide-y divide-slate-100 rounded-xl border border-slate-200 bg-white overflow-hidden">
        <div
          v-for="item in filteredItems"
          :key="`${item.source}-${item.id}`"
          class="flex items-start gap-3 px-4 py-3"
        >
          <AlertTriangle class="mt-0.5 size-4 shrink-0 text-amber-400" />

          <div class="min-w-0 flex-1">
            <div class="flex flex-wrap items-center gap-2">
              <span
                class="rounded-full px-2 py-0.5 text-xs font-semibold"
                :class="typeTag(item.type)"
              >{{ typeLabel(item.type) }}</span>
              <p class="truncate text-sm font-medium text-ink">{{ item.title }}</p>
            </div>

            <div class="mt-1.5 flex flex-wrap gap-1.5">
              <span
                v-for="flag in item.flags"
                :key="flag"
                class="rounded-full px-2 py-0.5 text-xs font-medium"
                :class="severityClass(flag)"
              >
                {{ FLAG_LABELS[flag] }}
              </span>
            </div>
          </div>

          <a
            :href="item.edit_url"
            target="_blank"
            rel="noopener"
            class="mt-0.5 shrink-0 text-graphite hover:text-ink transition-colors"
            title="Open in CMS"
          >
            <ExternalLink class="size-4" />
          </a>
        </div>
      </div>

      <p v-else-if="activeFilter !== 'all'" class="text-center text-sm text-graphite py-6">
        No pages with this issue.
      </p>

    </template>
  </div>
</template>

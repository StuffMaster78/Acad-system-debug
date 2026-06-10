<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import {
  AlertTriangle, BookOpen, CheckCircle2, ChevronDown,
  ExternalLink, FilePenLine, Globe2, Link2, Loader2,
  Newspaper, PenSquare, Plus, RefreshCw, Search,
  Send, ShieldCheck, Sparkles, Users, X,
} from "@lucide/vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import WagtailGuideModal from "@/components/cms/WagtailGuideModal.vue";
import ContentHealthPanel from "@/components/cms/ContentHealthPanel.vue";
import SyncStatusPanel from "@/components/cms/SyncStatusPanel.vue";
import WebsiteSelectorBar from "@/components/ui/WebsiteSelectorBar.vue";
import { useAdminPublishingStore } from "@/stores/adminPublishing";
import { useAuthStore } from "@/stores/auth";
import { useWebsitesStore } from "@/stores/websites";
import type { PublishingContentType, PublishingItem } from "@/types/adminPublishing";

const route      = useRoute();
const publishing = useAdminPublishingStore();
const auth       = useAuthStore();
const websites   = useWebsitesStore();

const isSuperAdmin = computed(() => auth.role === "superadmin");
const isStaff      = computed(() => ["superadmin","admin","editor","support"].includes(auth.role ?? ""));

// ── Tabs + status filter ──────────────────────────────────────────────────
const tabs: Array<{ key: PublishingContentType | "all"; label: string }> = [
  { key: "all",     label: "All" },
  { key: "blog",    label: "Blog" },
  { key: "service", label: "Services" },
  { key: "seo",     label: "SEO pages" },
];

const statusFilter = ref<"all" | "published" | "draft" | "scheduled">("all");

const filteredByStatus = computed(() => {
  const base = publishing.filteredItems;
  if (statusFilter.value === "all") return base;
  if (statusFilter.value === "scheduled") return base.filter(i => isScheduled(i));
  if (statusFilter.value === "published") return base.filter(i => i.status === "published" && !isScheduled(i));
  return base.filter(i => i.status !== "published" && !isScheduled(i));
});

// ── Content summary stats ─────────────────────────────────────────────────
const totalPublished  = computed(() => publishing.filteredItems.filter(i => i.status === "published").length);
const totalDraft      = computed(() => publishing.filteredItems.filter(i => i.status !== "published" && !isScheduled(i)).length);
const totalScheduled  = computed(() => publishing.filteredItems.filter(i => isScheduled(i)).length);
const totalCount      = computed(() => publishing.filteredItems.length);

// ── Content type metadata ─────────────────────────────────────────────────
const contentTypes = [
  { key: "blog"    as PublishingContentType, label: "Blog article",     hint: "Rich editorial page managed in Wagtail CMS.",           icon: "📝" },
  { key: "service" as PublishingContentType, label: "Service page",     hint: "Conversion landing page managed in Wagtail CMS.",        icon: "🛠️" },
  { key: "seo"     as PublishingContentType, label: "SEO landing page", hint: "Lightweight structured page managed via the API.",      icon: "🔍" },
];

// ── Create slide-over ─────────────────────────────────────────────────────
const showCreate   = ref(false);
const showAdvanced = ref(false);

function openCreate() { showCreate.value = true; showAdvanced.value = false; }

// ── Link suggestions ──────────────────────────────────────────────────────
const linkSuggestions        = ref<{ page_id: number; title: string; url: string; reason: string; score: number }[]>([]);
const linkSuggestionPageId   = ref<number | null>(null);
const isFetchingSuggestions  = ref(false);
const showLinkTool           = ref(false);

async function fetchLinkSuggestions() {
  if (!linkSuggestionPageId.value) return;
  isFetchingSuggestions.value = true;
  try {
    const { cmsIntelligenceApi } = await import("@/api/cms");
    const { data } = await cmsIntelligenceApi.linkSuggestions(linkSuggestionPageId.value);
    linkSuggestions.value = Array.isArray(data) ? data : [];
  } catch {
    linkSuggestions.value = [];
  } finally {
    isFetchingSuggestions.value = false;
  }
}

// ── Panels ────────────────────────────────────────────────────────────────
const showHealth = ref(false);
const showSync   = ref(false);

// ── Helpers ───────────────────────────────────────────────────────────────
const roleLabel = computed(() => {
  const seg = String(route.path.split("/")[1] || "staff");
  if (seg === "superadmin") return "Superadmin";
  return seg.charAt(0).toUpperCase() + seg.slice(1);
});

const visibleResponsibilities = computed(() => {
  const current = String(route.path.split("/")[1] || "");
  return publishing.roleResponsibilities.filter(
    item => item.role === current || current === "superadmin",
  );
});

function fmtDate(v: string | null) {
  if (!v) return "—";
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(new Date(v));
}

function fmtRelative(v: string | null) {
  if (!v) return "—";
  const ms   = Date.now() - new Date(v).getTime();
  const mins = Math.floor(ms / 60_000);
  if (mins < 60)  return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24)   return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  if (days < 30)  return `${days}d ago`;
  return fmtDate(v);
}

function isScheduled(item: PublishingItem): boolean {
  return item.status === "draft" && !!item.publishedAt && new Date(item.publishedAt) > new Date();
}

function statusTone(item: PublishingItem) {
  if (isScheduled(item))          return "warning";
  if (item.status === "published") return "success";
  return "neutral";
}

function statusLabel(item: PublishingItem) {
  if (isScheduled(item)) return "scheduled";
  return item.status;
}

const TYPE_META: Record<PublishingContentType, { badge: string; dot: string; label: string }> = {
  blog:    { badge: "bg-blue-50 text-blue-700 border-blue-100",   dot: "bg-blue-400",   label: "Blog"    },
  service: { badge: "bg-violet-50 text-violet-700 border-violet-100", dot: "bg-violet-400", label: "Service" },
  seo:     { badge: "bg-amber-50 text-amber-700 border-amber-100",  dot: "bg-amber-400",  label: "SEO"     },
};

onMounted(() => publishing.hydrate().catch(() => undefined));
</script>

<template>
  <div class="flex h-full flex-col bg-gray-50">

    <!-- ── Top header ──────────────────────────────────────────────────────── -->
    <div class="border-b border-gray-200 bg-white px-6 py-4">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">

        <!-- Title -->
        <div class="flex items-center gap-3">
          <div class="flex size-9 items-center justify-center rounded-xl bg-indigo-600 shadow-sm">
            <Newspaper class="size-5 text-white" />
          </div>
          <div>
            <h1 class="text-base font-bold text-gray-900 leading-tight">Publishing Desk</h1>
            <p class="text-xs text-gray-400">{{ roleLabel }} · content inventory &amp; tools</p>
          </div>
        </div>

        <!-- Actions row -->
        <div class="flex flex-wrap items-center gap-2">
          <a
            href="/cms-admin/"
            target="_blank"
            rel="noreferrer"
            class="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 bg-white px-3 py-1.5 text-xs font-medium text-gray-600 hover:bg-gray-50 transition-colors"
          >
            <ExternalLink class="size-3.5" /> Wagtail CMS
          </a>
          <WagtailGuideModal />
          <button
            class="inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors"
            :class="showHealth ? 'border-amber-300 bg-amber-50 text-amber-800' : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50'"
            @click="showHealth = !showHealth; showSync = false"
          >
            <AlertTriangle class="size-3.5" /> Health
          </button>
          <button
            class="inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-colors"
            :class="showSync ? 'border-sky-300 bg-sky-50 text-sky-800' : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50'"
            @click="showSync = !showSync; showHealth = false"
          >
            <RefreshCw class="size-3.5" /> Sync
          </button>
          <button
            class="rounded-lg border border-gray-200 bg-white p-1.5 text-gray-500 hover:bg-gray-50 disabled:opacity-50 transition-colors"
            :disabled="publishing.isLoading"
            @click="publishing.hydrate().catch(() => undefined)"
          >
            <RefreshCw class="size-4" :class="{ 'animate-spin text-indigo-500': publishing.isLoading }" />
          </button>
          <button
            class="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-indigo-700 shadow-sm transition-colors"
            @click="openCreate"
          >
            <Plus class="size-3.5" /> New page
          </button>
        </div>
      </div>

      <!-- ── Stats strip ──────────────────────────────────────────────────── -->
      <div class="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <button
          v-for="stat in [
            { label: 'Total pages',  value: totalCount,     key: 'all',       color: 'bg-gray-50 border-gray-200 text-gray-800' },
            { label: 'Published',    value: totalPublished, key: 'published',  color: 'bg-green-50 border-green-200 text-green-800' },
            { label: 'Drafts',       value: totalDraft,     key: 'draft',      color: 'bg-amber-50 border-amber-200 text-amber-800' },
            { label: 'Scheduled',    value: totalScheduled, key: 'scheduled',  color: 'bg-blue-50 border-blue-200 text-blue-800' },
          ]"
          :key="stat.key"
          class="rounded-xl border px-4 py-3 text-left transition-all hover:shadow-sm"
          :class="[stat.color, statusFilter === stat.key ? 'ring-2 ring-indigo-300' : '']"
          @click="statusFilter = stat.key as typeof statusFilter"
        >
          <p class="text-2xl font-bold leading-none">{{ stat.value }}</p>
          <p class="mt-1 text-xs font-medium opacity-70">{{ stat.label }}</p>
        </button>
      </div>
    </div>

    <!-- Notices -->
    <div v-if="publishing.error || publishing.notice" class="px-6 pt-3">
      <p v-if="publishing.error" class="rounded-lg border border-amber-200 bg-amber-50 px-4 py-2.5 text-xs text-amber-900">
        {{ publishing.error }}
      </p>
      <p v-if="publishing.notice" class="rounded-lg border border-green-200 bg-green-50 px-4 py-2.5 text-xs text-green-900">
        {{ publishing.notice }}
      </p>
    </div>

    <!-- Health / Sync panels -->
    <div v-if="showHealth" class="border-b border-amber-200 bg-amber-50/60 px-6 py-5">
      <ContentHealthPanel />
    </div>
    <div v-if="showSync" class="border-b border-sky-200 bg-sky-50/60 px-6 py-5">
      <SyncStatusPanel />
    </div>

    <!-- ── Body ─────────────────────────────────────────────────────────── -->
    <div class="flex min-h-0 flex-1 gap-0 overflow-hidden">

      <!-- Left: content list -->
      <div class="flex min-h-0 flex-1 flex-col overflow-hidden">

        <!-- Filters bar -->
        <div class="flex flex-wrap items-center gap-3 border-b border-gray-200 bg-white px-5 py-3">
          <!-- Type tabs -->
          <div class="flex gap-0.5 rounded-lg border border-gray-200 bg-gray-50 p-0.5">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              class="rounded-md px-3 py-1.5 text-xs font-semibold transition-colors"
              :class="publishing.activeType === tab.key
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-500 hover:text-gray-700'"
              @click="publishing.activeType = tab.key"
            >{{ tab.label }}</button>
          </div>

          <!-- Search -->
          <label class="relative min-w-48 flex-1 max-w-sm">
            <Search class="pointer-events-none absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-gray-400" />
            <input
              v-model="publishing.query"
              type="search"
              placeholder="Search title or slug…"
              class="h-8 w-full rounded-lg border border-gray-200 bg-white pl-8 pr-3 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
          </label>

          <span class="ml-auto text-xs text-gray-400">
            {{ filteredByStatus.length }} page{{ filteredByStatus.length !== 1 ? 's' : '' }}
          </span>
        </div>

        <!-- Content cards -->
        <div class="flex-1 overflow-y-auto p-4 space-y-2">

          <div v-if="publishing.isLoading && !filteredByStatus.length" class="flex justify-center py-16">
            <Loader2 class="size-6 text-gray-400 animate-spin" />
          </div>

          <template v-else-if="filteredByStatus.length">
            <div
              v-for="item in filteredByStatus"
              :key="`${item.source}-${item.id}`"
              class="group rounded-xl border border-gray-200 bg-white p-4 transition-all hover:border-indigo-200 hover:shadow-sm"
            >
              <div class="flex items-start gap-3">

                <!-- Type dot -->
                <div
                  class="mt-1 size-2.5 shrink-0 rounded-full"
                  :class="TYPE_META[item.type].dot"
                />

                <!-- Content -->
                <div class="min-w-0 flex-1">
                  <div class="flex flex-wrap items-start justify-between gap-2">
                    <div class="min-w-0">
                      <p class="font-semibold text-gray-900 leading-tight line-clamp-1">{{ item.title }}</p>
                      <p class="mt-0.5 font-mono text-xs text-gray-400 truncate">/{{ item.slug }}/</p>
                    </div>
                    <div class="flex shrink-0 items-center gap-2">
                      <StatusPill
                        :label="statusLabel(item)"
                        :tone="statusTone(item)"
                      />
                      <span
                        class="rounded-full border px-2 py-0.5 text-xs font-semibold"
                        :class="TYPE_META[item.type].badge"
                      >{{ TYPE_META[item.type].label }}</span>
                    </div>
                  </div>

                  <!-- Summary + meta -->
                  <p v-if="item.summary && !item.summary.includes('.')" class="mt-1.5 text-xs text-gray-500 line-clamp-1">
                    {{ item.summary }}
                  </p>

                  <div class="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-gray-400">
                    <span v-if="item.websiteName" class="flex items-center gap-1">
                      <Globe2 class="size-3" /> {{ item.websiteName }}
                    </span>
                    <span v-if="item.publishedAt && item.status === 'published'">
                      Published {{ fmtDate(item.publishedAt) }}
                    </span>
                    <span v-if="isScheduled(item)" class="text-blue-600 font-medium">
                      Scheduled for {{ fmtDate(item.publishedAt) }}
                    </span>
                    <span v-if="item.updatedAt">
                      Updated {{ fmtRelative(item.updatedAt) }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Actions — visible on hover -->
              <div class="mt-3 flex items-center gap-2 opacity-0 transition-opacity group-hover:opacity-100">
                <button
                  v-if="item.source === 'seo_pages'"
                  class="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 bg-gray-50 px-3 py-1 text-xs font-semibold text-gray-600 hover:bg-gray-100 disabled:opacity-50 transition-colors"
                  :disabled="publishing.isMutating"
                  @click="publishing.setPublishState(item, item.status !== 'published').catch(() => undefined)"
                >
                  <ShieldCheck class="size-3" />
                  {{ item.status === 'published' ? 'Unpublish' : 'Publish' }}
                </button>
                <a
                  v-if="item.url"
                  :href="item.url"
                  target="_blank"
                  rel="noreferrer"
                  class="inline-flex items-center gap-1.5 rounded-lg border border-gray-200 bg-gray-50 px-3 py-1 text-xs font-medium text-gray-600 hover:bg-gray-100 transition-colors"
                >
                  <ExternalLink class="size-3" /> View live
                </a>
                <a
                  v-if="item.source === 'wagtail'"
                  href="/cms-admin/"
                  target="_blank"
                  rel="noreferrer"
                  class="inline-flex items-center gap-1.5 rounded-lg border border-indigo-100 bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700 hover:bg-indigo-100 transition-colors"
                >
                  <PenSquare class="size-3" /> Edit in CMS
                </a>
              </div>
            </div>
          </template>

          <!-- Empty state -->
          <div v-else class="flex flex-col items-center justify-center py-24 text-center">
            <div class="mb-4 flex size-16 items-center justify-center rounded-2xl bg-gray-100">
              <Newspaper class="size-8 text-gray-300" />
            </div>
            <p class="font-semibold text-gray-700">No pages found</p>
            <p class="mt-1 max-w-xs text-sm text-gray-400">
              {{ publishing.query
                  ? `No results for "${publishing.query}". Try a different search.`
                  : 'Create your first page or check that the CMS is online.' }}
            </p>
            <button
              v-if="!publishing.query"
              class="mt-4 inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
              @click="openCreate"
            >
              <Plus class="size-4" /> Create a page
            </button>
          </div>
        </div>
      </div>

      <!-- ── Right sidebar ─────────────────────────────────────────────── -->
      <aside class="flex w-72 shrink-0 flex-col gap-0 overflow-y-auto border-l border-gray-200 bg-white">

        <!-- CMS Metrics (from store) -->
        <div v-if="publishing.metrics.length" class="border-b border-gray-100 px-4 py-4">
          <p class="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-400">Content health</p>
          <div class="space-y-2">
            <div
              v-for="metric in publishing.metrics"
              :key="metric.label"
              class="flex items-center justify-between rounded-lg px-3 py-2 text-xs"
              class="bg-white border border-slate-200"
            >
              <span class="font-medium text-gray-700">{{ metric.label }}</span>
              <span
                class="font-bold"
                :class="{
                  'text-green-700' : metric.tone === 'good',
                  'text-amber-700' : metric.tone === 'warn',
                  'text-red-700'   : metric.tone === 'risk',
                  'text-gray-600'  : metric.tone === 'neutral',
                }"
              >{{ metric.value }}</span>
            </div>
          </div>
        </div>

        <!-- Quick links to CMS -->
        <div class="border-b border-gray-100 px-4 py-4">
          <p class="mb-3 text-xs font-semibold uppercase tracking-wide text-gray-400">Wagtail quick links</p>
          <div class="space-y-1">
            <a
              v-for="link in publishing.adminLinks"
              :key="link.label"
              :href="link.href"
              target="_blank"
              rel="noreferrer"
              class="flex items-center justify-between rounded-lg px-3 py-2 text-xs font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors"
            >
              <span>{{ link.label }}</span>
              <ExternalLink class="size-3 shrink-0 text-gray-300" />
            </a>
          </div>
        </div>

        <!-- Internal link suggestions -->
        <div class="border-b border-gray-100">
          <button
            class="flex w-full items-center justify-between px-4 py-3.5 text-left hover:bg-gray-50 transition-colors"
            @click="showLinkTool = !showLinkTool"
          >
            <div class="flex items-center gap-2">
              <div class="flex size-6 items-center justify-center rounded-md bg-indigo-50">
                <Link2 class="size-3.5 text-indigo-600" />
              </div>
              <span class="text-xs font-semibold text-gray-800">Link suggestions</span>
            </div>
            <ChevronDown
              class="size-3.5 text-gray-400 transition-transform"
              :class="showLinkTool ? 'rotate-180' : ''"
            />
          </button>

          <div v-if="showLinkTool" class="px-4 pb-4 space-y-3">
            <p class="text-xs text-gray-400">Enter a Wagtail page ID to find related pages that should link to it.</p>
            <div class="flex gap-2">
              <input
                v-model.number="linkSuggestionPageId"
                type="number"
                class="min-w-0 flex-1 rounded-lg border border-gray-200 px-2.5 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-400"
                placeholder="Page ID"
                @keydown.enter="fetchLinkSuggestions"
              />
              <button
                class="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                :disabled="isFetchingSuggestions || !linkSuggestionPageId"
                @click="fetchLinkSuggestions"
              >
                <Loader2 v-if="isFetchingSuggestions" class="size-3.5 animate-spin" />
                <span v-else>Analyse</span>
              </button>
            </div>

            <div v-if="linkSuggestions.length" class="space-y-2">
              <a
                v-for="s in linkSuggestions"
                :key="s.page_id"
                :href="s.url ?? '#'"
                target="_blank"
                rel="noreferrer"
                class="block rounded-xl border border-gray-100 p-3 text-xs hover:border-indigo-200 hover:bg-indigo-50 transition-all"
              >
                <div class="flex items-start justify-between gap-2">
                  <p class="font-semibold text-gray-800 line-clamp-2 leading-snug">{{ s.title }}</p>
                  <span class="shrink-0 rounded-full bg-green-100 px-1.5 py-0.5 text-xs font-bold text-green-700">
                    {{ (s.score * 100).toFixed(0) }}%
                  </span>
                </div>
                <p class="mt-1 text-gray-400">{{ s.reason }}</p>
              </a>
            </div>
          </div>
        </div>

        <!-- Role responsibilities -->
        <div v-if="visibleResponsibilities.length" class="px-4 py-4">
          <div class="mb-3 flex items-center gap-2">
            <div class="flex size-6 items-center justify-center rounded-md bg-gray-100">
              <Users class="size-3.5 text-gray-500" />
            </div>
            <p class="text-xs font-semibold text-gray-400 uppercase tracking-wide">Role responsibilities</p>
          </div>
          <div class="space-y-3">
            <div
              v-for="role in visibleResponsibilities"
              :key="role.role"
              class="rounded-xl border border-gray-100 bg-gray-50 p-3"
            >
              <p class="text-xs font-semibold text-gray-800">{{ role.label }}</p>
              <ul class="mt-2 space-y-1.5">
                <li v-for="action in role.actions" :key="action" class="flex items-start gap-1.5 text-xs text-gray-500">
                  <CheckCircle2 class="mt-0.5 size-3 shrink-0 text-green-500" />
                  {{ action }}
                </li>
              </ul>
            </div>
          </div>
        </div>

      </aside>
    </div>

    <!-- ── Create slide-over ─────────────────────────────────────────────── -->
    <Teleport to="body">
      <Transition name="slideover">
        <div
          v-if="showCreate"
          class="fixed inset-0 z-40 flex"
        >
          <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="showCreate = false" />

          <div class="relative ml-auto flex h-full w-full max-w-md flex-col bg-white shadow-2xl">

            <!-- Slide-over header -->
            <div class="flex items-center justify-between border-b border-gray-100 bg-gradient-to-r from-indigo-600 to-indigo-500 px-5 py-4">
              <div class="flex items-center gap-3">
                <div class="flex size-8 items-center justify-center rounded-lg bg-white/20">
                  <FilePenLine class="size-4 text-white" />
                </div>
                <div>
                  <h2 class="font-bold text-white">New page</h2>
                  <p class="text-xs text-indigo-200">Draft or publish a new piece of content</p>
                </div>
              </div>
              <button class="rounded-lg p-1.5 text-white/70 hover:bg-white/10 hover:text-white transition-colors" @click="showCreate = false">
                <X class="size-5" />
              </button>
            </div>

            <!-- Form body -->
            <div class="flex-1 overflow-y-auto px-5 py-5 space-y-5">

              <!-- Website selector -->
              <div v-if="isSuperAdmin">
                <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">Publishing to</p>
                <WebsiteSelectorBar v-model="publishing.draft.website" label="Website:" />
              </div>

              <!-- Type selector -->
              <div>
                <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">Content type</p>
                <div class="grid gap-2">
                  <button
                    v-for="ct in contentTypes"
                    :key="ct.key"
                    class="flex items-start gap-3 rounded-xl border-2 p-4 text-left transition-all"
                    :class="publishing.draft.type === ct.key
                      ? 'border-indigo-500 bg-indigo-50 shadow-sm'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'"
                    @click="publishing.draft.type = ct.key"
                  >
                    <span class="text-xl leading-none mt-0.5">{{ ct.icon }}</span>
                    <div>
                      <p class="text-sm font-semibold text-gray-900">{{ ct.label }}</p>
                      <p class="mt-0.5 text-xs text-gray-500 leading-relaxed">{{ ct.hint }}</p>
                    </div>
                    <div
                      class="ml-auto mt-0.5 flex size-4 shrink-0 items-center justify-center rounded-full border-2 transition-all"
                      :class="publishing.draft.type === ct.key ? 'border-indigo-500 bg-indigo-500' : 'border-gray-300'"
                    >
                      <div v-if="publishing.draft.type === ct.key" class="size-1.5 rounded-full bg-white" />
                    </div>
                  </button>
                </div>
              </div>

              <!-- Route hint -->
              <div class="rounded-xl border border-indigo-100 bg-indigo-50 px-4 py-3">
                <p class="text-xs font-semibold text-indigo-800">{{ publishing.selectedWritePath.title }}</p>
                <p class="mt-1 text-xs text-indigo-600 leading-5">{{ publishing.selectedWritePath.detail }}</p>
                <p v-if="isStaff && publishing.draft.website" class="mt-1.5 text-xs font-medium text-indigo-700">
                  Publishing to: <span class="font-bold">{{ websites.nameById(publishing.draft.website) }}</span>
                </p>
              </div>

              <!-- Core fields -->
              <div class="space-y-4">
                <label class="block">
                  <span class="text-xs font-semibold text-gray-600">Title <span class="text-red-400">*</span></span>
                  <input
                    v-model="publishing.draft.title"
                    type="text"
                    placeholder="How to write a research paper"
                    class="mt-1.5 h-10 w-full rounded-xl border border-gray-200 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  />
                </label>

                <label class="block">
                  <span class="text-xs font-semibold text-gray-600">URL slug <span class="text-red-400">*</span></span>
                  <div class="mt-1.5 flex items-center">
                    <span class="rounded-l-xl border border-r-0 border-gray-200 bg-gray-50 px-3 py-2 text-xs text-gray-400 h-10 flex items-center">/lp/</span>
                    <input
                      v-model="publishing.draft.slug"
                      type="text"
                      placeholder="how-to-write-research-paper"
                      class="min-w-0 flex-1 h-10 rounded-r-xl border border-gray-200 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                    />
                  </div>
                </label>

                <label class="block">
                  <span class="text-xs font-semibold text-gray-600">Meta description</span>
                  <textarea
                    v-model="publishing.draft.meta_description"
                    rows="3"
                    maxlength="160"
                    placeholder="A concise description for search results (150–160 chars)…"
                    class="mt-1.5 w-full rounded-xl border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400 resize-none"
                  />
                  <p class="mt-1 text-right text-xs text-gray-400">
                    {{ (publishing.draft.meta_description ?? "").length }}/160
                  </p>
                </label>

                <label v-if="publishing.draft.type === 'seo'" class="block">
                  <span class="text-xs font-semibold text-gray-600">Schedule publish <span class="font-normal text-gray-400">(optional)</span></span>
                  <input
                    v-model="publishing.draft.publish_date"
                    type="datetime-local"
                    :min="new Date().toISOString().slice(0, 16)"
                    class="mt-1.5 h-10 w-full rounded-xl border border-gray-200 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
                  />
                </label>
              </div>

              <!-- Advanced fields -->
              <div class="rounded-xl border border-gray-100">
                <button
                  class="flex w-full items-center justify-between rounded-xl px-4 py-3 text-left hover:bg-gray-50 transition-colors"
                  @click="showAdvanced = !showAdvanced"
                >
                  <span class="text-xs font-semibold text-gray-600">Advanced SEO fields</span>
                  <ChevronDown class="size-3.5 text-gray-400 transition-transform" :class="showAdvanced ? 'rotate-180' : ''" />
                </button>

                <div v-if="showAdvanced" class="border-t border-gray-100 px-4 pb-4 pt-3 space-y-3">
                  <label class="block">
                    <span class="text-xs font-semibold text-gray-600">Primary keyword</span>
                    <input v-model="publishing.draft.primary_keyword" type="text" placeholder="e.g. research paper help"
                      class="mt-1.5 h-9 w-full rounded-xl border border-gray-200 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
                  </label>
                  <label class="block">
                    <span class="text-xs font-semibold text-gray-600">Target audience</span>
                    <input v-model="publishing.draft.audience" type="text" placeholder="e.g. undergraduate students"
                      class="mt-1.5 h-9 w-full rounded-xl border border-gray-200 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
                  </label>
                  <div class="grid grid-cols-2 gap-3">
                    <label class="block">
                      <span class="text-xs font-semibold text-gray-600">CTA label</span>
                      <input v-model="publishing.draft.cta_label" type="text"
                        class="mt-1.5 h-9 w-full rounded-xl border border-gray-200 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
                    </label>
                    <label class="block">
                      <span class="text-xs font-semibold text-gray-600">CTA URL</span>
                      <input v-model="publishing.draft.cta_href" type="text"
                        class="mt-1.5 h-9 w-full rounded-xl border border-gray-200 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400" />
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <!-- Footer -->
            <div class="border-t border-gray-100 bg-gray-50 px-5 py-4">
              <div class="flex gap-2">
                <button
                  class="flex flex-1 items-center justify-center gap-1.5 rounded-xl border border-gray-200 bg-white py-2.5 text-sm font-semibold text-gray-600 hover:bg-gray-50 disabled:opacity-60 transition-colors"
                  :disabled="publishing.isMutating"
                  @click="publishing.createContentDraft(false).catch(() => undefined)"
                >
                  <FilePenLine class="size-4" /> Save draft
                </button>
                <button
                  class="flex flex-1 items-center justify-center gap-1.5 rounded-xl bg-indigo-600 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-60 shadow-sm transition-colors"
                  :disabled="publishing.isMutating"
                  @click="publishing.createContentDraft(true).catch(() => undefined)"
                >
                  <Send class="size-4" /> {{ publishing.selectedWritePath.actionLabel }}
                </button>
              </div>
              <p class="mt-2 text-center text-xs text-gray-400">
                {{ publishing.draft.type === 'seo'
                    ? 'SEO pages are saved directly from this desk.'
                    : 'Draft is created in Wagtail — the editor opens in a new tab.' }}
              </p>
            </div>

          </div>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<style scoped>
.slideover-enter-active,
.slideover-leave-active {
  transition: opacity 0.2s ease;
}
.slideover-enter-active .relative,
.slideover-leave-active .relative {
  transition: transform 0.25s ease;
}
.slideover-enter-from { opacity: 0; }
.slideover-leave-to   { opacity: 0; }
.slideover-enter-from .relative { transform: translateX(100%); }
.slideover-leave-to .relative   { transform: translateX(100%); }
</style>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import {
  AlertTriangle,
  BookOpen,
  CheckCircle2,
  ChevronDown,
  ExternalLink,
  FilePenLine,
  Globe2,
  Link2,
  Loader2,
  Newspaper,
  Plus,
  RefreshCw,
  Search,
  Send,
  Users,
  X,
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

const route = useRoute();
const publishing = useAdminPublishingStore();
const auth = useAuthStore();
const websites = useWebsitesStore();
const isSuperAdmin = computed(() => auth.role === "superadmin");
const isStaff = computed(() => ["superadmin", "admin", "editor", "support"].includes(auth.role ?? ""));

// ── Filters ───────────────────────────────────────────────────────────────
const tabs: Array<{ key: PublishingContentType | "all"; label: string }> = [
  { key: "all", label: "All" },
  { key: "blog", label: "Blog" },
  { key: "service", label: "Service" },
  { key: "seo", label: "SEO pages" },
];

// ── Content type options ──────────────────────────────────────────────────
const contentTypes = [
  { key: "blog" as PublishingContentType, label: "Blog article", hint: "Rich editorial page managed in Wagtail CMS." },
  { key: "service" as PublishingContentType, label: "Service page", hint: "Conversion landing page managed in Wagtail CMS." },
  { key: "seo" as PublishingContentType, label: "SEO landing page", hint: "Lightweight structured page managed via the API." },
];

// ── Create panel ──────────────────────────────────────────────────────────
const showCreate = ref(false);
const showAdvanced = ref(false);

function openCreate() {
  showCreate.value = true;
  showAdvanced.value = false;
}

// ── Link suggestions ──────────────────────────────────────────────────────
const linkSuggestions = ref<{ page_id: number; title: string; url: string; reason: string; score: number }[]>([]);
const linkSuggestionPageId = ref<number | null>(null);
const isFetchingSuggestions = ref(false);
const showLinkTool = ref(false);

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

// ── Helpers ───────────────────────────────────────────────────────────────
const roleLabel = computed(() => {
  const seg = String(route.path.split("/")[1] || "staff");
  if (seg === "superadmin") return "Superadmin";
  return seg.charAt(0).toUpperCase() + seg.slice(1);
});

const visibleResponsibilities = computed(() => {
  const current = String(route.path.split("/")[1] || "");
  return publishing.roleResponsibilities.filter(
    (item) => item.role === current || current === "superadmin"
  );
});

function fmtDate(v: string | null) {
  if (!v) return "—";
  return new Intl.DateTimeFormat(undefined, { dateStyle: "medium" }).format(new Date(v));
}

function isScheduled(item: PublishingItem): boolean {
  return item.status === "draft" && !!item.publishedAt && new Date(item.publishedAt) > new Date();
}

function statusTone(status: string) {
  if (status === "published") return "success";
  if (status.includes("ready")) return "neutral";
  return "warning";
}

function typeBadge(type: PublishingContentType): string {
  if (type === "blog") return "bg-blue-100 text-blue-700";
  if (type === "service") return "bg-purple-100 text-purple-700";
  return "bg-amber-100 text-amber-700";
}

function typeLabel(type: PublishingContentType): string {
  if (type === "blog") return "Blog";
  if (type === "service") return "Service";
  return "SEO";
}

onMounted(() => {
  publishing.hydrate().catch(() => undefined);
});

const showHealth = ref(false);
const showSync = ref(false);
</script>

<template>
  <div class="flex h-full flex-col gap-0">

    <!-- ── Top bar ────────────────────────────────────────────────────────── -->
    <div class="flex items-center justify-between gap-4 border-b border-slate-200 bg-white px-6 py-4">
      <div class="flex items-center gap-3">
        <Newspaper class="size-5 text-berry shrink-0" />
        <div>
          <h1 class="font-bold text-ink">Publishing Desk</h1>
          <p class="text-xs text-graphite">{{ roleLabel }} — blog, service &amp; SEO pages</p>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <!-- Stat chips -->
        <div class="hidden items-center gap-1 md:flex">
          <span
            v-for="metric in publishing.metrics"
            :key="metric.label"
            class="rounded-full border px-2.5 py-1 text-xs font-semibold"
            :class="{
              'border-emerald-200 bg-emerald-50 text-emerald-700': metric.tone === 'good',
              'border-amber-200 bg-amber-50 text-amber-700' : metric.tone === 'warn',
              'border-rose-200 bg-rose-50 text-rose-700' : metric.tone === 'risk',
              'border-slate-200 bg-slate-50 text-graphite' : metric.tone === 'neutral',
            }"
          >
            {{ metric.value }} {{ metric.label }}
          </span>
        </div>

        <div class="h-5 w-px bg-slate-200 hidden md:block" />

        <a
          href="/cms-admin/"
          target="_blank"
          rel="noreferrer"
          class="focus-ring inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-graphite hover:bg-slate-50"
        >
          <ExternalLink class="size-3.5" /> Wagtail
        </a>

        <WagtailGuideModal />

        <button
          class="focus-ring inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-semibold transition-colors"
          :class="showHealth
            ? 'border-amber-300 bg-amber-50 text-amber-800'
            : 'border-slate-200 bg-white text-graphite hover:bg-slate-50'"
          @click="showHealth = !showHealth; showSync = false"
        >
          <AlertTriangle class="size-3.5" />
          Health
        </button>

        <button
          class="focus-ring inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-semibold transition-colors"
          :class="showSync
            ? 'border-sky-300 bg-sky-50 text-sky-800'
            : 'border-slate-200 bg-white text-graphite hover:bg-slate-50'"
          @click="showSync = !showSync; showHealth = false"
        >
          <RefreshCw class="size-3.5" />
          Sync
        </button>

        <button
          class="focus-ring inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-graphite hover:bg-slate-50 disabled:opacity-50"
          :disabled="publishing.isLoading"
          @click="publishing.hydrate().catch(() => undefined)"
        >
          <RefreshCw class="size-3.5" :class="{ 'animate-spin': publishing.isLoading }" />
        </button>

        <button
          class="focus-ring inline-flex items-center gap-1.5 rounded-lg bg-berry px-3 py-1.5 text-xs font-semibold text-white hover:bg-rose-700"
          @click="openCreate"
        >
          <Plus class="size-3.5" /> New page
        </button>
      </div>
    </div>

    <!-- ── Notices ────────────────────────────────────────────────────────── -->
    <div v-if="publishing.error || publishing.notice" class="px-6 pt-3">
      <p v-if="publishing.error" class="rounded-lg border border-amber-200 bg-amber-50 px-4 py-2.5 text-xs text-amber-900">
        {{ publishing.error }}
      </p>
      <p v-if="publishing.notice" class="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-2.5 text-xs text-emerald-900">
        {{ publishing.notice }}
      </p>
    </div>

    <!-- ── Content health panel (toggled) ───────────────────────────────── -->
    <div v-if="showHealth" class="border-b border-amber-200 bg-amber-50/60 px-6 py-5">
      <ContentHealthPanel />
    </div>

    <div v-if="showSync" class="border-b border-sky-200 bg-sky-50/60 px-6 py-5">
      <SyncStatusPanel />
    </div>

    <!-- ── Body: inventory + sidebar ────────────────────────────────────── -->
    <div class="flex min-h-0 flex-1 gap-0 overflow-hidden">

      <!-- Content inventory -->
      <div class="flex min-h-0 flex-1 flex-col overflow-hidden">

        <!-- Filters bar -->
        <div class="flex flex-wrap items-center gap-3 border-b border-slate-200 bg-white px-6 py-3">
          <!-- Type tabs -->
          <div class="flex gap-0.5 rounded-lg border border-slate-200 bg-slate-50 p-0.5">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              class="rounded-md px-3 py-1.5 text-xs font-semibold transition-colors"
              :class="publishing.activeType === tab.key
                ? 'bg-white text-ink shadow-sm'
                : 'text-graphite hover:text-ink'"
              @click="publishing.activeType = tab.key"
            >{{ tab.label }}</button>
          </div>

          <!-- Search -->
          <label class="relative min-w-48 flex-1">
            <Search class="pointer-events-none absolute left-2.5 top-1/2 size-3.5 -translate-y-1/2 text-slate-400" />
            <input
              v-model="publishing.query"
              type="search"
              placeholder="Search title or slug…"
              class="focus-ring h-8 w-full rounded-lg border border-slate-200 bg-white pl-8 pr-3 text-xs"
            />
          </label>

          <span class="ml-auto text-xs text-graphite">
            {{ publishing.filteredItems.length }} page{{ publishing.filteredItems.length !== 1 ? 's' : '' }}
          </span>
        </div>

        <!-- Table -->
        <div class="flex-1 overflow-y-auto">
          <table v-if="publishing.filteredItems.length" class="min-w-full text-sm">
            <thead class="sticky top-0 z-10 border-b border-slate-200 bg-slate-50 text-left">
              <tr>
                <th class="px-6 py-2.5 text-xs font-semibold uppercase tracking-wide text-graphite">Page</th>
                <th class="px-3 py-2.5 text-xs font-semibold uppercase tracking-wide text-graphite">Type</th>
                <th v-if="isStaff" class="px-3 py-2.5 text-xs font-semibold uppercase tracking-wide text-graphite">Website</th>
                <th class="px-3 py-2.5 text-xs font-semibold uppercase tracking-wide text-graphite">Status</th>
                <th class="px-3 py-2.5 text-xs font-semibold uppercase tracking-wide text-graphite">Published</th>
                <th class="px-3 py-2.5 text-xs font-semibold uppercase tracking-wide text-graphite">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 bg-white">
              <tr
                v-for="item in publishing.filteredItems"
                :key="`${item.source}-${item.id}`"
                class="group hover:bg-slate-50"
              >
                <td class="px-6 py-3">
                  <p class="font-medium text-ink">{{ item.title }}</p>
                  <p class="mt-0.5 font-mono text-xs text-slate-400">/{{ item.slug }}/</p>
                </td>

                <td class="px-3 py-3">
                  <span
                    class="rounded-full px-2 py-0.5 text-xs font-semibold"
                    :class="typeBadge(item.type)"
                  >{{ typeLabel(item.type) }}</span>
                </td>

                <!-- Website name — all staff roles -->
                <td v-if="isStaff" class="px-3 py-3">
                  <span v-if="item.websiteName" class="text-xs font-medium text-graphite">
                    {{ item.websiteName }}
                  </span>
                  <span v-else class="text-xs text-slate-300">—</span>
                </td>

                <td class="px-3 py-3">
                  <StatusPill
                    :label="isScheduled(item) ? 'scheduled' : item.status"
                    :tone="isScheduled(item) ? 'warning' : statusTone(item.status)"
                  />
                </td>

                <td class="px-3 py-3 text-xs text-graphite">{{ fmtDate(item.publishedAt) }}</td>

                <td class="px-3 py-3">
                  <div class="flex items-center gap-1.5 opacity-0 transition-opacity group-hover:opacity-100">
                    <!-- SEO pages: publish toggle -->
                    <button
                      v-if="item.source === 'seo_pages'"
                      class="rounded-md border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold text-graphite hover:bg-slate-50 disabled:opacity-50"
                      :disabled="publishing.isMutating"
                      @click="publishing.setPublishState(item, item.status !== 'published').catch(() => undefined)"
                    >
                      {{ item.status === 'published' ? 'Unpublish' : 'Publish' }}
                    </button>
                    <!-- Wagtail pages: open in CMS -->
                    <a
                      v-if="item.url"
                      :href="item.url"
                      target="_blank"
                      rel="noreferrer"
                      class="inline-flex items-center gap-1 rounded-md border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold text-graphite hover:bg-slate-50"
                    >
                      <ExternalLink class="size-3" /> View
                    </a>
                    <a
                      v-if="item.source === 'wagtail'"
                      href="/cms-admin/"
                      target="_blank"
                      rel="noreferrer"
                      class="inline-flex items-center gap-1 rounded-md border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold text-graphite hover:bg-slate-50"
                    >
                      Edit in CMS
                    </a>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Empty -->
          <div v-else class="flex flex-col items-center justify-center py-24 text-center">
            <Newspaper class="mb-4 size-10 text-slate-300" />
            <p class="font-semibold text-ink">No pages found</p>
            <p class="mt-1 text-sm text-graphite">
              {{ publishing.query ? 'Try a different search.' : 'Create your first page or refresh when the CMS is online.' }}
            </p>
          </div>
        </div>
      </div>

      <!-- ── Right sidebar ──────────────────────────────────────────────── -->
      <aside class="flex w-72 shrink-0 flex-col gap-0 overflow-y-auto border-l border-slate-200 bg-white">

        <!-- Quick links -->
        <div class="border-b border-slate-200 px-4 py-3">
          <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-graphite">Wagtail quick links</p>
          <div class="space-y-1">
            <a
              v-for="link in publishing.adminLinks"
              :key="link.label"
              :href="link.href"
              target="_blank"
              rel="noreferrer"
              class="flex items-center justify-between rounded-lg px-2.5 py-1.5 text-xs font-medium text-graphite hover:bg-slate-50 hover:text-ink transition-colors"
            >
              <span>{{ link.label }}</span>
              <ExternalLink class="size-3 shrink-0 text-slate-400" />
            </a>
          </div>
        </div>

        <!-- Link suggestions tool -->
        <div class="border-b border-slate-200">
          <button
            class="flex w-full items-center justify-between px-4 py-3 text-left"
            @click="showLinkTool = !showLinkTool"
          >
            <div class="flex items-center gap-2">
              <Link2 class="size-4 text-graphite" />
              <span class="text-xs font-semibold text-ink">Link suggestions</span>
            </div>
            <ChevronDown
              class="size-3.5 text-graphite transition-transform"
              :class="showLinkTool ? 'rotate-180' : ''"
            />
          </button>

          <div v-if="showLinkTool" class="px-4 pb-4 space-y-3">
            <div class="flex gap-2">
              <input
                v-model.number="linkSuggestionPageId"
                type="number"
                class="focus-ring min-w-0 flex-1 rounded-lg border border-slate-200 px-2.5 py-1.5 text-xs"
                placeholder="Page ID"
                @keydown.enter="fetchLinkSuggestions"
              />
              <button
                class="rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-xs font-semibold text-graphite hover:bg-slate-100 disabled:opacity-50"
                :disabled="isFetchingSuggestions || !linkSuggestionPageId"
                @click="fetchLinkSuggestions"
              >
                <Loader2 v-if="isFetchingSuggestions" class="size-3.5 animate-spin" />
                <span v-else>Analyse</span>
              </button>
            </div>

            <div v-if="linkSuggestions.length" class="space-y-1.5">
              <a
                v-for="s in linkSuggestions"
                :key="s.page_id"
                :href="s.url ?? '#'"
                target="_blank"
                rel="noreferrer"
                class="block rounded-lg border border-slate-200 p-2.5 text-xs hover:border-berry/40 hover:bg-slate-50 transition-colors"
              >
                <div class="flex items-start justify-between gap-2">
                  <p class="font-semibold text-ink leading-snug line-clamp-2">{{ s.title }}</p>
                  <span class="shrink-0 rounded-full bg-emerald-100 px-1.5 py-0.5 text-xs font-bold text-emerald-700">
                    {{ (s.score * 100).toFixed(0) }}%
                  </span>
                </div>
                <p class="mt-0.5 text-slate-400">{{ s.reason }}</p>
              </a>
            </div>
            <p v-else-if="!isFetchingSuggestions" class="text-xs text-graphite text-center py-2">
              Enter a Wagtail page ID to get link suggestions.
            </p>
          </div>
        </div>

        <!-- Staff responsibilities (collapsible) -->
        <div v-if="visibleResponsibilities.length" class="border-b border-slate-200">
          <button
            class="flex w-full items-center justify-between px-4 py-3 text-left"
            @click="publishing.activeType = publishing.activeType"
          >
            <div class="flex items-center gap-2">
              <Users class="size-4 text-graphite" />
              <span class="text-xs font-semibold text-ink">Role responsibilities</span>
            </div>
          </button>
          <div class="space-y-2 px-4 pb-4">
            <div
              v-for="role in visibleResponsibilities"
              :key="role.role"
              class="rounded-lg border border-slate-100 bg-slate-50 p-3"
            >
              <p class="text-xs font-semibold text-ink">{{ role.label }}</p>
              <ul class="mt-2 space-y-1">
                <li v-for="action in role.actions" :key="action" class="flex gap-1.5 text-xs text-graphite">
                  <CheckCircle2 class="mt-0.5 size-3 shrink-0 text-emerald-500" />
                  {{ action }}
                </li>
              </ul>
            </div>
          </div>
        </div>

      </aside>
    </div>

    <!-- ── Create page slide-over ─────────────────────────────────────── -->
    <Teleport to="body">
      <div
        v-if="showCreate"
        class="fixed inset-0 z-40 flex"
        @click.self="showCreate = false"
      >
        <div class="absolute inset-0 bg-black/30" @click="showCreate = false" />

        <div class="relative ml-auto flex h-full w-full max-w-md flex-col bg-white shadow-2xl">
          <!-- Header -->
          <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
            <div class="flex items-center gap-2">
              <FilePenLine class="size-5 text-berry" />
              <div>
                <h2 class="font-bold text-ink">New page</h2>
                <p class="text-xs text-graphite">Draft or publish a new piece of content</p>
              </div>
            </div>
            <button class="rounded p-1 text-graphite hover:text-ink" @click="showCreate = false">
              <X class="size-5" />
            </button>
          </div>

          <!-- Form -->
          <div class="flex-1 overflow-y-auto px-5 py-5 space-y-4">

            <!-- Website selector — superadmin only (admin is scoped by site) -->
            <div v-if="isSuperAdmin">
              <p class="mb-1.5 text-xs font-semibold uppercase tracking-wide text-graphite">
                Publishing to
              </p>
              <WebsiteSelectorBar
                v-model="publishing.draft.website"
                label="Website:"
              />
            </div>

            <!-- Type selector — visual cards -->
            <div>
              <p class="mb-2 text-xs font-semibold uppercase tracking-wide text-graphite">Content type</p>
              <div class="grid gap-2">
                <button
                  v-for="ct in contentTypes"
                  :key="ct.key"
                  class="rounded-xl border-2 px-4 py-3 text-left transition-all"
                  :class="publishing.draft.type === ct.key
                    ? 'border-berry bg-berry/5'
                    : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'"
                  @click="publishing.draft.type = ct.key"
                >
                  <p class="text-sm font-semibold text-ink">{{ ct.label }}</p>
                  <p class="mt-0.5 text-xs text-graphite">{{ ct.hint }}</p>
                </button>
              </div>
            </div>

            <!-- Route hint -->
            <div class="rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs">
              <p class="font-semibold text-ink">{{ publishing.selectedWritePath.title }}</p>
              <p class="mt-0.5 text-graphite leading-5">{{ publishing.selectedWritePath.detail }}</p>
              <p v-if="isStaff && publishing.draft.website" class="mt-1.5 font-medium text-ink">
                Publishing to: <span class="text-berry">{{ websites.nameById(publishing.draft.website) }}</span>
              </p>
            </div>

            <!-- Core fields -->
            <label class="block">
              <span class="text-xs font-semibold text-graphite">Title <span class="text-rose-500">*</span></span>
              <input
                v-model="publishing.draft.title"
                class="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                type="text"
                placeholder="How to write a research paper"
              />
            </label>

            <label class="block">
              <span class="text-xs font-semibold text-graphite">URL slug <span class="text-rose-500">*</span></span>
              <div class="mt-1 flex items-center">
                <span class="rounded-l-lg border border-r-0 border-slate-200 bg-slate-50 px-2.5 py-2 text-xs text-graphite">/lp/</span>
                <input
                  v-model="publishing.draft.slug"
                  class="focus-ring min-w-0 flex-1 rounded-r-lg border border-slate-200 px-3 py-2 text-sm"
                  type="text"
                  placeholder="how-to-write-research-paper"
                />
              </div>
            </label>

            <label class="block">
              <span class="text-xs font-semibold text-graphite">Meta description</span>
              <textarea
                v-model="publishing.draft.meta_description"
                class="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                rows="3"
                placeholder="A concise description for search results (150–160 chars)…"
                maxlength="160"
              />
            </label>

            <!-- Schedule (SEO only) -->
            <label v-if="publishing.draft.type === 'seo'" class="block">
              <span class="text-xs font-semibold text-graphite">Schedule publish <span class="font-normal text-slate-400">(optional)</span></span>
              <input
                v-model="publishing.draft.publish_date"
                type="datetime-local"
                class="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                :min="new Date().toISOString().slice(0, 16)"
              />
            </label>

            <!-- Advanced fields (collapsible) -->
            <div>
              <button
                class="flex items-center gap-1.5 text-xs font-semibold text-graphite hover:text-ink"
                @click="showAdvanced = !showAdvanced"
              >
                <ChevronDown class="size-3.5 transition-transform" :class="showAdvanced ? 'rotate-180' : ''" />
                {{ showAdvanced ? 'Hide' : 'Show' }} advanced fields
              </button>

              <div v-if="showAdvanced" class="mt-3 space-y-3">
                <label class="block">
                  <span class="text-xs font-semibold text-graphite">Primary keyword</span>
                  <input v-model="publishing.draft.primary_keyword" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" type="text" placeholder="e.g. research paper help" />
                </label>
                <label class="block">
                  <span class="text-xs font-semibold text-graphite">Target audience</span>
                  <input v-model="publishing.draft.audience" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" type="text" placeholder="e.g. undergraduate students" />
                </label>
                <div class="grid grid-cols-2 gap-3">
                  <label class="block">
                    <span class="text-xs font-semibold text-graphite">CTA label</span>
                    <input v-model="publishing.draft.cta_label" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" type="text" />
                  </label>
                  <label class="block">
                    <span class="text-xs font-semibold text-graphite">CTA href</span>
                    <input v-model="publishing.draft.cta_href" class="focus-ring mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm" type="text" />
                  </label>
                </div>
              </div>
            </div>

          </div>

          <!-- Footer actions -->
          <div class="border-t border-slate-200 px-5 py-4">
            <div class="flex gap-2">
              <button
                class="focus-ring flex-1 rounded-lg border border-slate-200 bg-white py-2.5 text-sm font-semibold text-graphite hover:bg-slate-50 disabled:opacity-60"
                :disabled="publishing.isMutating"
                @click="publishing.createContentDraft(false).catch(() => undefined)"
              >
                <FilePenLine class="inline size-4 mr-1" />Save draft
              </button>
              <button
                class="focus-ring flex-1 rounded-lg bg-berry py-2.5 text-sm font-semibold text-white hover:bg-rose-700 disabled:opacity-60"
                :disabled="publishing.isMutating"
                @click="publishing.createContentDraft(true).catch(() => undefined)"
              >
                <Send class="inline size-4 mr-1" />{{ publishing.selectedWritePath.actionLabel }}
              </button>
            </div>
            <p class="mt-2 text-center text-xs text-graphite">
              {{ publishing.draft.type === 'seo'
                  ? 'SEO pages are saved directly from this desk.'
                  : 'Draft is created in Wagtail and the editor opens in a new tab.' }}
            </p>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

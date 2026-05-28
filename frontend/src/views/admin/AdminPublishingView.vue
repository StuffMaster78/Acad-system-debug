<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import {
  CheckCircle2,
  ExternalLink,
  FilePenLine,
  Globe2,
  LibraryBig,
  Newspaper,
  RefreshCw,
  Search,
  Send,
  Sparkles,
} from "@lucide/vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useAdminPublishingStore } from "@/stores/adminPublishing";
import type { PublishingContentType, PublishingItem } from "@/types/adminPublishing";

const route = useRoute();
const publishing = useAdminPublishingStore();

const metricToneClasses = {
  neutral: "border-slate-200 bg-white",
  good: "border-emerald-200 bg-emerald-50",
  warn: "border-amber-200 bg-amber-50",
  risk: "border-rose-200 bg-rose-50",
};

const tabs: Array<{ key: PublishingContentType | "all"; label: string }> = [
  { key: "all", label: "All" },
  { key: "blog", label: "Blog articles" },
  { key: "service", label: "Service pages" },
  { key: "seo", label: "SEO pages" },
];

const contentTypes: Array<{ key: PublishingContentType; label: string; hint: string }> = [
  { key: "blog", label: "Blog article", hint: "Editorial content managed in Wagtail." },
  { key: "service", label: "Service page", hint: "Rich service page managed in Wagtail." },
  { key: "seo", label: "SEO landing page", hint: "Structured page managed through the SEO API." },
];

const roleLabel = computed(() => {
  const segment = String(route.path.split("/")[1] || "staff");
  if (segment === "superadmin") return "Superadmin";
  return segment.charAt(0).toUpperCase() + segment.slice(1);
});

const visibleResponsibilities = computed(() => {
  const current = String(route.path.split("/")[1] || "");
  return publishing.roleResponsibilities.filter((item) => item.role === current || current === "superadmin");
});

function formatDate(value: string | null) {
  if (!value) return "Not published";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function statusTone(status: string) {
  if (status === "published") return "success";
  if (status.includes("ready")) return "neutral";
  return "warning";
}

function typeLabel(type: PublishingContentType) {
  if (type === "blog") return "Blog";
  if (type === "service") return "Service";
  return "SEO";
}

function sourceLabel(item: PublishingItem) {
  return item.source === "wagtail" ? "Wagtail CMS" : "SEO pages API";
}

onMounted(() => {
  publishing.hydrate().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-8">
    <section class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase text-signal">{{ roleLabel }} publishing</p>
        <h1 class="mt-2 text-3xl font-semibold">Publishing desk</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          A single staff flow for blog articles, service pages, and SEO landing pages.
          Wagtail owns rich editorial pages; the SEO pages API owns fast structured landing pages.
        </p>
      </div>
      <div class="flex flex-wrap gap-2">
        <a
          class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
          href="/cms-admin/pages/"
          target="_blank"
          rel="noreferrer"
        >
          <ExternalLink class="h-4 w-4" />
          CMS pages
        </a>
        <button
          class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold disabled:opacity-60"
          type="button"
          :disabled="publishing.isLoading"
          @click="publishing.hydrate().catch(() => undefined)"
        >
          <RefreshCw class="h-4 w-4" :class="{ 'animate-spin': publishing.isLoading }" />
          Refresh
        </button>
      </div>
    </section>

    <p
      v-if="publishing.error"
      class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {{ publishing.error }} Preview mode will still show the publishing structure.
    </p>

    <p
      v-if="publishing.notice"
      class="rounded-md border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-900"
    >
      {{ publishing.notice }}
    </p>

    <section class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      <div
        v-for="metric in publishing.metrics"
        :key="metric.label"
        class="min-h-32 rounded-md border p-4"
        :class="metricToneClasses[metric.tone]"
      >
        <p class="text-sm font-medium text-graphite">{{ metric.label }}</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ metric.value }}</p>
        <p class="mt-2 text-sm leading-5 text-graphite">{{ metric.detail }}</p>
      </div>
    </section>

    <section class="rounded-md border border-slate-200 bg-white p-4">
      <div class="flex items-center gap-2">
        <Sparkles class="h-5 w-5 text-signal" />
        <h2 class="text-base font-semibold">Structural flow</h2>
      </div>
      <div class="mt-4 grid gap-3 md:grid-cols-3 xl:grid-cols-6">
        <div
          v-for="(step, index) in publishing.flowSteps"
          :key="step.label"
          class="rounded-md border border-slate-200 bg-slate-50 p-3"
        >
          <div class="flex items-center justify-between gap-2">
            <span class="inline-flex h-7 w-7 items-center justify-center rounded-full bg-ink text-xs font-semibold text-white">
              {{ index + 1 }}
            </span>
            <StatusPill :label="step.owner" tone="neutral" />
          </div>
          <h3 class="mt-3 text-sm font-semibold text-ink">{{ step.label }}</h3>
          <p class="mt-2 text-xs leading-5 text-graphite">{{ step.detail }}</p>
        </div>
      </div>
    </section>

    <section class="grid gap-6 xl:grid-cols-[minmax(0,1.35fr)_minmax(360px,0.85fr)]">
      <div class="rounded-md border border-slate-200 bg-white">
        <div class="flex flex-col gap-4 border-b border-slate-200 px-4 py-4 lg:flex-row lg:items-center lg:justify-between">
          <div class="flex items-center gap-2">
            <Newspaper class="h-5 w-5 text-signal" />
            <div>
              <h2 class="text-base font-semibold">Content inventory</h2>
              <p class="text-sm text-graphite">Wagtail pages and SEO landing pages staff can act on.</p>
            </div>
          </div>

          <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
            <div class="inline-flex rounded-md border border-slate-200 bg-slate-50 p-1">
              <button
                v-for="tab in tabs"
                :key="tab.key"
                class="focus-ring min-h-9 rounded px-3 text-sm font-semibold"
                :class="publishing.activeType === tab.key ? 'bg-white text-ink shadow-sm' : 'text-graphite'"
                type="button"
                @click="publishing.activeType = tab.key"
              >
                {{ tab.label }}
              </button>
            </div>
            <label class="relative block min-w-64">
              <Search class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-graphite" />
              <input
                v-model="publishing.query"
                class="focus-ring h-10 w-full rounded-md border border-slate-200 bg-white pl-9 pr-3 text-sm"
                type="search"
                placeholder="Search content"
              >
            </label>
          </div>
        </div>

        <div v-if="publishing.filteredItems.length" class="overflow-x-auto">
          <table class="min-w-full divide-y divide-slate-200 text-sm">
            <thead class="bg-slate-50 text-left text-xs font-semibold uppercase text-graphite">
              <tr>
                <th class="px-3 py-2">Title</th>
                <th class="px-3 py-2">Type</th>
                <th class="px-3 py-2">Source</th>
                <th class="px-3 py-2">Status</th>
                <th class="px-3 py-2">Published</th>
                <th class="px-3 py-2">Action</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="item in publishing.filteredItems" :key="`${item.source}-${item.id}`">
                <td class="px-3 py-2.5">
                  <p class="font-semibold text-ink">{{ item.title }}</p>
                  <p class="mt-1 text-xs text-graphite">/{{ item.slug }}/</p>
                  <p v-if="item.summary" class="mt-1 max-w-lg text-xs leading-5 text-graphite">{{ item.summary }}</p>
                </td>
                <td class="px-3 py-2.5">
                  <StatusPill :label="typeLabel(item.type)" />
                </td>
                <td class="px-3 py-2.5 text-graphite">
                  {{ sourceLabel(item) }}
                </td>
                <td class="px-3 py-2.5">
                  <StatusPill :label="item.status" :tone="statusTone(item.status)" />
                </td>
                <td class="px-3 py-2.5 text-graphite">
                  {{ formatDate(item.publishedAt) }}
                </td>
                <td class="px-3 py-2.5">
                  <button
                    v-if="item.source === 'seo_pages'"
                    class="focus-ring inline-flex h-9 items-center justify-center rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold disabled:opacity-60"
                    type="button"
                    :disabled="publishing.isMutating"
                    @click="publishing.setPublishState(item, item.status !== 'published').catch(() => undefined)"
                  >
                    {{ item.status === "published" ? "Unpublish" : "Publish" }}
                  </button>
                  <a
                    v-else
                    class="focus-ring inline-flex h-9 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-xs font-semibold"
                    :href="item.url || '/cms-admin/pages/'"
                    target="_blank"
                    rel="noreferrer"
                  >
                    <ExternalLink class="h-3.5 w-3.5" />
                    CMS
                  </a>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else class="p-4">
          <EmptyState
            :icon="Newspaper"
            title="No content found"
            message="Refresh when the CMS backend is online or adjust the filters."
          />
        </div>
      </div>

      <aside class="space-y-4">
        <section class="rounded-md border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2">
            <FilePenLine class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold">Create publishing draft</h2>
          </div>
          <p class="mt-2 text-sm leading-6 text-graphite">
            Pick the page type first. The desk will send SEO pages through the API and direct rich content to Wagtail.
          </p>

          <div class="mt-4 space-y-3">
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Content type</span>
              <select
                v-model="publishing.draft.type"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 bg-white px-3 text-sm"
              >
                <option v-for="type in contentTypes" :key="type.key" :value="type.key">
                  {{ type.label }}
                </option>
              </select>
              <span class="mt-1 block text-xs text-graphite">
                {{ contentTypes.find((type) => type.key === publishing.draft.type)?.hint }}
              </span>
            </label>

            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Title</span>
              <input
                v-model="publishing.draft.title"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="text"
              >
            </label>

            <div class="grid gap-3 sm:grid-cols-2">
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Slug</span>
                <input
                  v-model="publishing.draft.slug"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  type="text"
                >
              </label>
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">Website ID</span>
                <input
                  v-model.number="publishing.draft.website"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  min="1"
                  type="number"
                >
              </label>
            </div>

            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Primary keyword</span>
              <input
                v-model="publishing.draft.primary_keyword"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="text"
              >
            </label>

            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Audience</span>
              <input
                v-model="publishing.draft.audience"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="text"
              >
            </label>

            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Summary / meta description</span>
              <textarea
                v-model="publishing.draft.meta_description"
                class="focus-ring mt-1 min-h-28 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
              />
            </label>

            <div class="grid gap-3 sm:grid-cols-2">
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">CTA label</span>
                <input
                  v-model="publishing.draft.cta_label"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  type="text"
                >
              </label>
              <label class="block">
                <span class="text-xs font-semibold uppercase text-graphite">CTA href</span>
                <input
                  v-model="publishing.draft.cta_href"
                  class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                  type="text"
                >
              </label>
            </div>
          </div>

          <div class="mt-4 rounded-md border border-slate-200 bg-slate-50 p-3">
            <p class="text-sm font-semibold text-ink">{{ publishing.selectedWritePath.title }}</p>
            <p class="mt-1 text-xs leading-5 text-graphite">{{ publishing.selectedWritePath.detail }}</p>
          </div>

          <div class="mt-4 grid gap-2">
            <button
              class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold disabled:opacity-60"
              type="button"
              :disabled="publishing.isMutating"
              @click="publishing.createContentDraft(false).catch(() => undefined)"
            >
              <FilePenLine class="h-4 w-4" />
              Save draft
            </button>
            <button
              class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md bg-ink px-3 text-sm font-semibold text-white disabled:opacity-60"
              type="button"
              :disabled="publishing.isMutating"
              @click="publishing.createContentDraft(true).catch(() => undefined)"
            >
              <Send class="h-4 w-4" />
              {{ publishing.selectedWritePath.actionLabel }}
            </button>
          </div>
        </section>

        <section class="rounded-md border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2">
            <LibraryBig class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold">Taxonomy & profiles</h2>
          </div>
          <p class="mt-2 text-sm leading-6 text-graphite">
            Authors, categories, and tags are CMS objects. Create them first, then attach them while drafting blog and service pages.
          </p>

          <div class="mt-4 space-y-3">
            <a
              v-for="link in publishing.adminLinks"
              :key="link.label"
              class="focus-ring block rounded-md border border-slate-200 bg-slate-50 p-3 transition hover:border-signal/50 hover:bg-white"
              :href="link.href"
              target="_blank"
              rel="noreferrer"
            >
              <span class="flex items-center justify-between gap-3">
                <span class="text-sm font-semibold text-ink">{{ link.label }}</span>
                <ExternalLink class="h-4 w-4 shrink-0 text-graphite" />
              </span>
              <span class="mt-1 block text-xs leading-5 text-graphite">{{ link.detail }}</span>
              <span class="mt-2 inline-flex rounded-md border border-slate-200 bg-white px-2 py-1 text-xs font-semibold text-graphite">
                {{ link.owner }}
              </span>
            </a>
          </div>
        </section>

        <section class="rounded-md border border-slate-200 bg-white p-4">
          <div class="flex items-center gap-2">
            <Globe2 class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold">Staff ownership</h2>
          </div>
          <div class="mt-4 space-y-3">
            <div
              v-for="role in visibleResponsibilities"
              :key="role.role"
              class="rounded-md border border-slate-200 bg-slate-50 p-3"
            >
              <p class="text-sm font-semibold text-ink">{{ role.label }}</p>
              <p class="mt-1 text-xs leading-5 text-graphite">{{ role.scope }}</p>
              <ul class="mt-3 space-y-2">
                <li v-for="action in role.actions" :key="action" class="flex gap-2 text-xs text-graphite">
                  <CheckCircle2 class="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-600" />
                  <span>{{ action }}</span>
                </li>
              </ul>
            </div>
          </div>
        </section>
      </aside>
    </section>
  </div>
</template>

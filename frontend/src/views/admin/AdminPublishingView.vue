<script setup lang="ts">
import { onMounted } from "vue";
import {
  ExternalLink,
  FilePenLine,
  Newspaper,
  RefreshCw,
  Search,
  Send,
} from "@lucide/vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import StatusPill from "@/components/ui/StatusPill.vue";
import { useAdminPublishingStore } from "@/stores/adminPublishing";
import type { PublishingContentType } from "@/types/adminPublishing";

const publishing = useAdminPublishingStore();

const metricToneClasses = {
  neutral: "border-slate-200 bg-white",
  good: "border-emerald-200 bg-emerald-50",
  warn: "border-amber-200 bg-amber-50",
  risk: "border-rose-200 bg-rose-50",
};

const tabs: Array<{ key: PublishingContentType | "all"; label: string }> = [
  { key: "all", label: "All" },
  { key: "blog", label: "Blogs" },
  { key: "service", label: "Services" },
  { key: "seo", label: "Landing pages" },
];

function formatDate(value: string | null) {
  if (!value) return "Not published";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function statusTone(status: string) {
  return status === "published" ? "success" : "warning";
}

function typeLabel(type: PublishingContentType) {
  if (type === "blog") return "Blog";
  if (type === "service") return "Service";
  return "Landing";
}

onMounted(() => {
  publishing.hydrate().catch(() => undefined);
});
</script>

<template>
  <div class="space-y-8">
    <section class="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase text-signal">Admin</p>
        <h1 class="mt-2 text-3xl font-semibold">Publishing</h1>
        <p class="mt-2 max-w-3xl text-sm leading-6 text-graphite">
          Blog posts, service pages, and SEO landing pages for staff publishing.
          Wagtail remains the full CMS editor; this console gives operations a fast overview and landing-page path.
        </p>
      </div>
      <div class="flex flex-wrap gap-2">
        <a
          class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
          href="/cms-admin/"
          target="_blank"
          rel="noreferrer"
        >
          <ExternalLink class="h-4 w-4" />
          Wagtail admin
        </a>
        <button
          class="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-4 text-sm font-semibold"
          type="button"
          @click="publishing.hydrate"
        >
          <RefreshCw class="h-4 w-4" />
          Refresh
        </button>
      </div>
    </section>

    <p
      v-if="publishing.error"
      class="rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900"
    >
      {{ publishing.error }} Preview mode will still show the layout.
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
        class="min-h-32 rounded-md border p-4 shadow-panel"
        :class="metricToneClasses[metric.tone]"
      >
        <p class="text-sm font-medium text-graphite">{{ metric.label }}</p>
        <p class="mt-3 text-3xl font-semibold text-ink">{{ metric.value }}</p>
        <p class="mt-2 text-sm leading-5 text-graphite">{{ metric.detail }}</p>
      </div>
    </section>

    <section class="grid gap-6 xl:grid-cols-[minmax(0,1.4fr)_minmax(360px,0.8fr)]">
      <div class="rounded-md border border-slate-200 bg-white shadow-panel">
        <div class="flex flex-col gap-4 border-b border-slate-200 px-4 py-4 lg:flex-row lg:items-center lg:justify-between">
          <div class="flex items-center gap-2">
            <Newspaper class="h-5 w-5 text-signal" />
            <div>
              <h2 class="text-base font-semibold">Content inventory</h2>
              <p class="text-sm text-graphite">Wagtail pages and SEO landing pages visible to admin staff.</p>
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
                <th class="px-4 py-3">Title</th>
                <th class="px-4 py-3">Type</th>
                <th class="px-4 py-3">Source</th>
                <th class="px-4 py-3">Status</th>
                <th class="px-4 py-3">Published</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="item in publishing.filteredItems" :key="`${item.source}-${item.id}`">
                <td class="px-4 py-4">
                  <p class="font-semibold text-ink">{{ item.title }}</p>
                  <p class="mt-1 text-xs text-graphite">/{{ item.slug }}/</p>
                  <p v-if="item.summary" class="mt-1 max-w-lg text-xs text-graphite">{{ item.summary }}</p>
                </td>
                <td class="px-4 py-4">
                  <StatusPill :label="typeLabel(item.type)" />
                </td>
                <td class="px-4 py-4 text-graphite">
                  {{ item.source === "wagtail" ? "Wagtail CMS" : "SEO pages API" }}
                </td>
                <td class="px-4 py-4">
                  <StatusPill :label="item.status" :tone="statusTone(item.status)" />
                </td>
                <td class="px-4 py-4 text-graphite">
                  {{ formatDate(item.publishedAt) }}
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

      <aside class="space-y-6">
        <section class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
          <div class="flex items-center gap-2">
            <FilePenLine class="h-5 w-5 text-signal" />
            <h2 class="text-base font-semibold">Quick landing page</h2>
          </div>
          <p class="mt-2 text-sm leading-6 text-graphite">
            Creates a service-style SEO page through the current backend API. Full blog and rich service pages still go through Wagtail.
          </p>

          <div class="mt-4 space-y-3">
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Title</span>
              <input
                v-model="publishing.draft.title"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="text"
              >
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Slug</span>
              <input
                v-model="publishing.draft.slug"
                class="focus-ring mt-1 h-10 w-full rounded-md border border-slate-200 px-3 text-sm"
                type="text"
              >
            </label>
            <label class="block">
              <span class="text-xs font-semibold uppercase text-graphite">Meta description</span>
              <textarea
                v-model="publishing.draft.meta_description"
                class="focus-ring mt-1 min-h-28 w-full rounded-md border border-slate-200 px-3 py-2 text-sm"
              />
            </label>
          </div>

          <div class="mt-4 grid gap-2">
            <button
              class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold"
              type="button"
              :disabled="publishing.isMutating"
              @click="publishing.createLandingPage(false).catch(() => undefined)"
            >
              <FilePenLine class="h-4 w-4" />
              Save draft
            </button>
            <button
              class="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded-md bg-ink px-3 text-sm font-semibold text-white"
              type="button"
              :disabled="publishing.isMutating"
              @click="publishing.createLandingPage(true).catch(() => undefined)"
            >
              <Send class="h-4 w-4" />
              Publish landing page
            </button>
          </div>
        </section>

        <section class="rounded-md border border-slate-200 bg-white p-4 shadow-panel">
          <h2 class="text-base font-semibold">CMS write path</h2>
          <p class="mt-2 text-sm leading-6 text-graphite">
            Blog posts and rich service pages should be created in Wagtail so staff get workflows, preview, media, StreamField blocks, and approvals.
          </p>
          <a
            class="focus-ring mt-4 inline-flex h-10 items-center justify-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm font-semibold"
            href="/cms-admin/pages/"
            target="_blank"
            rel="noreferrer"
          >
            <ExternalLink class="h-4 w-4" />
            Open CMS pages
          </a>
        </section>
      </aside>
    </section>
  </div>
</template>

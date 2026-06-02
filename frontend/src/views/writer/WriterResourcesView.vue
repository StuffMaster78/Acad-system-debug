<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import {
  BookOpen, Download, ExternalLink, FileText, Loader2,
  RefreshCw, Tag, Video, Wrench,
} from "@lucide/vue";
import { api, apiPath } from "@/api/client";

interface ResourceCategory {
  id: number;
  name: string;
}

interface WriterResource {
  id: number;
  title: string;
  description: string;
  resource_type: string;
  resource_type_display: string;
  category: number | null;
  category_name: string | null;
  file: string | null;
  external_url: string;
  video_url: string;
  content: string;
  is_featured: boolean;
  has_file: boolean;
  has_external_url: boolean;
  created_at: string;
}

interface DownloadResult {
  download_url?: string;
  url?: string;
  message?: string;
}

const resources = ref<WriterResource[]>([]);
const categories = ref<ResourceCategory[]>([]);
const loading = ref(false);
const activeCategory = ref<number | null>(null);
const downloadingId = ref<number | null>(null);
const downloadError = ref("");

const typeIcon: Record<string, typeof FileText> = {
  document: FileText,
  video: Video,
  link: ExternalLink,
  article: BookOpen,
  tool: Wrench,
};

const featured = computed(() => resources.value.filter((r) => r.is_featured));
const filtered = computed(() => {
  const all = resources.value.filter((r) => !r.is_featured);
  if (!activeCategory.value) return all;
  return all.filter((r) => r.category === activeCategory.value);
});

async function load() {
  loading.value = true;
  try {
    const { data } = await api.get<WriterResource[] | { results: WriterResource[] }>(
      apiPath("/writer-management/resources/"),
    );
    const list: WriterResource[] = Array.isArray(data) ? data : (data as { results: WriterResource[] }).results ?? [];
    resources.value = list;
    const seen = new Set<number>();
    categories.value = list
      .filter((r) => r.category !== null && r.category_name)
      .filter((r) => { if (seen.has(r.category!)) return false; seen.add(r.category!); return true; })
      .map((r) => ({ id: r.category!, name: r.category_name! }))
      .sort((a, b) => a.name.localeCompare(b.name));
  } catch {
    // non-critical
  } finally {
    loading.value = false;
  }
}

async function openResource(resource: WriterResource) {
  downloadError.value = "";
  if (resource.has_external_url && resource.external_url) {
    window.open(resource.external_url, "_blank", "noopener");
    return;
  }
  if (resource.video_url) {
    window.open(resource.video_url, "_blank", "noopener");
    return;
  }
  if (resource.has_file) {
    downloadingId.value = resource.id;
    try {
      const { data } = await api.post<DownloadResult>(
        apiPath(`/writer-management/resources/${resource.id}/download/`), {},
      );
      const url = data.download_url ?? data.url;
      if (url) window.open(url, "_blank", "noopener");
    } catch {
      downloadError.value = "Could not retrieve the download link. Please try again.";
    } finally {
      downloadingId.value = null;
    }
  }
}

function resourceAction(r: WriterResource): string {
  if (r.resource_type === "article") return "Read";
  if (r.resource_type === "video") return "Watch";
  if (r.has_external_url || r.resource_type === "link") return "Open";
  return "Download";
}

function fmtDate(v: string) {
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric" }).format(new Date(v));
}

onMounted(load);
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <section class="flex flex-col gap-4 border-b border-slate-200 pb-6 lg:flex-row lg:items-end lg:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-wide text-signal">Writer workspace</p>
        <h1 class="mt-2 text-3xl font-semibold text-ink">Resources</h1>
        <p class="mt-2 text-sm text-graphite">Training materials, guides, templates, and tools for your work.</p>
      </div>
      <button
        class="focus-ring inline-flex items-center gap-2 rounded-md border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold disabled:opacity-60"
        type="button"
        :disabled="loading"
        @click="load"
      >
        <Loader2 v-if="loading" class="h-4 w-4 animate-spin" />
        <RefreshCw v-else class="h-4 w-4" />
        Refresh
      </button>
    </section>

    <div v-if="loading && !resources.length" class="py-20 text-center text-sm text-graphite">
      Loading resources…
    </div>

    <div v-else-if="!resources.length" class="rounded-lg border border-slate-200 bg-white px-6 py-16 text-center">
      <BookOpen class="mx-auto h-8 w-8 text-slate-300" />
      <p class="mt-3 text-sm font-medium text-ink">No resources yet</p>
      <p class="mt-1 text-sm text-graphite">Training materials added by your team will appear here.</p>
    </div>

    <template v-else>
      <p v-if="downloadError" class="rounded-md border border-rose-200 bg-rose-50 px-4 py-2.5 text-sm text-rose-800">
        {{ downloadError }}
      </p>

      <!-- Featured resources -->
      <section v-if="featured.length">
        <h2 class="mb-3 text-xs font-semibold uppercase tracking-wide text-graphite">Featured</h2>
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <div
            v-for="r in featured"
            :key="r.id"
            class="flex flex-col rounded-xl border border-signal/30 bg-white p-5 shadow-sm"
          >
            <div class="flex items-start gap-3">
              <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-signal/10">
                <component :is="typeIcon[r.resource_type] ?? FileText" class="h-4 w-4 text-signal" />
              </div>
              <div class="min-w-0 flex-1">
                <p class="font-semibold text-ink">{{ r.title }}</p>
                <p v-if="r.category_name" class="mt-0.5 text-xs text-graphite">{{ r.category_name }}</p>
              </div>
            </div>
            <p v-if="r.description" class="mt-3 text-sm leading-6 text-graphite line-clamp-2">{{ r.description }}</p>
            <button
              class="focus-ring mt-4 inline-flex items-center gap-1.5 self-start rounded-md bg-signal px-3 py-1.5 text-xs font-semibold text-white disabled:opacity-60"
              type="button"
              :disabled="downloadingId === r.id"
              @click="openResource(r)"
            >
              <Loader2 v-if="downloadingId === r.id" class="h-3 w-3 animate-spin" />
              <Download v-else-if="r.has_file" class="h-3 w-3" />
              <ExternalLink v-else class="h-3 w-3" />
              {{ resourceAction(r) }}
            </button>
          </div>
        </div>
      </section>

      <!-- Category filter -->
      <div v-if="categories.length > 1" class="flex flex-wrap gap-2">
        <button
          class="rounded-full border px-3.5 py-1 text-xs font-medium transition-colors"
          :class="activeCategory === null ? 'border-ink bg-ink text-white' : 'border-slate-200 bg-white text-graphite hover:border-slate-300'"
          @click="activeCategory = null"
        >All</button>
        <button
          v-for="cat in categories"
          :key="cat.id"
          class="rounded-full border px-3.5 py-1 text-xs font-medium transition-colors"
          :class="activeCategory === cat.id ? 'border-ink bg-ink text-white' : 'border-slate-200 bg-white text-graphite hover:border-slate-300'"
          @click="activeCategory = cat.id"
        >
          <Tag class="mr-1 inline h-3 w-3" />{{ cat.name }}
        </button>
      </div>

      <!-- Resource list -->
      <div v-if="filtered.length" class="divide-y divide-slate-100 rounded-xl border border-slate-200 bg-white">
        <div
          v-for="r in filtered"
          :key="r.id"
          class="flex items-start gap-4 px-5 py-4 hover:bg-slate-50 transition-colors"
        >
          <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-100">
            <component :is="typeIcon[r.resource_type] ?? FileText" class="h-4 w-4 text-graphite" />
          </div>
          <div class="min-w-0 flex-1">
            <p class="font-semibold text-ink">{{ r.title }}</p>
            <p v-if="r.description" class="mt-0.5 text-sm text-graphite line-clamp-1">{{ r.description }}</p>
            <div class="mt-1 flex flex-wrap items-center gap-3 text-xs text-slate-400">
              <span>{{ r.resource_type_display }}</span>
              <span v-if="r.category_name">{{ r.category_name }}</span>
              <span>{{ fmtDate(r.created_at) }}</span>
            </div>
          </div>
          <button
            class="focus-ring shrink-0 inline-flex items-center gap-1.5 rounded-md border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-graphite hover:bg-slate-50 disabled:opacity-60"
            type="button"
            :disabled="downloadingId === r.id"
            @click="openResource(r)"
          >
            <Loader2 v-if="downloadingId === r.id" class="h-3 w-3 animate-spin" />
            <Download v-else-if="r.has_file" class="h-3 w-3" />
            <ExternalLink v-else class="h-3 w-3" />
            {{ resourceAction(r) }}
          </button>
        </div>
      </div>

      <div v-else-if="activeCategory" class="rounded-lg border border-slate-100 bg-slate-50 py-10 text-center">
        <p class="text-sm text-graphite">No resources in this category.</p>
      </div>
    </template>
  </div>
</template>

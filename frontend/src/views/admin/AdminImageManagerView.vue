<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { CheckCircle2, Edit2, ExternalLink, ImageIcon, Loader2, RefreshCw, Search, Trash2, Upload, X } from "@lucide/vue";
import { api, apiPath } from "@/api/client";

interface PageImage {
  id: number;
  title: string;
  thumbnail: string | null;
  full: string | null;
}

interface PageRecord {
  id: number;
  type: "blog" | "service";
  title: string;
  slug: string;
  site: string;
  siteName: string;
  editUrl: string;
  image: PageImage | null;
}

interface ListResponse {
  results: PageRecord[];
  total: number;
  missing: number;
}

// ── state ─────────────────────────────────────────────────────────────────
const pages    = ref<PageRecord[]>([]);
const loading  = ref(false);
const error    = ref<string | null>(null);

const siteFilter    = ref("");
const typeFilter    = ref<"" | "blog" | "service">("");
const missingOnly   = ref(false);
const searchQuery   = ref("");

const uploading  = ref<Record<number, boolean>>({});
const removing   = ref<Record<number, boolean>>({});
const uploadErr  = ref<Record<number, string>>({});
const justDone   = ref<Record<number, boolean>>({});
const dragging   = ref<Record<number, boolean>>({});

const stats = ref({ total: 0, missing: 0 });

// ── derived ────────────────────────────────────────────────────────────────
const allSites = computed(() => {
  const seen = new Map<string, string>();
  for (const p of pages.value) {
    if (p.site && !seen.has(p.site)) seen.set(p.site, p.siteName || p.site);
  }
  return Array.from(seen.entries()).map(([k, v]) => ({ hostname: k, label: v }));
});

const filtered = computed(() => {
  let list = pages.value;
  if (siteFilter.value) list = list.filter(p => p.site === siteFilter.value);
  if (typeFilter.value) list = list.filter(p => p.type === typeFilter.value);
  if (missingOnly.value) list = list.filter(p => !p.image);
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    list = list.filter(p => p.title.toLowerCase().includes(q) || p.slug.includes(q));
  }
  return list;
});

const filteredMissing = computed(() => filtered.value.filter(p => !p.image).length);

// ── site colour coding ─────────────────────────────────────────────────────
const SITE_COLORS: Record<string, string> = {
  "nursemygrade.com":      "bg-teal-100 text-teal-700",
  "essaymaniacs.com":      "bg-violet-100 text-violet-700",
  "gradecrest.com":        "bg-green-100 text-green-700",
  "researchpapermate.com": "bg-amber-100 text-amber-700",
  "writerscreek.com":      "bg-rose-100 text-rose-700",
};
function siteColor(hostname: string) {
  return SITE_COLORS[hostname] ?? "bg-slate-100 text-slate-700";
}

// ── data loading ───────────────────────────────────────────────────────────
async function load() {
  loading.value = true;
  error.value = null;
  try {
    const res = await api.get<ListResponse>(apiPath("/cms-api/image-manager/pages/"));
    pages.value = res.data.results;
    stats.value = { total: res.data.total, missing: res.data.missing };
  } catch {
    error.value = "Could not load pages. Make sure the backend is running.";
  } finally {
    loading.value = false;
  }
}

// ── file upload ────────────────────────────────────────────────────────────
function openPicker(pageId: number) {
  const input = document.getElementById(`file-${pageId}`) as HTMLInputElement | null;
  input?.click();
}

function onFileChange(event: Event, pageId: number) {
  const file = (event.target as HTMLInputElement).files?.[0];
  if (file) uploadFile(pageId, file);
}

function onDrop(event: DragEvent, pageId: number) {
  dragging.value[pageId] = false;
  const file = event.dataTransfer?.files[0];
  if (file) uploadFile(pageId, file);
}

async function uploadFile(pageId: number, file: File) {
  const allowed = ["image/jpeg", "image/png", "image/webp", "image/avif"];
  if (!allowed.includes(file.type)) {
    uploadErr.value[pageId] = "Use a JPEG, PNG, or WebP image.";
    return;
  }
  uploading.value[pageId] = true;
  uploadErr.value[pageId] = "";
  const form = new FormData();
  form.append("image", file);
  try {
    const res = await api.post<PageRecord>(apiPath(`/cms-api/image-manager/pages/${pageId}/image/`), form);
    const idx = pages.value.findIndex(p => p.id === pageId);
    if (idx !== -1) pages.value[idx] = res.data;
    stats.value.missing = pages.value.filter(p => !p.image).length;
    // flash success state
    justDone.value[pageId] = true;
    setTimeout(() => { delete justDone.value[pageId]; }, 2500);
  } catch (err: any) {
    uploadErr.value[pageId] = err?.response?.data?.error ?? "Upload failed — try again.";
  } finally {
    uploading.value[pageId] = false;
  }
}

async function removeImage(pageId: number) {
  removing.value[pageId] = true;
  try {
    const res = await api.delete<PageRecord>(apiPath(`/cms-api/image-manager/pages/${pageId}/image/`));
    const idx = pages.value.findIndex(p => p.id === pageId);
    if (idx !== -1) pages.value[idx] = res.data;
    stats.value.missing = pages.value.filter(p => !p.image).length;
  } catch {
    // silent — image state will refresh on next load
  } finally {
    removing.value[pageId] = false;
  }
}

onMounted(load);
</script>

<template>
  <div class="space-y-6">

    <!-- Header -->
    <div class="flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 class="text-xl font-bold text-slate-900">Image Manager</h1>
        <p class="mt-0.5 text-sm text-slate-500">
          Upload and assign featured images for blog posts and service pages.
        </p>
      </div>
      <button
        class="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 shadow-sm transition hover:bg-slate-50 disabled:opacity-50"
        :disabled="loading"
        @click="load"
      >
        <RefreshCw class="h-3.5 w-3.5" :class="{ 'animate-spin': loading }" />
        Refresh
      </button>
    </div>

    <!-- Stats strip -->
    <div class="grid grid-cols-3 gap-3 sm:grid-cols-3">
      <div class="rounded-xl border border-slate-100 bg-white p-4 shadow-sm text-center">
        <p class="text-2xl font-bold text-slate-900">{{ stats.total }}</p>
        <p class="text-xs text-slate-500 mt-0.5">Total pages</p>
      </div>
      <div class="rounded-xl border border-slate-100 bg-white p-4 shadow-sm text-center">
        <p class="text-2xl font-bold" :class="stats.missing > 0 ? 'text-amber-600' : 'text-emerald-600'">{{ stats.missing }}</p>
        <p class="text-xs text-slate-500 mt-0.5">Missing images</p>
      </div>
      <div class="rounded-xl border border-slate-100 bg-white p-4 shadow-sm text-center">
        <p class="text-2xl font-bold text-emerald-600">{{ stats.total - stats.missing }}</p>
        <p class="text-xs text-slate-500 mt-0.5">Have images</p>
      </div>
    </div>

    <!-- Filters -->
    <div class="flex flex-wrap items-center gap-3">

      <!-- Search -->
      <div class="relative flex-1 min-w-[160px] max-w-xs">
        <Search class="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search pages…"
          class="w-full rounded-lg border border-slate-200 bg-white py-2 pl-9 pr-3 text-sm text-slate-800 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
        />
      </div>

      <!-- Site filter -->
      <select
        v-model="siteFilter"
        class="rounded-lg border border-slate-200 bg-white py-2 pl-3 pr-8 text-sm text-slate-700 focus:border-brand-400 focus:outline-none focus:ring-2 focus:ring-brand-100"
      >
        <option value="">All sites</option>
        <option v-for="s in allSites" :key="s.hostname" :value="s.hostname">{{ s.label }}</option>
      </select>

      <!-- Type filter -->
      <div class="flex overflow-hidden rounded-lg border border-slate-200 bg-white">
        <button
          v-for="opt in [{ v: '', l: 'All' }, { v: 'blog', l: 'Blog' }, { v: 'service', l: 'Services' }]"
          :key="opt.v"
          class="px-3 py-2 text-xs font-semibold transition-colors"
          :class="typeFilter === opt.v ? 'bg-brand-600 text-white' : 'text-slate-600 hover:bg-slate-50'"
          @click="typeFilter = opt.v as any"
        >{{ opt.l }}</button>
      </div>

      <!-- Missing only toggle -->
      <button
        class="flex items-center gap-1.5 rounded-lg border px-3 py-2 text-xs font-semibold transition-colors"
        :class="missingOnly ? 'border-amber-400 bg-amber-50 text-amber-700' : 'border-slate-200 bg-white text-slate-600 hover:bg-slate-50'"
        @click="missingOnly = !missingOnly"
      >
        <span class="inline-block h-2 w-2 rounded-full" :class="missingOnly ? 'bg-amber-500' : 'bg-slate-300'" />
        Missing only
      </button>

      <span class="text-xs text-slate-400 ml-auto">{{ filtered.length }} pages · {{ filteredMissing }} missing</span>
    </div>

    <!-- Error -->
    <div v-if="error" class="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
      {{ error }}
    </div>

    <!-- Loading skeleton -->
    <div v-else-if="loading" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      <div v-for="i in 12" :key="i" class="animate-pulse rounded-2xl border border-slate-100 bg-white overflow-hidden">
        <div class="aspect-video bg-slate-100" />
        <div class="p-3 space-y-2">
          <div class="h-3 w-3/4 rounded bg-slate-100" />
          <div class="h-2.5 w-1/2 rounded bg-slate-100" />
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-else-if="filtered.length === 0" class="rounded-2xl border border-slate-100 bg-white p-16 text-center">
      <ImageIcon class="mx-auto mb-3 h-10 w-10 text-slate-200" />
      <p class="text-sm font-semibold text-slate-600">No pages match your filters</p>
      <p class="mt-1 text-xs text-slate-400">Try removing some filters or refreshing the list.</p>
    </div>

    <!-- Page grid -->
    <div v-else class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">

      <div
        v-for="page in filtered"
        :key="page.id"
        class="group relative flex flex-col overflow-hidden rounded-2xl border bg-white shadow-sm transition"
        :class="[
          dragging[page.id] ? 'border-brand-400 ring-2 ring-brand-400 scale-[1.01]' : 'border-slate-100 hover:border-slate-200 hover:shadow-md',
          justDone[page.id] ? 'border-emerald-400' : '',
        ]"
        @dragover.prevent="dragging[page.id] = true"
        @dragleave="dragging[page.id] = false"
        @drop.prevent="onDrop($event, page.id)"
      >

        <!-- Hidden file input -->
        <input
          :id="`file-${page.id}`"
          type="file"
          accept="image/jpeg,image/png,image/webp,image/avif"
          class="sr-only"
          @change="onFileChange($event, page.id)"
        />

        <!-- Image area -->
        <div
          class="relative aspect-video cursor-pointer bg-slate-50 overflow-hidden"
          @click="openPicker(page.id)"
        >
          <!-- Has image -->
          <img
            v-if="page.image?.thumbnail"
            :src="page.image.thumbnail"
            :alt="page.title"
            class="h-full w-full object-cover transition-transform group-hover:scale-[1.02]"
          />

          <!-- No image placeholder -->
          <div v-else class="flex h-full flex-col items-center justify-center gap-2 text-slate-300">
            <ImageIcon class="h-8 w-8" />
            <span class="text-xs font-medium">No image</span>
          </div>

          <!-- Upload overlay on hover / dragging -->
          <div
            class="absolute inset-0 flex items-center justify-center transition-opacity"
            :class="[
              dragging[page.id] ? 'opacity-100 bg-brand-600/80' : 'opacity-0 group-hover:opacity-100 bg-black/40',
            ]"
          >
            <div v-if="!uploading[page.id]" class="flex flex-col items-center gap-1.5 text-white">
              <Upload class="h-7 w-7" />
              <span class="text-xs font-semibold">{{ dragging[page.id] ? 'Drop to upload' : page.image ? 'Replace image' : 'Upload image' }}</span>
            </div>
            <Loader2 v-else class="h-8 w-8 animate-spin text-white" />
          </div>

          <!-- Success flash -->
          <Transition name="fade">
            <div v-if="justDone[page.id]" class="absolute inset-0 flex items-center justify-center bg-emerald-500/90">
              <CheckCircle2 class="h-8 w-8 text-white" />
            </div>
          </Transition>
        </div>

        <!-- Card body -->
        <div class="flex flex-1 flex-col gap-2 p-3">

          <!-- Badges -->
          <div class="flex flex-wrap items-center gap-1.5">
            <span
              class="rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide"
              :class="siteColor(page.site)"
            >{{ page.siteName || page.site }}</span>
            <span
              class="rounded-full px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide"
              :class="page.type === 'blog' ? 'bg-blue-50 text-blue-700' : 'bg-purple-50 text-purple-700'"
            >{{ page.type === 'blog' ? 'Blog' : 'Service' }}</span>
          </div>

          <!-- Title -->
          <p class="line-clamp-2 text-xs font-semibold leading-snug text-slate-800">{{ page.title }}</p>

          <!-- Error -->
          <p v-if="uploadErr[page.id]" class="text-[11px] text-red-600">{{ uploadErr[page.id] }}</p>

          <!-- Actions -->
          <div class="mt-auto flex items-center gap-1.5 pt-1">
            <button
              class="flex flex-1 items-center justify-center gap-1 rounded-lg bg-brand-600 py-1.5 text-[11px] font-semibold text-white transition hover:bg-brand-700 disabled:opacity-50"
              :disabled="uploading[page.id]"
              @click="openPicker(page.id)"
            >
              <Upload v-if="!uploading[page.id]" class="h-3 w-3" />
              <Loader2 v-else class="h-3 w-3 animate-spin" />
              {{ page.image ? 'Replace' : 'Upload' }}
            </button>

            <button
              v-if="page.image"
              class="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-200 text-slate-400 transition hover:border-red-300 hover:text-red-500 disabled:opacity-40"
              :disabled="removing[page.id]"
              :title="removing[page.id] ? 'Removing…' : 'Remove image'"
              @click="removeImage(page.id)"
            >
              <Loader2 v-if="removing[page.id]" class="h-3 w-3 animate-spin" />
              <Trash2 v-else class="h-3 w-3" />
            </button>

            <a
              :href="page.editUrl"
              target="_blank"
              rel="noopener"
              class="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-200 text-slate-400 transition hover:border-brand-300 hover:text-brand-600"
              title="Edit in Wagtail"
            >
              <ExternalLink class="h-3 w-3" />
            </a>
          </div>
        </div>
      </div>

    </div>

  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.4s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import {
  BookOpen, ChevronRight, Download, RefreshCw, Search,
  HelpCircle, Settings, ShieldCheck, Users, CreditCard,
  FileText, LifeBuoy, MessageSquare,
} from "@lucide/vue";
import { api, apiPath } from "@/api/client";

const props = defineProps<{ role: string }>();
const router = useRouter();

interface GuideItem {
  id:                     number;
  slug:                   string;
  title:                  string;
  summary:                string;
  audience:               string;
  icon:                   string;
  is_featured:            boolean;
  estimated_read_minutes: number;
  published_at:           string | null;
  pdf:                    { title: string; url: string } | null;
}

const ICON_MAP: Record<string, unknown> = {
  "book-open":      BookOpen,
  "credit-card":    CreditCard,
  "file-text":      FileText,
  "help-circle":    HelpCircle,
  "life-buoy":      LifeBuoy,
  "message-square": MessageSquare,
  "settings":       Settings,
  "shield-check":   ShieldCheck,
  "users":          Users,
};
function icon(name: string) { return ICON_MAP[name] ?? HelpCircle; }

const isLoading = ref(true);
const guides    = ref<GuideItem[]>([]);
const query     = ref("");

const featured  = computed(() => guides.value.filter(g => g.is_featured));
const displayed = computed(() => {
  const q = query.value.trim().toLowerCase();
  const list = q
    ? guides.value.filter(g =>
        g.title.toLowerCase().includes(q) || g.summary.toLowerCase().includes(q))
    : guides.value;
  return list;
});

async function loadAll() {
  isLoading.value = true;
  try {
    const { data } = await api.get<{ items: GuideItem[] }>(
      apiPath("/cms-api/guides/"),
    );
    guides.value = data.items ?? [];
  } catch { guides.value = []; }
  finally { isLoading.value = false; }
}

function open(slug: string) {
  router.push({ name: `${props.role}-guide-article`, params: { slug } });
}

onMounted(loadAll);
</script>

<template>
  <div class="space-y-6">

    <!-- Header -->
    <div class="flex items-start justify-between gap-4">
      <div>
        <h1 class="text-xl font-semibold text-neutral-900">Guides &amp; Training</h1>
        <p class="mt-0.5 text-sm text-neutral-500">
          Onboarding docs, SOPs, and training materials — managed in Wagtail CMS.
        </p>
      </div>
      <button
        class="inline-flex items-center gap-1.5 rounded-lg border border-neutral-200 px-3 py-2 text-sm hover:bg-neutral-50"
        @click="loadAll"
      >
        <RefreshCw class="size-4" :class="isLoading ? 'animate-spin' : ''" />
        Refresh
      </button>
    </div>

    <!-- Loading skeleton -->
    <div v-if="isLoading" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 animate-pulse">
      <div v-for="n in 6" :key="n" class="rounded-xl border border-neutral-200 bg-white p-5">
        <div class="mb-3 size-9 rounded-full bg-neutral-200" />
        <div class="h-4 w-3/4 rounded bg-neutral-200" />
        <div class="mt-2 h-3 w-full rounded bg-neutral-100" />
      </div>
    </div>

    <template v-else>

      <!-- Featured -->
      <section v-if="featured.length && !query">
        <h2 class="mb-3 text-xs font-semibold uppercase tracking-wider text-neutral-400">
          Featured
        </h2>
        <div class="grid gap-3 sm:grid-cols-2">
          <button
            v-for="g in featured"
            :key="g.id"
            class="group flex items-start gap-4 rounded-xl border border-neutral-200 bg-white p-4 text-left hover:border-indigo-400 hover:shadow-sm transition-all"
            @click="open(g.slug)"
          >
            <div class="flex size-10 shrink-0 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 group-hover:bg-indigo-100">
              <component :is="icon(g.icon)" class="size-5" />
            </div>
            <div class="min-w-0 flex-1">
              <p class="font-semibold text-neutral-900 group-hover:text-indigo-600 truncate">{{ g.title }}</p>
              <p class="mt-0.5 text-xs text-neutral-500 line-clamp-2">{{ g.summary }}</p>
              <div class="mt-1.5 flex items-center gap-2">
                <span class="text-[11px] text-neutral-400">{{ g.estimated_read_minutes }} min read</span>
                <span v-if="g.pdf" class="inline-flex items-center gap-0.5 text-[11px] text-indigo-500">
                  <Download class="size-3" /> PDF
                </span>
              </div>
            </div>
            <ChevronRight class="mt-1 size-4 shrink-0 text-neutral-300 group-hover:text-indigo-400" />
          </button>
        </div>
      </section>

      <!-- Search + full list -->
      <div class="space-y-4">
        <div class="relative">
          <Search class="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-neutral-400" />
          <input
            v-model="query"
            type="search"
            placeholder="Search guides…"
            class="h-10 w-full rounded-lg border border-neutral-200 bg-white pl-9 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <!-- Empty state -->
        <div v-if="!displayed.length" class="flex flex-col items-center py-16 text-neutral-400">
          <BookOpen class="mb-3 size-10" />
          <p class="text-sm font-medium">
            {{ query ? 'No guides match your search.' : 'No guides available yet.' }}
          </p>
          <p v-if="!query" class="mt-1 text-xs">
            Staff can add guides in Wagtail CMS → Guides.
          </p>
        </div>

        <!-- Guide list -->
        <div v-else class="divide-y divide-neutral-100 rounded-xl border border-neutral-200 bg-white overflow-hidden">
          <button
            v-for="g in displayed"
            :key="g.id"
            class="group flex w-full items-center gap-4 px-4 py-4 text-left hover:bg-neutral-50 transition-colors"
            @click="open(g.slug)"
          >
            <div class="flex size-9 shrink-0 items-center justify-center rounded-lg bg-neutral-100 text-neutral-500 group-hover:bg-indigo-50 group-hover:text-indigo-600 transition-colors">
              <component :is="icon(g.icon)" class="size-4" />
            </div>
            <div class="min-w-0 flex-1">
              <p class="font-medium text-neutral-900 group-hover:text-indigo-600">{{ g.title }}</p>
              <p v-if="g.summary" class="mt-0.5 text-xs text-neutral-500 line-clamp-1">{{ g.summary }}</p>
              <div class="mt-1 flex items-center gap-2">
                <span class="text-[11px] text-neutral-400">{{ g.estimated_read_minutes }} min</span>
                <span v-if="g.pdf" class="inline-flex items-center gap-0.5 rounded-full bg-indigo-50 px-2 py-0.5 text-[11px] font-medium text-indigo-600">
                  <Download class="size-3" /> PDF
                </span>
              </div>
            </div>
            <ChevronRight class="size-4 shrink-0 text-neutral-300 group-hover:text-indigo-400" />
          </button>
        </div>
      </div>

    </template>
  </div>
</template>

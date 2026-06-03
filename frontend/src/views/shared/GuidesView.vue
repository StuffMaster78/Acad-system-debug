<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import {
  BookOpen, ChevronRight, HelpCircle, LifeBuoy,
  MessageSquare, RefreshCw, Search, Settings,
  ShieldCheck, Users, CreditCard, FileText,
} from "@lucide/vue";
import { legalApi, type HelpArticleSummary, type HelpCategory } from "@/api/legal";

defineProps<{ role: string }>();

const router = useRouter();

const isLoading     = ref(true);
const categories    = ref<HelpCategory[]>([]);
const articles      = ref<HelpArticleSummary[]>([]);
const activeCategory = ref<HelpCategory | null>(null);
const query         = ref("");

const ICON_MAP: Record<string, unknown> = {
  "book-open":     BookOpen,
  "credit-card":   CreditCard,
  "file-text":     FileText,
  "help-circle":   HelpCircle,
  "life-buoy":     LifeBuoy,
  "message-square": MessageSquare,
  "settings":      Settings,
  "shield-check":  ShieldCheck,
  "users":         Users,
};

function icon(name: string) {
  return ICON_MAP[name] ?? HelpCircle;
}

const featured = computed(() =>
  articles.value.filter((a) => a.is_featured),
);

const displayed = computed(() => {
  let list = activeCategory.value
    ? articles.value.filter((a) => a.category === activeCategory.value!.id)
    : articles.value;

  if (query.value.trim()) {
    const q = query.value.trim().toLowerCase();
    list = list.filter(
      (a) =>
        a.title.toLowerCase().includes(q) ||
        a.summary.toLowerCase().includes(q),
    );
  }
  return list;
});

async function loadAll() {
  isLoading.value = true;
  try {
    const [catRes, artRes] = await Promise.all([
      legalApi.categories(),
      legalApi.articles(),
    ]);
    categories.value = catRes.data;
    articles.value   = artRes.data;
  } catch { /* backend not seeded yet — show empty state */ }
  finally { isLoading.value = false; }
}

function openArticle(slug: string) {
  router.push({ name: "guide-article", params: { slug } });
}

onMounted(loadAll);
watch(activeCategory, () => { query.value = ""; });
</script>

<template>
  <div class="space-y-6">

    <!-- Header -->
    <div class="flex items-start justify-between gap-4">
      <div>
        <h1 class="text-xl font-semibold text-neutral-900">Guides &amp; Help</h1>
        <p class="mt-0.5 text-sm text-neutral-500">
          Step-by-step articles for getting the most out of the platform.
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

    <!-- Loading -->
    <div v-if="isLoading" class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 animate-pulse">
      <div v-for="n in 6" :key="n" class="rounded-xl border border-neutral-200 bg-white p-5">
        <div class="mb-3 size-9 rounded-full bg-neutral-200" />
        <div class="h-4 w-3/4 rounded bg-neutral-200" />
        <div class="mt-2 h-3 w-full rounded bg-neutral-100" />
      </div>
    </div>

    <template v-else>
      <!-- Featured -->
      <section v-if="!activeCategory && featured.length">
        <h2 class="mb-3 text-xs font-semibold uppercase tracking-wider text-neutral-400">
          Featured guides
        </h2>
        <div class="grid gap-3 sm:grid-cols-2">
          <button
            v-for="a in featured"
            :key="a.id"
            class="group flex items-start gap-4 rounded-xl border border-neutral-200 bg-white p-4 text-left hover:border-indigo-400 hover:shadow-sm transition-all"
            @click="openArticle(a.slug)"
          >
            <BookOpen class="mt-0.5 size-5 shrink-0 text-indigo-500" />
            <div class="min-w-0">
              <p class="font-semibold text-neutral-900 group-hover:text-indigo-600 truncate">{{ a.title }}</p>
              <p class="mt-0.5 text-xs text-neutral-500 line-clamp-2">{{ a.summary }}</p>
            </div>
            <ChevronRight class="mt-0.5 size-4 shrink-0 text-neutral-300 group-hover:text-indigo-400" />
          </button>
        </div>
      </section>

      <!-- Categories + article list -->
      <div class="flex gap-6">

        <!-- Category sidebar -->
        <aside v-if="categories.length" class="hidden w-56 shrink-0 md:block">
          <p class="mb-2 text-xs font-semibold uppercase tracking-wider text-neutral-400">Topics</p>
          <nav class="space-y-0.5">
            <button
              class="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors"
              :class="activeCategory === null
                ? 'bg-indigo-50 text-indigo-700'
                : 'text-neutral-600 hover:bg-neutral-100'"
              @click="activeCategory = null"
            >
              <BookOpen class="size-4 shrink-0" />
              All guides
              <span class="ml-auto text-xs text-neutral-400">{{ articles.length }}</span>
            </button>
            <button
              v-for="cat in categories"
              :key="cat.id"
              class="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm font-medium transition-colors"
              :class="activeCategory?.id === cat.id
                ? 'bg-indigo-50 text-indigo-700'
                : 'text-neutral-600 hover:bg-neutral-100'"
              @click="activeCategory = cat"
            >
              <component :is="icon(cat.icon)" class="size-4 shrink-0" />
              <span class="truncate">{{ cat.title }}</span>
              <span class="ml-auto text-xs text-neutral-400">{{ cat.article_count }}</span>
            </button>
          </nav>
        </aside>

        <!-- Article list -->
        <div class="min-w-0 flex-1 space-y-4">

          <!-- Search -->
          <div class="relative">
            <Search class="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-neutral-400" />
            <input
              v-model="query"
              type="search"
              placeholder="Search guides…"
              class="h-10 w-full rounded-lg border border-neutral-200 bg-white pl-9 pr-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <!-- Category heading -->
          <div v-if="activeCategory" class="flex items-center gap-2">
            <component :is="icon(activeCategory.icon)" class="size-5 text-indigo-500" />
            <h2 class="text-base font-semibold text-neutral-800">{{ activeCategory.title }}</h2>
            <span class="text-xs text-neutral-400">{{ displayed.length }} article{{ displayed.length !== 1 ? 's' : '' }}</span>
          </div>

          <!-- Empty -->
          <div
            v-if="!displayed.length"
            class="flex flex-col items-center py-16 text-neutral-400"
          >
            <BookOpen class="mb-3 size-10" />
            <p class="text-sm font-medium">
              {{ query ? 'No articles match your search.' : 'No guides available yet.' }}
            </p>
            <p class="mt-1 text-xs">
              {{ query ? '' : 'Check back soon — the team is adding content.' }}
            </p>
          </div>

          <!-- Articles -->
          <div v-else class="divide-y divide-neutral-100 rounded-xl border border-neutral-200 bg-white overflow-hidden">
            <button
              v-for="a in displayed"
              :key="a.id"
              class="group flex w-full items-start gap-4 px-4 py-4 text-left hover:bg-neutral-50 transition-colors"
              @click="openArticle(a.slug)"
            >
              <FileText class="mt-0.5 size-5 shrink-0 text-neutral-400 group-hover:text-indigo-500" />
              <div class="min-w-0 flex-1">
                <p class="font-medium text-neutral-900 group-hover:text-indigo-600">{{ a.title }}</p>
                <p v-if="a.summary" class="mt-0.5 text-xs text-neutral-500 line-clamp-2">{{ a.summary }}</p>
                <p class="mt-1 text-xs text-neutral-400">{{ a.category_title }}</p>
              </div>
              <ChevronRight class="mt-0.5 size-4 shrink-0 text-neutral-300 group-hover:text-indigo-400" />
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

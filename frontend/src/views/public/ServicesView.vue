<template>
  <div class="min-h-screen bg-slate-50">

    <!-- Hero -->
    <div class="bg-white border-b border-slate-200 px-6 py-16 text-center">
      <h1 class="text-4xl font-extrabold text-ink">{{ heroHeading }}</h1>
      <!-- eslint-disable-next-line vue/no-v-html -->
      <p v-if="heroIntroHtml" class="mt-3 max-w-2xl mx-auto text-lg text-graphite" v-html="heroIntroHtml" />
      <p v-else class="mt-3 max-w-2xl mx-auto text-lg text-graphite">{{ heroIntroText }}</p>
      <RouterLink
        to="/auth/register"
        class="mt-8 inline-flex items-center gap-2 rounded-xl bg-berry px-7 py-3.5 font-bold text-white shadow-lg hover:bg-rose-700 transition-colors"
      >
        Place an order <ArrowRight class="size-4" />
      </RouterLink>
    </div>

    <div class="mx-auto max-w-6xl px-6 py-12">

      <!-- Loading -->
      <div v-if="isLoading" class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 animate-pulse">
        <div v-for="n in 6" :key="n" class="rounded-xl border border-slate-200 bg-white p-6 space-y-3">
          <div class="h-4 w-3/4 rounded bg-slate-200" />
          <div class="h-3 w-full rounded bg-slate-100" />
          <div class="h-3 w-2/3 rounded bg-slate-100" />
        </div>
      </div>

      <template v-else>
        <!-- Category filters -->
        <div v-if="categories.length" class="mb-8 flex flex-wrap gap-2">
          <button
            class="rounded-full border px-4 py-1.5 text-sm font-medium transition-colors"
            :class="activeCategory === null
              ? 'border-berry bg-berry text-white'
              : 'border-slate-200 bg-white text-graphite hover:border-slate-300'"
            @click="activeCategory = null"
          >All</button>
          <button
            v-for="cat in categories"
            :key="cat"
            class="rounded-full border px-4 py-1.5 text-sm font-medium transition-colors"
            :class="activeCategory === cat
              ? 'border-berry bg-berry text-white'
              : 'border-slate-200 bg-white text-graphite hover:border-slate-300'"
            @click="activeCategory = cat"
          >{{ cat }}</button>
        </div>

        <!-- CMS service cards -->
        <div v-if="filteredServices.length" class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          <RouterLink
            v-for="svc in filteredServices"
            :key="svc.id"
            :to="`/services/${svc.meta.slug}`"
            class="group flex flex-col rounded-xl border border-slate-200 bg-white p-6 transition-all hover:border-berry/40 hover:shadow-md"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <span v-if="svc.service_category" class="mb-2 inline-flex rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold text-graphite">
                  {{ svc.service_category.name }}
                </span>
                <h2 class="text-base font-bold text-ink group-hover:text-berry transition-colors">{{ svc.title }}</h2>
              </div>
              <div v-if="svc.pricing_from" class="shrink-0 text-right">
                <p class="text-lg font-bold text-ink">from ${{ svc.pricing_from }}</p>
              </div>
            </div>
            <div class="mt-3 flex flex-wrap gap-3 text-xs text-graphite">
              <span v-if="svc.turnaround_hours_fastest" class="flex items-center gap-1">
                <Clock class="size-3.5" /> From {{ formatTurnaround(svc.turnaround_hours_fastest) }}
              </span>
            </div>
            <p class="mt-auto pt-4 text-xs font-semibold text-berry group-hover:underline">Learn more →</p>
          </RouterLink>
        </div>

        <!-- Static fallback when CMS has no published pages yet -->
        <div v-else class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          <div v-for="svc in STATIC_SERVICES" :key="svc.title" class="rounded-xl border border-slate-200 bg-white p-6">
            <span class="mb-2 inline-flex rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold text-graphite">{{ svc.category }}</span>
            <h2 class="text-base font-bold text-ink">{{ svc.title }}</h2>
            <p class="mt-2 text-sm leading-6 text-graphite">{{ svc.description }}</p>
            <p class="mt-3 text-xs text-graphite">{{ svc.turnaround }} · from {{ svc.from }}</p>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { RouterLink } from "vue-router";
import { ArrowRight, Clock } from "@lucide/vue";
import { cmsApi, type ServicePageSummary } from "@/api/cms";
import { useMeta, webPageSchema } from "@/composables/useMeta";
import { usePortalContextStore } from "@/stores/portalContext";

const portalCtx = usePortalContextStore();

// ── Hero content — CMS → branding → static fallback ─────────────────────
const FALLBACK_HEADING = "Academic writing services";
const FALLBACK_INTRO   = "Expert writing assistance across every subject, academic level, and deadline.";

const cmsHeading  = ref<string | null>(null);
const cmsIntro    = ref<string | null>(null); // raw RichTextField HTML from Wagtail

const heroHeading = computed(
  () => cmsHeading.value
    ?? (portalCtx.branding?.brand_name ? `${portalCtx.branding.brand_name} writing services` : null)
    ?? FALLBACK_HEADING,
);

// If CMS returned rich-text HTML use it; otherwise fall back to plain text.
const heroIntroHtml = computed(() => cmsIntro.value ?? null);
const heroIntroText = computed(() => portalCtx.branding?.tagline || FALLBACK_INTRO);

// ── Meta — static fallback on setup, reactive title update after CMS load ─
useMeta({
  title: FALLBACK_HEADING,
  description: FALLBACK_INTRO,
  schema: webPageSchema({ title: "Services", url: window.location.href }),
});

watch(heroHeading, (title) => {
  const siteName = portalCtx.branding?.brand_name ?? "WritingSystem";
  document.title = `${title} — ${siteName}`;
});

// ── Service listing ───────────────────────────────────────────────────────
const isLoading = ref(true);
const services = ref<ServicePageSummary[]>([]);
const activeCategory = ref<string | null>(null);

const categories = computed(() => {
  const cats = new Set(
    services.value.map((s) => s.service_category?.name).filter(Boolean) as string[],
  );
  return [...cats].sort();
});

const filteredServices = computed(() =>
  activeCategory.value
    ? services.value.filter((s) => s.service_category?.name === activeCategory.value)
    : services.value,
);

function formatTurnaround(hours: number): string {
  if (hours < 24) return `${hours}h`;
  const days = Math.floor(hours / 24);
  return `${days} day${days !== 1 ? "s" : ""}`;
}

onMounted(async () => {
  const [indexRes, pagesRes] = await Promise.allSettled([
    cmsApi.serviceIndexPage(),
    cmsApi.servicePages(),
  ]);

  if (indexRes.status === "fulfilled") {
    const page = indexRes.value.data.items?.[0];
    if (page) {
      cmsHeading.value = page.title || null;
      cmsIntro.value   = page.intro?.trim() || null;
    }
  }

  if (pagesRes.status === "fulfilled") {
    services.value = pagesRes.value.data.items;
  }

  isLoading.value = false;
});

const STATIC_SERVICES = [
  { title: "Essays", category: "Academic writing", description: "Argumentative, descriptive, compare-and-contrast, reflective, and narrative essays across all academic levels.", turnaround: "From 3 hours", from: "$12" },
  { title: "Research papers", category: "Academic writing", description: "Primary and secondary research papers with proper sourcing, citations, and literature synthesis.", turnaround: "From 6 hours", from: "$15" },
  { title: "Case studies", category: "Academic writing", description: "In-depth analysis of real-world scenarios applied to business, law, medicine, and social sciences.", turnaround: "From 6 hours", from: "$14" },
  { title: "Dissertations", category: "Graduate work", description: "Full dissertations from proposal through final chapter with methodology and literature review support.", turnaround: "From 7 days", from: "$22" },
  { title: "Lab reports", category: "STEM", description: "Scientific lab reports following APA, IEEE, or custom institutional formats.", turnaround: "From 6 hours", from: "$13" },
  { title: "Editing & proofreading", category: "Editing", description: "Grammar, clarity, structure, and citation review by academic editors.", turnaround: "From 3 hours", from: "$8" },
];
</script>

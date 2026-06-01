<template>
  <div class="min-h-screen bg-white">
    <div class="mx-auto max-w-3xl px-6 py-16">

      <!-- Breadcrumb -->
      <nav class="mb-8 flex items-center gap-2 text-sm text-graphite">
        <RouterLink to="/help" class="hover:text-ink">Help Center</RouterLink>
        <span>/</span>
        <RouterLink
          v-if="article?.category_slug"
          :to="`/help/category/${article.category_slug}`"
          class="hover:text-ink"
        >
          {{ article.category_title }}
        </RouterLink>
        <template v-if="article?.category_slug"><span>/</span></template>
        <span class="text-ink truncate max-w-xs">{{ article?.title ?? "Article" }}</span>
      </nav>

      <!-- Loading -->
      <div v-if="isLoading" class="animate-pulse space-y-4">
        <div class="h-8 w-2/3 rounded bg-slate-200" />
        <div class="h-3 w-40 rounded bg-slate-100" />
        <div class="mt-8 space-y-3">
          <div v-for="n in 8" :key="n" class="h-3 rounded bg-slate-100" :style="{ width: n % 3 === 0 ? '75%' : '100%' }" />
        </div>
      </div>

      <!-- Not found -->
      <div v-else-if="notFound" class="py-20 text-center">
        <FileX class="mx-auto mb-4 size-10 text-slate-300" />
        <p class="font-semibold text-ink">Article not found</p>
        <RouterLink to="/help" class="mt-4 inline-flex items-center gap-1.5 text-sm text-berry hover:underline">
          <ArrowLeft class="size-3.5" /> Back to Help Center
        </RouterLink>
      </div>

      <!-- Article -->
      <template v-else-if="article">
        <header class="mb-10 border-b border-slate-100 pb-8">
          <h1 class="text-3xl font-bold text-ink">{{ article.title }}</h1>
          <p v-if="article.summary" class="mt-3 text-lg text-graphite">{{ article.summary }}</p>
          <p class="mt-3 text-xs text-slate-400">
            Last updated {{ fmtDate(article.updated_at) }}
          </p>
        </header>

        <div class="prose prose-slate max-w-none" v-html="article.content" />

        <div class="mt-12 rounded-xl border border-slate-200 bg-slate-50 p-6 text-center">
          <p class="text-sm font-semibold text-ink">Was this article helpful?</p>
          <p class="mt-1 text-sm text-graphite">
            Still have questions?
            <RouterLink to="/help" class="text-berry hover:underline">Browse more guides</RouterLink>
            or contact our support team via the messages section.
          </p>
        </div>
      </template>

    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { useRoute, RouterLink } from "vue-router";
import { ArrowLeft, FileX } from "@lucide/vue";
import { legalApi, type HelpArticle } from "@/api/legal";

const route = useRoute();
const isLoading = ref(true);
const notFound = ref(false);
const article = ref<HelpArticle | null>(null);

async function load() {
  const slug = route.params.slug as string;
  isLoading.value = true;
  notFound.value = false;
  article.value = null;
  try {
    const { data } = await legalApi.article(slug);
    article.value = data;
  } catch {
    notFound.value = true;
  } finally {
    isLoading.value = false;
  }
}

function fmtDate(v: string) {
  return new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(v));
}

onMounted(load);
watch(() => route.params.slug, load);
</script>

<style scoped>
:deep(.prose h2) { @apply mt-10 text-xl font-semibold text-ink; }
:deep(.prose h3) { @apply mt-8 text-base font-semibold text-ink; }
:deep(.prose p) { @apply leading-7 text-graphite; }
:deep(.prose ul, .prose ol) { @apply my-4 space-y-1 text-graphite; }
:deep(.prose li::marker) { @apply text-berry; }
:deep(.prose a) { @apply text-berry hover:underline; }
:deep(.prose strong) { @apply font-semibold text-ink; }
:deep(.prose code) { @apply rounded bg-slate-100 px-1 py-0.5 font-mono text-sm text-berry; }
:deep(.prose blockquote) { @apply border-l-4 border-slate-200 pl-4 italic text-graphite; }
</style>

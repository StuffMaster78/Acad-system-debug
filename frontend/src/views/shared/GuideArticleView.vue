<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ArrowLeft, FileX, RefreshCw } from "@lucide/vue";
import { legalApi, type HelpArticle } from "@/api/legal";

const props = defineProps<{ role: string }>();

const route  = useRoute();
const router = useRouter();

const isLoading = ref(true);
const notFound  = ref(false);
const article   = ref<HelpArticle | null>(null);

async function load() {
  const slug = route.params.slug as string;
  isLoading.value = true;
  notFound.value  = false;
  article.value   = null;
  try {
    const { data } = await legalApi.article(slug);
    article.value  = data;
  } catch {
    notFound.value = true;
  } finally {
    isLoading.value = false;
  }
}

function back() {
  if (window.history.length > 1) router.back();
  else router.push({ name: `${props.role}-guides` });
}

function fmtDate(v: string) {
  return new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(v));
}

onMounted(load);
watch(() => route.params.slug, load);
</script>

<template>
  <div class="mx-auto max-w-3xl space-y-6">

    <!-- Back -->
    <button
      class="inline-flex items-center gap-1.5 text-sm text-neutral-500 hover:text-neutral-800 transition-colors"
      @click="back"
    >
      <ArrowLeft class="size-4" /> Back to Guides
    </button>

    <!-- Loading -->
    <div v-if="isLoading" class="animate-pulse space-y-4 rounded-xl border border-neutral-200 bg-white p-8">
      <div class="h-7 w-2/3 rounded bg-neutral-200" />
      <div class="h-3 w-40 rounded bg-neutral-100" />
      <div class="mt-6 space-y-3">
        <div v-for="n in 8" :key="n" class="h-3 rounded bg-neutral-100" :style="{ width: n % 3 === 0 ? '70%' : '100%' }" />
      </div>
    </div>

    <!-- Not found -->
    <div v-else-if="notFound" class="flex flex-col items-center py-20 text-neutral-400">
      <FileX class="mb-4 size-12" />
      <p class="font-semibold text-neutral-700">Article not found</p>
      <p class="mt-1 text-sm">This guide may have been moved or removed.</p>
      <button
        class="mt-4 inline-flex items-center gap-1.5 text-sm text-indigo-600 hover:underline"
        @click="back"
      >
        <ArrowLeft class="size-3.5" /> Back to guides
      </button>
    </div>

    <!-- Article -->
    <template v-else-if="article">
      <div class="rounded-xl border border-neutral-200 bg-white overflow-hidden">

        <!-- Header -->
        <div class="border-b border-neutral-100 px-8 py-7">
          <div v-if="article.category_title" class="mb-2 text-xs font-semibold uppercase tracking-wider text-indigo-500">
            {{ article.category_title }}
          </div>
          <h1 class="text-2xl font-bold text-neutral-900">{{ article.title }}</h1>
          <p v-if="article.summary" class="mt-2 text-base text-neutral-500">{{ article.summary }}</p>
          <p class="mt-3 text-xs text-neutral-400">
            Last updated {{ fmtDate(article.updated_at) }}
          </p>
        </div>

        <!-- Body -->
        <div class="guide-body px-8 py-7" v-html="article.content" />

        <!-- Footer CTA -->
        <div class="border-t border-neutral-100 bg-neutral-50 px-8 py-5 text-center">
          <p class="text-sm font-medium text-neutral-700">Was this helpful?</p>
          <p class="mt-1 text-sm text-neutral-500">
            Still have questions? Open a support ticket from the
            <strong>Support</strong> section in your dashboard.
          </p>
        </div>
      </div>
    </template>

  </div>
</template>

<style scoped>
.guide-body :deep(h2) { @apply mt-8 text-lg font-semibold text-neutral-900; }
.guide-body :deep(h3) { @apply mt-6 text-base font-semibold text-neutral-800; }
.guide-body :deep(p)  { @apply mt-4 leading-7 text-neutral-600; }
.guide-body :deep(ul),
.guide-body :deep(ol) { @apply mt-4 space-y-1.5 pl-5 text-neutral-600; }
.guide-body :deep(li) { @apply list-disc; }
.guide-body :deep(ol li) { @apply list-decimal; }
.guide-body :deep(a)  { @apply text-indigo-600 hover:underline; }
.guide-body :deep(strong) { @apply font-semibold text-neutral-800; }
.guide-body :deep(blockquote) { @apply my-4 border-l-4 border-neutral-200 pl-4 italic text-neutral-500; }
.guide-body :deep(code) { @apply rounded bg-neutral-100 px-1.5 py-0.5 font-mono text-sm text-indigo-600; }
.guide-body :deep(pre) { @apply my-4 overflow-x-auto rounded-lg bg-neutral-900 p-4 font-mono text-sm text-neutral-100; }
.guide-body :deep(hr)  { @apply my-6 border-neutral-200; }
.guide-body :deep(table) { @apply my-4 w-full text-sm; }
.guide-body :deep(th)  { @apply border border-neutral-200 bg-neutral-50 px-3 py-2 text-left font-semibold text-neutral-700; }
.guide-body :deep(td)  { @apply border border-neutral-200 px-3 py-2 text-neutral-600; }
</style>

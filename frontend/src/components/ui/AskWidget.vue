<template>
  <div class="rounded-2xl border border-indigo-100 bg-gradient-to-br from-indigo-50 to-white p-5">
    <div class="flex items-center gap-2 mb-3">
      <span class="flex size-7 items-center justify-center rounded-full bg-indigo-600 text-white text-xs font-bold">AI</span>
      <p class="text-sm font-semibold text-indigo-900">Ask a question about this topic</p>
    </div>

    <form @submit.prevent="search" class="flex gap-2">
      <input
        v-model="query"
        type="text"
        :placeholder="placeholder"
        maxlength="200"
        class="flex-1 rounded-xl border border-indigo-200 bg-white px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
      />
      <button
        type="submit"
        :disabled="loading || query.trim().length < 3"
        class="flex items-center gap-1.5 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-40 transition-colors"
      >
        <Loader2 v-if="loading" class="size-4 animate-spin" />
        <Search v-else class="size-4" />
        Ask
      </button>
    </form>

    <!-- Results -->
    <div v-if="results.length" class="mt-4 space-y-2">
      <p class="text-xs font-semibold uppercase tracking-wide text-gray-400">Top answers from our content</p>
      <a
        v-for="r in results"
        :key="r.url"
        :href="r.url"
        class="group flex items-start gap-3 rounded-xl border border-gray-100 bg-white p-3 hover:border-indigo-200 hover:shadow-sm transition-all"
      >
        <FileText class="mt-0.5 size-4 shrink-0 text-indigo-400 group-hover:text-indigo-600" />
        <div class="min-w-0">
          <p class="text-sm font-semibold text-gray-900 group-hover:text-indigo-700 line-clamp-1">{{ r.title }}</p>
          <p v-if="r.excerpt" class="text-xs text-gray-500 mt-0.5 line-clamp-2">{{ r.excerpt }}</p>
        </div>
        <ChevronRight class="mt-0.5 size-4 shrink-0 text-gray-300 group-hover:text-indigo-400" />
      </a>
    </div>

    <!-- Zero results -->
    <div v-else-if="searched && !loading" class="mt-4 flex items-start gap-2 rounded-xl bg-amber-50 border border-amber-100 px-3 py-2.5 text-sm text-amber-800">
      <AlertCircle class="mt-0.5 size-4 shrink-0" />
      <span>No articles found for <strong>"{{ lastQuery }}"</strong>. Try different keywords or <a href="/blog" class="underline hover:text-amber-900">browse all articles</a>.</span>
    </div>

    <p class="mt-3 text-xs text-gray-400">Searches our own content — no external AI required.</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { AlertCircle, ChevronRight, FileText, Loader2, Search } from "@lucide/vue";
import { api, apiPath } from "@/api/client";

interface SearchResult {
  title: string;
  url: string;
  excerpt: string;
  type: string;
}

withDefaults(defineProps<{ placeholder?: string }>(), {
  placeholder: "e.g. How do I cite a journal article in APA?",
});

const query     = ref("");
const lastQuery = ref("");
const loading   = ref(false);
const searched  = ref(false);
const results   = ref<SearchResult[]>([]);

async function search() {
  const q = query.value.trim();
  if (q.length < 3) return;
  loading.value  = true;
  searched.value = false;
  lastQuery.value = q;
  try {
    const { data } = await api.get<{ results: SearchResult[] }>(
      apiPath(`/cms/intelligence/answers/?q=${encodeURIComponent(q)}`),
    );
    results.value  = data.results ?? [];
    searched.value = true;
  } catch {
    results.value  = [];
    searched.value = true;
  } finally {
    loading.value = false;
  }
}
</script>

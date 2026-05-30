<template>
  <div class="min-h-screen bg-white">
    <div class="mx-auto max-w-3xl px-6 py-16">

      <!-- Back -->
      <RouterLink to="/help" class="mb-8 inline-flex items-center gap-1.5 text-sm text-graphite hover:text-ink">
        <ArrowLeft class="size-3.5" /> Help & Legal
      </RouterLink>

      <!-- Loading -->
      <div v-if="isLoading" class="space-y-4 animate-pulse">
        <div class="h-8 w-2/3 rounded bg-slate-200" />
        <div class="h-4 w-1/3 rounded bg-slate-100" />
        <div class="mt-8 space-y-3">
          <div v-for="n in 6" :key="n" class="h-3 rounded bg-slate-100" :style="{ width: n % 2 ? '100%' : '80%' }" />
        </div>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="rounded-lg border border-rose-200 bg-rose-50 p-8 text-center">
        <FileX class="mx-auto mb-3 size-8 text-rose-300" />
        <p class="font-semibold text-ink">{{ error }}</p>
        <p class="mt-1 text-sm text-graphite">Check back soon or contact support.</p>
      </div>

      <!-- Document -->
      <template v-else-if="doc">
        <header class="mb-10 border-b border-slate-100 pb-8">
          <h1 class="text-3xl font-bold text-ink">{{ doc.title }}</h1>
          <p class="mt-2 text-sm text-graphite">
            Version {{ doc.version }} · Effective {{ fmtDate(doc.effective_date) }}
          </p>
        </header>

        <!-- Rendered HTML content -->
        <div
          class="prose prose-slate max-w-none"
          v-html="doc.content"
        />

        <div class="mt-12 border-t border-slate-100 pt-8 text-xs text-graphite">
          If you have questions about this document, please
          <RouterLink to="/help" class="text-berry hover:underline">contact our support team</RouterLink>.
        </div>
      </template>

    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { useRoute, RouterLink } from "vue-router";
import { ArrowLeft, FileX } from "@lucide/vue";
import { legalApi, type DocType, type LegalDocument } from "@/api/legal";

const route = useRoute();
const isLoading = ref(true);
const error = ref("");
const doc = ref<LegalDocument | null>(null);

async function load() {
  const docType = route.params.docType as DocType;
  isLoading.value = true;
  error.value = "";
  doc.value = null;
  try {
    const { data } = await legalApi.document(docType);
    doc.value = data;
  } catch {
    error.value = "This document is not available yet.";
  } finally {
    isLoading.value = false;
  }
}

function fmtDate(v: string) {
  return new Intl.DateTimeFormat("en", { dateStyle: "long" }).format(new Date(v));
}

onMounted(load);
watch(() => route.params.docType, load);
</script>

<style scoped>
/* Override prose for legal document formatting */
:deep(.prose h2) {
  @apply mt-10 text-xl font-semibold text-ink;
}
:deep(.prose h3) {
  @apply mt-8 text-base font-semibold text-ink;
}
:deep(.prose p) {
  @apply leading-7 text-graphite;
}
:deep(.prose ul, .prose ol) {
  @apply my-4 space-y-1 text-graphite;
}
:deep(.prose a) {
  @apply text-berry hover:underline;
}
:deep(.prose strong) {
  @apply font-semibold text-ink;
}
</style>

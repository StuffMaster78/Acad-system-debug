<template>
  <div class="min-h-screen bg-white">

    <div v-if="isLoading" class="mx-auto max-w-4xl px-6 py-20 animate-pulse space-y-8">
      <div class="h-10 w-2/3 rounded bg-slate-200" />
      <div class="h-64 rounded-xl bg-slate-200" />
    </div>

    <div v-else-if="notFound" class="py-32 text-center">
      <p class="font-semibold text-ink">Page not found.</p>
      <RouterLink to="/" class="mt-4 inline-flex items-center gap-1.5 text-sm text-berry hover:underline">
        <ArrowLeft class="size-3.5" /> Home
      </RouterLink>
    </div>

    <template v-else-if="lp">
      <!-- Render JSON blocks through BlockRenderer -->
      <div class="mx-auto max-w-5xl px-6 py-10">
        <BlockRenderer :blocks="normalizedBlocks" />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { RouterLink, useRoute } from "vue-router";
import { ArrowLeft } from "@lucide/vue";
import { cmsApi, type SeoLandingPage, type WagtailBlock } from "@/api/cms";
import { useMeta, webPageSchema } from "@/composables/useMeta";
import BlockRenderer from "@/components/cms/BlockRenderer.vue";

const route = useRoute();
const isLoading = ref(true);
const notFound = ref(false);
const lp = ref<SeoLandingPage | null>(null);

// SEO landing pages store blocks as plain dicts; cast to WagtailBlock shape
const normalizedBlocks = computed((): WagtailBlock[] =>
  (lp.value?.blocks ?? []).map((b) => ({
    type: String((b as Record<string, unknown>).type ?? "paragraph"),
    value: (b as Record<string, unknown>).value ?? b,
    id: String((b as Record<string, unknown>).id ?? ""),
  })),
);

async function load() {
  const slug = route.params.slug as string;
  isLoading.value = true;
  notFound.value = false;
  lp.value = null;

  try {
    const { data } = await cmsApi.landingPage(slug);
    if (!data.is_published) { notFound.value = true; return; }
    lp.value = data;

    useMeta({
      title: lp.value.meta_title ?? lp.value.title,
      description: lp.value.meta_description ?? "",
      url: window.location.href,
      schema: webPageSchema({
        title: lp.value.meta_title ?? lp.value.title,
        description: lp.value.meta_description,
        url: window.location.href,
      }),
    });
  } catch {
    notFound.value = true;
  } finally {
    isLoading.value = false;
  }
}

onMounted(load);
watch(() => route.params.slug, load);
</script>

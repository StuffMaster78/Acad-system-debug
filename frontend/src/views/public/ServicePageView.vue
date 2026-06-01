<template>
  <div class="min-h-screen bg-white">

    <div v-if="isLoading" class="mx-auto max-w-4xl px-6 py-16 animate-pulse space-y-8">
      <div class="h-10 w-2/3 rounded bg-slate-200" />
      <div class="h-4 w-1/3 rounded bg-slate-100" />
      <div class="h-72 rounded-xl bg-slate-200" />
    </div>

    <div v-else-if="notFound" class="py-32 text-center">
      <p class="font-semibold text-ink">Service page not found.</p>
      <RouterLink to="/services" class="mt-4 inline-flex items-center gap-1.5 text-sm text-berry hover:underline">
        <ArrowLeft class="size-3.5" /> All services
      </RouterLink>
    </div>

    <template v-else-if="page">
      <!-- StreamField renders the full page body (Hero block first if exists) -->
      <BlockRenderer :blocks="page.body ?? []" />

      <!-- Pricing summary bar -->
      <div v-if="page.pricing_from" class="sticky bottom-0 border-t border-slate-200 bg-white/95 backdrop-blur-sm">
        <div class="mx-auto flex max-w-5xl items-center justify-between gap-6 px-6 py-4">
          <div class="flex flex-wrap gap-6 text-sm text-graphite">
            <span><span class="font-semibold text-ink">From ${{ page.pricing_from }}</span> per page</span>
            <span v-if="page.turnaround_hours_fastest">
              <Clock class="inline size-3.5" /> Deadline from {{ formatTurnaround(page.turnaround_hours_fastest) }}
            </span>
          </div>
          <RouterLink
            :to="page.primary_cta_url ?? '/auth/register'"
            class="inline-flex items-center gap-2 rounded-xl bg-berry px-6 py-2.5 font-bold text-white shadow hover:bg-rose-700"
          >
            {{ page.primary_cta_text ?? 'Order now' }}
            <ArrowRight class="size-4" />
          </RouterLink>
        </div>
      </div>

      <!-- Reviewer / expert card -->
      <div v-if="page.reviewer" class="border-t border-slate-100 bg-slate-50">
        <div class="mx-auto max-w-3xl px-6 py-8">
          <p class="mb-4 text-xs font-semibold uppercase tracking-wider text-graphite">Reviewed by</p>
          <div class="flex items-start gap-4">
            <img
              v-if="page.reviewer.profile_photo?.meta?.download_url"
              :src="page.reviewer.profile_photo.meta.download_url"
              :alt="page.reviewer.name"
              class="size-12 rounded-full object-cover"
            />
            <div>
              <p class="font-semibold text-ink">{{ page.reviewer.name }}</p>
              <p v-if="page.reviewer.credentials" class="text-xs text-graphite">{{ page.reviewer.credentials }}</p>
              <p v-if="page.reviewer.bio" class="mt-1 text-sm text-graphite">{{ page.reviewer.bio }}</p>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { RouterLink, useRoute } from "vue-router";
import { ArrowLeft, ArrowRight, Clock } from "@lucide/vue";
import { cmsApi, type ServicePage } from "@/api/cms";
import { useMeta, serviceSchema } from "@/composables/useMeta";
import BlockRenderer from "@/components/cms/BlockRenderer.vue";

const route = useRoute();
const isLoading = ref(true);
const notFound = ref(false);
const page = ref<ServicePage | null>(null);

function formatTurnaround(hours: number): string {
  if (hours < 24) return `${hours}h`;
  return `${Math.floor(hours / 24)} days`;
}

async function load() {
  const slug = route.params.slug as string;
  isLoading.value = true;
  notFound.value = false;
  page.value = null;

  try {
    const { data } = await cmsApi.servicePage(slug);
    if (!data.items.length) { notFound.value = true; return; }
    page.value = data.items[0];

    useMeta({
      title: page.value.title,
      description: `${page.value.title} — from $${page.value.pricing_from ?? "12"} per page. ${page.value.turnaround_hours_fastest ? `Delivery from ${formatTurnaround(page.value.turnaround_hours_fastest)}.` : ""}`,
      url: window.location.href,
      schema: serviceSchema({
        name: page.value.title,
        url: window.location.href,
        pricingFrom: page.value.pricing_from ?? undefined,
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

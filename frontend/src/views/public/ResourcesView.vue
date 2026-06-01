<template>
  <div class="min-h-screen bg-slate-50">
    <div class="bg-white border-b border-slate-200 px-6 py-14">
      <div class="mx-auto max-w-4xl">
        <p class="mb-2 text-xs font-semibold uppercase tracking-wider text-berry">Free downloads</p>
        <h1 class="text-4xl font-extrabold text-ink">Templates, samples & guides</h1>
        <p class="mt-3 max-w-2xl text-lg text-graphite">
          Academic templates, sample papers, formatting guides, and research tools — free or gated for verified students.
        </p>
      </div>
    </div>

    <div class="mx-auto max-w-5xl px-6 py-12">

      <!-- Filters -->
      <div class="mb-8 flex flex-wrap gap-2">
        <button
          v-for="f in FILTERS"
          :key="f.value ?? 'all'"
          class="rounded-full border px-4 py-1.5 text-sm font-medium transition-colors"
          :class="activeFilter === f.value
            ? 'border-berry bg-berry text-white'
            : 'border-slate-200 bg-white text-graphite hover:border-slate-300'"
          @click="activeFilter = f.value"
        >{{ f.label }}</button>
      </div>

      <!-- Loading -->
      <div v-if="isLoading" class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 animate-pulse">
        <div v-for="n in 6" :key="n" class="rounded-xl border border-slate-200 bg-white p-5 space-y-3">
          <div class="h-4 w-3/4 rounded bg-slate-200" />
          <div class="h-3 w-full rounded bg-slate-100" />
          <div class="h-8 w-1/2 rounded-full bg-slate-100 mt-4" />
        </div>
      </div>

      <div v-else-if="!resources.length" class="py-20 text-center">
        <FileDown class="mx-auto mb-4 size-10 text-slate-300" />
        <p class="text-sm text-graphite">No resources available yet.</p>
      </div>

      <div v-else class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        <RouterLink
          v-for="r in resources"
          :key="r.id"
          :to="`/resources/${r.slug}`"
          class="group flex flex-col rounded-xl border border-slate-200 bg-white p-5 transition-all hover:border-berry/40 hover:shadow-md"
        >
          <!-- Type + gate badges -->
          <div class="mb-3 flex flex-wrap gap-1.5">
            <span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold text-graphite capitalize">
              {{ r.attachment_type.replace(/_/g, " ") }}
            </span>
            <span
              class="rounded-full px-2 py-0.5 text-xs font-semibold"
              :class="gateBadgeClass(r.gate_type)"
            >{{ gateLabel(r.gate_type) }}</span>
          </div>

          <h2 class="flex-1 font-bold text-ink group-hover:text-berry transition-colors leading-snug">{{ r.title }}</h2>
          <p v-if="r.description" class="mt-2 line-clamp-2 text-xs text-graphite">{{ r.description }}</p>

          <div class="mt-4 flex flex-wrap items-center gap-3 text-xs text-graphite">
            <span v-if="r.page_count">{{ r.page_count }} pages</span>
            <span v-if="r.file_format" class="uppercase">{{ r.file_format }}</span>
            <span v-if="r.academic_level">{{ r.academic_level }}</span>
            <span v-if="r.average_rating" class="ml-auto flex items-center gap-1 text-saffron">
               {{ r.average_rating.toFixed(1) }}
              <span class="text-graphite">({{ r.rating_count }})</span>
            </span>
          </div>
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { RouterLink } from "vue-router";
import { FileDown } from "@lucide/vue";
import { cmsApi, type AttachmentSummary } from "@/api/cms";
import { useMeta, webPageSchema } from "@/composables/useMeta";

useMeta({
  title: "Free Downloads — Templates, Samples & Guides",
  description: "Academic templates, sample papers, and formatting guides. Free or email-gated.",
  schema: webPageSchema({ title: "Resources", url: window.location.href }),
});

const FILTERS = [
  { label: "All", value: null as string | null },
  { label: "Templates", value: "template" },
  { label: "Sample essays", value: "sample_essay" },
  { label: "Guides", value: "guide" },
  { label: "Outlines", value: "outline" },
];

const isLoading = ref(true);
const resources = ref<AttachmentSummary[]>([]);
const activeFilter = ref<string | null>(null);

async function load() {
  isLoading.value = true;
  try {
    const { data } = await cmsApi.attachments(
      activeFilter.value ? { type: activeFilter.value } : undefined,
    );
    resources.value = Array.isArray(data) ? data : (data as { results: AttachmentSummary[] }).results ?? [];
  } catch { resources.value = []; }
  finally { isLoading.value = false; }
}

function gateBadgeClass(gate: string): string {
  if (gate === "free") return "bg-emerald-100 text-emerald-700";
  if (gate === "email") return "bg-amber-100 text-amber-700";
  if (gate === "account") return "bg-blue-100 text-blue-700";
  return "bg-rose-100 text-rose-700";
}

function gateLabel(gate: string): string {
  if (gate === "free") return "Free";
  if (gate === "email") return "Email required";
  if (gate === "account") return "Sign in";
  if (gate === "customer") return "Customers only";
  return `Paid`;
}

onMounted(load);
watch(activeFilter, load);
</script>

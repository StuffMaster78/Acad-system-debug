<template>
  <div class="min-h-screen bg-slate-50">

    <!-- Hero -->
    <div class="border-b border-slate-200 bg-white px-6 py-16">
      <div class="mx-auto max-w-4xl">
        <p class="mb-2 text-xs font-semibold uppercase tracking-wider text-brand-700">Our editorial team</p>
        <h1 class="text-4xl font-extrabold text-ink">Meet the authors</h1>
        <p class="mt-3 max-w-2xl text-lg text-graphite">
          Credentialed writers, editors, and subject-matter experts behind every article.
        </p>
        <div class="mt-5 inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-4 py-1.5 text-sm font-semibold text-emerald-700">
          <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
          </svg>
          All content written by humans — zero AI
        </div>
      </div>
    </div>

    <div class="mx-auto max-w-5xl px-6 py-12">

      <!-- Loading skeleton -->
      <div v-if="isLoading" class="grid gap-6 sm:grid-cols-2 lg:grid-cols-2 animate-pulse">
        <div v-for="n in 4" :key="n" class="flex gap-4 rounded-2xl border border-slate-200 bg-white p-6">
          <div class="h-16 w-16 shrink-0 rounded-2xl bg-slate-200" />
          <div class="flex-1 space-y-2 pt-1">
            <div class="h-4 w-1/2 rounded bg-slate-200" />
            <div class="h-3 w-2/3 rounded bg-slate-100" />
            <div class="h-3 w-full rounded bg-slate-100" />
          </div>
        </div>
      </div>

      <!-- Empty state — only shown when API returns no authors -->
      <div v-else-if="!authors.length" class="py-24 text-center">
        <Users class="mx-auto mb-4 size-10 text-slate-300" />
        <p class="font-semibold text-ink">No authors published yet.</p>
        <p class="mt-1 text-sm text-graphite">Author profiles are published via the Wagtail admin under Snippets → Authors.</p>
      </div>

      <!-- Author grid -->
      <div v-else class="grid gap-6 sm:grid-cols-2">
        <RouterLink
          v-for="author in authors"
          :key="author.id"
          :to="`/authors/${author.slug}`"
          class="group flex gap-5 rounded-2xl border border-slate-200 bg-white p-6 transition-all hover:border-brand-200 hover:shadow-md"
        >
          <!-- Avatar -->
          <div class="relative shrink-0">
            <img
              v-if="author.profile_photo?.meta?.download_url"
              :src="author.profile_photo.meta.download_url"
              :alt="author.name"
              class="h-16 w-16 rounded-2xl object-cover ring-2 ring-white shadow-sm"
            />
            <div
              v-else
              class="flex h-16 w-16 items-center justify-center rounded-2xl bg-brand-100 text-xl font-bold text-brand-700 ring-2 ring-white shadow-sm"
            >
              {{ initials(author.name) }}
            </div>
            <!-- Verified dot -->
            <span
              v-if="author.orcid_id || author.google_scholar_url"
              class="absolute -bottom-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500 ring-2 ring-white"
              title="Verified credentials"
            >
              <svg class="h-2.5 w-2.5 text-white" fill="none" viewBox="0 0 12 12" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2 6l3 3 5-5"/>
              </svg>
            </span>
          </div>

          <!-- Info -->
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-1.5">
              <p class="font-bold text-ink transition-colors group-hover:text-brand-700">{{ author.name }}</p>
              <span
                v-if="author.role"
                class="rounded-full px-2 py-0.5 text-[11px] font-semibold"
                :class="roleBadge(author.role)"
              >
                {{ formatRole(author.role) }}
              </span>
            </div>

            <p v-if="author.credentials" class="mt-0.5 text-xs font-medium text-graphite">{{ author.credentials }}</p>
            <p v-if="author.areas_of_expertise" class="mt-1.5 text-sm leading-5 text-graphite line-clamp-2">
              {{ author.areas_of_expertise }}
            </p>

            <!-- Verified pills -->
            <div class="mt-2.5 flex flex-wrap gap-1.5">
              <span v-if="author.orcid_id" class="rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[11px] font-semibold text-emerald-700">
                <span class="font-bold">iD</span> ORCID
              </span>
              <span v-if="author.google_scholar_url" class="rounded-full border border-blue-200 bg-blue-50 px-2 py-0.5 text-[11px] font-semibold text-blue-700">Scholar</span>
              <span v-if="author.linkedin_url" class="rounded-full border border-slate-200 bg-white px-2 py-0.5 text-[11px] font-medium text-graphite">LinkedIn</span>
            </div>
          </div>
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { Users } from "@lucide/vue";
import { cmsApi, type CMSAuthor } from "@/api/cms";
import { useMeta, webPageSchema } from "@/composables/useMeta";

useMeta({
  title: "Our Expert Writers & Editors",
  description: "Meet the credentialed academics, editors, and subject-matter experts who write every article.",
  schema: webPageSchema({ title: "Authors", url: window.location.href }),
});

const isLoading = ref(true);
const authors = ref<CMSAuthor[]>([]);

onMounted(async () => {
  try {
    const { data } = await cmsApi.authors();
    authors.value = Array.isArray(data) ? data : (data as { results: CMSAuthor[] }).results ?? [];
  } catch { /* shows empty state */ }
  finally { isLoading.value = false; }
});

function initials(name: string): string {
  const w = name.trim().split(/\s+/);
  return w.length >= 2 ? (w[0][0] + w[w.length - 1][0]).toUpperCase() : name[0].toUpperCase();
}

const ROLE_LABELS: Record<string, string> = {
  writer: "Writer",
  senior_writer: "Senior Writer",
  editor: "Editor",
  subject_matter_expert: "Subject Expert",
  clinical_reviewer: "Clinical Reviewer",
};

const ROLE_BADGE: Record<string, string> = {
  writer: "bg-slate-100 text-slate-600",
  senior_writer: "bg-brand-100 text-brand-700",
  editor: "bg-violet-100 text-violet-700",
  subject_matter_expert: "bg-amber-100 text-amber-700",
  clinical_reviewer: "bg-emerald-100 text-emerald-700",
};

function formatRole(role: string): string {
  return ROLE_LABELS[role] ?? role.replace(/_/g, " ");
}

function roleBadge(role: string): string {
  return ROLE_BADGE[role] ?? "bg-slate-100 text-slate-600";
}
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

<template>
  <div class="min-h-screen bg-slate-50">
    <div class="bg-white border-b border-slate-200 px-6 py-14">
      <div class="mx-auto max-w-4xl">
        <p class="mb-2 text-xs font-semibold uppercase tracking-wider text-berry">Our experts</p>
        <h1 class="text-4xl font-extrabold text-ink">Meet the team</h1>
        <p class="mt-3 max-w-2xl text-lg text-graphite">
          Credentialed writers, editors, and subject-matter experts behind every order.
        </p>
      </div>
    </div>

    <div class="mx-auto max-w-5xl px-6 py-12">
      <div v-if="isLoading" class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 animate-pulse">
        <div v-for="n in 6" :key="n" class="rounded-xl border border-slate-200 bg-white p-6 space-y-3">
          <div class="size-16 rounded-full bg-slate-200" />
          <div class="h-4 w-2/3 rounded bg-slate-200" />
          <div class="h-3 w-full rounded bg-slate-100" />
        </div>
      </div>

      <div v-else-if="!authors.length" class="py-24 text-center">
        <Users class="mx-auto mb-4 size-10 text-slate-300" />
        <p class="text-sm text-graphite">Author profiles coming soon.</p>
      </div>

      <div v-else class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <RouterLink
          v-for="author in authors"
          :key="author.id"
          :to="`/authors/${author.slug}`"
          class="group flex flex-col rounded-xl border border-slate-200 bg-white p-6 transition-all hover:border-berry/40 hover:shadow-md"
        >
          <!-- Avatar -->
          <div class="mb-4 flex items-center gap-3">
            <img
              v-if="author.profile_photo?.meta?.download_url"
              :src="author.profile_photo.meta.download_url"
              :alt="author.name"
              class="size-14 rounded-full object-cover"
            />
            <div
              v-else
              class="flex size-14 items-center justify-center rounded-full bg-berry/10 text-xl font-bold text-berry"
            >{{ author.name[0] }}</div>
            <div class="min-w-0">
              <p class="font-bold text-ink group-hover:text-berry transition-colors">{{ author.name }}</p>
              <span
                v-if="author.role"
                class="inline-flex rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-graphite capitalize"
              >{{ author.role.replace(/_/g, " ") }}</span>
            </div>
          </div>

          <p v-if="author.credentials" class="mb-2 text-xs font-semibold text-graphite">{{ author.credentials }}</p>
          <p v-if="author.areas_of_expertise" class="flex-1 text-sm text-graphite line-clamp-2">
            {{ author.areas_of_expertise }}
          </p>

          <div class="mt-4 flex flex-wrap gap-2">
            <span v-if="author.orcid_id" class="rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-medium text-emerald-700">ORCID</span>
            <span v-if="author.google_scholar_url" class="rounded-full bg-blue-50 px-2 py-0.5 text-xs font-medium text-blue-700">Scholar</span>
            <span v-if="author.linkedin_url" class="rounded-full bg-sky-50 px-2 py-0.5 text-xs font-medium text-sky-700">LinkedIn</span>
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
  description: "Meet the credentialed academics, editors, and subject-matter experts who work on your orders.",
  schema: webPageSchema({ title: "Authors", url: window.location.href }),
});

const isLoading = ref(true);
const authors = ref<CMSAuthor[]>([]);

onMounted(async () => {
  try {
    const { data } = await cmsApi.authors();
    authors.value = Array.isArray(data) ? data : (data as { results: CMSAuthor[] }).results ?? [];
  } catch { /* empty state */ }
  finally { isLoading.value = false; }
});
</script>

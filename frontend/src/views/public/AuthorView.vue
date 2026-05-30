<template>
  <div class="min-h-screen bg-white">

    <div v-if="isLoading" class="mx-auto max-w-3xl px-6 py-16 animate-pulse space-y-6">
      <div class="flex gap-6">
        <div class="size-24 shrink-0 rounded-full bg-slate-200" />
        <div class="flex-1 space-y-3 pt-2">
          <div class="h-6 w-1/2 rounded bg-slate-200" />
          <div class="h-4 w-2/3 rounded bg-slate-100" />
          <div class="h-3 w-full rounded bg-slate-100" />
        </div>
      </div>
    </div>

    <div v-else-if="notFound" class="py-32 text-center">
      <RouterLink to="/authors" class="text-sm text-berry hover:underline">← All authors</RouterLink>
      <p class="mt-4 font-semibold text-ink">Author not found.</p>
    </div>

    <template v-else-if="author">
      <!-- Profile header -->
      <div class="border-b border-slate-100 bg-slate-50 px-6 py-14">
        <div class="mx-auto max-w-3xl flex flex-col gap-8 sm:flex-row sm:items-start">
          <!-- Avatar -->
          <img
            v-if="author.profile_photo?.meta?.download_url"
            :src="author.profile_photo.meta.download_url"
            :alt="author.name"
            class="size-28 shrink-0 rounded-2xl object-cover shadow-sm"
          />
          <div
            v-else
            class="flex size-28 shrink-0 items-center justify-center rounded-2xl bg-berry/10 text-4xl font-extrabold text-berry"
          >{{ author.name[0] }}</div>

          <div class="min-w-0">
            <RouterLink to="/authors" class="mb-3 inline-flex items-center gap-1.5 text-xs text-graphite hover:text-ink">
              <ArrowLeft class="size-3" /> All authors
            </RouterLink>
            <h1 class="text-3xl font-extrabold text-ink">{{ author.name }}</h1>
            <p v-if="author.credentials" class="mt-1 text-sm font-semibold text-graphite">{{ author.credentials }}</p>
            <p v-if="author.role" class="mt-1 text-xs text-graphite capitalize">{{ author.role.replace(/_/g, " ") }}</p>

            <!-- Expertise + experience -->
            <div class="mt-3 flex flex-wrap gap-3 text-xs text-graphite">
              <span v-if="author.years_experience">{{ author.years_experience }}+ years experience</span>
              <span v-if="author.areas_of_expertise">{{ author.areas_of_expertise }}</span>
            </div>

            <!-- External links -->
            <div class="mt-4 flex flex-wrap gap-3">
              <a v-if="author.orcid_id" :href="`https://orcid.org/${author.orcid_id}`" target="_blank" rel="noreferrer"
                 class="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700 hover:bg-emerald-100">
                ORCID
              </a>
              <a v-if="author.google_scholar_url" :href="author.google_scholar_url" target="_blank" rel="noreferrer"
                 class="inline-flex items-center gap-1.5 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-700 hover:bg-blue-100">
                Google Scholar
              </a>
              <a v-if="author.linkedin_url" :href="author.linkedin_url" target="_blank" rel="noreferrer"
                 class="inline-flex items-center gap-1.5 rounded-full border border-sky-200 bg-sky-50 px-3 py-1 text-xs font-semibold text-sky-700 hover:bg-sky-100">
                LinkedIn
              </a>
              <a v-if="author.twitter_handle" :href="`https://twitter.com/${author.twitter_handle}`" target="_blank" rel="noreferrer"
                 class="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-graphite hover:bg-slate-50">
                @{{ author.twitter_handle }}
              </a>
              <a v-if="author.personal_website" :href="author.personal_website" target="_blank" rel="noreferrer"
                 class="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-graphite hover:bg-slate-50">
                Website
              </a>
            </div>
          </div>
        </div>
      </div>

      <div class="mx-auto max-w-3xl px-6 py-10 space-y-10">
        <!-- Bio -->
        <section v-if="author.bio">
          <h2 class="mb-4 text-lg font-bold text-ink">About</h2>
          <p class="leading-7 text-graphite">{{ author.bio }}</p>
        </section>

        <!-- Degrees + licenses -->
        <section v-if="author.degrees?.length || author.licenses?.length">
          <h2 class="mb-4 text-lg font-bold text-ink">Credentials</h2>
          <ul class="space-y-1.5">
            <li v-for="deg in author.degrees ?? []" :key="deg" class="flex items-start gap-2 text-sm text-graphite">
              <GraduationCap class="mt-0.5 size-4 shrink-0 text-berry" />{{ deg }}
            </li>
            <li v-for="lic in (author as any).licenses ?? []" :key="lic" class="flex items-start gap-2 text-sm text-graphite">
              <Award class="mt-0.5 size-4 shrink-0 text-signal" />{{ lic }}
            </li>
          </ul>
        </section>

        <!-- Recent posts -->
        <section v-if="posts.length">
          <h2 class="mb-4 text-lg font-bold text-ink">Articles by {{ author.name }}</h2>
          <div class="space-y-4">
            <RouterLink
              v-for="post in posts"
              :key="post.id"
              :to="`/blog/${post.meta.slug}`"
              class="group flex gap-4 rounded-xl border border-slate-200 bg-white p-4 transition-all hover:border-berry/40 hover:shadow-sm"
            >
              <img
                v-if="post.featured_image?.meta?.download_url"
                :src="post.featured_image.meta.download_url"
                :alt="post.title"
                class="size-16 shrink-0 rounded-lg object-cover"
              />
              <div class="min-w-0">
                <p class="font-semibold text-ink group-hover:text-berry transition-colors line-clamp-2">{{ post.title }}</p>
                <p v-if="post.excerpt" class="mt-1 text-xs text-graphite line-clamp-1">{{ post.excerpt }}</p>
                <p class="mt-1 text-xs text-slate-400">
                  <span v-if="post.reading_time">{{ post.reading_time }} min read</span>
                  <span v-if="post.meta.first_published_at"> · {{ fmtDate(post.meta.first_published_at) }}</span>
                </p>
              </div>
            </RouterLink>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { RouterLink, useRoute } from "vue-router";
import { ArrowLeft, Award, GraduationCap } from "@lucide/vue";
import { cmsApi, type BlogPostSummary, type CMSAuthor } from "@/api/cms";
import { useMeta } from "@/composables/useMeta";

const route     = useRoute();
const isLoading = ref(true);
const notFound  = ref(false);
const author    = ref<CMSAuthor | null>(null);
const posts     = ref<BlogPostSummary[]>([]);

async function load() {
  const slug = route.params.slug as string;
  isLoading.value = true;
  notFound.value  = false;
  author.value    = null;
  posts.value     = [];

  try {
    const [authorRes, postsRes] = await Promise.all([
      cmsApi.author(slug),
      cmsApi.authorPosts(slug),
    ]);
    author.value = authorRes.data;
    posts.value  = Array.isArray(postsRes.data) ? postsRes.data : [];

    useMeta({
      title: author.value.name,
      description: author.value.bio ?? `Articles and expertise by ${author.value.name}.`,
      image: author.value.profile_photo?.meta?.download_url,
      url: window.location.href,
      schema: {
        "@context": "https://schema.org",
        "@type": "Person",
        name: author.value.name,
        description: author.value.bio,
        image: author.value.profile_photo?.meta?.download_url,
        sameAs: [
          author.value.orcid_id        ? `https://orcid.org/${author.value.orcid_id}` : null,
          author.value.google_scholar_url,
          author.value.linkedin_url,
          author.value.personal_website,
        ].filter(Boolean),
        jobTitle: author.value.role?.replace(/_/g, " "),
      },
    });
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

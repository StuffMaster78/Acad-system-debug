<template>
  <div class="min-h-screen bg-white">

    <!-- Loading -->
    <div v-if="isLoading" class="mx-auto max-w-3xl px-6 py-16 animate-pulse space-y-6">
      <div class="flex gap-6">
        <div class="size-28 shrink-0 rounded-2xl bg-slate-200" />
        <div class="flex-1 space-y-3 pt-2">
          <div class="h-6 w-1/2 rounded bg-slate-200" />
          <div class="h-4 w-2/3 rounded bg-slate-100" />
          <div class="h-3 w-full rounded bg-slate-100" />
        </div>
      </div>
    </div>

    <!-- Not found -->
    <div v-else-if="notFound" class="py-32 text-center">
      <RouterLink to="/authors" class="text-sm text-graphite hover:text-ink">← All authors</RouterLink>
      <p class="mt-4 font-semibold text-ink">Author not found.</p>
    </div>

    <template v-else-if="author">

      <!-- ── Profile header ───────────────────────────────────────────── -->
      <div class="border-b border-slate-100 bg-slate-50 px-6 py-14">
        <div class="mx-auto max-w-3xl flex flex-col gap-8 sm:flex-row sm:items-start">

          <!-- Avatar with verified dot -->
          <div class="relative shrink-0 self-start">
            <img
              v-if="author.profile_photo?.meta?.download_url"
              :src="author.profile_photo.meta.download_url"
              :alt="author.name"
              class="size-28 rounded-2xl object-cover shadow-sm ring-2 ring-white"
            />
            <div
              v-else
              class="flex size-28 items-center justify-center rounded-2xl bg-brand-100 text-4xl font-extrabold text-brand-700 ring-2 ring-white"
            >
              {{ author.name[0] }}
            </div>
            <span
              v-if="author.orcid_id || author.google_scholar_url"
              class="absolute -bottom-1.5 -right-1.5 flex size-6 items-center justify-center rounded-full bg-emerald-500 ring-2 ring-white"
              title="Verified credentials"
            >
              <svg class="size-3 text-white" fill="none" viewBox="0 0 12 12" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2 6l3 3 5-5" />
              </svg>
            </span>
          </div>

          <!-- Identity -->
          <div class="min-w-0">
            <RouterLink to="/authors" class="mb-3 inline-flex items-center gap-1.5 text-xs text-graphite hover:text-ink">
              <ArrowLeft class="size-3" /> All authors
            </RouterLink>

            <div class="flex flex-wrap items-center gap-2">
              <h1 class="text-3xl font-extrabold text-ink">{{ author.name }}</h1>
              <span
                v-if="author.role"
                class="rounded-full px-2.5 py-0.5 text-xs font-semibold"
                :class="roleBadgeClass(author.role)"
              >
                {{ formatRole(author.role) }}
              </span>
            </div>

            <p v-if="author.credentials" class="mt-1 text-sm font-semibold text-graphite">
              {{ author.credentials }}
            </p>

            <div class="mt-2 flex flex-wrap gap-3 text-xs text-graphite">
              <span v-if="author.years_experience" class="flex items-center gap-1">
                <GraduationCap class="size-3.5" /> {{ author.years_experience }}+ years experience
              </span>
              <span v-if="author.areas_of_expertise">{{ author.areas_of_expertise }}</span>
              <span v-if="posts.length" class="flex items-center gap-1">
                <BookOpen class="size-3.5" /> {{ posts.length }}{{ posts.length === 20 ? "+" : "" }} articles
              </span>
            </div>

            <!-- Verified credential pills -->
            <div class="mt-3 flex flex-wrap gap-2">
              <a
                v-if="author.orcid_id"
                :href="`https://orcid.org/${author.orcid_id}`"
                target="_blank" rel="noreferrer"
                class="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700 hover:bg-emerald-100 transition-colors"
              >
                <span class="font-bold">iD</span> ORCID
              </a>
              <a
                v-if="author.google_scholar_url"
                :href="author.google_scholar_url"
                target="_blank" rel="noreferrer"
                class="inline-flex items-center gap-1 rounded-full border border-blue-200 bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700 hover:bg-blue-100 transition-colors"
              >
                <BookOpen class="size-3" /> Google Scholar
              </a>
              <a
                v-if="author.linkedin_url"
                :href="author.linkedin_url"
                target="_blank" rel="noreferrer"
                class="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold text-graphite hover:bg-slate-50 transition-colors"
              >
                LinkedIn
              </a>
              <a
                v-if="author.twitter_handle"
                :href="`https://twitter.com/${author.twitter_handle.replace('@', '')}`"
                target="_blank" rel="noreferrer"
                class="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold text-graphite hover:bg-slate-50 transition-colors"
              >
                @{{ author.twitter_handle.replace("@", "") }}
              </a>
              <a
                v-if="author.personal_website"
                :href="author.personal_website"
                target="_blank" rel="noreferrer"
                class="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold text-graphite hover:bg-slate-50 transition-colors"
              >
                Website
              </a>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Body ───────────────────────────────────────────────────────── -->
      <div class="mx-auto max-w-3xl px-6 py-10 space-y-10">

        <!-- Bio -->
        <section v-if="author.bio">
          <h2 class="mb-3 text-lg font-bold text-ink">About</h2>
          <p class="leading-7 text-graphite">{{ author.bio }}</p>
        </section>

        <!-- Credentials -->
        <section v-if="author.degrees?.length || author.licenses?.length">
          <h2 class="mb-3 text-lg font-bold text-ink">Credentials</h2>
          <ul class="space-y-1.5">
            <li
              v-for="deg in author.degrees ?? []"
              :key="String(deg)"
              class="flex items-start gap-2 text-sm text-graphite"
            >
              <GraduationCap class="mt-0.5 size-4 shrink-0 text-brand-700" />
              {{ typeof deg === "object" ? formatDegree(deg) : deg }}
            </li>
            <li
              v-for="lic in author.licenses ?? []"
              :key="String(lic)"
              class="flex items-start gap-2 text-sm text-graphite"
            >
              <Award class="mt-0.5 size-4 shrink-0 text-emerald-600" />
              {{ typeof lic === "object" ? formatLicense(lic) : lic }}
            </li>
          </ul>
        </section>

        <!-- Articles -->
        <section v-if="posts.length">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-lg font-bold text-ink">Articles by {{ author.name }}</h2>
            <span class="text-xs text-graphite">
              {{ posts.length }}{{ posts.length === 20 ? "+" : "" }} published
            </span>
          </div>
          <div class="space-y-3">
            <RouterLink
              v-for="post in posts"
              :key="post.id"
              :to="`/blog/${post.meta.slug}`"
              class="group flex gap-4 rounded-xl border border-slate-200 bg-white p-4 transition-all hover:border-brand-200 hover:shadow-sm"
            >
              <img
                v-if="post.featured_image?.meta?.download_url"
                :src="post.featured_image.meta.download_url"
                :alt="post.title"
                class="size-16 shrink-0 rounded-lg object-cover bg-slate-100"
                loading="lazy"
              />
              <div v-else class="size-16 shrink-0 rounded-lg bg-slate-100 flex items-center justify-center">
                <BookOpen class="size-6 text-slate-300" />
              </div>
              <div class="min-w-0">
                <p class="font-semibold text-ink transition-colors group-hover:text-brand-700 line-clamp-2 leading-snug">
                  {{ post.title }}
                </p>
                <p v-if="post.excerpt" class="mt-1 text-xs text-graphite line-clamp-1">
                  {{ post.excerpt }}
                </p>
                <div class="mt-1.5 flex flex-wrap items-center gap-2 text-xs text-slate-400">
                  <span v-if="post.reading_time">{{ post.reading_time }} min read</span>
                  <span v-if="displayDate(post)">· {{ displayDate(post) }}</span>
                  <span
                    v-if="post.category"
                    class="ml-auto rounded-full bg-brand-50 px-2 py-0.5 text-[11px] font-semibold text-brand-700"
                  >
                    {{ post.category.name }}
                  </span>
                </div>
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
import { ArrowLeft, Award, BookOpen, GraduationCap } from "@lucide/vue";
import { cmsApi, type BlogPostSummary, type CMSAuthor } from "@/api/cms";
import { useMeta, personSchema, breadcrumbSchema } from "@/composables/useMeta";

const route = useRoute();
const isLoading = ref(true);
const notFound = ref(false);
const author = ref<CMSAuthor | null>(null);
const posts = ref<BlogPostSummary[]>([]);

async function load() {
  const slug = route.params.slug as string;
  isLoading.value = true;
  notFound.value = false;
  author.value = null;
  posts.value = [];

  try {
    const [authorRes, postsRes] = await Promise.all([
      cmsApi.author(slug),
      cmsApi.authorPosts(slug),
    ]);
    author.value = authorRes.data;
    posts.value = Array.isArray(postsRes.data) ? postsRes.data : [];

    const a = author.value;
    useMeta({
      title:       a.name,
      description: a.bio ?? `Articles and expertise by ${a.name}.`,
      image:       a.profile_photo?.meta?.download_url,
      url:         window.location.href,
      schemas: [
        personSchema({
          name:             a.name,
          url:              window.location.href,
          bio:              a.bio,
          image:            a.profile_photo?.meta?.download_url,
          jobTitle:         a.role?.replace(/_/g, " "),
          credentials:      a.credentials,
          degrees:          a.degrees,
          areasOfExpertise: a.areas_of_expertise,
          yearsExperience:  a.years_experience,
          orcidId:          a.orcid_id,
          googleScholarUrl: a.google_scholar_url,
          linkedinUrl:      a.linkedin_url,
          personalWebsite:  a.personal_website,
        }),
        breadcrumbSchema([
          { name: "Home",    url: window.location.origin + "/" },
          { name: "Authors", url: window.location.origin + "/authors" },
          { name: a.name,    url: window.location.href },
        ]),
      ],
    });
  } catch {
    notFound.value = true;
  } finally {
    isLoading.value = false;
  }
}

function displayDate(post: BlogPostSummary): string {
  const raw = post.canonical_published_at ?? post.original_published_at ?? post.meta.first_published_at;
  if (!raw) return "";
  return new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(raw));
}

const ROLE_LABELS: Record<string, string> = {
  writer:                "Writer",
  senior_writer:         "Senior Writer",
  editor:                "Editor",
  subject_matter_expert: "Subject Expert",
  clinical_reviewer:     "Clinical Reviewer",
};
function formatRole(role?: string): string {
  return role ? (ROLE_LABELS[role] ?? role.replace(/_/g, " ")) : "";
}
const ROLE_BADGE: Record<string, string> = {
  writer:                "bg-slate-100 text-slate-600",
  senior_writer:         "bg-brand-100 text-brand-700",
  editor:                "bg-violet-100 text-violet-700",
  subject_matter_expert: "bg-amber-100 text-amber-700",
  clinical_reviewer:     "bg-emerald-100 text-emerald-700",
};
function roleBadgeClass(role: string): string {
  return ROLE_BADGE[role] ?? "bg-slate-100 text-slate-600";
}

function formatDegree(d: unknown): string {
  if (typeof d !== "object" || !d) return String(d);
  const obj = d as Record<string, string>;
  return [obj.degree, obj.institution, obj.year].filter(Boolean).join(", ");
}
function formatLicense(l: unknown): string {
  if (typeof l !== "object" || !l) return String(l);
  const obj = l as Record<string, string>;
  return [obj.license, obj.state, obj.number].filter(Boolean).join(" · ");
}

onMounted(load);
watch(() => route.params.slug, load);
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.line-clamp-1 {
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

<template>
  <!-- Primary author — large card -->
  <div v-if="variant === 'primary'" class="not-prose rounded-2xl border border-slate-200 bg-white overflow-hidden">
    <!-- Header band -->
    <div class="flex items-start gap-5 bg-slate-50 px-6 py-6 border-b border-slate-100">
      <!-- Avatar -->
      <div class="relative shrink-0">
        <img
          v-if="author.profile_photo?.meta?.download_url"
          :src="author.profile_photo.meta.download_url"
          :alt="author.name"
          class="size-20 rounded-2xl object-cover ring-2 ring-white shadow-md"
        />
        <div
          v-else
          class="size-20 rounded-2xl bg-brand-100 flex items-center justify-center text-2xl font-bold text-brand-700 ring-2 ring-white shadow-md"
        >
          {{ author.name[0] }}
        </div>
        <!-- Verified dot -->
        <span
          v-if="author.orcid_id || author.google_scholar_url"
          class="absolute -bottom-1 -right-1 flex size-5 items-center justify-center rounded-full bg-emerald-500 ring-2 ring-white"
          title="Verified credentials"
        >
          <svg class="size-2.5 text-white" fill="none" viewBox="0 0 12 12" stroke="currentColor" stroke-width="2.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M2 6l3 3 5-5" />
          </svg>
        </span>
      </div>

      <!-- Identity -->
      <div class="min-w-0 flex-1">
        <div class="flex flex-wrap items-center gap-2">
          <RouterLink
            :to="`/authors/${author.slug}`"
            class="text-lg font-bold text-ink hover:text-brand-700 transition-colors"
          >
            {{ author.name }}
          </RouterLink>
          <span
            v-if="author.role"
            class="rounded-full px-2 py-0.5 text-[11px] font-semibold"
            :class="roleBadgeClass(author.role)"
          >
            {{ formatRole(author.role) }}
          </span>
        </div>

        <p v-if="author.credentials" class="mt-0.5 text-sm font-medium text-graphite">
          {{ author.credentials }}
        </p>

        <div class="mt-1.5 flex flex-wrap items-center gap-3 text-xs text-graphite">
          <span v-if="author.years_experience" class="flex items-center gap-1">
            <GraduationCap class="size-3.5" /> {{ author.years_experience }} yrs experience
          </span>
          <span v-if="author.areas_of_expertise" class="truncate max-w-[240px]">
            {{ author.areas_of_expertise }}
          </span>
        </div>

        <!-- Verified credential pills -->
        <div class="mt-2.5 flex flex-wrap gap-2">
          <a
            v-if="author.orcid_id"
            :href="`https://orcid.org/${author.orcid_id}`"
            target="_blank" rel="noreferrer"
            class="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[11px] font-semibold text-emerald-700 hover:bg-emerald-100 transition-colors"
          >
            <span class="font-bold">iD</span> ORCID
          </a>
          <a
            v-if="author.google_scholar_url"
            :href="author.google_scholar_url"
            target="_blank" rel="noreferrer"
            class="inline-flex items-center gap-1 rounded-full border border-blue-200 bg-blue-50 px-2 py-0.5 text-[11px] font-semibold text-blue-700 hover:bg-blue-100 transition-colors"
          >
            <BookOpen class="size-3" /> Scholar
          </a>
        </div>
      </div>
    </div>

    <!-- Bio + socials -->
    <div class="px-6 py-5">
      <p v-if="author.bio" class="text-sm leading-7 text-graphite">{{ author.bio }}</p>

      <!-- Social links -->
      <div v-if="hasSocials" class="mt-4 flex flex-wrap gap-2">
        <a
          v-if="author.linkedin_url"
          :href="author.linkedin_url"
          target="_blank" rel="noreferrer"
          class="social-pill"
          title="LinkedIn"
        >
          <LinkedInIcon /> LinkedIn
        </a>
        <a
          v-if="author.twitter_handle"
          :href="`https://twitter.com/${author.twitter_handle.replace('@','')}`"
          target="_blank" rel="noreferrer"
          class="social-pill"
          title="X / Twitter"
        >
          <TwitterIcon /> @{{ author.twitter_handle.replace('@','') }}
        </a>
        <a
          v-if="author.personal_website"
          :href="author.personal_website"
          target="_blank" rel="noreferrer"
          class="social-pill"
          title="Website"
        >
          <Globe class="size-3.5" /> Website
        </a>
      </div>
    </div>

    <!-- More articles strip -->
    <div v-if="recentPosts.length" class="border-t border-slate-100">
      <div class="px-6 py-4">
        <p class="mb-3 text-xs font-semibold uppercase tracking-wider text-graphite">
          More by {{ author.name }}
        </p>
        <div class="space-y-2.5">
          <RouterLink
            v-for="p in recentPosts.slice(0, 3)"
            :key="p.id"
            :to="`/blog/${p.meta.slug}`"
            class="group flex items-start gap-3"
          >
            <img
              v-if="p.featured_image?.meta?.download_url"
              :src="p.featured_image.meta.download_url"
              :alt="p.title"
              class="size-12 shrink-0 rounded-lg object-cover bg-slate-100"
              loading="lazy"
            />
            <div v-else class="size-12 shrink-0 rounded-lg bg-slate-100" />
            <p class="text-sm font-medium text-ink group-hover:text-brand-700 transition-colors leading-snug line-clamp-2">
              {{ p.title }}
            </p>
          </RouterLink>
        </div>
        <RouterLink
          :to="`/authors/${author.slug}`"
          class="mt-4 inline-flex items-center gap-1 text-xs font-semibold text-brand-700 hover:underline"
        >
          See all articles <ArrowRight class="size-3" />
        </RouterLink>
      </div>
    </div>
  </div>

  <!-- Contributing author — compact card -->
  <RouterLink
    v-else
    :to="`/authors/${author.slug}`"
    class="not-prose group flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 transition-all hover:border-brand-200 hover:shadow-sm"
  >
    <img
      v-if="author.profile_photo?.meta?.download_url"
      :src="author.profile_photo.meta.download_url"
      :alt="author.name"
      class="size-10 shrink-0 rounded-full object-cover"
    />
    <div v-else class="size-10 shrink-0 rounded-full bg-brand-100 flex items-center justify-center text-sm font-bold text-brand-700">
      {{ author.name[0] }}
    </div>
    <div class="min-w-0">
      <p class="text-sm font-semibold text-ink group-hover:text-brand-700 transition-colors">{{ author.name }}</p>
      <p class="text-xs text-graphite truncate">{{ author.credentials || formatRole(author.role) }}</p>
    </div>
    <ArrowRight class="ml-auto size-3.5 shrink-0 text-slate-300 group-hover:text-brand-400 transition-colors" />
  </RouterLink>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { ArrowRight, BookOpen, Globe, GraduationCap } from "@lucide/vue";
import { cmsApi, type BlogPostSummary, type CMSAuthor } from "@/api/cms";

const props = defineProps<{
  author: CMSAuthor;
  variant?: "primary" | "contributing";
}>();

const recentPosts = ref<BlogPostSummary[]>([]);

const hasSocials = computed(() =>
  !!(props.author.linkedin_url || props.author.twitter_handle || props.author.personal_website)
);

onMounted(async () => {
  if (props.variant !== "primary") return;
  try {
    const res = await cmsApi.authorPosts(props.author.slug);
    recentPosts.value = Array.isArray(res.data) ? res.data.slice(0, 3) : [];
  } catch { /* silent */ }
});

// ── Inline SVG icons ─────────────────────────────────────────────────────

const LinkedInIcon = defineComponent({ setup() {
  return () => h("svg", { viewBox: "0 0 24 24", fill: "currentColor", class: "size-3.5" }, [
    h("path", { d: "M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" }),
  ]);
}});

const TwitterIcon = defineComponent({ setup() {
  return () => h("svg", { viewBox: "0 0 24 24", fill: "currentColor", class: "size-3.5" }, [
    h("path", { d: "M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.744l7.73-8.835L1.254 2.25H8.08l4.261 5.635 5.903-5.635Zm-1.161 17.52h1.833L7.084 4.126H5.117z" }),
  ]);
}});

// ── Helpers ───────────────────────────────────────────────────────────────

const ROLE_LABELS: Record<string, string> = {
  writer: "Writer",
  senior_writer: "Senior Writer",
  editor: "Editor",
  subject_matter_expert: "Subject Expert",
  clinical_reviewer: "Clinical Reviewer",
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
</script>

<style scoped>
.social-pill {
  @apply inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-graphite transition-colors hover:border-brand-300 hover:text-brand-700;
}
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

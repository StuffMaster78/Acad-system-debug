<template>
  <div class="min-h-screen bg-white">

    <!-- Loading -->
    <div v-if="isLoading" class="mx-auto max-w-3xl px-6 py-16 animate-pulse space-y-6">
      <div class="h-8 w-3/4 rounded bg-slate-200" />
      <div class="h-4 w-1/2 rounded bg-slate-100" />
      <div class="h-64 rounded-xl bg-slate-200" />
      <div v-for="n in 5" :key="n" class="h-3 rounded bg-slate-100" :style="{ width: n % 2 ? '100%' : '80%' }" />
    </div>

    <!-- Not found -->
    <div v-else-if="notFound" class="py-32 text-center">
      <p class="text-lg font-semibold text-ink">Article not found</p>
      <RouterLink to="/blog" class="mt-4 inline-flex items-center gap-1.5 text-sm text-berry hover:underline">
        <ArrowLeft class="size-3.5" /> Back to blog
      </RouterLink>
    </div>

    <template v-else-if="post">
      <!-- Article header -->
      <div class="border-b border-slate-100 bg-slate-50 px-6 py-14">
        <div class="mx-auto max-w-3xl">
          <RouterLink to="/blog" class="mb-6 inline-flex items-center gap-1.5 text-sm text-graphite hover:text-ink">
            <ArrowLeft class="size-3.5" /> All articles
          </RouterLink>

          <span
            v-if="post.category"
            class="mb-3 inline-flex rounded-full bg-berry/10 px-2.5 py-0.5 text-xs font-semibold text-berry"
          >
            {{ post.category.name }}
          </span>

          <h1 class="text-4xl font-extrabold leading-tight text-ink">{{ post.title }}</h1>
          <p v-if="post.excerpt" class="mt-4 text-xl text-graphite leading-8">{{ post.excerpt }}</p>

          <!-- Author + meta row -->
          <div class="mt-6 flex flex-wrap items-center gap-4">
            <div v-if="post.primary_author" class="flex items-center gap-2.5">
              <img
                v-if="post.primary_author.profile_photo?.meta?.download_url"
                :src="post.primary_author.profile_photo.meta.download_url"
                :alt="post.primary_author.name"
                class="size-9 rounded-full object-cover"
              />
              <div v-else class="flex size-9 items-center justify-center rounded-full bg-berry/10 text-sm font-bold text-berry">
                {{ post.primary_author.name[0] }}
              </div>
              <div>
                <p class="text-sm font-semibold text-ink">{{ post.primary_author.name }}</p>
                <p v-if="post.primary_author.credentials" class="text-xs text-graphite">{{ post.primary_author.credentials }}</p>
              </div>
            </div>
            <div class="flex flex-wrap gap-3 text-xs text-graphite">
              <span v-if="post.meta.first_published_at">{{ fmtDate(post.meta.first_published_at) }}</span>
              <span
                v-if="post.last_substantive_update && post.last_substantive_update !== post.meta.first_published_at"
                class="text-signal font-medium"
              >
                · Updated {{ fmtDate(post.last_substantive_update) }}
              </span>
              <span v-if="post.reading_time">· {{ post.reading_time }} min read</span>
              <span v-if="post.word_count">· {{ post.word_count.toLocaleString() }} words</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Featured image -->
      <div v-if="post.featured_image?.meta?.download_url" class="bg-slate-100">
        <img
          :src="post.featured_image.meta.download_url"
          :alt="post.title"
          class="mx-auto max-h-96 w-full max-w-4xl object-cover"
          loading="eager"
        />
      </div>

      <!-- Body -->
      <div class="mx-auto max-w-3xl px-6 py-12">
        <!-- Table of contents -->
        <nav
          v-if="post.toc?.length"
          class="mb-10 rounded-xl border border-slate-200 bg-slate-50 p-5"
        >
          <p class="mb-3 text-xs font-semibold uppercase tracking-wider text-graphite">In this article</p>
          <ol class="space-y-1">
            <li
              v-for="item in post.toc"
              :key="item.anchor"
              :class="item.level === 3 ? 'ml-4' : ''"
            >
              <a :href="`#${item.anchor}`" class="text-sm text-berry hover:underline">{{ item.text }}</a>
            </li>
          </ol>
        </nav>

        <!-- StreamField blocks -->
        <BlockRenderer :blocks="post.body ?? []" />

        <!-- Engagement bar -->
        <ArticleEngagementBar
          :summary="engagement.summary.value"
          :is-mutating="engagement.isMutating.value"
          :is-authenticated="auth.isAuthenticated"
          :reading-time="post.reading_time ?? null"
          :page-url="canonicalUrl"
          @react="engagement.react"
          @share="engagement.share"
          @bookmark="engagement.bookmark"
        />

        <!-- Tags -->
        <div v-if="post.tags?.length" class="mt-10 flex flex-wrap gap-2 border-t border-slate-100 pt-6">
          <span
            v-for="tag in post.tags"
            :key="tag.id"
            class="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-medium text-graphite"
          >
            #{{ tag.name }}
          </span>
        </div>

        <!-- Author bio card -->
        <div v-if="post.primary_author" class="mt-10 rounded-xl border border-slate-200 bg-slate-50 p-6">
          <div class="flex items-start gap-4">
            <img
              v-if="post.primary_author.profile_photo?.meta?.download_url"
              :src="post.primary_author.profile_photo.meta.download_url"
              :alt="post.primary_author.name"
              class="size-14 rounded-full object-cover"
            />
            <div v-else class="flex size-14 items-center justify-center rounded-full bg-berry/10 text-xl font-bold text-berry">
              {{ post.primary_author.name[0] }}
            </div>
            <div class="min-w-0">
              <p class="font-bold text-ink">{{ post.primary_author.name }}</p>
              <p v-if="post.primary_author.credentials" class="text-xs text-graphite">{{ post.primary_author.credentials }}</p>
              <p v-if="post.primary_author.bio" class="mt-2 text-sm leading-6 text-graphite">{{ post.primary_author.bio }}</p>
              <div class="mt-3 flex flex-wrap gap-3 text-xs">
                <a v-if="post.primary_author.linkedin_url" :href="post.primary_author.linkedin_url" target="_blank" rel="noreferrer" class="text-berry hover:underline">LinkedIn</a>
                <a v-if="post.primary_author.orcid_id" :href="`https://orcid.org/${post.primary_author.orcid_id}`" target="_blank" rel="noreferrer" class="text-berry hover:underline">ORCID</a>
                <a v-if="post.primary_author.google_scholar_url" :href="post.primary_author.google_scholar_url" target="_blank" rel="noreferrer" class="text-berry hover:underline">Google Scholar</a>
              </div>
            </div>
          </div>
        </div>

        <!-- Ask Widget -->
        <div class="mt-10">
          <AskWidget :placeholder="`Ask a question about '${post?.title ?? 'this topic'}'…`" />
        </div>

        <!-- CTA -->
        <div class="mt-10 rounded-2xl bg-gradient-to-br from-ink to-slate-700 p-8 text-center text-white">
          <h3 class="text-2xl font-bold">Need help with your assignment?</h3>
          <p class="mt-2 text-slate-300">Our expert writers are ready. Place your order in minutes.</p>
          <RouterLink
            to="/auth/register"
            class="mt-6 inline-flex items-center gap-2 rounded-xl bg-berry px-7 py-3.5 font-bold text-white shadow-lg hover:bg-rose-700"
          >
            Get started <ArrowRight class="size-4" />
          </RouterLink>
        </div>
      </div>

        <!-- Citations / references -->
        <CitationList
          v-if="citations.length && post.citation_mode && post.citation_mode !== 'none'"
          :citations="citations"
          :mode="post.citation_mode"
        />
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
import { RouterLink, useRoute } from "vue-router";
import { ArrowLeft, ArrowRight } from "@lucide/vue";
import { cmsApi, type BlogPost, type Citation } from "@/api/cms";
import {
  useMeta, articleSchema, breadcrumbSchema, faqPageSchema,
  extractFaqItems, personSchema,
} from "@/composables/useMeta";
import BlockRenderer from "@/components/cms/BlockRenderer.vue";
import CitationList from "@/components/cms/CitationList.vue";
import AskWidget from "@/components/ui/AskWidget.vue";
import ArticleEngagementBar from "@/components/cms/ArticleEngagementBar.vue";
import { usePageEngagement } from "@/composables/usePageEngagement";
import { useAuthStore } from "@/stores/auth";
import { computed } from "vue";

const route = useRoute();
const isLoading = ref(true);
const notFound = ref(false);
const post = ref<BlogPost | null>(null);
const citations = ref<Citation[]>([]);
const auth = useAuthStore();
const canonicalUrl = computed(() => window.location.href);

// Engagement — page ID is available after post loads; composable handles null gracefully
const postId = computed(() => post.value?.id ?? null);
const engagement = usePageEngagement(postId.value);

async function load() {
  const slug = route.params.slug as string;
  isLoading.value = true;
  notFound.value = false;
  post.value = null;

  try {
    const { data } = await cmsApi.blogPost(slug);
    if (!data.items.length) {
      notFound.value = true;
      return;
    }
    post.value = data.items[0];

    // Fetch formal citations if mode requires it
    if (post.value.citation_mode && post.value.citation_mode !== 'none') {
      try {
        const citRes = await cmsApi.citations(post.value.id);
        citations.value = Array.isArray(citRes.data) ? citRes.data : [];
      } catch { citations.value = []; }
    }

    const faqItems = extractFaqItems(post.value.body ?? []);
    const author   = post.value.primary_author;

    const schemas = [
      articleSchema({
        title:       post.value.title,
        description: post.value.excerpt,
        url:         window.location.href,
        image:       post.value.featured_image?.meta?.download_url,
        publishedAt: post.value.meta.first_published_at ?? undefined,
        updatedAt:   post.value.last_substantive_update ?? undefined,
        authorName:  author?.name,
        authorUrl:   author ? `${window.location.origin}/authors/${post.value.meta?.slug?.split("/")[0] ?? ""}` : undefined,
      }),
      breadcrumbSchema([
        { name: "Home",   url: window.location.origin + "/" },
        { name: "Blog",   url: window.location.origin + "/blog" },
        { name: post.value.title, url: window.location.href },
      ]),
      ...(faqItems.length ? [faqPageSchema(faqItems)!] : []),
      ...(author ? [personSchema({
        name:              author.name,
        url:               `${window.location.origin}/authors/${author.slug ?? ""}`,
        bio:               author.bio,
        image:             author.profile_photo?.meta?.download_url,
        jobTitle:          author.role?.replace(/_/g, " "),
        credentials:       author.credentials,
        degrees:           author.degrees,
        areasOfExpertise:  author.areas_of_expertise,
        yearsExperience:   author.years_experience,
        orcidId:           author.orcid_id,
        googleScholarUrl:  author.google_scholar_url,
        linkedinUrl:       author.linkedin_url,
        personalWebsite:   author.personal_website,
      })] : []),
    ].filter(Boolean) as Record<string, unknown>[];

    useMeta({
      title:       post.value.title,
      description: post.value.excerpt ?? "",
      image:       post.value.featured_image?.meta?.download_url,
      url:         window.location.href,
      type:        "article",
      publishedAt: post.value.meta.first_published_at ?? undefined,
      author:      author?.name,
      schemas,
    });
  } catch {
    notFound.value = true;
  } finally {
    isLoading.value = false;
  }
}

function fmtDate(v: string) {
  return new Intl.DateTimeFormat("en", { dateStyle: "long" }).format(new Date(v));
}

onMounted(load);
watch(() => route.params.slug, load);
</script>

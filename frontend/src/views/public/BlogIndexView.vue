<template>
  <div class="min-h-screen bg-slate-50">

    <!-- Hero -->
    <div class="bg-white border-b border-slate-200 px-6 py-16">
      <div class="mx-auto max-w-4xl">
        <p class="mb-2 text-xs font-semibold uppercase tracking-wider text-berry">The blog</p>
        <h1 class="text-4xl font-extrabold text-ink">Guides, tips, and academic insights</h1>
        <p class="mt-3 max-w-2xl text-lg text-graphite">
          Expert writing advice, citation guides, and academic success strategies from our team.
        </p>
      </div>
    </div>

    <div class="mx-auto max-w-6xl px-6 py-12">

      <!-- Loading -->
      <div v-if="isLoading" class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 animate-pulse">
        <div v-for="n in 6" :key="n" class="rounded-xl border border-slate-200 bg-white overflow-hidden">
          <div class="h-48 bg-slate-200" />
          <div class="p-5 space-y-3">
            <div class="h-3 w-20 rounded bg-slate-200" />
            <div class="h-5 w-full rounded bg-slate-200" />
            <div class="h-3 w-3/4 rounded bg-slate-100" />
          </div>
        </div>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="py-20 text-center">
        <p class="text-sm text-graphite">{{ error }}</p>
      </div>

      <template v-else>
        <!-- Post grid -->
        <div v-if="posts.length" class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <RouterLink
            v-for="post in posts"
            :key="post.id"
            :to="`/blog/${post.meta.slug}`"
            class="group flex flex-col overflow-hidden rounded-xl border border-slate-200 bg-white transition-all hover:border-slate-300 hover:shadow-md"
          >
            <!-- Featured image -->
            <div class="h-48 overflow-hidden bg-slate-100">
              <img
                v-if="post.featured_image?.meta?.download_url"
                :src="post.featured_image.meta.download_url"
                :alt="post.title"
                class="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                loading="lazy"
              />
              <div v-else class="flex h-full items-center justify-center">
                <BookOpen class="size-10 text-slate-300" />
              </div>
            </div>

            <div class="flex flex-1 flex-col p-5">
              <!-- Category -->
              <span
                v-if="post.category"
                class="mb-2 inline-flex w-fit rounded-full bg-berry/10 px-2.5 py-0.5 text-xs font-semibold text-berry"
              >
                {{ post.category.name }}
              </span>

              <h2 class="flex-1 text-base font-bold leading-snug text-ink group-hover:text-berry transition-colors">
                {{ post.title }}
              </h2>

              <p v-if="post.excerpt" class="mt-2 line-clamp-2 text-sm text-graphite">
                {{ post.excerpt }}
              </p>

              <div class="mt-4 flex items-center gap-2 text-xs text-graphite">
                <span v-if="post.primary_author">{{ post.primary_author.name }}</span>
                <span v-if="post.primary_author && post.reading_time">·</span>
                <span v-if="post.reading_time">{{ post.reading_time }} min read</span>
                <span v-if="post.meta.first_published_at" class="ml-auto">
                  {{ fmtDate(post.meta.first_published_at) }}
                </span>
              </div>
            </div>
          </RouterLink>
        </div>

        <!-- Empty -->
        <div v-else class="py-24 text-center">
          <BookOpen class="mx-auto mb-4 size-12 text-slate-300" />
          <p class="font-semibold text-ink">No articles published yet.</p>
          <p class="mt-1 text-sm text-graphite">Check back soon.</p>
        </div>

        <!-- Pagination -->
        <div v-if="totalCount > pageSize" class="mt-12 flex items-center justify-center gap-3">
          <button
            class="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-graphite hover:bg-slate-100 disabled:opacity-40"
            :disabled="page === 1"
            @click="navigate(-1)"
          >← Previous</button>
          <span class="text-sm text-graphite">Page {{ page }} of {{ totalPages }}</span>
          <button
            class="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-graphite hover:bg-slate-100 disabled:opacity-40"
            :disabled="page >= totalPages"
            @click="navigate(1)"
          >Next →</button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { RouterLink, useRoute, useRouter } from "vue-router";
import { BookOpen } from "@lucide/vue";
import { cmsApi, type BlogPostSummary } from "@/api/cms";
import { useMeta, webPageSchema } from "@/composables/useMeta";

const route  = useRoute();
const router = useRouter();

const pageSize  = 12;
const page      = ref(Number(route.query.page ?? 1));
const posts     = ref<BlogPostSummary[]>([]);
const totalCount = ref(0);
const isLoading  = ref(true);
const error      = ref("");

const totalPages = computed(() => Math.ceil(totalCount.value / pageSize));

useMeta({
  title: "Blog — Academic Writing Guides & Tips",
  description: "Expert guides on essay writing, research papers, citations, and academic success strategies.",
  type: "website",
  schema: webPageSchema({
    title: "Blog",
    description: "Academic writing guides and tips",
    url: window.location.href,
  }),
});

async function load() {
  isLoading.value = true;
  error.value = "";
  try {
    const { data } = await cmsApi.blogPosts({
      limit: pageSize,
      offset: (page.value - 1) * pageSize,
    });
    posts.value      = data.items;
    totalCount.value = data.meta.total_count;
  } catch {
    error.value = "Could not load articles. Please try again.";
  } finally {
    isLoading.value = false;
  }
}

function navigate(dir: number) {
  page.value += dir;
  router.replace({ query: { page: page.value > 1 ? page.value : undefined } });
}

function fmtDate(v: string) {
  return new Intl.DateTimeFormat("en", { dateStyle: "medium" }).format(new Date(v));
}

onMounted(load);
watch(page, load);
</script>

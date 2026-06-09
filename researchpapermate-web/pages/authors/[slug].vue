<script setup lang="ts">
const route = useRoute()
const slug = route.params.slug as string

const { getByAuthor } = useBlog()
const posts = getByAuthor(slug)
// Prefer author resolved from their posts; fall back to the AUTHORS registry
// so profiles render even when a writer has no static seed posts yet.
const author = posts[0]?.author ?? getAuthorBySlug(slug)

if (!author) {
  throw createError({ statusCode: 404, message: 'Author not found' })
}

const ROLE_BADGE: Record<string, string> = {
  'Senior Writer':         'bg-brand-100 text-brand-700',
  'Subject Matter Expert': 'bg-amber-100 text-amber-700',
  'Writer':                'bg-slate-100 text-slate-600',
  'Editor':                'bg-violet-100 text-violet-700',
  'Clinical Reviewer':     'bg-emerald-100 text-emerald-700',
}

const initials = author.name.split(' ').map((w: string) => w[0]).slice(0, 2).join('')

function fmtDate(d: string) {
  return new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}

useSeoMeta({
  title: `${author.name} — ${author.role} | ResearchPaperMate`,
  description: author.bio,
  ogTitle: author.name,
  ogDescription: author.bio,
})

useHead({
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'Person',
      name: author.name,
      honorificSuffix: author.credentials,
      description: author.bio,
      url: `https://researchpapermate.com/authors/${author.slug}`,
      ...(author.orcid ? { sameAs: [`https://orcid.org/${author.orcid}`] } : {}),
    }),
  }],
})
</script>

<template>
  <div class="min-h-screen bg-white">

    <!-- ── Profile header ─────────────────────────────────────────── -->
    <section class="border-b border-slate-100 bg-slate-50 px-6 py-14">
      <div class="mx-auto max-w-3xl">
        <NuxtLink href="/authors" class="mb-6 inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800">
          ← All authors
        </NuxtLink>

        <div class="flex flex-col gap-8 sm:flex-row sm:items-start">
          <!-- Avatar -->
          <div class="relative shrink-0 self-start">
            <div class="flex h-28 w-28 items-center justify-center rounded-2xl bg-brand-100 text-4xl font-bold text-brand-700 ring-2 ring-white shadow-sm">
              {{ initials }}
            </div>
            <!-- Verified dot -->
            <span
              v-if="author.orcid || author.scholar"
              class="absolute -bottom-1.5 -right-1.5 flex h-6 w-6 items-center justify-center rounded-full bg-emerald-500 ring-2 ring-white"
              title="Verified credentials"
            >
              <svg class="h-3 w-3 text-white" fill="none" viewBox="0 0 12 12" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2 6l3 3 5-5"/>
              </svg>
            </span>
          </div>

          <!-- Identity -->
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <h1 class="font-serif text-3xl font-bold text-slate-900">{{ author.name }}</h1>
              <span
                class="rounded-full px-2.5 py-0.5 text-xs font-semibold"
                :class="ROLE_BADGE[author.role] ?? 'bg-slate-100 text-slate-600'"
              >
                {{ author.role }}
              </span>
            </div>

            <p class="mt-1 text-sm font-semibold text-slate-500">{{ author.credentials }}</p>

            <p class="mt-3 leading-7 text-slate-600">{{ author.bio }}</p>

            <!-- Verified credential pills -->
            <div class="mt-4 flex flex-wrap gap-2">
              <a
                v-if="author.orcid"
                :href="`https://orcid.org/${author.orcid}`"
                target="_blank" rel="noreferrer"
                class="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700 hover:bg-emerald-100 transition-colors"
              >
                <span class="font-bold">iD</span> ORCID
              </a>
              <a
                v-if="author.scholar"
                :href="author.scholar"
                target="_blank" rel="noreferrer"
                class="inline-flex items-center gap-1 rounded-full border border-blue-200 bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700 hover:bg-blue-100 transition-colors"
              >
                Google Scholar
              </a>
              <a
                v-if="author.linkedin"
                :href="author.linkedin"
                target="_blank" rel="noreferrer"
                class="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold text-slate-600 hover:bg-slate-50 transition-colors"
              >
                LinkedIn
              </a>
              <a
                v-if="author.twitter"
                :href="`https://twitter.com/${author.twitter.replace('@','')}`"
                target="_blank" rel="noreferrer"
                class="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold text-slate-600 hover:bg-slate-50 transition-colors"
              >
                @{{ author.twitter.replace('@','') }}
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ── Articles ───────────────────────────────────────────────── -->
    <div class="mx-auto max-w-3xl px-6 py-10">
      <div class="mb-6 flex items-center justify-between">
        <h2 class="font-serif text-xl font-bold text-slate-900">
          Articles by {{ author.name.split(' ')[0] }}
        </h2>
        <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-500">
          {{ posts.length }} {{ posts.length === 1 ? 'article' : 'articles' }}
        </span>
      </div>

      <div v-if="posts.length" class="space-y-4">
        <NuxtLink
          v-for="post in posts"
          :key="post.slug"
          :href="`/blog/${post.slug}`"
          class="group flex gap-4 rounded-xl border border-slate-200 bg-white p-4 transition-all hover:border-brand-200 hover:shadow-sm"
        >
          <!-- Category dot + info -->
          <div class="flex min-w-0 flex-1 flex-col justify-between gap-1">
            <div>
              <span class="mb-1.5 inline-flex rounded-full bg-brand-50 px-2.5 py-0.5 text-xs font-semibold text-brand-700">
                {{ post.category }}
              </span>
              <p class="font-semibold leading-snug text-slate-900 transition-colors group-hover:text-brand-700 line-clamp-2">
                {{ post.title }}
              </p>
              <p class="mt-1 text-sm leading-5 text-slate-500 line-clamp-2">{{ post.excerpt }}</p>
            </div>
            <div class="flex items-center gap-3 text-xs text-slate-400">
              <time>{{ fmtDate(post.date) }}</time>
              <span>·</span>
              <span>{{ post.readTime }}</span>
            </div>
          </div>
          <span class="mt-1 shrink-0 text-xs font-semibold text-brand-600 opacity-0 transition-opacity group-hover:opacity-100">
            Read →
          </span>
        </NuxtLink>
      </div>

      <div v-else class="py-16 text-center">
        <p class="text-slate-500">No articles yet.</p>
      </div>
    </div>

  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>

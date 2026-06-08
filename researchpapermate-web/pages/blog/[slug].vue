<script setup lang="ts">
const route = useRoute()
const { getBySlug, getAll } = useBlog()

const post = getBySlug(route.params.slug as string)

if (!post) {
  throw createError({ statusCode: 404, message: 'Post not found' })
}

const related = getAll()
  .filter(p => p.slug !== post.slug && p.category === post.category)
  .slice(0, 3)

const app = useAppUrl()

useSeoMeta({
  title: post.title,
  description: post.excerpt,
  ogTitle: post.title,
  ogDescription: post.excerpt,
  articlePublishedTime: post.date,
})

useHead({
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'Article',
      headline: post.title,
      description: post.excerpt,
      datePublished: post.date,
      author: { '@type': 'Organization', name: 'ResearchPaperMate' },
      publisher: { '@type': 'Organization', name: 'ResearchPaperMate', url: 'https://researchpapermate.com' },
    }),
  }],
})
</script>

<template>
  <div class="section">
    <div class="mx-auto max-w-3xl">
      <!-- Back -->
      <NuxtLink href="/blog" class="mb-8 inline-flex items-center gap-1 text-sm text-brand-600 hover:underline">
        ← Back to blog
      </NuxtLink>

      <!-- Meta -->
      <div class="mb-4 flex flex-wrap items-center gap-3">
        <span class="rounded-full bg-brand-50 px-3 py-1 text-xs font-medium text-brand-700">
          {{ post.category }}
        </span>
        <span class="text-xs text-slate-400">{{ post.readTime }}</span>
        <time class="text-xs text-slate-400">
          {{ new Date(post.date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) }}
        </time>
      </div>

      <h1 class="font-serif text-3xl font-bold leading-tight text-slate-900 sm:text-4xl">
        {{ post.title }}
      </h1>
      <p class="mt-4 text-lg text-slate-600 leading-relaxed">{{ post.excerpt }}</p>

      <!-- Body -->
      <div class="prose prose-slate prose-lg mt-10 max-w-none
                  prose-headings:font-serif prose-headings:font-bold
                  prose-a:text-brand-600 prose-a:no-underline hover:prose-a:underline
                  prose-strong:text-slate-900"
        v-html="post.body"
      />

      <!-- CTA box -->
      <div class="mt-12 rounded-2xl bg-brand-900 p-8 text-center">
        <h2 class="font-serif text-2xl font-bold text-white">Need help with your paper?</h2>
        <p class="mt-3 text-brand-200">
          Our expert writers cover 100+ subjects. Get yours written from $15/page.
        </p>
        <NuxtLink to="/register" class="btn-primary mt-6 bg-white text-brand-700 hover:bg-brand-50 px-8 py-3">
          Place an order
        </NuxtLink>
      </div>
    </div>

    <!-- Related posts -->
    <div v-if="related.length" class="mx-auto mt-16 max-w-3xl">
      <h2 class="mb-6 font-serif text-xl font-bold text-slate-900">More on {{ post.category }}</h2>
      <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <NuxtLink
          v-for="r in related"
          :key="r.slug"
          :href="`/blog/${r.slug}`"
          class="card group"
        >
          <span class="mb-2 block text-xs text-slate-400">{{ r.readTime }}</span>
          <h3 class="font-semibold leading-snug text-slate-900 group-hover:text-brand-700 transition-colors">
            {{ r.title }}
          </h3>
          <p class="mt-2 text-xs text-slate-400 line-clamp-2">{{ r.excerpt }}</p>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

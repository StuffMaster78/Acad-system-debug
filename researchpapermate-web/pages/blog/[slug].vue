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
    <div class="grid gap-10 lg:grid-cols-[1fr_300px]">

      <!-- Left: article content -->
      <div class="min-w-0">
        <!-- Back link -->
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

        <!-- Article body -->
        <div
          class="prose prose-slate prose-lg mt-10 max-w-none
                 prose-headings:font-serif prose-headings:font-bold
                 prose-a:text-brand-600 prose-a:no-underline hover:prose-a:underline
                 prose-strong:text-slate-900"
          v-html="post.body"
        />

        <!-- End-of-article CTA -->
        <div class="mt-12 rounded-2xl bg-brand-900 p-8">
          <div class="sm:flex sm:items-center sm:justify-between sm:gap-8">
            <div>
              <h2 class="font-serif text-2xl font-bold text-white">Need help with your paper?</h2>
              <p class="mt-2 text-brand-200 leading-relaxed">
                Our expert writers cover 100+ subjects — from essays to dissertations. Human-written, plagiarism-free, from $15/page.
              </p>
              <ul class="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-sm text-brand-300">
                <li class="flex items-center gap-1"><span class="text-green-400">✓</span> Grade or money back</li>
                <li class="flex items-center gap-1"><span class="text-green-400">✓</span> Zero AI content</li>
                <li class="flex items-center gap-1"><span class="text-green-400">✓</span> 2-hour minimum turnaround</li>
              </ul>
            </div>
            <NuxtLink
              to="/order"
              class="mt-6 block shrink-0 rounded-xl bg-white px-8 py-3 text-center text-sm font-bold text-brand-700 hover:bg-brand-50 transition-colors sm:mt-0"
            >
              Place an order
            </NuxtLink>
          </div>
        </div>

        <!-- Related posts -->
        <div v-if="related.length" class="mt-16">
          <h2 class="mb-6 font-serif text-xl font-bold text-slate-900">More on {{ post.category }}</h2>
          <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <NuxtLink
              v-for="r in related"
              :key="r.slug"
              :href="`/blog/${r.slug}`"
              class="card group flex flex-col transition-shadow hover:shadow-md hover:border-brand-200"
            >
              <div class="mb-2 flex items-center gap-2">
                <span class="rounded-full bg-brand-50 px-2 py-0.5 text-xs font-medium text-brand-700">
                  {{ r.category }}
                </span>
                <span class="text-xs text-slate-400">{{ r.readTime }}</span>
              </div>
              <h3 class="flex-1 font-semibold leading-snug text-slate-900 transition-colors group-hover:text-brand-700">
                {{ r.title }}
              </h3>
              <p class="mt-2 line-clamp-2 text-xs text-slate-500 leading-relaxed">{{ r.excerpt }}</p>
              <div class="mt-4 flex items-center justify-between border-t border-slate-100 pt-3">
                <time class="text-xs text-slate-400">
                  {{ new Date(r.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) }}
                </time>
                <span class="text-xs font-semibold text-brand-600 group-hover:underline">Read article →</span>
              </div>
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- Right: sticky sidebar -->
      <div class="lg:sticky lg:top-24 lg:self-start">
        <BlogSidebar />
      </div>

    </div>
  </div>
</template>

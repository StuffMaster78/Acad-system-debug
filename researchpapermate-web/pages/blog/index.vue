<script setup lang="ts">
const { getAll } = useBlog()
const posts = getAll()

const categories = [...new Set(posts.map(p => p.category))]
const activeCategory = ref<string | null>(null)

const filtered = computed(() =>
  activeCategory.value ? posts.filter(p => p.category === activeCategory.value) : posts
)

useSeoMeta({
  title: 'Blog — Academic Writing Guides',
  description: 'Expert guides on research papers, essays, dissertations, outlines, and academic writing — from the ResearchPaperMate team.',
})
</script>

<template>
  <div>
    <section class="bg-gradient-to-br from-brand-900 to-brand-700 py-16 text-center">
      <div class="section py-0">
        <h1 class="font-serif text-4xl font-bold text-white sm:text-5xl">Academic Writing Blog</h1>
        <p class="mx-auto mt-4 max-w-2xl text-lg text-brand-100">
          Practical guides on research papers, essays, dissertations, and every other academic writing challenge.
        </p>
      </div>
    </section>

    <div class="section">
      <!-- Category filter -->
      <div class="mb-8 flex flex-wrap gap-2">
        <button
          class="rounded-full px-4 py-1.5 text-sm font-medium transition-colors"
          :class="activeCategory === null ? 'bg-brand-700 text-white' : 'bg-slate-100 text-slate-600 hover:bg-brand-50'"
          @click="activeCategory = null"
        >
          All
        </button>
        <button
          v-for="cat in categories"
          :key="cat"
          class="rounded-full px-4 py-1.5 text-sm font-medium transition-colors"
          :class="activeCategory === cat ? 'bg-brand-700 text-white' : 'bg-slate-100 text-slate-600 hover:bg-brand-50'"
          @click="activeCategory = cat"
        >
          {{ cat }}
        </button>
      </div>

      <div class="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
        <NuxtLink
          v-for="post in filtered"
          :key="post.slug"
          :href="`/blog/${post.slug}`"
          class="card group flex flex-col"
        >
          <!-- Category + read time -->
          <div class="mb-3 flex items-center gap-2">
            <span class="rounded-full bg-brand-50 px-2.5 py-0.5 text-xs font-medium text-brand-700">
              {{ post.category }}
            </span>
            <span class="text-xs text-slate-400">{{ post.readTime }}</span>
          </div>

          <h2 class="flex-1 font-serif text-lg font-bold leading-snug text-slate-900 group-hover:text-brand-700 transition-colors">
            {{ post.title }}
          </h2>
          <p class="mt-3 text-sm text-slate-500 leading-relaxed line-clamp-3">{{ post.excerpt }}</p>

          <div class="mt-4 flex items-center justify-between border-t border-slate-100 pt-4">
            <time class="text-xs text-slate-400">
              {{ new Date(post.date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' }) }}
            </time>
            <span class="text-xs font-medium text-brand-600 group-hover:underline">Read →</span>
          </div>
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

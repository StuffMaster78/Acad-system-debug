<script setup lang="ts">
import type { BlogAuthor } from '~/composables/useBlog'

const { getAll } = useBlog()

// Derive unique authors from posts — respects category→author mapping
const authorMap = new Map<string, BlogAuthor>()
getAll().forEach(p => {
  if (p.author && !authorMap.has(p.author.slug)) {
    authorMap.set(p.author.slug, p.author)
  }
})
const authors = [...authorMap.values()]

const ROLE_BADGE: Record<string, string> = {
  'Senior Writer':         'bg-brand-100 text-brand-700',
  'Subject Matter Expert': 'bg-amber-100 text-amber-700',
  'Writer':                'bg-slate-100 text-slate-600',
  'Editor':                'bg-violet-100 text-violet-700',
  'Clinical Reviewer':     'bg-emerald-100 text-emerald-700',
}

useSeoMeta({
  title: 'Our Nurse Writers & Editors — NurseMyGrade',
  description: 'Meet the BSN, MSN, and DNP nurses who write and review every article on NurseMyGrade.',
  ogImageWidth:  1200,
  ogImageHeight: 630,
  twitterCard:   'summary_large_image',
})

useHead({
  script: [{
    type: 'application/ld+json',
    innerHTML: JSON.stringify({
      '@context': 'https://schema.org',
      '@type': 'ItemList',
      name: 'Editorial Team',
      itemListElement: authors.map((a, i) => ({
        '@type': 'ListItem',
        position: i + 1,
        item: {
          '@type': 'Person',
          name: a.name,
          honorificSuffix: a.credentials,
          description: a.bio,
          url: `https://nursemygrade.com/authors/${a.slug}`,
        },
      })),
    }),
  }],
})
</script>

<template>
  <div class="min-h-screen bg-slate-50">

    <!-- Hero -->
    <section class="border-b border-slate-200 bg-white px-6 py-16">
      <div class="mx-auto max-w-4xl">
        <p class="mb-2 text-xs font-semibold uppercase tracking-wider text-brand-700">Our editorial team</p>
        <h1 class="font-serif text-4xl font-bold text-slate-900 sm:text-5xl">Meet the authors</h1>
        <p class="mt-4 max-w-2xl text-lg leading-relaxed text-slate-500">
          Every article on NurseMyGrade is written by a credentialed nurse — a BSN, MSN, or DNP professional
          with real clinical experience in the subject area, reviewed by a senior nurse editor.
        </p>
        <!-- Human-written assurance -->
        <div class="mt-6 inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-4 py-1.5 text-sm font-semibold text-emerald-700">
          <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
          </svg>
          All content written by humans — zero AI
        </div>
      </div>
    </section>

    <!-- Author grid -->
    <div class="mx-auto max-w-5xl px-6 py-12">
      <div class="grid gap-6 sm:grid-cols-2 lg:grid-cols-2">
        <NuxtLink
          v-for="author in authors"
          :key="author.slug"
          :href="`/authors/${author.slug}`"
          class="group flex gap-5 rounded-2xl border border-slate-200 bg-white p-6 transition-all hover:border-brand-200 hover:shadow-md"
        >
          <!-- Avatar -->
          <div
            class="flex h-16 w-16 shrink-0 items-center justify-center rounded-2xl bg-brand-100 text-xl font-bold text-brand-700 ring-2 ring-white shadow-sm"
          >
            {{ author.name.split(' ').map((w: string) => w[0]).slice(0, 2).join('') }}
          </div>

          <!-- Identity -->
          <div class="min-w-0">
            <div class="flex flex-wrap items-center gap-2">
              <p class="font-bold text-slate-900 transition-colors group-hover:text-brand-700">
                {{ author.name }}
              </p>
              <span
                class="rounded-full px-2 py-0.5 text-[11px] font-semibold"
                :class="ROLE_BADGE[author.role] ?? 'bg-slate-100 text-slate-600'"
              >
                {{ author.role }}
              </span>
            </div>

            <p class="mt-0.5 text-xs font-medium text-slate-500">{{ author.credentials }}</p>
            <p class="mt-2 text-sm leading-5 text-slate-500 line-clamp-2">{{ author.bio }}</p>

            <!-- Verified pills -->
            <div class="mt-3 flex flex-wrap gap-1.5">
              <span v-if="author.orcid" class="rounded-full border border-emerald-200 bg-emerald-50 px-2 py-0.5 text-[11px] font-semibold text-emerald-700">
                <span class="font-bold">iD</span> ORCID
              </span>
              <span v-if="author.scholar" class="rounded-full border border-blue-200 bg-blue-50 px-2 py-0.5 text-[11px] font-semibold text-blue-700">
                Scholar
              </span>
              <span v-if="author.linkedin" class="rounded-full border border-slate-200 bg-white px-2 py-0.5 text-[11px] font-medium text-slate-600">
                LinkedIn
              </span>
            </div>
          </div>
        </NuxtLink>
      </div>
    </div>

  </div>
</template>

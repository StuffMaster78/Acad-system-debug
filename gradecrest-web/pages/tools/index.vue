<script setup lang="ts">
useSeoMeta({
  title: 'Free Academic Writing Tools | EssayManiacs',
  description: 'Free rule-based academic writing tools: citation generator (APA, MLA, Chicago, Harvard, IEEE), thesis generator, outline builder, title page generator, and literature review builder. No sign-up required.',
  ogTitle: 'Free Academic Writing Tools — No Sign-Up Required',
  ogDescription: 'Instant, rule-based tools for citation formatting, thesis statements, research outlines, title pages, and literature reviews.',
})

const tools = [
  {
    href: '/tools/citation-generator',
    title: 'Citation Generator',
    description: 'Format references in APA, MLA, Chicago, Harvard & IEEE in seconds',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25"/></svg>`,
  },
  {
    href: '/tools/thesis-generator',
    title: 'Thesis Statement Generator',
    description: 'Get a strong thesis for argumentative, analytical, and expository essays',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7"><path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10"/></svg>`,
  },
  {
    href: '/tools/outline-generator',
    title: 'Research Paper Outline Generator',
    description: 'Build a complete Roman numeral outline for any paper type',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7"><path stroke-linecap="round" stroke-linejoin="round" d="M8.25 6.75h12M8.25 12h12m-12 5.25h12M3.75 6.75h.007v.008H3.75V6.75zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zM3.75 12h.007v.008H3.75V12zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0zm-.375 5.25h.007v.008H3.75v-.008zm.375 0a.375.375 0 11-.75 0 .375.375 0 01.75 0z"/></svg>`,
  },
  {
    href: '/tools/title-page-generator',
    title: 'Title Page Generator',
    description: 'Format and download a title page in APA, MLA, or Chicago — Word file included',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"/></svg>`,
  },
  {
    href: '/tools/literature-review-builder',
    title: 'Literature Review Builder',
    description: 'Generate a structured lit review template with thematic sections',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75a1.875 1.875 0 010 3.75H5.625a1.875 1.875 0 010-3.75z"/></svg>`,
  },
  {
    href: '/tools/word-counter',
    title: 'Word Counter',
    description: 'Count words, characters, sentences and get reading time instantly',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7"><path stroke-linecap="round" stroke-linejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 01.865-.501 48.172 48.172 0 003.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z"/></svg>`,
  },
  {
    href: '/tools/words-to-pages',
    title: 'Words to Pages Converter',
    description: 'See exactly how many pages your word count fills at any font and spacing',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"/></svg>`,
  },
  {
    href: '/tools/gpa-calculator',
    title: 'GPA Calculator',
    description: 'Calculate your semester and cumulative GPA on a 4.0 scale',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7"><path stroke-linecap="round" stroke-linejoin="round" d="M4.26 10.147a60.438 60.438 0 00-.491 6.347A48.627 48.627 0 0112 20.904a48.627 48.627 0 018.232-4.41 60.46 60.46 0 00-.491-6.347m-15.482 0a50.57 50.57 0 00-2.658-.813A59.905 59.905 0 0112 3.493a59.902 59.902 0 0110.399 5.84c-.896.248-1.783.52-2.658.814m-15.482 0A50.697 50.697 0 0112 13.489a50.702 50.702 0 017.74-3.342M6.75 15a.75.75 0 100-1.5.75.75 0 000 1.5zm0 0v-3.675A55.378 55.378 0 0112 8.443m-7.007 11.55A5.981 5.981 0 006.75 15.75v-1.5"/></svg>`,
  },
  {
    href: '/tools/grade-calculator',
    title: 'Grade Calculator',
    description: 'Find your current grade or what score you need on the final exam',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7"><path stroke-linecap="round" stroke-linejoin="round" d="M15.75 15.75V18m-7.5-6.75h.008v.008H8.25v-.008zm0 2.25h.008v.008H8.25V13.5zm0 2.25h.008v.008H8.25v-.008zm0 2.25h.008v.008H8.25V18zm2.498-6.75h.007v.008h-.007v-.008zm0 2.25h.007v.008h-.007V13.5zm0 2.25h.007v.008h-.007v-.008zm0 2.25h.007v.008h-.007V18zm2.504-6.75h.008v.008h-.008v-.008zm0 2.25h.008v.008h-.008V13.5zm0 2.25h.008v.008h-.008v-.008zm0 2.25h.008v.008h-.008V18zm2.498-6.75h.008v.008h-.008v-.008zm0 2.25h.008v.008h-.008V13.5zM8.25 6h7.5v2.25h-7.5V6zM12 2.25c-1.892 0-3.758.11-5.593.322C5.307 2.7 4.5 3.65 4.5 4.757V19.5a2.25 2.25 0 002.25 2.25h10.5a2.25 2.25 0 002.25-2.25V4.757c0-1.108-.806-2.057-1.907-2.185A48.507 48.507 0 0012 2.25z"/></svg>`,
  },
  {
    href: '/tools/topic-generator',
    title: 'Essay Topic Generator',
    description: 'Get 8 specific essay topic ideas for any subject and essay type',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7"><path stroke-linecap="round" stroke-linejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.517 0c.85.493 1.509 1.333 1.509 2.316V18"/></svg>`,
  },
  {
    href: '/tools/plagiarism-checker',
    title: 'Plagiarism Checker',
    description: 'Detect repeated sentences and phrases in your text before submitting',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z"/></svg>`,
  },
  {
    href: '/tools/research-gap-identifier',
    title: 'Research Gap Identifier',
    description: 'Find your research gap, generate a Chapter 1 gap statement, and build H₀/H₁ hypotheses for your dissertation',
    icon: `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7"><path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 15.803m10.607 0A7.5 7.5 0 0 0 5.196 15.803M13.5 10.5h-6"/></svg>`,
  },
]
</script>

<template>
  <div class="bg-slate-50 min-h-screen">
    <!-- Masthead -->
    <section class="bg-brand-700 text-white py-16 px-4">
      <div class="max-w-4xl mx-auto text-center">
        <p class="text-brand-200 text-sm font-semibold uppercase tracking-widest mb-3">Academic Tools</p>
        <h1 class="text-4xl sm:text-5xl font-extrabold mb-4 leading-tight">Free Academic Writing Tools</h1>
        <p class="text-xl text-brand-100 max-w-xl mx-auto">No sign-up. No AI. Instant results.</p>
      </div>
    </section>

    <!-- Tools grid -->
    <section class="max-w-5xl mx-auto px-4 py-14">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        <NuxtLink
          v-for="tool in tools"
          :key="tool.href"
          :to="tool.href"
          class="group rounded-2xl bg-white border border-slate-100 shadow-sm p-6 flex flex-col gap-4 hover:border-brand-300 hover:shadow-md transition-all"
        >
          <span class="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-brand-50 text-brand-600 group-hover:bg-brand-100 transition-colors" v-html="tool.icon" />
          <div class="flex-1">
            <h2 class="text-base font-bold text-slate-800 mb-1 group-hover:text-brand-700 transition-colors">{{ tool.title }}</h2>
            <p class="text-sm text-slate-500 leading-relaxed">{{ tool.description }}</p>
          </div>
          <span class="text-sm font-semibold text-brand-600 group-hover:text-brand-700 flex items-center gap-1">
            Open tool
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3"/></svg>
          </span>
        </NuxtLink>
      </div>
    </section>

    <!-- Bottom CTA -->
    <section class="max-w-3xl mx-auto px-4 pb-16 text-center">
      <div class="rounded-2xl bg-white border border-slate-100 shadow-sm p-8">
        <h2 class="text-xl font-bold text-slate-800 mb-2">Looking for more help?</h2>
        <p class="text-slate-500 mb-5 text-sm">Our expert writers handle full papers, essays, and dissertations from scratch.</p>
        <NuxtLink to="/order" class="inline-block rounded-xl bg-brand-600 px-7 py-3 text-sm font-bold text-white hover:bg-brand-700 transition-colors">
          Place an order →
        </NuxtLink>
      </div>
    </section>
  </div>
</template>

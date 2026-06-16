<script setup lang="ts">
useSeoMeta({
  title: 'Writer Resources & Blog | Writers Creek',
  description: 'Guides, tips, and resources for Writers Creek writers — academic writing advice, payout information, and platform updates.',
})
</script>

<template>
  <div class="bg-white">

    <!-- Header -->
    <div class="border-b border-slate-100 bg-slate-50 px-4 py-12 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-5xl">
        <Breadcrumbs :items="[{ label: 'Blog' }]" />
        <h1 class="mt-4 text-3xl font-bold text-slate-900 sm:text-4xl">Writer resources</h1>
        <p class="mt-2 text-slate-600">Guides and updates for Writers Creek writers.</p>
      </div>
    </div>

    <!-- Placeholder -->
    <div class="mx-auto max-w-5xl px-4 py-20 text-center sm:px-6 lg:px-8">
      <div class="mx-auto max-w-md">
        <div class="mb-6 flex justify-center">
          <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-100">
            <svg class="h-8 w-8 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/>
            </svg>
          </div>
        </div>
        <h2 class="text-xl font-bold text-slate-900">Articles coming soon</h2>
        <p class="mt-2 text-slate-600">We are preparing writer guides, tips on assignment quality, and payout FAQs. Check back shortly.</p>
        <NuxtLink to="/apply" class="mt-8 inline-flex items-center gap-2 rounded-xl bg-brand-600 px-6 py-3 text-sm font-bold text-white transition-colors hover:bg-brand-700">
          Apply to write while you wait
        </NuxtLink>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
defineProps<{
  publishedAt?: string
  updatedAt?: string
  reviewerName?: string
  reviewerCredentials?: string
}>()

const steps = [
  { icon: 'search',       title: 'Topic identified',            description: 'Topics come from reader requests, keyword research, and real gaps in nursing guidance — not a content calendar.' },
  { icon: 'book-open',    title: 'In-depth research & writing', description: 'A credentialed nurse writer — BSN at minimum, often MSN or DNP — conducts primary and secondary research before writing a single word.' },
  { icon: 'pen-line',     title: 'Strict editorial review',     description: 'A senior editor reviews the draft for clinical accuracy, clarity, and academic integrity. Nurse subject-matter experts verify specialist claims before approval.' },
  { icon: 'check-circle', title: 'Published',                   description: 'Once approved, the article is published with full author attribution and verified nursing credentials.' },
  { icon: 'refresh-cw',  title: 'Tracked & updated',           description: 'Our team actively monitors articles for clinical drift and new nursing guidelines — updating content proactively rather than waiting for readers to report errors.' },
]

function fmtDate(v?: string) {
  if (!v) return ''
  return new Intl.DateTimeFormat('en', { dateStyle: 'long' }).format(new Date(v))
}
</script>

<template>
  <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white">
    <!-- Header -->
    <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 bg-slate-50 px-6 py-4">
      <div class="flex items-center gap-2.5">
        <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-700">
          <svg class="h-4 w-4 text-white" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
        </div>
        <p class="font-semibold text-slate-900">How this article was written</p>
      </div>
      <!-- Human-written badge -->
      <span class="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
        <svg class="h-3 w-3 text-emerald-500" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
        </svg>
        Written by humans, not AI
      </span>
    </div>

    <!-- Steps -->
    <div class="px-6 py-5">
      <ol class="space-y-0">
        <li v-for="(step, i) in steps" :key="step.title" class="relative flex gap-4 pb-5 last:pb-0">
          <!-- Connector -->
          <div v-if="i < steps.length - 1" class="absolute bottom-0 left-[15px] top-8 w-px bg-slate-200" />

          <!-- Icon circle -->
          <div class="relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 border-brand-600 bg-brand-600">
            <Icon :name="step.icon" class="h-3.5 w-3.5 text-white" />
          </div>

          <!-- Content -->
          <div class="min-w-0 pt-1">
            <p class="font-semibold text-slate-900">{{ step.title }}</p>
            <p class="mt-0.5 text-sm leading-5 text-slate-500">{{ step.description }}</p>

            <!-- Dynamic details -->
            <p v-if="i === 2 && reviewerName" class="mt-1 text-xs font-medium text-brand-700">
              Reviewed by {{ reviewerName }}{{ reviewerCredentials ? ` · ${reviewerCredentials}` : '' }}
            </p>
            <p v-if="i === 3 && publishedAt" class="mt-1 text-xs font-medium text-brand-700">
              First published {{ fmtDate(publishedAt) }}
            </p>
            <p v-if="i === 4 && updatedAt" class="mt-1 text-xs font-medium text-brand-700">
              Last updated {{ fmtDate(updatedAt) }}
            </p>
          </div>
        </li>
      </ol>
    </div>

    <!-- No-AI statement -->
    <div class="border-t border-slate-100 bg-slate-50 px-6 py-4">
      <p class="text-xs leading-5 text-slate-500">
        <span class="font-semibold text-slate-800">Our commitment:</span>
        We do not use AI to write our articles. Our active team of credentialed writers works directly with
        authors who double as editors in their respective academic fields — ensuring every article is accurate,
        well-researched, and reviewed before it reaches you.
      </p>
    </div>
  </div>
</template>

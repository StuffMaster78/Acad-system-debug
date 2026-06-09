<script setup lang="ts">
defineProps<{
  publishedAt?: string
  updatedAt?: string
  reviewerName?: string
  reviewerCredentials?: string
}>()

const steps = [
  {
    icon: '🔍',
    title: 'Topic identified',
    description: 'Topics come from reader requests, keyword research, and real gaps in academic guidance — not a content calendar.',
  },
  {
    icon: '📚',
    title: 'In-depth research & writing',
    description: 'A credentialed specialist — often with a postgraduate degree in the subject area — conducts primary and secondary research before writing a single word.',
  },
  {
    icon: '✏️',
    title: 'Strict editorial review',
    description: 'A senior editor reviews the draft for accuracy, clarity, and academic integrity. Subject-matter experts verify specialist claims before approval.',
  },
  {
    icon: '✅',
    title: 'Published',
    description: 'Once approved, the article is published with full author attribution and verified credentials.',
  },
  {
    icon: '🔄',
    title: 'Tracked & updated',
    description: 'Our team actively monitors articles for factual drift and new research — updating content proactively rather than waiting for readers to report errors.',
  },
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
        <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-700 text-sm text-white">
          🛡️
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
          <div class="relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 border-brand-600 bg-brand-600 text-sm leading-none">
            {{ step.icon }}
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

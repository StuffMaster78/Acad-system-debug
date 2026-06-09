<script setup lang="ts">
import type { CmsBlock } from '~/composables/useServiceCms'

defineProps<{ blocks: CmsBlock[] }>()

// ── Block value type helpers ──────────────────────────────────────
type HeadingVal   = { text: string; level: 'h2' | 'h3' | 'h4' }
type ParagraphVal = string
type ListVal      = { items: string[]; style: 'bullet' | 'numbered' }
type ChecklistVal = { title?: string; items: { text: string; checked?: boolean }[] }
type QuoteVal     = { quote: string; author?: string }
type CalloutVal   = { type: 'info' | 'warning' | 'tip' | 'important'; text: string }
type FaqVal       = { question: string; answer: string }
type StatItem     = { value: string; label: string; description?: string }
type StatsVal     = { stats: StatItem[] }
type FeatureItem  = { icon?: string; title: string; description: string }
type FeatureVal   = { title?: string; columns: number; features: FeatureItem[] }
type StepItem     = { title: string; description: string }
type StepsVal     = { title?: string; steps: StepItem[] }
type CtaVal       = { heading: string; subheading?: string; button_text: string; button_url: string }
type DefinitionVal= { term: string; definition: string }
type TimelineItem = { date: string; title: string; description?: string }
type TimelineVal  = { title?: string; entries: TimelineItem[] }
type SampleVal    = { excerpt: string; paper_type?: string; academic_level?: string; title?: string }
type ImageVal     = {
  url?: string
  meta?: { download_url?: string }
  alt_text?: string
  caption?: string
  display?: 'inline' | 'wide' | 'infographic'
}
type AttachmentVal = {
  slug: string
  title: string
  description?: string
  file_format?: string
  file_size_bytes?: number
  page_count?: number
  academic_level?: string
  formatting_style?: string
  gate_type: 'free' | 'email' | 'account' | 'customer' | 'paid'
  price?: string | null
  preview_url?: string
  display_style?: 'card' | 'list' | 'hero' | 'button'
}

const openFaqs = ref<Set<number>>(new Set())
function toggleFaq(i: number) {
  if (openFaqs.value.has(i)) openFaqs.value.delete(i)
  else openFaqs.value.add(i)
}

const CALLOUT_STYLES: Record<string, string> = {
  info:      'border-blue-200 bg-blue-50 text-blue-800',
  tip:       'border-green-200 bg-green-50 text-green-800',
  warning:   'border-amber-200 bg-amber-50 text-amber-800',
  important: 'border-rose-200 bg-rose-50 text-rose-800',
}
</script>

<template>
  <div class="space-y-8">
    <template v-for="block in blocks" :key="block.id">

      <!-- heading -->
      <template v-if="block.type === 'heading'">
        <component
          :is="(block.value as HeadingVal).level || 'h2'"
          class="font-serif font-bold text-slate-900"
          :class="{
            'text-3xl sm:text-4xl': (block.value as HeadingVal).level === 'h2',
            'text-2xl sm:text-3xl': (block.value as HeadingVal).level === 'h3',
            'text-xl':              (block.value as HeadingVal).level === 'h4',
          }"
        >
          {{ (block.value as HeadingVal).text }}
        </component>
      </template>

      <!-- paragraph / richtext -->
      <template v-else-if="block.type === 'paragraph'">
        <div
          class="prose prose-slate prose-lg max-w-none
                 prose-headings:font-serif prose-a:text-brand-600 prose-a:no-underline
                 hover:prose-a:underline prose-strong:text-slate-900"
          v-html="block.value as ParagraphVal"
        />
      </template>

      <!-- list -->
      <template v-else-if="block.type === 'list'">
        <component
          :is="(block.value as ListVal).style === 'numbered' ? 'ol' : 'ul'"
          class="space-y-2 pl-5 text-slate-700"
          :class="(block.value as ListVal).style === 'numbered' ? 'list-decimal' : 'list-disc'"
        >
          <li v-for="item in (block.value as ListVal).items" :key="item"
            class="leading-relaxed" v-html="item" />
        </component>
      </template>

      <!-- checklist -->
      <template v-else-if="block.type === 'checklist'">
        <div class="rounded-2xl border border-brand-100 bg-brand-50/50 p-6">
          <h3 v-if="(block.value as ChecklistVal).title" class="mb-4 font-serif text-xl font-bold text-slate-900">
            {{ (block.value as ChecklistVal).title }}
          </h3>
          <ul class="space-y-3">
            <li v-for="item in (block.value as ChecklistVal).items" :key="item.text"
              class="flex items-start gap-3">
              <Icon name="check-circle" class="mt-0.5 h-5 w-5 shrink-0 text-brand-600" />
              <span class="text-slate-700 leading-relaxed">{{ item.text }}</span>
            </li>
          </ul>
        </div>
      </template>

      <!-- quote -->
      <template v-else-if="block.type === 'quote'">
        <blockquote class="border-l-4 border-brand-300 pl-6 py-1">
          <p class="text-lg italic text-slate-700 leading-relaxed">
            "{{ (block.value as QuoteVal).quote }}"
          </p>
          <footer v-if="(block.value as QuoteVal).author" class="mt-2 text-sm font-semibold text-slate-500">
            — {{ (block.value as QuoteVal).author }}
          </footer>
        </blockquote>
      </template>

      <!-- callout -->
      <template v-else-if="block.type === 'callout'">
        <div class="rounded-xl border p-5 text-sm leading-relaxed"
          :class="CALLOUT_STYLES[(block.value as CalloutVal).type] ?? CALLOUT_STYLES.info">
          <span v-html="(block.value as CalloutVal).text" />
        </div>
      </template>

      <!-- faq — accordion -->
      <template v-else-if="block.type === 'faq'">
        <div class="overflow-hidden rounded-xl border border-slate-200 bg-white">
          <button
            class="flex w-full items-center justify-between gap-4 px-5 py-4 text-left hover:bg-slate-50 transition-colors"
            @click="toggleFaq(blocks.indexOf(block))"
          >
            <span class="font-semibold text-slate-900">{{ (block.value as FaqVal).question }}</span>
            <svg class="h-5 w-5 shrink-0 text-slate-400 transition-transform"
              :class="openFaqs.has(blocks.indexOf(block)) ? 'rotate-180' : ''"
              fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </button>
          <div v-show="openFaqs.has(blocks.indexOf(block))"
            class="border-t border-slate-100 bg-slate-50/50 px-5 py-4 text-sm text-slate-600 leading-relaxed"
            v-html="(block.value as FaqVal).answer" />
        </div>
      </template>

      <!-- stats_highlight -->
      <template v-else-if="block.type === 'stats_highlight'">
        <div class="grid gap-4" :class="`sm:grid-cols-${Math.min((block.value as StatsVal).stats.length, 4)}`">
          <div v-for="stat in (block.value as StatsVal).stats" :key="stat.label"
            class="rounded-2xl border border-brand-100 bg-brand-50 p-5 text-center">
            <div class="text-3xl font-bold text-brand-700">{{ stat.value }}</div>
            <div class="mt-1 font-semibold text-slate-700">{{ stat.label }}</div>
            <div v-if="stat.description" class="mt-1 text-xs text-slate-500">{{ stat.description }}</div>
          </div>
        </div>
      </template>

      <!-- feature_grid -->
      <template v-else-if="block.type === 'feature_grid'">
        <div>
          <h3 v-if="(block.value as FeatureVal).title" class="mb-6 font-serif text-2xl font-bold text-slate-900">
            {{ (block.value as FeatureVal).title }}
          </h3>
          <div class="grid gap-5" :class="(block.value as FeatureVal).columns >= 3 ? 'sm:grid-cols-3' : 'sm:grid-cols-2'">
            <div v-for="feat in (block.value as FeatureVal).features" :key="feat.title"
              class="rounded-xl border border-slate-100 bg-white p-5 shadow-sm">
              <div v-if="feat.icon" class="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-brand-100">
                <Icon :name="feat.icon" class="h-5 w-5 text-brand-600" />
              </div>
              <h4 class="font-semibold text-slate-900">{{ feat.title }}</h4>
              <p class="mt-1.5 text-sm text-slate-500 leading-relaxed">{{ feat.description }}</p>
            </div>
          </div>
        </div>
      </template>

      <!-- how_it_works -->
      <template v-else-if="block.type === 'how_it_works'">
        <div>
          <h3 v-if="(block.value as StepsVal).title" class="mb-6 font-serif text-2xl font-bold text-slate-900">
            {{ (block.value as StepsVal).title }}
          </h3>
          <ol class="space-y-5">
            <li v-for="(step, i) in (block.value as StepsVal).steps" :key="step.title"
              class="flex gap-4">
              <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-700 text-sm font-bold text-white">
                {{ i + 1 }}
              </div>
              <div>
                <h4 class="font-semibold text-slate-900">{{ step.title }}</h4>
                <p class="mt-1 text-sm text-slate-500 leading-relaxed">{{ step.description }}</p>
              </div>
            </li>
          </ol>
        </div>
      </template>

      <!-- cta -->
      <template v-else-if="block.type === 'cta'">
        <div class="rounded-2xl bg-brand-900 px-8 py-8 text-center">
          <h3 class="font-serif text-2xl font-bold text-white">{{ (block.value as CtaVal).heading }}</h3>
          <p v-if="(block.value as CtaVal).subheading" class="mt-3 text-brand-200">
            {{ (block.value as CtaVal).subheading }}
          </p>
          <a :href="(block.value as CtaVal).button_url"
            class="mt-5 inline-block rounded-xl bg-white px-8 py-3 font-bold text-brand-700 hover:bg-brand-50 transition-colors">
            {{ (block.value as CtaVal).button_text }}
          </a>
        </div>
      </template>

      <!-- definition -->
      <template v-else-if="block.type === 'definition'">
        <div class="rounded-xl border border-slate-200 bg-slate-50 p-5">
          <dt class="font-bold text-slate-900">{{ (block.value as DefinitionVal).term }}</dt>
          <dd class="mt-1.5 text-slate-600 leading-relaxed" v-html="(block.value as DefinitionVal).definition" />
        </div>
      </template>

      <!-- timeline -->
      <template v-else-if="block.type === 'timeline'">
        <div>
          <h3 v-if="(block.value as TimelineVal).title" class="mb-5 font-serif text-2xl font-bold text-slate-900">
            {{ (block.value as TimelineVal).title }}
          </h3>
          <div class="space-y-0">
            <div v-for="(entry, i) in (block.value as TimelineVal).entries" :key="entry.date"
              class="flex gap-5 pb-6 last:pb-0">
              <div class="flex flex-col items-center">
                <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-700 text-xs font-bold text-white">
                  {{ i + 1 }}
                </div>
                <div v-if="i < (block.value as TimelineVal).entries.length - 1" class="mt-1 h-full w-0.5 bg-brand-100" />
              </div>
              <div class="pt-0.5 pb-2">
                <p class="text-sm font-bold text-brand-600">{{ entry.date }}</p>
                <h4 class="font-semibold text-slate-900">{{ entry.title }}</h4>
                <p v-if="entry.description" class="mt-1 text-sm text-slate-500">{{ entry.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- sample_excerpt -->
      <template v-else-if="block.type === 'sample_excerpt'">
        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div v-if="(block.value as SampleVal).title" class="mb-3 flex items-center justify-between gap-4">
            <h4 class="font-semibold text-slate-900">{{ (block.value as SampleVal).title }}</h4>
            <div class="flex gap-2">
              <span v-if="(block.value as SampleVal).paper_type"
                class="rounded-full bg-brand-50 px-2.5 py-0.5 text-xs font-medium text-brand-700">
                {{ (block.value as SampleVal).paper_type }}
              </span>
              <span v-if="(block.value as SampleVal).academic_level"
                class="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
                {{ (block.value as SampleVal).academic_level }}
              </span>
            </div>
          </div>
          <div class="prose prose-sm prose-slate max-w-none border-t border-slate-100 pt-4"
            v-html="(block.value as SampleVal).excerpt" />
          <p class="mt-3 text-xs text-slate-400">Sample excerpt only — all work is written fresh to your brief.</p>
        </div>
      </template>

      <!-- image / infographic -->
      <template v-else-if="block.type === 'image'">
        <figure
          :class="(block.value as ImageVal).display === 'wide' || (block.value as ImageVal).display === 'infographic'
            ? '-mx-6 sm:-mx-10'
            : ''"
        >
          <img
            :src="(block.value as ImageVal).url ?? (block.value as ImageVal).meta?.download_url ?? ''"
            :alt="(block.value as ImageVal).alt_text ?? ''"
            loading="lazy"
            :class="[
              'w-full rounded-xl object-cover shadow-sm',
              (block.value as ImageVal).display === 'infographic' ? 'max-h-[600px] object-contain bg-slate-50' : '',
            ]"
          />
          <figcaption
            v-if="(block.value as ImageVal).caption"
            class="mt-2 text-center text-xs italic text-slate-400"
          >
            {{ (block.value as ImageVal).caption }}
          </figcaption>
        </figure>
      </template>

      <!-- attachment / downloadable sample -->
      <template v-else-if="block.type === 'attachment'">
        <ClientOnly>
          <SampleDownload
            :attachment="block.value as AttachmentVal"
            :variant="(block.value as AttachmentVal).display_style === 'hero' ? 'hero'
              : (block.value as AttachmentVal).display_style === 'list' ? 'compact'
              : 'card'"
          />
        </ClientOnly>
      </template>

      <!-- divider -->
      <template v-else-if="block.type === 'divider'">
        <hr class="border-slate-200" />
      </template>

      <!-- fallback: unknown block type — silently skip -->

    </template>
  </div>
</template>

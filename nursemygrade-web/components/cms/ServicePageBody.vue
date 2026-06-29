<script setup lang="ts">
import type { CmsBlock } from '~/composables/useServiceCms'

defineProps<{ blocks: CmsBlock[] }>()

const { getAll: getAllServices } = useServices()
const { getAll: getAllBlogPosts } = useBlog()
const _serviceSlugs = new Set(getAllServices().map(s => s.slug))
const _blogSlugs    = new Set(getAllBlogPosts().map(p => p.slug))
const _fixedRoutes  = new Set([
  'order','pricing','contact','about','faq','blog','services',
  'authors','privacy','terms','refunds','resources','login','register',
])

function _escRe(s: string) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') }
const _siteHost = useRequestURL().hostname

function rewriteLinks(html: string): string {
  if (!html) return html
  const re = new RegExp(`href="https?://${_escRe(_siteHost)}(?::\\d+)?(/[^"]*)"`, 'gi')
  let out = html.replace(re, 'href="$1"')
  out = out.replace(/href="\/([a-z][a-z0-9-]*)\/?"(?=[^>]*>)/g, (_m, slug) => {
    if (_serviceSlugs.has(slug) || _blogSlugs.has(slug) || _fixedRoutes.has(slug))
      return `href="/${slug}"`
    return _m
  })
  out = out.replace(/(<a\s[^>]*href="https?:\/\/[^"]*"[^>]*)>/gi, (m, a) =>
    /target=/i.test(a) ? m : `${a} target="_blank" rel="noopener noreferrer">`)
  return out
}

function cleanHtml(html: string): string {
  return html
    .replace(/<img[^>]*src="(?!https?:\/\/)[^"]*"[^>]*>/gi, '')
    .replace(/(<br\s*\/?>\s*)+(<\/?(p|h[1-6]|ul|ol|li|div|blockquote)[^>]*>)/gi, '$2')
    .replace(/(<\/?(p|h[1-6]|ul|ol|li|div|blockquote)[^>]*>)\s*(<br\s*\/?>)+/gi, '$1')
    .replace(/\r\n|\r/g, '\n').replace(/\t/g, '')
}

// ── type aliases ───────────────────────────────────────────────────────────
type HeadingVal   = { text: string; level: 'h2'|'h3'|'h4'; subtitle?: string }
type ParagraphVal = string
type ListVal      = { items: string[]; style: 'bullet'|'numbered' }
type ChecklistVal = { title?: string; items: { text: string; detail?: string; checked?: boolean }[] }
type QuoteVal     = { quote: string; author?: string }
type CalloutVal   = { type: 'info'|'warning'|'tip'|'important'; text: string }
type FaqVal       = { question: string; answer: string }
type StatItem     = { value: string; label: string; description?: string }
type StatsVal     = { stats: StatItem[]; supporting_text?: string }
type FeatureItem  = { icon?: string; title: string; description: string }
type FeatureVal   = { heading?: string; title?: string; columns?: number; features: FeatureItem[] }
type StepItem     = { step_number?: number; title: string; description: string }
type StepsVal     = { heading?: string; title?: string; steps: StepItem[] }
type CtaVal       = { heading: string; subheading?: string; button_text: string; button_url: string }
type DefinitionVal= { term: string; definition: string }
type TimelineItem = { date: string; title: string; description?: string }
type TimelineVal  = { title?: string; entries: TimelineItem[] }
type SampleVal    = { excerpt: string; paper_type?: string; academic_level?: string; title?: string }
type ImageVal     = { url?: string; meta?: { download_url?: string }; alt_text?: string; caption?: string; display?: string }
type AttachmentVal= { slug: string; title: string; description?: string; gate_type: string; display_style?: string; price?: string|null }

const openFaqs = ref<Set<string>>(new Set())
function toggleFaq(id: string) {
  if (openFaqs.value.has(id)) openFaqs.value.delete(id)
  else openFaqs.value.add(id)
}

const CALLOUT: Record<string, { bar: string; bg: string; text: string; icon: string }> = {
  info:      { bar: 'bg-blue-500',   bg: 'bg-blue-50   border-blue-200',   text: 'text-blue-800',   icon: 'info' },
  tip:       { bar: 'bg-emerald-500',bg: 'bg-emerald-50 border-emerald-200',text: 'text-emerald-800',icon: 'lightbulb' },
  warning:   { bar: 'bg-amber-500',  bg: 'bg-amber-50  border-amber-200',  text: 'text-amber-800',  icon: 'alert-triangle' },
  important: { bar: 'bg-rose-500',   bg: 'bg-rose-50   border-rose-200',   text: 'text-rose-800',   icon: 'alert-circle' },
}
</script>

<template>
  <div class="space-y-10">
    <template v-for="block in blocks" :key="block.id">

      <!-- ── HEADING ─────────────────────────────────────────────────────── -->
      <template v-if="block.type === 'heading'">
        <div class="pt-4 first:pt-0">
          <component
            :is="(block.value as HeadingVal).level || 'h2'"
            class="font-serif font-bold text-slate-900"
            :class="{
              'text-2xl sm:text-3xl': (block.value as HeadingVal).level === 'h2',
              'text-xl sm:text-2xl':  (block.value as HeadingVal).level === 'h3',
              'text-lg':              (block.value as HeadingVal).level === 'h4',
            }"
          >
            {{ (block.value as HeadingVal).text }}
          </component>
          <p v-if="(block.value as HeadingVal).subtitle" class="mt-2 text-slate-500">
            {{ (block.value as HeadingVal).subtitle }}
          </p>
          <div class="mt-3 h-0.5 w-12 rounded-full bg-brand-500" />
        </div>
      </template>

      <!-- ── PARAGRAPH ───────────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'paragraph'">
        <div
          class="prose prose-slate max-w-none
                 prose-p:leading-[1.8] prose-p:text-slate-600
                 prose-a:text-brand-600 prose-a:no-underline hover:prose-a:underline
                 prose-strong:text-slate-800 prose-headings:font-serif"
          v-html="rewriteLinks(cleanHtml(block.value as ParagraphVal))"
        />
      </template>

      <!-- ── STATS — horizontal scroll strip ────────────────────────────── -->
      <template v-else-if="block.type === 'stats_highlight'">
        <div>
          <!-- Scroll strip (hides scrollbar) -->
          <div class="-mx-4 px-4 sm:-mx-6 sm:px-6 lg:mx-0 lg:px-0">
            <div
              class="flex gap-4 overflow-x-auto snap-x snap-mandatory pb-1"
              style="scrollbar-width: none;"
            >
              <div
                v-for="stat in (block.value as StatsVal).stats"
                :key="stat.label"
                class="snap-start shrink-0 w-44 sm:w-52 rounded-2xl
                       border border-brand-100 bg-brand-50 p-5 text-center"
              >
                <div class="text-3xl font-black text-brand-700 leading-none">{{ stat.value }}</div>
                <div class="mt-2 text-sm font-semibold text-slate-700">{{ stat.label }}</div>
                <div v-if="stat.description" class="mt-1 text-xs text-slate-500">{{ stat.description }}</div>
              </div>
            </div>
          </div>
          <p v-if="(block.value as StatsVal).supporting_text" class="mt-3 text-sm text-slate-500 italic">
            {{ (block.value as StatsVal).supporting_text }}
          </p>
        </div>
      </template>

      <!-- ── HOW IT WORKS — horizontal scroll step cards ─────────────────── -->
      <template v-else-if="block.type === 'how_it_works'">
        <div>
          <h3 v-if="(block.value as StepsVal).heading || (block.value as StepsVal).title"
              class="mb-5 font-serif text-xl font-bold text-slate-900">
            {{ (block.value as StepsVal).heading || (block.value as StepsVal).title }}
          </h3>
          <div class="-mx-4 px-4 sm:-mx-6 sm:px-6 lg:mx-0 lg:px-0">
            <div
              class="flex gap-4 overflow-x-auto snap-x snap-mandatory pb-2"
              style="scrollbar-width: none;"
            >
              <div
                v-for="(step, i) in (block.value as StepsVal).steps"
                :key="step.title"
                class="snap-start shrink-0 w-64 sm:w-72
                       rounded-2xl border border-slate-200 bg-white p-6 shadow-sm
                       flex flex-col"
              >
                <!-- Step number -->
                <div class="mb-4 flex h-10 w-10 items-center justify-center rounded-full bg-brand-600 text-sm font-bold text-white">
                  {{ step.step_number ?? (i + 1) }}
                </div>
                <h4 class="font-semibold text-slate-900 leading-snug">{{ step.title }}</h4>
                <p class="mt-2 flex-1 text-sm text-slate-500 leading-relaxed" v-html="step.description" />
              </div>
              <!-- Trailing spacer so last card isn't flush against edge -->
              <div class="shrink-0 w-4" aria-hidden="true" />
            </div>
          </div>
        </div>
      </template>

      <!-- ── FEATURE GRID — horizontal scroll cards ─────────────────────── -->
      <template v-else-if="block.type === 'feature_grid'">
        <div>
          <h3 v-if="(block.value as FeatureVal).heading || (block.value as FeatureVal).title"
              class="mb-5 font-serif text-xl font-bold text-slate-900">
            {{ (block.value as FeatureVal).heading || (block.value as FeatureVal).title }}
          </h3>
          <div class="-mx-4 px-4 sm:-mx-6 sm:px-6 lg:mx-0 lg:px-0">
            <div
              class="flex gap-4 overflow-x-auto snap-x snap-mandatory pb-2"
              style="scrollbar-width: none;"
            >
              <div
                v-for="feat in (block.value as FeatureVal).features"
                :key="feat.title"
                class="snap-start shrink-0 w-56 sm:w-64
                       rounded-2xl border border-slate-200 bg-white p-5 shadow-sm
                       flex flex-col"
              >
                <div v-if="feat.icon" class="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-brand-100">
                  <Icon :name="feat.icon" class="h-5 w-5 text-brand-700" />
                </div>
                <h4 class="font-semibold text-slate-900 leading-snug">{{ feat.title }}</h4>
                <p class="mt-2 flex-1 text-sm text-slate-500 leading-relaxed">{{ feat.description }}</p>
              </div>
              <div class="shrink-0 w-4" aria-hidden="true" />
            </div>
          </div>
        </div>
      </template>

      <!-- ── CHECKLIST — two-column grid with detail text ───────────────── -->
      <template v-else-if="block.type === 'checklist'">
        <div class="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
          <!-- Header band -->
          <div v-if="(block.value as ChecklistVal).title"
               class="flex items-center gap-3 border-b border-slate-100 bg-slate-50 px-6 py-4">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-100">
              <Icon name="check-circle" class="h-4 w-4 text-brand-700" />
            </div>
            <h3 class="font-serif text-lg font-bold text-slate-900">
              {{ (block.value as ChecklistVal).title }}
            </h3>
          </div>
          <!-- Items — two columns on sm+ -->
          <div class="grid gap-px sm:grid-cols-2 bg-slate-100">
            <div
              v-for="item in (block.value as ChecklistVal).items"
              :key="item.text"
              class="flex items-start gap-3 bg-white px-5 py-4"
            >
              <Icon name="check" class="mt-0.5 h-4 w-4 shrink-0 text-brand-600" />
              <div class="min-w-0">
                <p class="text-sm font-medium text-slate-800 leading-snug">{{ item.text }}</p>
                <p v-if="item.detail" class="mt-0.5 text-xs text-slate-500 leading-relaxed">{{ item.detail }}</p>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- ── FAQ — vertically stacked accordion card ─────────────────────── -->
      <template v-else-if="block.type === 'faq'">
        <div class="rounded-xl border border-slate-200 bg-white overflow-hidden">
          <button
            class="flex w-full items-center justify-between gap-4 px-5 py-4 text-left hover:bg-slate-50 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-brand-500"
            :aria-expanded="openFaqs.has(block.id)"
            @click="toggleFaq(block.id)"
          >
            <span class="font-semibold text-slate-900">{{ (block.value as FaqVal).question }}</span>
            <svg class="h-5 w-5 shrink-0 text-slate-400 transition-transform duration-200"
              :class="openFaqs.has(block.id) ? 'rotate-180' : ''"
              fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </button>
          <div
            v-show="openFaqs.has(block.id)"
            class="border-t border-slate-100 bg-slate-50/60 px-5 py-4 text-sm text-slate-600 leading-relaxed prose prose-sm max-w-none"
            v-html="(block.value as FaqVal).answer"
          />
        </div>
      </template>

      <!-- ── QUOTE ───────────────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'quote'">
        <blockquote class="relative rounded-2xl border border-slate-200 bg-white px-8 py-7 shadow-sm">
          <div class="absolute left-6 top-5 text-5xl leading-none text-brand-200 font-serif select-none">&ldquo;</div>
          <p class="relative mt-4 text-lg italic text-slate-700 leading-relaxed">
            {{ (block.value as QuoteVal).quote }}
          </p>
          <footer v-if="(block.value as QuoteVal).author" class="mt-4 text-sm font-semibold text-slate-500">
            — {{ (block.value as QuoteVal).author }}
          </footer>
        </blockquote>
      </template>

      <!-- ── CALLOUT ─────────────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'callout'">
        <div class="flex gap-4 rounded-2xl border p-5"
          :class="(CALLOUT[(block.value as CalloutVal).type] ?? CALLOUT.info).bg">
          <Icon
            :name="(CALLOUT[(block.value as CalloutVal).type] ?? CALLOUT.info).icon"
            class="mt-0.5 h-5 w-5 shrink-0"
            :class="(CALLOUT[(block.value as CalloutVal).type] ?? CALLOUT.info).text"
          />
          <div
            class="text-sm leading-relaxed"
            :class="(CALLOUT[(block.value as CalloutVal).type] ?? CALLOUT.info).text"
            v-html="(block.value as CalloutVal).text"
          />
        </div>
      </template>

      <!-- ── LIST ────────────────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'list'">
        <component
          :is="(block.value as ListVal).style === 'numbered' ? 'ol' : 'ul'"
          class="space-y-2.5 pl-5 text-slate-600"
          :class="(block.value as ListVal).style === 'numbered' ? 'list-decimal' : 'list-disc'"
        >
          <li v-for="item in (block.value as ListVal).items" :key="item"
            class="leading-relaxed" v-html="rewriteLinks(item)" />
        </component>
      </template>

      <!-- ── NUMBERED LIST ───────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'numbered_list'">
        <div>
          <h3 v-if="(block.value as any).heading" class="mb-5 font-serif text-xl font-bold text-slate-900">
            {{ (block.value as any).heading }}
          </h3>
          <ol class="space-y-4">
            <li v-for="(item, i) in (block.value as any).items || []" :key="i"
              class="flex items-start gap-4">
              <span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-brand-600 text-xs font-bold text-white mt-0.5">
                {{ i + 1 }}
              </span>
              <div>
                <p class="font-semibold text-slate-900">{{ item.title }}</p>
                <p v-if="item.description" class="mt-1 text-sm text-slate-500 leading-relaxed" v-html="item.description" />
              </div>
            </li>
          </ol>
        </div>
      </template>

      <!-- ── DEFINITION ──────────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'definition'">
        <div class="rounded-xl border border-slate-200 bg-slate-50 px-5 py-4">
          <dt class="font-bold text-slate-900">{{ (block.value as DefinitionVal).term }}</dt>
          <dd class="mt-1.5 text-sm text-slate-600 leading-relaxed"
            v-html="(block.value as DefinitionVal).definition" />
        </div>
      </template>

      <!-- ── CTA banner ──────────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'cta'">
        <div class="rounded-2xl bg-brand-700 px-8 py-8 text-center shadow">
          <h3 class="font-serif text-2xl font-bold text-white">{{ (block.value as CtaVal).heading }}</h3>
          <p v-if="(block.value as CtaVal).subheading" class="mt-2 text-brand-200 text-sm">
            {{ (block.value as CtaVal).subheading }}
          </p>
          <a :href="(block.value as CtaVal).button_url"
            class="mt-5 inline-block rounded-xl bg-white px-8 py-3 text-sm font-bold text-brand-700 hover:bg-brand-50 transition-colors shadow-sm">
            {{ (block.value as CtaVal).button_text }}
          </a>
        </div>
      </template>

      <!-- ── PRO/CON ─────────────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'pro_con'">
        <div>
          <h3 v-if="(block.value as any).heading" class="mb-4 font-serif text-xl font-bold text-slate-900">
            {{ (block.value as any).heading }}
          </h3>
          <div class="grid gap-4 sm:grid-cols-2">
            <div class="rounded-2xl border border-emerald-200 bg-emerald-50 p-5">
              <p class="mb-3 text-xs font-bold uppercase tracking-wider text-emerald-700">
                {{ (block.value as any).pro_heading || 'Pros' }}
              </p>
              <ul class="space-y-2">
                <li v-for="(pro, i) in (block.value as any).pros || []" :key="i"
                  class="flex items-start gap-2 text-sm text-emerald-900">
                  <Icon name="check-circle" class="h-4 w-4 shrink-0 mt-0.5 text-emerald-600" />
                  {{ pro }}
                </li>
              </ul>
            </div>
            <div class="rounded-2xl border border-red-200 bg-red-50 p-5">
              <p class="mb-3 text-xs font-bold uppercase tracking-wider text-red-700">
                {{ (block.value as any).con_heading || 'Cons' }}
              </p>
              <ul class="space-y-2">
                <li v-for="(con, i) in (block.value as any).cons || []" :key="i"
                  class="flex items-start gap-2 text-sm text-red-900">
                  <Icon name="x-circle" class="h-4 w-4 shrink-0 mt-0.5 text-red-400" />
                  {{ con }}
                </li>
              </ul>
            </div>
          </div>
        </div>
      </template>

      <!-- ── TIMELINE ────────────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'timeline'">
        <div>
          <h3 v-if="(block.value as TimelineVal).title" class="mb-5 font-serif text-xl font-bold text-slate-900">
            {{ (block.value as TimelineVal).title }}
          </h3>
          <div class="relative pl-8 space-y-6 before:absolute before:left-3.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-brand-200">
            <div v-for="(entry, i) in (block.value as TimelineVal).entries" :key="entry.date" class="relative">
              <div class="absolute -left-8 flex h-7 w-7 items-center justify-center rounded-full bg-brand-600 text-[11px] font-bold text-white">
                {{ i + 1 }}
              </div>
              <p class="text-xs font-bold text-brand-600 mb-0.5">{{ entry.date }}</p>
              <h4 class="font-semibold text-slate-900">{{ entry.title }}</h4>
              <p v-if="entry.description" class="mt-1 text-sm text-slate-500">{{ entry.description }}</p>
            </div>
          </div>
        </div>
      </template>

      <!-- ── SAMPLE EXCERPT ──────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'sample_excerpt'">
        <div class="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
          <div class="flex items-center justify-between gap-4 border-b border-slate-100 bg-slate-50 px-6 py-4">
            <h4 class="font-semibold text-slate-900">
              {{ (block.value as SampleVal).title || 'Sample Excerpt' }}
            </h4>
            <div class="flex gap-2">
              <span v-if="(block.value as SampleVal).paper_type"
                class="rounded-full bg-brand-100 px-2.5 py-0.5 text-xs font-medium text-brand-700">
                {{ (block.value as SampleVal).paper_type }}
              </span>
              <span v-if="(block.value as SampleVal).academic_level"
                class="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
                {{ (block.value as SampleVal).academic_level }}
              </span>
            </div>
          </div>
          <div class="max-h-64 overflow-y-auto px-6 py-5">
            <div class="prose prose-sm prose-slate max-w-none" v-html="(block.value as SampleVal).excerpt" />
          </div>
          <p class="border-t border-slate-100 px-6 py-3 text-xs text-slate-400 bg-slate-50">
            Sample excerpt only — all work is written fresh to your brief.
          </p>
        </div>
      </template>

      <!-- ── IMAGE ───────────────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'image'">
        <figure>
          <img
            :src="(block.value as ImageVal).url ?? (block.value as ImageVal).meta?.download_url ?? ''"
            :alt="(block.value as ImageVal).alt_text ?? ''"
            loading="lazy"
            class="w-full rounded-2xl object-cover shadow-sm"
            :class="(block.value as ImageVal).display === 'infographic'
              ? 'max-h-[600px] object-contain bg-slate-50' : ''"
          />
          <figcaption v-if="(block.value as ImageVal).caption"
            class="mt-2 text-center text-xs italic text-slate-400">
            {{ (block.value as ImageVal).caption }}
          </figcaption>
        </figure>
      </template>

      <!-- ── ATTACHMENT ──────────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'attachment'">
        <ClientOnly>
          <SampleDownload
            :attachment="block.value as AttachmentVal"
            :variant="(block.value as AttachmentVal).display_style === 'hero' ? 'hero'
              : (block.value as AttachmentVal).display_style === 'list' ? 'compact' : 'card'"
          />
        </ClientOnly>
      </template>

      <!-- ── CHIPS ───────────────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'chips'">
        <div>
          <p v-if="(block.value as any).heading" class="mb-3 font-semibold text-slate-700">
            {{ (block.value as any).heading }}
          </p>
          <div class="flex flex-wrap gap-2">
            <span v-for="(chip, i) in (block.value as any).items || []" :key="i"
              class="rounded-full border px-3 py-1.5 text-xs font-medium"
              :class="{
                'border-brand-200 bg-brand-50 text-brand-700': !(block.value as any).color || (block.value as any).color === 'brand',
                'border-emerald-200 bg-emerald-50 text-emerald-700': (block.value as any).color === 'green',
                'border-amber-200 bg-amber-50 text-amber-700': (block.value as any).color === 'amber',
                'border-violet-200 bg-violet-50 text-violet-700': (block.value as any).color === 'purple',
                'border-slate-200 bg-slate-50 text-slate-600': (block.value as any).color === 'slate',
              }"
            >{{ chip }}</span>
          </div>
        </div>
      </template>

      <!-- ── DIVIDER ─────────────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'divider'">
        <hr class="border-slate-200" />
      </template>

      <!-- ── TABLE ───────────────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'table'">
        <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <p v-if="(block.value as any).table_caption"
            class="border-b border-slate-100 bg-slate-50 px-4 py-2.5 text-xs font-semibold text-slate-600">
            {{ (block.value as any).table_caption }}
          </p>
          <div class="max-h-[28rem] overflow-x-auto overflow-y-auto">
            <table class="min-w-full text-left text-sm">
              <thead v-if="(block.value as any).first_row_is_table_header && (block.value as any).data?.length" class="sticky top-0 z-10">
                <tr>
                  <th v-for="(cell, ci) in (block.value as any).data[0]" :key="ci"
                    class="whitespace-nowrap bg-brand-50 px-4 py-3 font-semibold text-brand-900 border-b border-brand-100">
                    {{ cell }}
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-100">
                <tr v-for="(row, ri) in (block.value as any).first_row_is_table_header
                  ? ((block.value as any).data || []).slice(1) : ((block.value as any).data || [])"
                  :key="ri" class="hover:bg-slate-50 transition-colors">
                  <td v-for="(cell, ci) in row" :key="ci"
                    class="px-4 py-3 text-slate-600 align-top"
                    :class="ci === 0 && (block.value as any).first_col_is_header
                      ? 'font-semibold text-slate-800' : ''">
                    {{ cell }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>

    </template>
  </div>
</template>

<style scoped>
:deep(a[target="_blank"][href^="http"])::after {
  content: '\2197';
  display: inline-block;
  font-size: 0.65em;
  vertical-align: super;
  margin-left: 0.15em;
  opacity: 0.6;
}
</style>

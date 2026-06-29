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
type HeadingVal      = { text: string; level: 'h2'|'h3'|'h4'; subtitle?: string }
type ParagraphVal    = string
type ListVal         = { items: string[]; style: 'bullet'|'numbered' }
type ChecklistVal    = { title?: string; items: { text: string; detail?: string; checked?: boolean }[] }
type QuoteVal        = { quote: string; author?: string }
type CalloutVal      = { type: 'info'|'warning'|'tip'|'important'; text: string }
type FaqVal          = { question: string; answer: string }
type StatItem        = { value: string; label: string; description?: string }
type StatsVal        = { stats: StatItem[]; supporting_text?: string }
type FeatureItem     = { icon?: string; icon_name?: string; title: string; description: string }
type FeatureVal      = { heading?: string; title?: string; columns?: number; features: FeatureItem[] }
type StepItem        = { step_number?: number; title: string; description: string }
type StepsVal        = { heading?: string; title?: string; steps: StepItem[] }
type CtaVal          = { heading: string; subheading?: string; button_text: string; button_url: string; text?: string; url?: string }
type DefinitionVal   = { term: string; definition: string }
type TimelineItem    = { date?: string; date_label?: string; title: string; description?: string }
type TimelineVal     = { heading?: string; title?: string; entries: TimelineItem[] }
type SampleVal       = { excerpt: string; paper_type?: string; academic_level?: string; title?: string }
type ImageVal        = { url?: string; meta?: { download_url?: string }; alt_text?: string; caption?: string; display?: string }
type AttachmentVal   = { slug: string; title: string; description?: string; gate_type: 'email'|'free'|'account'|'customer'|'paid'; display_style?: string; price?: string|null }
// new block types
type HeroVal         = { headline: string; subheadline?: string; cta_text?: string; cta_url?: string; background_image?: { url: string } }
type TrustStripVal   = { rating_value: number; review_count: number; years_in_business: number; orders_completed: number }
type IconListVal     = { icon: string; style: string; items: string[] }
type HighlightListVal= { style: string; color: string; items: string[] }
type BeforeAfterVal  = { heading?: string; label_before?: string; content_before: string; label_after?: string; content_after: string; caption?: string }
type PricingRow      = { service: string; price: string; turnaround: string }
type PricingTableVal = { heading?: string; rows: PricingRow[] }
type CompRow         = { feature: string; us: string; competitor: string }
type CompTableVal    = { heading?: string; competitor_name?: string; rows: CompRow[] }
type TestimonialItem = { quote: string; author_name: string; author_title?: string; rating: number }
type TestimonialsVal = { heading?: string; testimonials: TestimonialItem[] }
type GuaranteeItem   = { icon_name?: string; title: string; description: string }
type GuaranteesVal   = { heading?: string; guarantees: GuaranteeItem[] }
type BenefitItem     = { title: string; description: string }
type BadgeItem       = { label: string; icon_emoji?: string }
type BenefitsVal     = { heading: string; intro?: string; benefits: BenefitItem[]; badges?: BadgeItem[]; closing_text?: string }
type AuthorReviewVal = { reviewer_name: string; credentials: string; review_date: string; photo?: { url: string }; reviewer_url?: string }
type DisclaimerVal   = { style: string; text: string }
type Dataset         = { label: string; values: string; color?: string }
type ChartVal        = { chart_type: string; title: string; caption?: string; x_labels: string; datasets: Dataset[] }
type EmbedVal        = { embed_url: string; height?: number; caption?: string }
type InternalLinkVal = { page?: { title: string; slug: string; url?: string; description?: string }; custom_title?: string; custom_description?: string }
type CalculatorVal   = { title?: string; subtitle?: string; service_code?: string; cta_text?: string; cta_url?: string; default_pages?: number; default_deadline_hours?: number }

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

const ICON_MAP: Record<string, string> = {
  check: 'check', arrow: 'arrow-right', star: 'star', lightning: 'zap',
  shield: 'shield', dot: 'minus', plus: 'plus', minus: 'minus',
  tick_sphere: 'check', tick_sphere_outline: 'check',
}
function iconListIcon(icon: string): string {
  return ICON_MAP[icon] ?? 'check'
}

const HL_COLORS: Record<string, Record<string, string>> = {
  brand:  { zebra: 'bg-brand-50',   boxed: 'border border-brand-200 bg-brand-50 text-brand-800',   border_left: 'border-brand-500 bg-brand-50/60 text-brand-900',  highlight: 'bg-brand-600 text-white' },
  green:  { zebra: 'bg-emerald-50', boxed: 'border border-emerald-200 bg-emerald-50 text-emerald-800', border_left: 'border-emerald-500 bg-emerald-50 text-emerald-900', highlight: 'bg-emerald-600 text-white' },
  amber:  { zebra: 'bg-amber-50',   boxed: 'border border-amber-200 bg-amber-50 text-amber-800',   border_left: 'border-amber-500 bg-amber-50 text-amber-900',  highlight: 'bg-amber-500 text-white' },
  purple: { zebra: 'bg-violet-50',  boxed: 'border border-violet-200 bg-violet-50 text-violet-800', border_left: 'border-violet-500 bg-violet-50 text-violet-900', highlight: 'bg-violet-600 text-white' },
  slate:  { zebra: 'bg-slate-100',  boxed: 'border border-slate-200 bg-slate-100 text-slate-700',   border_left: 'border-slate-400 bg-slate-50 text-slate-800',   highlight: 'bg-slate-700 text-white' },
}
function hlColor(color: string, variant: string): string {
  return HL_COLORS[color]?.[variant] ?? HL_COLORS.brand[variant] ?? ''
}

function chartBarWidth(chart: ChartVal, dsIdx: number, labelIdx: number): number {
  const all = chart.datasets.flatMap(ds =>
    ds.values.split(',').map(v => parseFloat(v.trim()) || 0)
  )
  const max = Math.max(...all, 1)
  const val = parseFloat((chart.datasets[dsIdx]?.values.split(',')[labelIdx] ?? '0').trim()) || 0
  return Math.round((val / max) * 100)
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

      <!-- ── HERO ───────────────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'hero'">
        <div
          class="relative overflow-hidden rounded-2xl bg-brand-900 px-8 py-14 text-center text-white shadow-lg"
          :style="(block.value as HeroVal).background_image?.url
            ? `background-image:url(${(block.value as HeroVal).background_image!.url});background-size:cover;background-position:center`
            : ''"
        >
          <div v-if="(block.value as HeroVal).background_image?.url"
            class="absolute inset-0 bg-brand-900/70" />
          <div class="relative">
            <h2 class="font-serif text-3xl font-bold leading-snug sm:text-4xl">
              {{ (block.value as HeroVal).headline }}
            </h2>
            <p v-if="(block.value as HeroVal).subheadline"
              class="mx-auto mt-4 max-w-xl text-brand-200 leading-relaxed">
              {{ (block.value as HeroVal).subheadline }}
            </p>
            <a v-if="(block.value as HeroVal).cta_url"
              :href="(block.value as HeroVal).cta_url"
              class="mt-7 inline-block rounded-xl bg-white px-8 py-3.5 text-sm font-bold text-brand-800 shadow hover:bg-brand-50 transition-colors">
              {{ (block.value as HeroVal).cta_text || 'Order Now' }}
            </a>
          </div>
        </div>
      </template>

      <!-- ── TRUST STRIP ─────────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'trust_strip'">
        <div class="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div class="flex flex-col items-center rounded-2xl border border-brand-100 bg-brand-50 py-5 px-3 text-center">
            <div class="text-2xl font-black text-brand-700">
              {{ (block.value as TrustStripVal).rating_value }}<span class="text-brand-400 text-lg">/5</span>
            </div>
            <div class="mt-1 flex gap-0.5">
              <Icon v-for="n in 5" :key="n" name="star"
                class="h-3.5 w-3.5"
                :class="n <= Math.round((block.value as TrustStripVal).rating_value) ? 'text-amber-400' : 'text-slate-300'" />
            </div>
            <p class="mt-1.5 text-xs text-slate-500">Customer rating</p>
          </div>
          <div class="flex flex-col items-center rounded-2xl border border-brand-100 bg-brand-50 py-5 px-3 text-center">
            <div class="text-2xl font-black text-brand-700">
              {{ (block.value as TrustStripVal).review_count.toLocaleString() }}+
            </div>
            <p class="mt-1.5 text-xs text-slate-500">Reviews</p>
          </div>
          <div class="flex flex-col items-center rounded-2xl border border-brand-100 bg-brand-50 py-5 px-3 text-center">
            <div class="text-2xl font-black text-brand-700">
              {{ (block.value as TrustStripVal).years_in_business }}
            </div>
            <p class="mt-1.5 text-xs text-slate-500">Years in business</p>
          </div>
          <div class="flex flex-col items-center rounded-2xl border border-brand-100 bg-brand-50 py-5 px-3 text-center">
            <div class="text-2xl font-black text-brand-700">
              {{ (block.value as TrustStripVal).orders_completed.toLocaleString() }}+
            </div>
            <p class="mt-1.5 text-xs text-slate-500">Orders completed</p>
          </div>
        </div>
      </template>

      <!-- ── ICON LIST ───────────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'icon_list'">
        <div>
          <!-- inline_pills layout -->
          <div v-if="(block.value as IconListVal).style === 'inline_pills'"
            class="flex flex-wrap gap-2">
            <span v-for="(item, i) in (block.value as IconListVal).items" :key="i"
              class="flex items-center gap-1.5 rounded-full border border-brand-200 bg-brand-50 px-3 py-1.5 text-sm text-brand-800"
              v-html="item" />
          </div>
          <!-- grid_3 layout -->
          <ul v-else-if="(block.value as IconListVal).style === 'grid_3'"
            class="grid gap-3 sm:grid-cols-3">
            <li v-for="(item, i) in (block.value as IconListVal).items" :key="i"
              class="flex items-start gap-2.5 rounded-xl border border-slate-200 bg-white p-3.5 shadow-sm">
              <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-100 mt-0.5">
                <Icon v-if="(block.value as IconListVal).icon !== 'number_auto'" :name="iconListIcon((block.value as IconListVal).icon)" class="h-3.5 w-3.5 text-brand-700" />
                <span v-else class="text-[11px] font-bold text-brand-700">{{ i + 1 }}</span>
              </span>
              <span class="text-sm text-slate-700 leading-relaxed" v-html="item" />
            </li>
          </ul>
          <!-- grid (2-col) layout -->
          <ul v-else-if="(block.value as IconListVal).style === 'grid'"
            class="grid gap-3 sm:grid-cols-2">
            <li v-for="(item, i) in (block.value as IconListVal).items" :key="i"
              class="flex items-start gap-2.5 rounded-xl border border-slate-200 bg-white p-3.5 shadow-sm">
              <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-100 mt-0.5">
                <Icon v-if="(block.value as IconListVal).icon !== 'number_auto'" :name="iconListIcon((block.value as IconListVal).icon)" class="h-3.5 w-3.5 text-brand-700" />
                <span v-else class="text-[11px] font-bold text-brand-700">{{ i + 1 }}</span>
              </span>
              <span class="text-sm text-slate-700 leading-relaxed" v-html="item" />
            </li>
          </ul>
          <!-- cards layout -->
          <ul v-else-if="(block.value as IconListVal).style === 'cards'"
            class="space-y-2.5">
            <li v-for="(item, i) in (block.value as IconListVal).items" :key="i"
              class="flex items-start gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
              <span class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-brand-100 mt-0.5">
                <Icon v-if="(block.value as IconListVal).icon !== 'number_auto'" :name="iconListIcon((block.value as IconListVal).icon)" class="h-3.5 w-3.5 text-brand-700" />
                <span v-else class="text-[11px] font-bold text-brand-700">{{ i + 1 }}</span>
              </span>
              <span class="text-sm text-slate-700 leading-relaxed" v-html="item" />
            </li>
          </ul>
          <!-- cards_border layout -->
          <ul v-else-if="(block.value as IconListVal).style === 'cards_border'"
            class="space-y-2.5">
            <li v-for="(item, i) in (block.value as IconListVal).items" :key="i"
              class="flex items-start gap-3 border-l-4 border-brand-500 bg-brand-50/50 px-4 py-3 rounded-r-xl">
              <span class="flex h-5 w-5 shrink-0 items-center justify-center mt-0.5">
                <Icon v-if="(block.value as IconListVal).icon !== 'number_auto'" :name="iconListIcon((block.value as IconListVal).icon)" class="h-4 w-4 text-brand-600" />
                <span v-else class="text-xs font-bold text-brand-700">{{ i + 1 }}</span>
              </span>
              <span class="text-sm text-slate-700 leading-relaxed" v-html="item" />
            </li>
          </ul>
          <!-- simple (default) -->
          <ul v-else class="space-y-2.5">
            <li v-for="(item, i) in (block.value as IconListVal).items" :key="i"
              class="flex items-start gap-3">
              <span class="flex h-5 w-5 shrink-0 items-center justify-center mt-0.5">
                <Icon v-if="(block.value as IconListVal).icon !== 'number_auto'" :name="iconListIcon((block.value as IconListVal).icon)" class="h-4 w-4 text-brand-600" />
                <span v-else class="flex h-5 w-5 items-center justify-center rounded-full bg-brand-600 text-[11px] font-bold text-white">{{ i + 1 }}</span>
              </span>
              <span class="text-sm text-slate-700 leading-relaxed" v-html="item" />
            </li>
          </ul>
        </div>
      </template>

      <!-- ── HIGHLIGHT LIST ──────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'highlight_list'">
        <!-- inline_pills variant -->
        <div v-if="(block.value as HighlightListVal).style === 'boxed'"
          class="grid gap-2 sm:grid-cols-2">
          <div v-for="(item, i) in (block.value as HighlightListVal).items" :key="i"
            class="rounded-xl px-4 py-3 text-sm font-medium"
            :class="hlColor((block.value as HighlightListVal).color, 'boxed')"
            v-html="item" />
        </div>
        <div v-else-if="(block.value as HighlightListVal).style === 'border_left'"
          class="space-y-2">
          <div v-for="(item, i) in (block.value as HighlightListVal).items" :key="i"
            class="border-l-4 px-4 py-2.5 text-sm leading-relaxed rounded-r-xl"
            :class="hlColor((block.value as HighlightListVal).color, 'border_left')"
            v-html="item" />
        </div>
        <div v-else-if="(block.value as HighlightListVal).style === 'highlight'"
          class="space-y-2">
          <div v-for="(item, i) in (block.value as HighlightListVal).items" :key="i"
            class="rounded-xl px-5 py-3 text-sm font-medium"
            :class="hlColor((block.value as HighlightListVal).color, 'highlight')"
            v-html="item" />
        </div>
        <!-- zebra (default) -->
        <div v-else class="overflow-hidden rounded-xl border border-slate-200">
          <div v-for="(item, i) in (block.value as HighlightListVal).items" :key="i"
            class="px-5 py-3 text-sm text-slate-700 leading-relaxed"
            :class="i % 2 === 0 ? 'bg-white' : hlColor((block.value as HighlightListVal).color, 'zebra')"
            v-html="item" />
        </div>
      </template>

      <!-- ── BEFORE / AFTER ─────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'before_after'">
        <div>
          <h3 v-if="(block.value as BeforeAfterVal).heading"
            class="mb-4 font-serif text-xl font-bold text-slate-900">
            {{ (block.value as BeforeAfterVal).heading }}
          </h3>
          <div class="grid gap-4 sm:grid-cols-2">
            <div class="rounded-2xl border border-red-200 bg-red-50 overflow-hidden">
              <div class="flex items-center gap-2 border-b border-red-200 bg-red-100 px-4 py-2.5">
                <span class="h-2.5 w-2.5 rounded-full bg-red-400" />
                <span class="text-xs font-bold uppercase tracking-wider text-red-700">
                  {{ (block.value as BeforeAfterVal).label_before || 'Before' }}
                </span>
              </div>
              <div class="px-5 py-4 prose prose-sm prose-red max-w-none text-red-900"
                v-html="(block.value as BeforeAfterVal).content_before" />
            </div>
            <div class="rounded-2xl border border-emerald-200 bg-emerald-50 overflow-hidden">
              <div class="flex items-center gap-2 border-b border-emerald-200 bg-emerald-100 px-4 py-2.5">
                <span class="h-2.5 w-2.5 rounded-full bg-emerald-500" />
                <span class="text-xs font-bold uppercase tracking-wider text-emerald-700">
                  {{ (block.value as BeforeAfterVal).label_after || 'After' }}
                </span>
              </div>
              <div class="px-5 py-4 prose prose-sm prose-emerald max-w-none text-emerald-900"
                v-html="(block.value as BeforeAfterVal).content_after" />
            </div>
          </div>
          <p v-if="(block.value as BeforeAfterVal).caption"
            class="mt-2 text-center text-xs italic text-slate-400">
            {{ (block.value as BeforeAfterVal).caption }}
          </p>
        </div>
      </template>

      <!-- ── PRICING TABLE ──────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'pricing_table'">
        <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div v-if="(block.value as PricingTableVal).heading"
            class="border-b border-slate-100 bg-brand-50 px-6 py-4">
            <h3 class="font-serif text-lg font-bold text-brand-900">
              {{ (block.value as PricingTableVal).heading }}
            </h3>
          </div>
          <table class="min-w-full text-sm">
            <thead>
              <tr class="border-b border-slate-100">
                <th class="px-6 py-3 text-left font-semibold text-slate-600">Service</th>
                <th class="px-6 py-3 text-left font-semibold text-slate-600">Price</th>
                <th class="px-6 py-3 text-left font-semibold text-slate-600">Turnaround</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="(row, i) in (block.value as PricingTableVal).rows" :key="i"
                class="hover:bg-slate-50 transition-colors">
                <td class="px-6 py-3.5 font-medium text-slate-800">{{ row.service }}</td>
                <td class="px-6 py-3.5 font-bold text-brand-700">{{ row.price }}</td>
                <td class="px-6 py-3.5 text-slate-500">{{ row.turnaround }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>

      <!-- ── COMPARISON TABLE ───────────────────────────────────────────── -->
      <template v-else-if="block.type === 'comparison_table'">
        <div class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div class="border-b border-slate-100 bg-brand-50 px-6 py-4">
            <h3 class="font-serif text-lg font-bold text-brand-900">
              {{ (block.value as CompTableVal).heading || 'Why Choose Us' }}
            </h3>
          </div>
          <table class="min-w-full text-sm">
            <thead>
              <tr class="border-b border-slate-100">
                <th class="px-5 py-3 text-left font-semibold text-slate-500 w-2/5">Feature</th>
                <th class="px-5 py-3 text-left font-semibold text-brand-700 w-[30%]">Us</th>
                <th class="px-5 py-3 text-left font-semibold text-slate-400 w-[30%]">
                  {{ (block.value as CompTableVal).competitor_name || 'Others' }}
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="(row, i) in (block.value as CompTableVal).rows" :key="i"
                class="hover:bg-slate-50 transition-colors">
                <td class="px-5 py-3.5 font-medium text-slate-700">{{ row.feature }}</td>
                <td class="px-5 py-3.5">
                  <span class="flex items-center gap-1.5 text-emerald-700 font-medium">
                    <Icon name="check-circle" class="h-4 w-4 shrink-0 text-emerald-500" />
                    {{ row.us }}
                  </span>
                </td>
                <td class="px-5 py-3.5 text-slate-400">{{ row.competitor }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>

      <!-- ── TESTIMONIALS ───────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'testimonials'">
        <div>
          <h3 v-if="(block.value as TestimonialsVal).heading"
            class="mb-5 font-serif text-xl font-bold text-slate-900">
            {{ (block.value as TestimonialsVal).heading }}
          </h3>
          <div class="-mx-4 px-4 sm:-mx-6 sm:px-6 lg:mx-0 lg:px-0">
            <div
              class="flex gap-4 overflow-x-auto snap-x snap-mandatory pb-2"
              style="scrollbar-width: none;">
              <div
                v-for="(t, i) in (block.value as TestimonialsVal).testimonials"
                :key="i"
                class="snap-start shrink-0 w-72 sm:w-80 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm flex flex-col">
                <div class="flex gap-0.5 mb-3">
                  <Icon v-for="n in 5" :key="n" name="star"
                    class="h-4 w-4"
                    :class="n <= t.rating ? 'text-amber-400' : 'text-slate-200'" />
                </div>
                <div class="flex-1 prose prose-sm prose-slate max-w-none text-slate-600 leading-relaxed"
                  v-html="t.quote" />
                <div class="mt-4 pt-4 border-t border-slate-100">
                  <p class="font-semibold text-slate-800 text-sm">{{ t.author_name }}</p>
                  <p v-if="t.author_title" class="text-xs text-slate-400 mt-0.5">{{ t.author_title }}</p>
                </div>
              </div>
              <div class="shrink-0 w-4" aria-hidden="true" />
            </div>
          </div>
        </div>
      </template>

      <!-- ── GUARANTEES ─────────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'guarantees'">
        <div>
          <h3 v-if="(block.value as GuaranteesVal).heading"
            class="mb-5 font-serif text-xl font-bold text-slate-900">
            {{ (block.value as GuaranteesVal).heading }}
          </h3>
          <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div
              v-for="(g, i) in (block.value as GuaranteesVal).guarantees"
              :key="i"
              class="flex items-start gap-4 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
              <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-100">
                <Icon :name="g.icon_name || 'shield-check'" class="h-5 w-5 text-brand-700" />
              </div>
              <div>
                <p class="font-semibold text-slate-900 leading-snug">{{ g.title }}</p>
                <p class="mt-1 text-sm text-slate-500 leading-relaxed">{{ g.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- ── BENEFITS SECTION ───────────────────────────────────────────── -->
      <template v-else-if="block.type === 'benefits_section'">
        <div class="rounded-2xl border border-brand-100 bg-brand-50 p-7">
          <h3 class="font-serif text-2xl font-bold text-brand-900">
            {{ (block.value as BenefitsVal).heading }}
          </h3>
          <p v-if="(block.value as BenefitsVal).intro"
            class="mt-2 text-slate-600">
            {{ (block.value as BenefitsVal).intro }}
          </p>
          <ul class="mt-5 space-y-3">
            <li
              v-for="(b, i) in (block.value as BenefitsVal).benefits"
              :key="i"
              class="flex items-start gap-3">
              <Icon name="check-circle" class="mt-0.5 h-5 w-5 shrink-0 text-brand-600" />
              <div>
                <p class="font-semibold text-slate-900">{{ b.title }}</p>
                <p v-if="b.description" class="mt-0.5 text-sm text-slate-600">{{ b.description }}</p>
              </div>
            </li>
          </ul>
          <!-- Badge row -->
          <div v-if="(block.value as BenefitsVal).badges?.length"
            class="-mx-2 mt-6 flex gap-3 overflow-x-auto pb-1" style="scrollbar-width: none;">
            <span
              v-for="(badge, i) in (block.value as BenefitsVal).badges"
              :key="i"
              class="shrink-0 flex items-center gap-1.5 rounded-full border border-brand-200 bg-white px-3.5 py-1.5 text-xs font-medium text-brand-800">
              <span v-if="badge.icon_emoji">{{ badge.icon_emoji }}</span>
              {{ badge.label }}
            </span>
          </div>
          <p v-if="(block.value as BenefitsVal).closing_text"
            class="mt-4 text-xs text-slate-500 italic">
            {{ (block.value as BenefitsVal).closing_text }}
          </p>
        </div>
      </template>

      <!-- ── AUTHOR REVIEW BADGE ────────────────────────────────────────── -->
      <template v-else-if="block.type === 'author_review'">
        <div class="flex items-start gap-4 rounded-2xl border border-slate-200 bg-slate-50 px-6 py-5">
          <img
            v-if="(block.value as AuthorReviewVal).photo?.url"
            :src="(block.value as AuthorReviewVal).photo!.url"
            :alt="(block.value as AuthorReviewVal).reviewer_name"
            class="h-14 w-14 rounded-full object-cover shrink-0 border-2 border-white shadow-sm"
          />
          <div v-else
            class="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-brand-100 border-2 border-white shadow-sm">
            <Icon name="user-check" class="h-6 w-6 text-brand-700" />
          </div>
          <div class="min-w-0">
            <p class="font-bold text-slate-900">{{ (block.value as AuthorReviewVal).reviewer_name }}</p>
            <p class="text-sm text-slate-500">{{ (block.value as AuthorReviewVal).credentials }}</p>
            <p class="mt-1 text-xs text-slate-400">
              Reviewed {{ (block.value as AuthorReviewVal).review_date }}
            </p>
            <a v-if="(block.value as AuthorReviewVal).reviewer_url"
              :href="(block.value as AuthorReviewVal).reviewer_url"
              target="_blank" rel="noopener noreferrer"
              class="mt-1.5 inline-flex items-center gap-1 text-xs font-medium text-brand-600 hover:underline">
              View profile
              <Icon name="external-link" class="h-3 w-3" />
            </a>
          </div>
          <div class="ml-auto shrink-0 hidden sm:flex items-center gap-1.5 rounded-full bg-brand-100 px-3 py-1.5">
            <Icon name="check-circle" class="h-4 w-4 text-brand-700" />
            <span class="text-xs font-semibold text-brand-800">Expert reviewed</span>
          </div>
        </div>
      </template>

      <!-- ── DISCLAIMER ─────────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'disclaimer'">
        <div class="flex gap-3 rounded-xl border px-5 py-4"
          :class="{
            'border-amber-200 bg-amber-50': (block.value as DisclaimerVal).style === 'academic_integrity',
            'border-slate-200 bg-slate-50': (block.value as DisclaimerVal).style === 'copyright' || (block.value as DisclaimerVal).style === 'general',
            'border-red-200 bg-red-50':     (block.value as DisclaimerVal).style === 'medical',
          }">
          <Icon name="shield"
            class="mt-0.5 h-5 w-5 shrink-0"
            :class="{
              'text-amber-600': (block.value as DisclaimerVal).style === 'academic_integrity',
              'text-slate-500': (block.value as DisclaimerVal).style === 'copyright' || (block.value as DisclaimerVal).style === 'general',
              'text-red-500':   (block.value as DisclaimerVal).style === 'medical',
            }"
          />
          <div
            class="prose prose-sm max-w-none text-slate-700"
            v-html="(block.value as DisclaimerVal).text"
          />
        </div>
      </template>

      <!-- ── CHART (CSS bars) ───────────────────────────────────────────── -->
      <template v-else-if="block.type === 'chart'">
        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <h4 class="font-serif text-lg font-bold text-slate-900 mb-4">
            {{ (block.value as ChartVal).title }}
          </h4>
          <div class="space-y-3">
            <template v-for="(ds, di) in (block.value as ChartVal).datasets" :key="di">
              <div v-for="(label, li) in (block.value as ChartVal).x_labels.split(',')" :key="li">
                <div class="flex items-center gap-3 text-sm">
                  <span class="w-28 shrink-0 text-xs text-slate-500 text-right truncate">{{ label.trim() }}</span>
                  <div class="flex-1 rounded-full bg-slate-100 h-5 overflow-hidden">
                    <div
                      class="h-full rounded-full transition-all"
                      :style="{
                        width: chartBarWidth((block.value as ChartVal), di, li) + '%',
                        background: ds.color || '#4f46e5',
                      }"
                    />
                  </div>
                  <span class="w-10 shrink-0 text-xs font-semibold text-slate-700">
                    {{ (ds.values.split(',')[li] ?? '').trim() }}
                  </span>
                </div>
              </div>
              <p v-if="(block.value as ChartVal).datasets.length > 1" class="text-xs text-slate-400 pl-[7.5rem]">
                {{ ds.label }}
              </p>
            </template>
          </div>
          <p v-if="(block.value as ChartVal).caption"
            class="mt-4 text-xs italic text-slate-400 text-center">
            {{ (block.value as ChartVal).caption }}
          </p>
        </div>
      </template>

      <!-- ── EMBED (iframe) ─────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'embed'">
        <div>
          <div class="overflow-hidden rounded-2xl border border-slate-200 bg-slate-50 shadow-sm">
            <ClientOnly>
              <iframe
                :src="(block.value as EmbedVal).embed_url"
                :height="(block.value as EmbedVal).height || 480"
                class="w-full border-0"
                loading="lazy"
                sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
                title="Embedded content"
              />
            </ClientOnly>
          </div>
          <p v-if="(block.value as EmbedVal).caption"
            class="mt-2 text-center text-xs italic text-slate-400">
            {{ (block.value as EmbedVal).caption }}
          </p>
        </div>
      </template>

      <!-- ── INTERNAL LINK CARD ─────────────────────────────────────────── -->
      <template v-else-if="block.type === 'internal_link'">
        <NuxtLink
          v-if="(block.value as InternalLinkVal).page"
          :to="`/${(block.value as InternalLinkVal).page!.slug}`"
          class="group flex items-start gap-4 rounded-2xl border border-slate-200 bg-white px-6 py-5 shadow-sm hover:border-brand-300 hover:shadow-md transition-all no-underline"
        >
          <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-100 group-hover:bg-brand-200 transition-colors">
            <Icon name="arrow-right" class="h-5 w-5 text-brand-700" />
          </div>
          <div class="min-w-0">
            <p class="font-semibold text-slate-900 group-hover:text-brand-700 transition-colors leading-snug">
              {{ (block.value as InternalLinkVal).custom_title || (block.value as InternalLinkVal).page!.title }}
            </p>
            <p v-if="(block.value as InternalLinkVal).custom_description || (block.value as InternalLinkVal).page!.description"
              class="mt-1 text-sm text-slate-500 line-clamp-2">
              {{ (block.value as InternalLinkVal).custom_description || (block.value as InternalLinkVal).page!.description }}
            </p>
          </div>
          <Icon name="chevron-right" class="ml-auto shrink-0 h-5 w-5 text-slate-300 group-hover:text-brand-400 transition-colors mt-0.5" />
        </NuxtLink>
      </template>

      <!-- ── CALCULATOR ─────────────────────────────────────────────────── -->
      <template v-else-if="block.type === 'calculator'">
        <div class="rounded-2xl border border-brand-200 bg-gradient-to-br from-brand-50 to-brand-100 px-8 py-8 shadow-sm">
          <div class="flex items-center gap-3 mb-4">
            <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-600">
              <Icon name="calculator" class="h-5 w-5 text-white" />
            </div>
            <div>
              <h3 class="font-serif text-xl font-bold text-brand-900">
                {{ (block.value as CalculatorVal).title || 'Get Your Instant Price' }}
              </h3>
              <p v-if="(block.value as CalculatorVal).subtitle" class="text-sm text-brand-700">
                {{ (block.value as CalculatorVal).subtitle }}
              </p>
            </div>
          </div>
          <div class="flex flex-col sm:flex-row gap-3 sm:items-center text-sm text-brand-700 mb-6">
            <span v-if="(block.value as CalculatorVal).default_pages" class="flex items-center gap-1.5">
              <Icon name="file-text" class="h-4 w-4" />
              {{ (block.value as CalculatorVal).default_pages }} page{{ (block.value as CalculatorVal).default_pages! > 1 ? 's' : '' }}
            </span>
            <span v-if="(block.value as CalculatorVal).default_deadline_hours" class="flex items-center gap-1.5">
              <Icon name="clock" class="h-4 w-4" />
              {{ (block.value as CalculatorVal).default_deadline_hours }}h deadline
            </span>
          </div>
          <a
            :href="(block.value as CalculatorVal).cta_url || '/order'"
            class="inline-block rounded-xl bg-brand-600 px-8 py-3.5 text-sm font-bold text-white hover:bg-brand-700 transition-colors shadow">
            {{ (block.value as CalculatorVal).cta_text || 'Calculate My Price' }}
          </a>
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

<script setup lang="ts">
import type { CmsBlock } from '~/composables/useServiceCms'

defineProps<{ blocks: CmsBlock[] }>()

const { getAll: getAllServices } = useServices()
const { getAll: getAllBlogPosts } = useBlog()
const _serviceSlugs = new Set(getAllServices().map(s => s.slug))
const _blogSlugs    = new Set(getAllBlogPosts().map(p => p.slug))

const _fixedRoutes = new Set([
  'order', 'pricing', 'contact', 'about', 'faq', 'blog', 'services',
  'authors', 'privacy', 'terms', 'refunds', 'resources', 'login', 'register',
])

function _escRe(s: string) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') }
const _siteHost = useRequestURL().hostname

function rewriteLinks(html: string): string {
  if (!html) return html
  const sameOriginRe = new RegExp(
    `href="https?://${_escRe(_siteHost)}(?::\\d+)?(/[^"]*)"`, 'gi',
  )
  let out = html.replace(sameOriginRe, 'href="$1"')
  out = out.replace(/href="\/([a-z][a-z0-9-]*)\/?"(?=[^>]*>)/g, (_match, slug) => {
    if (_serviceSlugs.has(slug)) return `href="/services/${slug}"`
    if (_blogSlugs.has(slug))    return `href="/blog/${slug}"`
    if (_fixedRoutes.has(slug))  return `href="/${slug}"`
    return _match
  })
  out = out.replace(/(<a\s[^>]*href="https?:\/\/[^"]*"[^>]*)>/gi, (m, attrs) =>
    /target=/i.test(attrs) ? m : `${attrs} target="_blank" rel="noopener noreferrer">`
  )
  return out
}

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
// ── New block type aliases ────────────────────────────────────────
type HeroVal         = { headline: string; subheadline?: string; cta_text?: string; cta_url?: string; background_image?: { url: string } }
type TrustStripVal   = { rating_value: number; review_count: number; years_in_business: number; orders_completed: number }
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
type InternalLinkVal = { page?: { title: string; slug: string; description?: string }; custom_title?: string; custom_description?: string }
type CalculatorVal   = { title?: string; subtitle?: string; service_code?: string; cta_text?: string; cta_url?: string; default_pages?: number; default_deadline_hours?: number }

const openFaqs = ref<Set<number>>(new Set())
function toggleFaq(i: number) {
  if (openFaqs.value.has(i)) openFaqs.value.delete(i)
  else openFaqs.value.add(i)
}

function cleanHtml(html: string): string {
  return html
    .replace(/<img[^>]*src="(?!https?:\/\/)[^"]*"[^>]*>/gi, '')
    .replace(/(<br\s*\/?>\s*)+(<\/?(p|h[1-6]|ul|ol|li|div|blockquote)[^>]*>)/gi, '$2')
    .replace(/(<\/?(p|h[1-6]|ul|ol|li|div|blockquote)[^>]*>)\s*(<br\s*\/?>)+/gi, '$1')
    .replace(/\r\n|\r/g, '\n')
    .replace(/\t/g, '')
}

const CALLOUT_STYLES: Record<string, string> = {
  info:      'border-blue-200 bg-blue-50 text-blue-800',
  tip:       'border-green-200 bg-green-50 text-green-800',
  warning:   'border-amber-200 bg-amber-50 text-amber-800',
  important: 'border-rose-200 bg-rose-50 text-rose-800',
}

const HL_COLORS: Record<string, Record<string, string>> = {
  brand:  { zebra: 'bg-claret-50',     boxed: 'border border-claret-200 bg-claret-50 text-claret-800',   border_left: 'border-claret-500 bg-claret-50/60 text-claret-900',  highlight: 'bg-claret-700 text-white' },
  green:  { zebra: 'bg-emerald-50',    boxed: 'border border-emerald-200 bg-emerald-50 text-emerald-800', border_left: 'border-emerald-500 bg-emerald-50 text-emerald-900',   highlight: 'bg-emerald-600 text-white' },
  amber:  { zebra: 'bg-amber-50',      boxed: 'border border-amber-200 bg-amber-50 text-amber-800',       border_left: 'border-amber-500 bg-amber-50 text-amber-900',         highlight: 'bg-amber-500 text-white' },
  purple: { zebra: 'bg-violet-50',     boxed: 'border border-violet-200 bg-violet-50 text-violet-800',    border_left: 'border-violet-500 bg-violet-50 text-violet-900',      highlight: 'bg-violet-600 text-white' },
  slate:  { zebra: 'bg-parchment-100', boxed: 'border border-parchment-300 bg-parchment-100 text-claret-800', border_left: 'border-claret-400 bg-parchment-50 text-claret-800', highlight: 'bg-claret-900 text-white' },
}
function hlColor(color: string, variant: string): string {
  return HL_COLORS[color]?.[variant] ?? HL_COLORS.brand[variant] ?? ''
}

function chartBarWidth(chart: ChartVal, dsIdx: number, labelIdx: number): number {
  const all = chart.datasets.flatMap(ds => ds.values.split(',').map(v => parseFloat(v.trim()) || 0))
  const max = Math.max(...all, 1)
  const val = parseFloat((chart.datasets[dsIdx]?.values.split(',')[labelIdx] ?? '0').trim()) || 0
  return Math.round((val / max) * 100)
}
</script>

<template>
  <div>
    <template v-for="block in blocks" :key="block.id">

      <!-- heading — inline, flows with column -->
      <template v-if="block.type === 'heading'">
        <div class="mb-6 break-inside-avoid">
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
        </div>
      </template>

      <!-- paragraph / richtext — no break-inside-avoid so CSS columns can flow naturally -->
      <template v-else-if="block.type === 'paragraph'">
        <div
          class="prose prose-slate max-w-none
                 prose-headings:font-serif prose-headings:break-after-avoid
                 prose-a:text-amber-700 prose-a:underline prose-a:decoration-amber-300 hover:prose-a:decoration-amber-600
                 prose-strong:text-slate-900 prose-p:mb-4 prose-p:leading-relaxed"
          v-html="rewriteLinks(cleanHtml(block.value as ParagraphVal))"
        />
      </template>

      <!-- list -->
      <template v-else-if="block.type === 'list'">
        <div class="mb-8 break-inside-avoid">
          <component
            :is="(block.value as ListVal).style === 'numbered' ? 'ol' : 'ul'"
            class="space-y-2 pl-5 text-slate-700"
            :class="(block.value as ListVal).style === 'numbered' ? 'list-decimal' : 'list-disc'"
          >
            <li v-for="item in (block.value as ListVal).items" :key="item"
              class="leading-relaxed" v-html="rewriteLinks(item)" />
          </component>
        </div>
      </template>

      <!-- checklist -->
      <template v-else-if="block.type === 'checklist'">
        <div class="mb-8 break-inside-avoid">
          <div class="rounded-2xl border border-claret-200 bg-parchment-50 p-6">
            <h3 v-if="(block.value as ChecklistVal).title" class="mb-4 font-serif text-xl font-bold text-slate-900">
              {{ (block.value as ChecklistVal).title }}
            </h3>
            <ul class="space-y-3">
              <li v-for="item in (block.value as ChecklistVal).items" :key="item.text"
                class="flex items-start gap-3">
                <Icon name="check-circle" class="mt-0.5 h-5 w-5 shrink-0 text-amber-700" />
                <span class="text-slate-700 leading-relaxed">{{ item.text }}</span>
              </li>
            </ul>
          </div>
        </div>
      </template>

      <!-- icon_list -->
      <template v-else-if="block.type === 'icon_list'">
        <div class="mb-8 break-inside-avoid">
        <div v-if="(block.value as any).style === 'grid'" class="grid gap-3 sm:grid-cols-2">
          <div v-for="(item, i) in (block.value as any).items || []" :key="i"
            class="flex items-start gap-3 rounded-xl border border-parchment-200 bg-parchment-50 p-4">
            <Icon :name="({ check: 'check-circle', arrow: 'arrow-right', star: 'star', lightning: 'zap', shield: 'shield-check', dot: 'check' } as Record<string, string>)[(block.value as any).icon] || 'check-circle'"
              class="h-4 w-4 shrink-0 mt-0.5 text-amber-700" />
            <div class="text-sm text-slate-700 leading-relaxed" v-html="rewriteLinks(item)" />
          </div>
        </div>
        <div v-else-if="(block.value as any).style === 'cards'" class="space-y-2">
          <div v-for="(item, i) in (block.value as any).items || []" :key="i"
            class="flex items-start gap-3 rounded-xl border border-parchment-200 bg-parchment-50 px-5 py-4">
            <Icon :name="({ check: 'check-circle', arrow: 'arrow-right', star: 'star', lightning: 'zap', shield: 'shield-check', dot: 'check' } as Record<string, string>)[(block.value as any).icon] || 'check-circle'"
              class="h-4 w-4 shrink-0 mt-0.5 text-amber-700" />
            <div class="text-sm text-slate-700 leading-relaxed" v-html="rewriteLinks(item)" />
          </div>
        </div>
        <ul v-else class="space-y-3">
          <li v-for="(item, i) in (block.value as any).items || []" :key="i" class="flex items-start gap-3 text-sm text-slate-700">
            <Icon :name="({ check: 'check-circle', arrow: 'arrow-right', star: 'star', lightning: 'zap', shield: 'shield-check', dot: 'check' } as Record<string, string>)[(block.value as any).icon] || 'check-circle'"
              class="h-4 w-4 shrink-0 mt-0.5 text-amber-700" />
            <div class="leading-relaxed" v-html="rewriteLinks(item)" />
          </li>
        </ul>
        </div>
      </template>

      <!-- numbered_list -->
      <template v-else-if="block.type === 'numbered_list'">
        <div class="mb-8 break-inside-avoid">
        <div class="space-y-4">
          <h3 v-if="(block.value as any).heading" class="font-serif text-xl font-bold text-claret-900">{{ (block.value as any).heading }}</h3>
          <ol v-if="(block.value as any).style === 'steps'" class="space-y-0">
            <li v-for="(item, i) in (block.value as any).items || []" :key="i" class="flex gap-4">
              <div class="flex flex-col items-center">
                <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-claret-700 text-xs font-bold text-white z-10">{{ i + 1 }}</span>
                <div v-if="i < ((block.value as any).items || []).length - 1" class="w-0.5 flex-1 bg-claret-200 my-1" />
              </div>
              <div class="pb-6 min-w-0">
                <p class="text-sm font-semibold text-claret-900">{{ item.title }}</p>
                <div v-if="item.description" class="mt-1 text-sm text-slate-600 leading-relaxed" v-html="item.description" />
              </div>
            </li>
          </ol>
          <ol v-else-if="(block.value as any).style === 'counter'" class="space-y-6">
            <li v-for="(item, i) in (block.value as any).items || []" :key="i" class="flex gap-4 items-start">
              <span class="text-5xl font-black text-claret-100 leading-none w-14 shrink-0 text-right tabular-nums select-none">{{ String(i + 1).padStart(2, '0') }}</span>
              <div class="pt-1 min-w-0">
                <p class="text-sm font-semibold text-claret-900">{{ item.title }}</p>
                <div v-if="item.description" class="mt-1 text-sm text-slate-600 leading-relaxed" v-html="item.description" />
              </div>
            </li>
          </ol>
          <ol v-else class="space-y-4">
            <li v-for="(item, i) in (block.value as any).items || []" :key="i" class="flex gap-4 items-start">
              <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 border-amber-600 text-xs font-bold text-amber-700 mt-0.5">{{ i + 1 }}</span>
              <div class="min-w-0">
                <p class="text-sm font-semibold text-claret-900">{{ item.title }}</p>
                <div v-if="item.description" class="mt-1 text-sm text-slate-600 leading-relaxed" v-html="item.description" />
              </div>
            </li>
          </ol>
        </div>
        </div>
      </template>

      <!-- pro_con — wide: spans both columns -->
      <template v-else-if="block.type === 'pro_con'">
        <div class="mb-8 [column-span:all]">
        <div class="space-y-4">
          <h3 v-if="(block.value as any).heading" class="font-serif text-xl font-bold text-claret-900">{{ (block.value as any).heading }}</h3>
          <div class="grid gap-4 sm:grid-cols-2">
            <div class="rounded-2xl border border-emerald-200 bg-emerald-50 p-5">
              <p class="mb-3 text-sm font-bold text-emerald-800">{{ (block.value as any).pro_heading || 'Pros' }}</p>
              <ul class="space-y-2">
                <li v-for="(pro, i) in (block.value as any).pros || []" :key="i" class="flex items-start gap-2 text-sm text-emerald-900">
                  <Icon name="check-circle" class="h-4 w-4 shrink-0 mt-0.5 text-emerald-600" />{{ pro }}
                </li>
              </ul>
            </div>
            <div class="rounded-2xl border border-red-200 bg-red-50 p-5">
              <p class="mb-3 text-sm font-bold text-red-800">{{ (block.value as any).con_heading || 'Cons' }}</p>
              <ul class="space-y-2">
                <li v-for="(con, i) in (block.value as any).cons || []" :key="i" class="flex items-start gap-2 text-sm text-red-900">
                  <Icon name="zap" class="h-4 w-4 shrink-0 mt-0.5 text-red-400" />{{ con }}
                </li>
              </ul>
            </div>
          </div>
        </div>
        </div>
      </template>

      <!-- chips -->
      <template v-else-if="block.type === 'chips'">
        <div class="mb-8 break-inside-avoid">
        <div class="space-y-3">
          <p v-if="(block.value as any).heading" class="font-semibold text-claret-900">{{ (block.value as any).heading }}</p>
          <div class="flex flex-wrap gap-2">
            <span v-for="(chip, i) in (block.value as any).items || []" :key="i"
              class="rounded-full border px-3 py-1.5 text-xs font-medium"
              :class="{
                'border-claret-200 bg-claret-50 text-claret-700': (block.value as any).color === 'brand' || !(block.value as any).color,
                'border-emerald-200 bg-emerald-50 text-emerald-700': (block.value as any).color === 'green',
                'border-amber-200 bg-amber-50 text-amber-700': (block.value as any).color === 'amber',
                'border-violet-200 bg-violet-50 text-violet-700': (block.value as any).color === 'purple',
                'border-slate-200 bg-slate-50 text-slate-600': (block.value as any).color === 'slate',
              }"
            >{{ chip }}</span>
          </div>
        </div>
        </div>
      </template>

      <!-- quote -->
      <template v-else-if="block.type === 'quote'">
        <div class="mb-8 break-inside-avoid">
        <blockquote class="border-l-4 border-claret-200 pl-6 py-1">
          <p class="text-lg italic text-slate-700 leading-relaxed">
            "{{ (block.value as QuoteVal).quote }}"
          </p>
          <footer v-if="(block.value as QuoteVal).author" class="mt-2 text-sm font-semibold text-slate-500">
            — {{ (block.value as QuoteVal).author }}
          </footer>
        </blockquote>
        </div>
      </template>

      <!-- callout -->
      <template v-else-if="block.type === 'callout'">
        <div class="mb-8 break-inside-avoid">
        <div class="rounded-xl border p-5 text-sm leading-relaxed"
          :class="CALLOUT_STYLES[(block.value as CalloutVal).type] ?? CALLOUT_STYLES.info">
          <span v-html="(block.value as CalloutVal).text" />
        </div>
        </div>
      </template>

      <!-- faq — accordion -->
      <template v-else-if="block.type === 'faq'">
        <div class="mb-4 break-inside-avoid">
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
        </div>
      </template>

      <!-- stats_highlight — wide: spans both columns -->
      <template v-else-if="block.type === 'stats_highlight'">
        <div class="mb-8 [column-span:all]">
        <div class="grid gap-4" :class="`sm:grid-cols-${Math.min((block.value as StatsVal).stats.length, 4)}`">
          <div v-for="stat in (block.value as StatsVal).stats" :key="stat.label"
            class="rounded-2xl border border-claret-200 bg-claret-900 p-5 text-center">
            <div class="text-3xl font-bold text-amber-700">{{ stat.value }}</div>
            <div class="mt-1 font-semibold text-slate-700">{{ stat.label }}</div>
            <div v-if="stat.description" class="mt-1 text-xs text-slate-500">{{ stat.description }}</div>
          </div>
        </div>
        </div>
      </template>

      <!-- feature_grid — wide: spans both columns -->
      <template v-else-if="block.type === 'feature_grid'">
        <div class="mb-8 [column-span:all]">
        <div>
          <h3 v-if="(block.value as FeatureVal).title" class="mb-6 font-serif text-2xl font-bold text-slate-900">
            {{ (block.value as FeatureVal).title }}
          </h3>
          <div class="grid gap-5" :class="(block.value as FeatureVal).columns >= 3 ? 'sm:grid-cols-3' : 'sm:grid-cols-2'">
            <div v-for="feat in (block.value as FeatureVal).features" :key="feat.title"
              class="rounded-xl border border-slate-100 bg-white p-5 shadow-sm">
              <div v-if="feat.icon" class="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-claret-900">
                <Icon :name="feat.icon" class="h-5 w-5 text-amber-700" />
              </div>
              <h4 class="font-semibold text-slate-900">{{ feat.title }}</h4>
              <p class="mt-1.5 text-sm text-slate-500 leading-relaxed">{{ feat.description }}</p>
            </div>
          </div>
        </div>
        </div>
      </template>

      <!-- how_it_works — wide: spans both columns -->
      <template v-else-if="block.type === 'how_it_works'">
        <div class="mb-8 [column-span:all]">
        <div>
          <h3 v-if="(block.value as StepsVal).title" class="mb-6 font-serif text-2xl font-bold text-slate-900">
            {{ (block.value as StepsVal).title }}
          </h3>
          <ol class="space-y-5">
            <li v-for="(step, i) in (block.value as StepsVal).steps" :key="step.title"
              class="flex gap-4">
              <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-claret-900 text-sm font-bold text-white">
                {{ i + 1 }}
              </div>
              <div>
                <h4 class="font-semibold text-slate-900">{{ step.title }}</h4>
                <p class="mt-1 text-sm text-slate-500 leading-relaxed">{{ step.description }}</p>
              </div>
            </li>
          </ol>
        </div>
        </div>
      </template>

      <!-- cta — wide: spans both columns -->
      <template v-else-if="block.type === 'cta'">
        <div class="mb-8 [column-span:all]">
          <div class="rounded-2xl bg-claret-900 px-8 py-8 text-center">
            <h3 class="font-serif text-2xl font-bold text-white">{{ (block.value as CtaVal).heading }}</h3>
            <p v-if="(block.value as CtaVal).subheading" class="mt-3 text-amber-700">
              {{ (block.value as CtaVal).subheading }}
            </p>
            <a :href="(block.value as CtaVal).button_url"
              class="mt-5 inline-block rounded-xl bg-white px-8 py-3 font-bold text-amber-700 hover:bg-claret-900 transition-colors">
              {{ (block.value as CtaVal).button_text }}
            </a>
          </div>
        </div>
      </template>

      <!-- definition -->
      <template v-else-if="block.type === 'definition'">
        <div class="mb-8 break-inside-avoid">
          <div class="rounded-xl border border-slate-200 bg-slate-50 p-5">
            <dt class="font-bold text-slate-900">{{ (block.value as DefinitionVal).term }}</dt>
            <dd class="mt-1.5 text-slate-600 leading-relaxed" v-html="(block.value as DefinitionVal).definition" />
          </div>
        </div>
      </template>

      <!-- timeline — wide: spans both columns -->
      <template v-else-if="block.type === 'timeline'">
        <div class="mb-8 [column-span:all]">
        <div>
          <h3 v-if="(block.value as TimelineVal).title" class="mb-5 font-serif text-2xl font-bold text-slate-900">
            {{ (block.value as TimelineVal).title }}
          </h3>
          <div class="space-y-0">
            <div v-for="(entry, i) in (block.value as TimelineVal).entries" :key="entry.date"
              class="flex gap-5 pb-6 last:pb-0">
              <div class="flex flex-col items-center">
                <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-claret-900 text-xs font-bold text-white">
                  {{ i + 1 }}
                </div>
                <div v-if="i < (block.value as TimelineVal).entries.length - 1" class="mt-1 h-full w-0.5 bg-claret-900" />
              </div>
              <div class="pt-0.5 pb-2">
                <p class="text-sm font-bold text-amber-700">{{ entry.date }}</p>
                <h4 class="font-semibold text-slate-900">{{ entry.title }}</h4>
                <p v-if="entry.description" class="mt-1 text-sm text-slate-500">{{ entry.description }}</p>
              </div>
            </div>
          </div>
        </div>
        </div>
      </template>

      <!-- sample_excerpt — wide: spans both columns -->
      <template v-else-if="block.type === 'sample_excerpt'">
        <div class="mb-8 [column-span:all]">
        <div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div v-if="(block.value as SampleVal).title" class="mb-3 flex items-center justify-between gap-4">
            <h4 class="font-semibold text-slate-900">{{ (block.value as SampleVal).title }}</h4>
            <div class="flex gap-2">
              <span v-if="(block.value as SampleVal).paper_type"
                class="rounded-full bg-claret-900 px-2.5 py-0.5 text-xs font-medium text-amber-700">
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
        </div>
      </template>

      <!-- image / infographic -->
      <template v-else-if="block.type === 'image'">
        <div
          class="mb-8"
          :class="(block.value as ImageVal).display === 'wide' || (block.value as ImageVal).display === 'infographic'
            ? '[column-span:all]'
            : 'break-inside-avoid'"
        >
        <figure>
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
        </div>
      </template>

      <!-- attachment — wide: spans both columns -->
      <template v-else-if="block.type === 'attachment'">
        <div class="mb-8 [column-span:all]">
        <ClientOnly>
          <SampleDownload
            :attachment="block.value as AttachmentVal"
            :variant="(block.value as AttachmentVal).display_style === 'hero' ? 'hero'
              : (block.value as AttachmentVal).display_style === 'list' ? 'compact'
              : 'card'"
          />
        </ClientOnly>
        </div>
      </template>

      <!-- divider -->
      <template v-else-if="block.type === 'divider'">
        <div class="mb-8 break-inside-avoid">
          <hr class="border-parchment-300" />
        </div>
      </template>

      <!-- table — wide: spans both columns -->
      <template v-else-if="block.type === 'table'">
        <div class="mb-8 [column-span:all]">
        <div class="overflow-hidden rounded-2xl border border-parchment-200 bg-white shadow-sm">
          <p v-if="(block.value as any).table_caption" class="border-b border-parchment-100 bg-parchment-50 px-4 py-2.5 text-xs font-semibold text-claret-700">
            {{ (block.value as any).table_caption }}
          </p>
          <div class="max-h-[28rem] overflow-x-auto overflow-y-auto">
            <table class="min-w-full text-left text-sm">
              <thead v-if="(block.value as any).first_row_is_table_header && (block.value as any).data?.length" class="sticky top-0 z-10">
                <tr>
                  <th v-for="(cell, ci) in (block.value as any).data[0]" :key="ci"
                    class="whitespace-nowrap bg-parchment-100 px-4 py-3 font-semibold text-claret-800 border-b border-parchment-200"
                    :class="ci === 0 && (block.value as any).first_col_is_header ? 'sticky left-0 z-20 bg-parchment-200' : ''">
                    {{ cell }}
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-parchment-100">
                <tr v-for="(row, ri) in ((block.value as any).first_row_is_table_header ? ((block.value as any).data || []).slice(1) : ((block.value as any).data || []))"
                  :key="ri" class="hover:bg-parchment-50 transition-colors">
                  <td v-for="(cell, ci) in row" :key="ci"
                    class="px-4 py-3 text-slate-700 align-top"
                    :class="ci === 0 && (block.value as any).first_col_is_header ? 'sticky left-0 z-10 bg-white font-semibold text-claret-800 border-r border-parchment-100' : ''">
                    {{ cell }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        </div>
      </template>

      <!-- ── NEW BLOCKS ──────────────────────────────────────────────────── -->

      <!-- hero — RPM: split layout — headline left, CTA button right on desktop — wide -->
      <template v-else-if="block.type === 'hero'">
        <div class="mb-8 [column-span:all]">
          <div
            class="relative overflow-hidden rounded-2xl bg-claret-900 px-8 py-12"
            :style="(block.value as HeroVal).background_image?.url
              ? `background-image:url(${(block.value as HeroVal).background_image!.url});background-size:cover;background-position:center`
              : ''"
          >
            <div v-if="(block.value as HeroVal).background_image?.url" class="absolute inset-0 bg-claret-900/80" />
            <div class="relative flex flex-col sm:flex-row sm:items-center sm:justify-between sm:gap-10">
              <div class="flex-1">
                <h2 class="font-serif text-3xl font-bold text-white leading-tight sm:text-4xl">
                  {{ (block.value as HeroVal).headline }}
                </h2>
                <p v-if="(block.value as HeroVal).subheadline" class="mt-3 text-parchment-200 leading-relaxed max-w-lg">
                  {{ (block.value as HeroVal).subheadline }}
                </p>
              </div>
              <div v-if="(block.value as HeroVal).cta_url" class="mt-7 sm:mt-0 sm:shrink-0">
                <a :href="(block.value as HeroVal).cta_url"
                  class="inline-block rounded-xl bg-amber-500 px-8 py-4 text-sm font-bold text-white hover:bg-amber-600 transition-colors shadow">
                  {{ (block.value as HeroVal).cta_text || 'Order Now' }}
                </a>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- trust_strip — RPM: 4-cell grid with metric name above number — wide -->
      <template v-else-if="block.type === 'trust_strip'">
        <div class="mb-8 [column-span:all]">
          <div class="grid grid-cols-2 gap-0 sm:grid-cols-4 overflow-hidden rounded-xl border border-parchment-200">
            <div class="flex flex-col items-center py-6 px-4 text-center bg-parchment-50 border-r border-b border-parchment-200 sm:border-b-0">
              <p class="text-xs font-semibold uppercase tracking-wider text-claret-700 mb-1">Customer rating</p>
              <div class="text-2xl font-black text-claret-900">{{ (block.value as TrustStripVal).rating_value }}<span class="text-base font-normal text-slate-400">/5</span></div>
              <div class="mt-1 flex gap-0.5">
                <Icon v-for="n in 5" :key="n" name="star"
                  class="h-3 w-3"
                  :class="n <= Math.round((block.value as TrustStripVal).rating_value) ? 'text-amber-500' : 'text-slate-300'" />
              </div>
            </div>
            <div class="flex flex-col items-center py-6 px-4 text-center bg-parchment-50 border-b border-parchment-200 sm:border-b-0 sm:border-r">
              <p class="text-xs font-semibold uppercase tracking-wider text-claret-700 mb-1">Reviews</p>
              <div class="text-2xl font-black text-claret-900">{{ (block.value as TrustStripVal).review_count.toLocaleString() }}+</div>
            </div>
            <div class="flex flex-col items-center py-6 px-4 text-center bg-parchment-50 border-r border-parchment-200">
              <p class="text-xs font-semibold uppercase tracking-wider text-claret-700 mb-1">Years in business</p>
              <div class="text-2xl font-black text-claret-900">{{ (block.value as TrustStripVal).years_in_business }}</div>
            </div>
            <div class="flex flex-col items-center py-6 px-4 text-center bg-parchment-50">
              <p class="text-xs font-semibold uppercase tracking-wider text-claret-700 mb-1">Orders completed</p>
              <div class="text-2xl font-black text-claret-900">{{ (block.value as TrustStripVal).orders_completed.toLocaleString() }}+</div>
            </div>
          </div>
        </div>
      </template>

      <!-- highlight_list — RPM palette -->
      <template v-else-if="block.type === 'highlight_list'">
        <div class="mb-8 break-inside-avoid">
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
          <div v-else class="overflow-hidden rounded-xl border border-parchment-200">
            <div v-for="(item, i) in (block.value as HighlightListVal).items" :key="i"
              class="px-5 py-3 text-sm text-slate-700 leading-relaxed"
              :class="i % 2 === 0 ? 'bg-white' : hlColor((block.value as HighlightListVal).color, 'zebra')"
              v-html="item" />
          </div>
        </div>
      </template>

      <!-- before_after — wide -->
      <template v-else-if="block.type === 'before_after'">
        <div class="mb-8 [column-span:all]">
          <h3 v-if="(block.value as BeforeAfterVal).heading" class="mb-4 font-serif text-xl font-bold text-claret-900">
            {{ (block.value as BeforeAfterVal).heading }}
          </h3>
          <div class="grid gap-4 sm:grid-cols-2">
            <div class="overflow-hidden rounded-xl border border-parchment-200">
              <div class="flex items-center gap-2 border-b border-parchment-200 bg-parchment-100 px-4 py-2.5">
                <span class="h-2 w-2 rounded-full bg-claret-300" />
                <span class="text-xs font-bold uppercase tracking-wider text-claret-700">
                  {{ (block.value as BeforeAfterVal).label_before || 'Before' }}
                </span>
              </div>
              <div class="px-5 py-4 prose prose-sm prose-slate max-w-none text-slate-700"
                v-html="(block.value as BeforeAfterVal).content_before" />
            </div>
            <div class="overflow-hidden rounded-xl border border-claret-200">
              <div class="flex items-center gap-2 border-b border-claret-200 bg-claret-50 px-4 py-2.5">
                <span class="h-2 w-2 rounded-full bg-claret-600" />
                <span class="text-xs font-bold uppercase tracking-wider text-claret-700">
                  {{ (block.value as BeforeAfterVal).label_after || 'After' }}
                </span>
              </div>
              <div class="px-5 py-4 prose prose-sm max-w-none text-claret-900"
                v-html="(block.value as BeforeAfterVal).content_after" />
            </div>
          </div>
          <p v-if="(block.value as BeforeAfterVal).caption" class="mt-2 text-center text-xs italic text-slate-400">
            {{ (block.value as BeforeAfterVal).caption }}
          </p>
        </div>
      </template>

      <!-- pricing_table — RPM: data-table style with alternating row shading — wide -->
      <template v-else-if="block.type === 'pricing_table'">
        <div class="mb-8 [column-span:all]">
          <div class="overflow-hidden rounded-xl border border-parchment-200 bg-white shadow-sm">
            <div v-if="(block.value as PricingTableVal).heading"
              class="border-b border-parchment-200 bg-claret-900 px-6 py-4">
              <h3 class="font-serif text-lg font-bold text-white">{{ (block.value as PricingTableVal).heading }}</h3>
            </div>
            <table class="min-w-full text-sm">
              <thead>
                <tr class="border-b border-parchment-200 bg-parchment-100">
                  <th class="px-6 py-3 text-left text-xs font-bold uppercase tracking-wider text-claret-700">Service</th>
                  <th class="px-6 py-3 text-left text-xs font-bold uppercase tracking-wider text-claret-700">Price</th>
                  <th class="px-6 py-3 text-left text-xs font-bold uppercase tracking-wider text-claret-700">Turnaround</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, i) in (block.value as PricingTableVal).rows" :key="i"
                  :class="i % 2 === 0 ? 'bg-white' : 'bg-parchment-50'">
                  <td class="px-6 py-3.5 font-medium text-slate-800">{{ row.service }}</td>
                  <td class="px-6 py-3.5 font-bold text-amber-700">{{ row.price }}</td>
                  <td class="px-6 py-3.5 text-slate-500">{{ row.turnaround }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>

      <!-- comparison_table — wide -->
      <template v-else-if="block.type === 'comparison_table'">
        <div class="mb-8 [column-span:all]">
          <div class="overflow-hidden rounded-xl border border-parchment-200 bg-white shadow-sm">
            <div class="border-b border-parchment-200 bg-parchment-100 px-6 py-4">
              <h3 class="font-serif text-lg font-bold text-claret-900">{{ (block.value as CompTableVal).heading || 'Why Choose Us' }}</h3>
            </div>
            <table class="min-w-full text-sm">
              <thead>
                <tr class="border-b border-parchment-100">
                  <th class="px-5 py-3 text-left font-semibold text-slate-500 w-2/5">Feature</th>
                  <th class="px-5 py-3 text-left font-semibold text-amber-700 w-[30%]">Us</th>
                  <th class="px-5 py-3 text-left font-semibold text-slate-400 w-[30%]">
                    {{ (block.value as CompTableVal).competitor_name || 'Others' }}
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-parchment-100">
                <tr v-for="(row, i) in (block.value as CompTableVal).rows" :key="i"
                  class="hover:bg-parchment-50 transition-colors">
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
        </div>
      </template>

      <!-- testimonials — RPM: compact card grid (2-col on desktop), star rating on top — wide -->
      <template v-else-if="block.type === 'testimonials'">
        <div class="mb-8 [column-span:all]">
          <h3 v-if="(block.value as TestimonialsVal).heading" class="mb-5 font-serif text-2xl font-bold text-claret-900">
            {{ (block.value as TestimonialsVal).heading }}
          </h3>
          <div class="grid gap-4 sm:grid-cols-2">
            <div v-for="(t, i) in (block.value as TestimonialsVal).testimonials" :key="i"
              class="flex flex-col rounded-xl border border-parchment-200 bg-parchment-50 p-5">
              <!-- Stars on top -->
              <div class="flex gap-0.5 mb-3">
                <Icon v-for="n in 5" :key="n" name="star"
                  class="h-4 w-4"
                  :class="n <= t.rating ? 'text-amber-500' : 'text-slate-300'" />
              </div>
              <div class="flex-1 prose prose-sm prose-slate max-w-none text-slate-700 leading-relaxed"
                v-html="t.quote" />
              <div class="mt-4 pt-3 border-t border-parchment-300">
                <p class="font-semibold text-claret-900 text-sm">{{ t.author_name }}</p>
                <p v-if="t.author_title" class="text-xs text-slate-400 mt-0.5">{{ t.author_title }}</p>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- guarantees — wide -->
      <template v-else-if="block.type === 'guarantees'">
        <div class="mb-8 [column-span:all]">
          <h3 v-if="(block.value as GuaranteesVal).heading" class="mb-5 font-serif text-2xl font-bold text-claret-900">
            {{ (block.value as GuaranteesVal).heading }}
          </h3>
          <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div v-for="(g, i) in (block.value as GuaranteesVal).guarantees" :key="i"
              class="flex items-start gap-4 rounded-xl border border-parchment-200 bg-parchment-50 p-5">
              <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-claret-900">
                <Icon :name="g.icon_name || 'shield-check'" class="h-5 w-5 text-amber-500" />
              </div>
              <div>
                <p class="font-semibold text-slate-900 leading-snug">{{ g.title }}</p>
                <p class="mt-1 text-sm text-slate-500 leading-relaxed">{{ g.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- benefits_section — RPM: icon-led rows with fine rule separators — wide -->
      <template v-else-if="block.type === 'benefits_section'">
        <div class="mb-8 [column-span:all]">
          <div class="rounded-xl border border-parchment-200 bg-parchment-50 p-7">
            <h3 class="font-serif text-2xl font-bold text-claret-900">{{ (block.value as BenefitsVal).heading }}</h3>
            <p v-if="(block.value as BenefitsVal).intro" class="mt-2 text-slate-600 leading-relaxed">{{ (block.value as BenefitsVal).intro }}</p>
            <ul class="mt-5 divide-y divide-parchment-300">
              <li v-for="(b, i) in (block.value as BenefitsVal).benefits" :key="i" class="flex items-start gap-4 py-4 first:pt-0 last:pb-0">
                <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-claret-900 mt-0.5">
                  <Icon name="check-circle" class="h-4 w-4 text-amber-500" />
                </div>
                <div>
                  <p class="font-semibold text-slate-900">{{ b.title }}</p>
                  <p v-if="b.description" class="mt-0.5 text-sm text-slate-600 leading-relaxed">{{ b.description }}</p>
                </div>
              </li>
            </ul>
            <div v-if="(block.value as BenefitsVal).badges?.length" class="mt-5 flex flex-wrap gap-2">
              <span v-for="(badge, i) in (block.value as BenefitsVal).badges" :key="i"
                class="flex items-center gap-1.5 rounded-full border border-claret-200 bg-white px-3.5 py-1.5 text-xs font-medium text-claret-800">
                <span v-if="badge.icon_emoji">{{ badge.icon_emoji }}</span>{{ badge.label }}
              </span>
            </div>
            <p v-if="(block.value as BenefitsVal).closing_text" class="mt-4 text-xs italic text-slate-400">{{ (block.value as BenefitsVal).closing_text }}</p>
          </div>
        </div>
      </template>

      <!-- author_review -->
      <template v-else-if="block.type === 'author_review'">
        <div class="mb-8 break-inside-avoid">
          <div class="flex items-center gap-4 rounded-xl border border-parchment-200 bg-parchment-50 px-6 py-5">
            <img v-if="(block.value as AuthorReviewVal).photo?.url"
              :src="(block.value as AuthorReviewVal).photo!.url"
              :alt="(block.value as AuthorReviewVal).reviewer_name"
              class="h-12 w-12 rounded-full object-cover shrink-0 border-2 border-parchment-200" />
            <div v-else class="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-claret-100 border-2 border-parchment-200">
              <Icon name="user-check" class="h-5 w-5 text-claret-700" />
            </div>
            <div class="min-w-0">
              <p class="font-bold text-claret-900 text-sm">{{ (block.value as AuthorReviewVal).reviewer_name }}</p>
              <p class="text-xs text-slate-500">{{ (block.value as AuthorReviewVal).credentials }}</p>
              <p class="mt-0.5 text-xs text-slate-400">Reviewed {{ (block.value as AuthorReviewVal).review_date }}</p>
              <a v-if="(block.value as AuthorReviewVal).reviewer_url"
                :href="(block.value as AuthorReviewVal).reviewer_url"
                target="_blank" rel="noopener noreferrer"
                class="mt-1 inline-flex items-center gap-1 text-xs font-medium text-amber-700 hover:underline">
                View profile <Icon name="external-link" class="h-3 w-3" />
              </a>
            </div>
            <div class="ml-auto shrink-0 hidden sm:flex items-center gap-1.5 rounded-full border border-claret-200 bg-claret-50 px-3 py-1">
              <Icon name="check-circle" class="h-3.5 w-3.5 text-claret-700" />
              <span class="text-xs font-semibold text-claret-800">Expert reviewed</span>
            </div>
          </div>
        </div>
      </template>

      <!-- disclaimer -->
      <template v-else-if="block.type === 'disclaimer'">
        <div class="mb-8 break-inside-avoid">
          <div class="flex gap-3 rounded-xl border px-5 py-4"
            :class="{
              'border-amber-200 bg-amber-50': (block.value as DisclaimerVal).style === 'academic_integrity',
              'border-parchment-300 bg-parchment-50': (block.value as DisclaimerVal).style === 'copyright' || (block.value as DisclaimerVal).style === 'general',
              'border-red-200 bg-red-50':     (block.value as DisclaimerVal).style === 'medical',
            }">
            <Icon name="shield-check"
              class="mt-0.5 h-5 w-5 shrink-0"
              :class="{
                'text-amber-600': (block.value as DisclaimerVal).style === 'academic_integrity',
                'text-claret-500': (block.value as DisclaimerVal).style === 'copyright' || (block.value as DisclaimerVal).style === 'general',
                'text-red-500':   (block.value as DisclaimerVal).style === 'medical',
              }"
            />
            <div class="prose prose-sm max-w-none text-slate-700" v-html="(block.value as DisclaimerVal).text" />
          </div>
        </div>
      </template>

      <!-- chart — RPM: data-dashboard horizontal bar chart with header band — wide -->
      <template v-else-if="block.type === 'chart'">
        <div class="mb-8 [column-span:all]">
          <div class="rounded-xl border border-parchment-200 bg-white shadow-sm overflow-hidden">
            <div class="border-b border-parchment-200 bg-parchment-100 px-6 py-3.5">
              <h4 class="font-semibold text-claret-900">{{ (block.value as ChartVal).title }}</h4>
            </div>
            <div class="p-6 space-y-3">
              <template v-for="(ds, di) in (block.value as ChartVal).datasets" :key="di">
                <div v-for="(label, li) in (block.value as ChartVal).x_labels.split(',')" :key="li" class="flex items-center gap-3 text-sm">
                  <span class="w-28 shrink-0 text-xs text-slate-500 text-right truncate">{{ label.trim() }}</span>
                  <div class="flex-1 h-5 rounded bg-parchment-100 overflow-hidden">
                    <div class="h-full rounded transition-all"
                      :style="{ width: chartBarWidth((block.value as ChartVal), di, li) + '%', background: ds.color || '#9e1540' }" />
                  </div>
                  <span class="w-10 shrink-0 text-xs font-bold text-claret-800 tabular-nums">
                    {{ (ds.values.split(',')[li] ?? '').trim() }}
                  </span>
                </div>
                <p v-if="(block.value as ChartVal).datasets.length > 1" class="text-xs text-slate-400 pl-[7.5rem]">{{ ds.label }}</p>
              </template>
            </div>
            <p v-if="(block.value as ChartVal).caption"
              class="border-t border-parchment-100 px-6 py-2.5 text-xs italic text-slate-400 bg-parchment-50">
              {{ (block.value as ChartVal).caption }}
            </p>
          </div>
        </div>
      </template>

      <!-- embed — wide -->
      <template v-else-if="block.type === 'embed'">
        <div class="mb-8 [column-span:all]">
          <div class="overflow-hidden rounded-xl border border-parchment-200 bg-parchment-50 shadow-sm">
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
          <p v-if="(block.value as EmbedVal).caption" class="mt-2 text-center text-xs italic text-slate-400">
            {{ (block.value as EmbedVal).caption }}
          </p>
        </div>
      </template>

      <!-- internal_link -->
      <template v-else-if="block.type === 'internal_link'">
        <div class="mb-8 break-inside-avoid">
          <NuxtLink v-if="(block.value as InternalLinkVal).page"
            :to="`/services/${(block.value as InternalLinkVal).page!.slug}`"
            class="group flex items-center gap-4 rounded-xl border border-parchment-200 bg-parchment-50 px-6 py-4 hover:border-claret-300 transition-colors no-underline">
            <div>
              <p class="font-semibold text-claret-900 group-hover:text-claret-700 transition-colors text-sm leading-snug">
                {{ (block.value as InternalLinkVal).custom_title || (block.value as InternalLinkVal).page!.title }}
              </p>
              <p v-if="(block.value as InternalLinkVal).custom_description || (block.value as InternalLinkVal).page?.description"
                class="mt-0.5 text-xs text-slate-500 line-clamp-1">
                {{ (block.value as InternalLinkVal).custom_description || (block.value as InternalLinkVal).page?.description }}
              </p>
            </div>
            <Icon name="chevron-right" class="ml-auto h-5 w-5 shrink-0 text-parchment-400 group-hover:text-amber-600 transition-colors" />
          </NuxtLink>
        </div>
      </template>

      <!-- calculator — RPM: inline widget feel with a clear "Estimate" CTA — wide -->
      <template v-else-if="block.type === 'calculator'">
        <div class="mb-8 [column-span:all]">
          <div class="rounded-xl border border-parchment-200 bg-parchment-50 overflow-hidden">
            <div class="flex items-center gap-4 border-b border-parchment-200 bg-claret-900 px-6 py-4">
              <Icon name="calculator" class="h-5 w-5 text-amber-400 shrink-0" />
              <div>
                <h3 class="font-serif font-bold text-white">{{ (block.value as CalculatorVal).title || 'Instant Price Estimate' }}</h3>
                <p v-if="(block.value as CalculatorVal).subtitle" class="text-xs text-parchment-200 mt-0.5">{{ (block.value as CalculatorVal).subtitle }}</p>
              </div>
            </div>
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 px-6 py-5">
              <div class="flex flex-wrap gap-4 text-sm text-slate-600">
                <span v-if="(block.value as CalculatorVal).default_pages" class="flex items-center gap-1.5">
                  <Icon name="file-text" class="h-4 w-4 text-claret-400" />
                  {{ (block.value as CalculatorVal).default_pages }} page{{ (block.value as CalculatorVal).default_pages! > 1 ? 's' : '' }}
                </span>
                <span v-if="(block.value as CalculatorVal).default_deadline_hours" class="flex items-center gap-1.5">
                  <Icon name="clock" class="h-4 w-4 text-claret-400" />
                  {{ (block.value as CalculatorVal).default_deadline_hours }}h deadline
                </span>
              </div>
              <a :href="(block.value as CalculatorVal).cta_url || '/order'"
                class="inline-block shrink-0 rounded-xl bg-amber-600 px-7 py-3 text-sm font-bold text-white hover:bg-amber-700 transition-colors">
                {{ (block.value as CalculatorVal).cta_text || 'Get My Estimate' }}
              </a>
            </div>
          </div>
        </div>
      </template>

      <!-- fallback: unknown block type — silently skip -->

    </template>
  </div>
</template>

<style scoped>
:deep(.prose table), :deep(table) { display: block; overflow-x: auto; overflow-y: auto; max-height: 28rem; border-collapse: collapse; width: max-content; max-width: 100%; }
:deep(.prose th), :deep(th) { position: sticky; top: 0; background: #FDFAF4; font-weight: 600; color: #5C1A38; padding: 0.625rem 1rem; border: 1px solid #fce4ee; white-space: nowrap; z-index: 1; }
:deep(.prose td), :deep(td) { padding: 0.5rem 1rem; border: 1px solid #e2e8f0; color: #475569; vertical-align: top; font-size: 0.875rem; }
:deep(.prose tr:hover), :deep(tr:hover) { background: #FDFAF4; }
:deep(a[target="_blank"][href^="http"])::after { content: '\2197'; display: inline-block; font-size: 0.65em; vertical-align: super; margin-left: 0.15em; opacity: 0.7; }
</style>

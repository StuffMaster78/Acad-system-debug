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
  out = out.replace(/href="\/(?:blog|services)\/([\w-]+)\/?"/gi, 'href="/$1"')
  out = out.replace(/href="\/([a-z][a-z0-9-]*)\/?"(?=[^>]*>)/g, (_match, slug) => {
    if (_serviceSlugs.has(slug)) return `href="/${slug}"`
    if (_blogSlugs.has(slug))    return `href="/${slug}"`
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
          <div class="rounded-2xl border border-claret-200 bg-claret-900/50 p-6">
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
            <Icon :name="({ check: 'check-circle', arrow: 'arrow-right', star: 'star', lightning: 'zap', shield: 'shield', dot: 'circle' } as Record<string, string>)[(block.value as any).icon] || 'check-circle'"
              class="h-4 w-4 shrink-0 mt-0.5 text-amber-700" />
            <div class="text-sm text-slate-700 leading-relaxed" v-html="rewriteLinks(item)" />
          </div>
        </div>
        <div v-else-if="(block.value as any).style === 'cards'" class="space-y-2">
          <div v-for="(item, i) in (block.value as any).items || []" :key="i"
            class="flex items-start gap-3 rounded-xl border border-parchment-200 bg-parchment-50 px-5 py-4">
            <Icon :name="({ check: 'check-circle', arrow: 'arrow-right', star: 'star', lightning: 'zap', shield: 'shield', dot: 'circle' } as Record<string, string>)[(block.value as any).icon] || 'check-circle'"
              class="h-4 w-4 shrink-0 mt-0.5 text-amber-700" />
            <div class="text-sm text-slate-700 leading-relaxed" v-html="rewriteLinks(item)" />
          </div>
        </div>
        <ul v-else class="space-y-3">
          <li v-for="(item, i) in (block.value as any).items || []" :key="i" class="flex items-start gap-3 text-sm text-slate-700">
            <Icon :name="({ check: 'check-circle', arrow: 'arrow-right', star: 'star', lightning: 'zap', shield: 'shield', dot: 'circle' } as Record<string, string>)[(block.value as any).icon] || 'check-circle'"
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
                  <Icon name="x-circle" class="h-4 w-4 shrink-0 mt-0.5 text-red-400" />{{ con }}
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

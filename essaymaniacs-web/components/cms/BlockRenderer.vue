<script setup lang="ts">
import { computed } from 'vue'
import { CheckCircle2, ArrowRight, ExternalLink, Download } from '@lucide/vue'

const app = useAppUrl()

interface Block { type: string; value: unknown }

const props = defineProps<{
  blocks: Block[]
  /** Brand-specific inline CTA HTML injected after the 4th paragraph block. */
  inlineCta?: string
}>()

// ── Helpers ───────────────────────────────────────────────────────────────────
function asStr(v: unknown): string { return typeof v === 'string' ? v : '' }
function asObj(v: unknown): Record<string, unknown> {
  return (v && typeof v === 'object' && !Array.isArray(v)) ? v as Record<string, unknown> : {}
}
function asArr(v: unknown): unknown[] { return Array.isArray(v) ? v : [] }
function asBool(v: unknown): boolean { return v === true }

function heading(v: unknown) {
  const o = asObj(v)
  return { text: asStr(o.text), level: asStr(o.level) || 'h2', id: slugifyHeading(asStr(o.text)) }
}

function ctaUrl(raw: string): string {
  if (!raw) return app.order
  if (raw.startsWith('http') || raw.startsWith('/')) return raw
  return raw
}

/** Convert a YouTube or Vimeo watch URL to an embed URL. */
function videoEmbedUrl(url: string): string {
  try {
    const u = new URL(url)
    // YouTube
    if (u.hostname.includes('youtube.com') || u.hostname.includes('youtu.be')) {
      const id = u.hostname.includes('youtu.be')
        ? u.pathname.slice(1)
        : u.searchParams.get('v') ?? ''
      return id ? `https://www.youtube.com/embed/${id}` : ''
    }
    // Vimeo
    if (u.hostname.includes('vimeo.com')) {
      const id = u.pathname.split('/').filter(Boolean)[0] ?? ''
      return id ? `https://player.vimeo.com/video/${id}` : ''
    }
  } catch { /* ignore */ }
  return ''
}

// ── Callout style map ─────────────────────────────────────────────────────────
const CALLOUT_STYLE: Record<string, { border: string; bg: string; icon: string; label: string }> = {
  note:      { border: 'border-blue-400',   bg: 'bg-blue-50',   icon: 'ℹ',  label: 'Note'      },
  tip:       { border: 'border-green-400',  bg: 'bg-green-50',  icon: '💡', label: 'Tip'       },
  warning:   { border: 'border-amber-400',  bg: 'bg-amber-50',  icon: '⚠️', label: 'Warning'   },
  important: { border: 'border-red-400',    bg: 'bg-red-50',    icon: '❗', label: 'Important' },
}
function calloutStyle(style: string) {
  return CALLOUT_STYLE[style] ?? CALLOUT_STYLE.note
}

// ── Disclaimer style map ──────────────────────────────────────────────────────
const DISCLAIMER_STYLE: Record<string, { border: string; bg: string; label: string }> = {
  academic_integrity: { border: 'border-brand-300', bg: 'bg-brand-50',  label: 'Academic Integrity Notice' },
  copyright:          { border: 'border-slate-300',  bg: 'bg-slate-50',  label: 'Copyright Notice'          },
  medical:            { border: 'border-rose-300',   bg: 'bg-rose-50',   label: 'Health Notice'             },
  general:            { border: 'border-slate-300',  bg: 'bg-slate-50',  label: 'Notice'                    },
}
function disclaimerStyle(style: string) {
  return DISCLAIMER_STYLE[style] ?? DISCLAIMER_STYLE.general
}

// ── Sample excerpt formatting labels ─────────────────────────────────────────
const FORMAT_LABELS: Record<string, string> = {
  apa7: 'APA 7th Ed.', mla9: 'MLA 9th Ed.', chicago: 'Chicago',
  harvard: 'Harvard', ieee: 'IEEE', none: 'General',
}
const LEVEL_LABELS: Record<string, string> = {
  high_school: 'High School', undergraduate: 'Undergraduate',
  graduate: 'Graduate / Masters', phd: 'PhD / Doctoral',
}

// ── Table helpers ─────────────────────────────────────────────────────────────
function tableData(v: unknown): string[][] {
  const o = asObj(v)
  const rows = asArr(o.data)
  return rows.map(r => asArr(r).map(c => asStr(c)))
}
function tableHasHeader(v: unknown): boolean {
  return asBool(asObj(v).first_row_is_table_header)
}
function tableHasColHeader(v: unknown): boolean {
  return asBool(asObj(v).first_col_is_header)
}

// ── Mid-article CTA injection ─────────────────────────────────────────────────
// Injects the inline CTA HTML after the 4th paragraph block.
const enrichedBlocks = computed<(Block & { _cta?: boolean })[]>(() => {
  if (!props.inlineCta) return props.blocks
  let pCount = 0
  const result: (Block & { _cta?: boolean })[] = []
  for (const block of props.blocks) {
    result.push(block)
    if (block.type === 'paragraph') {
      pCount++
      if (pCount === 4) result.push({ type: '_inline_cta', value: null, _cta: true })
    }
  }
  return result
})
</script>

<template>
  <template v-for="(block, i) in enrichedBlocks" :key="i">

    <!-- ── Mid-article CTA ──────────────────────────────────────────────── -->
    <div v-if="block._cta" v-html="inlineCta" class="not-prose" />

    <!-- ── Paragraph / rich text ────────────────────────────────────────── -->
    <div
      v-else-if="block.type === 'paragraph'"
      class="prose-content"
      v-html="asStr(block.value)"
    />

    <!-- ── Heading ──────────────────────────────────────────────────────── -->
    <component
      :is="heading(block.value).level"
      v-else-if="block.type === 'heading'"
      :id="heading(block.value).id"
      class="font-bold text-ink mt-8 mb-3 scroll-mt-24"
      :class="{
        'text-2xl': heading(block.value).level === 'h2',
        'text-xl':  heading(block.value).level === 'h3',
        'text-lg':  heading(block.value).level === 'h4',
      }"
    >{{ heading(block.value).text }}</component>

    <!-- ── Key Takeaways ────────────────────────────────────────────────── -->
    <div
      v-else-if="block.type === 'key_takeaways'"
      class="my-6 rounded-2xl border border-brand-200 bg-brand-50 p-5"
    >
      <p class="text-xs font-bold uppercase tracking-widest text-brand-600 mb-3">
        {{ asStr(asObj(block.value).heading) || 'Key Takeaways' }}
      </p>
      <ul class="space-y-2">
        <li
          v-for="(item, j) in asArr(asObj(block.value).items)"
          :key="j"
          class="flex items-start gap-2 text-sm text-ink"
        >
          <CheckCircle2 class="size-4 shrink-0 text-brand-600 mt-0.5" />
          <span>{{ asStr(item) }}</span>
        </li>
      </ul>
    </div>

    <!-- ── Quote ────────────────────────────────────────────────────────── -->
    <figure
      v-else-if="block.type === 'quote'"
      class="my-8 not-prose"
    >
      <blockquote class="relative border-l-4 border-brand-500 pl-6 py-1">
        <span class="absolute -top-2 left-4 text-5xl leading-none text-brand-200 font-serif select-none">"</span>
        <div
          class="text-lg font-medium leading-relaxed text-ink italic pl-2"
          v-html="asStr(asObj(block.value).text)"
        />
      </blockquote>
      <figcaption
        v-if="asStr(asObj(block.value).attribution)"
        class="mt-3 pl-6 text-sm text-slate-500"
      >
        — {{ asStr(asObj(block.value).attribution) }}
      </figcaption>
    </figure>

    <!-- ── Callout (style-aware) ─────────────────────────────────────────── -->
    <div
      v-else-if="block.type === 'callout'"
      class="my-6 rounded-xl border-l-4 px-5 py-4"
      :class="[calloutStyle(asStr(asObj(block.value).style)).border, calloutStyle(asStr(asObj(block.value).style)).bg]"
    >
      <p class="mb-1 text-xs font-bold uppercase tracking-wider text-slate-500">
        {{ calloutStyle(asStr(asObj(block.value).style)).icon }}
        {{ calloutStyle(asStr(asObj(block.value).style)).label }}
      </p>
      <div class="text-sm text-ink" v-html="asStr(asObj(block.value).text)" />
    </div>

    <!-- ── List (bulleted / numbered) ───────────────────────────────────── -->
    <div v-else-if="block.type === 'list'" class="my-4">
      <ol v-if="asStr(asObj(block.value).style) === 'numbered'" class="list-decimal pl-5 space-y-1.5">
        <li
          v-for="(item, j) in asArr(asObj(block.value).items)"
          :key="j"
          class="text-ink text-sm leading-relaxed"
          v-html="asStr(item)"
        />
      </ol>
      <ul v-else class="list-disc pl-5 space-y-1.5">
        <li
          v-for="(item, j) in asArr(asObj(block.value).items)"
          :key="j"
          class="text-ink text-sm leading-relaxed"
          v-html="asStr(item)"
        />
      </ul>
    </div>

    <!-- ── Checklist ────────────────────────────────────────────────────── -->
    <div v-else-if="block.type === 'checklist'" class="my-6">
      <p v-if="asStr(asObj(block.value).title)" class="text-sm font-semibold text-ink mb-3">
        {{ asStr(asObj(block.value).title) }}
      </p>
      <ul class="space-y-2">
        <li
          v-for="(item, j) in asArr(asObj(block.value).items)"
          :key="j"
          class="flex items-start gap-2.5 text-sm"
        >
          <CheckCircle2 class="size-4 shrink-0 text-brand-600 mt-0.5" />
          <div>
            <span class="text-ink">{{ asStr(asObj(item).text) }}</span>
            <span v-if="asStr(asObj(item).detail)" class="block text-xs text-slate-500 mt-0.5">
              {{ asStr(asObj(item).detail) }}
            </span>
          </div>
        </li>
      </ul>
    </div>

    <!-- ── Stats Highlight ──────────────────────────────────────────────── -->
    <div v-else-if="block.type === 'stats_highlight'" class="my-8 not-prose">
      <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div
          v-for="(stat, j) in asArr(asObj(block.value).stats)"
          :key="j"
          class="rounded-2xl border border-brand-100 bg-brand-50 px-5 py-5 text-center"
        >
          <p class="text-3xl font-extrabold text-brand-700">{{ asStr(asObj(stat).value) }}</p>
          <p class="mt-1 text-xs font-medium text-slate-500">{{ asStr(asObj(stat).label) }}</p>
        </div>
      </div>
      <p
        v-if="asStr(asObj(block.value).supporting_text)"
        class="mt-3 text-center text-xs text-slate-400"
      >{{ asStr(asObj(block.value).supporting_text) }}</p>
    </div>

    <!-- ── Before & After ───────────────────────────────────────────────── -->
    <div v-else-if="block.type === 'before_after'" class="my-8 not-prose">
      <p v-if="asStr(asObj(block.value).heading)" class="mb-4 text-sm font-bold uppercase tracking-widest text-slate-400">
        {{ asStr(asObj(block.value).heading) }}
      </p>
      <div class="grid gap-4 sm:grid-cols-2">
        <div class="rounded-2xl border border-red-200 bg-red-50 overflow-hidden">
          <p class="px-4 py-2 text-xs font-bold uppercase tracking-wider text-red-600 border-b border-red-100">
            {{ asStr(asObj(block.value).label_before) || 'Before' }}
          </p>
          <div class="px-4 py-4 text-sm text-ink leading-relaxed" v-html="asStr(asObj(block.value).content_before)" />
        </div>
        <div class="rounded-2xl border border-green-200 bg-green-50 overflow-hidden">
          <p class="px-4 py-2 text-xs font-bold uppercase tracking-wider text-green-600 border-b border-green-100">
            {{ asStr(asObj(block.value).label_after) || 'After' }}
          </p>
          <div class="px-4 py-4 text-sm text-ink leading-relaxed" v-html="asStr(asObj(block.value).content_after)" />
        </div>
      </div>
      <p v-if="asStr(asObj(block.value).caption)" class="mt-2 text-center text-xs text-slate-400">
        {{ asStr(asObj(block.value).caption) }}
      </p>
    </div>

    <!-- ── Definition ───────────────────────────────────────────────────── -->
    <div
      v-else-if="block.type === 'definition'"
      class="my-6 rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4"
    >
      <p class="text-xs font-bold uppercase tracking-widest text-brand-600 mb-1">Definition</p>
      <p class="font-semibold text-ink">{{ asStr(asObj(block.value).term) }}</p>
      <div class="mt-1 text-sm text-ink leading-relaxed" v-html="asStr(asObj(block.value).definition)" />
      <p v-if="asStr(asObj(block.value).example)" class="mt-2 text-xs text-slate-500 italic">
        <span class="font-semibold not-italic">Example:</span> {{ asStr(asObj(block.value).example) }}
      </p>
    </div>

    <!-- ── Timeline ─────────────────────────────────────────────────────── -->
    <div v-else-if="block.type === 'timeline'" class="my-8 not-prose">
      <p v-if="asStr(asObj(block.value).heading)" class="mb-5 text-lg font-bold text-ink">
        {{ asStr(asObj(block.value).heading) }}
      </p>
      <ol class="relative border-l border-brand-200 ml-3">
        <li
          v-for="(entry, j) in asArr(asObj(block.value).entries)"
          :key="j"
          class="mb-8 ml-6 last:mb-0"
        >
          <span class="absolute -left-3 flex size-6 items-center justify-center rounded-full bg-brand-600 ring-4 ring-white">
            <span class="text-[9px] font-bold text-white">{{ j + 1 }}</span>
          </span>
          <p class="text-[10px] font-bold uppercase tracking-widest text-brand-500 mb-0.5">
            {{ asStr(asObj(entry).date_label) }}
          </p>
          <p class="font-semibold text-ink text-sm">{{ asStr(asObj(entry).title) }}</p>
          <div class="mt-1 text-sm text-slate-600 leading-relaxed" v-html="asStr(asObj(entry).description)" />
        </li>
      </ol>
    </div>

    <!-- ── Sample Excerpt ───────────────────────────────────────────────── -->
    <div v-else-if="block.type === 'sample_excerpt'" class="my-8 not-prose">
      <div class="rounded-2xl border border-slate-200 overflow-hidden">
        <div class="flex items-center justify-between gap-3 border-b border-slate-100 bg-slate-50 px-5 py-3">
          <p class="font-semibold text-sm text-ink">
            {{ asStr(asObj(block.value).title) || 'Writing Sample' }}
          </p>
          <div class="flex gap-2">
            <span class="rounded-full bg-brand-100 px-2.5 py-0.5 text-[10px] font-bold text-brand-700">
              {{ FORMAT_LABELS[asStr(asObj(block.value).formatting_style)] ?? asStr(asObj(block.value).formatting_style) }}
            </span>
            <span class="rounded-full bg-slate-200 px-2.5 py-0.5 text-[10px] font-bold text-slate-600">
              {{ LEVEL_LABELS[asStr(asObj(block.value).academic_level)] ?? asStr(asObj(block.value).academic_level) }}
            </span>
          </div>
        </div>
        <div class="px-6 py-5 font-serif text-sm leading-8 text-ink bg-white" v-html="asStr(asObj(block.value).excerpt)" />
        <div v-if="asStr(asObj(block.value).download_cta)" class="border-t border-slate-100 px-5 py-3 bg-slate-50">
          <a
            href="#"
            class="inline-flex items-center gap-1.5 text-xs font-semibold text-brand-600 hover:underline"
          >
            <Download class="size-3.5" />
            {{ asStr(asObj(block.value).download_cta) || 'Download Full Sample' }}
          </a>
        </div>
      </div>
    </div>

    <!-- ── Table ─────────────────────────────────────────────────────────── -->
    <figure v-else-if="block.type === 'table'" class="my-6 not-prose overflow-x-auto">
      <table class="w-full text-sm border-collapse">
        <template v-for="(row, rIdx) in tableData(asObj(block.value).table)" :key="rIdx">
          <thead v-if="rIdx === 0 && tableHasHeader(asObj(block.value).table)">
            <tr>
              <th
                v-for="(cell, cIdx) in row"
                :key="cIdx"
                class="border border-slate-200 bg-slate-100 px-4 py-2 text-left font-semibold text-ink"
              >{{ cell }}</th>
            </tr>
          </thead>
          <tbody v-else-if="rIdx > 0 || !tableHasHeader(asObj(block.value).table)">
            <tr class="even:bg-slate-50">
              <template v-for="(cell, cIdx) in row" :key="cIdx">
                <th
                  v-if="cIdx === 0 && tableHasColHeader(asObj(block.value).table)"
                  class="border border-slate-200 bg-slate-100 px-4 py-2 text-left font-semibold text-ink"
                >{{ cell }}</th>
                <td v-else class="border border-slate-200 px-4 py-2 text-ink">{{ cell }}</td>
              </template>
            </tr>
          </tbody>
        </template>
      </table>
      <figcaption
        v-if="asStr(asObj(block.value).caption)"
        class="mt-2 text-center text-xs text-slate-400"
      >{{ asStr(asObj(block.value).caption) }}</figcaption>
    </figure>

    <!-- ── Code Block ────────────────────────────────────────────────────── -->
    <figure v-else-if="block.type === 'code'" class="my-6 not-prose">
      <div class="flex items-center justify-between rounded-t-xl bg-slate-800 px-4 py-2">
        <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400">
          {{ asStr(asObj(block.value).language) || 'text' }}
        </span>
      </div>
      <pre class="rounded-b-xl bg-slate-900 px-5 py-4 overflow-x-auto"><code class="text-sm text-slate-100 leading-relaxed">{{ asStr(asObj(block.value).code) }}</code></pre>
      <figcaption
        v-if="asStr(asObj(block.value).caption)"
        class="mt-1.5 text-center text-xs text-slate-400"
      >{{ asStr(asObj(block.value).caption) }}</figcaption>
    </figure>

    <!-- ── Sources / References ──────────────────────────────────────────── -->
    <div v-else-if="block.type === 'sources'" class="my-8 not-prose">
      <p class="mb-3 text-xs font-bold uppercase tracking-widest text-slate-400">
        {{ asStr(asObj(block.value).heading) || 'Articles Consulted' }}
      </p>
      <ol class="space-y-3">
        <li
          v-for="(src, j) in asArr(asObj(block.value).sources)"
          :key="j"
          class="flex gap-3 text-xs text-slate-600 leading-relaxed"
        >
          <span class="shrink-0 font-bold text-slate-400 tabular-nums w-5 text-right">{{ j + 1 }}.</span>
          <span>
            <span v-if="asStr(asObj(src).author)" class="font-medium text-ink">{{ asStr(asObj(src).author) }}.&nbsp;</span>
            <a :href="asStr(asObj(src).url)" target="_blank" rel="noopener noreferrer" class="underline decoration-dotted hover:text-brand-600">
              {{ asStr(asObj(src).title) }}
            </a>
            <span v-if="asStr(asObj(src).publication)" class="text-slate-500">. <em>{{ asStr(asObj(src).publication) }}</em></span>
            <span v-if="asStr(asObj(src).year)" class="text-slate-500"> ({{ asStr(asObj(src).year) }})</span>
          </span>
        </li>
      </ol>
    </div>

    <!-- ── Manual Table of Contents ──────────────────────────────────────── -->
    <nav
      v-else-if="block.type === 'toc'"
      class="my-6 rounded-2xl border border-slate-200 bg-slate-50 px-5 py-4 not-prose"
      aria-label="Table of contents"
    >
      <p class="mb-2 text-xs font-bold uppercase tracking-widest text-slate-400">
        {{ asStr(asObj(block.value).heading) || 'In This Article' }}
      </p>
      <ol class="space-y-1.5">
        <li
          v-for="(entry, j) in asArr(asObj(block.value).entries)"
          :key="j"
          class="flex items-baseline gap-2 text-sm"
        >
          <span class="shrink-0 tabular-nums text-slate-400 text-[11px] w-4">{{ j + 1 }}.</span>
          <a :href="`#${asStr(asObj(entry).anchor)}`" class="text-brand-600 hover:underline leading-snug">
            {{ asStr(asObj(entry).label) }}
          </a>
        </li>
      </ol>
    </nav>

    <!-- ── Author Review Badge ────────────────────────────────────────────── -->
    <div
      v-else-if="block.type === 'author_review'"
      class="my-6 flex items-start gap-4 rounded-2xl border border-brand-100 bg-brand-50 px-5 py-4 not-prose"
    >
      <div class="flex size-12 shrink-0 items-center justify-center rounded-full bg-brand-600 text-lg font-bold text-white">
        {{ asStr(asObj(block.value).reviewer_name).charAt(0).toUpperCase() }}
      </div>
      <div class="flex-1 min-w-0">
        <p class="text-xs font-bold uppercase tracking-widest text-brand-600 mb-0.5">Expert Reviewed</p>
        <a
          v-if="asStr(asObj(block.value).reviewer_url)"
          :href="asStr(asObj(block.value).reviewer_url)"
          target="_blank"
          rel="noopener noreferrer"
          class="font-semibold text-sm text-ink hover:text-brand-700 flex items-center gap-1"
        >
          {{ asStr(asObj(block.value).reviewer_name) }}
          <ExternalLink class="size-3 opacity-50" />
        </a>
        <p v-else class="font-semibold text-sm text-ink">{{ asStr(asObj(block.value).reviewer_name) }}</p>
        <p class="text-xs text-slate-500 mt-0.5">{{ asStr(asObj(block.value).credentials) }}</p>
        <p v-if="asStr(asObj(block.value).review_date)" class="text-[10px] text-slate-400 mt-1">
          Reviewed {{ asStr(asObj(block.value).review_date) }}
        </p>
      </div>
    </div>

    <!-- ── Disclaimer ────────────────────────────────────────────────────── -->
    <div
      v-else-if="block.type === 'disclaimer'"
      class="my-6 rounded-xl border-l-4 px-5 py-4 not-prose"
      :class="[disclaimerStyle(asStr(asObj(block.value).style)).border, disclaimerStyle(asStr(asObj(block.value).style)).bg]"
    >
      <p class="text-[10px] font-bold uppercase tracking-widest text-slate-500 mb-1">
        {{ disclaimerStyle(asStr(asObj(block.value).style)).label }}
      </p>
      <div class="text-xs text-slate-600 leading-relaxed" v-html="asStr(asObj(block.value).text)" />
    </div>

    <!-- ── Internal Link Card ─────────────────────────────────────────────── -->
    <a
      v-else-if="block.type === 'internal_link' && asObj(asObj(block.value).page).meta"
      :href="asStr(asObj(asObj(asObj(block.value).page).meta).url || ('/' + asStr(asObj(asObj(asObj(block.value).page).meta).slug)))"
      class="my-6 flex items-center gap-4 rounded-2xl border border-brand-100 bg-brand-50 px-5 py-4 transition-colors hover:border-brand-300 hover:bg-brand-100 group not-prose block"
    >
      <div class="flex-1 min-w-0">
        <p class="text-xs font-bold uppercase tracking-widest text-brand-500 mb-0.5">Read Also</p>
        <p class="font-semibold text-ink group-hover:text-brand-700 leading-snug">
          {{ asStr(asObj(block.value).custom_title) || asStr(asObj(asObj(block.value).page).title) }}
        </p>
        <p v-if="asStr(asObj(block.value).custom_description)" class="text-xs text-slate-500 mt-0.5 line-clamp-2">
          {{ asStr(asObj(block.value).custom_description) }}
        </p>
      </div>
      <ArrowRight class="size-5 shrink-0 text-brand-500 group-hover:translate-x-0.5 transition-transform" />
    </a>

    <!-- ── Video Embed ────────────────────────────────────────────────────── -->
    <figure v-else-if="block.type === 'video' && videoEmbedUrl(asStr(asObj(block.value).url))" class="my-6 not-prose">
      <div class="relative aspect-video overflow-hidden rounded-2xl bg-slate-100">
        <iframe
          :src="videoEmbedUrl(asStr(asObj(block.value).url))"
          class="absolute inset-0 h-full w-full"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen
          loading="lazy"
          sandbox="allow-scripts allow-same-origin allow-presentation"
        />
      </div>
      <figcaption
        v-if="asStr(asObj(block.value).caption)"
        class="mt-2 text-center text-xs text-slate-400"
      >{{ asStr(asObj(block.value).caption) }}</figcaption>
    </figure>

    <!-- ── Third-party Embed ──────────────────────────────────────────────── -->
    <figure v-else-if="block.type === 'embed' && asStr(asObj(block.value).embed_url)" class="my-6 not-prose">
      <div class="overflow-hidden rounded-2xl border border-slate-200 bg-slate-50">
        <iframe
          :src="asStr(asObj(block.value).embed_url)"
          :height="Number(asObj(block.value).height) || 480"
          class="w-full"
          loading="lazy"
          sandbox="allow-scripts allow-same-origin allow-popups allow-forms"
        />
      </div>
      <figcaption
        v-if="asStr(asObj(block.value).caption)"
        class="mt-2 text-center text-xs text-slate-400"
      >{{ asStr(asObj(block.value).caption) }}</figcaption>
    </figure>

    <!-- ── Image ──────────────────────────────────────────────────────────── -->
    <figure
      v-else-if="block.type === 'image' && asObj(asObj(block.value).image).url"
      class="my-6"
    >
      <img
        :src="asStr(asObj(asObj(block.value).image).url)"
        :alt="asStr(asObj(block.value).alt_text)"
        class="w-full rounded-xl"
        loading="lazy"
      />
      <figcaption
        v-if="asStr(asObj(block.value).caption)"
        class="mt-2 text-center text-xs text-slate-400"
      >{{ asStr(asObj(block.value).caption) }}</figcaption>
    </figure>

    <!-- ── CTA Button ─────────────────────────────────────────────────────── -->
    <div
      v-else-if="block.type === 'cta' && asStr(asObj(block.value).text)"
      class="my-6 not-prose"
    >
      <a
        :href="ctaUrl(asStr(asObj(block.value).url))"
        class="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-6 py-3 text-sm font-bold text-white hover:bg-brand-700 transition-colors"
      >
        {{ asStr(asObj(block.value).text) }}
        <ArrowRight class="size-4" />
      </a>
    </div>

    <!-- ── FAQ ───────────────────────────────────────────────────────────── -->
    <details
      v-else-if="block.type === 'faq'"
      class="my-3 group rounded-2xl border border-slate-200 bg-white shadow-sm not-prose"
    >
      <summary class="flex cursor-pointer list-none items-center justify-between gap-4 px-6 py-4 text-sm font-semibold text-ink">
        {{ asStr(asObj(block.value).question) }}
        <span class="flex size-6 shrink-0 items-center justify-center rounded-full bg-slate-100 transition-transform group-open:rotate-45 text-slate-500">+</span>
      </summary>
      <div class="border-t border-slate-100 px-6 pb-5 pt-4 text-sm text-slate-600 leading-relaxed" v-html="asStr(asObj(block.value).answer)" />
    </details>

    <!-- ── Divider ────────────────────────────────────────────────────────── -->
    <hr v-else-if="block.type === 'divider'" class="my-8 border-slate-200" />

  </template>
</template>

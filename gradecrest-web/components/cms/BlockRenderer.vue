<script setup lang="ts">
import { CheckCircle2, ArrowRight } from '@lucide/vue'

const app = useAppUrl()

interface Block {
  type: string
  value: unknown
}
const props = defineProps<{ blocks: Block[] }>()

function asStr(v: unknown): string { return typeof v === 'string' ? v : '' }
function asObj(v: unknown): Record<string, unknown> { return (v && typeof v === 'object' && !Array.isArray(v)) ? v as Record<string, unknown> : {} }
function asArr(v: unknown): unknown[] { return Array.isArray(v) ? v : [] }

function heading(v: unknown) {
  const o = asObj(v)
  return { text: asStr(o.text), level: asStr(o.level) || 'h2' }
}

function ctaUrl(raw: string): string {
  if (!raw) return app.order
  if (raw.startsWith('http')) return raw
  return raw
}
</script>

<template>
  <template v-for="(block, i) in blocks" :key="i">

    <!-- paragraph / rich text -->
    <div
      v-if="block.type === 'paragraph'"
      class="prose-content"
      v-html="asStr(block.value)"
    />

    <!-- heading -->
    <component
      :is="heading(block.value).level"
      v-else-if="block.type === 'heading'"
      class="font-bold text-ink mt-8 mb-3"
      :class="{
        'text-2xl': heading(block.value).level === 'h2',
        'text-xl':  heading(block.value).level === 'h3',
        'text-lg':  heading(block.value).level === 'h4',
      }"
    >{{ heading(block.value).text }}</component>

    <!-- key_takeaways -->
    <div
      v-else-if="block.type === 'key_takeaways'"
      class="my-6 rounded-2xl border border-gc-200 bg-gc-50 p-5"
    >
      <p class="text-xs font-bold uppercase tracking-widest text-gc-600 mb-3">
        {{ asStr(asObj(block.value).heading) || 'Key Takeaways' }}
      </p>
      <ul class="space-y-2">
        <li
          v-for="(item, j) in asArr(asObj(block.value).items)"
          :key="j"
          class="flex items-start gap-2 text-sm text-ink"
        >
          <CheckCircle2 class="size-4 shrink-0 text-gc-600 mt-0.5" />
          <span>{{ asStr(item) }}</span>
        </li>
      </ul>
    </div>

    <!-- checklist -->
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
          <CheckCircle2 class="size-4 shrink-0 text-gc-600 mt-0.5" />
          <span class="text-ink">{{ asStr(asObj(item).text) }}</span>
        </li>
      </ul>
    </div>

    <!-- callout -->
    <div
      v-else-if="block.type === 'callout'"
      class="my-6 rounded-xl border-l-4 border-gc-500 bg-gc-50 px-5 py-4 text-sm text-ink"
      v-html="asStr(asObj(block.value).text || block.value)"
    />

    <!-- quote -->
    <blockquote
      v-else-if="block.type === 'quote'"
      class="my-6 border-l-4 border-gc-500 pl-5 italic text-ink"
    >{{ asStr(asObj(block.value).quote || block.value) }}</blockquote>

    <!-- image -->
    <figure
      v-else-if="block.type === 'image' && asObj(asObj(block.value).image).url"
      class="my-6"
    >
      <img
        :src="asStr(asObj(asObj(block.value).image).url)"
        :alt="asStr(asObj(block.value).alt_text)"
        class="w-full rounded-xl"
      />
      <figcaption
        v-if="asStr(asObj(block.value).caption)"
        class="mt-2 text-center text-xs text-graphite"
      >{{ asStr(asObj(block.value).caption) }}</figcaption>
    </figure>

    <!-- cta block (simple button) -->
    <div
      v-else-if="block.type === 'cta' && asStr(asObj(block.value).text)"
      class="my-6 not-prose"
    >
      <a
        :href="ctaUrl(asStr(asObj(block.value).url))"
        class="inline-flex items-center gap-2 rounded-xl bg-gc-600 px-6 py-3 text-sm font-bold text-white hover:bg-gc-700 transition-colors"
      >
        {{ asStr(asObj(block.value).text) }}
        <ArrowRight class="size-4" />
      </a>
    </div>

    <!-- faq -->
    <details
      v-else-if="block.type === 'faq'"
      class="my-3 group rounded-2xl border border-slate-200 bg-white shadow-card not-prose"
    >
      <summary class="flex cursor-pointer list-none items-center justify-between gap-4 px-6 py-4 text-sm font-semibold text-ink">
        {{ asStr(asObj(block.value).question) }}
        <span class="flex size-6 shrink-0 items-center justify-center rounded-full bg-slate-100 transition-transform group-open:rotate-45">+</span>
      </summary>
      <div class="px-6 pb-5 text-sm text-graphite leading-relaxed" v-html="asStr(asObj(block.value).answer)" />
    </details>

    <!-- divider -->
    <hr v-else-if="block.type === 'divider'" class="my-8 border-slate-200" />

  </template>
</template>

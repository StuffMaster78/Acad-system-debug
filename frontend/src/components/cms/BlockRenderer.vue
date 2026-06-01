<template>
  <div class="cms-blocks space-y-6">
    <template v-for="(block, i) in blocks" :key="block.id ?? i">

      <!-- Heading -->
      <component
        v-if="block.type === 'heading'"
        :is="(block.value as HeadingValue).level || 'h2'"
        class="font-bold text-ink"
        :class="{
          'text-3xl mt-10': (block.value as HeadingValue).level === 'h2',
          'text-2xl mt-8': (block.value as HeadingValue).level === 'h3',
          'text-xl mt-6': (block.value as HeadingValue).level === 'h4',
        }"
        v-html="(block.value as HeadingValue).text"
      />

      <!-- Paragraph / rich text -->
      <div
        v-else-if="block.type === 'paragraph'"
        class="prose prose-slate max-w-none leading-7 text-graphite"
        v-html="typeof block.value === 'string' ? block.value : (block.value as any).html ?? ''"
      />

      <!-- Image -->
      <figure v-else-if="block.type === 'image'" class="my-8">
        <img
          :src="(block.value as ImageValue).url ?? (block.value as any).meta?.download_url"
          :alt="(block.value as ImageValue).alt ?? ''"
          class="w-full rounded-xl object-cover shadow-sm"
          loading="lazy"
        />
        <figcaption v-if="(block.value as ImageValue).caption" class="mt-2 text-center text-xs text-graphite italic">
          {{ (block.value as ImageValue).caption }}
        </figcaption>
      </figure>

      <!-- Quote / Blockquote -->
      <blockquote v-else-if="block.type === 'quote'" class="my-8 border-l-4 border-berry pl-6">
        <p class="text-lg italic text-ink" v-html="(block.value as QuoteValue).text" />
        <cite v-if="(block.value as QuoteValue).attribution" class="mt-2 block text-sm text-graphite not-italic">
          — {{ (block.value as QuoteValue).attribution }}
        </cite>
      </blockquote>

      <!-- Callout / Alert -->
      <div
        v-else-if="block.type === 'callout'"
        class="flex gap-4 rounded-xl border p-5"
        :class="calloutClass((block.value as CalloutValue).type)"
      >
        <span class="text-xl">{{ calloutIcon((block.value as CalloutValue).type) }}</span>
        <div>
          <p v-if="(block.value as CalloutValue).title" class="mb-1 font-semibold text-ink">
            {{ (block.value as CalloutValue).title }}
          </p>
          <div class="text-sm leading-6" v-html="(block.value as CalloutValue).body" />
        </div>
      </div>

      <!-- FAQ -->
      <div v-else-if="block.type === 'faq'" class="space-y-3">
        <details
          v-for="(item, fi) in (block.value as FaqValue).items"
          :key="fi"
          class="group rounded-xl border border-slate-200 bg-white"
        >
          <summary class="flex cursor-pointer items-center justify-between gap-4 px-5 py-4 font-semibold text-ink select-none">
            {{ item.question }}
            <ChevronDown class="size-4 shrink-0 text-graphite transition-transform group-open:rotate-180" />
          </summary>
          <div class="border-t border-slate-100 px-5 py-4 text-sm leading-7 text-graphite" v-html="item.answer" />
        </details>
      </div>

      <!-- CTA button -->
      <div v-else-if="block.type === 'cta'" class="my-8 text-center">
        <a
          :href="(block.value as CtaValue).url"
          class="inline-flex items-center gap-2 rounded-xl bg-berry px-8 py-4 text-base font-bold text-white shadow-lg transition-all hover:bg-rose-700 hover:shadow-xl"
        >
          {{ (block.value as CtaValue).text }}
          <ArrowRight class="size-5" />
        </a>
        <p v-if="(block.value as CtaValue).subtext" class="mt-3 text-sm text-graphite">
          {{ (block.value as CtaValue).subtext }}
        </p>
      </div>

      <!-- Hero (service pages) -->
      <div
        v-else-if="block.type === 'hero'"
        class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-ink to-slate-700 px-8 py-16 text-white"
      >
        <h1 class="text-4xl font-extrabold leading-tight">{{ (block.value as HeroValue).heading }}</h1>
        <p v-if="(block.value as HeroValue).subheading" class="mt-4 max-w-2xl text-lg text-slate-300">
          {{ (block.value as HeroValue).subheading }}
        </p>
        <a
          v-if="(block.value as HeroValue).cta_text"
          :href="(block.value as HeroValue).cta_url ?? '/auth/register'"
          class="mt-8 inline-flex items-center gap-2 rounded-xl bg-berry px-7 py-3.5 font-bold text-white shadow-lg hover:bg-rose-700"
        >
          {{ (block.value as HeroValue).cta_text }}
          <ArrowRight class="size-4" />
        </a>
      </div>

      <!-- Trust strip -->
      <div v-else-if="block.type === 'trust_strip'" class="flex flex-wrap items-center justify-center gap-8 py-4">
        <div
          v-for="(item, ti) in (block.value as TrustStripValue).items"
          :key="ti"
          class="flex items-center gap-2 text-sm font-semibold text-graphite"
        >
          <CheckCircle class="size-5 text-signal" />
          {{ item.label }}
        </div>
      </div>

      <!-- Feature grid -->
      <div v-else-if="block.type === 'feature_grid'" class="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div
          v-for="(feat, fi) in (block.value as FeatureGridValue).features"
          :key="fi"
          class="rounded-xl border border-slate-200 bg-white p-6"
        >
          <p class="text-2xl">{{ feat.icon }}</p>
          <h3 class="mt-3 font-semibold text-ink">{{ feat.title }}</h3>
          <p class="mt-1 text-sm leading-6 text-graphite">{{ feat.body }}</p>
        </div>
      </div>

      <!-- Pricing table -->
      <div v-else-if="block.type === 'pricing_table'" class="overflow-x-auto rounded-xl border border-slate-200 bg-white">
        <table class="min-w-full text-sm">
          <thead class="border-b border-slate-200 bg-slate-50 text-left text-xs font-semibold uppercase tracking-wide text-graphite">
            <tr>
              <th class="px-5 py-3">Pages</th>
              <th class="px-5 py-3">Standard</th>
              <th class="px-5 py-3">Urgent</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr
              v-for="(row, ri) in (block.value as PricingTableValue).rows"
              :key="ri"
              class="hover:bg-slate-50"
            >
              <td class="px-5 py-3 font-medium text-ink">{{ row.pages }}</td>
              <td class="px-5 py-3 text-graphite">{{ row.standard }}</td>
              <td class="px-5 py-3 text-graphite">{{ row.urgent }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Testimonials -->
      <div v-else-if="block.type === 'testimonials'" class="grid gap-6 sm:grid-cols-2">
        <blockquote
          v-for="(t, ti) in (block.value as TestimonialsValue).items"
          :key="ti"
          class="rounded-xl border border-slate-200 bg-white p-6"
        >
          <div class="mb-3 flex gap-0.5">
            <Star v-for="s in 5" :key="s" class="size-4 fill-saffron text-saffron" />
          </div>
          <p class="text-sm leading-7 text-graphite italic">"{{ t.quote }}"</p>
          <footer class="mt-4 text-xs font-semibold text-ink">— {{ t.author }}<span v-if="t.context" class="font-normal text-graphite">, {{ t.context }}</span></footer>
        </blockquote>
      </div>

      <!-- Code block -->
      <div v-else-if="block.type === 'code'" class="overflow-x-auto rounded-xl bg-slate-900 p-5">
        <p v-if="(block.value as CodeValue).language" class="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
          {{ (block.value as CodeValue).language }}
        </p>
        <pre class="text-sm text-slate-100"><code>{{ (block.value as CodeValue).code }}</code></pre>
      </div>

      <!-- Divider -->
      <hr v-else-if="block.type === 'divider'" class="border-slate-200" />

      <!-- How it works -->
      <div v-else-if="block.type === 'how_it_works'" class="space-y-6">
        <h2 v-if="(block.value as HowItWorksValue).heading" class="text-2xl font-bold text-ink">
          {{ (block.value as HowItWorksValue).heading }}
        </h2>
        <ol class="space-y-4">
          <li
            v-for="(step, si) in (block.value as HowItWorksValue).steps"
            :key="si"
            class="flex gap-4"
          >
            <span class="flex size-8 shrink-0 items-center justify-center rounded-full bg-berry text-sm font-bold text-white">
              {{ si + 1 }}
            </span>
            <div>
              <p class="font-semibold text-ink">{{ step.title }}</p>
              <p class="mt-0.5 text-sm text-graphite">{{ step.body }}</p>
            </div>
          </li>
        </ol>
      </div>

      <!-- Guarantees -->
      <div v-else-if="block.type === 'guarantees'" class="grid gap-4 sm:grid-cols-2">
        <div
          v-for="(g, gi) in (block.value as GuaranteesValue).items"
          :key="gi"
          class="flex items-start gap-3 rounded-xl border border-emerald-100 bg-emerald-50 p-4"
        >
          <ShieldCheck class="mt-0.5 size-5 shrink-0 text-signal" />
          <div>
            <p class="font-semibold text-ink">{{ g.title }}</p>
            <p class="mt-0.5 text-sm text-graphite">{{ g.body }}</p>
          </div>
        </div>
      </div>

      <!-- Comparison table -->
      <div v-else-if="block.type === 'comparison_table'" class="overflow-x-auto rounded-xl border border-slate-200 bg-white">
        <table class="min-w-full text-sm">
          <thead class="border-b border-slate-200 bg-slate-50 text-left text-xs font-semibold text-graphite">
            <tr>
              <th class="px-5 py-3">Feature</th>
              <th v-for="col in (block.value as ComparisonValue).columns" :key="col" class="px-5 py-3">{{ col }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="(row, ri) in (block.value as ComparisonValue).rows" :key="ri" class="hover:bg-slate-50">
              <td class="px-5 py-3 font-medium text-ink">{{ row.feature }}</td>
              <td v-for="(val, vi) in row.values" :key="vi" class="px-5 py-3 text-graphite">
                <CheckCircle v-if="val === true" class="size-4 text-signal" />
                <span v-else-if="val === false" class="text-rose-400"></span>
                <span v-else>{{ val }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Fallback: raw JSON for unknown blocks (dev only) -->
      <details v-else class="rounded-lg border border-dashed border-amber-200 bg-amber-50 p-4 text-xs text-amber-800">
        <summary class="cursor-pointer font-mono font-semibold">Unknown block: {{ block.type }}</summary>
        <pre class="mt-2 overflow-x-auto">{{ JSON.stringify(block.value, null, 2) }}</pre>
      </details>

    </template>
  </div>
</template>

<script setup lang="ts">
import { ArrowRight, CheckCircle, ChevronDown, ShieldCheck, Star } from "@lucide/vue";
import type { WagtailBlock } from "@/api/cms";

defineProps<{ blocks: WagtailBlock[] }>();

// ── Block value type helpers ──────────────────────────────────────────────
interface HeadingValue { level: string; text: string }
interface ImageValue { url?: string; alt?: string; caption?: string }
interface QuoteValue { text: string; attribution?: string }
interface CalloutValue { type?: string; title?: string; body: string }
interface FaqValue { items: { question: string; answer: string }[] }
interface CtaValue { text: string; url: string; subtext?: string }
interface HeroValue { heading: string; subheading?: string; cta_text?: string; cta_url?: string }
interface TrustStripValue { items: { label: string }[] }
interface FeatureGridValue { features: { icon?: string; title: string; body: string }[] }
interface PricingTableValue { rows: { pages: string; standard: string; urgent: string }[] }
interface TestimonialsValue { items: { quote: string; author: string; context?: string }[] }
interface CodeValue { code: string; language?: string }
interface HowItWorksValue { heading?: string; steps: { title: string; body: string }[] }
interface GuaranteesValue { items: { title: string; body: string }[] }
interface ComparisonValue { columns: string[]; rows: { feature: string; values: (string | boolean)[] }[] }

function calloutClass(type?: string): string {
  if (type === "warning") return "border-amber-200 bg-amber-50 text-amber-900";
  if (type === "danger") return "border-rose-200 bg-rose-50 text-rose-900";
  if (type === "success") return "border-emerald-200 bg-emerald-50 text-emerald-900";
  return "border-blue-200 bg-blue-50 text-blue-900";
}

function calloutIcon(type?: string): string {
  if (type === "warning") return "️";
  if (type === "danger") return "";
  if (type === "success") return "";
  return "ℹ️";
}
</script>

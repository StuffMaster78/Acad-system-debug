<script setup lang="ts">
import { CheckCircle2, ArrowRight, Star, Zap, Shield, Circle, X } from '@lucide/vue'
import PricingCalculator from '~/components/ui/PricingCalculator.vue'
import type { CmsBlock } from '~/types/cms'

defineProps<{
  blocks: CmsBlock[]
}>()

const html = (value: unknown) => String(value ?? '')

const ctaClass = (style?: string) => {
  if (style === 'secondary') return 'bg-forest-950 text-white hover:bg-forest-900'
  if (style === 'outline') return 'border border-slate-300 bg-white text-ink hover:border-gc-300 hover:text-gc-700'
  return 'bg-gc-600 text-white hover:bg-gc-700'
}

// ── Heading helpers ──────────────────────────────────────────────────────────
const headingClass = (level: string) => ({
  h2: 'text-2xl font-bold text-ink',
  h3: 'text-xl font-semibold text-ink',
  h4: 'text-lg font-semibold text-ink',
}[level] ?? 'text-2xl font-bold text-ink')

// ── Icon list helpers ────────────────────────────────────────────────────────
const chipColor = (color: string) => ({
  brand:  'border-gc-200 bg-gc-50 text-gc-700',
  green:  'border-emerald-200 bg-emerald-50 text-emerald-700',
  amber:  'border-amber-200 bg-amber-50 text-amber-700',
  purple: 'border-violet-200 bg-violet-50 text-violet-700',
  slate:  'border-slate-200 bg-slate-50 text-slate-600',
}[color] ?? 'border-gc-200 bg-gc-50 text-gc-700')
</script>

<template>
  <section v-if="blocks.length" class="bg-white py-14">
    <div class="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
      <div class="space-y-10">
        <template v-for="block in blocks" :key="block.id ?? `${block.type}-${JSON.stringify(block.value).slice(0, 40)}`">
          <!-- ── Heading — accent variants ─────────────────────────────── -->
          <div v-if="block.type === 'heading'">
            <div
              v-if="(block.value as any).accent === 'bar'"
              class="border-l-4 border-gc-500 pl-4"
            >
              <component :is="(block.value as any).level || 'h2'" :class="headingClass((block.value as any).level)">
                {{ (block.value as any).text }}
              </component>
              <p v-if="(block.value as any).subtitle" class="mt-1 text-sm text-graphite">{{ (block.value as any).subtitle }}</p>
            </div>
            <div v-else-if="(block.value as any).accent === 'underline'" class="border-b-2 border-gc-200 pb-2">
              <component :is="(block.value as any).level || 'h2'" :class="headingClass((block.value as any).level)">
                {{ (block.value as any).text }}
              </component>
              <p v-if="(block.value as any).subtitle" class="mt-1 text-sm text-graphite">{{ (block.value as any).subtitle }}</p>
            </div>
            <div v-else-if="(block.value as any).accent === 'badge'" class="flex items-center gap-3">
              <span class="rounded-full bg-gc-100 px-3 py-1 text-xs font-bold uppercase tracking-wider text-gc-700">
                {{ (block.value as any).text }}
              </span>
            </div>
            <div v-else>
              <component :is="(block.value as any).level || 'h2'" :class="headingClass((block.value as any).level)">
                {{ (block.value as any).text }}
              </component>
              <p v-if="(block.value as any).subtitle" class="mt-1 text-sm text-graphite">{{ (block.value as any).subtitle }}</p>
            </div>
          </div>

          <div
            v-else-if="block.type === 'paragraph'"
            class="prose prose-slate max-w-none prose-a:text-gc-700 prose-strong:text-ink"
            v-html="html(block.value)"
          />

          <figure v-else-if="block.type === 'image' && (block.value as any).image" class="space-y-3">
            <img
              :src="(block.value as any).image.url"
              :alt="(block.value as any).alt_text || (block.value as any).image.title || ''"
              class="w-full rounded-2xl border border-slate-200 object-cover"
            >
            <figcaption v-if="(block.value as any).caption" class="text-center text-xs text-slate-500">
              {{ (block.value as any).caption }}
            </figcaption>
          </figure>

          <div v-else-if="block.type === 'list'" class="rounded-2xl border border-slate-200 bg-mist p-6">
            <ol v-if="(block.value as any).style === 'numbered'" class="list-decimal space-y-2 pl-5 text-sm text-graphite">
              <li v-for="item in (block.value as any).items || []" :key="html(item)" v-html="html(item)" />
            </ol>
            <ul v-else class="list-disc space-y-2 pl-5 text-sm text-graphite">
              <li v-for="item in (block.value as any).items || []" :key="html(item)" v-html="html(item)" />
            </ul>
          </div>

          <div v-else-if="block.type === 'checklist'" class="rounded-2xl border border-slate-200 bg-white p-6 shadow-card">
            <h2 class="text-xl font-bold text-ink">{{ (block.value as any).title }}</h2>
            <ul class="mt-5 space-y-4">
              <li v-for="item in (block.value as any).items || []" :key="item.text" class="text-sm text-graphite">
                <p class="font-semibold text-ink">{{ item.text }}</p>
                <p v-if="item.detail" class="mt-1 leading-relaxed">{{ item.detail }}</p>
              </li>
            </ul>
          </div>

          <!-- ── Icon List ─────────────────────────────────────────────────── -->
          <div v-else-if="block.type === 'icon_list'">
            <!-- Grid layout -->
            <div
              v-if="(block.value as any).style === 'grid'"
              class="grid gap-3 sm:grid-cols-2"
            >
              <div
                v-for="(item, i) in (block.value as any).items || []"
                :key="i"
                class="flex items-start gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-card"
              >
                <span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gc-100 mt-0.5">
                  <CheckCircle2 v-if="(block.value as any).icon === 'check' || !(block.value as any).icon" class="size-3.5 text-gc-600" />
                  <ArrowRight    v-else-if="(block.value as any).icon === 'arrow'"     class="size-3.5 text-gc-600" />
                  <Star          v-else-if="(block.value as any).icon === 'star'"      class="size-3.5 text-gc-600" />
                  <Zap           v-else-if="(block.value as any).icon === 'lightning'" class="size-3.5 text-gc-600" />
                  <Shield        v-else-if="(block.value as any).icon === 'shield'"    class="size-3.5 text-gc-600" />
                  <Circle        v-else                                                class="size-2.5 fill-gc-600 text-gc-600" />
                </span>
                <div class="text-sm text-graphite leading-relaxed" v-html="html(item)" />
              </div>
            </div>
            <!-- Cards layout -->
            <div v-else-if="(block.value as any).style === 'cards'" class="space-y-2">
              <div
                v-for="(item, i) in (block.value as any).items || []"
                :key="i"
                class="flex items-start gap-3 rounded-xl border border-slate-100 bg-mist px-5 py-4"
              >
                <CheckCircle2 v-if="(block.value as any).icon === 'check' || !(block.value as any).icon" class="size-4 shrink-0 mt-0.5 text-gc-600" />
                <ArrowRight    v-else-if="(block.value as any).icon === 'arrow'"     class="size-4 shrink-0 mt-0.5 text-gc-600" />
                <Star          v-else-if="(block.value as any).icon === 'star'"      class="size-4 shrink-0 mt-0.5 text-gc-600" />
                <Zap           v-else-if="(block.value as any).icon === 'lightning'" class="size-4 shrink-0 mt-0.5 text-gc-600" />
                <Shield        v-else-if="(block.value as any).icon === 'shield'"    class="size-4 shrink-0 mt-0.5 text-gc-600" />
                <Circle        v-else                                                class="size-2.5 shrink-0 mt-1.5 fill-gc-500 text-gc-500" />
                <div class="text-sm text-graphite leading-relaxed" v-html="html(item)" />
              </div>
            </div>
            <!-- Simple layout (default) -->
            <ul v-else class="space-y-3">
              <li
                v-for="(item, i) in (block.value as any).items || []"
                :key="i"
                class="flex items-start gap-3 text-sm text-graphite"
              >
                <CheckCircle2 v-if="(block.value as any).icon === 'check' || !(block.value as any).icon" class="size-4 shrink-0 mt-0.5 text-gc-600" />
                <ArrowRight    v-else-if="(block.value as any).icon === 'arrow'"     class="size-4 shrink-0 mt-0.5 text-gc-600" />
                <Star          v-else-if="(block.value as any).icon === 'star'"      class="size-4 shrink-0 mt-0.5 text-gc-600" />
                <Zap           v-else-if="(block.value as any).icon === 'lightning'" class="size-4 shrink-0 mt-0.5 text-gc-600" />
                <Shield        v-else-if="(block.value as any).icon === 'shield'"    class="size-4 shrink-0 mt-0.5 text-gc-600" />
                <Circle        v-else                                                class="size-2.5 shrink-0 mt-1.5 fill-gc-500 text-gc-500" />
                <div class="leading-relaxed" v-html="html(item)" />
              </li>
            </ul>
          </div>

          <!-- ── Numbered List ──────────────────────────────────────────────── -->
          <div v-else-if="block.type === 'numbered_list'" class="space-y-4">
            <h3 v-if="(block.value as any).heading" class="text-xl font-bold text-ink">
              {{ (block.value as any).heading }}
            </h3>
            <!-- Steps: vertically connected -->
            <ol v-if="(block.value as any).style === 'steps'" class="space-y-0">
              <li
                v-for="(item, i) in (block.value as any).items || []"
                :key="i"
                class="flex gap-4"
              >
                <div class="flex flex-col items-center">
                  <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gc-600 text-xs font-bold text-white z-10">
                    {{ i + 1 }}
                  </span>
                  <div
                    v-if="i < ((block.value as any).items || []).length - 1"
                    class="w-0.5 flex-1 bg-gc-200 my-1"
                  />
                </div>
                <div class="pb-6 min-w-0">
                  <p class="text-sm font-semibold text-ink">{{ item.title }}</p>
                  <div v-if="item.description" class="mt-1 text-sm text-graphite leading-relaxed" v-html="html(item.description)" />
                </div>
              </li>
            </ol>
            <!-- Counter: large faded numbers -->
            <ol v-else-if="(block.value as any).style === 'counter'" class="space-y-6">
              <li v-for="(item, i) in (block.value as any).items || []" :key="i" class="flex gap-4 items-start">
                <span class="text-5xl font-black text-gc-100 leading-none w-14 shrink-0 text-right tabular-nums select-none">
                  {{ String(i + 1).padStart(2, '0') }}
                </span>
                <div class="pt-1 min-w-0">
                  <p class="text-sm font-semibold text-ink">{{ item.title }}</p>
                  <div v-if="item.description" class="mt-1 text-sm text-graphite leading-relaxed" v-html="html(item.description)" />
                </div>
              </li>
            </ol>
            <!-- Badge: numbered circles (default) -->
            <ol v-else class="space-y-4">
              <li v-for="(item, i) in (block.value as any).items || []" :key="i" class="flex gap-4 items-start">
                <span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 border-gc-600 text-xs font-bold text-gc-600 mt-0.5">
                  {{ i + 1 }}
                </span>
                <div class="min-w-0">
                  <p class="text-sm font-semibold text-ink">{{ item.title }}</p>
                  <div v-if="item.description" class="mt-1 text-sm text-graphite leading-relaxed" v-html="html(item.description)" />
                </div>
              </li>
            </ol>
          </div>

          <!-- ── Pro / Con ──────────────────────────────────────────────────── -->
          <div v-else-if="block.type === 'pro_con'" class="space-y-4">
            <h3 v-if="(block.value as any).heading" class="text-xl font-bold text-ink">
              {{ (block.value as any).heading }}
            </h3>
            <div class="grid gap-4 sm:grid-cols-2">
              <!-- Pros -->
              <div class="rounded-2xl border border-emerald-200 bg-emerald-50 p-5">
                <p class="mb-3 text-sm font-bold text-emerald-800">
                  {{ (block.value as any).pro_heading || 'Pros' }}
                </p>
                <ul class="space-y-2">
                  <li
                    v-for="(pro, i) in (block.value as any).pros || []"
                    :key="i"
                    class="flex items-start gap-2 text-sm text-emerald-900"
                  >
                    <CheckCircle2 class="size-4 shrink-0 mt-0.5 text-emerald-600" />
                    {{ pro }}
                  </li>
                </ul>
              </div>
              <!-- Cons -->
              <div class="rounded-2xl border border-red-200 bg-red-50 p-5">
                <p class="mb-3 text-sm font-bold text-red-800">
                  {{ (block.value as any).con_heading || 'Cons' }}
                </p>
                <ul class="space-y-2">
                  <li
                    v-for="(con, i) in (block.value as any).cons || []"
                    :key="i"
                    class="flex items-start gap-2 text-sm text-red-900"
                  >
                    <X class="size-4 shrink-0 mt-0.5 text-red-400" />
                    {{ con }}
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <!-- ── Chips / Tags ───────────────────────────────────────────────── -->
          <div v-else-if="block.type === 'chips'" class="space-y-3">
            <p v-if="(block.value as any).heading" class="text-base font-semibold text-ink">
              {{ (block.value as any).heading }}
            </p>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="(chip, i) in (block.value as any).items || []"
                :key="i"
                class="rounded-full border px-3 py-1.5 text-xs font-medium"
                :class="chipColor((block.value as any).color)"
              >{{ chip }}</span>
            </div>
          </div>

          <div v-else-if="block.type === 'feature_grid'" class="space-y-5">
            <h2 class="text-2xl font-bold text-ink">{{ (block.value as any).heading }}</h2>
            <div class="grid gap-4 sm:grid-cols-2">
              <div v-for="feature in (block.value as any).features || []" :key="feature.title" class="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
                <p class="text-sm font-bold text-ink">{{ feature.title }}</p>
                <div class="mt-2 text-sm leading-relaxed text-graphite" v-html="html(feature.description)" />
              </div>
            </div>
          </div>

          <div v-else-if="block.type === 'how_it_works'" class="space-y-5">
            <h2 class="text-2xl font-bold text-ink">{{ (block.value as any).heading }}</h2>
            <div class="space-y-4">
              <div v-for="step in (block.value as any).steps || []" :key="`${step.step_number}-${step.title}`" class="flex gap-4">
                <span class="flex size-8 shrink-0 items-center justify-center rounded-full border-2 border-gc-600 text-xs font-bold text-gc-600">{{ step.step_number }}</span>
                <div>
                  <p class="text-sm font-semibold text-ink">{{ step.title }}</p>
                  <div class="mt-1 text-sm leading-relaxed text-graphite" v-html="html(step.description)" />
                </div>
              </div>
            </div>
          </div>

          <div v-else-if="block.type === 'stats_highlight'" class="rounded-2xl bg-forest-950 p-6 text-white">
            <div class="grid gap-4 sm:grid-cols-3">
              <div v-for="stat in (block.value as any).stats || []" :key="stat.label">
                <p class="text-3xl font-extrabold">{{ stat.value }}</p>
                <p class="mt-1 text-sm text-slate-300">{{ stat.label }}</p>
              </div>
            </div>
            <p v-if="(block.value as any).supporting_text" class="mt-5 text-sm text-slate-300">
              {{ (block.value as any).supporting_text }}
            </p>
          </div>

          <div v-else-if="block.type === 'pricing_table'" class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-card">
            <div class="border-b border-slate-200 bg-mist px-5 py-4">
              <h2 class="text-xl font-bold text-ink">{{ (block.value as any).heading }}</h2>
            </div>
            <div class="overflow-x-auto">
              <table class="min-w-full text-left text-sm">
                <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    <th class="px-5 py-3">Service</th>
                    <th class="px-5 py-3">Price</th>
                    <th class="px-5 py-3">Turnaround</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                  <tr v-for="row in (block.value as any).rows || []" :key="`${row.service}-${row.price}`">
                    <td class="px-5 py-3 font-medium text-ink">{{ row.service }}</td>
                    <td class="px-5 py-3 text-graphite">{{ row.price }}</td>
                    <td class="px-5 py-3 text-graphite">{{ row.turnaround }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div v-else-if="block.type === 'comparison_table'" class="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-card">
            <div class="border-b border-slate-200 bg-mist px-5 py-4">
              <h2 class="text-xl font-bold text-ink">{{ (block.value as any).heading }}</h2>
            </div>
            <div class="overflow-x-auto">
              <table class="min-w-full text-left text-sm">
                <thead class="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    <th class="px-5 py-3">Feature</th>
                    <th class="px-5 py-3">GradeCrest</th>
                    <th class="px-5 py-3">{{ (block.value as any).competitor_name || 'Other services' }}</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-100">
                  <tr v-for="row in (block.value as any).rows || []" :key="row.feature">
                    <td class="px-5 py-3 font-medium text-ink">{{ row.feature }}</td>
                    <td class="px-5 py-3 text-graphite">{{ row.us }}</td>
                    <td class="px-5 py-3 text-graphite">{{ row.competitor }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div v-else-if="block.type === 'testimonials'" class="space-y-5">
            <h2 class="text-2xl font-bold text-ink">{{ (block.value as any).heading }}</h2>
            <div class="grid gap-4 sm:grid-cols-2">
              <blockquote v-for="testimonial in (block.value as any).testimonials || []" :key="testimonial.author_name" class="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
                <div class="text-sm leading-relaxed text-graphite" v-html="html(testimonial.quote)" />
                <footer class="mt-4 text-sm font-semibold text-ink">{{ testimonial.author_name }}</footer>
              </blockquote>
            </div>
          </div>

          <div v-else-if="block.type === 'guarantees'" class="space-y-5">
            <h2 class="text-2xl font-bold text-ink">{{ (block.value as any).heading }}</h2>
            <div class="grid gap-4 sm:grid-cols-2">
              <div v-for="guarantee in (block.value as any).guarantees || []" :key="guarantee.title" class="rounded-2xl border border-slate-200 bg-mist p-5">
                <p class="text-sm font-bold text-ink">{{ guarantee.title }}</p>
                <p class="mt-2 text-sm leading-relaxed text-graphite">{{ guarantee.description }}</p>
              </div>
            </div>
          </div>

          <details v-else-if="block.type === 'faq'" class="group rounded-2xl border border-slate-200 bg-white shadow-card">
            <summary class="flex cursor-pointer list-none items-center justify-between gap-4 px-6 py-4 text-sm font-semibold text-ink">
              {{ (block.value as any).question }}
              <span class="flex size-6 shrink-0 items-center justify-center rounded-full bg-slate-100 transition-transform group-open:rotate-45">+</span>
            </summary>
            <div class="px-6 pb-5 text-sm leading-relaxed text-graphite" v-html="html((block.value as any).answer)" />
          </details>

          <div v-else-if="block.type === 'cta'" class="rounded-2xl border border-slate-200 bg-mist p-6 text-center">
            <a :href="(block.value as any).url" class="inline-flex items-center justify-center rounded-xl px-6 py-3 text-sm font-bold transition-colors" :class="ctaClass((block.value as any).style)">
              {{ (block.value as any).text }}
            </a>
          </div>

          <div v-else-if="block.type === 'calculator'" class="rounded-2xl border border-slate-200 bg-white p-5 shadow-card">
            <div v-if="(block.value as any).title || (block.value as any).subtitle" class="mb-4">
              <h2 v-if="(block.value as any).title" class="text-xl font-bold text-ink">{{ (block.value as any).title }}</h2>
              <p v-if="(block.value as any).subtitle" class="mt-1 text-sm text-graphite">{{ (block.value as any).subtitle }}</p>
            </div>
            <PricingCalculator />
          </div>
        </template>
      </div>
    </div>
  </section>
</template>

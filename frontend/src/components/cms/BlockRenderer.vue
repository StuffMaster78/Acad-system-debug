<template>
  <div class="cms-blocks space-y-6">
    <template v-for="(block, i) in blocks" :key="block.id ?? i">

      <!-- Heading -->
      <component
        v-if="block.type === 'heading'"
        :is="(block.value as HeadingValue).level || 'h2'"
        :id="headingId((block.value as HeadingValue).text)"
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
          class="inline-flex items-center gap-2 rounded-xl px-8 py-4 text-base font-bold shadow-lg transition-all"
          :class="{
            'bg-berry text-white hover:bg-rose-700 hover:shadow-xl':
              !(block.value as CtaValue).style || (block.value as CtaValue).style === 'primary',
            'bg-slate-100 text-ink hover:bg-slate-200':
              (block.value as CtaValue).style === 'secondary',
            'border-2 border-berry bg-transparent text-berry hover:bg-berry hover:text-white':
              (block.value as CtaValue).style === 'outline',
          }"
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
        <h1 class="text-4xl font-extrabold leading-tight">{{ (block.value as HeroValue).headline }}</h1>
        <p v-if="(block.value as HeroValue).subheadline" class="mt-4 max-w-2xl text-lg text-slate-300">
          {{ (block.value as HeroValue).subheadline }}
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

      <!-- Key Takeaways -->
      <div
        v-else-if="block.type === 'key_takeaways'"
        class="my-6 rounded-xl border border-emerald-200 bg-emerald-50 p-5"
      >
        <div class="flex items-center gap-2 text-emerald-800">
          <svg class="size-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          <p class="text-sm font-semibold uppercase tracking-wide">
            {{ (block.value as KeyTakeawaysValue).heading || 'Key Takeaways' }}
          </p>
        </div>
        <ul class="mt-3 space-y-2">
          <li
            v-for="(item, i) in (block.value as KeyTakeawaysValue).items"
            :key="i"
            class="flex items-start gap-2.5 text-sm leading-6 text-emerald-900"
          >
            <svg class="mt-0.5 size-4 shrink-0 text-emerald-500" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/></svg>
            {{ item }}
          </li>
        </ul>
      </div>

      <!-- Table of Contents -->
      <nav
        v-else-if="block.type === 'toc'"
        class="my-6 rounded-xl border border-slate-200 bg-slate-50 p-5"
        aria-label="Table of contents"
      >
        <p class="text-sm font-semibold text-ink">
          {{ (block.value as TocValue).heading || 'In This Article' }}
        </p>
        <ol class="mt-3 space-y-1.5">
          <li
            v-for="(entry, i) in (block.value as TocValue).entries"
            :key="i"
            class="flex items-baseline gap-2 text-sm"
          >
            <span class="min-w-[1.25rem] text-xs font-semibold text-slate-400">{{ i + 1 }}.</span>
            <a
              :href="`#${entry.anchor}`"
              class="text-signal hover:underline"
            >{{ entry.label }}</a>
          </li>
        </ol>
      </nav>

      <!-- Author Review Badge -->
      <div
        v-else-if="block.type === 'author_review'"
        class="my-4 flex items-start gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3"
      >
        <img
          v-if="(block.value as AuthorReviewValue).photo?.meta?.download_url"
          :src="(block.value as AuthorReviewValue).photo!.meta!.download_url"
          :alt="(block.value as AuthorReviewValue).reviewer_name"
          class="size-10 shrink-0 rounded-full object-cover"
        />
        <div
          v-else
          class="flex size-10 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-bold text-graphite"
        >
          {{ (block.value as AuthorReviewValue).reviewer_name.charAt(0) }}
        </div>
        <div class="min-w-0 text-xs leading-5 text-graphite">
          <span class="text-slate-400">Reviewed by </span>
          <component
            :is="(block.value as AuthorReviewValue).reviewer_url ? 'a' : 'span'"
            :href="(block.value as AuthorReviewValue).reviewer_url || undefined"
            class="font-semibold text-ink hover:underline"
          >{{ (block.value as AuthorReviewValue).reviewer_name }}</component>
          <span class="mx-1 text-slate-300">·</span>
          <span>{{ (block.value as AuthorReviewValue).credentials }}</span>
          <span class="mx-1 text-slate-300">·</span>
          <time class="text-slate-400">Updated {{ (block.value as AuthorReviewValue).review_date }}</time>
        </div>
      </div>

      <!-- Disclaimer -->
      <div
        v-else-if="block.type === 'disclaimer'"
        class="my-6 flex items-start gap-3 rounded-xl border px-4 py-3 text-sm leading-6"
        :class="disclaimerClass((block.value as DisclaimerValue).style)"
      >
        <span class="mt-0.5 shrink-0 text-base leading-none">{{ disclaimerIcon((block.value as DisclaimerValue).style) }}</span>
        <div class="prose-sm" v-html="(block.value as DisclaimerValue).text" />
      </div>

      <!-- Checklist -->
      <div v-else-if="block.type === 'checklist'" class="my-6 rounded-xl border border-slate-200 bg-white p-5">
        <p class="font-semibold text-ink">{{ (block.value as ChecklistValue).title }}</p>
        <ul class="mt-4 space-y-3">
          <li
            v-for="(item, i) in (block.value as ChecklistValue).items"
            :key="i"
            class="flex items-start gap-3"
          >
            <span class="mt-0.5 flex size-5 shrink-0 items-center justify-center rounded border-2 border-slate-300 bg-white">
              <svg class="size-3 text-transparent" fill="none" viewBox="0 0 12 12" stroke="currentColor" stroke-width="2.5"><path stroke-linecap="round" stroke-linejoin="round" d="M2 6l3 3 5-5"/></svg>
            </span>
            <div>
              <p class="text-sm leading-6 text-ink">{{ item.text }}</p>
              <p v-if="item.detail" class="mt-0.5 text-xs text-graphite">{{ item.detail }}</p>
            </div>
          </li>
        </ul>
      </div>

      <!-- Stats Highlight -->
      <div v-else-if="block.type === 'stats_highlight'" class="my-6">
        <div class="grid gap-4" :class="`sm:grid-cols-${Math.min((block.value as StatsHighlightValue).stats.length, 4)}`">
          <div
            v-for="(stat, i) in (block.value as StatsHighlightValue).stats"
            :key="i"
            class="rounded-xl border border-slate-200 bg-white p-5 text-center"
          >
            <p class="text-3xl font-extrabold text-ink">{{ stat.value }}</p>
            <p class="mt-1 text-sm text-graphite">{{ stat.label }}</p>
          </div>
        </div>
        <p v-if="(block.value as StatsHighlightValue).supporting_text" class="mt-3 text-center text-xs text-graphite">
          {{ (block.value as StatsHighlightValue).supporting_text }}
        </p>
      </div>

      <!-- Before & After -->
      <div v-else-if="block.type === 'before_after'" class="my-6">
        <p v-if="(block.value as BeforeAfterValue).heading" class="mb-3 font-semibold text-ink">
          {{ (block.value as BeforeAfterValue).heading }}
        </p>
        <div class="grid gap-3 sm:grid-cols-2">
          <div class="rounded-xl border border-rose-200 bg-rose-50">
            <div class="rounded-t-xl bg-rose-100 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-rose-700">
              {{ (block.value as BeforeAfterValue).label_before }}
            </div>
            <div class="px-4 py-4 text-sm leading-7 text-ink prose-sm" v-html="(block.value as BeforeAfterValue).content_before" />
          </div>
          <div class="rounded-xl border border-emerald-200 bg-emerald-50">
            <div class="rounded-t-xl bg-emerald-100 px-4 py-2 text-xs font-semibold uppercase tracking-wide text-emerald-700">
              {{ (block.value as BeforeAfterValue).label_after }}
            </div>
            <div class="px-4 py-4 text-sm leading-7 text-ink prose-sm" v-html="(block.value as BeforeAfterValue).content_after" />
          </div>
        </div>
        <p v-if="(block.value as BeforeAfterValue).caption" class="mt-2 text-center text-xs text-graphite">
          {{ (block.value as BeforeAfterValue).caption }}
        </p>
      </div>

      <!-- Sample Excerpt -->
      <div v-else-if="block.type === 'sample_excerpt'" class="my-6 rounded-xl border border-slate-200 bg-white">
        <div class="flex flex-wrap items-center gap-2 border-b border-slate-100 px-5 py-3">
          <p v-if="(block.value as SampleExcerptValue).title" class="text-sm font-semibold text-ink">
            {{ (block.value as SampleExcerptValue).title }}
          </p>
          <span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-graphite">
            {{ FORMATTING_LABELS[(block.value as SampleExcerptValue).formatting_style] ?? (block.value as SampleExcerptValue).formatting_style }}
          </span>
          <span class="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-graphite">
            {{ LEVEL_LABELS[(block.value as SampleExcerptValue).academic_level] ?? (block.value as SampleExcerptValue).academic_level }}
          </span>
        </div>
        <div class="px-5 py-4 font-serif text-sm leading-7 text-ink" v-html="(block.value as SampleExcerptValue).excerpt" />
        <div v-if="(block.value as SampleExcerptValue).attachment" class="border-t border-slate-100 px-5 py-3">
          <a
            :href="`/resources/${(block.value as SampleExcerptValue).attachment!.slug}`"
            class="inline-flex items-center gap-1.5 text-sm font-semibold text-signal hover:underline"
          >
            <svg class="size-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
            {{ (block.value as SampleExcerptValue).download_cta || 'Download Full Sample' }}
          </a>
        </div>
      </div>

      <!-- Definition -->
      <div v-else-if="block.type === 'definition'" class="my-4 rounded-xl border-l-4 border-signal bg-white px-5 py-4">
        <p class="text-sm font-bold text-ink">
          {{ (block.value as DefinitionValue).term }}
          <span class="ml-1 text-xs font-normal italic text-graphite">n.</span>
        </p>
        <div class="mt-1 text-sm leading-6 text-graphite" v-html="(block.value as DefinitionValue).definition" />
        <p v-if="(block.value as DefinitionValue).example" class="mt-2 text-xs italic text-slate-400">
          "{{ (block.value as DefinitionValue).example }}"
        </p>
      </div>

      <!-- Timeline -->
      <div v-else-if="block.type === 'timeline'" class="my-6">
        <p v-if="(block.value as TimelineValue).heading" class="mb-4 text-lg font-bold text-ink">
          {{ (block.value as TimelineValue).heading }}
        </p>
        <ol class="relative border-l-2 border-slate-200 space-y-6 pl-6">
          <li
            v-for="(entry, i) in (block.value as TimelineValue).entries"
            :key="i"
            class="relative"
          >
            <span class="absolute -left-[1.4375rem] flex size-5 items-center justify-center rounded-full border-2 border-signal bg-white text-xs font-bold text-signal ring-4 ring-white">
              {{ i + 1 }}
            </span>
            <p class="text-xs font-semibold uppercase tracking-wide text-signal">{{ entry.date_label }}</p>
            <p class="mt-0.5 font-semibold text-ink">{{ entry.title }}</p>
            <div class="mt-1 text-sm leading-6 text-graphite" v-html="entry.description" />
          </li>
        </ol>
      </div>

      <!-- Embed -->
      <figure v-else-if="block.type === 'embed'" class="my-6">
        <iframe
          v-if="safeEmbedUrl((block.value as EmbedValue).embed_url)"
          :src="safeEmbedUrl((block.value as EmbedValue).embed_url)!"
          :height="`${(block.value as EmbedValue).height ?? 480}`"
          class="w-full rounded-xl border border-slate-200"
          sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
          loading="lazy"
          referrerpolicy="no-referrer"
        />
        <div v-else class="flex h-32 items-center justify-center rounded-xl border border-dashed border-slate-200 bg-slate-50 text-sm text-graphite">
          Embed domain not allowed.
        </div>
        <figcaption v-if="(block.value as EmbedValue).caption" class="mt-2 text-center text-xs text-graphite">
          {{ (block.value as EmbedValue).caption }}
        </figcaption>
      </figure>

      <!-- Data table -->
      <figure v-else-if="block.type === 'table'" class="my-6 overflow-x-auto">
        <table class="min-w-full rounded-xl border border-slate-200 bg-white text-sm">
          <thead v-if="(block.value as TableValue).table?.first_row_is_table_header && (block.value as TableValue).table?.data?.length">
            <tr class="border-b border-slate-200 bg-slate-50">
              <th
                v-for="(cell, ci) in (block.value as TableValue).table.data[0]"
                :key="ci"
                class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-graphite"
              >{{ cell }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr
              v-for="(row, ri) in tableBodyRows(block.value as TableValue)"
              :key="ri"
              class="hover:bg-slate-50"
            >
              <td
                v-for="(cell, ci) in row"
                :key="ci"
                class="px-4 py-3 text-graphite"
                :class="(block.value as TableValue).table?.first_col_is_header && ci === 0 ? 'font-semibold text-ink' : ''"
              >{{ cell }}</td>
            </tr>
          </tbody>
        </table>
        <figcaption
          v-if="(block.value as TableValue).caption"
          class="mt-2 text-center text-xs text-graphite"
        >{{ (block.value as TableValue).caption }}</figcaption>
      </figure>

      <!-- Chart -->
      <figure v-else-if="block.type === 'chart'" class="my-6">
        <p v-if="(block.value as ChartValue).title" class="mb-2 text-center text-sm font-semibold text-ink">
          {{ (block.value as ChartValue).title }}
        </p>
        <AppChart :option="buildChartOption(block.value as ChartValue)" height="300px" />
        <figcaption
          v-if="(block.value as ChartValue).caption"
          class="mt-2 text-center text-xs text-graphite"
        >{{ (block.value as ChartValue).caption }}</figcaption>
      </figure>

      <!-- Pricing Calculator (interactive, calls pricing API) -->
      <PricingCalculator
        v-else-if="block.type === 'calculator'"
        :title="(block.value as CalculatorValue).title || undefined"
        :subtitle="(block.value as CalculatorValue).subtitle || undefined"
        :service-code="(block.value as CalculatorValue).service_code || 'standard_paper'"
        :default-pages="(block.value as CalculatorValue).default_pages ?? 1"
        :default-deadline-hours="(block.value as CalculatorValue).default_deadline_hours ?? 48"
        :default-academic-level-code="(block.value as CalculatorValue).default_academic_level_code || ''"
        :default-paper-type-code="(block.value as CalculatorValue).default_paper_type_code || ''"
        :show-line-breakdown="(block.value as CalculatorValue).show_line_breakdown !== 'no'"
        :cta-text="(block.value as CalculatorValue).cta_text || 'Place Order'"
        :cta-url="(block.value as CalculatorValue).cta_url || '/auth/register'"
      />

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
import type { EChartsOption } from "echarts";
import AppChart from "@/components/ui/AppChart.vue";
import PricingCalculator from "@/components/cms/PricingCalculator.vue";
import type { WagtailBlock } from "@/api/cms";

defineProps<{ blocks: WagtailBlock[] }>();

// ── Block value type helpers ──────────────────────────────────────────────
interface HeadingValue { level: string; text: string }
interface ImageValue { url?: string; alt?: string; caption?: string }
interface QuoteValue { text: string; attribution?: string }
interface CalloutValue { type?: string; title?: string; body: string }
interface FaqValue { items: { question: string; answer: string }[] }
interface CtaValue { text: string; url: string; subtext?: string; style?: 'primary' | 'secondary' | 'outline' }
interface HeroValue { headline: string; subheadline?: string; cta_text?: string; cta_url?: string; background_image?: unknown }
interface TrustStripValue { items: { label: string }[] }
interface FeatureGridValue { features: { icon?: string; title: string; body: string }[] }
interface PricingTableValue { rows: { pages: string; standard: string; urgent: string }[] }
interface TestimonialsValue { items: { quote: string; author: string; context?: string }[] }
interface CodeValue { code: string; language?: string }
interface HowItWorksValue { heading?: string; steps: { title: string; body: string }[] }
interface GuaranteesValue { items: { title: string; body: string }[] }
interface ComparisonValue { columns: string[]; rows: { feature: string; values: (string | boolean)[] }[] }
interface TableInner { data: string[][]; first_row_is_table_header: boolean; first_col_is_header: boolean }
interface TableValue { caption?: string; table: TableInner }
interface ChartDataset { label: string; values: string; color?: string }
interface ChartValue { chart_type: string; title?: string; caption?: string; x_labels: string; datasets: ChartDataset[] }
interface KeyTakeawaysValue { heading?: string; items: string[] }
interface TocEntry { label: string; anchor: string }
interface TocValue { heading?: string; entries: TocEntry[] }
interface AuthorReviewValue { reviewer_name: string; credentials: string; review_date: string; photo?: { meta?: { download_url?: string } }; reviewer_url?: string }
interface DisclaimerValue { style: string; text: string }
interface ChecklistItem { text: string; detail?: string }
interface ChecklistValue { title: string; items: ChecklistItem[] }
interface StatItem { value: string; label: string }
interface StatsHighlightValue { stats: StatItem[]; supporting_text?: string }
interface BeforeAfterValue { heading?: string; label_before: string; content_before: string; label_after: string; content_after: string; caption?: string }
interface SampleExcerptValue { title?: string; formatting_style: string; academic_level: string; excerpt: string; attachment?: { title?: string; slug?: string }; download_cta?: string }
interface DefinitionValue { term: string; definition: string; example?: string }
interface TimelineEntry { date_label: string; title: string; description: string }
interface TimelineValue { heading?: string; entries: TimelineEntry[] }
interface EmbedValue { embed_url: string; height?: number; caption?: string }
interface CalculatorValue {
  title?: string; subtitle?: string; service_code?: string;
  default_pages?: number; default_deadline_hours?: number;
  default_academic_level_code?: string; default_paper_type_code?: string;
  show_line_breakdown?: "yes" | "no"; cta_text?: string; cta_url?: string;
}

function headingId(text: string): string {
  return text.toLowerCase().replace(/\s+/g, "-").replace(/[^a-z0-9-]/g, "").slice(0, 60);
}

function tableBodyRows(v: TableValue): string[][] {
  const rows = v.table?.data ?? [];
  return v.table?.first_row_is_table_header ? rows.slice(1) : rows;
}

const CHART_PALETTE = ["#7c3aed", "#0ea5e9", "#10b981", "#f59e0b", "#f43f5e"];

function buildChartOption(v: ChartValue): EChartsOption {
  const labels = v.x_labels?.split(",").map((s) => s.trim()) ?? [];
  const isPie = v.chart_type === "pie" || v.chart_type === "doughnut";

  if (isPie) {
    const ds = v.datasets?.[0];
    const nums = ds?.values?.split(",").map((s) => Number(s.trim())) ?? [];
    const pieData = labels.map((name, i) => ({ name, value: nums[i] ?? 0 }));
    return {
      tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
      series: [{
        type: v.chart_type === "doughnut" ? "pie" : "pie",
        radius: v.chart_type === "doughnut" ? ["40%", "70%"] : "60%",
        data: pieData,
        itemStyle: { borderRadius: 4 },
      }],
    };
  }

  const series = (v.datasets ?? []).map((ds, i) => ({
    name: ds.label,
    type: (v.chart_type === "area" ? "line" : v.chart_type) as "bar" | "line",
    data: ds.values?.split(",").map((s) => Number(s.trim())) ?? [],
    smooth: v.chart_type === "line" || v.chart_type === "area",
    areaStyle: v.chart_type === "area" ? { opacity: 0.15 } : undefined,
    itemStyle: { color: ds.color || CHART_PALETTE[i % CHART_PALETTE.length] },
    lineStyle: ds.color ? { color: ds.color } : undefined,
  }));

  return {
    tooltip: { trigger: "axis" },
    legend: series.length > 1 ? { bottom: 0, data: series.map((s) => s.name) } : undefined,
    grid: { left: 50, right: 20, top: 10, bottom: series.length > 1 ? 36 : 20 },
    xAxis: { type: "category", data: labels, axisLabel: { rotate: labels.length > 6 ? 30 : 0 } },
    yAxis: { type: "value" },
    series,
  };
}

const FORMATTING_LABELS: Record<string, string> = {
  apa7: "APA 7th",  mla9: "MLA 9th",  chicago: "Chicago",
  harvard: "Harvard",  ieee: "IEEE",  none: "General",
};
const LEVEL_LABELS: Record<string, string> = {
  high_school: "High School",  undergraduate: "Undergraduate",
  graduate: "Graduate",  phd: "PhD",
};

function safeEmbedUrl(url: string): string | null {
  const ALLOWED = [
    "docs.google.com", "sheets.google.com", "slides.google.com",
    "public.tableau.com", "app.flourish.studio", "datawrapper.dwcdn.net",
    "www.canva.com", "canva.com", "prezi.com", "airtable.com", "app.powerbi.com",
  ];
  try {
    const host = new URL(url).hostname.toLowerCase();
    return ALLOWED.some((d) => host === d || host.endsWith("." + d)) ? url : null;
  } catch { return null; }
}

function disclaimerClass(style: string): string {
  if (style === "academic_integrity") return "border-amber-200 bg-amber-50 text-amber-900";
  if (style === "medical") return "border-blue-200 bg-blue-50 text-blue-900";
  if (style === "copyright") return "border-slate-200 bg-slate-50 text-slate-700";
  return "border-slate-200 bg-slate-50 text-slate-700";
}

function disclaimerIcon(style: string): string {
  if (style === "academic_integrity") return "⚠️";
  if (style === "medical") return "🩺";
  if (style === "copyright") return "©";
  return "ℹ️";
}

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

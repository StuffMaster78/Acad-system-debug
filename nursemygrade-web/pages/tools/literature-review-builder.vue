<script setup lang="ts">
useSeoMeta({
  title: 'Free Literature Review Builder — Structured Template Generator | EssayManiacs',
  description: 'Generate a structured literature review template with thematic sections, word count estimates, and citation tips. Free, instant, no sign-up required.',
})

type Scope = '5' | '10' | '20' | 'all'
type SourceCount = '5-10' | '10-20' | '20-40' | '40+'
type CitStyle = 'APA' | 'MLA' | 'Chicago' | 'Harvard'
type Purpose = 'standalone' | 'dissertation' | 'paper'

const topic = ref('')
const scope = ref<Scope>('10')
const sourceCount = ref<SourceCount>('10-20')
const citStyle = ref<CitStyle>('APA')
const purpose = ref<Purpose>('paper')
const themes = ref(['', '', '', '', ''])

const scopes = [
  { value: '5' as Scope,   label: 'Last 5 years' },
  { value: '10' as Scope,  label: 'Last 10 years' },
  { value: '20' as Scope,  label: 'Last 20 years' },
  { value: 'all' as Scope, label: 'All time' },
]

const sourceCounts = [
  { value: '5-10' as SourceCount,  label: '5–10 sources' },
  { value: '10-20' as SourceCount, label: '10–20 sources' },
  { value: '20-40' as SourceCount, label: '20–40 sources' },
  { value: '40+' as SourceCount,   label: '40+ sources' },
]

const citStyles = ['APA', 'MLA', 'Chicago', 'Harvard'] as CitStyle[]

const purposes = [
  { value: 'standalone' as Purpose,   label: 'Standalone Literature Review' },
  { value: 'dissertation' as Purpose, label: 'Chapter in Dissertation' },
  { value: 'paper' as Purpose,        label: 'Part of Research Paper' },
]

const validThemes = computed(() => themes.value.map(t => t.trim()).filter(Boolean))

const generated = ref(false)
const output = ref('')
const copied = ref(false)

// Word count estimates based on source count and purpose
function wordEstimate(themeCount: number): number {
  const base: Record<SourceCount, number> = {
    '5-10': 200, '10-20': 350, '20-40': 500, '40+': 700,
  }
  const mult = purpose.value === 'dissertation' ? 1.5 : purpose.value === 'standalone' ? 1.3 : 1
  return Math.round((base[sourceCount.value] / Math.max(themeCount, 1)) * mult)
}

function sourcesPerTheme(themeCount: number): number {
  const counts: Record<SourceCount, number> = {
    '5-10': 7, '10-20': 15, '20-40': 30, '40+': 50,
  }
  return Math.round(counts[sourceCount.value] / Math.max(themeCount, 1))
}

function totalWordEstimate(): number {
  const themes_ = validThemes.value.length || 2
  const perTheme = wordEstimate(themes_)
  const intro = 175
  const synth = purpose.value === 'dissertation' ? 350 : 250
  const conc = purpose.value === 'dissertation' ? 200 : 125
  return intro + (perTheme * themes_) + synth + conc
}

function citTips(cs: CitStyle): string[] {
  const tips: Record<CitStyle, string[]> = {
    APA: [
      'Use (Author, Year) in-text citations for every claim',
      'Arrange references alphabetically by author last name',
      'Use "&" between authors in parenthetical citations, "and" in prose',
      'Include DOI or URL for all electronic sources',
    ],
    MLA: [
      'Use (Author Page) parenthetical citations (e.g. Smith 45)',
      'Compile sources in Works Cited, not References',
      'Use hanging indent for Works Cited entries',
      'Include the URL or DOI for online sources',
    ],
    Chicago: [
      'Use footnotes or endnotes for in-text citations',
      'Author-date format is also acceptable for scientific fields',
      'List all sources in a Bibliography at the end',
      'Include the city of publication for print books',
    ],
    Harvard: [
      'Use (Author, Year, p. X) for direct quotes',
      'List sources alphabetically in the reference list',
      'No initials spaces — write F.M. not F. M.',
      'Use "and" (not "&") between authors in prose',
    ],
  }
  return tips[cs]
}

function scopeLabel(s: Scope): string {
  return scopes.find(x => x.value === s)?.label ?? s
}

function generateOutput() {
  const t = topic.value.trim() || '[your topic]'
  const themes_ = validThemes.value.length >= 2
    ? validThemes.value
    : ['[Theme 1]', '[Theme 2]', '[Theme 3]']
  const themePreview = themes_.slice(0, 3).join(', ') + (themes_.length > 3 ? `, and ${themes_.length - 3} more` : '')
  const srcLabel = sourceCount.value
  const divider = '─'.repeat(52)

  const sections: string[] = []

  // Header
  sections.push(`LITERATURE REVIEW TEMPLATE: ${t.toUpperCase()}`)
  sections.push(`Generated for ${srcLabel} sources | ${scopeLabel(scope.value)} | ${citStyle.value}`)
  sections.push(divider)
  sections.push('')

  // Introduction
  sections.push(`INTRODUCTION (~150–200 words)`)
  sections.push(`This section introduces the scope of the review, explains why ${t} is an`)
  sections.push(`important area of inquiry, and outlines the organizational structure of the review.`)
  sections.push('')
  sections.push(`• Introduce ${t} and its relevance to the field`)
  sections.push(`• State the purpose of this literature review`)
  sections.push(`• Briefly preview the thematic structure: ${themePreview}`)
  sections.push(`• Identify any limitations in the existing literature`)
  sections.push(`• Note the scope of sources: ${scopeLabel(scope.value)}`)
  sections.push('')
  sections.push(divider)
  sections.push('')

  // Theme sections
  themes_.forEach((theme, idx) => {
    const wEst = wordEstimate(themes_.length)
    const sEst = sourcesPerTheme(themes_.length)
    sections.push(`SECTION ${idx + 1}: ${theme.toUpperCase()} (~${wEst} words / ~${sEst} sources)`)
    sections.push('')
    sections.push(`${idx + 1}.1 Overview of existing literature on ${theme}`)
    sections.push(`   Synthesise key findings from seminal and recent works. Avoid summarising`)
    sections.push(`   sources one-by-one; instead, group them by argument or finding.`)
    sections.push('')
    sections.push(`   Key questions to address:`)
    sections.push(`   • What does the literature say about ${theme} in the context of ${t}?`)
    sections.push(`   • Are there areas of consensus or disagreement among scholars?`)
    sections.push(`   • What methodologies have been used to study this aspect?`)
    sections.push('')
    sections.push(`${idx + 1}.2 Gaps, limitations, and debates`)
    sections.push(`   • Identify what is missing or contested in this sub-area`)
    sections.push(`   • Note methodological limitations (sample sizes, geographic focus, etc.)`)
    sections.push(`   • Highlight how these gaps inform your own research / paper`)
    sections.push('')
    sections.push(divider)
    sections.push('')
  })

  // Synthesis
  const synthWords = purpose.value === 'dissertation' ? '300–450' : '200–300'
  sections.push(`SYNTHESIS AND CRITICAL ANALYSIS (~${synthWords} words)`)
  sections.push(`• Compare and contrast findings across themes`)
  sections.push(`• Identify overarching patterns, contradictions, or convergences`)
  sections.push(`• Evaluate the quality and reliability of the evidence`)
  if (purpose.value === 'dissertation') {
    sections.push(`• Situate your dissertation research within the existing body of work`)
    sections.push(`• Articulate your theoretical or conceptual framework`)
  } else {
    sections.push(`• Situate your paper's argument within the existing body of work`)
  }
  sections.push('')
  sections.push(divider)
  sections.push('')

  // Conclusion
  const concWords = purpose.value === 'dissertation' ? '150–250' : '100–150'
  sections.push(`CONCLUSION (~${concWords} words)`)
  sections.push(`• Summarise the state of the field on ${t}`)
  sections.push(`• Restate the key gaps and debates identified`)
  sections.push(`• Transition to your research question${purpose.value === 'dissertation' ? ', hypothesis, or methodology chapter' : ' or methodology'}`)
  sections.push('')
  sections.push(divider)
  sections.push('')

  // References
  sections.push(`REFERENCES`)
  sections.push(`[List your ${srcLabel} sources in ${citStyle.value} format here]`)
  sections.push(`Tip: Use the Citation Generator tool to format each source correctly.`)
  sections.push(`   → /tools/citation-generator`)
  sections.push('')
  sections.push(divider)
  sections.push('')

  // Citation tips
  sections.push(`WRITING TIPS FOR ${citStyle.value}:`)
  for (const tip of citTips(citStyle.value)) {
    sections.push(`• ${tip}`)
  }
  sections.push('')
  sections.push(`Estimated total word count: ~${totalWordEstimate().toLocaleString()} words`)
  sections.push(`(excluding references, based on ${srcLabel} sources and ${purpose.value} purpose)`)

  output.value = sections.join('\n')
  generated.value = true
}

async function copyOutput() {
  await navigator.clipboard.writeText(output.value)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

function downloadTxt() {
  const blob = new Blob([output.value], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'literature-review-template.txt'
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<template>
  <div class="bg-slate-50 min-h-screen">
    <!-- Breadcrumb -->
    <div class="max-w-4xl mx-auto px-4 pt-6 pb-2">
      <nav class="text-sm text-slate-500 flex items-center gap-1.5">
        <NuxtLink to="/tools" class="hover:text-brand-600 transition-colors">Tools</NuxtLink>
        <span>/</span>
        <span class="text-slate-700 font-medium">Literature Review Builder</span>
      </nav>
    </div>

    <div class="max-w-4xl mx-auto px-4 pb-4">
      <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-800 mb-1">Literature Review Builder</h1>
      <p class="text-slate-500 text-sm">Generate a structured template with thematic sections, word count estimates, and citation tips.</p>
    </div>

    <div class="max-w-4xl mx-auto px-4 pb-16 space-y-6">

      <!-- Topic + Purpose -->
      <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6 space-y-5">
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1.5">Topic <span class="text-red-400">*</span></label>
          <input
            v-model="topic"
            type="text"
            placeholder="e.g. Machine learning in healthcare diagnostics"
            class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-2">Lit Review Purpose</label>
          <div class="flex flex-wrap gap-2">
            <label
              v-for="p in purposes"
              :key="p.value"
              :class="[
                'flex items-center gap-2 rounded-xl border-2 px-4 py-2 cursor-pointer transition-all text-sm',
                purpose === p.value
                  ? 'border-brand-500 bg-brand-50 text-brand-700 font-semibold'
                  : 'border-slate-200 text-slate-600 hover:border-brand-200'
              ]"
            >
              <input type="radio" :value="p.value" v-model="purpose" class="accent-brand-600" />
              {{ p.label }}
            </label>
          </div>
        </div>
      </div>

      <!-- Scope + Sources + Citation -->
      <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6 space-y-5">
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-2">Scope / Time Period</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="s in scopes"
              :key="s.value"
              type="button"
              @click="scope = s.value"
              :class="[
                'rounded-full border px-4 py-1.5 text-sm font-semibold transition-all',
                scope === s.value
                  ? 'border-brand-500 bg-brand-600 text-white'
                  : 'border-slate-200 text-slate-600 hover:border-brand-300'
              ]"
            >
              {{ s.label }}
            </button>
          </div>
        </div>

        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-2">Number of Sources to Cite</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="sc in sourceCounts"
              :key="sc.value"
              type="button"
              @click="sourceCount = sc.value"
              :class="[
                'rounded-full border px-4 py-1.5 text-sm font-semibold transition-all',
                sourceCount === sc.value
                  ? 'border-brand-500 bg-brand-600 text-white'
                  : 'border-slate-200 text-slate-600 hover:border-brand-300'
              ]"
            >
              {{ sc.label }}
            </button>
          </div>
        </div>

        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-2">Citation Style</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="cs in citStyles"
              :key="cs"
              type="button"
              @click="citStyle = cs"
              :class="[
                'rounded-full border px-4 py-1.5 text-sm font-semibold transition-all',
                citStyle === cs
                  ? 'border-brand-500 bg-brand-600 text-white'
                  : 'border-slate-200 text-slate-600 hover:border-brand-300'
              ]"
            >
              {{ cs }}
            </button>
          </div>
        </div>
      </div>

      <!-- Themes -->
      <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6 space-y-4">
        <h2 class="text-sm font-bold text-slate-500 uppercase tracking-wider">Thematic Sections</h2>
        <p class="text-xs text-slate-400">At least 2 themes required. Each becomes a dedicated section in your lit review.</p>
        <div class="space-y-3">
          <div v-for="(_, i) in themes" :key="i">
            <label class="block text-xs font-semibold text-slate-500 mb-1">
              Theme {{ i + 1 }} {{ i >= 2 ? '(optional)' : '' }}
              {{ i < 2 ? '*' : '' }}
            </label>
            <input
              v-model="themes[i]"
              type="text"
              :placeholder="i === 0 ? 'e.g. Impact on academic performance' : i === 1 ? 'e.g. Psychological effects' : `Theme ${i + 1}`"
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
            />
          </div>
        </div>

        <button
          type="button"
          @click="generateOutput"
          :disabled="validThemes.length < 2"
          :class="[
            'w-full sm:w-auto rounded-xl px-8 py-3 text-sm font-bold text-white transition-colors',
            validThemes.length >= 2
              ? 'bg-brand-600 hover:bg-brand-700'
              : 'bg-slate-300 cursor-not-allowed'
          ]"
        >
          Generate literature review template →
        </button>
        <p v-if="validThemes.length < 2" class="text-xs text-slate-400">Please fill in at least 2 themes to generate the template.</p>
      </div>

      <!-- Output -->
      <div v-if="generated" class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
        <div class="flex items-center justify-between mb-4 flex-wrap gap-3">
          <div>
            <h2 class="text-sm font-bold text-slate-500 uppercase tracking-wider">Generated Template</h2>
            <p class="text-xs text-slate-400 mt-0.5">Estimated total: ~{{ totalWordEstimate().toLocaleString() }} words</p>
          </div>
          <div class="flex gap-2">
            <button
              type="button"
              @click="copyOutput"
              class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors flex items-center gap-1.5"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184"/></svg>
              {{ copied ? 'Copied!' : 'Copy' }}
            </button>
            <button
              type="button"
              @click="downloadTxt"
              class="rounded-xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 transition-colors flex items-center gap-1.5"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"/></svg>
              Download .txt
            </button>
          </div>
        </div>
        <pre class="text-xs sm:text-sm text-slate-700 leading-relaxed font-mono bg-slate-50 rounded-xl border border-slate-200 p-4 overflow-x-auto whitespace-pre-wrap">{{ output }}</pre>
      </div>

      <!-- CTA -->
      <div class="rounded-2xl bg-white border border-slate-100 shadow-sm p-6 text-center">
        <p class="text-sm text-slate-600 mb-3">Need a full literature review written by subject experts? Delivered from <strong>$10/page</strong>.</p>
        <NuxtLink to="/order" class="inline-block rounded-xl bg-brand-600 px-6 py-3 text-sm font-bold text-white hover:bg-brand-700 transition-colors">
          Order a paper →
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

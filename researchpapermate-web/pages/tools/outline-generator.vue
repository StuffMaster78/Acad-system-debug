<script setup lang="ts">
useSeoMeta({
  title: 'Free Research Paper Outline Generator — Roman Numeral Outline | EssayManiacs',
  description: 'Generate a complete Roman numeral research paper outline for argumentative, analytical, research, and literature review papers. Free, instant, no sign-up.',
})

type PaperType = 'argumentative' | 'research' | 'analytical' | 'litreview' | 'expository'
type PageCount = '3' | '5' | '8' | '10+'
type CitationStyle = 'APA' | 'MLA' | 'Chicago' | 'Harvard' | 'Other'

const paperType = ref<PaperType>('argumentative')
const topic = ref('')
const researchQuestion = ref('')
const pageCount = ref<PageCount>('5')
const citationStyle = ref<CitationStyle>('APA')
const arguments_ = ref(['', '', ''])

const paperTypes = [
  { value: 'argumentative' as PaperType, label: 'Argumentative' },
  { value: 'research' as PaperType,      label: 'Research' },
  { value: 'analytical' as PaperType,    label: 'Analytical' },
  { value: 'litreview' as PaperType,     label: 'Literature Review' },
  { value: 'expository' as PaperType,    label: 'Expository' },
]

const pageCounts = [
  { value: '3' as PageCount,   label: '3 pages' },
  { value: '5' as PageCount,   label: '5 pages' },
  { value: '8' as PageCount,   label: '8 pages' },
  { value: '10+' as PageCount, label: '10+ pages' },
]

const citationStyles = ['APA', 'MLA', 'Chicago', 'Harvard', 'Other'] as CitationStyle[]

function addArgument() {
  if (arguments_.value.length < 5) arguments_.value.push('')
}
function removeArgument(i: number) {
  if (arguments_.value.length > 2) arguments_.value.splice(i, 1)
}

const generated = ref(false)
const outline = ref('')
const copied = ref(false)

function romanNumeral(n: number): string {
  const map: [number, string][] = [[10,'X'],[9,'IX'],[5,'V'],[4,'IV'],[1,'I']]
  let result = ''
  for (const [val, sym] of map) {
    while (n >= val) { result += sym; n -= val }
  }
  return result
}

function generateOutline() {
  const t = topic.value.trim() || '[your topic]'
  const rq = researchQuestion.value.trim()
  const thesisLine = rq ? `Research Question: ${rq}` : `Thesis: [State your central argument about ${t}]`
  const args = arguments_.value.map(a => a.trim()).filter(Boolean)
  const refLabel = citationStyle.value === 'MLA' ? 'Works Cited' : 'References'
  const is10plus = pageCount.value === '10+'
  const is3page = pageCount.value === '3'

  const sections: string[] = []
  let sectionNum = 1

  // I. Introduction
  const introSubs = [
    `   A. Background context on ${t}`,
    `   B. Significance and relevance of the topic`,
    !is3page ? `   C. Overview of existing debates and scholarship` : '',
    `   ${is3page ? 'C' : 'D'}. ${thesisLine}`,
  ].filter(Boolean)
  sections.push(`${romanNumeral(sectionNum++)}. Introduction\n${introSubs.join('\n')}`)

  // Literature Review (skip for 3-page)
  if (!is3page) {
    if (paperType.value === 'litreview') {
      sections.push(`${romanNumeral(sectionNum++)}. Scope and Methodology\n   A. Search strategy and databases used\n   B. Inclusion and exclusion criteria\n   C. Overview of sources reviewed`)
    } else if (paperType.value !== 'expository') {
      sections.push(`${romanNumeral(sectionNum++)}. Literature Review / Background\n   A. Existing scholarship on ${t}\n   B. Key debates and theoretical frameworks\n   C. Gaps this paper addresses`)
    }
  }

  // Main argument sections
  const filledArgs = args.length > 0 ? args : ['[Main argument 1]', '[Main argument 2]', '[Main argument 3]']
  for (const arg of filledArgs) {
    if (paperType.value === 'litreview') {
      sections.push(`${romanNumeral(sectionNum++)}. Theme: ${arg}\n   A. Overview of literature on this theme\n   B. Key findings and areas of consensus\n   C. Gaps, debates, and methodological limitations`)
    } else if (paperType.value === 'argumentative') {
      sections.push(`${romanNumeral(sectionNum++)}. ${arg}\n   A. Evidence and analysis\n   B. Supporting examples and data\n   C. Counterargument and rebuttal`)
    } else if (paperType.value === 'analytical') {
      sections.push(`${romanNumeral(sectionNum++)}. ${arg}\n   A. Close analysis and evidence\n   B. Interpretation and significance\n   C. Connection to central argument`)
    } else if (paperType.value === 'research') {
      sections.push(`${romanNumeral(sectionNum++)}. ${arg}\n   A. Evidence and supporting data\n   B. Analysis of findings\n   C. Relationship to research question`)
    } else {
      sections.push(`${romanNumeral(sectionNum++)}. ${arg}\n   A. Definition and explanation\n   B. Examples and illustrations\n   C. Significance to the overall topic`)
    }
  }

  // Discussion (8+ pages)
  if (!is3page && pageCount.value !== '5') {
    if (paperType.value === 'litreview') {
      sections.push(`${romanNumeral(sectionNum++)}. Synthesis and Critical Analysis\n   A. Comparison of findings across themes\n   B. Overarching patterns and contradictions\n   C. Situating current research within existing scholarship`)
    } else {
      sections.push(`${romanNumeral(sectionNum++)}. Discussion\n   A. Synthesis of findings\n   B. Implications for ${t}\n   C. Limitations of the study\n   ${is10plus ? 'D. Recommendations for future research' : ''}`.trimEnd())
    }
  }

  // Conclusion
  const conclusionSubs = [
    `   A. Restatement of thesis / central argument`,
    `   B. Summary of main points`,
    paperType.value !== 'expository' ? `   C. Broader implications and significance` : `   C. Final explanation of the topic's importance`,
    !is3page ? `   D. Call to action / directions for future research` : '',
    `   ${is3page ? 'C' : 'E'}. ${refLabel} [${citationStyle.value} format]`,
  ].filter(Boolean)
  sections.push(`${romanNumeral(sectionNum++)}. Conclusion\n${conclusionSubs.join('\n')}`)

  outline.value = [
    `RESEARCH PAPER OUTLINE`,
    `Topic: ${t}`,
    rq ? `Research Question: ${rq}` : '',
    `Paper Type: ${paperTypes.find(p => p.value === paperType.value)?.label}  |  Length: ${pageCount.value} pages  |  Citation Style: ${citationStyle.value}`,
    `${'─'.repeat(52)}`,
    '',
    ...sections.map(s => s + '\n'),
    `${'─'.repeat(52)}`,
    `Note: Expand each sub-point with evidence, analysis,`,
    `and proper ${citationStyle.value} in-text citations.`,
  ].filter(s => s !== null && s !== undefined).join('\n')

  generated.value = true
}

async function copyOutline() {
  await navigator.clipboard.writeText(outline.value)
  copied.value = true
  setTimeout(() => { copied.value = false }, 2000)
}

function downloadTxt() {
  const blob = new Blob([outline.value], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'research-paper-outline.txt'
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
        <span class="text-slate-700 font-medium">Research Paper Outline Generator</span>
      </nav>
    </div>

    <div class="max-w-4xl mx-auto px-4 pb-4">
      <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-800 mb-1">Research Paper Outline Generator</h1>
      <p class="text-slate-500 text-sm">Fill in the details and generate a Roman numeral outline tailored to your paper type and length.</p>
    </div>

    <div class="max-w-4xl mx-auto px-4 pb-16 space-y-6">

      <!-- Paper type -->
      <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
        <h2 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">Paper Type</h2>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="pt in paperTypes"
            :key="pt.value"
            type="button"
            @click="paperType = pt.value"
            :class="[
              'rounded-full border px-4 py-1.5 text-sm font-semibold transition-all',
              paperType === pt.value
                ? 'border-brand-500 bg-brand-600 text-white'
                : 'border-slate-200 text-slate-600 hover:border-brand-300'
            ]"
          >
            {{ pt.label }}
          </button>
        </div>
      </div>

      <!-- Core fields -->
      <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6 space-y-5">
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1.5">Topic <span class="text-red-400">*</span></label>
          <input
            v-model="topic"
            type="text"
            placeholder="e.g. The impact of social media on youth mental health"
            class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1.5">
            Research Question
            <span class="text-slate-400 font-normal text-xs">(optional)</span>
          </label>
          <input
            v-model="researchQuestion"
            type="text"
            placeholder="e.g. How does social media use correlate with anxiety in teenagers?"
            class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
          />
        </div>

        <!-- Page count -->
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1.5">Estimated Pages</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="pc in pageCounts"
              :key="pc.value"
              type="button"
              @click="pageCount = pc.value"
              :class="[
                'rounded-full border px-4 py-1.5 text-sm font-semibold transition-all',
                pageCount === pc.value
                  ? 'border-brand-500 bg-brand-600 text-white'
                  : 'border-slate-200 text-slate-600 hover:border-brand-300'
              ]"
            >
              {{ pc.label }}
            </button>
          </div>
        </div>

        <!-- Citation style -->
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1.5">Citation Style</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="cs in citationStyles"
              :key="cs"
              type="button"
              @click="citationStyle = cs"
              :class="[
                'rounded-full border px-4 py-1.5 text-sm font-semibold transition-all',
                citationStyle === cs
                  ? 'border-brand-500 bg-brand-600 text-white'
                  : 'border-slate-200 text-slate-600 hover:border-brand-300'
              ]"
            >
              {{ cs }}
            </button>
          </div>
        </div>

        <!-- Main arguments -->
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1.5">
            Main Arguments / Themes
            <span class="text-slate-400 font-normal text-xs">(2–5)</span>
          </label>
          <div class="space-y-2">
            <div
              v-for="(_, i) in arguments_"
              :key="i"
              class="flex gap-2 items-center"
            >
              <span class="text-xs font-bold text-slate-400 w-5 text-center flex-shrink-0">{{ i + 1 }}</span>
              <input
                v-model="arguments_[i]"
                type="text"
                :placeholder="`Argument / theme ${i + 1}${i >= 2 ? ' (optional)' : ''}`"
                class="flex-1 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
              />
              <button
                v-if="arguments_.length > 2"
                type="button"
                @click="removeArgument(i)"
                class="text-slate-400 hover:text-red-500 transition-colors flex-shrink-0"
                aria-label="Remove"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
              </button>
            </div>
          </div>
          <button
            v-if="arguments_.length < 5"
            type="button"
            @click="addArgument"
            class="mt-2 text-sm text-brand-600 font-semibold hover:text-brand-700 transition-colors flex items-center gap-1"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15"/></svg>
            Add argument
          </button>
        </div>

        <button
          type="button"
          @click="generateOutline"
          class="w-full sm:w-auto rounded-xl bg-brand-600 px-8 py-3 text-sm font-bold text-white hover:bg-brand-700 transition-colors"
        >
          Generate outline →
        </button>
      </div>

      <!-- Output -->
      <div v-if="generated" class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-sm font-bold text-slate-500 uppercase tracking-wider">Generated Outline</h2>
          <div class="flex gap-2">
            <button
              type="button"
              @click="copyOutline"
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
        <pre class="text-xs sm:text-sm text-slate-700 leading-relaxed font-mono bg-slate-50 rounded-xl border border-slate-200 p-4 overflow-x-auto whitespace-pre-wrap">{{ outline }}</pre>
      </div>

      <!-- CTA -->
      <div class="rounded-2xl bg-white border border-slate-100 shadow-sm p-6 text-center">
        <p class="text-sm text-slate-600 mb-3">Need a professionally written paper? Our experts deliver custom, plagiarism-free papers from <strong>$10/page</strong>.</p>
        <NuxtLink to="/order" class="inline-block rounded-xl bg-brand-600 px-6 py-3 text-sm font-bold text-white hover:bg-brand-700 transition-colors">
          Order a paper →
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

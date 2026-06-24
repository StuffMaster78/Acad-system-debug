<script setup lang="ts">
useSeoMeta({
  title: 'Free Plagiarism Checker — Detect Repetition in Your Text',
  description: 'Check your essay for repeated sentences and phrases with our client-side repetition analyser. Get a uniqueness score and vocabulary richness report. Free, no sign-up.',
})

interface DuplicatePair {
  a: string
  b: string
  similarity: number
}

interface AnalysisResult {
  totalSentences: number
  uniqueSentences: number
  duplicatePairs: DuplicatePair[]
  repeatedPhrases: [string, number][]
  ttr: number
  uniquenessScore: number
}

const text = ref('')
const result = ref<AnalysisResult | null>(null)
const analysing = ref(false)

const wordCount = computed(() => {
  const m = text.value.trim().match(/\S+/g)
  return m ? m.length : 0
})

function normalize(s: string): string {
  return s.toLowerCase().replace(/[^a-z0-9\s]/g, '').replace(/\s+/g, ' ').trim()
}

function jaccard(a: string, b: string): number {
  const wordsA = a.split(' ').filter(Boolean)
  const wordsB = b.split(' ').filter(Boolean)
  if (wordsA.length === 0 || wordsB.length === 0) return 0
  const sa = new Set(wordsA)
  const sb = new Set(wordsB)
  let inter = 0
  for (const w of sa) { if (sb.has(w)) inter++ }
  const union = new Set([...wordsA, ...wordsB]).size
  return union === 0 ? 0 : inter / union
}

function analyzeText(rawText: string): AnalysisResult {
  // 1. Tokenise sentences
  const sentences = (rawText.match(/[^.!?]+[.!?]+/g) ?? [])
    .map(s => s.trim())
    .filter(s => s.length > 10)

  // 2. Normalise
  const normalised = sentences.map(normalize)

  // 3. Find near-duplicate sentence pairs (Jaccard > 0.70)
  const duplicatePairs: DuplicatePair[] = []
  const isDuplicate = new Set<number>()
  for (let i = 0; i < normalised.length; i++) {
    for (let j = i + 1; j < normalised.length; j++) {
      const sim = jaccard(normalised[i], normalised[j])
      if (sim >= 0.7) {
        duplicatePairs.push({ a: sentences[i], b: sentences[j], similarity: Math.round(sim * 100) })
        isDuplicate.add(i)
        isDuplicate.add(j)
      }
    }
  }

  // 4. 3-word phrases appearing 3+ times
  const words = rawText.toLowerCase().replace(/[^a-z0-9\s]/g, '').split(/\s+/).filter(Boolean)
  const phraseCount: Record<string, number> = {}
  for (let i = 0; i < words.length - 2; i++) {
    const phrase = `${words[i]} ${words[i + 1]} ${words[i + 2]}`
    phraseCount[phrase] = (phraseCount[phrase] ?? 0) + 1
  }
  const repeatedPhrases = Object.entries(phraseCount)
    .filter(([, n]) => n >= 3)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 15)

  // 5. Type-token ratio
  const uniqueWords = new Set(words).size
  const ttr = words.length > 0 ? Math.round((uniqueWords / words.length) * 100) : 0

  // 6. Uniqueness score: % of sentences not flagged as duplicates
  const uniqueSentences = sentences.length - isDuplicate.size
  const uniquenessScore = sentences.length > 0
    ? Math.round((uniqueSentences / sentences.length) * 100)
    : 100

  return {
    totalSentences: sentences.length,
    uniqueSentences,
    duplicatePairs,
    repeatedPhrases,
    ttr,
    uniquenessScore,
  }
}

function runAnalysis() {
  if (!text.value.trim()) return
  analysing.value = true
  // Wrap in setTimeout to allow the UI to update before heavy computation
  setTimeout(() => {
    result.value = analyzeText(text.value)
    analysing.value = false
  }, 50)
}

function clearAll() {
  text.value = ''
  result.value = null
}

function scoreColor(score: number): string {
  if (score >= 85) return 'text-green-600'
  if (score >= 70) return 'text-amber-600'
  return 'text-red-600'
}
function scoreBg(score: number): string {
  if (score >= 85) return 'bg-green-50 border-green-200'
  if (score >= 70) return 'bg-amber-50 border-amber-200'
  return 'bg-red-50 border-red-200'
}
function ttrLabel(ttr: number): string {
  if (ttr >= 60) return 'Rich vocabulary'
  if (ttr >= 40) return 'Moderate vocabulary'
  return 'Low vocabulary diversity'
}
function ttrColor(ttr: number): string {
  if (ttr >= 60) return 'bg-green-500'
  if (ttr >= 40) return 'bg-amber-500'
  return 'bg-red-500'
}
</script>

<template>
  <div class="bg-slate-50 min-h-screen">
    <!-- Breadcrumb -->
    <div class="max-w-4xl mx-auto px-4 pt-6 pb-2">
      <nav class="text-sm text-slate-500 flex items-center gap-1.5">
        <NuxtLink to="/tools" class="hover:text-brand-600 transition-colors">Tools</NuxtLink>
        <span>/</span>
        <span class="text-slate-700 font-medium">Plagiarism Checker</span>
      </nav>
    </div>

    <div class="max-w-4xl mx-auto px-4 pb-4">
      <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-800 mb-1">Plagiarism Checker</h1>
      <p class="text-slate-500 text-sm">Detect repeated sentences and phrases within your text. All analysis runs in your browser — nothing is uploaded.</p>
    </div>

    <div class="max-w-4xl mx-auto px-4 pb-16 space-y-6">

      <!-- Disclaimer (always visible) -->
      <div class="rounded-2xl bg-blue-50 border border-blue-200 p-4 flex gap-3">
        <span class="text-blue-500 text-lg flex-shrink-0 mt-0.5">ℹ</span>
        <p class="text-sm text-blue-800 leading-relaxed">
          <strong>Scope notice:</strong> This tool checks for repetition <em>within your own text only</em>. It does not compare your text against external sources, websites, or academic databases. For submission-grade plagiarism detection, use <strong>Turnitin</strong>, <strong>Copyscape</strong>, or your institution's tool.
        </p>
      </div>

      <!-- Input -->
      <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6 space-y-3">
        <div class="flex items-center justify-between flex-wrap gap-2">
          <label class="text-sm font-bold text-slate-700">Your Text</label>
          <div class="flex items-center gap-3">
            <span :class="['text-xs font-semibold', wordCount > 5000 ? 'text-red-500' : 'text-slate-400']">
              {{ wordCount.toLocaleString() }} / 5,000 words
            </span>
            <button v-if="text" type="button" @click="clearAll" class="text-xs font-semibold text-slate-500 hover:text-red-500 transition-colors flex items-center gap-1">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
              Clear
            </button>
          </div>
        </div>
        <textarea
          v-model="text"
          placeholder="Paste your text here (up to 5,000 words)…"
          class="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none resize-y leading-relaxed"
          style="min-height: 350px;"
        />
        <div class="flex items-center gap-3">
          <button
            type="button"
            @click="runAnalysis"
            :disabled="!text.trim() || wordCount > 5000 || analysing"
            class="rounded-xl bg-brand-600 px-6 py-3 text-sm font-bold text-white hover:bg-brand-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            <svg v-if="analysing" class="animate-spin w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
            {{ analysing ? 'Analysing…' : 'Check for repetition →' }}
          </button>
          <span v-if="wordCount > 5000" class="text-xs text-red-500 font-semibold">Text exceeds 5,000 words — please reduce before checking.</span>
        </div>
      </div>

      <!-- Results -->
      <template v-if="result">

        <!-- Score card -->
        <div :class="['rounded-2xl border shadow-sm p-8 text-center', scoreBg(result.uniquenessScore)]">
          <p :class="['text-7xl font-extrabold', scoreColor(result.uniquenessScore)]">
            {{ result.uniquenessScore }}%
          </p>
          <p :class="['text-lg font-bold mt-1', scoreColor(result.uniquenessScore)]">Unique</p>
          <p class="text-xs text-slate-500 mt-2">Based on internal repetition analysis only</p>
        </div>

        <!-- Stats row -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div class="rounded-2xl bg-white border border-slate-100 shadow-sm p-4 text-center">
            <p class="text-2xl font-extrabold text-slate-700">{{ result.totalSentences }}</p>
            <p class="text-xs font-semibold text-slate-500 mt-1 uppercase tracking-wide">Total sentences</p>
          </div>
          <div class="rounded-2xl bg-white border border-slate-100 shadow-sm p-4 text-center">
            <p class="text-2xl font-extrabold text-green-600">{{ result.uniqueSentences }}</p>
            <p class="text-xs font-semibold text-slate-500 mt-1 uppercase tracking-wide">Unique sentences</p>
          </div>
          <div class="rounded-2xl bg-white border border-slate-100 shadow-sm p-4 text-center">
            <p class="text-2xl font-extrabold text-amber-600">{{ result.duplicatePairs.length }}</p>
            <p class="text-xs font-semibold text-slate-500 mt-1 uppercase tracking-wide">Similar pairs found</p>
          </div>
          <div class="rounded-2xl bg-white border border-slate-100 shadow-sm p-4 text-center">
            <p class="text-2xl font-extrabold text-slate-700">{{ result.ttr }}%</p>
            <p class="text-xs font-semibold text-slate-500 mt-1 uppercase tracking-wide">Vocabulary richness</p>
          </div>
        </div>

        <!-- Vocabulary richness gauge -->
        <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
          <h2 class="text-sm font-bold text-slate-700 mb-3">Vocabulary Richness (Type-Token Ratio)</h2>
          <div class="flex items-center gap-4">
            <div class="flex-1 bg-slate-100 rounded-full h-3 overflow-hidden">
              <div
                :class="['h-full rounded-full transition-all', ttrColor(result.ttr)]"
                :style="{ width: `${result.ttr}%` }"
              />
            </div>
            <span :class="['text-sm font-bold w-20 text-right', result.ttr >= 60 ? 'text-green-600' : result.ttr >= 40 ? 'text-amber-600' : 'text-red-600']">
              {{ result.ttr }}%
            </span>
          </div>
          <p class="text-xs text-slate-500 mt-2">{{ ttrLabel(result.ttr) }} — ratio of unique words to total words</p>
        </div>

        <!-- Repeated phrases -->
        <div v-if="result.repeatedPhrases.length > 0" class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
          <h2 class="text-sm font-bold text-slate-700 mb-4">Repeated 3-Word Phrases</h2>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="[phrase, count] in result.repeatedPhrases"
              :key="phrase"
              class="inline-flex items-center gap-1.5 rounded-full bg-amber-50 border border-amber-100 px-3 py-1.5 text-xs font-semibold text-amber-800"
            >
              "{{ phrase }}"
              <span class="bg-amber-500 text-white rounded-full px-1.5 py-0.5 text-[10px] font-bold leading-none">×{{ count }}</span>
            </span>
          </div>
          <p class="text-xs text-slate-400 mt-3">Phrases appearing 3 or more times in your text.</p>
        </div>
        <div v-else class="rounded-2xl bg-white shadow-sm border border-slate-100 p-5 flex items-center gap-3">
          <span class="w-8 h-8 rounded-full bg-green-100 text-green-600 flex items-center justify-center flex-shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/></svg>
          </span>
          <p class="text-sm text-slate-600 font-medium">No 3-word phrases repeated 3 or more times.</p>
        </div>

        <!-- Duplicate sentence pairs -->
        <div v-if="result.duplicatePairs.length > 0" class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
          <h2 class="text-sm font-bold text-slate-700 mb-4">Similar Sentence Pairs</h2>
          <div class="space-y-4">
            <div
              v-for="(pair, i) in result.duplicatePairs"
              :key="i"
              class="rounded-xl bg-amber-50 border border-amber-100 p-4 space-y-2"
            >
              <div class="flex items-center justify-between mb-1">
                <span class="text-xs font-bold text-amber-700">{{ pair.similarity }}% similar</span>
              </div>
              <p class="text-sm text-slate-700 border-l-4 border-amber-400 pl-3 italic">"{{ pair.a }}"</p>
              <p class="text-sm text-slate-700 border-l-4 border-amber-300 pl-3 italic">"{{ pair.b }}"</p>
            </div>
          </div>
        </div>
        <div v-else class="rounded-2xl bg-white shadow-sm border border-slate-100 p-5 flex items-center gap-3">
          <span class="w-8 h-8 rounded-full bg-green-100 text-green-600 flex items-center justify-center flex-shrink-0">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5"/></svg>
          </span>
          <p class="text-sm text-slate-600 font-medium">No highly similar sentence pairs detected.</p>
        </div>

      </template>

      <!-- CTA -->
      <div class="rounded-2xl bg-white border border-slate-100 shadow-sm p-6 text-center">
        <p class="text-sm text-slate-600 mb-3">Need a full essay written by experts? We deliver custom, plagiarism-free papers from <strong>$10/page</strong>.</p>
        <NuxtLink to="/order" class="inline-block rounded-xl bg-brand-600 px-6 py-3 text-sm font-bold text-white hover:bg-brand-700 transition-colors">
          Order a paper →
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

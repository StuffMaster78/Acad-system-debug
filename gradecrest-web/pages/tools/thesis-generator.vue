<script setup lang="ts">
useSeoMeta({
  title: 'Free Thesis Statement Generator — Argumentative, Analytical & More | EssayManiacs',
  description: 'Generate strong thesis statements for argumentative, analytical, expository, and compare & contrast essays. Free, instant, no sign-up required.',
})

type EssayType = 'argumentative' | 'analytical' | 'expository' | 'compare'

const essayType = ref<EssayType>('argumentative')
const topic = ref('')
const position = ref('')
const reason1 = ref('')
const reason2 = ref('')
const reason3 = ref('')

const essayTypes = [
  { value: 'argumentative' as EssayType, label: 'Argumentative', desc: 'Take a stance and defend it' },
  { value: 'analytical' as EssayType,    label: 'Analytical',    desc: 'Break down and examine a subject' },
  { value: 'expository' as EssayType,    label: 'Expository',    desc: 'Explain or describe a topic' },
  { value: 'compare' as EssayType,       label: 'Compare & Contrast', desc: 'Examine similarities and differences' },
]

const positionLabel = computed(() =>
  essayType.value === 'compare' ? 'Second Subject to Compare' : 'Your Position / Main Claim'
)
const positionPlaceholder = computed(() =>
  essayType.value === 'compare'
    ? 'e.g. traditional education'
    : 'e.g. social media worsens anxiety'
)

const generated = ref(false)
const theses = ref<string[]>([])
const copiedIdx = ref<number | null>(null)

function buildReasonStr(includeThird: boolean): string {
  const r3 = reason3.value.trim()
  if (includeThird && r3) return `, and ${r3}`
  return ''
}

function generateTheses() {
  const t = topic.value.trim() || '[topic]'
  const p = position.value.trim() || '[position/second subject]'
  const r1 = reason1.value.trim() || '[reason 1]'
  const r2 = reason2.value.trim() || '[reason 2]'
  const r3 = reason3.value.trim()

  const reasonsShort = r3 ? `${r1}, ${r2}, and ${r3}` : `${r1} and ${r2}`
  const reasonsEnd = r3 ? `, and ${r3}` : ''

  switch (essayType.value) {
    case 'argumentative':
      theses.value = [
        `Although there are opposing views, ${t} ${p} because ${r1}, ${r2}${reasonsEnd}.`,
        `Because ${r1}, ${r2}${reasonsEnd}, ${t} ${p}.`,
        `${t.charAt(0).toUpperCase() + t.slice(1)} ${p}, as demonstrated by ${reasonsShort}.`,
      ]
      break
    case 'analytical':
      theses.value = [
        `An analysis of ${t} reveals that ${p} through ${r1}, ${r2}${reasonsEnd}.`,
        `By examining ${reasonsShort}, this paper argues that ${t} ${p}.`,
        `${t.charAt(0).toUpperCase() + t.slice(1)} demonstrates ${p}, which can be understood through ${reasonsShort}.`,
      ]
      break
    case 'expository':
      theses.value = [
        `${t.charAt(0).toUpperCase() + t.slice(1)} involves ${r1}, ${r2}${reasonsEnd}, which together ${p}.`,
        `Understanding ${t} requires examining ${reasonsShort}.`,
        `${t.charAt(0).toUpperCase() + t.slice(1)} can be explained through three key factors: ${reasonsShort}.`,
      ]
      break
    case 'compare':
      theses.value = r3
        ? [
            `While ${t} and ${p} share important similarities, they differ fundamentally in ${r1} and ${r2}, with ${r3} highlighting the contrast.`,
            `${t.charAt(0).toUpperCase() + t.slice(1)} and ${p} are often compared, but an examination of ${r1} and ${r2} reveals significant distinctions.`,
            `Despite surface similarities, ${t} and ${p} are distinguished by ${r1}, ${r2}, and ${r3}.`,
          ]
        : [
            `While ${t} and ${p} share important similarities, they differ fundamentally in ${r1} and ${r2}.`,
            `${t.charAt(0).toUpperCase() + t.slice(1)} and ${p} are often compared, but an examination of ${r1} and ${r2} reveals significant distinctions.`,
            `Despite surface similarities, ${t} and ${p} are distinguished by ${r1} and ${r2}.`,
          ]
      break
  }
  generated.value = true
}

async function copyThesis(i: number) {
  await navigator.clipboard.writeText(theses.value[i])
  copiedIdx.value = i
  setTimeout(() => { copiedIdx.value = null }, 2000)
}
</script>

<template>
  <div class="bg-slate-50 min-h-screen">
    <!-- Breadcrumb -->
    <div class="max-w-4xl mx-auto px-4 pt-6 pb-2">
      <nav class="text-sm text-slate-500 flex items-center gap-1.5">
        <NuxtLink to="/tools" class="hover:text-brand-600 transition-colors">Tools</NuxtLink>
        <span>/</span>
        <span class="text-slate-700 font-medium">Thesis Statement Generator</span>
      </nav>
    </div>

    <div class="max-w-4xl mx-auto px-4 pb-4">
      <h1 class="text-2xl sm:text-3xl font-extrabold text-slate-800 mb-1">Thesis Statement Generator</h1>
      <p class="text-slate-500 text-sm">Fill in the form and click Generate to get 3 thesis statement variants.</p>
    </div>

    <div class="max-w-4xl mx-auto px-4 pb-16 space-y-6">

      <!-- Essay type -->
      <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6">
        <h2 class="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">Essay Type</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <label
            v-for="et in essayTypes"
            :key="et.value"
            :class="[
              'flex items-start gap-3 rounded-xl border-2 p-4 cursor-pointer transition-all',
              essayType === et.value
                ? 'border-brand-500 bg-brand-50'
                : 'border-slate-200 hover:border-brand-200'
            ]"
          >
            <input type="radio" :value="et.value" v-model="essayType" class="mt-0.5 accent-brand-600" />
            <div>
              <div class="font-semibold text-sm text-slate-800">{{ et.label }}</div>
              <div class="text-xs text-slate-500 mt-0.5">{{ et.desc }}</div>
            </div>
          </label>
        </div>
      </div>

      <!-- Core fields -->
      <div class="rounded-2xl bg-white shadow-sm border border-slate-100 p-6 space-y-5">
        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1.5">
            Topic / Subject <span class="text-red-400">*</span>
          </label>
          <input
            v-model="topic"
            type="text"
            placeholder="e.g. social media and mental health"
            class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
          />
        </div>

        <div>
          <label class="block text-sm font-semibold text-slate-700 mb-1.5">
            {{ positionLabel }} <span class="text-red-400">*</span>
          </label>
          <input
            v-model="position"
            type="text"
            :placeholder="positionPlaceholder"
            class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
          />
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">
              Supporting Reason 1 <span class="text-red-400">*</span>
            </label>
            <input
              v-model="reason1"
              type="text"
              placeholder="First reason"
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
            />
          </div>
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">
              Supporting Reason 2 <span class="text-red-400">*</span>
            </label>
            <input
              v-model="reason2"
              type="text"
              placeholder="Second reason"
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
            />
          </div>
          <div>
            <label class="block text-sm font-semibold text-slate-700 mb-1.5">
              Supporting Reason 3 <span class="text-slate-400 font-normal text-xs">(optional)</span>
            </label>
            <input
              v-model="reason3"
              type="text"
              placeholder="Third reason (optional)"
              class="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm focus:border-brand-400 focus:ring-2 focus:ring-brand-100 outline-none"
            />
          </div>
        </div>

        <button
          type="button"
          @click="generateTheses"
          class="w-full sm:w-auto rounded-xl bg-brand-600 px-8 py-3 text-sm font-bold text-white hover:bg-brand-700 transition-colors"
        >
          Generate thesis statements →
        </button>
      </div>

      <!-- Output -->
      <div v-if="generated" class="space-y-4">
        <h2 class="text-base font-bold text-slate-700">Generated Thesis Statements</h2>
        <div
          v-for="(thesis, i) in theses"
          :key="i"
          class="rounded-2xl bg-white border border-slate-100 shadow-sm p-5 flex gap-4"
        >
          <span class="flex-shrink-0 w-8 h-8 rounded-full bg-brand-100 text-brand-700 text-sm font-extrabold flex items-center justify-center">
            {{ i + 1 }}
          </span>
          <div class="flex-1">
            <p class="text-sm text-slate-700 leading-relaxed">{{ thesis }}</p>
          </div>
          <button
            type="button"
            @click="copyThesis(i)"
            class="flex-shrink-0 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-50 transition-colors self-start"
          >
            {{ copiedIdx === i ? 'Copied!' : 'Copy' }}
          </button>
        </div>

        <!-- Tip -->
        <div class="rounded-xl bg-amber-50 border border-amber-100 p-4 flex gap-3">
          <span class="text-amber-500 text-lg flex-shrink-0">💡</span>
          <p class="text-sm text-amber-800"><strong>Tip:</strong> A strong thesis is specific, arguable, and maps your paper's structure. Choose the variant that best fits your argument and refine it to suit your paper.</p>
        </div>
      </div>

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
